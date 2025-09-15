import datetime
import hashlib
from pinecone import Pinecone

# ========================
# GESTION DES DONNÉES DANS PINECONE
# ========================

def refresh_actu(PINECONE_API_KEY, PINECONE_INDEX_NAME, refresh_after_days):
    """Supprime les actus trop anciennes dans Pinecone."""
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index_pc = pc.Index(PINECONE_INDEX_NAME)
    namespace = "actu"

    date_limite = datetime.datetime.now() - datetime.timedelta(days=refresh_after_days)

    query_results = index_pc.describe_index_stats()
    vector_count = query_results["namespaces"].get(namespace, {}).get("vector_count", 0)

    try:
        result = index_pc.query(
            namespace=namespace,
            top_k=vector_count,
            include_values=False,
            include_metadata=True,
            vector=[0.0] * 1024
        )
        ids_a_supprimer = []
        if 'matches' in result and result['matches']:
            for match in result['matches']:
                date_str = match['metadata']['date']
                date_article = datetime.datetime.strptime(date_str, "%Y-%m-%d")

                if date_article and date_article < date_limite:
                    ids_a_supprimer.append(match['id'])

            if ids_a_supprimer:
                index_pc.delete(ids=ids_a_supprimer, namespace=namespace)

    except Exception:
        print("Erreur dans la récupération des vecteurs sur Pinecone")


def extract_liste_entreprise_nom(PINECONE_API_KEY, PINECONE_INDEX_NAME):
    """Extrait la liste des entreprises dans Pinecone."""
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
    namespace = "actu"

    entreprises_distinctes = set()
    query_response = index.query(
        namespace=namespace,
        top_k=100,
        include_metadata=True,
        vector=[0.0] * 1024
    )

    for match in query_response['matches']:
        entreprise_nom = match['metadata'].get('entreprise_nom')
        if entreprise_nom:
            entreprises_distinctes.add(entreprise_nom)

    next_page = query_response.get('next_page')
    while next_page:
        query_response = index.query(
            namespace=namespace,
            top_k=100,
            include_metadata=True,
            cursor=next_page
        )
        for match in query_response['matches']:
            entreprise_nom = match['metadata'].get('entreprise_nom')
            if entreprise_nom:
                entreprises_distinctes.add(entreprise_nom)
        next_page = query_response.get('next_page')

    return list(entreprises_distinctes)


def check_for_actu_in_pinecone(PINECONE_API_KEY, entreprise_nom, model_name, PINECONE_INDEX_NAME, prompt_de_recherche_CLIENT):
    """Recherche des actus dans Pinecone pour une entreprise."""
    pc = Pinecone(api_key=PINECONE_API_KEY)

    embedding_CLIENT = pc.inference.embed(
        model=model_name,
        inputs=[prompt_de_recherche_CLIENT],
        parameters={"input_type": "query"}
    )
    query_embedding_CLIENT = embedding_CLIENT[0]['values']

    index_pc = pc.Index(PINECONE_INDEX_NAME)

    results_CLIENT = index_pc.query(
        namespace="actu",
        vector=query_embedding_CLIENT,
        top_k=7,
        include_values=False,
        include_metadata=True,
        filter={"entreprise_nom": entreprise_nom}
    )

    if not results_CLIENT.get("matches"):
        return None
    return [result["metadata"]["text"] for result in results_CLIENT["matches"]]


def get_embedding(PINECONE_API_KEY, model_name, texts):
    """Crée des embeddings pour un texte."""
    pc = Pinecone(api_key=PINECONE_API_KEY)
    embeddings = pc.inference.embed(
        model=model_name,
        inputs=texts,
        parameters={"input_type": "passage", "truncate": "END"}
    )
    return [e["values"] for e in embeddings]


def upsert_article_in_pinecone(PINECONE_API_KEY, PINECONE_INDEX_NAME, model_name, article):
    """Insère un article dans Pinecone."""
    pc = Pinecone(api_key=PINECONE_API_KEY)

    nom_entreprise = article["nom_entreprise"]
    date = article["date"]
    titre_article = article["titre_article"]
    texte_article = article["texte_article"]

    data = {
        "id": f"{hashlib.md5(texte_article.encode()).hexdigest()}",
        "text": texte_article,
        "date": date,
        "title": titre_article,
        "nom_entreprise": nom_entreprise
    }

    embeddings = get_embedding(PINECONE_API_KEY, model_name, [data["text"]])

    vectors = [
        {
            "id": data["id"],
            "values": e,
            "metadata": {
                "type": "ACTU",
                "date": data["date"],
                "text": data["text"],
                "title": data["title"],
                "entreprise_nom": data["nom_entreprise"]
            }
        }
        for e in embeddings
    ]
    index_pc = pc.Index(PINECONE_INDEX_NAME)
    index_pc.upsert(vectors=vectors, namespace="actu")
