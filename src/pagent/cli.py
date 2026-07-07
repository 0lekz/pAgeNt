from pagent.llm import ask
from pagent.config import load_settings


def main():
    settings = load_settings()
    while True:
        try:
            command = input("> ")
            if command == "/quit":
                break
            if command == "/help":
                print("...")
                continue
            print(ask(command, model=settings.model))
        except EOFError:
            print()
            break


if __name__ == "__main__":
    main()
