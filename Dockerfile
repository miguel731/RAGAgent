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
ENV COHERE_MODEL="command-r-plus-08-2024"
ENV COHERE_EMBEDDING_MODEL="embed-multilingual-v3.0"

# OpenAI
ENV OPENAI_API_KEY=""
ENV OPENAI_MODEL="gpt-4o-mini"
ENV OPENAI_EMBEDDING_MODEL="text-embedding-3-small"

# Anthropic
ENV ANTHROPIC_API_KEY=""
ENV ANTHROPIC_MODEL="claude-3-5-haiku-20241022"

# Ollama
ENV OLLAMA_BASE_URL="http://localhost:11434"
ENV OLLAMA_MODEL="llama3.2"
ENV OLLAMA_EMBEDDING_MODEL="nomic-embed-text"

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
