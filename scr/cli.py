"""Início do atendimento pelo terminal."""


GREETINGS = {"oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"}


def is_greeting_only(message: str) -> bool:
    """Reconhece mensagens que contêm apenas uma saudação."""
    normalized = message.casefold().strip().rstrip(" !?.,:;")
    return normalized in GREETINGS


def main() -> None:
    has_introduced = False

    while True:
        try:
            message = input("Cliente: ").strip()
        except EOFError:
            break

        if not message:
            print("Tom: Escreva uma mensagem para continuar.")
            continue

        if message.casefold() == "sair":
            print("Tom: Obrigado pelo contato! Até mais.")
            break

        introduction = ""
        if not has_introduced:
            introduction = "Oi! Eu sou o Tom, assistente virtual do Empório da Música. "
            has_introduced = True

        if is_greeting_only(message):
            print(f"Tom: {introduction}Como posso ajudar?")
        else:
            # A análise da dúvida será conectada em uma próxima etapa.
            print(f"Tom: {introduction}Vou verificar sua dúvida.")


if __name__ == "__main__":
    main()
