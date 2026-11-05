# Fonte: data/políticas_da_loja.pdf, seção 2 — Horário de Funcionamento.
OPENING_HOURS_RESPONSE = (
    "O atendimento presencial e via WhatsApp funciona de segunda a sexta, "
    "das 9h às 18h, e aos sábados, das 9h às 13h. Aos domingos e feriados, "
    "a loja fica fechada. Fora do expediente, o WhatsApp envia respostas "
    "automáticas. Em datas especiais, o horário pode ser estendido; "
    "alterações são comunicadas pelos canais da loja."
)

OPENING_HOURS_DETAILS = {
    "weekdays": "De segunda a sexta, a loja e o WhatsApp atendem das 9h às 18h.",
    "saturday": "Aos sábados, a loja e o WhatsApp atendem das 9h às 13h.",
    "sunday_holidays": (
        "A loja fica fechada aos domingos e feriados. Em datas especiais, "
        "confira os canais da loja para possíveis alterações."
    ),
    "whatsapp": (
        "O WhatsApp atende de segunda a sexta, das 9h às 18h, e aos sábados, "
        "das 9h às 13h. Fora desse horário, envia respostas automáticas."
    ),
    "now": (
        "Não consigo confirmar a abertura em tempo real. O horário padrão é "
        "de segunda a sexta, das 9h às 18h, e sábado, das 9h às 13h; "
        "domingos e feriados, a loja fica fechada."
    ),
}


def get_opening_hours(detail: str = "general") -> str:
    """Devolve o horário padrão, sem afirmar se a loja está aberta agora."""
    return OPENING_HOURS_DETAILS.get(detail, OPENING_HOURS_RESPONSE)


# Fonte: data/políticas_da_loja.pdf, seções 3, 3.1 e 6.2.
PAYMENT_POLICY_RESPONSE = (
    "Aceitamos PIX à vista, com 5% de desconto sobre o preço de tabela; "
    "o desconto não se aplica a preços já promocionais. Também aceitamos "
    "cartão de débito à vista (todas as bandeiras), cartão de crédito em até "
    "12x sem juros e boleto bancário à vista, com compensação em até 3 dias úteis. "
    "No crédito, até 3x são sem juros, com parcela de pelo menos R$ 50,00; "
    "de 4x a 6x, a parcela mínima é de R$ 80,00; e de 7x a 12x, "
    "a parcela mínima é de R$ 100,00. Para compras acima de R$ 2.000,00, "
    "é possível combinar formas de pagamento, como PIX e cartão."
)

PAYMENT_DETAILS = {
    "pix": (
        "Aceitamos PIX à vista, com 5% de desconto sobre o preço de tabela. "
        "Esse desconto não se aplica a preços já promocionais."
    ),
    "debit": "Aceitamos cartão de débito à vista, em todas as bandeiras.",
    "credit": (
        "Aceitamos cartão de crédito em até 12x sem juros, respeitando o valor "
        "mínimo de parcela conforme o número de vezes."
    ),
    "boleto": "Aceitamos boleto bancário à vista; a compensação pode levar até 3 dias úteis.",
    "installments": (
        "No cartão de crédito, parcelamos sem juros em até 12x. Até 3x, a "
        "parcela mínima é de R$ 50,00; de 4x a 6x, R$ 80,00; e de 7x a 12x, "
        "R$ 100,00."
    ),
    "combined_payment": (
        "Para compras acima de R$ 2.000,00, você pode combinar formas de "
        "pagamento, como PIX e cartão."
    ),
}


def get_payment_policy(detail: str = "general") -> str:
    """Devolve os meios de pagamento e as regras gerais de parcelamento."""
    return PAYMENT_DETAILS.get(detail, PAYMENT_POLICY_RESPONSE)


# Fonte: data/políticas_da_loja.pdf, seção 4 — Trocas e Devoluções.
RETURN_POLICY_RESPONSE = (
    "Para compras online, a devolução por arrependimento pode ser solicitada "
    "em até 7 dias corridos após o recebimento. Trocas por defeito de fabricação "
    "podem ser solicitadas em até 30 dias corridos após a compra. Trocas por "
    "preferência são permitidas em até 7 dias, conforme disponibilidade e "
    "condições do produto. Qual dessas situações é a sua?"
)

RETURN_DETAILS = {
    "online_return": (
        "Em compras online, você pode solicitar a devolução por arrependimento "
        "em até 7 dias corridos após receber o produto. Ele deve estar na "
        "embalagem original, sem sinais de uso, com acessórios e manuais. "
        "O reembolso ocorre pela forma de pagamento original em até 10 dias "
        "úteis, e a loja paga o frete da devolução."
    ),
    "defect": (
        "Produtos com defeito de fabricação podem ser trocados em até 30 dias "
        "corridos após a compra. Depois desse prazo, é preciso acionar a "
        "garantia do fabricante; a loja pode intermediar mediante solicitação. "
        "Danos por mau uso ou modificações não autorizadas não são cobertos."
    ),
    "preference": (
        "Trocas por preferência de cor, modelo ou tamanho são permitidas em até "
        "7 dias, se houver disponibilidade do item desejado. O produto deve "
        "estar em perfeito estado e na embalagem original. Diferenças de valor "
        "são cobradas ou reembolsadas conforme o caso."
    ),
    "return_exclusions": (
        "Não são elegíveis para troca instrumentos personalizados ou ajustados "
        "sob encomenda, produtos de liquidação com aviso explícito de venda "
        "final e boquilhas de instrumentos de sopro."
    ),
}


def get_return_policy(detail: str = "general") -> str:
    """Devolve a regra de troca ou devolução solicitada."""
    return RETURN_DETAILS.get(detail, RETURN_POLICY_RESPONSE)
