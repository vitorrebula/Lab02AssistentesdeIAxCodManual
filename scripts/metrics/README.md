# Coleta de métricas estáticas

Refs #5 — script que roda Radon (complexidade ciclomática, LOC,
Maintainability Index), jscpd (duplicação de código, equivalente ao PMD CPD
para Python) e a suíte de aceitação de cada trial sob `pytest-cov` (cobertura
de linhas) sobre o código final de cada trial, consolidando o resultado em
uma tabela por trial/tratamento.

## Pré-requisitos

- Python 3.10+
- Node.js 18+ (usado via `npx jscpd`, sem precisar instalar globalmente)

```bash
pip install -r scripts/metrics/requirements.txt
```

## Convenção de entrada

O script espera o código de cada trial em:

```
trials/<participante>/<kata>_<ai|manual>/src/*.py
```

(ver `docs/ambiente-experimento.md`, seção 4). Arquivos de teste
(`test_*.py`, `*_test.py`) são ignorados no cálculo de complexidade/LOC.

## Uso

```bash
python scripts/metrics/collect_metrics.py
# ou, para customizar caminhos:
python scripts/metrics/collect_metrics.py --trials-dir trials --output results/static_metrics.csv
```

Saída: um CSV em `results/static_metrics.csv` com uma linha por trial:

| coluna | descrição |
|---|---|
| `participant` | integrante que executou o trial |
| `kata` | identificador da kata |
| `treatment` | `ai` ou `manual` |
| `files` | nº de arquivos `.py` analisados |
| `loc` / `sloc` | linhas de código / linhas de código-fonte (sem brancos/comentários) |
| `cc_avg` / `cc_total` | complexidade ciclomática média e total por função/método |
| `mi_avg` | Maintainability Index médio |
| `duplication_pct` | % de linhas duplicadas (jscpd) |
| `coverage_pct` | % de linhas de `src/` exercitadas pela suíte de aceitação do trial (`pytest-cov`) |
| `collected_at` | timestamp UTC da coleta |

### Sobre `duplication_pct`

O jscpd roda isolado por trial, sobre um único arquivo `src/solucao.py` de
poucas dezenas de linhas. Sem outro arquivo para comparar e sem bloco repetido
de ≥5 linhas/50 tokens dentro do próprio arquivo, o resultado tende a 0% quase
por construção — isso é o valor real devolvido pelo jscpd (não é o fallback de
`duplication_pct=0.0` usado quando `npx`/jscpd falha), mas também não é uma
métrica informativa para comparar tratamentos neste desenho.

### Sobre `coverage_pct`

Roda `pytest --cov=src` isolado por trial (mesmo padrão de descoberta
`python_files=test_*.py teste_*.py *_test.py` usado na suíte de aceitação),
medindo quantas linhas de `src/solucao.py` são exercitadas pelos testes da
kata. Cobertura baixa é sinal de código morto ou de branches defensivos que a
suíte de aceitação não cobre — uma dimensão diferente de CC/MI/duplicação, que
descrevem a forma do código, não o quanto dele é de fato usado pelos testes.
Se o trial não tiver `tests/` ou o `pytest-cov` não estiver instalado, o
script avisa em stderr e grava `0.0` (mesmo padrão de fallback do jscpd).

## Testando com o fixture de exemplo

Há um trial de exemplo em `scripts/metrics/fixtures/` (não é uma kata real do
experimento, apenas para validar o script) que pode ser usado assim:

```bash
python scripts/metrics/collect_metrics.py \
  --trials-dir scripts/metrics/fixtures \
  --output /tmp/static_metrics_teste.csv
```
