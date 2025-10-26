import weaviate
import json

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

client = weaviate.WeaviateClient(connection)
client.connect()

query = "what causes global warming?"

res = client.collections.get("Tweet").query.near_text(
    query=query,
    limit=5,
    return_properties=["text", "source"]
)

client.close()

data = []
for obj in res.objects:
    data.append({
        "text": obj.properties.get("text"),
        "source": obj.properties.get("source")
    })

print(json.dumps({"results": data}, indent=2))
