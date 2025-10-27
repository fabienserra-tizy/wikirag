#!/usr/bin/env python3
"""
Script de listing des collections Weaviate
Affiche toutes les collections disponibles avec leurs statistiques
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

def list_collections():
    """Liste toutes les collections Weaviate avec leurs statistiques"""
    
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
    
    try:
        # Récupération de toutes les collections
        collections = client_db.collections.list_all()
        
        if not collections:
            print("📋 Aucune collection trouvée dans Weaviate.")
            return
        
        print(f"\n📋 Collections disponibles ({len(collections)} trouvée(s)) :")
        print("=" * 80)
        
        # Affichage des collections avec statistiques
        for i, collection_name in enumerate(collections, 1):
            try:
                collection = client_db.collections.get(collection_name)
                
                # Récupération des statistiques
                try:
                    count = collection.aggregate.over_all(total_count=True).total_count
                except Exception:
                    count = "N/A"
                
                # Récupération des propriétés
                try:
                    properties = collection.config.get().properties
                    prop_names = [prop.name for prop in properties]
                    properties_str = ", ".join(prop_names) if prop_names else "Aucune"
                except Exception:
                    properties_str = "N/A"
                
                # Affichage formaté
                print(f"{i:2d}. 📁 {collection_name}")
                print(f"    📊 Objets : {count}")
                print(f"    🔧 Propriétés : {properties_str}")
                print()
                
            except Exception as e:
                print(f"{i:2d}. 📁 {collection_name}")
                print(f"    ❌ Erreur lors de la récupération des détails : {e}")
                print()
        
        print("=" * 80)
        print(f"📈 Total : {len(collections)} collection(s)")
        
        # Suggestions d'utilisation
        if collections:
            print(f"\n💡 Suggestions d'utilisation :")
            print(f"   • Tester une collection : python 03_query.py \"question\" {collections[0]}")
            print(f"   • Interface web : python 04_gradio.py {collections[0]}")
            print(f"   • Supprimer une collection : python 05_delete_collection.py <nom>")
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des collections : {e}")
        sys.exit(1)
    finally:
        client_db.close()
        print("🔒 Connexion fermée.")

def main():
    """Fonction principale"""
    
    # Support des arguments optionnels
    show_help = False
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', 'help']:
            show_help = True
    
    if show_help:
        print("""
📋 Listing des collections Weaviate
==================================

Utilisation : python 06_list_collections.py [options]

Options :
  -h, --help, help    Affiche cette aide

Exemples :
  python 06_list_collections.py
  python 06_list_collections.py --help

Ce script affiche :
  • Toutes les collections disponibles
  • Le nombre d'objets par collection
  • Les propriétés de chaque collection
  • Des suggestions d'utilisation
""")
        sys.exit(0)
    
    print("📋 Listing des collections Weaviate")
    print(f"🔗 Connexion à : {HOST}:{HTTP_PORT}")
    print("=" * 50)
    
    list_collections()

if __name__ == "__main__":
    main()
