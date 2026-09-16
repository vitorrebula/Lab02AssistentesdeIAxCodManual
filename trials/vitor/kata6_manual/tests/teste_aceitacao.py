import pytest
from solucao import processar_eventos


def test_lista_vazia():
    assert processar_eventos([]) == []


def test_empurrar_trancada():
    assert processar_eventos(["empurrar"]) == ["bloqueado"]


def test_moeda_destranca():
    assert processar_eventos(["moeda"]) == ["destrancada"]


def test_moeda_depois_empurrar():
    assert processar_eventos(["moeda", "empurrar"]) == ["destrancada", "passou"]


def test_moeda_dupla_ignorada():
    resultado = processar_eventos(["moeda", "moeda"])
    assert resultado == ["destrancada", "moeda_ignorada"]


def test_sequencia_completa():
    eventos = ["empurrar", "moeda", "moeda", "empurrar", "empurrar"]
    esperado = ["bloqueado", "destrancada", "moeda_ignorada", "passou", "bloqueado"]
    assert processar_eventos(eventos) == esperado


def test_evento_invalido():
    with pytest.raises(ValueError):
        processar_eventos(["girar"])


def test_estado_reinicia_apos_passar():
    eventos = ["moeda", "empurrar", "empurrar"]
    esperado = ["destrancada", "passou", "bloqueado"]
    assert processar_eventos(eventos) == esperado


def test_muitas_moedas_seguidas():
    eventos = ["moeda", "moeda", "moeda"]
    esperado = ["destrancada", "moeda_ignorada", "moeda_ignorada"]
    assert processar_eventos(eventos) == esperado
