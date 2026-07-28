"""
Pipeline de ingesta: lee todos los PDFs en data/, los fragmenta, genera embeddings
y guarda el vector store FAISS en disco junto con metadata del provider.

Uso standalone:
    python ingest.py

También importable desde agent.py para re-ingesta automática.
"""
import os
import json
import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

load_dotenv()

DATA_DIR = "data"
VECTORSTORE_PATH = "vectorstore"
PROVIDER_FILE = f"{VECTORSTORE_PATH}/provider.json"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def ingest(embeddings=None, embedding_key: str = None):
    """
    Ejecuta la ingesta completa de todos los PDFs en DATA_DIR.

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

    pdf_files = sorted(glob.glob(f"{DATA_DIR}/*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No se encontraron PDFs en '{DATA_DIR}/'")

    print(f"[1/4] Cargando {len(pdf_files)} documento(s) desde '{DATA_DIR}/'")
    all_pages = []
    for path in pdf_files:
        loader = PyPDFLoader(path)
        pages = loader.load()
        for page in pages:
            page.metadata["source"] = os.path.basename(path)
        all_pages.extend(pages)
        print(f"      {os.path.basename(path)} → {len(pages)} páginas")
    print(f"      Total: {len(all_pages)} páginas cargadas.")

    print(f"[2/4] Fragmentando texto (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(all_pages)
    print(f"      {len(chunks)} fragmentos generados.")

    print(f"[3/4] Generando embeddings con '{embedding_key}'...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    print("      Embeddings generados.")

    print(f"[4/4] Guardando vector store en '{VECTORSTORE_PATH}/'")
    os.makedirs(VECTORSTORE_PATH, exist_ok=True)
    vectorstore.save_local(VECTORSTORE_PATH)

    with open(PROVIDER_FILE, "w") as f:
        json.dump({"provider": embedding_key, "documents": [os.path.basename(p) for p in pdf_files]}, f, indent=2)
    print(f"      Vector store guardado (provider: {embedding_key}).")

    print("\n--- Verificación: búsqueda de prueba ---")
    results = vectorstore.similarity_search("¿Cómo cancelo un turno?", k=2)
    for i, doc in enumerate(results, 1):
        src = doc.metadata.get("source", "?")
        page = doc.metadata.get("page", 0)
        print(f"  Resultado {i} ({src}, pág. {page + 1}):")
        print(f"    {doc.page_content[:180].strip()}...")

    print("\nIngesta completada con éxito.")
    return vectorstore


if __name__ == "__main__":
    ingest()
