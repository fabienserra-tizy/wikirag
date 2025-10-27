import os
import sys
import weaviate
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
import warnings

# Suppression des warnings non critiques
warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", message="Con004")
os.environ["WEAVIATE_DISABLE_WARNINGS"] = "1"

load_dotenv()

# Configuration Weaviate via variables d'environnement
HOST = os.getenv("WEAVIATE_HOST", "wikiragweaviate")
HTTP_PORT = int(os.getenv("WEAVIATE_HTTP_PORT", "8080"))
GRPC_PORT = int(os.getenv("WEAVIATE_GRPC_PORT", "50051"))
DEFAULT_COLLECTION = os.getenv("WEAVIATE_DEFAULT_COLLECTION", "NewCollection")

if len(sys.argv) < 2:
    print("Utilisation : python 03_query.py \"poser une question ici\" [nom_collection]")
    print("Exemple : python 03_query.py \"trouver les fichiers volumineux\" CollectionName")
    sys.exit(1)

question = sys.argv[1]
collection_name = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_COLLECTION

# Configuration Langchain
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Connexion Weaviate v4
client_db = weaviate.connect_to_custom(
    http_host=HOST, http_port=HTTP_PORT, http_secure=False,
    grpc_host=HOST, grpc_port=GRPC_PORT, grpc_secure=False,
)

collection = client_db.collections.get(collection_name)

# Configuration du LLM avec Langchain
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Template de prompt personnalisé
prompt_template = """
Tu es un assistant Linux expert.
Réponds avec une commande dans un bloc code + explication ultra courte.

Question: {question}

Contexte:
{context}

Réponds en français, concis.
"""

PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["question", "context"]
)

# Génération de l'embedding pour la question
question_embedding = embeddings.embed_query(question)

# Recherche hybride avec Weaviate v4 (plus de résultats pour éviter les doublons)
results = collection.query.hybrid(
    query=question,
    vector=question_embedding,
    alpha=0.5,
    limit=12
).objects

# Élimination des doublons et construction du contexte
seen_commands = set()
unique_results = []
context = ""

for obj in results:
    cmd = obj.properties.get("command", "")
    desc = obj.properties.get("description", "")
    
    # Éviter les doublons basés sur la commande
    if cmd and cmd not in seen_commands:
        seen_commands.add(cmd)
        unique_results.append(obj)
        context += f"- {cmd} :: {desc}\n"
        
        # Limiter à 4 résultats uniques maximum
        if len(unique_results) >= 4:
            break

# Utiliser les résultats uniques pour l'affichage
results = unique_results

# Génération de la réponse avec Langchain
prompt = PROMPT.format(question=question, context=context)
response = llm.invoke(prompt)

print(f"\n🔍 Question: {question}")
print(f"🎯 Collection: {collection_name}")
print("=" * 50)

print("\n== Réponse Langchain ==")
print(response.content)

print("\n== Sources utilisées ==")
for i, obj in enumerate(results, 1):
    cmd = obj.properties.get("command", "")
    desc = obj.properties.get("description", "")
    print(f"{i}. {cmd} :: {desc}")

client_db.close()
