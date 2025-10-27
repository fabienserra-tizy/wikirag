# Linux RAG — Assistant de commandes Linux intelligent

Un système RAG moderne qui transforme vos questions en langage naturel en commandes Linux précises et sécurisées. Votre copilote shell bienveillant et intelligent, entièrement construit avec Langchain.

---

## 📋 Description

Linux RAG est un assistant intelligent qui utilise l'IA pour vous aider à trouver les bonnes commandes Linux. Posez une question en français, recevez la commande exacte à exécuter avec une explication claire et des sources fiables.

**Fonctionnalités clés :**
- 🔗 **Architecture Langchain complète** : Embeddings, Chains, Prompts
- 🔍 **Recherche vectorielle hybride** (BM25 + embeddings OpenAI)
- ⚡ **Mode API/CLI** pour intégration et tests
- 🎯 **Déduplication intelligente** des résultats
- 🏗️ **Support multi-collections** Weaviate
- 🚀 **Interface Gradio moderne** avec thème optimisé

---

## 🏗️ Architecture Langchain

```
┌──────────────────────────────────────────────────────────────┐
│                    Linux RAG System                          │
│                    (Architecture Langchain)                  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐  │
│  │   Gradio    │    │   Langchain  │    │    Weaviate     │  │
│  │     UI      │◄──►│   Backend    │◄──►│   Vector DB     │  │
│  │  (Port 7860)│    │  (Orchestr.) │    │   (Port 8080)   │  │
│  └─────────────┘    └──────────────┘    └─────────────────┘  │
│         │                   │                   │            │
│         │                   │                   │            │
│         ▼                   ▼                   ▼            │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐  │
│  │   Nginx     │    │   OpenAI     │    │   HuggingFace   │  │
│  │  (Traefik)  │    │     API      │    │   Dataset       │  │
│  │  (Port 80)  │    │ (Embeddings) │    │ Linux Commands  │  │
│  └─────────────┘    └──────────────┘    └─────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Flux de données Langchain :**
1. **Question utilisateur** → Interface Gradio
2. **Embedding** → `OpenAIEmbeddings` (text-embedding-3-small)
3. **Recherche hybride** → Weaviate v4 (BM25 + vector)
4. **Déduplication** → Algorithme intelligent des doublons
5. **Génération** → `ChatOpenAI` (GPT-4o-mini) avec `PromptTemplate`
6. **Affichage** → Interface utilisateur avec sources

---

## 🚀 Versions et Technologies

| Composant | Version | Rôle |
|-----------|---------|------|
| **Python** | 3.12 | Orchestration et logique métier |
| **Langchain** | 1.0.2+ | Framework RAG principal |
| **Langchain-Core** | 0.3.0+ | Composants de base |
| **Langchain-OpenAI** | 1.0.1+ | Intégration OpenAI |
| **Langchain-Community** | 0.3.0+ | Loaders et vectorstores |
| **Weaviate** | 1.33.1 | Base de données vectorielle |
| **OpenAI API** | Latest | Embeddings + génération |
| **Gradio** | 4.44.0+ | Interface utilisateur web |
| **Docker** | Latest | Containerisation |
| **Nginx** | 1.27.0 | Reverse proxy et routing |

---

## 💡 Concept Langchain

### Principe RAG (Retrieval-Augmented Generation)

1. **Chargement** : `datasets.load_dataset()` via HuggingFace
2. **Vectorisation** : `OpenAIEmbeddings` pour chaque commande
3. **Stockage** : Weaviate v4 avec schéma optimisé
4. **Recherche** : Recherche hybride BM25 + vectorielle
5. **Déduplication** : Algorithme intelligent des doublons
6. **Génération** : `ChatOpenAI` avec `PromptTemplate` personnalisé

### Architecture Langchain Détaillée

```python
# Composants Langchain utilisés
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from datasets import load_dataset  # Chargement HuggingFace
```

---

## 🛠️ Installation et lancement avec `tizy run`

> Note : `tizy run` est un raccourci de docker-compose up 

### Prérequis

1. **Variables d'environnement**

Modifiez le fichier `./docker/env.sh` :

```bash
VHOST_TRAEFIK=votre-domaine.com # (exemple wikirag.fserra.databird.io)
OPENAI_API_KEY=sk-xxxx
```

2. **Dépendances système** - Docker et Docker Compose installés et le raccourci `tizy run`

### Instructions étape par étape

#### 1. 🐳 Démarrage des conteneurs
```bash
tizy run
```

#### 2. 🔗 Connexion au conteneur Python
```bash
docker exec -it wikirag-python bash
# ou
tizy connect
```

#### 3. 📁 Navigation vers le dossier RAG
```bash
cd /usr/src/app/rag
```

#### 4. 🗄️ Création du schéma Weaviate (avec gestion intelligente)
```bash
python 01_create_schema.py
```
**Rôle :** Initialise la collection `LinuxCommand` dans Weaviate avec gestion intelligente des collections existantes.

**Options disponibles :**
- Supprimer et recréer la même collection
- Créer une nouvelle collection avec un nom différent
- Ignorer, ne rien faire

#### 5. 📥 Ingestion du dataset avec Langchain
```bash
python 02_ingest.py [nom_collection]
```
**Rôle :** 
- Charge le dataset `hrsvrn/linux-commands-dataset` (500 premières entrées)
- Génère les embeddings OpenAI via `OpenAIEmbeddings`
- Insère les données vectorisées dans Weaviate v4

**Exemples :**
```bash
python 02_ingest.py                    # Utilise "LinuxCommand" par défaut
python 02_ingest.py LinuxCommandsV2   # Utilise "LinuxCommandsV2"
```

#### 6. 🧪 Test en mode API/CLI avec Langchain
```bash
python 03_query.py "question" [nom_collection]
```
**Rôle :** Interface en ligne de commande utilisant l'architecture Langchain complète.

**Exemples :**
```bash
python 03_query.py "trouver les fichiers volumineux"
python 03_query.py "voir les processus" LinuxCommandsV2
```

#### 7. 🌐 Lancement de l'interface Gradio avec Langchain
```bash
python 04_gradio.py
```
**Rôle :** Démarre l'interface web complète avec :
- Architecture Langchain intégrée
- Recherche hybride avec déduplication
- Interface moderne avec thème Soft
- Affichage des sources utilisées
- Gestion d'erreurs robuste

✅ L'interface est accessible via https://votre-domaine.com/rag

#### 8. 📚 Aide et documentation
```bash
python 00_help.py
```
**Rôle :** Affiche la documentation complète et les exemples d'utilisation.

---

## 📊 Dataset Linux Commands

### Source
- **Dataset** : `hrsvrn/linux-commands-dataset` (HuggingFace)
- **Taille** : 500 commandes sélectionnées (optimisé pour les tests)
- **Format** : Paires question/réponse en anglais
- **Couverture** : Filesystem, réseau, processus, administration...

### Structure des données
```json
{
  "input": "Description de la tâche en anglais",
  "output": "Commande Linux correspondante"
}
```

### Exemples d'entrées
- **Input** : "Recursively change ownership of a directory to user 'john'"
- **Output** : "chown -R john:john /path/to/directory"

- **Input** : "Find all files modified in the last 7 days"
- **Output** : "find . -type f -mtime -7"

### Vectorisation Langchain
- **Modèle** : `text-embedding-3-small` (OpenAI)
- **Dimension** : 1536
- **Méthode** : Concaténation description + commande
- **Index** : HNSW (Hierarchical Navigable Small World)
- **Framework** : `OpenAIEmbeddings` de Langchain

---

## 🔧 Configuration avancée

### Paramètres Weaviate v4
```python
# Recherche hybride
alpha=0.5          # Équilibre BM25/vectoriel
limit=12           # Nombre de candidats (pour déduplication)
return_metadata=["score"]  # Scores de pertinence

# Index vectoriel
Configure.VectorIndex.hnsw()  # Algorithme HNSW
```

### Paramètres Langchain OpenAI
```python
# Embeddings
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Génération
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.0,  # Déterministe
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
```

### Déduplication intelligente
```python
# Algorithme de déduplication
seen_commands = set()
unique_results = []

for obj in results:
    cmd = obj.properties.get("command", "")
    if cmd and cmd not in seen_commands:
        seen_commands.add(cmd)
        unique_results.append(obj)
        if len(unique_results) >= 4:
            break
```

---

## 📁 Structure du projet

```
root/
├── docker/
│   ├── docker-compose.yml      # Configuration des conteneurs
│   ├── nginx/
│   │   ├── nginx.conf          # Configuration Nginx
│   │   └── vhost.conf          # Virtual host
│   └── start.sh                # Script de démarrage
├── web/app/rag/
│   ├── 00_help.py             # Script d'aide et documentation
│   ├── 01_create_schema.py     # Création schéma Weaviate (gestion intelligente)
│   ├── 02_ingest.py           # Ingestion dataset avec Langchain
│   ├── 03_query.py            # Interface CLI/API avec Langchain
│   ├── 04_gradio.py           # Interface web Gradio avec Langchain
│   └── requirements.txt        # Dépendances Python (Langchain inclus)
└── README.md                   # Documentation complète
```

---

## 🧪 Exemples d'utilisation

### Question simple
**Input :** "Comment voir l'espace disque utilisé ?"
**Output :**
```bash
df -h
```
Affiche l'utilisation des disques en format lisible.

### Question complexe
**Input :** "Trouver tous les fichiers .log plus gros que 100MB modifiés cette semaine"
**Output :**
```bash
find /var/log -name "*.log" -size +100M -mtime -7
```
Recherche les fichiers de log volumineux modifiés récemment.

### Interface Gradio
- **Question** : "Compresser un dossier en tar.gz"
- **Réponse** : Commande `tar -czf archive.tar.gz dossier/`
- **Sources** : Affichage des 4 sources les plus pertinentes

---

## 🔍 Requêtes GraphQL Weaviate

### Accès à l'interface GraphQL
```
https://votre-domaine.com/v1/graphql
```

### Requêtes utiles

#### 📋 Lister toutes les commandes (limité)
```graphql
{
  Get {
    LinuxCommand(limit: 10) {
      description
      command
    }
  }
}
```

#### 🔍 Recherche textuelle
```graphql
{
  Get {
    LinuxCommand(
      bm25: {
        query: "find files"
      }
      limit: 5
    ) {
      description
      command
      _additional {
        score
      }
    }
  }
}
```

#### 📊 Statistiques de la collection
```graphql
{
  Aggregate {
    LinuxCommand {
      meta {
        count
      }
    }
  }
}
```

---

## 🎯 Fonctionnalités avancées

### Gestion multi-collections
- **Collections multiples** : Support de plusieurs collections simultanées
- **Nommage flexible** : Création de collections avec noms personnalisés
- **Isolation des données** : Chaque collection est indépendante

### Déduplication intelligente
- **Élimination des doublons** : Algorithme basé sur les commandes uniques
- **Diversité des résultats** : Recherche élargie pour plus de variété
- **Ordre préservé** : Les résultats les plus pertinents sont prioritaires

### Interface utilisateur moderne
- **Thème Soft** : Design épuré et professionnel
- **Responsive** : Adaptation mobile et desktop
- **Sources visibles** : Affichage des sources utilisées
- **Gestion d'erreurs** : Messages d'erreur clairs et informatifs

---

## 👤 Auteur

**Fabien SERRA-MONTINERI**  
*Majeur de promotion - Formation Data Science*

---

## 📝 Notes techniques

### Améliorations apportées
- **Architecture hybride** : Weaviate v4 + Langchain pour compatibilité maximale
- **Gestion des warnings** : Suppression des warnings non critiques
- **Robustesse** : Gestion d'erreurs et validation des entrées
- **Performance** : Déduplication et optimisation des requêtes

### Technologies modernes
- **Langchain 1.0+** : Framework RAG de référence
- **Weaviate v4** : Base vectorielle nouvelle génération
- **GPT-4o-mini** : Modèle OpenAI optimisé
- **Docker** : Containerisation complète