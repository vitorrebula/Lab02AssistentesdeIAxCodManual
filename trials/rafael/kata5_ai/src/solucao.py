def criar_estoque():
    return {}


def registrar_entrada(estoque, sku, qtd):
    if qtd <= 0:
        raise ValueError("qtd deve ser positiva")
    estoque[sku] = estoque.get(sku, 0) + qtd


def registrar_saida(estoque, sku, qtd):
    if qtd <= 0:
        raise ValueError("qtd deve ser positiva")
    if sku not in estoque:
        raise KeyError(sku)
    if qtd > estoque[sku]:
        raise ValueError("estoque insuficiente")
    estoque[sku] -= qtd


def verificar_alertas(estoque, limites):
    return sorted(sku for sku, minimo in limites.items()
                  if estoque.get(sku, 0) < minimo)
