def soma(a, b):
    return a + b


def classifica_numero(n):
    if n < 0:
        return "negativo"
    elif n == 0:
        return "zero"
    elif n < 10:
        return "pequeno"
    elif n < 100:
        return "medio"
    else:
        return "grande"
