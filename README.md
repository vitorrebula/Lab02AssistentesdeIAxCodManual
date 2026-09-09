# Lab02 — Assistentes de IA vs. Codificação Manual

Experimento controlado (crossover within-subject) comparando o uso de
assistente de IA (Claude Code) e codificação manual, em relação a tempo de
resolução, defeitos e qualidade estrutural do código, em katas Python.

## Estrutura do repositório

```
docs/
  ambiente-experimento.md   # Issue #6 — linguagem, IDE, assistente de IA, convenções
scripts/
  metrics/                  # Issue #5 — coleta de métricas estáticas (Radon + jscpd)
trials/
  <participante>/<kata>_<ai|manual>/src/   # código de cada trial (S02)
results/
  static_metrics.csv        # saída consolidada do script de métricas (gerado)
```

## Ambiente

Ver [docs/ambiente-experimento.md](docs/ambiente-experimento.md): Python
3.10+, VS Code, Claude Code (Claude Pro) como assistente de IA fixo para
todos os trials.

## Métricas estáticas

Ver [scripts/metrics/README.md](scripts/metrics/README.md) para instalar e
rodar a coleta de complexidade ciclomática, LOC, Maintainability Index
(Radon) e duplicação de código (jscpd) sobre o código final de cada trial.
