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

# Gestion intelligente de la collection existante
collection_name = "LinuxCommand"

if client.collections.exists(collection_name):
    print(f"⚠️  La collection '{collection_name}' existe déjà !")
    print("\nQue souhaitez-vous faire ?")
    print("1. Supprimer et recréer la même collection")
    print("2. Créer une nouvelle collection avec un nom différent")
    print("3. Ignorer, ne rien faire")
    
    while True:
        choice = input("\nVotre choix (1/2/3) : ").strip()
        
        if choice == "1":
            print(f"🗑️ Suppression de la collection '{collection_name}'...")
            client.collections.delete(collection_name)
            time.sleep(1)
            print(f"🛠️ Création de la nouvelle collection '{collection_name}'…")
            break
            
        elif choice == "2":
            new_name = input("Entrez le nouveau nom de collection : ").strip()
            if not new_name:
                print("❌ Nom vide, veuillez réessayer.")
                continue
            collection_name = new_name
            print(f"🛠️ Création de la nouvelle collection '{collection_name}'…")
            break
            
        elif choice == "3":
            print("✅ Aucune modification effectuée.")
            client.close()
            sys.exit(0)
            
        else:
            print("❌ Choix invalide. Veuillez entrer 1, 2 ou 3.")
else:
    print(f"🛠️ Création de la nouvelle collection '{collection_name}'…")

# Création de la collection
client.collections.create(
    name=collection_name,
    properties=[
        Property(name="command", data_type=DataType.TEXT),
        Property(name="description", data_type=DataType.TEXT),
    ],
    vector_index_config=Configure.VectorIndex.hnsw()
)

print(f"✅ La collection '{collection_name}' est créée avec succès ✅")
client.close()
