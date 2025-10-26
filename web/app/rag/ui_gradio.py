import gradio as gr
from chain_rag import rag_answer

def ask(query):
    answer, docs = rag_answer(query)

    sources = "\n\n".join([f"- {d.page_content[:200]}..." for d in docs])
    return answer, sources

with gr.Blocks(title="Climate RAG 🧠🌍") as demo:

    gr.Markdown("## 🔎 Climate Question Answering\nAsk a question about climate science!")

    with gr.Row():
        with gr.Column(scale=2):
            query = gr.Textbox(label="Your question")
            submit = gr.Button("Answer")
        with gr.Column(scale=1):
            clear = gr.Button("Clear")

    answer = gr.Textbox(label="Answer", lines=5)
    sources = gr.Textbox(label="Sources", lines=10)

    submit.click(ask, inputs=query, outputs=[answer, sources])
    clear.click(lambda: ("", ""), outputs=[answer, sources])

demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    root_path="/rag"
)