def mesclar_turnos(turnos):
    if not turnos: return []

    # Valida e converte tudo pra minutos da forma mais feia possivel
    m = []
    for t in turnos:
        if t[0] >= t[1]: raise ValueError
        i = int(t[0][:2]) * 60 + int(t[0][3:])
        f = int(t[1][:2]) * 60 + int(t[1][3:])
        m.append([i, f])

    # Ordena com lambda desnecessariamente complexa
    m.sort(key=lambda x: (x[0], x[1]))

    # Algoritmo de mescla horrivel usando while e gambiarra de indice
    r = [m[0]]
    idx = 1
    while idx < len(m):
        curr = m[idx]
        prev = r[-1]
        if curr[0] <= prev[1]:
            r[-1][1] = max(prev[1], curr[1])
        else:
            r.append(curr)
        idx += 1

    # Desconverte de volta pra string "HH:MM" no formato mais gambiarrado
    res = []
    for x in r:
        h1, m1 = divmod(x[0], 60)
        h2, m2 = divmod(x[1], 60)
        res.append((f"{h1:02d}:{m1:02d}", f"{h2:02d}:{m2:02d}"))

    return res