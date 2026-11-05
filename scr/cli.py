"""Início do atendimento pelo terminal."""

from agent import (
    analyze_product_question,
    answer_unhandled_question,
    format_product_response,
    format_product_search_results,
    format_selected_product_response,
    get_policy_answer,
    search_products_with_filters,
)
from conversation import ConversationContext, asks_for_human, indicates_end
from llm import GeminiLLM, LLMError
from pydantic import ValidationError
from store_info import human_contact_guidance


GREETINGS = {"oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"}
FOLLOWUP_QUESTION = "Posso ajudar com mais alguma coisa?"


def is_greeting_only(message: str) -> bool:
    """Reconhece mensagens que contêm apenas uma saudação."""
    normalized = message.casefold().strip().rstrip(" !?.,:;")
    return normalized in GREETINGS


def offer_more_help(answer: str) -> str:
    """Convida a continuar após uma resposta completa."""
    return f"{answer} {FOLLOWUP_QUESTION}"


def main() -> None:
    has_introduced = False
    pending_products: list[dict] = []
    context = ConversationContext()
    awaiting_more_help = False
    llm = GeminiLLM()

    while True:
        try:
            message = input("Cliente: ").strip()
        except EOFError:
            break

        if not message:
            print("Tom: Escreva uma mensagem para continuar.")
            continue

        if message.casefold() == "sair" or indicates_end(message, awaiting_more_help):
            print("Tom: Obrigado pelo contato! Até mais.")
            break

        awaiting_more_help = False

        if asks_for_human(message):
            introduction = ""
            if not has_introduced:
                introduction = "Oi! Eu sou o Tom, assistente virtual do Empório da Música. "
                has_introduced = True
            pending_products = []
            context.clear()
            print(
                f"Tom: {introduction}Claro. {human_contact_guidance()} "
                "Não consigo transferir esta conversa pelo terminal."
            )
            continue

        if pending_products:
            valid_numbers = {str(number) for number in range(1, len(pending_products) + 1)}
            if message in valid_numbers:
                product = pending_products[int(message) - 1]
                pending_products = []
                context.remember_product(product["name"])
                print(f"Tom: {offer_more_help(format_selected_product_response(product))}")
                awaiting_more_help = True
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
                context.remember_product(matching_product["name"])
                print(f"Tom: {offer_more_help(format_selected_product_response(matching_product))}")
                awaiting_more_help = True
                continue

        introduction = ""
        if not has_introduced:
            introduction = "Oi! Eu sou o Tom, assistente virtual do Empório da Música. "
            has_introduced = True

        if is_greeting_only(message):
            print(f"Tom: {introduction}Como posso ajudar?")
        else:
            try:
                result = analyze_product_question(message, llm, context.product_name)
                if result is None:
                    search = search_products_with_filters(
                        message, llm, context.category, context.max_price_brl
                    )
                    if search is None:
                        policy_answer = get_policy_answer(message, llm, context.policy_topic)
                        if policy_answer is None:
                            answer = answer_unhandled_question(message, llm)
                            context.clear()
                        else:
                            answer = offer_more_help(policy_answer.text)
                            context.remember_policy(policy_answer.topic)
                            awaiting_more_help = True
                    else:
                        answer = format_product_search_results(search.products)
                        pending_products = search.products
                        context.remember_search(search.category, search.max_price_brl)
                else:
                    answer = format_product_response(result)
                    if result["outcome"] == "multiple_matches":
                        pending_products = result["products"]
                        context.clear()
                    elif result["outcome"] in {"available", "unavailable"}:
                        context.remember_product(result["product"]["name"])
                        answer = offer_more_help(answer)
                        awaiting_more_help = True
                    else:
                        context.clear()
            except (LLMError, ValidationError):
                answer = "Não consegui consultar agora. Pode tentar novamente em instantes?"
            print(f"Tom: {introduction}{answer}")


if __name__ == "__main__":
    main()
