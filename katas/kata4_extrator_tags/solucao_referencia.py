import re

_TAG_RE = re.compile(r"\[([a-z]+)\](.*?)\[/\1\]")


def extrair_tags(texto):
    resultado = {}
    for tag, conteudo in _TAG_RE.findall(texto):
        resultado.setdefault(tag, []).append(conteudo)
    return resultado


def remover_tags(texto):
    return _TAG_RE.sub(lambda m: m.group(2), texto)
