import os
import weaviate
from datasets import load_dataset
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

HOST = "wikiragweaviate"
HTTP_PORT = 8080
GRPC_PORT = 50051

connection = weaviate.connect.ConnectionParams.from_params(
    http_host=HOST,
    http_port=HTTP_PORT,
    http_secure=False,
    grpc_host=HOST,
    grpc_port=GRPC_PORT,
    grpc_secure=False,
)
client_db = weaviate.WeaviateClient(connection)
client_db.connect()
print("✅ Connecté Weaviate")

api_key = os.getenv("OPENAI_API_KEY")
client_ai = OpenAI(api_key=api_key)

print("📥 Chargement du dataset…")
ds = load_dataset("hrsvrn/linux-commands-dataset", split="train[:500]")

collection = client_db.collections.get("LinuxCommand")

count = 0
for item in ds:
    desc = (item.get("input") or "").strip()
    cmd = (item.get("output") or "").strip()

    if not desc or not cmd:
        continue

    # Embedding sur description + commande
    text_for_embedding = f"{desc}\n{cmd}"

    emb = client_ai.embeddings.create(
        model="text-embedding-3-small",
        input=text_for_embedding
    ).data[0].embedding

    collection.data.insert(
        properties={
            "command": cmd,
            "description": desc
        },
        vector=emb
    )
    count += 1

print(f"✅ {count} commandes indexées ✅")
client_db.close()
print("🔒 Weaviate fermé ✅")
