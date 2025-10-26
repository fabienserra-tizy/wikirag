import os
import weaviate
import gradio as gr
import pandas as pd
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

LOG_PATH = "/usr/src/app/logs/queries.csv"

# Init logs file if not exists
if not os.path.exists(LOG_PATH):
    pd.DataFrame(columns=["datetime", "question", "answer"]).to_csv(LOG_PATH, index=False)

client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client_db = weaviate.connect_to_custom(
    http_host="wikiragweaviate", http_port=8080, http_secure=False,
    grpc_host="wikiragweaviate", grpc_port=50051, grpc_secure=False,
)
collection = client_db.collections.get("LinuxCommand")

# Historique en mémoire
history = []


DANGEROUS_KEYWORDS = [
    "rm -rf", "mkfs", "dd ", "shutdown", "reboot", "kill -9",
    ">: ", ":(){:", "truncate", "chmod 000", "chown -R",
]


def is_dangerous(cmd: str) -> bool:
    return any(k in cmd.lower() for k in DANGEROUS_KEYWORDS)


def log_request(question, answer):
    df = pd.read_csv(LOG_PATH)
    df.loc[len(df)] = [
        datetime.now().isoformat(timespec="seconds"),
        question,
        answer.split("\n```")[0]  # éviter de foutre du markdown dans le CSV
    ]
    df.to_csv(LOG_PATH, index=False)


def ask(question: str, strict_mode: bool):
    if not question:
        return "❌ Pose une question stp", "", history

    emb = client_ai.embeddings.create(
        model="text-embedding-3-small",
        input=question
    ).data[0].embedding

    results = collection.query.near_vector(
        near_vector=emb,
        limit=4
    ).objects

    if not results:
        return "Aucune réponse trouvée.", "", history

    context = ""
    for obj in results:
        cmd = obj.properties.get("command", "")
        desc = obj.properties.get("description", "")
        context += f"- {cmd} :: {desc}\n"

    mode_prompt = "Uniquement un bloc code, sans explication." if strict_mode else \
                  "Une commande dans un bloc code + explication très courte."

    prompt = f"""
Tu es un assistant Linux.
{mode_prompt}

Question: {question}
Contexte:
{context}
"""

    resp = client_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Réponds en français."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    ).choices[0].message.content

    # Alerte sécurité
    if is_dangerous(resp):
        resp += "\n⚠️ **Commande potentiellement dangereuse ! Vérifie avant d’exécuter.**"

    # Log CSV
    log_request(question, resp)

    # Historique local
    history.insert(0, question)
    history_trimmed = history[:10]

    return resp, context, history_trimmed


with gr.Blocks(
    title="Linux RAG 🐧",
    css="""
body { background-color: #1c1c1c; color: #e6e6e6; }
.gradio-container { font-family: 'Fira Code', monospace !important; }
.markdown-body code { background-color: #000; color: #33ff66; }
textarea, input { background-color: #2b2b2b !important; color: #fafafa !important; }
"""
) as demo:

    gr.Markdown("### 💻 Linux Command Finder — Edition Tizy")
    gr.Markdown("Pose ta question, reçois une commande appropriée… et fais gaffe à ton `rm -rf` 👀")

    with gr.Row():
        question = gr.Textbox(scale=4, placeholder="ex : lister les fichiers .log")
        strict_toggle = gr.Checkbox(label="Mode strict (commande seule)", value=False)
        ask_btn = gr.Button("▶️ Envoyer 🚀", variant="primary")

    with gr.Row():
        answer = gr.Markdown(label="Réponse 🧠")
        docs = gr.Markdown(label="Contexte utilisé 📚")

    with gr.Accordion("🕓 Historique des requêtes", open=False):
        history_box = gr.List(label="Questions récentes", max_height=200)

    ask_btn.click(ask, inputs=[question, strict_toggle], outputs=[answer, docs, history_box])


demo.launch(server_name="0.0.0.0", server_port=7860, root_path="/rag")
