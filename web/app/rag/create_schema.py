import weaviate

client = weaviate.Client("http://wikiragnginx/weaviate")

schema = {
    "class": "Tweet",
    "vectorizer": "text2vec-transformers",
    "properties": [
        {"name": "text", "dataType": ["text"]},
        {"name": "source", "dataType": ["text"]}
    ]
}

if "Tweet" not in [c['class'] for c in client.schema.get()["classes"]]:
    client.schema.create_class(schema)
    print("✅ Schéma créé")
else:
    print("ℹ️ Schéma déjà existant")