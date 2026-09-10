# Kata 1 — Cesta de Compras

Implemente um pequeno módulo de carrinho de compras com as seguintes regras.

## Funções a implementar (arquivo `solucao.py`)

### `criar_carrinho() -> dict`
Retorna um carrinho vazio: `{"itens": []}`.

### `adicionar_item(carrinho, nome, preco, qtd)`
Adiciona um item ao carrinho. `preco` é float positivo, `qtd` é int positivo.
Se `preco <= 0` ou `qtd <= 0`, lance `ValueError`.
Se o item (mesmo `nome`) já existir no carrinho, some a quantidade ao invés de duplicar a entrada.

### `total_sem_desconto(carrinho) -> float`
Retorna a soma de `preco * qtd` de todos os itens, arredondada a 2 casas decimais.

### `aplicar_cupom(total, cupom) -> float`
Regras de cupom:
- `"PROMO10"`: aplica 10% de desconto, **somente se** `total > 100`. Caso contrário o cupom não tem efeito (retorna o total original).
- `"PROMO20"`: aplica 20% de desconto, **somente se** `total > 200`. Caso contrário não tem efeito.
- `None` ou string vazia: nenhum desconto, retorna o total original.
- Qualquer outro valor de cupom: lance `ValueError("cupom invalido")`.
- Resultado sempre arredondado a 2 casas decimais.

### `checkout(carrinho, cupom=None) -> dict`
Retorna `{"total_bruto": <float>, "total_final": <float>, "cupom_aplicado": <bool>}`.
- `total_bruto` = `total_sem_desconto(carrinho)`.
- `total_final` = resultado de `aplicar_cupom(total_bruto, cupom)`.
- `cupom_aplicado` = `True` somente se o total final for menor que o total bruto (ou seja, o desconto de fato incidiu).

## Critério de aceite
Todos os testes em `teste_aceitacao.py` devem passar.
