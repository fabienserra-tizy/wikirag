import os
import gradio as gr
import weaviate
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("❌ La variable OPENAI_API_KEY est manquante")

# Clients
client_ai = OpenAI(api_key=OPENAI_API_KEY)
client_db = weaviate.connect_to_custom(
    http_host="wikiragweaviate", http_port=8080, http_secure=False,
    grpc_host="wikiragweaviate", grpc_port=50051, grpc_secure=False,
)

collection = client_db.collections.get("LinuxCommand")


# Reranking + score (safe parsing)
def rerank_with_llm(question: str, candidates: list):
    prompt = f"""
Tu es un expert Linux.
Classe les commandes selon leur capacité à répondre à :
"{question}"

Réponds strictement sous ce format :

1. commande :: description
2. commande :: description

Commandes candidates :
{chr(10).join([f"- {cmd} :: {desc}" for cmd, desc in candidates])}
"""

    resp = client_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    ).choices[0].message.content

    results = []
    for line in resp.splitlines():
        line = line.strip()
        if not (line.startswith("1.") or line.startswith("2.")):
            continue

        rank = 1.0 if line.startswith("1.") else 0.8
        rank = round(rank, 2)

        if "::" not in line:
            continue  # format non conforme

        parts = line.split("::", 1)
        cmd = parts[0].split(".", 1)[-1].strip()
        desc = parts[1].strip()

        if cmd and desc:
            results.append((cmd, desc, rank))

    return results[:2]


def ask_linux(question: str):
    if not question:
        return "", ""

    # Embedding
    emb = client_ai.embeddings.create(
        model="text-embedding-3-small",
        input=question
    ).data[0].embedding

    # Hybrid Search
    res = collection.query.hybrid(
        query=question,
        vector=emb,
        alpha=0.5,
        limit=12,
        return_metadata=["score"]
    ).objects

    # Aucun résultat textuel du tout
    if not res:
        return (
            "😕 Je ne trouve aucune commande Linux liée à ta demande.",
            ""
        )

    # Score textuel Weaviate
    best_match = res[0]
    score = best_match.metadata.score if best_match.metadata.score is not None else 0.0

    # Seuil de pertinence réaliste
    if score < 0.20:
        return (
            "😕 Je ne vois pas de commande Linux pertinente pour ta requête.",
            f"📉 Score de pertinence trop faible ({score:.2f})"
        )

    # Création des candidats
    candidates = [
        (r.properties.get("command", ""), r.properties.get("description", ""))
        for r in res
    ]

    # Anti-duplication
    unique = {}
    for cmd, desc in candidates:
        if cmd and desc:
            unique[cmd] = desc
    candidates = list(unique.items())

    # Re-ranking LLM
    best = rerank_with_llm(question, candidates)

    context = ""
    for cmd, desc, rank in best:
        context += f"- **{cmd}** (🎯 {rank:.2f})\n  ↳ {desc}\n\n"

    # Prompt final enrichi
    prompt = f"""
Tu es un assistant Linux. Réponds en français, concis.

Format :
1) une seule commande dans un bloc code bash
2) une explication courte
3) améliore la commande si nécessaire

Question: {question}

Sources:
{context}
"""

    final = client_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    ).choices[0].message.content

    return final.strip(), context.strip()


# Interface Gradio
with gr.Blocks(title="Linux Commands RAG") as demo:
    gr.Markdown("## Trouvez facilement la bonne commande Linux")

    q = gr.Textbox(label="Votre question", placeholder="Ex : supprimer tous les fichiers tmp…")
    answer = gr.Markdown(label="Réponse générée")
    ctx = gr.Textbox(label="Sources retenues (score & LLM)", lines=10)

    btn = gr.Button("Rechercher")
    btn.click(ask_linux, inputs=q, outputs=[answer, ctx])

demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    root_path="/rag"
)
