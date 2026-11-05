"""Dados de contato e localização extraídos do manual da loja."""

# Manual de políticas, seção 1.2.
STORE_ADDRESS = "Rua 14 de Maio, 3200, Centro, Campo Grande - MS, CEP 79202-333."

# Manual de políticas, seção 7: canal principal de atendimento remoto.
HUMAN_WHATSAPP = "(67) 3321-4500"


def human_contact_guidance() -> str:
    """Orienta o contato, sem afirmar que o terminal realizou uma transferência."""
    return f"Fale com a equipe pelo WhatsApp {HUMAN_WHATSAPP}, durante o horário de atendimento."
