import weaviate
from datasets import load_dataset
import time

HOST = "wikiragweaviate"
HTTP_PORT = 8080
GRPC_PORT = 50051

# Connect client
connection = weaviate.connect.ConnectionParams.from_params(
    http_host=HOST,
    http_port=HTTP_PORT,
    http_secure=False,
    grpc_host=HOST,
    grpc_port=GRPC_PORT,
    grpc_secure=False,
)
client = weaviate.WeaviateClient(connection)
client.connect()

# ✅ Correct split
ds = load_dataset("climate_fever", split="test[:500]")

count = 0
collection = client.collections.get("Tweet")

for item in ds:
    text = item["claim"]
    if not text:
        continue

    collection.data.insert(
        properties={
            "text": text,
            "source": "climate_fever",
        }
    )
    count += 1

client.close()

print(f"✅ Ingestion terminée : {count} documents indexés")
