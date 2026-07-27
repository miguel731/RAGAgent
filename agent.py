"""
Agente RAG: carga el vector store FAISS y construye la cadena de recuperación
con Cohere (command-r-plus) para responder preguntas sobre la clínica.
"""
import os
from dotenv import load_dotenv
from langchain_cohere import CohereEmbeddings, ChatCohere
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

VECTORSTORE_PATH = "vectorstore"

PROMPT_TEMPLATE = """Eres un asistente virtual de la Clínica MediSalud. Responde las preguntas
de los pacientes de forma clara, amable y precisa, basándote únicamente en la información
proporcionada en el contexto. Si la respuesta no está en el contexto, indícalo honestamente
y sugiere que el paciente contacte a la clínica directamente.

Contexto:
{context}

Pregunta: {question}

Respuesta:"""


def build_agent():
    embeddings = CohereEmbeddings(
        model="embed-multilingual-v3.0",
        cohere_api_key=os.environ["COHERE_API_KEY"],
    )
    vectorstore = FAISS.load_local(
        VECTORSTORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    llm = ChatCohere(
        model="command-r-plus",
        cohere_api_key=os.environ["COHERE_API_KEY"],
        temperature=0.1,
    )

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"],
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )
    return chain
