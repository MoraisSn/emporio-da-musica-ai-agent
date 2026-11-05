from decimal import Decimal
from pathlib import Path
from unicodedata import combining, normalize

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PRODUCTS_FILE   = DATA_DIR / "desafio_tecnico_ai_eng - products.csv"
CATEGORIES_FILE = DATA_DIR / "desafio_tecnico_ai_eng - categories.csv"

CATEGORY_ALIASES = {
    "guitarra": "Guitarras",
    "baixo": "Baixos",
    "bateria": "Baterias e Percussão",
    "percussao": "Baterias e Percussão",
    "teclado": "Teclados e Pianos",
    "piano": "Teclados e Pianos",
    "violao": "Violões",
    "ukulele": "Ukuleles",
}


def _normalize_category_name(value: str) -> str:
    """Ignora maiúsculas e acentos ao comparar nomes de categorias."""
    return "".join(
        letter for letter in normalize("NFKD", value.casefold().strip())
        if not combining(letter)
    )


def resolve_category_name(value: str) -> str | None:
    """Encontra o nome oficial da categoria no CSV a partir do texto do cliente."""
    categories = pd.read_csv(CATEGORIES_FILE)["name"].tolist()
    normalized = _normalize_category_name(value)

    for category in categories:
        if _normalize_category_name(category) == normalized:
            return category

    alias = CATEGORY_ALIASES.get(normalized)
    return alias if alias in categories else None


def load_catalog() -> pd.DataFrame:
    """Lê os CSVs e acrescenta o nome da categoria a cada produto."""
    products   = pd.read_csv(PRODUCTS_FILE, dtype={"price_brl": str})
    categories = pd.read_csv(CATEGORIES_FILE)[["category_id", "name"]]
    categories = categories.rename(columns={"name": "category"})

    catalog = products.merge(categories, on="category_id", validate="many_to_one")
    catalog["price_brl"] = catalog["price_brl"].map(Decimal)
    return catalog

def _filter_active_products(products: pd.DataFrame) -> pd.DataFrame:
    """Mantém apenas produtos ativos."""
    return products.loc[products["status"] == "active"]


def _filter_active_and_in_stock(products: pd.DataFrame) -> pd.DataFrame:
    """Mantém apenas produtos ativos e com estoque positivo."""
    active_products = _filter_active_products(products)
    return active_products.loc[active_products["stock_quantity"] > 0]

def _filter_by_category(products: pd.DataFrame, category: str) -> pd.DataFrame:
    """Mantém produtos da categoria informada."""
    return products.loc[products["category"].str.casefold() == category.casefold()]

def _filter_by_max_price(products: pd.DataFrame, max_price: Decimal) -> pd.DataFrame:
    """Mantém produtos com preço até o limite, inclusive."""
    if max_price < 0:
        raise ValueError("max_price não pode ser negativo")
    return products.loc[products["price_brl"] <= max_price]

def _filter_by_name(products: pd.DataFrame, name: str) -> pd.DataFrame:
    """Mantém produtos cujo nome contém o texto informado."""
    if not name.strip():
        raise ValueError("name não pode estar vazio")
    return products.loc[
        products["name"].str.contains(name.strip(), case=False, regex=False, na=False)
    ]

def _to_records(products: pd.DataFrame, *, include_status: bool = False) -> list[dict]:
    """Devolve apenas os campos necessários para a resposta ao cliente."""
    columns = ["product_id", "name", "category", "price_brl", "stock_quantity"]
    if include_status:
        columns.append("status")
    return products[columns].to_dict(orient="records")

def find_products_by_name(name: str) -> list[dict]:
    """Encontra produtos ativos pelo nome, inclusive os que estão sem estoque."""
    matches = _filter_by_name(_filter_active_products(load_catalog()), name)
    return _to_records(matches, include_status=True)

def search_products(
    category: str | None = None,
    max_price: Decimal | None = None,
    name: str | None = None,
    *,
    include_status: bool = False,
) -> list[dict]:
    """Combina os filtros para buscar produtos disponíveis."""
    matches = _filter_active_and_in_stock(load_catalog())

    if category is not None:
        matches = _filter_by_category(matches, category)
    if max_price is not None:
        matches = _filter_by_max_price(matches, max_price)
    if name is not None:
        matches = _filter_by_name(matches, name)

    return _to_records(matches, include_status=include_status)


if __name__ == "__main__":
    for product in search_products(category="Violões", max_price=Decimal("1000")):
        print(f'{product["name"]}: R$ {product["price_brl"]:.2f}')
