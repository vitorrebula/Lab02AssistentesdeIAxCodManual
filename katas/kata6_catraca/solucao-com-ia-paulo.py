"""
Kata 6 — Máquina de Catraca

Máquina de estados simples que simula uma catraca de acesso,
processando uma sequência de eventos.

Função:
    processar_eventos(eventos: list[str]) -> list[str]
"""

_TRANCADA = "trancada"
_DESTRANCADA = "destrancada"

_EVENTOS_VALIDOS = {"moeda", "empurrar"}

# Tabela de transição: (estado_atual, evento) -> (novo_estado, resultado)
_TRANSICOES = {
    (_TRANCADA, "moeda"): (_DESTRANCADA, "destrancada"),
    (_DESTRANCADA, "moeda"): (_DESTRANCADA, "moeda_ignorada"),
    (_DESTRANCADA, "empurrar"): (_TRANCADA, "passou"),
    (_TRANCADA, "empurrar"): (_TRANCADA, "bloqueado"),
}


def processar_eventos(eventos: list) -> list:
    """
    Processa uma sequência de eventos de catraca e retorna o resultado
    de cada evento, na ordem em que foram processados.

    A catraca começa trancada.

    Eventos válidos: "moeda", "empurrar". Qualquer outro valor lança
    ValueError (interrompendo o processamento imediatamente — os
    resultados dos eventos anteriores àquele ponto não são retornados,
    pois a função só retorna ao final, com sucesso, da lista completa).

    Regras de transição:
        trancada    + moeda     -> destrancada  ("destrancada")
        destrancada + moeda     -> destrancada  ("moeda_ignorada")
        destrancada + empurrar  -> trancada      ("passou")
        trancada    + empurrar  -> trancada      ("bloqueado")

    Lista vazia -> retorna lista vazia.
    """
    estado = _TRANCADA
    resultados = []

    for i, evento in enumerate(eventos):
        if evento not in _EVENTOS_VALIDOS:
            raise ValueError(
                f"evento invalido {evento!r} na posicao {i}"
            )

        estado, resultado = _TRANSICOES[(estado, evento)]
        resultados.append(resultado)

    return resultados