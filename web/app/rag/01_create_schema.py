import weaviate
from weaviate.classes.config import Property, DataType, Configure
import requests
import sys
import time

HOST = "wikiragweaviate"
HTTP_PORT = 8080
GRPC_PORT = 50051

try:
    r = requests.get(f"http://{HOST}:{HTTP_PORT}/v1/.well-known/ready", timeout=5)
    print("⏳ Vérification Weaviate…")
    print("✅ HTTP accessible:", r.status_code)
except Exception as e:
    print("❌ HTTP inaccessible:", e)
    sys.exit(1)

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
print("✅ Client connecté ✅")

if client.collections.exists("LinuxCommand"):
    print("🗑️ Suppression ancienne collection...")
    client.collections.delete("LinuxCommand")
    time.sleep(1)

print("🛠️ Nouveau schéma…")

client.collections.create(
    name="LinuxCommand",
    properties=[
        Property(name="command", data_type=DataType.TEXT),
        Property(name="description", data_type=DataType.TEXT),
    ],
    vectorizer_config=Configure.Vectorizer.none(),
)

print("✅ Schéma OK ✅")
client.close()
