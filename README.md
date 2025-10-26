# 🐧 Linux RAG — Assistant de Commandes Linux Intelligent

Un système RAG (Retrieval-Augmented Generation) qui transforme vos questions en langage naturel en commandes Linux précises et sécurisées. Votre copilote shell bienveillant et intelligent.

---

## 📋 Description

Linux RAG est un assistant intelligent qui utilise l'IA pour vous aider à trouver les bonnes commandes Linux. Posez une question en français, recevez la commande exacte à exécuter avec une explication claire et des alertes de sécurité automatiques.

**Fonctionnalités clés :**
- 🔍 Recherche vectorielle hybride (BM25 + embeddings)
- 🛡️ Alertes de sécurité automatiques (`rm -rf`, `dd`, etc.)
- 📝 Historique des requêtes persistantes
- 🎨 Interface Gradio moderne avec thème terminal
- ⚡ Mode API/CLI pour intégration
- 🔄 Re-ranking intelligent par LLM

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Linux RAG System                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐   │
│  │   Gradio    │    │   Python     │    │    Weaviate     │   │
│  │     UI      │◄──►│   Backend    │◄──►│   Vector DB     │   │
│  │  (Port 7860)│    │  (Orchestr.) │    │   (Port 8080)   │   │
│  └─────────────┘    └──────────────┘    └─────────────────┘   │
│         │                   │                   │             │
│         │                   │                   │             │
│         ▼                   ▼                   ▼             │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐   │
│  │   Nginx     │    │   OpenAI     │    │   Dataset       │   │
│  │  (Traefik)  │    │     API      │    │  Linux Commands │   │
│  │  (Port 80)  │    │ (Embeddings) │    │   (500 items)   │   │
│  └─────────────┘    └──────────────┘    └─────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Flux de données :**
1. **Question utilisateur** → Interface Gradio
2. **Embedding** → OpenAI API (text-embedding-3-small)
3. **Recherche hybride** → Weaviate (BM25 + vector)
4. **Re-ranking** → LLM (GPT-4o-mini)
5. **Génération réponse** → LLM avec contexte enrichi
6. **Affichage** → Interface utilisateur

---

## 🚀 Versions

| Composant | Version | Rôle |
|-----------|---------|------|
| **Python** | 3.12 | Orchestration et logique métier |
| **Weaviate** | 1.33.1 | Base de données vectorielle |
| **OpenAI API** | Latest | Embeddings + génération |
| **Gradio** | 4.44.0+ | Interface utilisateur web |
| **Docker** | Latest | Containerisation |
| **Nginx** | 1.27.0 | Reverse proxy et routing |

---

## 💡 Concept

### Principe RAG (Retrieval-Augmented Generation)

1. **Indexation** : Le dataset de commandes Linux est vectorisé et stocké dans Weaviate
2. **Recherche** : La question utilisateur est convertie en embedding pour une recherche sémantique
3. **Récupération** : Les commandes les plus pertinentes sont extraites via recherche hybride
4. **Re-ranking** : Un LLM classe les résultats par pertinence
5. **Génération** : Un LLM génère la réponse finale avec la commande optimisée

---

## 🛠️ Installation et Lancement avec `tizy run`

### Prérequis

1. **Variables d'environnement** - Modifiez bien le fichier `./docker/env.sh`
```bash
OPENAI_API_KEY=sk-xxxx
VHOST_TRAEFIK=votre-domaine.com
```

2. **Dépendances système** - Docker et Docker Compose installés

### Instructions étape par étape

#### 1. 🐳 Démarrage des conteneurs
```bash
tizy run
```

#### 2. 🔗 Connexion au conteneur Python
```bash
docker exec -it wikirag-python bash
```

#### 3. 📁 Navigation vers le dossier RAG
```bash
cd /usr/src/app/rag
```

#### 4. 🗄️ Création du schéma Weaviate
```bash
python 01_create_schema.py
```
**Rôle :** Initialise la collection `LinuxCommand` dans Weaviate avec les propriétés `command` et `description`, configure l'index vectoriel HNSW.

#### 5. 📥 Ingestion du dataset
```bash
python 02_ingest.py
```
**Rôle :** 
- Charge le dataset `hrsvrn/linux-commands-dataset` (500 premières entrées)
- Génère les embeddings OpenAI pour chaque commande
- Insère les données vectorisées dans Weaviate

#### 6. 🧪 Test en mode API/CLI
```bash
python 03_query.py "trouver les fichiers modifiés depuis 7 jours"
```
**Rôle :** Interface en ligne de commande pour tester le système RAG sans interface graphique.

#### 7. 🌐 Lancement de l'interface Gradio
```bash
python 04_gradio.py
```
**Rôle :** Démarre l'interface web complète avec :
- Interface utilisateur moderne
- Recherche hybride avec re-ranking
- Historique des requêtes
- Alertes de sécurité
- Thème terminal stylé

✅ L'interface est accessible via https://votre-domaine.com/rag

---

## 📊 Dataset Linux Commands

### Source
- **Dataset** : `hrsvrn/linux-commands-dataset` (Hugging Face)
- **Taille** : 500 commandes sélectionnées
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

- **Input** : "dstat -cdngy"
- **Output** : "dstat -cdngy"

### Vectorisation
- **Modèle** : `text-embedding-3-small` (OpenAI)
- **Dimension** : 1536
- **Méthode** : Concaténation description + commande
- **Index** : HNSW (Hierarchical Navigable Small World)

---

## 🔧 Configuration avancée

### Paramètres Weaviate
```python
# Recherche hybride
alpha=0.5          # Équilibre BM25/vectoriel
limit=12           # Nombre de candidats
return_metadata=["score"]  # Scores de pertinence

# Index vectoriel
Configure.VectorIndex.hnsw()  # Algorithme HNSW
```

### Paramètres OpenAI
```python
# Embeddings
model="text-embedding-3-small"
dimension=1536

# Génération
model="gpt-4o-mini"
temperature=0.0  # Déterministe
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
│   ├── 01_create_schema.py     # Création schéma Weaviate
│   ├── 02_ingest.py           # Ingestion dataset
│   ├── 03_query.py            # Interface CLI/API
│   ├── 04_gradio.py           # Interface web Gradio
│   └── requirements.txt        # Dépendances Python
└── README.md                   # Documentation
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

#### 🔍 Recherche avec filtres
```graphql
{
  Get {
    LinuxCommand(
      where: {
        path: ["command"]
        operator: Like
        valueText: "*grep*"
      }
      limit: 10
    ) {
      description
      command
    }
  }
}
```

---

## 👤 Auteur

**Fabien SERRA-MONTINERI**