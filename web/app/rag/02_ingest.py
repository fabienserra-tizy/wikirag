import os
import weaviate
from weaviate.classes.data import DataObject
from datasets import load_dataset
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

HOST = "wikiragweaviate"
HTTP_PORT = 8080
GRPC_PORT = 50051

client_db = weaviate.connect_to_custom(
    http_host=HOST, http_port=HTTP_PORT, http_secure=False,
    grpc_host=HOST, grpc_port=GRPC_PORT, grpc_secure=False,
)
print("✅ Connecté Weaviate")

client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("📥 Chargement du dataset…")
ds = load_dataset("hrsvrn/linux-commands-dataset", split="train[:500]")

collection = client_db.collections.get("LinuxCommand")

batch = []

for item in ds:
    desc = (item.get("input") or "").strip()
    cmd = (item.get("output") or "").strip()
    if not desc or not cmd:
        continue

    emb = client_ai.embeddings.create(
        model="text-embedding-3-small",
        input=f"{desc}\n{cmd}"
    ).data[0].embedding

    batch.append(
        DataObject(
            properties={
                "command": cmd,
                "description": desc,
            },
            vector=emb,
        )
    )

# ✅ insertion propre & valide
collection.data.insert_many(batch)

print(f"✅ {len(batch)} commandes indexées ✅")
client_db.close()
print("🔒 Weaviate fermé ✅")
