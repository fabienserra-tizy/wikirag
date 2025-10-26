import os
import weaviate
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client_db = weaviate.connect_to_custom(
    http_host="wikiragweaviate", http_port=8080, http_secure=False,
    grpc_host="wikiragweaviate", grpc_port=50051, grpc_secure=False,
)
collection = client_db.collections.get("LinuxCommand")

DANGEROUS_KEYWORDS = [
    "rm -rf", "mkfs", "dd ", "shutdown", "reboot", "kill -9",
    ">: ", ":(){:", "truncate", "chmod 000", "chown -R",
]


def is_dangerous(cmd: str) -> bool:
    return any(k in cmd.lower() for k in DANGEROUS_KEYWORDS)


def ask(question: str):
    if not question:
        return "❌ Merci d’entrer une question", ""

    emb = client_ai.embeddings.create(
        model="text-embedding-3-small",
        input=question
    ).data[0].embedding

    results = collection.query.near_vector(
        near_vector=emb,
        limit=4
    ).objects

    if not results:
        return "Aucune réponse trouvée.", ""

    context = ""
    for obj in results:
        cmd = obj.properties.get("command", "")
        desc = obj.properties.get("description", "")
        context += f"- {cmd} :: {desc}\n"

    prompt = f"""
Tu es un assistant Linux.
Donne une commande shell dans un bloc code, suivie d'une explication très courte.

Question: {question}

Contexte:
{context}
"""

    resp = client_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Réponds en français, concis, format code + explication."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    ).choices[0].message.content

    # Alerte sécurité si nécessaire
    warning = ""
    if is_dangerous(resp):
        warning = "\n⚠️ **Commande potentiellement dangereuse : vérifie avant d’exécuter !**"

    return resp + warning, context


with gr.Blocks(
    title="Linux RAG 🐧",
    theme=gr.themes.Monochrome()
) as demo:

    gr.Markdown("## 🐧 Linux Command Finder")
    gr.Markdown("Pose ta question en langage naturel. L’outil te répond avec une commande Linux adaptée 🧠⚙️")

    question = gr.Textbox(
        label="Ta question",
        placeholder="ex : voir les fichiers modifiés récemment",
    )
    ask_btn = gr.Button("▶️ Envoyer 🚀")

    answer = gr.Markdown(label="Commande Linux")
    docs = gr.Markdown(label="Contexte utilisé")

    ask_btn.click(ask, inputs=question, outputs=[answer, docs])

    gr.Markdown("---")
    gr.Markdown("🔒 Les commandes risquées affichent un avertissement automatique.")


demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    root_path="/rag"
)
