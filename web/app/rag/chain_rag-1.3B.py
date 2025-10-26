import weaviate
from langchain_weaviate import WeaviateVectorStore
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# ------------------- MODEL LOADING ------------------- #

model_name = "EleutherAI/gpt-neo-1.3B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

# ------------------- WEAVIATE CLIENT ------------------- #

HOST = "wikiragweaviate"
HTTP_PORT = 8080
GRPC_PORT = 50051

connection = weaviate.connect.ConnectionParams.from_params(
    http_host=HOST,
    http_port=HTTP_PORT,
    http_secure=False,
    grpc_host=HOST,
    grpc_port=GRPC_PORT,
    grpc_secure=False,
)

client = weaviate.WeaviateClient(connection)
client.connect()


class NoEmbed(Embeddings):  # we don't need embedding, Weaviate does it
    def embed_query(self, text): return None
    def embed_documents(self, docs): return None


vector_store = WeaviateVectorStore(
    client=client,
    index_name="Tweet",
    text_key="text",
    embedding=NoEmbed()
)

retriever = vector_store.as_retriever(search_kwargs={"k": 3})


# ------------------- RAG PIPELINE ------------------- #

def rag_answer(query: str):
    docs = retriever.invoke(query)
    context = "\n".join([d.page_content for d in docs])

    # ✅ Prompt simplifié et guide explicite
    prompt = f"""
Réponds en français, en 4 phrases maximum, en utilisant uniquement le contexte ci-dessous.

Contexte :
{context}

Question : {query}

Voici la réponse :
"""

    tokens = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(
        **tokens,
        max_new_tokens=80,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        temperature=0.7
    )
    generated = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # ✅ extraire seulement le texte après "Voici la réponse :"
    answer = generated.split("Voici la réponse :")[-1].strip()

    # ✅ nettoyer la réponse
    answer = answer.replace("Question :", "").replace("Contexte :", "").strip()
    answer = answer.split("\n")[0].strip()

    # ✅ phrases max
    answer = ". ".join(answer.split(". ")[:3]).strip()
    if not answer.endswith("."):
        answer += "."

    return answer, docs



def cleanup():
    client.close()
