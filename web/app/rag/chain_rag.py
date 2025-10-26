import weaviate
from langchain_weaviate import WeaviateVectorStore
from langchain_core.embeddings import Embeddings
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


# ------------------- MODEL LOADING ------------------- #

model_name = "EleutherAI/gpt-neo-125M"  # ✅ rapide & stable
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)


# ------------------- WEAVIATE CLIENT ------------------- #

HOST = "wikiragweaviate"
HTTP_PORT = 8080
GRPC_PORT = 50051

connection = weaviate.connect.ConnectionParams.from_params(
    http_host=HOST, http_port=HTTP_PORT, http_secure=False,
    grpc_host=HOST, grpc_port=GRPC_PORT, grpc_secure=False,
)

client = weaviate.WeaviateClient(connection)
client.connect()


class NoEmbed(Embeddings):
    def embed_query(self, text): return None
    def embed_documents(self, docs): return None


vector_store = WeaviateVectorStore(
    client=client,
    index_name="Tweet",
    text_key="text",
    embedding=NoEmbed()
)
retriever = vector_store.as_retriever(search_kwargs={"k": 5})


# ------------------- RAG FUNCTION ------------------- #

def rag_answer(query: str):
    docs = retriever.invoke(query)
    context = "\n".join([d.page_content for d in docs])

    prompt = f"""
Based only on the context below, explain the causes of global warming.
Write a clear, factual answer in 3 short sentences maximum.
Do not invent any information.

Context:
{context}

Question: {query}

Answer:
1)
2)
3)
"""

    tokens = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(
        **tokens,
        max_new_tokens=120,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
    )

    raw = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # ✅ keep only after "Answer:"
    if "Answer:" in raw:
        raw = raw.split("Answer:")[1].strip()

    # ✅ text cleaning and strict sentence control
    lines = [
        line.strip(" -•0123456789).").strip()
        for line in raw.split("\n")
        if len(line.split()) > 2
    ]

    answer = " ".join(lines[:3]).strip()
    if not answer.endswith("."):
        answer += "."

    return answer, docs


def cleanup():
    client.close()
