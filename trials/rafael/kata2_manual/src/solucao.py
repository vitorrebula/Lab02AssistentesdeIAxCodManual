def mesclar_turnos(turnos):
    if not turnos:
        return []

    # converte "HH:MM" para minutos, fica mais facil de comparar
    convertidos = []
    for inicio, fim in turnos:
        h1, m1 = inicio.split(":")
        h2, m2 = fim.split(":")
        ini_min = int(h1) * 60 + int(m1)
        fim_min = int(h2) * 60 + int(m2)
        if ini_min >= fim_min:
            raise ValueError("turno invalido: inicio deve ser menor que o fim")
        convertidos.append((ini_min, fim_min))

    convertidos.sort()

    mesclados = []
    atual_ini, atual_fim = convertidos[0]
    for ini, fim in convertidos[1:]:
        if ini <= atual_fim:
            if fim > atual_fim:
                atual_fim = fim
        else:
            mesclados.append((atual_ini, atual_fim))
            atual_ini, atual_fim = ini, fim
    mesclados.append((atual_ini, atual_fim))

    saida = []
    for ini, fim in mesclados:
        saida.append(("%02d:%02d" % (ini // 60, ini % 60),
                      "%02d:%02d" % (fim // 60, fim % 60)))
    return saida
