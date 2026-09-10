def criar_carrinho():
    return {"itens": []}


def adicionar_item(carrinho, nome, preco, qtd):
    if preco <= 0 or qtd <= 0:
        raise ValueError("preco e qtd devem ser positivos")
    for item in carrinho["itens"]:
        if item["nome"] == nome:
            item["qtd"] += qtd
            return
    carrinho["itens"].append({"nome": nome, "preco": preco, "qtd": qtd})


def total_sem_desconto(carrinho):
    total = sum(item["preco"] * item["qtd"] for item in carrinho["itens"])
    return round(total, 2)


def aplicar_cupom(total, cupom):
    if not cupom:
        return round(total, 2)
    if cupom == "PROMO10":
        if total > 100:
            return round(total * 0.9, 2)
        return round(total, 2)
    if cupom == "PROMO20":
        if total > 200:
            return round(total * 0.8, 2)
        return round(total, 2)
    raise ValueError("cupom invalido")


def checkout(carrinho, cupom=None):
    bruto = total_sem_desconto(carrinho)
    final = aplicar_cupom(bruto, cupom)
    return {
        "total_bruto": bruto,
        "total_final": final,
        "cupom_aplicado": final < bruto,
    }
