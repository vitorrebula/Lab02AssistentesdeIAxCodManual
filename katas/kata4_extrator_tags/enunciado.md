# Kata 4 — Extrator de Tags

Um texto usa uma pseudo-marcação simples no formato `[tag]conteúdo[/tag]`
(sem aninhamento). Implemente funções para extrair e para remover essas
marcações.

## Funções a implementar (arquivo `solucao.py`)

### `extrair_tags(texto: str) -> dict[str, list[str]]`
- Retorna um dicionário mapeando cada nome de tag encontrado para a lista
  de conteúdos (na ordem em que aparecem no texto) entre `[tag]` e `[/tag]`.
- Tags sem marcação de fechamento correspondente devem ser ignoradas.
- Se não houver tags, retorna `{}`.
- Nomes de tag são sempre letras minúsculas (`[a-z]+`).

### `remover_tags(texto: str) -> str`
- Retorna o texto com todas as marcações `[tag]` e `[/tag]` removidas,
  mas mantendo o conteúdo interno.
- Espaços extras não precisam ser normalizados (apenas remova os
  marcadores literalmente).

### Exemplo
```python
extrair_tags("Isto e [b]importante[/b] e [i]sutil[/i], mas [b]urgente[/b].")
# -> {"b": ["importante", "urgente"], "i": ["sutil"]}

remover_tags("Isto e [b]importante[/b].")
# -> "Isto e importante."
```

## Critério de aceite
Todos os testes em `teste_aceitacao.py` devem passar.
