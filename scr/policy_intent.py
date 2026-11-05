"""Identificação de dúvidas sobre políticas da loja."""

from typing import Literal

from pydantic import BaseModel, Field

from llm import LLM


PolicyTopic = Literal["opening_hours", "payment", "returns", "other"]
PolicyDetail = Literal[
    "general", "weekdays", "saturday", "sunday_holidays", "whatsapp", "now",
    "pix", "debit", "credit", "boleto", "installments", "combined_payment",
    "online_return", "defect", "preference", "return_exclusions",
]


class PolicyQuestion(BaseModel):
    topic: PolicyTopic = Field(
        description="Assunto principal da dúvida: horário, pagamento, trocas/devoluções ou outro."
    )
    detail: PolicyDetail = Field(
        description="Parte da política perguntada; general para uma pergunta ampla ou sobre vários detalhes."
    )


def get_policy_intent(message: str, llm: LLM) -> PolicyQuestion:
    """Identifica o assunto e o detalhe perguntado em uma chamada ao Gemini."""
    if not message.strip():
        return PolicyQuestion(topic="other", detail="general")

    prompt = (
        "Classifique o assunto principal da dúvida do cliente. Use "
        "opening_hours para perguntas sobre dias ou horários de atendimento "
        "da loja ou do WhatsApp, inclusive quando perguntam se estão atendendo. "
        "Use payment para formas de pagamento, PIX, cartão, boleto, descontos "
        "de PIX ou parcelamento. Use returns para trocas, devoluções, "
        "arrependimento ou defeitos. Use other para preços ou disponibilidade "
        "de produtos e demais assuntos. Se misturar assuntos diferentes na "
        "mesma pergunta, use other para não responder só uma parte. "
        "O nome de um produto pode aparecer sem mudar o assunto da dúvida. "
        "Escolha também detail: para horário, use weekdays, saturday, "
        "sunday_holidays, whatsapp ou now quando a pergunta for específica; "
        "para pagamento, use pix, debit, credit, boleto, installments ou "
        "combined_payment; para returns, use online_return, defect, "
        "preference ou return_exclusions. Use general se a pergunta for ampla ou pedir "
        "vários detalhes. Para other, use general. Não trate uma pergunta "
        "sobre cálculo do valor de parcelas como simples consulta de regras; "
        "nesse caso, use other.\n\n"
        f"Mensagem do cliente: {message}"
    )
    response_text = llm.generate_structured_text(prompt, PolicyQuestion)
    return PolicyQuestion.model_validate_json(response_text)


def classify_policy_question(message: str, llm: LLM) -> PolicyTopic:
    """Devolve somente o assunto, para usos que não precisam do detalhe."""
    return get_policy_intent(message, llm).topic


def is_opening_hours_question(message: str, llm: LLM) -> bool:
    """Mantém a verificação de horário usada no terminal."""
    return classify_policy_question(message, llm) == "opening_hours"
