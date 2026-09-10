# Kata 2 — Escala de Plantões

Implemente uma função que mescla turnos de plantão que se sobrepõem ou são
contíguos.

## Função a implementar (arquivo `solucao.py`)

### `mesclar_turnos(turnos: list[tuple[str, str]]) -> list[tuple[str, str]]`

- `turnos` é uma lista de tuplas `(inicio, fim)`, com horários no formato
  `"HH:MM"` (24h), onde `inicio < fim` dentro do mesmo dia.
- Dois turnos são considerados sobrepostos ou contíguos se o início de um for
  **menor ou igual** ao fim do outro (ex.: `("09:00","10:00")` e
  `("10:00","11:00")` devem ser mesclados em `("09:00","11:00")`).
- A função deve retornar a lista de turnos mesclados, **ordenada por horário
  de início**, cada um como tupla `(inicio, fim)` no formato `"HH:MM"`.
- Se `turnos` for vazia, retornar lista vazia.
- Se algum turno tiver `inicio >= fim`, lance `ValueError`.
- A lista de entrada pode vir em qualquer ordem.

### Exemplo
```python
mesclar_turnos([("14:00","16:00"), ("09:00","10:30"), ("10:00","12:00")])
# -> [("09:00", "12:00"), ("14:00", "16:00")]
```

## Critério de aceite
Todos os testes em `teste_aceitacao.py` devem passar.
