#!/usr/bin/env python3
"""
Script d'aide pour le projet Linux RAG avec Langchain
Affiche les instructions d'utilisation et les exemples
"""

import sys

def print_help():
    print("""
🐧 Linux RAG - Assistant de Commandes Linux avec Langchain
============================================================

📋 INSTRUCTIONS D'UTILISATION :

1️⃣  Création du schéma Weaviate :
   python 01_create_schema.py
   
   Options disponibles si la collection existe déjà :
   - Supprimer et recréer la même collection
   - Créer une nouvelle collection avec un nom différent  
   - Ignorer, ne rien faire

2️⃣  Ingestion du dataset avec Langchain :
   python 02_ingest.py [nom_collection]
   
   Exemples :
   python 02_ingest.py                    # Utilise "LinuxCommand" par défaut
   python 02_ingest.py LinuxCommandsV2   # Utilise "LinuxCommandsV2"

3️⃣  Test en ligne de commande :
   python 03_query.py "question" [nom_collection]
   
   Exemples :
   python 03_query.py "trouver les fichiers volumineux"
   python 03_query.py "voir les processus" LinuxCommandsV2

4️⃣  Interface web Gradio :
   python 04_gradio.py
   
   Accès : https://votre-domaine.com/rag

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
- LinuxCommand (par défaut)
- LinuxCommandsV2 (version améliorée)
- LinuxCommandsTest (pour les tests)
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
