"""Estado mínimo da conversa e pedidos explícitos de atendimento humano."""

import re
from dataclasses import dataclass
from unicodedata import combining, normalize

from policy_intent import PolicyTopic


@dataclass
class ConversationContext:
    product_name: str | None = None
    policy_topic: PolicyTopic | None = None
    category: str | None = None
    max_price_brl: str | None = None

    def remember_product(self, name: str) -> None:
        self.product_name = name
        self.policy_topic = None
        self.category = None
        self.max_price_brl = None

    def remember_search(self, category: str | None, max_price_brl: str | None) -> None:
        self.product_name = None
        self.policy_topic = None
        self.category = category
        self.max_price_brl = max_price_brl

    def remember_policy(self, topic: PolicyTopic) -> None:
        self.policy_topic = topic
        self.product_name = None
        self.category = None
        self.max_price_brl = None

    def clear(self) -> None:
        self.product_name = None
        self.policy_topic = None
        self.category = None
        self.max_price_brl = None


def asks_for_human(message: str) -> bool:
    """Reconhece pedidos diretos por uma pessoa, sem depender do modelo."""
    normalized = "".join(
        char for char in normalize("NFKD", message.casefold()) if not combining(char)
    )
    return bool(
        re.search(r"\b(quero|preciso|gostaria|prefiro)\b.{0,50}\b(atendente|humano|pessoa)\b", normalized)
        or re.search(r"\b(falar|conversar|transferir|chamar)\b.{0,50}\b(atendente|humano|pessoa|equipe)\b", normalized)
    )


def indicates_end(message: str, awaiting_more_help: bool) -> bool:
    """Encerra somente quando a mensagem indica o fim do atendimento."""
    normalized = "".join(
        char for char in normalize("NFKD", message.casefold()) if not combining(char)
    )
    normalized = " ".join(re.findall(r"\w+", normalized))

    closing_phrases = {
        "obrigado", "obrigada", "ok obrigado", "ok obrigada", "valeu",
        "tchau", "ate mais", "ate logo", "era isso", "era so isso",
        "por enquanto e so", "so isso", "pode encerrar", "sem mais duvidas",
        "nao tenho mais duvidas", "nao preciso de mais nada",
        "nao obrigado", "nao obrigada",
    }
    if normalized in closing_phrases:
        return True
    return awaiting_more_help and normalized in {"nao", "nada mais"}
