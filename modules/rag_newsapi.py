import os
import requests

API_KEY = os.getenv("NEWSAPI_API_KEY")

def rag_newsapi(entreprise_nom):


    ENTREPRISES = [entreprise_nom]  # Mots-clés à rechercher

    # Construire la requête
    query = " OR ".join(ENTREPRISES)  # Ex: "Airbus OR Thales OR Dassault"

    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': query,
        'language': 'fr',
        'sortBy': 'publishedAt',
        'pageSize': 10,
        'apiKey': API_KEY
    }

    response = requests.get(url, params=params)

    # Vérifier la réponse
    if response.status_code == 200:
        data = response.json()
        return data['articles']
    else:
        return None