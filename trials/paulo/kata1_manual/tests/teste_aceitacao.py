import pytest
from solucao import criar_carrinho, adicionar_item, total_sem_desconto, aplicar_cupom, checkout


def test_carrinho_vazio():
    c = criar_carrinho()
    assert total_sem_desconto(c) == 0.0


def test_adicionar_item_simples():
    c = criar_carrinho()
    adicionar_item(c, "caneta", 2.5, 3)
    assert total_sem_desconto(c) == 7.5


def test_adicionar_item_duplicado_soma_qtd():
    c = criar_carrinho()
    adicionar_item(c, "caneta", 2.5, 3)
    adicionar_item(c, "caneta", 2.5, 2)
    assert len(c["itens"]) == 1
    assert total_sem_desconto(c) == 12.5


def test_adicionar_item_preco_invalido():
    c = criar_carrinho()
    with pytest.raises(ValueError):
        adicionar_item(c, "caneta", 0, 3)


def test_adicionar_item_qtd_invalida():
    c = criar_carrinho()
    with pytest.raises(ValueError):
        adicionar_item(c, "caneta", 2.5, 0)


def test_cupom_promo10_nao_atinge_minimo():
    assert aplicar_cupom(80, "PROMO10") == 80


def test_cupom_promo10_atinge_minimo():
    assert aplicar_cupom(150, "PROMO10") == 135.0


def test_cupom_promo20_atinge_minimo():
    assert aplicar_cupom(250, "PROMO20") == 200.0


def test_cupom_none():
    assert aplicar_cupom(50, None) == 50


def test_cupom_invalido():
    with pytest.raises(ValueError):
        aplicar_cupom(50, "XPTO")


def test_checkout_sem_cupom():
    c = criar_carrinho()
    adicionar_item(c, "livro", 50, 1)
    resultado = checkout(c)
    assert resultado["total_bruto"] == 50
    assert resultado["total_final"] == 50
    assert resultado["cupom_aplicado"] is False


def test_checkout_com_cupom_efetivo():
    c = criar_carrinho()
    adicionar_item(c, "livro", 60, 3)
    resultado = checkout(c, "PROMO10")
    assert resultado["total_bruto"] == 180
    assert resultado["total_final"] == 162.0
    assert resultado["cupom_aplicado"] is True
