from pagent.llm import ask


def main():
    while True:
        try:
            command = input("> ")
            if command == "/quit":
                break
            if command == "/help":
                print("...")
                continue
            print(ask(command))
        except EOFError:
            print()
            break


if __name__ == "__main__":
    main()
