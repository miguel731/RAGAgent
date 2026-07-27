"""
Servidor FastAPI que expone el agente RAG como API HTTP
con una interfaz web mínima para chatear.
"""
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from agent import build_agent

load_dotenv()

app = FastAPI(title="Asistente MediSalud")

_chain = None

def get_chain():
    global _chain
    if _chain is None:
        _chain = build_agent()
    return _chain


class Pregunta(BaseModel):
    texto: str


@app.get("/", response_class=HTMLResponse)
def index():
    return """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Asistente MediSalud</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; background: #f0f4f8; display: flex; flex-direction: column; height: 100vh; }
    header { background: #1a6fbf; color: white; padding: 16px 24px; }
    header h1 { font-size: 1.2rem; }
    header p { font-size: 0.85rem; opacity: 0.85; }
    #chat { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
    .msg { max-width: 75%; padding: 10px 14px; border-radius: 12px; line-height: 1.5; font-size: 0.93rem; }
    .user { align-self: flex-end; background: #1a6fbf; color: white; border-bottom-right-radius: 4px; }
    .bot  { align-self: flex-start; background: white; color: #222; border-bottom-left-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .bot .fuente { font-size: 0.75rem; color: #888; margin-top: 6px; }
    .typing { align-self: flex-start; color: #888; font-style: italic; font-size: 0.88rem; }
    form { display: flex; gap: 8px; padding: 12px 20px; background: white; border-top: 1px solid #ddd; }
    input { flex: 1; padding: 10px 14px; border: 1px solid #ccc; border-radius: 8px; font-size: 0.95rem; outline: none; }
    input:focus { border-color: #1a6fbf; }
    button { padding: 10px 20px; background: #1a6fbf; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 0.95rem; }
    button:hover { background: #155a9c; }
  </style>
</head>
<body>
  <header>
    <h1>Asistente Virtual — Clínica MediSalud</h1>
    <p>Consulta sobre turnos, coberturas, cancelaciones y más.</p>
  </header>
  <div id="chat">
    <div class="msg bot">¡Hola! Soy el asistente de la Clínica MediSalud. ¿En qué puedo ayudarte hoy?</div>
  </div>
  <form id="form">
    <input id="input" type="text" placeholder="Escribe tu pregunta..." autocomplete="off" autofocus>
    <button type="submit">Enviar</button>
  </form>
  <script>
    const chat = document.getElementById('chat');
    const form = document.getElementById('form');
    const input = document.getElementById('input');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const texto = input.value.trim();
      if (!texto) return;

      chat.innerHTML += `<div class="msg user">${texto}</div>`;
      input.value = '';
      chat.innerHTML += `<div class="typing" id="typing">Pensando...</div>`;
      chat.scrollTop = chat.scrollHeight;

      try {
        const res = await fetch('/preguntar', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ texto })
        });
        const data = await res.json();
        document.getElementById('typing').remove();
        const fuente = data.fuentes?.length ? `<div class="fuente">Fuentes: ${data.fuentes.join(', ')}</div>` : '';
        chat.innerHTML += `<div class="msg bot">${data.respuesta}${fuente}</div>`;
      } catch {
        document.getElementById('typing').remove();
        chat.innerHTML += `<div class="msg bot">Error al conectar con el servidor.</div>`;
      }
      chat.scrollTop = chat.scrollHeight;
    });
  </script>
</body>
</html>"""


@app.post("/preguntar")
def preguntar(body: Pregunta):
    chain = get_chain()
    result = chain.invoke({"query": body.texto})
    fuentes = sorted(set(
        f"página {d.metadata.get('page', 0) + 1}"
        for d in result.get("source_documents", [])
    ))
    return {"respuesta": result["result"], "fuentes": fuentes}


@app.get("/health")
def health():
    return {"status": "ok"}
