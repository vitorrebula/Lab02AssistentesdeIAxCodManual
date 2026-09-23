import pytest
from solucao import criar_estoque, registrar_entrada, registrar_saida, verificar_alertas


def test_estoque_vazio():
    assert criar_estoque() == {}


def test_registrar_entrada_novo_sku():
    e = criar_estoque()
    registrar_entrada(e, "A1", 10)
    assert e["A1"] == 10


def test_registrar_entrada_soma():
    e = criar_estoque()
    registrar_entrada(e, "A1", 10)
    registrar_entrada(e, "A1", 5)
    assert e["A1"] == 15


def test_registrar_entrada_invalida():
    e = criar_estoque()
    with pytest.raises(ValueError):
        registrar_entrada(e, "A1", 0)


def test_registrar_saida_normal():
    e = criar_estoque()
    registrar_entrada(e, "A1", 10)
    registrar_saida(e, "A1", 4)
    assert e["A1"] == 6


def test_registrar_saida_sku_inexistente():
    e = criar_estoque()
    with pytest.raises(KeyError):
        registrar_saida(e, "A1", 1)


def test_registrar_saida_insuficiente_nao_altera():
    e = criar_estoque()
    registrar_entrada(e, "A1", 3)
    with pytest.raises(ValueError):
        registrar_saida(e, "A1", 5)
    assert e["A1"] == 3


def test_registrar_saida_qtd_invalida():
    e = criar_estoque()
    registrar_entrada(e, "A1", 5)
    with pytest.raises(ValueError):
        registrar_saida(e, "A1", -1)


def test_alertas_abaixo_do_minimo():
    e = criar_estoque()
    registrar_entrada(e, "A1", 2)
    registrar_entrada(e, "B1", 10)
    limites = {"A1": 5, "B1": 5}
    assert verificar_alertas(e, limites) == ["A1"]


def test_alertas_sku_ausente_no_estoque():
    e = criar_estoque()
    limites = {"C1": 3}
    assert verificar_alertas(e, limites) == ["C1"]


def test_alertas_sku_sem_limite_ignorado():
    e = criar_estoque()
    registrar_entrada(e, "A1", 0 + 1)
    limites = {}
    assert verificar_alertas(e, limites) == []


def test_alertas_ordenados():
    e = criar_estoque()
    registrar_entrada(e, "Z1", 1)
    registrar_entrada(e, "A1", 1)
    limites = {"Z1": 5, "A1": 5}
    assert verificar_alertas(e, limites) == ["A1", "Z1"]
