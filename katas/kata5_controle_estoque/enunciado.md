# Kata 5 — Controle de Estoque

Implemente um pequeno controle de estoque por SKU, com registro de
entradas/saídas e verificação de alertas de reposição.

## Funções a implementar (arquivo `solucao.py`)

### `criar_estoque() -> dict`
Retorna um estoque vazio: `{}` (dict de `sku -> quantidade`).

### `registrar_entrada(estoque, sku, qtd)`
Soma `qtd` à quantidade do `sku` (cria a entrada com valor `qtd` se o SKU
ainda não existir). Se `qtd <= 0`, lance `ValueError`.

### `registrar_saida(estoque, sku, qtd)`
Subtrai `qtd` da quantidade do `sku`. Regras:
- Se `qtd <= 0`, lance `ValueError`.
- Se o `sku` não existir no estoque, lance `KeyError`.
- Se a saída deixar a quantidade negativa (estoque insuficiente), lance
  `ValueError` e **não** altere o estoque.

### `verificar_alertas(estoque, limites) -> list[str]`
- `limites` é um dict `sku -> quantidade_minima`.
- Retorna a lista de SKUs (ordenada alfabeticamente) cuja quantidade atual
  no estoque é **menor que** o limite mínimo definido para ele.
- SKUs presentes em `limites` mas ausentes do estoque contam como
  quantidade 0 (portanto entram no alerta se o limite for > 0).
- SKUs do estoque que não têm limite definido são ignorados (não geram
  alerta).

## Critério de aceite
Todos os testes em `teste_aceitacao.py` devem passar.
