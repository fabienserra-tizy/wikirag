#!/usr/bin/env python3
"""
Script d'aide pour le projet Linux RAG avec Langchain
Affiche les instructions d'utilisation et les exemples
"""

import sys

def print_help():
    print("""
🐧 Linux RAG - Assistant de commandes Linux
============================================================

🔧 VARIABLES D'ENVIRONNEMENT :

Les variables suivantes peuvent être configurées dans votre environnement :
- WEAVIATE_HOST="wikiragweaviate" (défaut)
- WEAVIATE_HTTP_PORT=8080 (défaut)
- WEAVIATE_GRPC_PORT=50051 (défaut)
- WEAVIATE_DEFAULT_COLLECTION="NewCollection" (défaut)
- OPENAI_API_KEY=sk-xxxx (requis)

📋 INSTRUCTIONS D'UTILISATION :

1️⃣  Création du schéma Weaviate :
   python 01_create_schema.py [nom_collection]
   
   Exemples :
   python 01_create_schema.py                    # Utilise la variable WEAVIATE_DEFAULT_COLLECTION
   python 01_create_schema.py CollectionName      # Crée la collection "CollectionName"
   
   Options disponibles si la collection existe déjà :
   - Supprimer et recréer la même collection
   - Créer une nouvelle collection avec un nom différent  
   - Ignorer, ne rien faire

2️⃣  Ingestion du dataset avec Langchain :
   python 02_ingest.py [nom_collection]
   
   Exemples :
   python 02_ingest.py                    # Utilise "NewCollection" par défaut
   python 02_ingest.py CollectionName   # Utilise "CollectionName"

3️⃣  Test en ligne de commande :
   python 03_query.py "question" [nom_collection]
   
   Exemples :
   python 03_query.py "trouver les fichiers volumineux"
   python 03_query.py "voir les processus" CollectionName

4️⃣  Interface web Gradio :
   python 04_gradio.py [nom_collection]
   
   Exemples :
   python 04_gradio.py                    # Utilise "NewCollection" par défaut
   python 04_gradio.py CollectionName   # Utilise "CollectionName"
   
   Accès : https://votre-domaine.com/rag

5️⃣  Suppression de collection :
   python 05_delete_collection.py <nom_collection>
   
   Exemples :
   python 05_delete_collection.py CollectionName
   python 05_delete_collection.py CollectionName2
   
   ⚠️  ATTENTION : Action IRRÉVERSIBLE !

6️⃣  Listing des collections :
   python 06_list_collections.py
   
   Affiche toutes les collections avec leurs statistiques

🔧 ARCHITECTURE LANGCHAIN :

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ HuggingFace     │───▶│ Langchain        │───▶│ Weaviate        │
│ Dataset         │    │ Document Loader  │    │ Vectorstore     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ RetrievalQA      │
                       │ Chain            │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ ChatOpenAI       │
                       │ (GPT-4o-mini)    │
                       └──────────────────┘

💡 EXEMPLES DE QUESTIONS :

- "Comment trouver tous les fichiers modifiés cette semaine ?"
- "Voir l'espace disque utilisé"
- "Compresser un dossier en tar.gz"
- "Installer un package avec apt"
- "Voir les processus qui consomment le plus de CPU"
- "Rechercher un fichier par nom"
- "Changer les permissions d'un fichier"

🎯 COLLECTIONS MULTIPLES :

Vous pouvez créer plusieurs collections pour différents usages :
- CollectionName (par défaut)
- CollectionName2 (version améliorée)
- CollectionName3 (pour les tests)
- etc.

Chaque collection est indépendante et peut contenir des données différentes.

📚 TECHNOLOGIES UTILISÉES :

- Langchain : Orchestration RAG complète
- HuggingFace : Chargement du dataset
- OpenAI : Embeddings + génération (GPT-4o-mini)
- Weaviate : Base de données vectorielle
- Gradio : Interface utilisateur web
- Docker : Containerisation

🔍 DÉPANNAGE :

Si vous rencontrez des erreurs :
1. Vérifiez que Weaviate est démarré : docker ps | grep weaviate
2. Vérifiez votre clé OpenAI : echo $OPENAI_API_KEY
3. Vérifiez que la collection existe : python 03_query.py "test" nom_collection

""")

if __name__ == "__main__":
    print_help()
