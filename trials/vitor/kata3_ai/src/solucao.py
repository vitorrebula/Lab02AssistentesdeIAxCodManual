def validar_senha(senha):
    violacoes = []

    if len(senha) < 8:
        violacoes.append("tamanho_minimo")
    if not any(c.isupper() for c in senha):
        violacoes.append("sem_maiuscula")
    if not any(c.islower() for c in senha):
        violacoes.append("sem_minuscula")
    if not any(c.isdigit() for c in senha):
        violacoes.append("sem_digito")
    if not any(c in "!@#$%" for c in senha):
        violacoes.append("sem_especial")
    if any(c.isspace() for c in senha):
        violacoes.append("contem_espaco")
    if "senha" in senha.lower():
        violacoes.append("contem_palavra_senha")

    return violacoes
