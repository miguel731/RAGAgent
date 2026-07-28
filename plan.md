# Plan del Proyecto: Alura Agente RAG - Clínica de Salud

## Stack Definido
- **LLM**: configurable — Cohere `command-r-plus-08-2024` (default), OpenAI, Anthropic, Ollama
- **Embeddings**: configurable — Cohere `embed-multilingual-v3.0` (default), OpenAI, Ollama
- **Vector Store**: FAISS (local, sin servidor); re-indexación automática al cambiar provider de embeddings
- **Memoria**: `ConversationBufferWindowMemory` (k=6, por sesión vía cookie)
- **Framework**: LangChain + FastAPI + Uvicorn
- **Documento fuente**: `data/clinica_salud.pdf` (5 páginas, generado con fpdf2)
- **Deploy**: Hetzner Cloud — Docker en puerto 3100
- **Branding**: Powered by Cybernexus

---

## Estado General
- [x] Etapa 1: Documento e Ingesta
- [x] Etapa 2: Agente RAG Local
- [x] Etapa 3: Deploy en la Nube
- [x] Etapa 4: Documentación Final (README)

---

## Etapa 1: Documento e Ingesta ✅

### Lo que se hizo
- `create_pdf.py` genera `data/clinica_salud.pdf` con 5 secciones usando fpdf2 + fuente DejaVuSans (UTF-8)
- `ingest.py` carga el PDF con `PyPDFLoader`, fragmenta (chunk_size=500, overlap=50), genera embeddings y guarda en FAISS
- Al finalizar la ingesta, guarda `vectorstore/provider.json` con el provider+modelo usado
- `ingest.py` es importable desde `agent.py` para re-ingesta automática; también ejecutable standalone
- Resultado: 5 páginas → 29 fragmentos → vectorstore FAISS guardado en disco

### Archivos
```
data/clinica_salud.pdf
requirements.txt
.env.example
.gitignore
ingest.py
create_pdf.py
vectorstore/
vectorstore/provider.json
```

---

## Etapa 2: Agente RAG Local ✅

### Lo que se hizo
- `agent.py` totalmente multi-provider:
  - `build_llm()` — dispatch por `LLM_PROVIDER` (cohere / openai / anthropic / ollama), imports lazy
  - `build_embeddings()` — dispatch por `EMBEDDING_PROVIDER` (cohere / openai / ollama), imports lazy
  - `get_embedding_key()` — retorna `"provider:model"` para comparar con `vectorstore/provider.json`
  - `build_agent()` — detecta si el provider cambió y re-indexa automáticamente antes de cargar FAISS
  - `build_session_chain()` — `ConversationalRetrievalChain` con `ConversationBufferWindowMemory` (k=6)
- Dos prompts: `CONDENSE_PROMPT` (reformula con historial) y `QA_PROMPT` (responde con contexto + historial)
- `main.py`: CLI interactiva con memoria de conversación
- Probado con preguntas directas y de seguimiento implícito ("¿Y para laboratorio?", "¿Y si llego tarde?")

### Archivos
```
agent.py
main.py
```

---

## Etapa 3: Deploy en la Nube ✅

### Lo que se hizo
- `app.py` — servidor FastAPI con:
  - `GET /` — chat web (dark/light theme, sidebar, typing indicator, chips de sugerencias)
  - `POST /preguntar` — RAG con memoria por sesión (cookie `session_id`, max_age=3600)
  - `POST /reset` — limpia memoria del servidor y genera nueva sesión
  - `GET /admin` — panel de administración (HTTP Basic Auth)
  - `POST /admin/env` — guarda variables al `.env` en caliente via `python-dotenv`
  - `POST /admin/action` — acciones: `reset_sessions`, `reindex`
  - `GET /health` — `{status, sessions, llm_provider, embedding_provider}`
- Panel admin protegido con `ADMIN_USER` / `ADMIN_PASS` (variables de entorno)
- Panel admin permite: cambiar provider LLM/embeddings, gestionar API keys, ajustes visuales del chat, forzar re-indexación, limpiar sesiones, cambiar credenciales admin
- `Dockerfile` — `python:3.12-slim`, copia vectorstore pre-generado, expone todas las variables de entorno con defaults seguros, puerto 8000
- Deploy: Hetzner Cloud, puerto 3100, `--restart unless-stopped`, `--env-file .env`

**URL pública:** `http://46.62.245.242:3100`
**Panel admin:** `http://46.62.245.242:3100/admin`

### Archivos
```
app.py
Dockerfile
```

---

## Etapa 4: Documentación Final ✅

### Lo que se hizo
- `README.md` creado con descripción, arquitectura, stack, instrucciones locales y Docker, ejemplos de preguntas/respuestas, configuración multi-provider y evidencia de deploy

---

## Estructura del Repositorio

```
RAGAgent/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── data/
│   └── clinica_salud.pdf
├── ingest.py
├── create_pdf.py
├── agent.py
├── main.py
├── app.py
└── Dockerfile
```

### Excluidos del repo
```
.env                    # secretos reales
.venv/                  # entorno virtual
__pycache__/
vectorstore/            # generado localmente o copiado a Docker
CLAUDE.md               # instrucciones internas
plan.md                 # este archivo
create_pdf.py           # script de generación del PDF
Eleccion*/Entregables*/Introduccion*  # docs del desafío
```

---

## Variables de Entorno

| Variable | Default | Descripción |
|---|---|---|
| `LLM_PROVIDER` | `cohere` | Provider del LLM: `cohere`, `openai`, `anthropic`, `ollama` |
| `EMBEDDING_PROVIDER` | `cohere` | Provider de embeddings: `cohere`, `openai`, `ollama` |
| `COHERE_API_KEY` | — | API key de Cohere |
| `COHERE_MODEL` | `command-r-plus-08-2024` | Modelo LLM de Cohere |
| `COHERE_EMBEDDING_MODEL` | `embed-multilingual-v3.0` | Modelo de embeddings de Cohere |
| `OPENAI_API_KEY` | — | API key de OpenAI |
| `OPENAI_MODEL` | `gpt-4o-mini` | Modelo LLM de OpenAI |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Modelo de embeddings de OpenAI |
| `ANTHROPIC_API_KEY` | — | API key de Anthropic |
| `ANTHROPIC_MODEL` | `claude-3-5-haiku-20241022` | Modelo LLM de Anthropic |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL de Ollama local |
| `OLLAMA_MODEL` | `llama3.2` | Modelo LLM de Ollama |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text` | Modelo de embeddings de Ollama |
| `ADMIN_USER` | `admin` | Usuario del panel de administración |
| `ADMIN_PASS` | `medisalud2024` | Contraseña del panel de administración |
| `CLINIC_NAME` | `Clínica MediSalud` | Nombre mostrado en el chat |
| `BRANDING` | `Powered by Cybernexus` | Texto del footer del sidebar |
| `CLINIC_PHONE` | `+56 2 2345 6789` | Teléfono sugerido en respuestas |
| `CLINIC_WEB` | `www.medisalud.cl` | Web sugerida en respuestas |

---

## Reglas de Desarrollo
1. Nunca intentar el deploy antes de que el agente funcione 100% local
2. Cada etapa tiene su propio commit antes de pasar a la siguiente
3. El `.env` real nunca entra al repositorio
4. Cambiar `EMBEDDING_PROVIDER` dispara re-indexación automática del PDF
