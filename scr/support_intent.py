"""Classificação das mensagens que não foram resolvidas pelo catálogo ou políticas."""

from typing import Literal

from pydantic import BaseModel, Field

from llm import LLM


SupportTopic = Literal[
    "missing_product", "needs_clarification", "accessory", "out_of_scope", "store_other"
]


class SupportQuestion(BaseModel):
    topic: SupportTopic = Field(description="Motivo pelo qual a dúvida ainda não foi respondida.")


def classify_unhandled_question(message: str, llm: LLM) -> SupportTopic:
    """Distingue falta de detalhes de assuntos fora do escopo da loja."""
    prompt = (
        "Classifique a mensagem do cliente que ainda não foi respondida. "
        "Use missing_product se ele pedir preço, estoque ou detalhes de um "
        "produto sem identificar qual. Use needs_clarification se a dúvida "
        "estiver vaga ou incompleta de outra forma. Use accessory se pedir "
        "cordas, palhetas, cabos, cases, pedais, amplificadores ou outros "
        "acessórios que a loja não vende. Use out_of_scope para assuntos sem "
        "relação com a loja ou instrumentos musicais. Use store_other para "
        "pedidos, reclamações ou outros assuntos da loja que exigem dados não "
        "disponíveis neste atendimento. Responda somente pelo esquema.\n\n"
        f"Mensagem do cliente: {message}"
    )
    response = llm.generate_structured_text(prompt, SupportQuestion)
    return SupportQuestion.model_validate_json(response).topic
