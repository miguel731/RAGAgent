"""
Punto de entrada CLI del agente RAG de Clínica MediSalud.
Mantiene memoria de conversación dentro de la sesión.

Uso:
    python main.py
"""
from agent import build_agent, build_session_chain


def main():
    print("=" * 60)
    print("  Asistente Virtual — Clínica MediSalud")
    print("  Escribe 'salir' para terminar.")
    print("=" * 60)
    print()

    print("Cargando agente...")
    retriever, llm = build_agent()
    chain = build_session_chain(retriever, llm)
    print("Agente listo. Puedes hacer tus preguntas.\n")

    while True:
        pregunta = input("Tú: ").strip()
        if not pregunta:
            continue
        if pregunta.lower() in ("salir", "exit", "quit"):
            print("¡Hasta pronto!")
            break

        result = chain.invoke({"question": pregunta})
        respuesta = result["answer"]

        fuentes = sorted(set(
            f"{d.metadata.get('source', 'doc')} pág. {d.metadata.get('page', 0) + 1}"
            for d in result.get("source_documents", [])
        ))

        print(f"\nAsistente: {respuesta}")
        if fuentes:
            print(f"[Fuentes: {', '.join(fuentes)}]")
        print()


if __name__ == "__main__":
    main()
