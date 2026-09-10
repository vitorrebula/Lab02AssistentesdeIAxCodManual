from solucao import extrair_tags, remover_tags


def test_sem_tags():
    assert extrair_tags("texto simples") == {}


def test_uma_tag():
    assert extrair_tags("[b]forte[/b]") == {"b": ["forte"]}


def test_tags_diferentes():
    resultado = extrair_tags("[b]importante[/b] e [i]sutil[/i]")
    assert resultado == {"b": ["importante"], "i": ["sutil"]}


def test_tag_repetida_mantem_ordem():
    resultado = extrair_tags("[b]um[/b] texto [b]dois[/b]")
    assert resultado == {"b": ["um", "dois"]}


def test_tag_sem_fechamento_ignorada():
    assert extrair_tags("[b]sem fechamento") == {}


def test_remover_tags_simples():
    assert remover_tags("Isto e [b]importante[/b].") == "Isto e importante."


def test_remover_tags_multiplas():
    texto = "[b]um[/b] e [i]dois[/i]"
    assert remover_tags(texto) == "um e dois"


def test_remover_tags_sem_tags():
    assert remover_tags("texto puro") == "texto puro"


def test_remover_tags_nao_fechada_mantem_marcador():
    texto = "[b]sem fechamento"
    assert remover_tags(texto) == "[b]sem fechamento"


def test_extrair_tags_conteudo_vazio():
    assert extrair_tags("[b][/b]") == {"b": [""]}
