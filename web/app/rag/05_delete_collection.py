#!/usr/bin/env python3
"""
Script de suppression de collection Weaviate
Supprime une collection spécifiée en paramètre avec confirmation
"""

import os
import sys
import weaviate
from dotenv import load_dotenv
import warnings

# Suppression des warnings non critiques
warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", message="Con004")
os.environ["WEAVIATE_DISABLE_WARNINGS"] = "1"

load_dotenv()

# Configuration Weaviate via variables d'environnement
HOST = os.getenv("WEAVIATE_HOST", "wikiragweaviate")
HTTP_PORT = int(os.getenv("WEAVIATE_HTTP_PORT", "8080"))
GRPC_PORT = int(os.getenv("WEAVIATE_GRPC_PORT", "50051"))

def delete_collection(collection_name: str):
    """Supprime une collection Weaviate avec confirmation"""
    
    # Connexion Weaviate v4
    try:
        client_db = weaviate.connect_to_custom(
            http_host=HOST, http_port=HTTP_PORT, http_secure=False,
            grpc_host=HOST, grpc_port=GRPC_PORT, grpc_secure=False,
        )
        print(f"✅ Connexion à Weaviate réussie ({HOST}:{HTTP_PORT})")
    except Exception as e:
        print(f"❌ Erreur de connexion à Weaviate : {e}")
        sys.exit(1)
    
    # Vérification de l'existence de la collection
    if not client_db.collections.exists(collection_name):
        print(f"❌ La collection '{collection_name}' n'existe pas.")
        print("📋 Collections disponibles :")
        try:
            collections = client_db.collections.list_all()
            if collections:
                for collection in collections:
                    print(f"   - {collection}")
            else:
                print("   (Aucune collection trouvée)")
        except Exception as e:
            print(f"   (Erreur lors de la récupération : {e})")
        client_db.close()
        sys.exit(1)
    
    # Affichage des informations de la collection
    try:
        collection = client_db.collections.get(collection_name)
        count = collection.aggregate.over_all(total_count=True).total_count
        print(f"📊 Collection '{collection_name}' trouvée")
        print(f"📈 Nombre d'objets : {count}")
    except Exception as e:
        print(f"⚠️  Impossible de récupérer les statistiques : {e}")
        count = "inconnu"
    
    # Confirmation de suppression
    print(f"\n⚠️  ATTENTION : Vous êtes sur le point de supprimer la collection '{collection_name}'")
    print(f"📊 Cette collection contient {count} objets")
    print("🗑️  Cette action est IRRÉVERSIBLE !")
    
    while True:
        confirmation = input(f"\nÊtes-vous sûr de vouloir supprimer '{collection_name}' ? (oui/non) : ").strip().lower()
        
        if confirmation in ['oui', 'o', 'yes', 'y']:
            break
        elif confirmation in ['non', 'n', 'no']:
            print("✅ Suppression annulée.")
            client_db.close()
            sys.exit(0)
        else:
            print("❌ Réponse invalide. Veuillez répondre 'oui' ou 'non'.")
    
    # Suppression de la collection
    try:
        print(f"🗑️  Suppression de la collection '{collection_name}'...")
        client_db.collections.delete(collection_name)
        print(f"✅ Collection '{collection_name}' supprimée avec succès !")
        
        # Vérification de la suppression
        if not client_db.collections.exists(collection_name):
            print(f"✅ Vérification : La collection '{collection_name}' n'existe plus.")
        else:
            print(f"⚠️  Attention : La collection '{collection_name}' existe encore.")
            
    except Exception as e:
        print(f"❌ Erreur lors de la suppression : {e}")
        sys.exit(1)
    finally:
        client_db.close()
        print("🔒 Connexion fermée.")

def main():
    """Fonction principale"""
    
    if len(sys.argv) < 2:
        print("""
🗑️  Suppression de collection Weaviate
=====================================

Utilisation : python 05_delete_collection.py <nom_collection>

Exemples :
  python 05_delete_collection.py CollectionName1
  python 05_delete_collection.py CollectionName2
  python 05_delete_collection.py CollectionName3

⚠️  ATTENTION : Cette action est IRRÉVERSIBLE !
""")
        sys.exit(1)
    
    collection_name = sys.argv[1]
    
    # Validation du nom de collection
    if not collection_name or not collection_name.strip():
        print("❌ Nom de collection invalide.")
        sys.exit(1)
    
    collection_name = collection_name.strip()
    
    print(f"🎯 Suppression de la collection : '{collection_name}'")
    print(f"🔗 Connexion à Weaviate : {HOST}:{HTTP_PORT}")
    print("=" * 50)
    
    delete_collection(collection_name)

if __name__ == "__main__":
    main()
