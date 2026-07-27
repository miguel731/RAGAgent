"""
Servidor FastAPI que expone el agente RAG como API HTTP
con interfaz web y memoria de conversación por sesión.
"""
import os
import uuid
from fastapi import FastAPI, Cookie, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from agent import build_agent, build_session_chain

load_dotenv()

app = FastAPI(title="Asistente MediSalud")

# Recursos compartidos (embeddings + LLM se cargan una sola vez)
_retriever = None
_llm = None

# Cadenas con memoria: una por session_id
_sessions: dict = {}


def get_shared_resources():
    global _retriever, _llm
    if _retriever is None:
        _retriever, _llm = build_agent()
    return _retriever, _llm


def get_session_chain(session_id: str):
    if session_id not in _sessions:
        retriever, llm = get_shared_resources()
        _sessions[session_id] = build_session_chain(retriever, llm)
    return _sessions[session_id]


class Pregunta(BaseModel):
    texto: str


HTML = """<!DOCTYPE html>
<html lang="es" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MediSalud — Asistente IA</title>
  <style>
    /* ── Tokens ── */
    :root {
      --bg:          #0A0F1C;
      --surface:     #111827;
      --surface-2:   #1a2236;
      --border:      rgba(255,255,255,0.07);
      --border-mid:  rgba(255,255,255,0.12);
      --cyan:        #00D4FF;
      --cyan-dim:    rgba(0,212,255,0.12);
      --cyan-glow:   rgba(0,212,255,0.25);
      --green:       #10B981;
      --green-dim:   rgba(16,185,129,0.12);
      --text-1:      #F0F4FF;
      --text-2:      #8B9CC8;
      --text-3:      #4A5578;
      --user-bg:     #1B4FD8;
      --user-bg-2:   #1e40af;
      --radius-sm:   10px;
      --radius-md:   16px;
      --radius-lg:   20px;
    }
    :root[data-theme="light"] {
      --bg:          #F0F4FB;
      --surface:     #FFFFFF;
      --surface-2:   #E8EDF8;
      --border:      rgba(0,0,0,0.07);
      --border-mid:  rgba(0,0,0,0.12);
      --cyan:        #0369A1;
      --cyan-dim:    rgba(3,105,161,0.08);
      --cyan-glow:   rgba(3,105,161,0.18);
      --green:       #059669;
      --green-dim:   rgba(5,150,105,0.1);
      --text-1:      #0F172A;
      --text-2:      #475569;
      --text-3:      #94A3B8;
      --user-bg:     #1B4FD8;
      --user-bg-2:   #1e40af;
    }
    @media (prefers-color-scheme: light) {
      :root:not([data-theme="dark"]) {
        --bg:          #F0F4FB;
        --surface:     #FFFFFF;
        --surface-2:   #E8EDF8;
        --border:      rgba(0,0,0,0.07);
        --border-mid:  rgba(0,0,0,0.12);
        --cyan:        #0369A1;
        --cyan-dim:    rgba(3,105,161,0.08);
        --cyan-glow:   rgba(3,105,161,0.18);
        --green:       #059669;
        --green-dim:   rgba(5,150,105,0.1);
        --text-1:      #0F172A;
        --text-2:      #475569;
        --text-3:      #94A3B8;
        --user-bg:     #1B4FD8;
        --user-bg-2:   #1e40af;
      }
    }

    /* ── Reset ── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html, body { height: 100%; overflow: hidden; }

    body {
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text-1);
      display: flex;
      height: 100vh;
    }

    /* ── Ambient background ── */
    body::before {
      content: '';
      position: fixed;
      inset: 0;
      background:
        radial-gradient(ellipse 60% 40% at 15% 50%, rgba(0,212,255,0.05) 0%, transparent 60%),
        radial-gradient(ellipse 40% 60% at 85% 20%, rgba(16,185,129,0.04) 0%, transparent 60%);
      pointer-events: none;
      z-index: 0;
    }

    /* ── Sidebar ── */
    .sidebar {
      width: 280px;
      flex-shrink: 0;
      background: var(--surface);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      position: relative;
      z-index: 1;
    }

    .sidebar-header {
      padding: 28px 24px 20px;
      border-bottom: 1px solid var(--border);
    }

    .logo-mark {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 6px;
    }

    .logo-icon {
      width: 36px;
      height: 36px;
      background: linear-gradient(135deg, var(--cyan), var(--green));
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .logo-icon svg { width: 18px; height: 18px; fill: white; }

    .logo-name {
      font-size: 1.05rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: var(--text-1);
    }

    .logo-tag {
      font-size: 0.7rem;
      font-weight: 500;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--cyan);
      margin-left: 46px;
    }

    .sidebar-status {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 24px;
      font-size: 0.75rem;
      color: var(--text-2);
      border-bottom: 1px solid var(--border);
    }

    .status-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--green);
      box-shadow: 0 0 6px var(--green);
      animation: pulse-dot 2.5s ease-in-out infinite;
    }

    @keyframes pulse-dot {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.4; }
    }

    .sidebar-section {
      padding: 20px 24px 12px;
    }

    .sidebar-label {
      font-size: 0.68rem;
      font-weight: 600;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--text-3);
      margin-bottom: 12px;
    }

    .quick-btn {
      width: 100%;
      text-align: left;
      background: transparent;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 10px 14px;
      color: var(--text-2);
      font-size: 0.8rem;
      cursor: pointer;
      transition: all 0.15s ease;
      margin-bottom: 6px;
      line-height: 1.4;
    }

    .quick-btn:hover {
      background: var(--cyan-dim);
      border-color: var(--cyan);
      color: var(--cyan);
    }

    .quick-btn:focus-visible {
      outline: 2px solid var(--cyan);
      outline-offset: 2px;
    }

    .sidebar-footer {
      margin-top: auto;
      padding: 16px 24px;
      border-top: 1px solid var(--border);
      font-size: 0.72rem;
      color: var(--text-3);
      line-height: 1.6;
    }

    /* ── Main chat area ── */
    .chat-area {
      flex: 1;
      display: flex;
      flex-direction: column;
      position: relative;
      z-index: 1;
      min-width: 0;
    }

    /* ── Top bar ── */
    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 28px;
      border-bottom: 1px solid var(--border);
      background: rgba(10,15,28,0.6);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      flex-shrink: 0;
    }

    :root[data-theme="light"] .topbar {
      background: rgba(240,244,251,0.8);
    }

    .topbar-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .topbar-avatar {
      width: 34px;
      height: 34px;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--cyan), var(--green));
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.75rem;
      font-weight: 700;
      color: white;
      flex-shrink: 0;
    }

    .topbar-title {
      font-size: 0.9rem;
      font-weight: 600;
      color: var(--text-1);
    }

    .topbar-sub {
      font-size: 0.73rem;
      color: var(--text-2);
    }

    .topbar-actions {
      display: flex;
      gap: 8px;
      align-items: center;
    }

    .icon-btn {
      width: 34px;
      height: 34px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: transparent;
      color: var(--text-2);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.15s;
    }

    .icon-btn:hover { background: var(--surface-2); color: var(--text-1); }
    .icon-btn:focus-visible { outline: 2px solid var(--cyan); outline-offset: 2px; }
    .icon-btn svg { width: 16px; height: 16px; }

    /* ── Messages ── */
    #messages {
      flex: 1;
      overflow-y: auto;
      padding: 28px;
      display: flex;
      flex-direction: column;
      gap: 20px;
      scroll-behavior: smooth;
    }

    #messages::-webkit-scrollbar { width: 4px; }
    #messages::-webkit-scrollbar-track { background: transparent; }
    #messages::-webkit-scrollbar-thumb { background: var(--border-mid); border-radius: 4px; }

    /* ── Message rows ── */
    .msg-row {
      display: flex;
      gap: 12px;
      animation: msg-in 0.25s cubic-bezier(0.22,1,0.36,1) both;
    }

    @keyframes msg-in {
      from { opacity: 0; transform: translateY(10px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    @media (prefers-reduced-motion: reduce) {
      .msg-row { animation: none; }
    }

    .msg-row.user { flex-direction: row-reverse; }

    .msg-avatar {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.7rem;
      font-weight: 700;
      margin-top: 2px;
    }

    .msg-avatar.bot-av {
      background: linear-gradient(135deg, var(--cyan), var(--green));
      color: white;
    }

    .msg-avatar.user-av {
      background: var(--user-bg);
      color: white;
    }

    .msg-content { max-width: 68%; display: flex; flex-direction: column; gap: 4px; }
    .msg-row.user .msg-content { align-items: flex-end; }

    .bubble {
      padding: 13px 16px;
      border-radius: var(--radius-md);
      font-size: 0.875rem;
      line-height: 1.65;
      word-break: break-word;
    }

    .bubble.bot {
      background: var(--surface);
      border: 1px solid var(--border-mid);
      border-left: 3px solid var(--cyan);
      color: var(--text-1);
      border-radius: var(--radius-md);
      border-top-left-radius: 4px;
    }

    .bubble.user {
      background: linear-gradient(135deg, var(--user-bg), var(--user-bg-2));
      color: #fff;
      border-top-right-radius: 4px;
    }

    .msg-meta {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.7rem;
      color: var(--text-3);
      padding: 0 4px;
    }

    .source-chip {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      background: var(--green-dim);
      border: 1px solid rgba(16,185,129,0.2);
      border-radius: 20px;
      padding: 2px 8px;
      font-size: 0.68rem;
      color: var(--green);
      font-weight: 500;
    }

    .source-chip svg { width: 10px; height: 10px; }

    /* ── Typing indicator ── */
    .typing-row {
      display: flex;
      gap: 12px;
      align-items: flex-start;
    }

    .typing-bubble {
      background: var(--surface);
      border: 1px solid var(--border-mid);
      border-left: 3px solid var(--cyan);
      border-radius: var(--radius-md);
      border-top-left-radius: 4px;
      padding: 14px 18px;
      display: flex;
      gap: 5px;
      align-items: center;
    }

    .typing-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--cyan);
      animation: typing 1.2s ease-in-out infinite;
    }

    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }

    @keyframes typing {
      0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
      30% { opacity: 1; transform: translateY(-4px); }
    }

    /* ── Input bar ── */
    .input-bar {
      padding: 16px 28px 20px;
      border-top: 1px solid var(--border);
      background: var(--surface);
      flex-shrink: 0;
    }

    .input-wrap {
      display: flex;
      align-items: center;
      gap: 10px;
      background: var(--surface-2);
      border: 1px solid var(--border-mid);
      border-radius: var(--radius-lg);
      padding: 6px 6px 6px 18px;
      transition: border-color 0.2s, box-shadow 0.2s;
    }

    .input-wrap:focus-within {
      border-color: var(--cyan);
      box-shadow: 0 0 0 3px var(--cyan-glow);
    }

    #input {
      flex: 1;
      border: none;
      background: transparent;
      font-size: 0.875rem;
      color: var(--text-1);
      outline: none;
      padding: 8px 0;
      font-family: inherit;
    }

    #input::placeholder { color: var(--text-3); }

    .send-btn {
      width: 38px;
      height: 38px;
      border-radius: 12px;
      border: none;
      background: linear-gradient(135deg, var(--cyan), #0099cc);
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: opacity 0.15s, transform 0.1s;
      flex-shrink: 0;
    }

    .send-btn:hover { opacity: 0.88; }
    .send-btn:active { transform: scale(0.93); }
    .send-btn:disabled { opacity: 0.35; cursor: not-allowed; }
    .send-btn:focus-visible { outline: 2px solid var(--cyan); outline-offset: 2px; }
    .send-btn svg { width: 16px; height: 16px; }

    .input-hint {
      text-align: center;
      font-size: 0.68rem;
      color: var(--text-3);
      margin-top: 8px;
    }

    /* ── Welcome state ── */
    .welcome {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      flex: 1;
      text-align: center;
      padding: 40px;
      gap: 16px;
    }

    .welcome-icon {
      width: 64px;
      height: 64px;
      border-radius: 20px;
      background: linear-gradient(135deg, var(--cyan), var(--green));
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 4px;
    }

    .welcome-icon svg { width: 32px; height: 32px; fill: white; }

    .welcome h2 {
      font-size: 1.35rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: var(--text-1);
    }

    .welcome p {
      font-size: 0.875rem;
      color: var(--text-2);
      max-width: 380px;
      line-height: 1.65;
    }

    .welcome-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: center;
      margin-top: 8px;
    }

    .chip {
      background: var(--surface);
      border: 1px solid var(--border-mid);
      border-radius: 20px;
      padding: 8px 14px;
      font-size: 0.78rem;
      color: var(--text-2);
      cursor: pointer;
      transition: all 0.15s;
    }

    .chip:hover {
      background: var(--cyan-dim);
      border-color: var(--cyan);
      color: var(--cyan);
    }

    .chip:focus-visible { outline: 2px solid var(--cyan); outline-offset: 2px; }

    /* ── Responsive ── */
    @media (max-width: 700px) {
      .sidebar { display: none; }
    }
  </style>
</head>
<body>

<!-- Sidebar -->
<aside class="sidebar">
  <div class="sidebar-header">
    <div class="logo-mark">
      <div class="logo-icon">
        <svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 100 20A10 10 0 0012 2zm1 14h-2v-2h2v2zm0-4h-2V7h2v5z"/></svg>
      </div>
      <span class="logo-name">MediSalud</span>
    </div>
    <div class="logo-tag">Asistente IA</div>
  </div>

  <div class="sidebar-status">
    <span class="status-dot"></span>
    En línea · Respuesta inmediata
  </div>

  <div class="sidebar-section">
    <div class="sidebar-label">Preguntas frecuentes</div>
    <button class="quick-btn" onclick="sendQuick('¿Cómo agendo un turno?')">¿Cómo agendo un turno?</button>
    <button class="quick-btn" onclick="sendQuick('¿Qué cubre FONASA en la clínica?')">¿Qué cubre FONASA?</button>
    <button class="quick-btn" onclick="sendQuick('¿Cuál es la política de cancelación?')">Política de cancelación</button>
    <button class="quick-btn" onclick="sendQuick('¿Qué debo traer a mi primera consulta?')">Primera consulta</button>
    <button class="quick-btn" onclick="sendQuick('¿Cuándo debo ir a urgencias?')">¿Cuándo ir a urgencias?</button>
  </div>

  <div class="sidebar-footer">
    Powered by Cybernexus<br>
    Documentación interna · Clínica MediSalud
  </div>
</aside>

<!-- Chat -->
<main class="chat-area">
  <div class="topbar">
    <div class="topbar-left">
      <div class="topbar-avatar">IA</div>
      <div>
        <div class="topbar-title">Asistente MediSalud</div>
        <div class="topbar-sub">Responde sobre turnos, coberturas y más</div>
      </div>
    </div>
    <div class="topbar-actions">
      <button class="icon-btn" id="theme-toggle" title="Cambiar tema" onclick="toggleTheme()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="5"/>
          <line x1="12" y1="1" x2="12" y2="3"/>
          <line x1="12" y1="21" x2="12" y2="23"/>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
          <line x1="1" y1="12" x2="3" y2="12"/>
          <line x1="21" y1="12" x2="23" y2="12"/>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>
      </button>
      <button class="icon-btn" title="Nueva conversación" onclick="clearChat()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="1 4 1 10 7 10"/>
          <path d="M3.51 15a9 9 0 1 0 .49-3.51"/>
        </svg>
      </button>
    </div>
  </div>

  <div id="messages">
    <div class="welcome" id="welcome">
      <div class="welcome-icon">
        <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
      </div>
      <h2>¿En qué puedo ayudarte?</h2>
      <p>Consulta sobre turnos, coberturas médicas, cancelaciones, instrucciones pre-consulta y más.</p>
      <div class="welcome-chips">
        <button class="chip" onclick="sendQuick('¿Cómo agendo un turno?')">📅 Agendar turno</button>
        <button class="chip" onclick="sendQuick('¿Qué ISAPRE tienen convenio?')">🏥 Convenios ISAPRE</button>
        <button class="chip" onclick="sendQuick('¿Qué debo hacer antes de un examen de sangre?')">🩸 Exámenes</button>
        <button class="chip" onclick="sendQuick('¿Cuánto cuesta una consulta particular?')">💰 Aranceles</button>
      </div>
    </div>
  </div>

  <div class="input-bar">
    <form id="form" autocomplete="off">
      <div class="input-wrap">
        <input id="input" type="text" placeholder="Escribe tu pregunta…" autocomplete="off" autofocus>
        <button class="send-btn" type="submit" id="send-btn" disabled>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </div>
    </form>
    <div class="input-hint">Las respuestas se basan en la documentación oficial de la clínica</div>
  </div>
</main>

<script>
  const messagesEl = document.getElementById('messages');
  const formEl     = document.getElementById('form');
  const inputEl    = document.getElementById('input');
  const sendBtn    = document.getElementById('send-btn');
  const welcomeEl  = document.getElementById('welcome');
  let isLoading    = false;

  // Enable/disable send button
  inputEl.addEventListener('input', () => {
    sendBtn.disabled = inputEl.value.trim() === '' || isLoading;
  });

  function now() {
    return new Date().toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' });
  }

  function escapeHtml(str) {
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  function addMessage(text, role, fuentes) {
    if (welcomeEl) welcomeEl.remove();

    const row = document.createElement('div');
    row.className = `msg-row ${role}`;

    const avEl = document.createElement('div');
    avEl.className = `msg-avatar ${role === 'bot' ? 'bot-av' : 'user-av'}`;
    avEl.textContent = role === 'bot' ? 'IA' : 'Tú';

    const content = document.createElement('div');
    content.className = 'msg-content';

    const bubble = document.createElement('div');
    bubble.className = `bubble ${role}`;
    bubble.innerHTML = escapeHtml(text).replace(/\\n/g, '<br>');

    content.appendChild(bubble);

    const meta = document.createElement('div');
    meta.className = 'msg-meta';
    meta.textContent = now();

    if (fuentes && fuentes.length > 0) {
      fuentes.forEach(f => {
        const chip = document.createElement('span');
        chip.className = 'source-chip';
        chip.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm-1 1.5L18.5 9H13V3.5zM6 20V4h5v7h7v9H6z"/></svg>${f}`;
        meta.appendChild(chip);
      });
    }

    content.appendChild(meta);

    if (role === 'bot') {
      row.appendChild(avEl);
      row.appendChild(content);
    } else {
      row.appendChild(content);
      row.appendChild(avEl);
    }

    messagesEl.appendChild(row);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function addTyping() {
    const row = document.createElement('div');
    row.className = 'typing-row';
    row.id = 'typing';

    const av = document.createElement('div');
    av.className = 'msg-avatar bot-av';
    av.textContent = 'IA';

    const bubble = document.createElement('div');
    bubble.className = 'typing-bubble';
    bubble.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';

    row.appendChild(av);
    row.appendChild(bubble);
    messagesEl.appendChild(row);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  async function sendMessage(text) {
    if (!text || isLoading) return;
    isLoading = true;
    sendBtn.disabled = true;

    addMessage(text, 'user');
    addTyping();

    try {
      const res = await fetch('/preguntar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texto: text })
      });
      const data = await res.json();
      document.getElementById('typing')?.remove();
      addMessage(data.respuesta, 'bot', data.fuentes);
    } catch {
      document.getElementById('typing')?.remove();
      addMessage('No pude conectar con el servidor. Por favor intenta nuevamente.', 'bot');
    }

    isLoading = false;
    sendBtn.disabled = inputEl.value.trim() === '';
    inputEl.focus();
  }

  formEl.addEventListener('submit', e => {
    e.preventDefault();
    const text = inputEl.value.trim();
    inputEl.value = '';
    sendBtn.disabled = true;
    sendMessage(text);
  });

  function sendQuick(text) {
    inputEl.value = '';
    sendMessage(text);
  }

  async function clearChat() {
    await fetch('/reset', { method: 'POST' });
    messagesEl.innerHTML = `<div class="welcome" id="welcome">
      <div class="welcome-icon">
        <svg viewBox="0 0 24 24" fill="white"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
      </div>
      <h2>¿En qué puedo ayudarte?</h2>
      <p>Consulta sobre turnos, coberturas médicas, cancelaciones, instrucciones pre-consulta y más.</p>
      <div class="welcome-chips">
        <button class="chip" onclick="sendQuick('¿Cómo agendo un turno?')">📅 Agendar turno</button>
        <button class="chip" onclick="sendQuick('¿Qué ISAPRE tienen convenio?')">🏥 Convenios ISAPRE</button>
        <button class="chip" onclick="sendQuick('¿Qué debo hacer antes de un examen de sangre?')">🩸 Exámenes</button>
        <button class="chip" onclick="sendQuick('¿Cuánto cuesta una consulta particular?')">💰 Aranceles</button>
      </div>
    </div>`;
  }

  function toggleTheme() {
    const root = document.documentElement;
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
  }
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def index():
    return HTML


@app.post("/preguntar")
def preguntar(body: Pregunta, response: Response, session_id: str = Cookie(default=None)):
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie("session_id", session_id, max_age=3600, samesite="lax")

    chain = get_session_chain(session_id)
    result = chain.invoke({"question": body.texto})

    fuentes = sorted(set(
        f"pág. {d.metadata.get('page', 0) + 1}"
        for d in result.get("source_documents", [])
    ))
    return {"respuesta": result["answer"], "fuentes": fuentes, "session_id": session_id}


@app.post("/reset")
def reset(response: Response, session_id: str = Cookie(default=None)):
    if session_id and session_id in _sessions:
        del _sessions[session_id]
    new_id = str(uuid.uuid4())
    response.set_cookie("session_id", new_id, max_age=3600, samesite="lax")
    return {"session_id": new_id}


@app.get("/health")
def health():
    return {"status": "ok", "sessions": len(_sessions)}
