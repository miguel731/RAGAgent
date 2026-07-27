FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data/ ./data/
COPY vectorstore/ ./vectorstore/
COPY ingest.py agent.py app.py main.py ./

# LLM provider
ENV LLM_PROVIDER=cohere
ENV EMBEDDING_PROVIDER=cohere

# Cohere
ENV COHERE_API_KEY=""
ENV COHERE_MODEL=""
ENV COHERE_EMBEDDING_MODEL=""

# OpenAI
ENV OPENAI_API_KEY=""
ENV OPENAI_MODEL=""
ENV OPENAI_EMBEDDING_MODEL=""

# Anthropic
ENV ANTHROPIC_API_KEY=""
ENV ANTHROPIC_MODEL=""

# Ollama
ENV OLLAMA_BASE_URL=""
ENV OLLAMA_MODEL=""
ENV OLLAMA_EMBEDDING_MODEL=""

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
