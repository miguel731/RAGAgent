# Plan del Proyecto: Alura Agente RAG - Clínica de Salud

## Stack Definido
- **LLM**: Cohere (`command-r-plus` via `langchain-cohere`)
- **Embeddings**: Cohere Embeddings (`embed-multilingual-v3.0`)
- **Vector Store**: FAISS (local, sin servidor)
- **Framework**: LangChain
- **Documentos**: PDF generado con contenido de clínica médica
- **Deploy**: OCI Compute (Etapa 3)

---

## Estado General
- [x] Etapa 1: Documento e Ingesta
- [x] Etapa 2: Agente RAG Local
- [ ] Etapa 3: Deploy en la Nube
- [ ] Etapa 4: Documentación Final (README)

---

## Etapa 1: Documento e Ingesta

**Objetivo:** Crear el documento fuente y construir el pipeline que lo lee, fragmenta, embebe y guarda en FAISS.

### Tareas
- [ ] Crear `data/clinica_salud.pdf` — documento PDF con 5 secciones:
  - Política de privacidad de datos del paciente
  - Preguntas frecuentes sobre consultas y turnos
  - Política de cancelaciones y reagendamiento
  - Guía de convenios y coberturas médicas
  - Instrucciones pre y post consulta
- [ ] Crear `requirements.txt` con dependencias
- [ ] Crear `ingest.py`:
  - Leer el PDF con PyPDF (`PyPDFLoader` de LangChain)
  - Dividir en chunks con `RecursiveCharacterTextSplitter` (chunk_size=500, overlap=50)
  - Generar embeddings con `CohereEmbeddings`
  - Guardar en `vectorstore/` con FAISS
- [ ] Crear `.env.example` con `COHERE_API_KEY=`
- [ ] Verificar ingesta con búsqueda de prueba (similarity search)

### Archivos a crear
```
RAGAgent/
├── requirements.txt
├── .env.example
├── .gitignore
├── data/
│   └── clinica_salud.pdf
├── ingest.py
└── vectorstore/           ← generado al correr ingest.py (ignorado en git)
```

---

## Etapa 2: Agente RAG Local

**Objetivo:** Construir el agente con LangChain + Cohere que responda preguntas usando el vector store.

### Tareas
- [ ] Crear `agent.py`:
  - Cargar el vector store FAISS
  - Configurar `CohereRerank` para reranking (opcional, mejora calidad)
  - Armar cadena RAG: retriever → prompt → `ChatCohere` (`command-r-plus`)
  - Usar `RetrievalQA` o `create_retrieval_chain`
- [ ] Crear `main.py`:
  - Loop de preguntas por línea de comandos
  - Imprimir respuesta + fuentes (página del PDF)
- [ ] Probar con al menos 5 preguntas distintas y documentar las respuestas

### Archivos a crear
```
RAGAgent/
├── agent.py
└── main.py
```

---

## Etapa 3: Deploy en la Nube

**Objetivo:** Contenerizar y desplegar en OCI Compute (o alternativa: Railway / Render).

### Tareas
- [ ] Crear `Dockerfile`
- [ ] Probar imagen localmente
- [ ] Provisionar instancia OCI (o plataforma alternativa)
- [ ] Configurar variable `COHERE_API_KEY` en el servidor
- [ ] Exponer el agente (puerto o URL pública)
- [ ] Capturar evidencia (screenshot o link)

### Archivos a crear
```
RAGAgent/
└── Dockerfile
```

---

## Etapa 4: Documentación Final

**Objetivo:** Repositorio listo para evaluación.

### Tareas
- [ ] Escribir `README.md` con:
  - [ ] Descripción del proyecto
  - [ ] Diagrama de arquitectura (texto/ASCII)
  - [ ] Tecnologías utilizadas
  - [ ] Instrucciones de ejecución local
  - [ ] 5+ ejemplos de preguntas y respuestas
  - [ ] Evidencia del deploy (link o screenshot)
- [ ] Revisar historial de commits
- [ ] Confirmar que el repositorio es público en GitHub

---

## Estructura Final del Repositorio

```
RAGAgent/
├── CLAUDE.md
├── README.md
├── plan.md
├── requirements.txt
├── .env.example
├── .gitignore
├── data/
│   └── clinica_salud.pdf
├── ingest.py
├── agent.py
├── main.py
├── Dockerfile
└── vectorstore/           ← en .gitignore
```

---

## Reglas de Desarrollo
1. Nunca intentar el deploy antes de que el agente funcione 100% local
2. Cada etapa tiene su propio commit antes de pasar a la siguiente
3. El `.env` real nunca entra al repositorio
4. El `vectorstore/` se genera localmente y no se sube a git
