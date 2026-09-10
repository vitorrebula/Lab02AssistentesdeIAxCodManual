# Lab02 Assistentes de IA vs. Codificação Manual

Experimento controlado (crossover within-subject) comparando o uso de
assistente de IA (Claude Code) e codificação manual, em relação a tempo de
resolução, defeitos e qualidade estrutural do código, em katas Python.

## Estrutura do repositório

```
docs/
  ambiente-experimento.md   # Issue #6 — linguagem, IDE, assistente de IA, convenções
scripts/
  metrics/                  # Issue #5 — coleta de métricas estáticas (Radon + jscpd)
  timing/                   # Issue #4 — cronometragem do time-to-green (time-box 35 min)
trials/
  <participante>/<kata>_<ai|manual>/
    src/                    # código de cada trial (S02)
    tests/                  # testes de aceitação da kata
results/
  static_metrics.csv        # saída do script de métricas (gerado)
  timing.json / timing.csv  # saída do script de cronometragem (gerado)
```

## Ambiente

Ver [docs/ambiente-experimento.md](docs/ambiente-experimento.md): Python
3.10+, VS Code, Claude Code (Claude Pro) como assistente de IA fixo para
todos os trials.

## Cronometragem (time-to-green)

Ver [scripts/timing/README.md](scripts/timing/README.md). Cronometra cada
trial até todos os testes de aceitação passarem, com time-box fixo de
35 minutos; trials que estouram o tempo são registrados como **censurados em
35 min** (nunca descartados). Saída em `results/timing.json` +
`results/timing.csv`.

```bash
python scripts/timing/track_time.py start --participant vitor --kata kata2 --treatment ai
python scripts/timing/track_time.py green
```

## Métricas estáticas

Ver [scripts/metrics/README.md](scripts/metrics/README.md) para instalar e
rodar a coleta de complexidade ciclomática, LOC, Maintainability Index
(Radon) e duplicação de código (jscpd) sobre o código final de cada trial.
