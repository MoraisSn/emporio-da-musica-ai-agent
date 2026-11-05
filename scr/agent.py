from decimal import Decimal
from dataclasses import dataclass

from catalog import find_products_by_name, resolve_category_name, search_products
from llm import LLM
from policies import get_opening_hours, get_payment_policy, get_return_policy
from policy_intent import PolicyTopic, get_policy_intent
from product_intent import extract_category_price_filters, extract_product_name
from support_intent import classify_unhandled_question
from store_info import HUMAN_WHATSAPP, STORE_ADDRESS, human_contact_guidance


def analyze_product_by_name(name: str) -> dict:
    """Classifica o resultado de uma busca por nome, sem gerar a resposta final."""
    products = find_products_by_name(name)

    if not products:
        return {"outcome": "not_found"}

    if len(products) > 1:
        return {"outcome": "multiple_matches", "products": products}

    return _classify_product(products[0])


def _classify_product(product: dict) -> dict:
    """Classifica a disponibilidade de um único produto do catálogo."""
    is_available = product["status"] == "active" and product["stock_quantity"] > 0
    outcome = "available" if is_available else "unavailable"
    return {"outcome": outcome, "product": product}


def format_product_response(result: dict) -> str:
    """Transforma o resultado da busca em uma resposta para o cliente."""
    outcome = result["outcome"]

    if outcome == "not_found":
        return "Não encontrei esse produto no catálogo. Pode me informar a marca e o modelo?"

    if outcome == "multiple_matches":
        options = "\n".join(f"{number}. {product['name']}" for number, product in enumerate(result["products"], start=1))
        return f"Encontrei estes modelos:\n{options}\nDigite o número do modelo que você procura."

    if outcome == "available":
        product = result["product"]
        price   = f"R$ {product['price_brl']:.2f}".replace(".", ",")
        return f"O {product['name']} está disponível por {price}."

    if outcome == "unavailable":
        product = result["product"]
        return f"Encontrei o {product['name']}, mas ele não está disponível para venda."

    raise ValueError(f"Resultado de busca desconhecido: {outcome}")


def format_selected_product_response(product: dict) -> str:
    """Responde sobre o produto escolhido em uma lista de resultados."""
    return format_product_response(_classify_product(product))


def format_product_search_results(products: list[dict]) -> str:
    """Apresenta produtos disponíveis encontrados por categoria e preço."""
    if not products:
        return "Não encontrei produtos disponíveis com esses filtros. Quer tentar outra categoria ou preço?"

    lines = []
    for number, product in enumerate(products, start=1):
        price = f"R$ {product['price_brl']:.2f}".replace(".", ",")
        lines.append(f"{number}. {product['name']} — {price}")
    options = "\n".join(lines)
    return (
        f"Encontrei {len(products)} opções disponíveis:\n{options}\n"
        "Digite o número do produto que você quer consultar."
    )


def analyze_product_question(
    message: str, llm: LLM, previous_product_name: str | None = None
) -> dict | None:
    """Busca o produto citado em uma dúvida sobre preço ou disponibilidade."""
    name = extract_product_name(message, llm, previous_product_name)
    if name is None:
        return None
    return analyze_product_by_name(name)

def answer_product_question(message: str, llm: LLM) -> str | None:
    """Responde a uma pergunta sobre produto específico; devolve None se não houver nome."""
    result = analyze_product_question(message, llm)
    if result is None:
        return None
    return format_product_response(result)

@dataclass(frozen=True)
class ProductSearch:
    products: list[dict]
    category: str | None
    max_price_brl: str | None


def search_products_with_filters(
    message: str,
    llm: LLM,
    previous_category: str | None = None,
    previous_max_price_brl: str | None = None,
) -> ProductSearch | None:
    """Consulta o catálogo e devolve os filtros usados para a próxima mensagem."""
    filters = extract_category_price_filters(
        message, llm, previous_category, previous_max_price_brl
    )
    if filters is None:
        return None

    category = None
    if filters.category is not None:
        category = resolve_category_name(filters.category)
        if category is None:
            return None

    max_price = Decimal(filters.max_price_brl) if filters.max_price_brl is not None else None
    products = search_products(category=category, max_price=max_price, include_status=True)
    return ProductSearch(products, category, filters.max_price_brl)


def search_products_by_message(message: str, llm: LLM) -> list[dict] | None:
    """Interface de busca para usos sem contexto de conversa."""
    result = search_products_with_filters(message, llm)
    return result.products if result is not None else None

def answer_opening_hours_question(message: str, llm: LLM) -> str | None:
    """Responde com o horário padrão quando a dúvida for sobre atendimento."""
    intent = get_policy_intent(message, llm)
    if intent.topic != "opening_hours":
        return None
    return get_opening_hours(intent.detail)

def answer_payment_question(message: str, llm: LLM) -> str | None:
    """Responde com a política de pagamento quando esse for o assunto."""
    intent = get_policy_intent(message, llm)
    if intent.topic != "payment":
        return None
    return get_payment_policy(intent.detail)

@dataclass(frozen=True)
class PolicyAnswer:
    text: str
    topic: PolicyTopic


def get_policy_answer(
    message: str, llm: LLM, previous_topic: PolicyTopic | None = None
) -> PolicyAnswer | None:
    """Escolhe a resposta e identifica a política para continuar a conversa."""
    intent = get_policy_intent(message, llm, previous_topic)
    if intent.topic == "opening_hours":
        return PolicyAnswer(get_opening_hours(intent.detail), intent.topic)
    if intent.topic == "payment":
        return PolicyAnswer(get_payment_policy(intent.detail), intent.topic)
    if intent.topic == "returns":
        return PolicyAnswer(get_return_policy(intent.detail), intent.topic)
    return None


def answer_policy_question(message: str, llm: LLM) -> str | None:
    """Mantém a interface simples para usos sem contexto de conversa."""
    result = get_policy_answer(message, llm)
    return result.text if result is not None else None


def answer_unhandled_question(message: str, llm: LLM) -> str:
    """Pede esclarecimento ou explica o limite do atendimento."""
    topic = classify_unhandled_question(message, llm)
    if topic == "missing_product":
        return "Qual produto você procura? Se souber, me diga a marca e o modelo."
    if topic == "needs_clarification":
        return "Pode me contar um pouco mais sobre o que você precisa?"
    if topic == "accessory":
        return (
            "A loja trabalha com instrumentos musicais, mas não vende acessórios. "
            "Posso ajudar você a encontrar um instrumento?"
        )
    if topic == "out_of_scope":
        return (
            "Só tenho informações sobre produtos e políticas do Empório da Música. "
            "Posso ajudar com alguma dúvida sobre a loja?"
        )
    if topic == "store_location":
        return f"A loja fica na {STORE_ADDRESS}"
    if topic == "store_contact":
        return f"O WhatsApp de atendimento da loja é {HUMAN_WHATSAPP}."
    if topic == "human_decision":
        return (
            "Essa solicitação precisa ser avaliada pela equipe da loja. "
            f"{human_contact_guidance()} Não consigo encaminhar a conversa por este terminal."
        )
    if topic == "unavailable_information":
        return (
            "Não consigo confirmar essa informação com os dados consultados aqui. "
            f"{human_contact_guidance()}"
        )
    return (
        "Não encontrei informação suficiente para responder com segurança. "
        f"{human_contact_guidance()}"
    )
