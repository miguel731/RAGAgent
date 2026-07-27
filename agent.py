"""
Agente RAG multi-provider: soporta Cohere, OpenAI, Anthropic y Ollama
tanto para el LLM como para los embeddings.

Provider se configura via variables de entorno:
  LLM_PROVIDER       = cohere | openai | anthropic | ollama  (default: cohere)
  EMBEDDING_PROVIDER = cohere | openai | ollama              (default: igual a LLM_PROVIDER)

Si el provider de embeddings cambia respecto al vectorstore en disco,
se re-indexa automáticamente antes de arrancar.
"""
import os
import json
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate

load_dotenv()

VECTORSTORE_PATH = "vectorstore"
PROVIDER_FILE = f"{VECTORSTORE_PATH}/provider.json"

CONDENSE_PROMPT = PromptTemplate.from_template(
    """Dado el historial de conversación y la pregunta de seguimiento, reformula
la pregunta de seguimiento como una pregunta independiente y completa en español.
Si la pregunta ya es independiente, devuélvela tal cual.

Historial:
{chat_history}

Pregunta de seguimiento: {question}
Pregunta reformulada:"""
)

QA_PROMPT = PromptTemplate.from_template(
    """Eres el asistente virtual de la Clínica MediSalud. Responde de forma clara,
amable y precisa basándote únicamente en el contexto proporcionado.
Si la respuesta no está en el contexto, dilo honestamente y sugiere contactar
a la clínica directamente al +56 2 2345 6789 o en www.medisalud.cl.

Contexto del documento:
{context}

Historial de la conversación:
{chat_history}

Pregunta actual: {question}

Respuesta:"""
)


def _get_provider(env_var: str, fallback_var: str = "LLM_PROVIDER", default: str = "cohere") -> str:
    value = os.getenv(env_var, "").strip().lower()
    if value:
        return value
    return os.getenv(fallback_var, default).strip().lower()


def build_llm():
    provider = _get_provider("LLM_PROVIDER", default="cohere")

    if provider == "cohere":
        from langchain_cohere import ChatCohere
        return ChatCohere(
            model=os.getenv("COHERE_MODEL", "command-r-plus-08-2024"),
            cohere_api_key=os.environ["COHERE_API_KEY"],
            temperature=0.1,
        )
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.environ["OPENAI_API_KEY"],
            temperature=0.1,
        )
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022"),
            api_key=os.environ["ANTHROPIC_API_KEY"],
            temperature=0.1,
        )
    elif provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.2"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0.1,
        )
    else:
        raise ValueError(
            f"LLM_PROVIDER='{provider}' no reconocido. "
            "Opciones válidas: cohere, openai, anthropic, ollama"
        )


def build_embeddings():
    provider = _get_provider("EMBEDDING_PROVIDER")

    if provider == "cohere":
        from langchain_cohere import CohereEmbeddings
        return CohereEmbeddings(
            model=os.getenv("COHERE_EMBEDDING_MODEL", "embed-multilingual-v3.0"),
            cohere_api_key=os.environ["COHERE_API_KEY"],
        )
    elif provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            api_key=os.environ["OPENAI_API_KEY"],
        )
    elif provider == "ollama":
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(
            model=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
    else:
        raise ValueError(
            f"EMBEDDING_PROVIDER='{provider}' no reconocido. "
            "Opciones válidas: cohere, openai, ollama"
        )


def get_embedding_key() -> str:
    provider = _get_provider("EMBEDDING_PROVIDER")
    models = {
        "cohere": os.getenv("COHERE_EMBEDDING_MODEL", "embed-multilingual-v3.0"),
        "openai": os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        "ollama": os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"),
    }
    model = models.get(provider, "unknown")
    return f"{provider}:{model}"


def _needs_reindex(active_key: str) -> bool:
    if not os.path.exists(PROVIDER_FILE):
        return True
    try:
        with open(PROVIDER_FILE) as f:
            saved = json.load(f).get("provider", "")
        return saved != active_key
    except Exception:
        return True


def build_agent():
    embeddings = build_embeddings()
    embedding_key = get_embedding_key()

    if _needs_reindex(embedding_key):
        print(f"[agente] Vectorstore desactualizado o inexistente. Re-indexando con '{embedding_key}'...")
        from ingest import ingest
        ingest(embeddings=embeddings, embedding_key=embedding_key)

    vectorstore = FAISS.load_local(
        VECTORSTORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    llm = build_llm()

    return retriever, llm


def build_session_chain(retriever, llm):
    memory = ConversationBufferWindowMemory(
        k=6,
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
    )
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        condense_question_prompt=CONDENSE_PROMPT,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT},
        verbose=False,
    )
