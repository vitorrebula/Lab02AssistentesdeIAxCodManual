def criar_estoque() -> dict:
    return {}


def registrar_entrada(estoque, sku, qtd):
    if qtd <= 0:
        raise ValueError("quantidade deve ser positiva")
    estoque[sku] = estoque.get(sku, 0) + qtd


def registrar_saida(estoque, sku, qtd):
    if qtd <= 0:
        raise ValueError("quantidade deve ser positiva")
    if sku not in estoque:
        raise KeyError(sku)
    if estoque[sku] - qtd < 0:
        raise ValueError("estoque insuficiente")
    estoque[sku] -= qtd


def verificar_alertas(estoque, limites) -> list[str]:
    alertas = []
    for sku, minimo in limites.items():
        atual = estoque.get(sku, 0)
        if atual < minimo:
            alertas.append(sku)
    return sorted(alertas)


if __name__ == "__main__":
    estoque = criar_estoque()
    registrar_entrada(estoque, "A1", 10)
    registrar_saida(estoque, "A1", 3)
    print(estoque)  # {'A1': 7}

    print(verificar_alertas(estoque, {"A1": 5, "B2": 1}))
    # -> ['B2']  (A1 tem 7, acima do limite 5; B2 nao existe, conta como 0)
