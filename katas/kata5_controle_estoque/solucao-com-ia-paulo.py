"""
Kata 5 — Controle de Estoque

Controle de estoque por SKU, com registro de entradas/saídas e
verificação de alertas de reposição.

Funções:
    criar_estoque() -> dict
    registrar_entrada(estoque, sku, qtd)
    registrar_saida(estoque, sku, qtd)
    verificar_alertas(estoque, limites) -> list[str]
"""


def criar_estoque() -> dict:
    """Retorna um estoque vazio (dict de sku -> quantidade)."""
    return {}


def registrar_entrada(estoque: dict, sku: str, qtd: int) -> None:
    """
    Registra uma entrada de `qtd` unidades do `sku` no estoque.

    Se o SKU ainda não existir, ele é criado com valor `qtd`.
    Se já existir, `qtd` é somada à quantidade atual.

    Levanta ValueError se qtd <= 0.
    """
    if qtd <= 0:
        raise ValueError("qtd deve ser positiva")

    estoque[sku] = estoque.get(sku, 0) + qtd


def registrar_saida(estoque: dict, sku: str, qtd: int) -> None:
    """
    Registra uma saída de `qtd` unidades do `sku` no estoque.

    Regras:
    - Levanta ValueError se qtd <= 0.
    - Levanta KeyError se o sku não existir no estoque.
    - Levanta ValueError se a saída deixar a quantidade negativa
      (estoque insuficiente); nesse caso o estoque NÃO é alterado.
    """
    if qtd <= 0:
        raise ValueError("qtd deve ser positiva")

    if sku not in estoque:
        raise KeyError(sku)

    nova_qtd = estoque[sku] - qtd
    if nova_qtd < 0:
        raise ValueError(f"estoque insuficiente para o sku {sku!r}")

    estoque[sku] = nova_qtd


def verificar_alertas(estoque: dict, limites: dict) -> list:
    """
    Verifica quais SKUs estão abaixo do limite mínimo de reposição.

    - `limites` é um dict sku -> quantidade_minima.
    - Retorna a lista de SKUs (ordenada alfabeticamente) cuja quantidade
      atual no estoque é MENOR que o limite mínimo definido para ele.
    - SKUs presentes em `limites` mas ausentes do estoque contam como
      quantidade 0 (portanto entram no alerta se o limite for > 0).
    - SKUs do estoque sem limite definido são ignorados.
    """
    alertas = [
        sku
        for sku, minimo in limites.items()
        if estoque.get(sku, 0) < minimo
    ]
    return sorted(alertas)