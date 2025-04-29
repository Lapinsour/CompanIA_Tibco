from pinecone import Pinecone, ServerlessSpec
import pinecone
import hashlib
import re
import string
import random
import pyodbc
import unicodedata
import unstructured
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from openai import OpenAI
import time
import os
import numpy
import html
import sys
import requests
from bs4 import BeautifulSoup
import datetime
from datetime import datetime as dt
import feedparser
from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer
import json
from bs4 import BeautifulSoup
from newspaper import Article
from dateutil.relativedelta import relativedelta
from dateutil import parser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import random
import time
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv

#fonctions maison
from send_mail import send_mail_func
from sauvegarde_rapport_sql import sauvegarde_rapport_func
from rag_sql_tibco import rag_sql_tibco
from rag_sql_tibco import liste_client_rag
from rag_secteur import rag_secteur_func
from prompt_generator import prompt_generator_func
from rag_actu_officielle import get_pappers_info, get_boamp_info



load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PAPPERS_API_KEY = os.getenv("PAPPERS_API_KEY")


entreprise_nom = sys.argv[1]
secteur = sys.argv[2] 
contexte = sys.argv[3]
collab_nom = sys.argv[4]
destinataire = sys.argv[5]
centre_interet = sys.argv[6] 
collab_fonction = sys.argv[7]
autre = sys.argv[8]



x_ = 1
while x_ < 7:
    
    x_+=1

# Convertir la liste des choix en liste Python
centre_interet_inputs = centre_interet.split(",") if centre_interet else []
# Convertir la liste des destinataires en liste python
destinataires = destinataire.split(";")


# Modèle
model_name = "multilingual-e5-large"
dimension_model = 1024
max_tokens = 96
tokenizer = AutoTokenizer.from_pretrained("intfloat/multilingual-e5-large")

# Ces prompts ne sont pas le prompt_rapport. Ils servent à scanner la BDD vectorielle.
prompt_de_recherche_CLIENT = f"Quelle(s) actualité(s) pourraient influencer l'activité et le profit de l'entreprise {entreprise_nom}?"

linkedin_url = f"https://www.google.com/search?q={collab_nom.replace(" ", "+")}+{entreprise_nom}+site:linkedin.com"     




def refresh_actu(PINECONE_API_KEY, PINECONE_INDEX_NAME, refresh_after_days):
    #Supprime toutes les lignes datant de plus de {refresh_after_days} jours dans Pinecone.
    pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
    index_pc = pc.Index(PINECONE_INDEX_NAME)
    namespace = "actu"

    # Déterminer la date limite (3 mois avant aujourd'hui)
    date_limite = datetime.datetime.now() - datetime.timedelta(days=90)  # 90 jours = 3 mois

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

            

            # Supprimer les articles identifiés dans le namespace
            if ids_a_supprimer:
                index_pc.delete(ids=ids_a_supprimer, namespace=namespace)
                
            
                
        
            
    except Exception as e:
        print("Merde")
        

def extract_liste_entreprise_nom(PINECONE_API_KEY, PINECONE_INDEX_NAME) :
  #Extrait la liste des entreprises dans le namespace "actu" dans Pinecone.

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


  


  return list(entreprises_distinctes)

def check_for_actu_in_pinecone(entreprise_nom, model_name, PINECONE_INDEX_NAME) :

    #Récupère les relevant actu dans Pinecone pour l'entreprise_nom.
    query_CLIENT = prompt_de_recherche_CLIENT

    pc = Pinecone(
      api_key=PINECONE_API_KEY
    )

    # Génération de l'embedding pour la requête
    embedding_CLIENT = pc.inference.embed(
        model=model_name,
        inputs=[query_CLIENT],
        parameters={"input_type": "query"}
    )
    query_embedding_CLIENT = embedding_CLIENT[0]['values']  # Vérifier que cette structure est correcte

    # Connexion à l'index Pinecone
    index_pc = pc.Index(PINECONE_INDEX_NAME)

    # Recherche des résultats similaires
    results_CLIENT = index_pc.query(
        namespace="actu",
        vector=query_embedding_CLIENT,
        top_k=7,
        include_values=False,
        include_metadata=True,
        filter={"entreprise_nom": entreprise_nom} #CE FILTRE PERMET DE NE RECHERCHER LES ACTUS QUE POUR L'ENTREPRISE CHOISIE
    )

    # Vérification si des résultats ont été trouvés
    if not results_CLIENT.get("matches"):
        
        return None

    # Extraire les morceaux de texte pertinents
    relevant_texts_CLIENT = [result["metadata"]["text"] for result in results_CLIENT["matches"]]

    return relevant_texts_CLIENT

def get_embedding(texts):
    """
    Génère des embeddings avec un modèle externe (ex : OpenAI, Ollama, Cohere)
    Fonction répétée dans internal_rag() et Query_GPT() si les scripts sont exécutés à part.
    """

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
    
    #Convertit une date relative du type "Il y a X jours" ou "Il y a X semaines" en une date absolue.
    
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



async def scrape_bing_news(query, secteur):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Simuler un vrai utilisateur avec un User-Agent
        page.set_default_timeout(10000)
        await page.set_extra_http_headers({"User-Agent": "Mozilla/5.0"})

        # Ouvrir Bing News
        url = f"""https://www.bing.com/news/search?q="{query.replace(' ', '+')}"+secteur+%20+{secteur.replace(' ', '+')}&qft=interval%3d"9"&form=PTFTNR"""
        await page.goto(url)
        await page.wait_for_timeout(3000)  # Attendre le chargement

        articles = []
        # Sélectionner tous les articles
        news_items = await page.query_selector_all("div.news-card.newsitem")  # S'assurer de bien cibler les articles

        for item in news_items:
            try:
                # Récupérer le titre et le lien
                title_element = await item.query_selector("a.title")
                title = await title_element.inner_text() if title_element else "Titre inconnu"
                link = await title_element.get_attribute("href") if title_element else None
                
                # Vérifier si le lien est valide
                if not link or not link.startswith("http"):
                    continue  # Ignorer si le lien est invalide

                # Récupérer la source
                source_element = await item.query_selector(".source")
                source = await source_element.inner_text() if source_element else "Source inconnue"

                # Récupérer la date
                date_element = await item.query_selector("span[aria-label]")
                date = await date_element.get_attribute("aria-label") if date_element else "Date inconnue"

                # Récupérer l'extrait (snippet)
                snippet_element = await item.query_selector(".snippet")
                chapo = await snippet_element.inner_text() if snippet_element else "Pas d'extrait disponible"

                # Si snippet est vide, essayer avec newspaper3k pour obtenir un extrait complet
                
                snippet = get_article_content(link)

                # Ajouter l'article à la liste
                articles.append({
                    "title": title,
                    "url": link,
                    "source": source,
                    "date": date,
                    "chapi":chapo,
                    "snippet": snippet
                })
            except Exception as e:
                
                continue  # Ignorer les erreurs et continuer

        await browser.close()
        return articles

def get_article_content(url):
    
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text[:1000]  # Retourne les 500 premiers caractères
    except Exception as e:        
        return "Impossible de récupérer le contenu"


def google_news_scrap(PINECONE_API_KEY, PINECONE_INDEX_NAME, entreprise_nom):
    
    articles = []

    all_entreprises = extract_liste_entreprise_nom(PINECONE_API_KEY, PINECONE_INDEX_NAME)    
    liste_entreprises = [element.lower() for element in all_entreprises]    
    

    if entreprise_nom.lower() in liste_entreprises :
      
      relevant_actu = check_for_actu_in_pinecone(entreprise_nom, model_name, PINECONE_INDEX_NAME)
      return relevant_actu

    else :
      
        news = asyncio.run(scrape_bing_news(f'{entreprise_nom}', secteur))
        

        # Sélectionner les éléments d'articles
        for article in news :
        

            # Ajouter les articles à la liste
            articles.append({
                "titre_article": article['title'],
                "date":  convertir_date_texte(article['date']).strftime("%Y-%m-%d") if convertir_date_texte(article['date']) else None, 
                "texte_article": article['snippet'],
                "nom_entreprise": entreprise_nom,
                'source': article['url']
            })

         
        for article in articles:
            if article["date"] is not None:
                upsert_article_in_pinecone(article)

        refresh_actu(PINECONE_API_KEY, PINECONE_INDEX_NAME, refresh_after_days=90)
        relevant_actu = check_for_actu_in_pinecone(entreprise_nom, model_name, PINECONE_INDEX_NAME)
        return relevant_actu




def Query_GPT(entreprise_nom, model_name, OPENAI_API_KEY,PINECONE_INDEX_NAME):


    pc = Pinecone(
      api_key=PINECONE_API_KEY
    )

    # Connexion à l'index Pinecone
    index_pc = pc.Index(PINECONE_INDEX_NAME)
    

    all_results_TIBCO = []

   

    

    for interet in centre_interet_inputs :            
        results_TIBCO = index_pc.query(
            namespace="DOC-TIBCO",
            vector=[0.0] * 1024,
            top_k=100, 
            include_values=False,
            include_metadata=True,
            filter={"offre": {"$eq": interet}}
        )

        all_results_interet = [result["metadata"]["text"] for result in results_TIBCO["matches"]]
        
        all_results_TIBCO.append(all_results_interet)

    relevant_texts_TIBCO = all_results_TIBCO

    def format_tibco_services(nested_text_blocks):
        formatted_text = ""

        for sublist in nested_text_blocks:
            for block in sublist:  # on boucle dans chaque sous-liste
                services = re.split(r"(Service proposé par TIBCO\s*:\s*[^\s]+)", block)
                grouped = list(zip(services[1::2], services[2::2]))

                for title, content in grouped:
                    title_clean = title.strip()
                    content_clean = content.strip()

                    # "__" devient un point + espace (fin de phrase)
                    content_clean = re.sub(r'__+', '. ', content_clean)

                    # "_" devient un espace
                    content_clean = re.sub(r'_+', ' ', content_clean)

                    # Majuscule après un point
                    content_clean = re.sub(r'(?<=\.)\s+([a-z])', lambda m: ' ' + m.group(1).upper(), content_clean)

                    formatted_text += f"{title_clean}\n{content_clean}\n\n"

        return formatted_text.strip()
    services_tibco = format_tibco_services(relevant_texts_TIBCO)   
    

    
    
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        )

    # Fonction pour interroger ChatGPT
    def chat_gpt(prompt_actu):
        response = client.chat.completions.create(        
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_actu}]
        )
        return response.choices[0].message.content.strip()



    def rag_actu_client(PINECONE_API_KEY, PINECONE_INDEX_NAME, entreprise_nom):
        news_client = google_news_scrap(PINECONE_API_KEY, PINECONE_INDEX_NAME, entreprise_nom)
        prompt_actu = f"Voici une sélection d'articles sur l'entreprise {entreprise_nom}."  
        if news_client :      
            for article in news_client:
                prompt_actu+= str(article)            
            prompt_actu+= f"A partir de cette sélection, résume en 1000 signes de l'entreprise {entreprise_nom}.\
                Accorde la priorité à l'actualité concernant la France et l'Europe.\
                Accorde plus d'importance aux actualités relatives à la cybersécurité, la Data, le numérique, la mise en réseau ou encore la réutilisation de composants électroniques."
            response_text_actu_client = chat_gpt(prompt_actu)        
        
        else :
            response_text_actu_client = "Désolé, je n'ai pas trouvé d'actualité pour cette entreprise."
            
        return response_text_actu_client


    news_secteur = rag_secteur_func(secteur)  
    actu_client = rag_actu_client(PINECONE_API_KEY, PINECONE_INDEX_NAME, entreprise_nom)  
    
    
    relation_sql = None
    siret = None 

    try:
        liste_client = liste_client_rag()

        if entreprise_nom in liste_client :
            
            try:
                relation_sql, nb_aff,nb_aff_en_cours,total_budget, total_facture, siret, type_date, derniere_date = rag_sql_tibco(entreprise_nom)  
                  
                total_budget = f"{total_budget:,.2f}".replace(",", " ").replace(".", ",")
                total_facture = f"{total_facture:,.2f}".replace(",", " ").replace(".", ",")            
                if nb_aff != 0 : 
                    if type_date == "fin" :
                        reponse_relation_sql = f"Cette entreprise est déjà cliente de Tibco ! Plus précisément, nous avons {nb_aff} affaires terminées avec elle, pour un budget total de {total_budget}€ et une facturation totale de {total_facture}€.\n\
                        L'affaire la plus récente s'est terminée le {derniere_date}.\n\
                        Pour en savoir plus, vous trouverez en pièce jointe un tableau récapitulatif de la relation de Tibco et de l'entreprise {entreprise_nom}."
                    
                    if type_date == "création":                                           
                        reponse_relation_sql = f"Cette entreprise est déjà cliente de Tibco ! Plus précisément, nous avons {nb_aff} affaires avec elle, dont {nb_aff_en_cours} en cours, pour un budget total de {total_budget}€ et une facturation totale de {total_facture}€.\n\
                        L'affaire la plus récente a débuté le {derniere_date}.\n\
                        Pour en savoir plus, vous trouverez en pièce jointe un tableau récapitulatif de la relation de Tibco et de l'entreprise {entreprise_nom}."
                else : 
                    reponse_relation_sql = f"L'entreprise {entreprise_nom} est déjà cliente de Tibco, mais nous n'avons aucune affaire passée ou en cours avec elle."
            except pyodbc.Error as e :
                print(pyodbc.Error)
                reponse_relation_sql ="Aïe, nous n'avons pas pu remonter les informations quant à la relation de Tibco avec cette entreprise, car les serveurs de Tibco sont indisponibles entre 12h15 et 13h."
            except Exception as e:
                print("Exception",e)
                reponse_relation_sql ="Aïe, nous n'avons pas pu remonter les informations quant à la relation de Tibco avec cette entreprise, car les serveurs de Tibco sont indisponibles entre 12h15 et 13h."
    
        else :
            reponse_relation_sql ="Cette entreprise ne compte pas parmi les clients de Tibco... Pour l'instant !\nSi vous pensez qu'il s'agit d'une erreur, n'hésitez pas à nous la faire remonter."
            
    except pyodbc.Error as e :
        reponse_relation_sql ="ERREUR PYODBC : Aïe, nous n'avons pas pu remonter les informations quant à la relation de Tibco avec cette entreprise, car les serveurs de Tibco sont indisponibles entre 12h15 et 13h."
    
    #boamp_info = get_boamp_info(entreprise_nom)
    #print(boamp_info)
    #if siret :
    #    print(f'SIRET = {siret}')        
    #    pappers_info = get_pappers_info(PAPPERS_API_KEY, siret)
    #    print(pappers_info)

        
    prompt = prompt_generator_func(entreprise_nom, collab_nom, centre_interet_inputs, contexte, secteur, actu_client, news_secteur, services_tibco, collab_fonction, autre)
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------#
        
    
    client = OpenAI(
    api_key=OPENAI_API_KEY,
    )

    # Fonction pour interroger ChatGPT
    def chat_gpt(prompt):
        response = client.chat.completions.create(
            
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    # Envoi du prompt à ChatGPT et récupération de la réponse
    response_text = chat_gpt(prompt)
    

    # Création de l'ID du rapport
    def getCode(length = 10, char = string.ascii_uppercase + string.digits + string.ascii_lowercase):
      return ''.join(random.choice( char) for x in range(length))
    ID_rapport = getCode()

    #Envoi du mail      
    send_mail_func(entreprise_nom, relation_sql, response_text, ID_rapport, destinataires, linkedin_url, reponse_relation_sql)

    #Sauvegarde du rapport dans HA-DWH
    sauvegarde_rapport_func(entreprise_nom, ID_rapport, response_text)

      


def fonction_principale():
   
    Query_GPT(entreprise_nom, model_name, OPENAI_API_KEY,PINECONE_INDEX_NAME)

if __name__ == '__main__':
    fonction_principale()



