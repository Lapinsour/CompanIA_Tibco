import requests
from bs4 import BeautifulSoup
import os

# Clé API Pappers (gratuite avec compte)
PAPPERS_API_KEY = os.getenv("PAPPERS_API_KEY")

def get_pappers_info(PAPPERS_API_KEY, siret):
    print("🔍 Recherche dans les publications officielles (Pappers)...")
    url = "https://api.pappers.fr/v2/entreprise"
    params = {
        "siret": siret,
        "api_token": PAPPERS_API_KEY
        
    }

    response = requests.get(url, params=params)
    data = response.json()
    print(data)


def get_boamp_info(entreprise_nom):
    print("🔍 Recherche sur BOAMP...")

    url = f'https://boamp-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/boamp/records?where=titulaire%20%3D%20%22{entreprise_nom}%22&limit=100'

    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        records = data.get('results', [])

        total_marches = len(records)

        marche_list = []
        for record in records:
            objet = record.get('objet', 'Non précisé')
            date = record.get('date_publication', 'Non précisée')

            # On tente d’extraire le code département
            departement = None
            if 'lieu_execution' in record and isinstance(record['lieu_execution'], dict):
                departement = record['lieu_execution'].get('code', 'Non précisé')
            elif 'code_departement' in record:
                departement = record['code_departement']
            else:
                departement = 'Non précisé'

            marche_list.append({
                'objet': objet,
                'departement': departement,
                'date_publication': date
            })

        return {
            'total_marches': total_marches,
            'marches': marche_list
        }

    else:
        return {"error": f"Accès API BOAMP indisponible ou protégé. Code {response.status_code}"}



if __name__ == "__main__":
    siret_test = "88816586700019" 
    entreprise_nom = "ORANGE FRANCE"

    #infos_pappers = get_pappers_info(siret_test)
    
    #print(infos_pappers)

    infos_boamp = get_boamp_info(entreprise_nom)
    print("\n--- Infos BOAMP ---")
    print(infos_boamp)

    