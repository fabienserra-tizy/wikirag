import weaviate
from weaviate.classes.config import Property, DataType, Configure
import requests, sys

HOST = "wikiragweaviate"
HTTP_PORT = 8080
GRPC_PORT = 50051

# Check Weaviate readiness
try:
    r = requests.get(f"http://{HOST}:{HTTP_PORT}/v1/.well-known/ready", timeout=5)
    print("✅ HTTP reachable:", r.status_code)
except Exception as e:
    print("❌ HTTP unreachable:", e)
    sys.exit(1)

# Init client (closed by default)
connection = weaviate.connect.ConnectionParams.from_params(
    http_host=HOST,
    http_port=HTTP_PORT,
    http_secure=False,
    grpc_host=HOST,
    grpc_port=GRPC_PORT,
    grpc_secure=False,
)

client = weaviate.WeaviateClient(connection)

# ✅ Open connection explicitly
client.connect()
print("✅ Client connected ✅")

schema_name = "Tweet"

existing = client.collections.list_all()

if schema_name in existing:
    print("ℹ️ Schéma 'Tweet' déjà existant")
else:
    client.collections.create(
        name=schema_name,
        properties=[
            Property(name="text", data_type=DataType.TEXT),
            Property(name="source", data_type=DataType.TEXT),
        ],
        vector_config=Configure.Vectors.text2vec_transformers()
    )
    print("✅ Schéma 'Tweet' créé avec succès")

# optional: close connection at end
client.close()
