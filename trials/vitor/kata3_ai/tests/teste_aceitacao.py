from solucao import validar_senha


def test_senha_valida():
    assert validar_senha("Abcd1234!") == []


def test_senha_curta():
    assert "tamanho_minimo" in validar_senha("Ab1!")


def test_sem_maiuscula():
    assert "sem_maiuscula" in validar_senha("abcd1234!")


def test_sem_minuscula():
    assert "sem_minuscula" in validar_senha("ABCD1234!")


def test_sem_digito():
    assert "sem_digito" in validar_senha("Abcdefgh!")


def test_sem_especial():
    assert "sem_especial" in validar_senha("Abcd1234")


def test_contem_espaco():
    assert "contem_espaco" in validar_senha("Abcd 1234!")


def test_contem_palavra_senha():
    assert "contem_palavra_senha" in validar_senha("MinhaSenha123!")


def test_contem_palavra_senha_case_insensitive():
    assert "contem_palavra_senha" in validar_senha("SENHA1234!ab")


def test_multiplas_violacoes():
    resultado = validar_senha("abc")
    assert set(resultado) == {"tamanho_minimo", "sem_maiuscula", "sem_digito", "sem_especial"}


def test_todas_violacoes():
    resultado = validar_senha("senha")
    assert set(resultado) == {
        "tamanho_minimo", "sem_maiuscula", "sem_digito",
        "sem_especial", "contem_palavra_senha",
    }
