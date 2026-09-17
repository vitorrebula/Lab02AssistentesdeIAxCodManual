"""Kata 1 - Cesta de Compras.

Modulo de carrinho de compras: montagem da cesta, total bruto,
cupons de desconto condicionais e fechamento (checkout).
"""

CUPONS = {
    "PROMO10": (0.10, 100),
    "PROMO20": (0.20, 200),
}


def criar_carrinho() -> dict:
    """Retorna um carrinho vazio."""
    return {"itens": []}


def adicionar_item(carrinho, nome, preco, qtd):
    """Adiciona um item ao carrinho, somando a qtd se o nome ja existir."""
    if preco <= 0:
        raise ValueError("preco deve ser positivo")
    if qtd <= 0:
        raise ValueError("qtd deve ser positiva")

    for item in carrinho["itens"]:
        if item["nome"] == nome:
            item["qtd"] += qtd
            return

    carrinho["itens"].append({"nome": nome, "preco": preco, "qtd": qtd})


def total_sem_desconto(carrinho) -> float:
    """Soma de preco * qtd de todos os itens, arredondada a 2 casas."""
    return round(sum(item["preco"] * item["qtd"] for item in carrinho["itens"]), 2)


def aplicar_cupom(total, cupom) -> float:
    """Aplica o cupom ao total, respeitando o valor minimo de cada promocao."""
    if not cupom:
        return round(total, 2)
    if cupom not in CUPONS:
        raise ValueError("cupom invalido")

    desconto, minimo = CUPONS[cupom]
    if total > minimo:
        return round(total * (1 - desconto), 2)
    return round(total, 2)


def checkout(carrinho, cupom=None) -> dict:
    """Fecha a cesta e informa se o desconto de fato incidiu."""
    total_bruto = total_sem_desconto(carrinho)
    total_final = aplicar_cupom(total_bruto, cupom)
    return {
        "total_bruto": total_bruto,
        "total_final": total_final,
        "cupom_aplicado": total_final < total_bruto,
    }
