import os
import gradio as gr
import weaviate
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
import warnings
import asyncio

# Suppression des warnings non critiques
warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message="unclosed event loop")
warnings.filterwarnings("ignore", message="websockets.legacy is deprecated")
warnings.filterwarnings("ignore", message="Con004")

# Suppression des warnings asyncio
asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

# Suppression des warnings Weaviate
os.environ["WEAVIATE_DISABLE_WARNINGS"] = "1"

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("❌ La variable OPENAI_API_KEY est manquante")

# Configuration Langchain
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=OPENAI_API_KEY
)

# Connexion Weaviate v4
client_db = weaviate.connect_to_custom(
    http_host="wikiragweaviate", http_port=8080, http_secure=False,
    grpc_host="wikiragweaviate", grpc_port=50051, grpc_secure=False,
)

collection = client_db.collections.get("LinuxCommand")

# Configuration du LLM avec Langchain
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.0,
    openai_api_key=OPENAI_API_KEY
)

# Template de prompt pour l'interface
prompt_template = """
Tu es un assistant Linux expert. Réponds en français, concis.

Format de réponse :
1) une seule commande dans un bloc code bash
2) une explication courte
3) améliore la commande si nécessaire

Question: {question}

Contexte:
{context}
"""

PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["question", "context"]
)

def ask_linux_langchain(question: str):
    """Fonction principale utilisant Langchain pour répondre aux questions Linux"""
    if not question:
        return "", ""

    try:
        # Génération de l'embedding pour la question
        question_embedding = embeddings.embed_query(question)
        
        # Recherche hybride avec Weaviate v4 (plus de résultats pour éviter les doublons)
        results = collection.query.hybrid(
            query=question,
            vector=question_embedding,
            alpha=0.5,
            limit=12  # Plus de résultats pour avoir de la diversité
        ).objects
        
        # Élimination des doublons et construction du contexte
        seen_commands = set()
        unique_results = []
        context = ""
        
        for obj in results:
            cmd = obj.properties.get("command", "")
            desc = obj.properties.get("description", "")
            
            # Éviter les doublons basés sur la commande
            if cmd and cmd not in seen_commands:
                seen_commands.add(cmd)
                unique_results.append(obj)
                context += f"- {cmd} :: {desc}\n"
                
                # Limiter à 4 résultats uniques maximum
                if len(unique_results) >= 4:
                    break
        
        # Génération de la réponse avec Langchain
        prompt = PROMPT.format(question=question, context=context)
        response = llm.invoke(prompt)
        
        # Formatage des sources pour l'affichage
        sources_text = "📚 Sources utilisées par Langchain:\n\n"
        for i, obj in enumerate(unique_results, 1):
            cmd = obj.properties.get("command", "")
            desc = obj.properties.get("description", "")
            sources_text += f"{i}. **{cmd}**\n   ↳ {desc}\n\n"
        
        return response.content.strip(), sources_text.strip()
        
    except Exception as e:
        error_msg = f"❌ Erreur Langchain: {str(e)}"
        return error_msg, ""

# Interface Gradio avec Langchain
with gr.Blocks(
    title="Linux Commands RAG - Langchain", 
    theme=gr.themes.Soft()
) as demo:
    
    gr.Markdown("""
    # 🐧 Assistant Linux Intelligent avec Langchain
    
    Posez votre question en français et recevez la commande Linux appropriée !
    
    **Technologies utilisées :**
    - 🔗 Langchain pour l'orchestration RAG
    - 🧠 OpenAI GPT-4o-mini pour la génération
    - 🔍 Weaviate pour la recherche vectorielle
    - 📊 HuggingFace pour le dataset
    """)

    with gr.Row():
        with gr.Column(scale=3):
            question_input = gr.Textbox(
                label="Votre question Linux", 
                placeholder="Ex: Comment trouver tous les fichiers modifiés cette semaine ?",
                lines=2
            )
            
            search_btn = gr.Button("🔍 Rechercher", variant="primary")
            
        with gr.Column(scale=1):
            gr.Markdown("""
            ### 💡 Exemples de questions
            - Trouver les fichiers volumineux
            - Voir les processus en cours
            - Compresser un dossier
            - Installer un package
            """)

    with gr.Row():
        with gr.Column():
            answer_output = gr.Markdown(
                label="🤖 Réponse générée par Langchain",
                value="Posez une question pour commencer..."
            )
            
        with gr.Column():
            sources_output = gr.Textbox(
                label="📚 Sources utilisées",
                lines=8,
                interactive=False
            )

    # Gestion des événements
    search_btn.click(
        fn=ask_linux_langchain,
        inputs=[question_input],
        outputs=[answer_output, sources_output]
    )
    
    # Recherche aussi avec Enter
    question_input.submit(
        fn=ask_linux_langchain,
        inputs=[question_input],
        outputs=[answer_output, sources_output]
    )

    # Footer avec informations techniques
    gr.Markdown("""
    ---
    **🔧 Architecture Langchain :**
    - `HuggingFaceDatasetLoader` → Chargement du dataset
    - `OpenAIEmbeddings` → Vectorisation des documents  
    - `Weaviate` → Stockage et recherche vectorielle
    - `RetrievalQA` → Chain RAG complète
    - `ChatOpenAI` → Génération des réponses
    """)

# Lancement de l'interface
demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    root_path="/rag"
)
