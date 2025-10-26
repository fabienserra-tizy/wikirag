import weaviate
from datasets import load_dataset

client = weaviate.Client("http://wikiragnginx/weaviate")

ds = load_dataset("climate_fever", split="train[:500]")

for item in ds:
    text = item["claim"]
    if not text:
        continue

    client.data_object.create(
        data_object={"text": text, "source": "climate_fever"},
        class_name="Tweet"
    )

print("✅ 500 documents indexés")
