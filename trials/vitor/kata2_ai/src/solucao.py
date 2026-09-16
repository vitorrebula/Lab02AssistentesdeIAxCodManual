def mesclar_turnos(turnos):
    for inicio, fim in turnos:
        if inicio >= fim:
            raise ValueError("turno invalido: inicio deve ser menor que fim")

    if not turnos:
        return []

    mesclados = []
    for inicio, fim in sorted(turnos):
        if mesclados and inicio <= mesclados[-1][1]:
            ultimo_inicio, ultimo_fim = mesclados[-1]
            mesclados[-1] = (ultimo_inicio, max(ultimo_fim, fim))
        else:
            mesclados.append((inicio, fim))

    return mesclados
