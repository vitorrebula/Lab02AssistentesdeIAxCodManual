# Cronometragem e registro de tempo (time-to-green)

Refs #4 — script que cronometra cada trial até o **time-to-green** (todos os
testes de aceitação da kata passando), com **time-box fixo de 35 minutos**, e
grava o resultado em formato estruturado (JSON + CSV) para uso posterior no
dashboard.

Regra central do experimento: **trial que estoura o time-box não é
descartado** — é registrado como *censurado* em 35 min (`censored = true`,
`time_to_green_s = 2100`). Isso preserva a amostra e permite tratar os dados
como análise de sobrevivência (coluna `event`: 1 = verde observado,
0 = censurado).

## Pré-requisitos

- Python 3.10+
- `pytest` (usado para verificar se os testes de aceitação estão verdes)

```bash
pip install -r scripts/timing/requirements.txt
```

## Convenção de entrada

O script espera cada trial em (ver `docs/ambiente-experimento.md`, seção 4):

```
trials/<participante>/<kata>_<ai|manual>/
  src/      # solução
  tests/    # testes de aceitação da kata
```

O `pytest` roda com `trial/` e `trial/src/` no `PYTHONPATH`, então os testes
podem importar tanto `from src.foo import ...` quanto `from foo import ...`.

## Uso no dia do trial

```bash
# 1. inicia o cronômetro (time-box de 35 min)
python scripts/timing/track_time.py start --participant vitor --kata kata2 --treatment ai

# 2. (opcional, a qualquer momento) quanto já passou / quanto resta
python scripts/timing/track_time.py status

# 3. ao achar que terminou: verifica os testes e para o cronômetro
python scripts/timing/track_time.py green
```

O comando `green` só fecha o trial como verde se o `pytest` realmente passar.
Se ainda houver teste falhando **e** sobrar time-box, ele recusa e mantém o
cronômetro rodando. Se o time-box já tiver estourado, fecha como censurado em
35 min automaticamente.

### Modo automático (recomendado)

Roda o `pytest` em intervalos e para exatamente quando fica verde — dispensa o
participante lembrar de rodar `green` e reduz o erro de medição:

```bash
python scripts/timing/track_time.py watch --participant vitor --kata kata2 --treatment ai --interval 15
```

Inicia o cronômetro (se ainda não estiver rodando) e encerra sozinho no verde
ou no estouro do time-box.

### Casos especiais

```bash
# participante desistiu antes dos 35 min -> censurado no tempo decorrido
python scripts/timing/track_time.py green --abort --notes "desistiu: travou na regra X"

# fechar como verde sem rodar pytest (só se a validação foi feita na mão)
python scripts/timing/track_time.py green --no-verify

# tempo medido fora do script (cronômetro externo / planilha)
python scripts/timing/track_time.py record --participant ana --kata kata1 --treatment manual \
  --elapsed 41:30      # >= 35 min -> registrado como censurado em 35 min
python scripts/timing/track_time.py record --participant ana --kata kata1 --treatment ai \
  --elapsed 12:30 --tests-passed 8

# regera o CSV a partir do JSON (ex.: depois de editar uma anotação)
python scripts/timing/track_time.py export
```

`--elapsed` aceita `MM:SS`, `HH:MM:SS` ou minutos decimais (`12.5`).

## Saída

| arquivo | papel |
|---|---|
| `results/timing.json` | fonte da verdade, um objeto por trial |
| `results/timing.csv` | mesma informação em tabela, para o dashboard |
| `results/timing_state.json` | trials em andamento (transitório, fora do git) |

Colunas:

| coluna | descrição |
|---|---|
| `participant` / `kata` / `treatment` | identificação do trial (`treatment` = `ai` ou `manual`) |
| `started_at` / `ended_at` | timestamps UTC de início e fim do cronômetro |
| `elapsed_s` / `elapsed_min` | tempo bruto medido, **sem** cortar no time-box |
| `time_to_green_s` / `time_to_green_min` | métrica de análise: tempo até o verde, ou 2100 s (35 min) se censurado |
| `censored` | `True` se o verde **não** foi observado dentro do time-box |
| `event` | 1 = verde observado, 0 = censurado (indicador para análise de sobrevivência) |
| `status` | `green`, `censored_timebox` (estourou 35 min) ou `censored_aborted` (abandonou antes) |
| `timebox_s` | time-box usado (2100 s por padrão) |
| `tests_passed` / `tests_failed` | contagem do `pytest` no momento do fechamento |
| `notes` | observação livre (`--notes`) |
| `recorded_at` | timestamp UTC da gravação |

`elapsed_*` e `time_to_green_*` são separados de propósito: o primeiro
documenta o que de fato aconteceu (ex.: 40 min), o segundo é o valor a usar na
análise, já censurado em 35 min.

Regravar o mesmo trial (mesmo `participant` + `kata` + `treatment`) substitui
o registro anterior, para não duplicar linha no dashboard.

## Testando com os fixtures de exemplo

Há dois trials de exemplo em `scripts/timing/fixtures/` (não são katas reais
do experimento, servem só para validar o script): `kata0_manual` com os testes
verdes e `kata0_ai` com um defeito proposital.

```bash
# fixture verde: fecha como green
python scripts/timing/track_time.py start --participant exemplo_participante \
  --kata kata0 --treatment manual --trials-dir scripts/timing/fixtures \
  --state /tmp/state.json --records /tmp/timing.json --csv /tmp/timing.csv
python scripts/timing/track_time.py green \
  --state /tmp/state.json --records /tmp/timing.json --csv /tmp/timing.csv

# fixture vermelho com time-box curto: fecha como censurado
python scripts/timing/track_time.py start --participant exemplo_participante \
  --kata kata0 --treatment ai --trials-dir scripts/timing/fixtures --timebox 0 \
  --state /tmp/state.json --records /tmp/timing.json --csv /tmp/timing.csv
python scripts/timing/track_time.py green \
  --state /tmp/state.json --records /tmp/timing.json --csv /tmp/timing.csv
```

Use sempre `--state/--records/--csv` apontando para fora de `results/` nos
testes, para não misturar dados de exemplo com os dados reais do experimento.

## Notas de medição

- O tempo é wall-clock em UTC, calculado entre `start` e o fechamento, e
  sobrevive a fechar/reabrir o terminal (o estado fica em disco).
- Não há pausa: o time-box de 35 min é corrido, como definido no desenho do
  experimento. Interrupções devem ser anotadas em `--notes` e discutidas como
  ameaça à validade.
- Rode `start` (ou `watch`) **imediatamente antes** de o participante começar a
  ler o enunciado da kata, para que todos os trials meçam a mesma coisa.
