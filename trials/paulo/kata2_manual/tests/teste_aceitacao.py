import pytest
from solucao import mesclar_turnos


def test_lista_vazia():
    assert mesclar_turnos([]) == []


def test_turno_unico():
    assert mesclar_turnos([("09:00", "10:00")]) == [("09:00", "10:00")]


def test_turnos_disjuntos():
    resultado = mesclar_turnos([("09:00", "10:00"), ("14:00", "15:00")])
    assert resultado == [("09:00", "10:00"), ("14:00", "15:00")]


def test_turnos_sobrepostos():
    resultado = mesclar_turnos([("09:00", "11:00"), ("10:00", "12:00")])
    assert resultado == [("09:00", "12:00")]


def test_turnos_contiguos():
    resultado = mesclar_turnos([("09:00", "10:00"), ("10:00", "11:00")])
    assert resultado == [("09:00", "11:00")]


def test_turnos_fora_de_ordem():
    resultado = mesclar_turnos([("14:00", "16:00"), ("09:00", "10:30"), ("10:00", "12:00")])
    assert resultado == [("09:00", "12:00"), ("14:00", "16:00")]


def test_multiplos_turnos_encadeados():
    resultado = mesclar_turnos([("08:00", "09:00"), ("09:00", "10:00"), ("10:00", "11:00")])
    assert resultado == [("08:00", "11:00")]


def test_turno_invalido_lanca_erro():
    with pytest.raises(ValueError):
        mesclar_turnos([("10:00", "09:00")])


def test_turno_invalido_igual_lanca_erro():
    with pytest.raises(ValueError):
        mesclar_turnos([("10:00", "10:00")])


def test_tres_grupos_distintos():
    turnos = [("07:00", "08:00"), ("08:00", "09:30"), ("12:00", "13:00"), ("18:00", "20:00"), ("19:00", "21:00")]
    resultado = mesclar_turnos(turnos)
    assert resultado == [("07:00", "09:30"), ("12:00", "13:00"), ("18:00", "21:00")]
