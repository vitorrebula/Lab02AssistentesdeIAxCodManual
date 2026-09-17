def processar_eventos(eventos: list[str]) -> list[str]:
    trancada = True
    resultados = []

    for evento in eventos:
        if evento not in ("moeda", "empurrar"):
            raise ValueError(f"evento invalido: {evento}")

        if evento == "moeda":
            if trancada:
                trancada = False
                resultados.append("destrancada")
            else:
                resultados.append("moeda_ignorada")
        else:  # evento == "empurrar"
            if trancada:
                resultados.append("bloqueado")
            else:
                trancada = True
                resultados.append("passou")

    return resultados


if __name__ == "__main__":
    eventos = ["empurrar", "moeda", "moeda", "empurrar", "empurrar"]
    print(processar_eventos(eventos))
    # -> ['bloqueado', 'destrancada', 'moeda_ignorada', 'passou', 'bloqueado']