import os
import sys
import weaviate
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

if len(sys.argv) < 2:
    print("Usage: python 03_query.py \"ta question\"")
    sys.exit(1)

question = sys.argv[1]

client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client_db = weaviate.connect_to_custom(
    http_host="wikiragweaviate", http_port=8080, http_secure=False,
    grpc_host="wikiragweaviate", grpc_port=50051, grpc_secure=False,
)

collection = client_db.collections.get("LinuxCommand")

# Vectorisation de la requête côté Python
emb = client_ai.embeddings.create(
    model="text-embedding-3-small",
    input=question
).data[0].embedding

results = collection.query.near_vector(
    near_vector=emb,
    limit=4
).objects

context = ""
for obj in results:
    cmd = obj.properties.get("command", "")
    desc = obj.properties.get("description", "")
    context += f"- {cmd} :: {desc}\n"

prompt = f"""
Tu es un assistant Linux.
Donne une commande dans un bloc code + une explication très courte.

Question: {question}

Contexte:
{context}
"""

resp = client_ai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Réponds en français, concis."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.0
)

print("\n== Réponse ==")
print(resp.choices[0].message.content)

client_db.close()
