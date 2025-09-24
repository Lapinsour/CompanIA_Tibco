import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from openai import OpenAI
import os
from modules.logging_config import logger

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 

client = OpenAI(api_key=OPENAI_API_KEY)


def résumé(texte_article, entreprise_nom):
    # Tronquage si le texte est trop long (garde les 10 000 premiers caractères)
    texte_article = texte_article[:10000] + "\n[Texte tronqué]" if len(texte_article) > 10000 else texte_article

    messages = [
        {
            "role": "system",
            "content": "Tu es un assistant professionnel et pédagogue."
        },
        {
            "role": "user",
            "content": f"Voici un article Wikipédia. S'il est bien à propos de l'entreprise {entreprise_nom}, résume-le en 1000 signes maximum. Sinon, renvoie EXACTEMENT la phrase 'Voici votre brief !'. Voici l'article Wikipédia :\n\n{texte_article}"
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0  
        )
        # Vérifie que la réponse est bien formée
        output = response.choices[0].message.content.strip()
        if not output:
            logger.warning("Réponse vide wikipédia.")
            return None
        return output
    except Exception as e:
        logger.error(f"Erreur lors de la génération du résumé : {e}")
        return None


def get_wikipedia_text(entreprise_nom, lang="fr"):
    """
    Recherche le bon article Wikipédia pour une entreprise et retourne le texte brut.
    """

    headers = {
        "User-Agent": "MyCompanyApp/1.0 (contact@mycompany.com)"
    }

    # 🔎 Étape 1 : rechercher le titre exact
    search_url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": entreprise_nom,
        "format": "json"
    }

    try:
        search_resp = requests.get(search_url, params=params, headers=headers)
        search_resp.raise_for_status()
    except Exception as e:
        print("❌ Erreur lors de la recherche Wikipédia :", e)
        return None

    search_results = search_resp.json()
    if not search_results.get("query", {}).get("search"):
        print("❌ Aucun résultat trouvé sur Wikipédia.")
        return None

    # 🎯 Prendre le premier résultat
    page_title = search_results["query"]["search"][0]["title"]
    encoded_title = quote(page_title)

    # 📄 Étape 2 : récupération du contenu HTML
    html_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/html/{encoded_title}"

    try:
        html_resp = requests.get(html_url, headers=headers)
        html_resp.raise_for_status()
    except Exception as e:
        print(f"❌ Impossible de récupérer l'article : {e}")
        return None

    soup = BeautifulSoup(html_resp.text, "html.parser")

    # 🧹 Nettoyage du contenu
    for tag in soup(["table", "style", "script", "noscript", "img", "figure", "nav"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    # ⚠️ Vérifie si c'est une page d'homonymie
    if "Ceci est une page d’homonymie" in text.lower():
        print("⚠️ Page de désambiguïsation détectée.")
        return None

    return text


def wikipedia_resume(entreprise_nom):
    texte_article = get_wikipedia_text(entreprise_nom)
    if texte_article:
        print("article wikipédia trouvé")
        logger.info("article wikipédia trouvé")
        return résumé(texte_article, entreprise_nom)
    else:
        print("Aucun texte récupéré ou problème d'article Wikipédia.")
        logger.info("Aucun texte récupéré ou problème d'article Wikipédia.")
        return None



