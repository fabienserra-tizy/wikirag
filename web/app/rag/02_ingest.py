import os
import sys
import weaviate
from weaviate.classes.data import DataObject
from dotenv import load_dotenv
from datasets import load_dataset
from langchain_openai import OpenAIEmbeddings
import warnings

# Suppression des warnings non critiques
warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", message="Con004")
os.environ["WEAVIATE_DISABLE_WARNINGS"] = "1"

load_dotenv()

HOST = "wikiragweaviate"
HTTP_PORT = 8080
GRPC_PORT = 50051

# Nom de la collection (par défaut LinuxCommand, peut être changé via argument)
collection_name = sys.argv[1] if len(sys.argv) > 1 else "LinuxCommand"

# Connexion Weaviate v4
client_db = weaviate.connect_to_custom(
    http_host=HOST, http_port=HTTP_PORT, http_secure=False,
    grpc_host=HOST, grpc_port=GRPC_PORT, grpc_secure=False,
)
print("✅ Weaviate est connecté ✅")

# Configuration Langchain pour les embeddings
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

print(f"📥 Chargement du dataset hrsvrn/linux-commands-dataset avec Langchain…")
print(f"🎯 Collection cible : '{collection_name}'")

# Chargement du dataset avec datasets (plus fiable)
ds = load_dataset("hrsvrn/linux-commands-dataset", split="train[:50]")

# Préparation des données pour insertion
batch = []
for item in ds:
    description = (item.get("input") or "").strip()
    command = (item.get("output") or "").strip()
    
    if description and command:
        # Génération de l'embedding avec Langchain
        embedding = embeddings.embed_query(f"{description}\n{command}")
        
        # Création de l'objet Weaviate v4
        data_obj = DataObject(
            properties={
                "command": command,
                "description": description,
            },
            vector=embedding,
        )
        batch.append(data_obj)

print(f"📝 {len(batch)} documents préparés pour l'indexation")

# Insertion directe avec Weaviate v4
collection = client_db.collections.get(collection_name)
collection.data.insert_many(batch)

print(f"✅ {len(batch)} commandes Linux indexées dans '{collection_name}' avec Langchain ✅")
client_db.close()
print("🔒 Fin de la connexion à Weaviate ✅")
