from pinecone import Pinecone, ServerlessSpec
import pinecone
import time

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME="lasttest"
dimension_model = 1024

def init_pinecone_db(PINECONE_INDEX_NAME,PINECONE_API_KEY, dimension_model):

  pc = Pinecone(
      api_key=PINECONE_API_KEY
  )
  if PINECONE_INDEX_NAME not in pc.list_indexes().names():

    index_name = PINECONE_INDEX_NAME

    pc.create_index(
        name=index_name,
        dimension=dimension_model,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    time.sleep(20)  # Attente pour la création de l'index

  index = pc.describe_index(name=PINECONE_INDEX_NAME)
  print(index.name)
  return index

  init_pinecone_db(PINECONE_INDEX_NAME,PINECONE_API_KEY, dimension_model)