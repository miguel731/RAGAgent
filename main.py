"""
Punto de entrada del agente RAG de Clínica MediSalud.
Interfaz de línea de comandos para hacer preguntas al agente.

Uso:
    python main.py
"""
from agent import build_agent


def main():
    print("=" * 60)
    print("  Asistente Virtual — Clínica MediSalud")
    print("  Escribe 'salir' para terminar.")
    print("=" * 60)
    print()

    print("Cargando agente...")
    chain = build_agent()
    print("Agente listo. Puedes hacer tus preguntas.\n")

    while True:
        pregunta = input("Tú: ").strip()
        if not pregunta:
            continue
        if pregunta.lower() in ("salir", "exit", "quit"):
            print("¡Hasta pronto!")
            break

        result = chain.invoke({"query": pregunta})
        respuesta = result["result"]

        fuentes = set()
        for doc in result.get("source_documents", []):
            page = doc.metadata.get("page", 0)
            fuentes.add(f"página {page + 1}")

        print(f"\nAsistente: {respuesta}")
        if fuentes:
            print(f"[Fuentes: {', '.join(sorted(fuentes))}]")
        print()


if __name__ == "__main__":
    main()
