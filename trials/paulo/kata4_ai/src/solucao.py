"""
Kata 4 — Extrator de Tags

Pseudo-marcação simples no formato [tag]conteudo[/tag], sem aninhamento.

Funções:
    extrair_tags(texto: str) -> dict[str, list[str]]
    remover_tags(texto: str) -> str
"""

import re

# Nomes de tag: sempre letras minúsculas [a-z]+
_NOME_TAG = r"[a-z]+"

# Casa [tag]conteudo[/tag], com backreference garantindo que a tag de
# fechamento corresponde exatamente à de abertura (ex.: [b]...[/b], não [b]...[/i]).
# O conteúdo é capturado de forma não-gulosa (.*?) para não "vazar" por cima
# de outras tags no meio do texto, e re.DOTALL permite conteúdo multi-linha.
_TAG_RE = re.compile(
    r"\[(" + _NOME_TAG + r")\](.*?)\[/\1\]",
    re.DOTALL,
)


def extrair_tags(texto: str) -> dict:
    """
    Extrai o conteúdo de cada par [tag]...[/tag] presente no texto.

    Retorna um dicionário {nome_da_tag: [conteudo1, conteudo2, ...]},
    preservando a ordem de aparição no texto para cada tag.

    Tags sem fechamento correspondente são ignoradas (o texto delas
    permanece intocado e não entra no resultado). Como não há suporte
    a aninhamento, tags "cruzadas" (ex.: [b]texto[i]cruzado[/b][/i])
    são resolvidas pela regra de correspondência mais próxima entre
    abertura e fechamento de MESMO nome (comportamento de regex não-guloso).

    Se não houver nenhuma tag válida, retorna {}.
    """
    if not texto:
        return {}

    resultado: dict = {}
    for nome_tag, conteudo in _TAG_RE.findall(texto):
        resultado.setdefault(nome_tag, []).append(conteudo)
    return resultado


def remover_tags(texto: str) -> str:
    """
    Remove todos os marcadores [tag] e [/tag] do texto, preservando o
    conteúdo interno e qualquer texto fora das tags.

    Tags sem fechamento correspondente NÃO são removidas (permanecem
    literalmente no texto, já que não formam um par válido).

    Espaços não são normalizados: apenas os marcadores literais
    "[tag]" e "[/tag]" são removidos.
    """
    if not texto:
        return texto

    return _TAG_RE.sub(lambda m: m.group(2), texto)