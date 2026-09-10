from datetime import datetime


def _parse(hhmm):
    return datetime.strptime(hhmm, "%H:%M")


def _fmt(dt):
    return dt.strftime("%H:%M")


def mesclar_turnos(turnos):
    if not turnos:
        return []

    parsed = []
    for inicio, fim in turnos:
        di, df = _parse(inicio), _parse(fim)
        if di >= df:
            raise ValueError(f"turno invalido: {inicio}-{fim}")
        parsed.append((di, df))

    parsed.sort(key=lambda t: t[0])

    mesclados = [parsed[0]]
    for di, df in parsed[1:]:
        ultimo_inicio, ultimo_fim = mesclados[-1]
        if di <= ultimo_fim:
            mesclados[-1] = (ultimo_inicio, max(ultimo_fim, df))
        else:
            mesclados.append((di, df))

    return [(_fmt(di), _fmt(df)) for di, df in mesclados]
