import re
from typing import NamedTuple

# Casa uma abertura [tag] ou um fechamento [/tag].
# Grupo 1: "/" se for fechamento, string vazia se for abertura.
# Grupo 2: o nome da tag (somente letras minusculas).
_TOKEN_TAG = re.compile(r"\[(/?)([a-z]+)\]")


class _ParCasado(NamedTuple):
    """Representa um par [tag]...[/tag] que foi corretamente casado."""
    nome: str
    abertura: re.Match       # o match de "[tag]"
    fechamento: re.Match     # o match de "[/tag]"


def _encontrar_pares_casados(texto: str) -> list[_ParCasado]:
    pares: list[_ParCasado] = []
    pilha: list[tuple[str, re.Match]] = []  # (nome_da_tag, match_de_abertura)

    for match in _TOKEN_TAG.finditer(texto):
        eh_fechamento = match.group(1) == "/"
        nome = match.group(2)

        if not eh_fechamento:
            # Abertura: so registramos na pilha; ainda nao sabemos
            # se ela vai encontrar um fechamento.
            pilha.append((nome, match))
        else:
            # Fechamento: so "casa" se for exatamente a tag que esta
            # no topo da pilha (formato sem aninhamento).
            if pilha and pilha[-1][0] == nome:
                _, match_abertura = pilha.pop()
                pares.append(_ParCasado(nome, match_abertura, match))
            # Caso contrario: fechamento orfao/desencontrado -> ignorado.

    # O que sobrou na pilha eram aberturas sem fechamento -> ignoradas.
    return pares


def extrair_tags(texto: str) -> dict[str, list[str]]:
    resultado: dict[str, list[str]] = {}

    # Os pares ja vem ordenados pela posicao do FECHAMENTO no texto,
    # o que corresponde a ordem natural de aparicao de cada tag.
    for nome, abertura, fechamento in _encontrar_pares_casados(texto):
        conteudo = texto[abertura.end():fechamento.start()]
        resultado.setdefault(nome, []).append(conteudo)

    return resultado


def remover_tags(texto: str) -> str:
    pares = _encontrar_pares_casados(texto)

    # Posicoes exatas (inicio, fim) de cada marcador que deve ser
    # removido: a abertura e o fechamento de cada par casado.
    intervalos_para_remover: list[tuple[int, int]] = []
    for _, abertura, fechamento in pares:
        intervalos_para_remover.append((abertura.start(), abertura.end()))
        intervalos_para_remover.append((fechamento.start(), fechamento.end()))
    intervalos_para_remover.sort()

    # Reconstroi o texto copiando tudo, exceto os intervalos marcados.
    pedacos: list[str] = []
    posicao_atual = 0
    for inicio, fim in intervalos_para_remover:
        pedacos.append(texto[posicao_atual:inicio])
        posicao_atual = fim
    pedacos.append(texto[posicao_atual:])

    return "".join(pedacos)