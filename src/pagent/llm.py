import ollama


def ask(prompt: str, model: str = "phi3") -> str:
    """Send a single prompt to a local Ollama model and return the reply text."""

    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.message.content

    except Exception as e:
        raise RuntimeError(f"Ollama call failed: {e}") from e


if __name__ == "__main__":
    while True:
        command = input("> ")
        if command == "/quit":
            break
        if command == "/help":
            print("...")
            continue
        print(ask(command))
