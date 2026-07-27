"""
Agente RAG con memoria de conversación: carga el vector store FAISS y construye
la cadena de recuperación con Cohere (command-r-plus-08-2024).

Cada sesión mantiene su propio historial en memoria para que el LLM pueda
resolver referencias al contexto previo ("¿y eso?", "¿cuánto cuesta eso?").
"""
import os
from dotenv import load_dotenv
from langchain_cohere import CohereEmbeddings, ChatCohere
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate

load_dotenv()

VECTORSTORE_PATH = "vectorstore"

# Prompt para condensar la pregunta usando el historial antes de buscar en FAISS
CONDENSE_PROMPT = PromptTemplate.from_template(
    """Dado el historial de conversación y la pregunta de seguimiento, reformula
la pregunta de seguimiento como una pregunta independiente y completa en español.
Si la pregunta ya es independiente, devuélvela tal cual.

Historial:
{chat_history}

Pregunta de seguimiento: {question}
Pregunta reformulada:"""
)

# Prompt final para generar la respuesta con contexto del documento
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
        model="command-r-plus-08-2024",
        cohere_api_key=os.environ["COHERE_API_KEY"],
        temperature=0.1,
    )

    return retriever, llm


def build_session_chain(retriever, llm):
    """Crea una cadena con memoria independiente por sesión."""
    memory = ConversationBufferWindowMemory(
        k=6,                          # últimos 6 intercambios
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
    )
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        condense_question_prompt=CONDENSE_PROMPT,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT},
        verbose=False,
    )
    return chain
