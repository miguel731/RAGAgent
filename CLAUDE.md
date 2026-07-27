# CLAUDE.md

Este archivo proporciona orientación a Claude Code (claude.ai/code) al trabajar con el código de este repositorio.

## Descripción del Proyecto

Este es el proyecto final **Alura Agente**: un agente de IA con RAG (Retrieval-Augmented Generation) que responde preguntas en lenguaje natural sobre documentos internos de una empresa. El dominio elegido es una **Clínica de Salud / Consultorio Médico** — el agente responderá preguntas sobre políticas de privacidad de pacientes, FAQ de turnos, políticas de cancelación, guías de cobertura médica e instrucciones pre/post consulta.

## Arquitectura Planificada

El proyecto tiene tres etapas:

1. **Ingesta de documentos** — leer y procesar un PDF o CSV (políticas de pacientes, FAQ, etc.) usando PyPDF o Pandas
2. **Agente RAG local** — construir un agente basado en LangChain respaldado por un LLM (Claude, Gemma o Cohere) que responda preguntas a partir del documento ingestado
3. **Deploy en la nube** — desplegar el agente funcionando en OCI Compute (u equivalente) y exponerlo públicamente

## Stack Tecnológico (planificado)

- **Lenguaje**: Python
- **Framework de agente**: LangChain
- **Procesamiento de documentos**: PyPDF (para PDF) o Pandas (para CSV)
- **LLM**: Claude (Anthropic), Gemma o Cohere
- **Destino de deploy**: OCI Compute

## Flujo de Desarrollo

Una vez que exista código, los comandos esperados serán:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el agente localmente
python main.py
```

## Restricciones Clave

- Siempre hacer funcionar el agente localmente antes de intentar el deploy en la nube
- El README debe incluir: descripción de arquitectura, ejemplos de preguntas y respuestas, e instrucciones de ejecución
- El repositorio en GitHub debe tener un historial de commits que refleje el desarrollo iterativo
