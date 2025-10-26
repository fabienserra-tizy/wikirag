import weaviate
from weaviate.classes.config import Property, DataType, Configure
import requests
import sys
import time

HOST = "wikiragweaviate"
HTTP_PORT = 8080
GRPC_PORT = 50051

# Health check
try:
    r = requests.get(f"http://{HOST}:{HTTP_PORT}/v1/.well-known/ready", timeout=5)
    print("⏳ Vérification de l'instance Weaviate…")
    print("✅ Weaviate semble accessible :", r.status_code)
except Exception as e:
    print("❌ Weaviate semble inaccessible :", e)
    sys.exit(1)

# Connexion client v4
client = weaviate.connect_to_custom(
    http_host=HOST, http_port=HTTP_PORT, http_secure=False,
    grpc_host=HOST, grpc_port=GRPC_PORT, grpc_secure=False
)
print("✅ Le client Weaviate est connecté ✅")

# Reset
if client.collections.exists("LinuxCommand"):
    print("🗑️ Suppression de la collection LinuxCommand...")
    client.collections.delete("LinuxCommand")
    time.sleep(1)

print("🛠️ Création de la nouvelle collection LinuxCommand…")

client.collections.create(
    name="LinuxCommand",
    properties=[
        Property(name="command", data_type=DataType.TEXT),
        Property(name="description", data_type=DataType.TEXT),
    ],
    vector_index_config=Configure.VectorIndex.hnsw()
)

print("✅ La collection LinuxCommand est OK ✅")
client.close()
