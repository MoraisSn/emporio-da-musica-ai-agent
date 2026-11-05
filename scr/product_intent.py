import re
from decimal import Decimal

from pydantic import BaseModel, Field

from llm import LLM, LLMError


class ProductMention(BaseModel):
    asks_price_or_availability: bool = Field(
        description="Verdadeiro somente se a dúvida é sobre preço ou disponibilidade de um produto, sem misturar outros assuntos."
    )
    product_name: str | None = Field(
        description="Marca, modelo ou nome comercial específico mencionado pelo cliente; null para categorias genéricas."
    )


class CategoryPriceFilters(BaseModel):
    is_product_search: bool = Field(
        description="Verdadeiro se o cliente quer encontrar produtos por categoria ou preço máximo."
    )
    category: str | None = Field(
        description="Categoria mencionada pelo cliente; null se não houver categoria."
    )
    max_price_brl: str | None = Field(
        description="Preço máximo em reais; null se não houver limite máximo."
    )


def _normalize_price_brl(value: str) -> str:
    """Converte valores como 1000, 1.000 e 1000,00 para 1000.00."""
    amount = re.sub(r"\s+", "", value.replace("R$", ""))

    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?", amount):
        amount = amount.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d+(?:[,.]\d{1,2})?", amount):
        amount = amount.replace(",", ".")
    else:
        raise ValueError("O Gemini retornou um preço máximo inválido.")

    return f"{Decimal(amount):.2f}"


def extract_product_name(message: str, llm: LLM) -> str | None:
    """Extrai um produto específico de uma dúvida sobre preço ou disponibilidade."""
    if not message.strip():
        return None

    prompt = (
        "Identifique se a dúvida é somente sobre preço ou disponibilidade de um "
        "produto. Se pedir outro assunto, como horário ou devolução, mesmo que "
        "cite um produto, marque asks_price_or_availability como false. Se "
        "misturar assuntos, também marque false. Extraia somente uma marca, "
        "modelo ou nome comercial específico mencionado pelo cliente. Não "
        "invente detalhes. Se a pessoa quiser um acessório para um modelo, "
        "não trate isso como pergunta sobre o preço do instrumento. Uma categoria "
        "genérica, como 'violão', 'teclado' ou 'guitarra', não identifica um "
        "produto: nesse caso, use null. Exemplo: 'Quanto custa um violão?' "
        "tem product_name null; 'Quanto custa o Takamine GD20?' tem "
        "product_name 'Takamine GD20'.\n\n"
        f"Mensagem do cliente: {message}"
    )
    response_text = llm.generate_structured_text(prompt, ProductMention)
    product = ProductMention.model_validate_json(response_text)
    if product.asks_price_or_availability and product.product_name:
        return product.product_name.strip() or None
    return None


def extract_category_price_filters(message: str, llm: LLM) -> CategoryPriceFilters | None:
    """Extrai categoria e preço máximo de uma busca genérica por produtos."""
    if not message.strip():
        return None

    prompt = (
        "Identifique se o cliente quer encontrar produtos por categoria ou por "
        "um preço máximo. Extraia a categoria com as palavras do cliente, sem "
        "inventar ou converter para o nome do catálogo. Extraia um preço somente "
        "quando for um limite máximo. Em reais, '1000', '1.000' e '1000,00' "
        "significam o mesmo valor; '1.000,50' significa mil reais e cinquenta "
        "centavos. Devolva max_price_brl como texto decimal, por exemplo "
        "'1000.00' ou '1000.50'. Se não houver categoria ou limite "
        "máximo, use null no campo correspondente. Não trate um modelo específico "
        "como categoria. Perguntas sobre horários, pagamentos ou devoluções não "
        "são buscas por produtos. Pedidos de acessórios como cordas, cabos, "
        "palhetas e cases também não são buscas de instrumentos. Se a mensagem "
        "pedir filtros diferentes, como "
        "preço mínimo, marque is_product_search como false para não fazer uma "
        "busca incompleta.\n\n"
        f"Mensagem do cliente: {message}"
    )
    response_text = llm.generate_structured_text(prompt, CategoryPriceFilters)
    filters = CategoryPriceFilters.model_validate_json(response_text)
    if not filters.is_product_search or (
        filters.category is None and filters.max_price_brl is None
    ):
        return None

    if filters.max_price_brl is not None:
        try:
            filters.max_price_brl = _normalize_price_brl(filters.max_price_brl)
        except ValueError as error:
            raise LLMError("O Gemini retornou um preço inválido.") from error

    return filters
