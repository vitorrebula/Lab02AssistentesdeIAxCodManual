# Coleta de métricas estáticas

Refs #5 — script que roda Radon (complexidade ciclomática, LOC,
Maintainability Index) e jscpd (duplicação de código, equivalente ao PMD CPD
para Python) sobre o código final de cada trial, consolidando o resultado em
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
| `collected_at` | timestamp UTC da coleta |

## Testando com o fixture de exemplo

Há um trial de exemplo em `scripts/metrics/fixtures/` (não é uma kata real do
experimento, apenas para validar o script) que pode ser usado assim:

```bash
python scripts/metrics/collect_metrics.py \
  --trials-dir scripts/metrics/fixtures \
  --output /tmp/static_metrics_teste.csv
```
