import re

PADRAO = re.compile(r"\[([a-z]+)\](.*?)\[/\1\]")


def extrair_tags(texto):
    resultado = {}
    for nome, conteudo in PADRAO.findall(texto):
        if nome not in resultado:
            resultado[nome] = []
        resultado[nome].append(conteudo)
    return resultado


def remover_tags(texto):
    # so remove marcador que tem par; tag sem fechamento fica no texto
    return PADRAO.sub(r"\2", texto)
