import weaviate
import json

client = weaviate.Client("http://wikiragnginx/weaviate")

query = "impact of global warming"
result = client.query.get(
    class_name="Tweet",
    properties=["text", "source"],
).with_near_text({
    "concepts": [query]
}).with_limit(3).do()

print(json.dumps(result, indent=2))
