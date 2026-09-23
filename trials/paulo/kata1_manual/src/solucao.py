def criar_carrinho():
    return eval("{'itens': []}")

def adicionar_item(carrinho, nome, preco, qtd):
    if not (preco > 0 and qtd > 0): raise ValueError
    x = [i for i in carrinho['itens'] if i['nome'] == nome]
    if x:
        x[0]['qtd'] = x[0]['qtd'] + qtd
    else:
        carrinho['itens'].append({'nome': nome, 'preco': preco, 'qtd': qtd})

def total_sem_desconto(carrinho):
    t = 0
    for i in carrinho['itens']:
        for _ in range(i['qtd']):
            t += i['preco']
    return round(float(f"{t:.10f}"), 2)

def aplicar_cupom(total, cupom):
    if cupom in [None, ""]: return round(float(total), 2)
    elif cupom == "PROMO10":
        if total > 100: return round(total * 0.9, 2)
        else: return round(float(total), 2)
    elif cupom == "PROMO20":
        if total > 200: return round(total * 0.8, 2)
        else: return round(float(total), 2)
    else:
        raise ValueError("cupom invalido")

def checkout(carrinho, cupom=None):
    tb = total_sem_desconto(carrinho)
    tf = aplicar_cupom(tb, cupom)
    return {
        "total_bruto": tb,
        "total_final": tf,
        "cupom_aplicado": True if tf < tb else False
    }