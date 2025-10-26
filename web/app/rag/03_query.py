import os
import sys
import weaviate
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

if len(sys.argv) < 2:
    print("Usage: python 03_query.py \"ta question ici\"")
    sys.exit(1)

question = sys.argv[1]

client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client_db = weaviate.connect_to_custom(
    http_host="wikiragweaviate", http_port=8080, http_secure=False,
    grpc_host="wikiragweaviate", grpc_port=50051, grpc_secure=False,
)

collection = client_db.collections.get("LinuxCommand")

# ✅ Embeddings côté client
emb = client_ai.embeddings.create(
    model="text-embedding-3-small",
    input=question
).data[0].embedding

# ✅ Hybrid local-vector search
results = collection.query.hybrid(
    query=question,
    vector=emb,
    alpha=0.5,
    limit=4
).objects

context = ""
for obj in results:
    cmd = obj.properties.get("command", "")
    desc = obj.properties.get("description", "")
    context += f"- {cmd} :: {desc}\n"

prompt = f"""
Tu es un assistant Linux.
Réponds avec une commande dans un bloc code + explication ultra courte.

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
