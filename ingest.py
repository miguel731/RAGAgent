"""
Pipeline de ingesta: lee el PDF, lo fragmenta, genera embeddings
y guarda el vector store FAISS en disco junto con metadata del provider.

Uso standalone:
    python ingest.py

También importable desde agent.py para re-ingesta automática.
"""
import os
import json
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

load_dotenv()

PDF_PATH = "data/clinica_salud.pdf"
VECTORSTORE_PATH = "vectorstore"
PROVIDER_FILE = f"{VECTORSTORE_PATH}/provider.json"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def ingest(embeddings=None, embedding_key: str = None):
    """
    Ejecuta la ingesta completa.

    Args:
        embeddings: objeto de embeddings ya construido (evita construirlo dos veces).
                    Si es None, se construye internamente usando las variables de entorno.
        embedding_key: string "provider:model" para guardar en provider.json.
                       Requerido si embeddings es externo.
    """
    if embeddings is None:
        from agent import build_embeddings, get_embedding_key
        embeddings = build_embeddings()
        embedding_key = get_embedding_key()

    print(f"[1/4] Cargando documento: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    pages = loader.load()
    print(f"      {len(pages)} páginas cargadas.")

    print(f"[2/4] Fragmentando texto (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(pages)
    print(f"      {len(chunks)} fragmentos generados.")

    print(f"[3/4] Generando embeddings con '{embedding_key}'...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    print("      Embeddings generados.")

    print(f"[4/4] Guardando vector store en '{VECTORSTORE_PATH}/'")
    os.makedirs(VECTORSTORE_PATH, exist_ok=True)
    vectorstore.save_local(VECTORSTORE_PATH)

    with open(PROVIDER_FILE, "w") as f:
        json.dump({"provider": embedding_key}, f)
    print(f"      Vector store guardado (provider: {embedding_key}).")

    print("\n--- Verificación: búsqueda de prueba ---")
    results = vectorstore.similarity_search("¿Cómo cancelo un turno?", k=2)
    for i, doc in enumerate(results, 1):
        page = doc.metadata.get("page", 0)
        print(f"  Resultado {i} (página {page + 1}):")
        print(f"    {doc.page_content[:180].strip()}...")

    print("\nIngesta completada con éxito.")
    return vectorstore


if __name__ == "__main__":
    ingest()
