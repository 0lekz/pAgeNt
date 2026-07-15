from pagent.llm import ask
from pagent.config import load_settings
from pagent.logger import setup_logger


def main():
    settings = load_settings()
    setup_logger(settings)
    
    # main loop
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
