"""Início do atendimento pelo terminal."""

from agent import (
    analyze_product_question,
    answer_policy_question,
    answer_unhandled_question,
    format_product_response,
    format_product_search_results,
    format_selected_product_response,
    search_products_by_message,
)
from llm import GeminiLLM, LLMError
from pydantic import ValidationError


GREETINGS = {"oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"}


def is_greeting_only(message: str) -> bool:
    """Reconhece mensagens que contêm apenas uma saudação."""
    normalized = message.casefold().strip().rstrip(" !?.,:;")
    return normalized in GREETINGS


def main() -> None:
    has_introduced = False
    pending_products: list[dict] = []
    llm = GeminiLLM()

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

        if pending_products:
            valid_numbers = {str(number) for number in range(1, len(pending_products) + 1)}
            if message in valid_numbers:
                product = pending_products[int(message) - 1]
                pending_products = []
                print(f"Tom: {format_selected_product_response(product)}")
                continue

            if message.isdecimal():
                print(f"Tom: Escolha um número de 1 a {len(pending_products)}.")
                continue

            matching_product = next(
                (product for product in pending_products if product["name"].casefold() == message.casefold()),
                None,
            )
            pending_products = []
            if matching_product is not None:
                print(f"Tom: {format_selected_product_response(matching_product)}")
                continue

        introduction = ""
        if not has_introduced:
            introduction = "Oi! Eu sou o Tom, assistente virtual do Empório da Música. "
            has_introduced = True

        if is_greeting_only(message):
            print(f"Tom: {introduction}Como posso ajudar?")
        else:
            try:
                result = analyze_product_question(message, llm)
                if result is None:
                    products = search_products_by_message(message, llm)
                    if products is None:
                        answer = answer_policy_question(message, llm)
                        if answer is None:
                            answer = answer_unhandled_question(message, llm)
                    else:
                        answer = format_product_search_results(products)
                        pending_products = products
                else:
                    answer = format_product_response(result)
                    if result["outcome"] == "multiple_matches":
                        pending_products = result["products"]
            except (LLMError, ValidationError):
                answer = "Não consegui consultar agora. Pode tentar novamente em instantes?"
            print(f"Tom: {introduction}{answer}")


if __name__ == "__main__":
    main()
