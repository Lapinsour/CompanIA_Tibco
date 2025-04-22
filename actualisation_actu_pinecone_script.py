from pinecone import Pinecone, ServerlessSpec
import pinecone
import hashlib
import asyncio
from playwright.async_api import async_playwright
import unstructured
from langchain.document_loaders import DirectoryLoader, PyPDFLoader, PyMuPDFLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from openai import OpenAI
import time
import datetime
from datetime import datetime as dt
import os
import nltk
nltk.download('punkt')  # Pour la tokenisation
nltk.download('averaged_perceptron_tagger')  # Pour le POS tagging
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('wordnet')  # Pour la lemmatisation
from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer
import requests
import json
from bs4 import BeautifulSoup
from newspaper import Article
from dateutil.relativedelta import relativedelta
from dateutil import parser
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Modèle
model_name = "multilingual-e5-large"
dimension_model = 1024
chunk_size = 6000
chunk_overlap = 0
max_tokens = 96
tokenizer = AutoTokenizer.from_pretrained("intfloat/multilingual-e5-large")


def extract_liste_entreprise_nom(PINECONE_API_KEY, PINECONE_INDEX_NAME) :

  pc = Pinecone(
          api_key=PINECONE_API_KEY
        )
  index = pc.Index(PINECONE_INDEX_NAME)
  namespace = "actu"

  # Initialisation d'un set pour stocker les valeurs distinctes de 'entreprise_nom'
  entreprises_distinctes = set()

  # Paramétrage de la requête de base : chercher toutes les données dans le namespace "actu"
  query_response = index.query(
      namespace=namespace,
      top_k=100,  # Nombre de résultats par requête
      include_metadata=True,
      vector=[0.0] * 1024  # vecteur neutre pour ne pas spécifier un vecteur précis
  )

  # Parcours des résultats et récupération des valeurs distinctes de 'entreprise_nom'
  for match in query_response['matches']:
      entreprise_nom = match['metadata'].get('entreprise_nom')
      if entreprise_nom:
          entreprises_distinctes.add(entreprise_nom)

  # Gestion de la pagination, si nécessaire
  next_page = query_response.get('next_page')
  while next_page:
      query_response = index.query(
          namespace=namespace,
          top_k=100,
          include_metadata=True,
          cursor=next_page  # Pagination
      )

      for match in query_response['matches']:
          entreprise_nom = match['metadata'].get('entreprise_nom')
          if entreprise_nom:
              entreprises_distinctes.add(entreprise_nom)

      next_page = query_response.get('next_page')  # Vérifie s'il y a d'autres pages


  #print("Entreprises distinctes :", entreprises_distinctes)


  return list(entreprises_distinctes)



def get_embedding(texts):

    #Génère des embeddings avec un modèle externe (ex : OpenAI, Ollama, Cohere)
    

    pc = Pinecone(
      api_key=PINECONE_API_KEY
   )
    embeddings = pc.inference.embed(
        model=model_name,
        inputs=texts,
        parameters={"input_type": "passage", "truncate": "END"}
    )
    return [e["values"] for e in embeddings]  # Extraction des valeurs des embeddings



def upsert_article_in_pinecone(article):
    """Upsert les articles dans Pinecone"""

    pc = Pinecone(
        api_key=PINECONE_API_KEY
    )

    nom_entreprise = article["nom_entreprise"]
    date = article["date"]
    titre_article = article["titre_article"]
    texte_article = article["texte_article"]

    data = {"id": f"{hashlib.md5(texte_article.encode()).hexdigest()}", "text": texte_article, "date": date, "title":titre_article, "nom_entreprise":nom_entreprise}
    # Préparer les textes à embedder
    texts = [data["text"]]


    # Générer les embeddings
    embeddings = get_embedding(texts)


    # Envoi vers Pinecone
    vectors = [
        {
            "id": data["id"],  # ID unique
            "values": e,     # Embedding sous forme de liste de flottants
            "metadata": {"type":"ACTU","date":data["date"], "text":data["text"],"title":data["title"],"entreprise_nom":data["nom_entreprise"]}  # PERMET DE NE RECHERCHER QUE LES DOCUMENTS MARQUES DOC-TIBCO
        }
        for d, e in zip(data, embeddings)
    ]

    index_pc = pc.Index(PINECONE_INDEX_NAME)
    index_pc.upsert(vectors=vectors, namespace="actu")



# Dictionnaire des mois en français vers anglais
mois_fr_vers_en = {
    "janv.": "Jan", "févr.": "Feb", "mars": "Mar", "avr.": "Apr", "mai": "May", "juin": "Jun",
    "juil.": "Jul", "août": "Aug", "sept.": "Sep", "oct.": "Oct", "nov.": "Nov", "déc.": "Dec"
}

def convertir_date_relative(date_str):
    """
    Convertit une date relative du type "Il y a X jours" ou "Il y a X semaines" en une date absolue.
    """
    date_str = date_str.replace("\xa0", " ")  # Supprimer les espaces insécables
    today = datetime.datetime.now()

    # Cherche une correspondance avec "Il y a X jours" ou "Il y a X semaines"
    match = re.match(r"il y a (\d+) (jour|jours|semaine|semaines|mois|heure|heures)", date_str, re.IGNORECASE)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)

        if "jour" in unit:
            return today - datetime.timedelta(days=amount)
        elif "semaine" in unit:
            return today - datetime.timedelta(weeks=amount)
        elif "mois" in unit:
        # Calculer un mois en soustrayant un nombre de jours approximatif
            return today - datetime.timedelta(days=amount * 30)
        elif "heure" in unit:
            return today - datetime.timedelta(hours=amount)


    return None


def convertir_mois_fr_en(date_str):
    """
    Remplace les mois abrégés en français par leur équivalent en anglais.
    """
    for mois_fr, mois_en in mois_fr_vers_en.items():
        date_str = date_str.replace(mois_fr, mois_en)
    return date_str

def convertir_date_texte(date_str):
    """
    Tente de convertir la date en un objet datetime.
    Gère les dates relatives et les dates absolues en texte.
    """
    # Vérifier si la date est relative
    date = convertir_date_relative(date_str)
    if date:
        return date

    # Essayer de convertir une date absolue (ex: "15 janv. 2024")
    date_str = convertir_mois_fr_en(date_str)  # Remplacer les mois français par anglais
    try:
        return datetime.datetime.strptime(date_str, "%d %b %Y")  # Format "15 Jan 2024"
    except ValueError:
        return None  # Si le format n'est pas reconnu



async def scrape_bing_news(query, browser):
    page = await browser.new_page()
    await page.set_extra_http_headers({"User-Agent": "Mozilla/5.0"})
    
    url = f"https://www.bing.com/news/search?q={query.replace(' ', '+')}+entreprise&qft=interval%3d\"9\"&form=PTFTNR"
    await page.goto(url)
    await page.wait_for_load_state("domcontentloaded")

    articles = []
    news_items = await page.query_selector_all("div.news-card.newsitem")

    for item in news_items:
        try:
            title_element = await item.query_selector("a.title")
            title = await title_element.inner_text() if title_element else "Titre inconnu"
            link = await title_element.get_attribute("href") if title_element else None
            if not link or not link.startswith("http"):
                continue

            source_element = await item.query_selector(".source")
            source = await source_element.inner_text() if source_element else "Source inconnue"

            date_element = await item.query_selector("span[aria-label]")
            date = await date_element.get_attribute("aria-label") if date_element else "Date inconnue"

            snippet_element = await item.query_selector(".snippet")
            chapo = await snippet_element.inner_text() if snippet_element else "Pas d'extrait disponible"

            articles.append({
                "title": title,
                "url": link,
                "source": source,
                "date": date,
                "chapi": chapo,
            })
        except Exception as e:
            print(f"Erreur lors du traitement d'un article : {e}")
            continue  

    await page.close()
    return articles

async def get_article_content_async(url):
    """Récupère le contenu de l'article de manière asynchrone."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text[:1000]
    except Exception:
        return "Impossible de récupérer le contenu"

async def google_news_scrap(PINECONE_API_KEY, PINECONE_INDEX_NAME):
    """Scrape Bing News en parallèle et stocke les résultats dans Pinecone."""
    liste_entreprises = extract_liste_entreprise_nom(PINECONE_API_KEY, PINECONE_INDEX_NAME)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # Scraper toutes les entreprises en parallèle
        tasks = [scrape_bing_news(nom, browser) for nom in liste_entreprises]
        all_articles = await asyncio.gather(*tasks)

        articles_to_insert = []
        
        # Télécharger les contenus d'article en parallèle
        for entreprise_nom, news in zip(liste_entreprises, all_articles):
            tasks = [get_article_content_async(article["url"]) for article in news]
            snippets = await asyncio.gather(*tasks)

            for article, snippet in zip(news, snippets):
                article_data = {
                    "titre_article": article["title"],
                    "date": convertir_date_texte(article["date"]).strftime("%Y-%m-%d") if convertir_date_texte(article["date"]) else None, 
                    "texte_article": snippet,
                    "nom_entreprise": entreprise_nom,
                    'source': article['url']
                }
                if article_data["date"] is not None:
                    articles_to_insert.append(article_data)

        # Insérer en base de données (optimisation en batch possible)
        for article in articles_to_insert:
            upsert_article_in_pinecone(article)
        
        print(f"Nombre total d'articles insérés : {len(articles_to_insert)}")

        await browser.close()





def refresh_actu(PINECONE_API_KEY, PINECONE_INDEX_NAME, refresh_after_days):
    pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
    index_pc = pc.Index(PINECONE_INDEX_NAME)
    namespace = "actu"

    # Déterminer la date limite (3 mois avant aujourd'hui)
    date_limite = datetime.datetime.now() - datetime.timedelta(days=10)  # 90 jours = 3 mois

    # Obtenir les statistiques du namespace
    query_results = index_pc.describe_index_stats()
    vector_count = query_results["namespaces"].get(namespace, {}).get("vector_count", 0)


    # Récupérer les vecteurs dans l'index Pinecone
    try:
        result = index_pc.query(
            namespace=namespace,
            top_k=vector_count,
            include_values=False,
            include_metadata=True,
            vector=[0.0] * 1024  # vecteur neutre pour ne pas spécifier un vecteur précis
        )



        ids_a_supprimer = []

        # Vérification des résultats
        if 'matches' in result and result['matches']:
            for match in result['matches']:
                # Vérifier et convertir la date de chaque article

                date_str = match['metadata']['date']
                date_article = dt.strptime(date_str, "%Y-%m-%d")

                if date_article and date_article < date_limite:
                    ids_a_supprimer.append(match['id'])  # Si l'article est trop ancien, on l'ajoute à la liste de suppression

            print(f"Articles à supprimer : {len(ids_a_supprimer)}")

            # Supprimer les articles identifiés dans le namespace
            if ids_a_supprimer:
                index_pc.delete(ids=ids_a_supprimer, namespace=namespace)
                print(f"🗑️ {len(ids_a_supprimer)} articles supprimés dans '{namespace}'.")
            else:
                print("Aucun article à supprimer.")
        else:
            print("Aucun article trouvé correspondant à la requête.")
    except Exception as e:
        print(f"Erreur lors de la requête Pinecone : {e}")


if __name__ == '__main__':
  asyncio.run(google_news_scrap(PINECONE_API_KEY, PINECONE_INDEX_NAME))
  refresh_actu(PINECONE_API_KEY, PINECONE_INDEX_NAME, 10)