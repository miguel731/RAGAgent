"""
Pipeline de ingesta: lee el PDF, lo fragmenta, genera embeddings con Cohere
y guarda el vector store FAISS en disco.

Uso:
    python ingest.py
"""
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

PDF_PATH = "data/clinica_salud.pdf"
VECTORSTORE_PATH = "vectorstore"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def ingest():
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

    print("[3/4] Generando embeddings con Cohere (embed-multilingual-v3.0)...")
    embeddings = CohereEmbeddings(
        model="embed-multilingual-v3.0",
        cohere_api_key=os.environ["COHERE_API_KEY"],
    )
    vectorstore = FAISS.from_documents(chunks, embeddings)
    print("      Embeddings generados.")

    print(f"[4/4] Guardando vector store en '{VECTORSTORE_PATH}/'")
    os.makedirs(VECTORSTORE_PATH, exist_ok=True)
    vectorstore.save_local(VECTORSTORE_PATH)
    print("      Vector store guardado exitosamente.")

    # Verificación rápida
    print("\n--- Verificación: búsqueda de prueba ---")
    results = vectorstore.similarity_search("¿Cómo cancelo un turno?", k=2)
    for i, doc in enumerate(results, 1):
        page = doc.metadata.get("page", "?")
        print(f"  Resultado {i} (página {page + 1}):")
        print(f"    {doc.page_content[:200].strip()}...")
    print("\nIngesta completada con éxito.")


if __name__ == "__main__":
    ingest()
