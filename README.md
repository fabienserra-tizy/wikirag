# 🐧 Linux RAG — Weaviate + OpenAI + Gradio

Pose une question Linux en langage naturel → reçois **la commande exacte** à exécuter.  
Ton copilote shell, propre et rassurant.

---

## 🚀 Le concept

- Weaviate stocke un dataset de commandes Linux + descriptions
- OpenAI vectorise la requête → recherche Top-K dans Weaviate
- OpenAI génère une commande adaptée + explication rapide
- Gradio affiche tout ça dans un thème terminal stylé

> Une ligne de commande **bienveillante** 👌

---

## 🛠️ Stack technique

| Composant | Rôle |
|----------|------|
| Python (3.12) | orchestration |
| Weaviate v4 | stockage + recherche vectorielle |
| OpenAI API | embeddings + génération |
| Gradio | UI web |
| Docker + Traefik/Nginx | déploiement & routing |

---

## 📦 Installation & Lancement

### Prérequis

Créer `.env` à la racine :

OPENAI_API_KEY=sk-xxxx
VHOST_TRAEFIK=ton-domaine.com


### Démarrage

docker compose down -v
docker compose up -d --build


Puis dans le conteneur Python :

docker exec -it wikirag-python python /usr/src/app/rag/04_gradio.py


---

## 🌍 Accès à l’UI

Local :
http://localhost:7860/rag/

Domaine :
https://<votre_domaine>/rag/

---

## ✨ Fonctionnalités

- Commande prête à copier-coller
- Alerte sécurité automatique (`rm -rf`, `dd`, etc.)
- Historique cliquable (10 derniers prompts)
- Logs CSV persistants
- Mode strict (commande seule)
- Thème iTerm2 (terminal moderne)

---

## 📁 Structure

rag/
├─ 01_create_schema.py
├─ 02_ingest.py
├─ 03_query.py
├─ 04_gradio.py
└─ logs/queries.csv

---

## ✅ Exemple

**Question**

Trouver les fichiers modifiés depuis 7 jours


**Réponse**
\`\`\`bash
find . -type f -mtime -7
\`\`\`
Liste les fichiers modifiés récemment dans le répertoire courant.

---

## 🔮 Améliorations prévues

- Hybrid Search (BM25 + vecteur)
- Catégorisation (Filesystem / Réseau / Process)
- Export dataset enrichi
- Mode Terminal CLI natif

---

## 👤 Auteur

Projet conçu par **Fabien SERRA-MONTINERI**  
Cabinet de conseil indépendant (CRM, Cloud & IA)

---

### 🐧 Merci d’utiliser Linux RAG 🎉