# Pipeline de importação e consolidação para o dashboard

Refs #48 — carga dos dados do experimento com Pandas: junta **tempo**,
**taxa de sucesso** e **métricas estáticas** em um DataFrame único (uma linha
por trial), pronto para plotagem (#49) e para os testes estatísticos
(#45, #46, #47).

Toda a importação é reprodutível: os caminhos são relativos à raiz do
repositório (inferida a partir da localização do script), nenhum dado está
embutido no código e, se um arquivo de entrada não existir, a coluna
correspondente fica vazia em vez de ser preenchida com valor inventado.

## Pré-requisitos

```bash
pip install -r scripts/dashboard/requirements.txt
```

Python 3.10+ e pandas 2.x ou 3.x (testado em 2.3 e 3.0).

## Fontes de dados e precedência

| Fonte | Conteúdo | Origem |
|---|---|---|
| `dados/consolidado.csv` | tempo, censura, testes passando/total | Issue #44 (**ainda não existe** no repo) |
| `results/timing.json` | tempo, censura, contagem de testes, notas | `scripts/timing/track_time.py` (#4) |
| `results/timing.csv` | idem, usado como *fallback* do JSON | idem |
| `results/static_metrics.csv` | LOC, SLOC, CC, MI, duplicação | `scripts/metrics/collect_metrics.py` (#5) |

Regras:

1. Se o consolidado da #44 existir (procurado em `dados/consolidado.csv`,
   `data/consolidado.csv`, `results/consolidado.csv`), ele **tem precedência**
   nas colunas de tempo/censura/testes; `timing.json` só preenche o que falta
   (`started_at`, `status`, `notes`, …). Enquanto a #44 não entregar o arquivo,
   o pipeline monta o dataset direto dos brutos — e avisa isso na saída.
2. Nomes de coluna em pt-BR do consolidado são aceitos e normalizados
   (`integrante`→`participant`, `tratamento`→`treatment`, `tempo`→
   `time_to_green_min`, `censurado`→`censored`, `testes_passando`→
   `tests_passed`, `testes_total`→`tests_total`), assim como os rótulos de
   tratamento (`com_ia`/`ia`→`ai`, `sem_ia`→`manual`).
3. A chave de junção é a tripla `participant` + `kata` + `treatment`
   (docs/desenho-experimento.md, §4.2). A junção é **externa**: um trial
   presente em apenas uma das fontes continua no dataset, com as colunas da
   outra vazias e sinalizado em `has_timing` / `has_metrics`.

## Uso

### Como script

```bash
# inspeciona o dataset (fontes, colunas/tipos, descritivos, avisos)
python scripts/dashboard/load_data.py

# grava os artefatos consumidos pelo dashboard
python scripts/dashboard/load_data.py \
  --output results/dashboard_dataset.csv \
  --paired-output results/dashboard_paired.csv

# só o dicionário de dados
python scripts/dashboard/load_data.py --dictionary
```

Flags úteis: `--no-consolidated` (ignora a #44 e usa os brutos),
`--consolidated <arquivo>`, `--timing <arquivo>`, `--static-metrics <arquivo>`,
`--repo-root <dir>`, `--agg {median,mean,min,max}`, `--quiet`.

### Como módulo (notebook do dashboard)

```python
import sys; sys.path.insert(0, "scripts/dashboard")
from load_data import build_dataset, build_paired_frame, describe_dataset

df = build_dataset()          # um trial por linha
print(describe_dataset(df))   # colunas, tipos, não-nulos
pares = build_paired_frame(df)  # um integrante por linha (manual/ai/diff)
```

O notebook [`dashboard.ipynb`](dashboard.ipynb) já faz essa carga e organiza as
seções RQ1/RQ2/RQ3 — os gráficos e testes estatísticos estão marcados como
`TODO(#49)` / `TODO(#45|#46|#47)` para as issues seguintes.

## DataFrame principal (`build_dataset`)

Uma linha por trial, ordenado por `participant`, `kata`, `treatment`.
`treatment` é categoria **ordenada** (`manual` < `ai`), para que eixos e
legendas saiam sempre na mesma ordem. Contagens usam tipos anuláveis (`Int64`,
`boolean`) porque a junção externa pode deixar células vazias.

| coluna | tipo (pandas) | grupo | descrição |
|---|---|---|---|
| `trial_id` | `string` | identificação | chave legível do trial: `<participant>/<kata>_<treatment>` |
| `participant` | `string` | identificação | integrante que executou o trial |
| `kata` | `string` | identificação | identificador da kata (`kata1`..`kata6`) |
| `treatment` | `category` | identificação | fator do experimento: `manual` ou `ai` |
| `time_to_green_s` | `float64` | RQ1 tempo | tempo até o verde em segundos, censurado no time-box |
| `time_to_green_min` | `float64` | RQ1 tempo | idem em minutos — variável dependente primária de RQ1 |
| `elapsed_s` | `float64` | RQ1 tempo | tempo bruto medido, sem cortar no time-box |
| `elapsed_min` | `float64` | RQ1 tempo | idem em minutos |
| `censored` | `boolean` | RQ1 tempo | `True` se o verde não foi observado dentro do time-box |
| `event` | `Int64` | RQ1 tempo | indicador de sobrevivência: 1 = verde observado, 0 = censurado |
| `status` | `string` | RQ1 tempo | `green`, `censored_timebox` ou `censored_aborted` |
| `timebox_s` / `timebox_min` | `float64` | RQ1 tempo | time-box aplicado (2100 s = 35 min) |
| `tests_passed` | `Int64` | RQ2 defeitos | testes de aceitação que passaram no fechamento |
| `tests_failed` | `Int64` | RQ2 defeitos | testes de aceitação que falharam no fechamento |
| `tests_total` | `Int64` | RQ2 defeitos | `tests_passed + tests_failed` (derivada) |
| `pct_tests_passing` | `float64` | RQ2 defeitos | `100 * tests_passed / tests_total` — medida contínua secundária |
| `success` | `boolean` | RQ2 defeitos | `True` se atingiu o verde dentro do time-box — base da taxa de sucesso (teste primário de RQ2) |
| `files` | `Int64` | RQ3 estrutura | nº de arquivos `.py` de solução analisados |
| `loc` | `Int64` | RQ3 estrutura | linhas de código da solução (H3c) |
| `sloc` | `Int64` | RQ3 estrutura | linhas de código sem brancos/comentários |
| `cc_avg` | `float64` | RQ3 estrutura | complexidade ciclomática média por função (H3a) |
| `cc_total` | `float64` | RQ3 estrutura | complexidade ciclomática total (exploratória) |
| `mi_avg` | `float64` | RQ3 estrutura | Maintainability Index médio (exploratória) |
| `duplication_pct` | `float64` | RQ3 estrutura | percentual de linhas duplicadas (H3b) |
| `started_at` / `ended_at` | `datetime64[ns, UTC]` | metadado | início e fim do cronômetro |
| `recorded_at` | `datetime64[ns, UTC]` | metadado | gravação do registro de tempo |
| `collected_at` | `datetime64[ns, UTC]` | metadado | coleta das métricas estáticas |
| `has_timing` / `has_metrics` | `boolean` | metadado | de quais fontes o trial veio |
| `notes` | `string` | metadado | observação livre do trial (desvios, re-registros) |

Colunas derivadas aqui (não existem nos brutos): `trial_id`, `tests_total`,
`pct_tests_passing`, `success`, `timebox_min`, `has_timing`, `has_metrics`, e
as conversões segundos↔minutos quando só um dos dois vem na fonte.

## DataFrames auxiliares

| função | formato | uso |
|---|---|---|
| `build_participant_summary(df, agg="median")` | uma linha por `participant` × `treatment`, com as métricas agregadas + `n_trials`, `n_timed`, `n_success`, `n_censored`, `success_rate` | insumo do teste pareado |
| `build_paired_frame(df, agg="median")` | uma linha por integrante, colunas `<métrica>_manual`, `<métrica>_ai`, `<métrica>_diff` (`diff = ai - manual`) | entrada direta de Wilcoxon/McNemar |
| `success_rate_by_treatment(df)` | uma linha por tratamento | variável primária de RQ2 |
| `descriptives_by_treatment(df, metrics)` | mediana, Q1, Q3, IQR, min, max, média, desvio | descritivos declarados no desenho, §7 |

> ⚠️ A unidade de análise do desenho crossover é o **integrante**, mas cada
> integrante executou mais de um trial por tratamento. O pareamento, portanto,
> agrega os trials de um integrante dentro de cada tratamento — a mediana é o
> default, coerente com os descritivos do desenho (§7), e o agregador é
> parâmetro explícito (`agg=`). A decisão final sobre o agregador e sobre o
> tratamento dos censurados pertence às issues de análise (#45/#46/#47).
> `success_rate` usa como denominador os trials **com registro de tempo**
> (`n_timed`): um trial que só tem métricas estáticas conta como dado faltante,
> não como fracasso.

## Checagens de integridade

`validate_dataset(df)` roda em toda execução do CLI e **não exclui nada** —
apenas lista o que precisa de decisão documentada na #44:

- trial presente em só uma das fontes (tempo sem métricas, ou o contrário);
- tripla `(participant, kata, treatment)` duplicada;
- integrante sem par completo `manual`/`ai` (fica fora do teste pareado);
- kata repetida pelo mesmo integrante (risco de *carryover*, desenho §5);
- `tests_total <= 0`, trial verde com teste falhando, ou `time_to_green` acima
  do time-box (deveria estar censurado).

## Saídas gravadas

| arquivo | conteúdo |
|---|---|
| `results/dashboard_dataset.csv` | DataFrame principal (um trial por linha) |
| `results/dashboard_paired.csv` | formato pareado por integrante |

Os dois são **gerados** — a fonte da verdade continua sendo `results/timing.json`,
`results/static_metrics.csv` e (quando existir) o consolidado da #44.

## Testando com os fixtures

Há um mini-repositório de exemplo em `scripts/dashboard/fixtures/` (dados
fictícios, não são trials reais) com um trial censurado, um trial só com tempo
e um trial só com métricas, para exercitar a junção externa e os avisos:

```bash
# usa dados/consolidado.csv do fixture (simula a entrega da #44)
python scripts/dashboard/load_data.py --repo-root scripts/dashboard/fixtures

# ignora o consolidado e monta a partir dos brutos
python scripts/dashboard/load_data.py --repo-root scripts/dashboard/fixtures --no-consolidated
```

Esperado nos dois casos: 5 trials, `manual` com 1 censurado e taxa de sucesso
0,5, e dois avisos de junção (`exemplo_dois/kata9_ai` sem métricas,
`exemplo_dois/kata7_ai` sem tempo).

## Pendências das próximas issues

- **#44** — gerar `dados/consolidado.csv` e registrar as decisões de outlier;
  quando existir, este pipeline passa a usá-lo sem alteração de código.
- **#45/#46/#47** — preencher os testes estatísticos nas seções do notebook.
- **#49** — gráficos por RQ, exportados em `results/figures/`.
- **#50** — dashboard final + README de reprodução de ponta a ponta.
