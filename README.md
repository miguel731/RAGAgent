# MediSalud RAG Agent

Agente de inteligencia artificial con RAG (Retrieval-Augmented Generation) que responde preguntas en lenguaje natural sobre la documentación interna de la Clínica MediSalud.

**Demo en vivo:** https://medisalud.cybernexus.cl
**Panel de administración:** https://medisalud.cybernexus.cl/admin

---

## Arquitectura

```
Usuario
  │
  ▼
FastAPI (app.py)
  │  cookie session_id → memoria por usuario
  ▼
ConversationalRetrievalChain (LangChain)
  ├── CONDENSE_PROMPT  →  reformula la pregunta con historial
  ├── Retriever        →  FAISS similarity search (k=3)
  │     └── vectorstore/ (embeddings del PDF)
  └── QA_PROMPT + LLM  →  genera la respuesta final
          │
          └── Provider configurable:
              Cohere | OpenAI | Anthropic | Ollama
```

El agente mantiene memoria de conversación por sesión (últimos 6 intercambios), permitiendo preguntas de seguimiento como "¿Y si mi ISAPRE no está en esa lista?" sin perder contexto.

Si se cambia el proveedor de embeddings, el vectorstore se re-indexa automáticamente al arrancar.

---

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| Framework agente | LangChain |
| LLM (default) | Cohere `command-r-plus-08-2024` |
| Embeddings (default) | Cohere `embed-multilingual-v3.0` |
| Vector store | FAISS (local) |
| Memoria | `ConversationBufferWindowMemory` (k=6) |
| API | FastAPI + Uvicorn |
| Documento fuente | PDF generado con fpdf2 |
| Contenedor | Docker (`python:3.12-slim`) |
| Deploy | Hetzner Cloud |

### Providers soportados

| Provider | LLM | Embeddings |
|---|---|---|
| Cohere | `command-r-plus-08-2024` | `embed-multilingual-v3.0` |
| OpenAI | `gpt-4o-mini` | `text-embedding-3-small` |
| Anthropic | `claude-3-5-haiku-20241022` | — |
| Ollama (local) | `llama3.2` | `nomic-embed-text` |

---

## Ejecución local

### Requisitos
- Python 3.10+
- API key del proveedor elegido

### Instalación

```bash
git clone <repo>
cd RAGAgent

python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Configuración

```bash
cp .env.example .env
# Edita .env con tu API key y provider preferido
```

Configuración mínima con Cohere:
```env
LLM_PROVIDER=cohere
EMBEDDING_PROVIDER=cohere
COHERE_API_KEY=tu_api_key
```

Con OpenAI:
```env
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=tu_api_key
```

Con Ollama (sin API key):
```env
LLM_PROVIDER=ollama
EMBEDDING_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
```

### Generar el PDF e indexar

```bash
python create_pdf.py   # genera data/clinica_salud.pdf
python ingest.py       # indexa el PDF → vectorstore/
```

> Si cambias de proveedor de embeddings, la re-indexación ocurre automáticamente al arrancar.

### Ejecutar

**CLI interactiva:**
```bash
python main.py
```

**Servidor web:**
```bash
uvicorn app:app --reload --port 8000
```
Luego abre `http://localhost:8000`

---

## Ejecución con Docker

```bash
# Build
docker build -t medisalud-rag .

# Run (con Cohere)
docker run -d --name medisalud \
  --restart unless-stopped \
  -e COHERE_API_KEY=tu_api_key \
  -p 8000:8000 medisalud-rag

# O con archivo .env
docker run -d --name medisalud \
  --restart unless-stopped \
  --env-file .env \
  -p 8000:8000 medisalud-rag
```

---

## Ejemplos de preguntas y respuestas

**P: ¿Cómo puedo agendar un turno?**
> Puede agendar su turno de tres maneras: (1) Llamando al +56 2 2345 6789 de lunes a viernes de 8:00 a 20:00 y sábados de 9:00 a 14:00. (2) A través del portal web www.medisalud.cl/turnos, disponible las 24 horas. (3) Presencialmente en recepción durante el horario de atención.

**P: ¿Qué pasa si cancelo con menos de 24 horas de anticipación?**
> Si cancela con menos de 24 horas de anticipación, se aplicará un cargo administrativo de $5.000 CLP para pacientes particulares. En casos de fuerza mayor debidamente documentados (hospitalización, accidente), el cargo puede ser eximido previa evaluación en administración.

**P: ¿Tengo cobertura con FONASA tramo B?**
> Sí, MediSalud es prestador preferente de FONASA en la modalidad de Libre Elección. Con tramo B recibe bonificación del 100% en medicina general y hasta 80% en especialidades. Los exámenes de laboratorio tienen bonificación del 75% en promedio.

**P: ¿Y para exámenes de laboratorio?** *(pregunta de seguimiento)*
> La cobertura para exámenes de laboratorio con FONASA tramo B es del 75% en promedio. Esto significa que usted solo pagará una pequeña parte del costo total del examen.

**P: ¿Qué debo hacer antes de un examen de sangre en ayunas?**
> Debe ayunar entre 8 y 12 horas antes (solo agua permitida) y no fumar durante el ayuno. Los exámenes de ayuno se realizan de lunes a sábado de 7:30 a 10:00. Para pacientes diabéticos, consulte con su médico si puede tomar sus medicamentos habituales.

**P: ¿Cuándo debo ir a urgencias de inmediato?**
> Consulte urgencias inmediatamente si presenta: fiebre superior a 39°C, dificultad para respirar, dolor en el pecho, pérdida de conciencia, sangrado que no cede, o reacción alérgica severa. Nuestra Unidad de Urgencias está abierta las 24 horas. En peligro inmediato de vida, llame al 131 (SAMU).

---

## Panel de administración

Accesible en `/admin` con autenticación HTTP Basic.

Permite gestionar sin reiniciar el servidor:
- Cambiar provider de LLM y embeddings en caliente
- Gestionar API keys de todos los providers
- Forzar re-indexación del documento
- Limpiar sesiones activas
- Ajustar nombre de clínica, branding y datos de contacto
- Cambiar credenciales de acceso al panel

Credenciales configurables via `ADMIN_USER` y `ADMIN_PASS` en `.env`.

---

## Estructura del repositorio

```
RAGAgent/
├── README.md
├── requirements.txt        # dependencias con versiones fijadas
├── .env.example            # plantilla de variables de entorno
├── .gitignore
├── data/
│   └── clinica_salud.pdf   # documento fuente (5 secciones)
├── create_pdf.py           # genera el PDF con fpdf2
├── ingest.py               # pipeline de ingesta → FAISS
├── agent.py                # LLM + embeddings + cadena RAG multi-provider
├── main.py                 # interfaz CLI
├── app.py                  # servidor FastAPI + panel admin
└── Dockerfile
```

---

## Deploy en producción

El agente está desplegado en Hetzner Cloud.

Pasos para replicar en cualquier servidor con Docker:

```bash
# Clonar y configurar
git clone <repo> && cd RAGAgent
cp .env.example .env && nano .env

# Generar PDF e indexar localmente
python create_pdf.py && python ingest.py

# Build y deploy
docker build -t medisalud-rag .
docker run -d --name medisalud \
  --restart unless-stopped \
  --env-file .env \
  -p 80:8000 medisalud-rag
```

---

Powered by Cybernexus
