# Plan del Proyecto: Alura Agente RAG - Clínica de Salud

## Stack Definido
- **LLM**: Cohere `command-r-plus-08-2024` (via `langchain-cohere`)
- **Embeddings**: Cohere `embed-multilingual-v3.0`
- **Vector Store**: FAISS (local, sin servidor)
- **Memoria**: `ConversationBufferWindowMemory` (k=6, por sesión vía cookie)
- **Framework**: LangChain
- **API**: FastAPI + Uvicorn
- **Documento fuente**: `data/clinica_salud.pdf` (5 páginas, generado con fpdf2)
- **Deploy**: Hetzner Cloud — Docker en puerto 3100
- **Branding**: Powered by Cybernexus

---

## Estado General
- [x] Etapa 1: Documento e Ingesta
- [x] Etapa 2: Agente RAG Local
- [x] Etapa 3: Deploy en la Nube
- [ ] Etapa 4: Documentación Final (README)

---

## Etapa 1: Documento e Ingesta ✅

**Completada.**

### Lo que se hizo
- `create_pdf.py` genera `data/clinica_salud.pdf` con 5 secciones usando fpdf2 + fuente DejaVuSans (UTF-8)
- `requirements.txt` con dependencias fijadas a versiones compatibles
- `ingest.py` carga el PDF con `PyPDFLoader`, fragmenta con `RecursiveCharacterTextSplitter` (chunk_size=500, overlap=50), genera embeddings con `CohereEmbeddings` y guarda en `vectorstore/` con FAISS
- `.env.example` y `.gitignore` configurados
- Resultado: 5 páginas → 29 fragmentos → vectorstore FAISS guardado en disco

### Archivos creados
```
data/clinica_salud.pdf
requirements.txt
.env.example
.gitignore
ingest.py
create_pdf.py
vectorstore/
```

---

## Etapa 2: Agente RAG Local ✅

**Completada.**

### Lo que se hizo
- `agent.py`: carga FAISS, construye retriever (k=3), inicializa `ChatCohere` y `ConversationalRetrievalChain` con `ConversationBufferWindowMemory` (k=6 intercambios)
- Dos prompts: `CONDENSE_PROMPT` (reformula la pregunta con historial) y `QA_PROMPT` (genera respuesta con contexto del documento + historial)
- `build_agent()` retorna retriever y LLM compartidos; `build_session_chain()` crea una cadena con memoria independiente por sesión
- `main.py`: CLI interactiva con memoria de sesión
- Probado con preguntas directas y de seguimiento con referencias implícitas ("¿Y para laboratorio?", "¿Y si llego tarde?")

### Archivos creados
```
agent.py
main.py
```

---

## Etapa 3: Deploy en la Nube ✅

**Completada.**

### Lo que se hizo
- `app.py`: servidor FastAPI con:
  - `GET /` — interfaz web de chat (HTML inline, dark/light theme, sidebar con quick questions)
  - `POST /preguntar` — endpoint RAG con memoria por sesión (cookie `session_id`)
  - `POST /reset` — limpia memoria y genera nueva sesión
  - `GET /health` — health check con conteo de sesiones activas
- Sesiones: `session_id` via cookie HTTP, un `ConversationalRetrievalChain` por sesión en dict en memoria
- UI: diseño 2026 — dark mode por defecto, toggle light/dark, sidebar con sugerencias, typing indicator animado, chips de fuente en cada respuesta
- Branding: "Powered by Cybernexus"
- `Dockerfile`: imagen `python:3.12-slim`, copia vectorstore pre-generado (no regenera en build)
- Deploy: Hetzner Cloud, puerto 3100, `--restart unless-stopped`

**URL pública:** `http://46.62.245.242:3100`

### Archivos creados
```
app.py
Dockerfile
```

---

## Etapa 4: Documentación Final ⏳

**Pendiente.**

### Tareas
- [ ] Escribir `README.md` con:
  - [ ] Descripción del proyecto
  - [ ] Diagrama de arquitectura (ASCII)
  - [ ] Tecnologías utilizadas
  - [ ] Instrucciones de ejecución local
  - [ ] 5+ ejemplos de preguntas y respuestas
  - [ ] Evidencia del deploy (link + screenshot)
- [ ] Revisar historial de commits
- [ ] Confirmar que el repositorio sea público en GitHub

---

## Estructura Final del Repositorio

```
RAGAgent/
├── README.md              ← pendiente
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
├── Dockerfile
└── vectorstore/           ← en .gitignore
```

### Archivos excluidos del repo (solo desarrollo/servidor)
```
.env
.venv/
__pycache__/
vectorstore/
CLAUDE.md
plan.md
Eleccion de desafio.md
Entregables del desafio,md
Introduccion Desafio.md
create_pdf.py
```

---

## Reglas de Desarrollo
1. Nunca intentar el deploy antes de que el agente funcione 100% local
2. Cada etapa tiene su propio commit antes de pasar a la siguiente
3. El `.env` real nunca entra al repositorio
4. El `vectorstore/` se copia a la imagen Docker pero no se sube a git
