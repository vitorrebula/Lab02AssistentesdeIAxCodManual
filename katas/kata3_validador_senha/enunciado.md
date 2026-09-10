# Kata 3 — Validador de Senha Corporativa

Implemente um validador de senhas que retorna a lista de regras violadas
(não apenas um booleano), para permitir feedback detalhado ao usuário.

## Função a implementar (arquivo `solucao.py`)

### `validar_senha(senha: str) -> list[str]`

Verifique as regras abaixo, **nesta ordem**, e retorne uma lista com o
identificador de cada regra violada (strings exatas abaixo). Se nenhuma
regra for violada, retorne lista vazia `[]`.

| Identificador       | Regra                                                              |
|----------------------|---------------------------------------------------------------------|
| `"tamanho_minimo"`   | senha deve ter pelo menos 8 caracteres                             |
| `"sem_maiuscula"`    | senha deve conter ao menos 1 letra maiúscula                       |
| `"sem_minuscula"`    | senha deve conter ao menos 1 letra minúscula                       |
| `"sem_digito"`       | senha deve conter ao menos 1 dígito                                |
| `"sem_especial"`     | senha deve conter ao menos 1 caractere de `!@#$%`                  |
| `"contem_espaco"`    | senha não pode conter espaços em branco                            |
| `"contem_palavra_senha"` | senha não pode conter a substring `"senha"` (case-insensitive) |

Todas as regras violadas devem aparecer na lista (não pare na primeira).

### Exemplos
```python
validar_senha("abc")
# -> ["tamanho_minimo", "sem_maiuscula", "sem_digito", "sem_especial"]

validar_senha("Abcd1234!")
# -> []
```

## Critério de aceite
Todos os testes em `teste_aceitacao.py` devem passar.
