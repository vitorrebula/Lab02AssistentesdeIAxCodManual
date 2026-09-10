# Kata 6 — Máquina de Catraca

Implemente uma máquina de estados simples que simula uma catraca de
acesso, processando uma sequência de eventos.

## Função a implementar (arquivo `solucao.py`)

### `processar_eventos(eventos: list[str]) -> list[str]`

- A catraca começa **trancada**.
- Eventos possíveis: `"moeda"` e `"empurrar"`. Qualquer outro valor deve
  lançar `ValueError`.
- Regras de transição:
  - Evento `"moeda"` quando trancada → destranca. Resultado do evento:
    `"destrancada"`.
  - Evento `"moeda"` quando já destrancada → não muda de estado (moeda
    "sobra"). Resultado do evento: `"moeda_ignorada"`.
  - Evento `"empurrar"` quando destrancada → tranca novamente. Resultado
    do evento: `"passou"`.
  - Evento `"empurrar"` quando trancada → não muda de estado. Resultado
    do evento: `"bloqueado"`.
- A função deve retornar a lista dos resultados de cada evento, na ordem
  em que foram processados (mesmo tamanho da lista de entrada).
- Se `eventos` for vazia, retornar lista vazia.

### Exemplo
```python
processar_eventos(["empurrar", "moeda", "moeda", "empurrar", "empurrar"])
# -> ["bloqueado", "destrancada", "moeda_ignorada", "passou", "bloqueado"]
```

## Critério de aceite
Todos os testes em `teste_aceitacao.py` devem passar.
