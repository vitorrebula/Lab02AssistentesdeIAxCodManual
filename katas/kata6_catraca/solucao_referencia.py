def processar_eventos(eventos):
    resultados = []
    destrancada = False

    for evento in eventos:
        if evento == "moeda":
            if destrancada:
                resultados.append("moeda_ignorada")
            else:
                destrancada = True
                resultados.append("destrancada")
        elif evento == "empurrar":
            if destrancada:
                destrancada = False
                resultados.append("passou")
            else:
                resultados.append("bloqueado")
        else:
            raise ValueError(f"evento invalido: {evento}")

    return resultados
