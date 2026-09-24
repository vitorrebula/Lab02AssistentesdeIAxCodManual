# Pipeline de importação, consolidação e gráficos do dashboard

Refs #48 — carga dos dados do experimento com Pandas: junta **tempo**,
**taxa de sucesso** e **métricas estáticas** em um DataFrame único (uma linha
por trial), pronto para plotagem e para os testes estatísticos
(#45, #46, #47).

Refs #49 — [`plots.py`](plots.py) gera as figuras por RQ a partir desse
DataFrame (boxplots de mediana/IQR, gráfico de pares por integrante, barras de
taxa de sucesso), exportadas em PNG para `results/figures/` e prontas para
entrar no Relatório Final. Ver [Gráficos por RQ](#gráficos-por-rq-issue-49).

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

O notebook [`dashboard.ipynb`](dashboard.ipynb) faz essa carga, organiza as
seções de **RQ1 a RQ5**, renderiza as 11 figuras (também gravadas em
`results/figures/`), imprime os testes estatísticos — lidos dos JSON de
`dados/`, gerados por `scripts/analysis/` — e monta a tabela-síntese por RQ do
Relatório Final. Executa de ponta a ponta com *Run All*; se algum
`dados/rq*_resultados.json` estiver faltando, o próprio notebook roda o script
de análise correspondente.

## Gráficos por RQ (issue #49)

`plots.py` consome o `build_dataset()` acima — nenhum número é digitado no
módulo — e produz um arquivo PNG por figura.

```bash
# grava todas as figuras em results/figures/
python scripts/dashboard/plots.py

# outro destino, outra resolução/formato
python scripts/dashboard/plots.py --fig-dir /tmp/figs --dpi 300 --format pdf
```

Flags: `--fig-dir`, `--dpi`, `--format {png,pdf,svg}`, `--agg`
(agregador dos trials de um integrante no gráfico de pares), `--repo-root`,
`--quiet`.

| figura | conteúdo | RQ |
|---|---|---|
| `rq1_time_to_green.png` | (a) boxplot de `time_to_green_min` por tratamento + (b) pares por integrante | RQ1 |
| `rq2_taxa_sucesso.png` | (a) barras de taxa de sucesso + (b) boxplot de `pct_tests_passing` | RQ2 |
| `rq3_estrutura.png` | painel único com `cc_avg`, `duplication_pct` e `loc` | RQ3 (H3a/H3b/H3c) |
| `rq3_cc_avg.png` · `rq3_duplication_pct.png` · `rq3_loc.png` | uma figura por métrica: boxplot + pares por integrante | RQ3 |

Como módulo (é o que o notebook faz):

```python
from plots import figure_rq1, figure_rq2, figure_rq3_overview, export_all, save_figure

fig = figure_rq1(df)                                  # matplotlib Figure
save_figure(fig, FIG_DIR / "rq1_time_to_green.png")   # PNG para o relatório
export_all(df, FIG_DIR)                               # todas de uma vez
```

Blocos reutilizáveis: `boxplot_by_treatment(ax, df, metric)`,
`paired_panel(ax, df, metric)` e `success_rate_panel(ax, df)` — qualquer
métrica do dataset pode ganhar figura sem duplicar estilo.

### Convenções de leitura das figuras

Decisões de representação, para que a figura não diga mais do que o dado
suporta:

- **Caixa = IQR (Q1–Q3), linha = mediana, hastes = mínimo e máximo.** As
  hastes vão até os extremos (`whis=(0,100)`) e não há *fliers* escondidos:
  **todos os trials aparecem como pontos** sobre a caixa (jitter determinístico,
  semente fixa). Com n = 4 por tratamento, esconder ponto seria perder o dado.
- **Mediana rotulada na figura; IQR e n no rótulo do eixo x** — os descritivos
  declarados na §7 do desenho ficam legíveis sem consultar tabela.
- **Censura sinalizada.** No gráfico de tempo, trial censurado sai como
  **triângulo vazado** (não como ponto) na altura do time-box, a linha de
  referência dos 35 min entra no eixo e a contagem de censurados aparece sob
  cada tratamento. Sem censura na amostra, o eixo **não** é esticado até 35 min
  (achataria os tempos observados) e a figura diz isso em texto, com o máximo
  observado.
- **Gráfico de pares em todas as figuras de RQ1/RQ3**, porque a unidade de
  análise do desenho crossover é o integrante (§5) — os trials de um integrante
  são agregados pela mediana (`--agg`).
- **Duas cores só**, uma por tratamento (azul = sem IA, laranja = com IA),
  validadas para daltonismo (ΔE CVD 24,7); identidade também pela posição no
  eixo e pela legenda, nunca só pela cor.
- **Métrica sem variação** (ex.: `duplication_pct` = 0 em todos os trials) é
  desenhada e **anotada como tal**, em vez de omitida.
- Cada figura carrega título, subtítulo com a convenção de leitura, nota de
  fonte (`results/dashboard_dataset.csv`) e a issue do teste estatístico
  correspondente — são autocontidas para colar no relatório.

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
| `results/figures/*.png` | figuras por RQ (`plots.py`, issue #49) |

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

## Figuras avançadas: uma por RQ (`plots_advanced.py`)

`plots_advanced.py` complementa `plots.py` com **uma figura por questão de
pesquisa**, cada uma no tipo de gráfico adequado à pergunta:

| Arquivo | RQ | Tipo | Por que este tipo |
|---|---|---|---|
| `rq1_violino_tempo.png` | RQ1 | violino + pares | mostra a forma da distribuição (bimodal entre tratamentos), não só mediana/IQR |
| `rq2_heatmap_testes.png` | RQ2 | heatmap integrante × kata | com todos os trials em 100%, um boxplot seria uma linha reta; o heatmap mostra o teto e a cobertura |
| `rq3_boxplot_estrutura.png` | RQ3 | box plot (4 métricas) | comparar dois tratamentos no mesmo grupo, com os trials visíveis |
| `rq4_dispersao_pearson.png` | RQ4 | dispersão + reta + `r` | relação entre duas medidas numéricas |
| `rq5_bolhas_speedup.png` | RQ5 | bolhas | três dimensões por kata: dificuldade × speedup × nº de testes (cor = razão de LOC) |

As estatísticas anotadas em RQ4 e RQ5 são **lidas** de
`dados/rq4_resultados.json` e `dados/rq5_resultados.json` — o módulo não
recalcula teste nenhum, para que figura, JSON, notebook e relatório não possam
divergir. Rode os scripts de análise antes:

```bash
python scripts/analysis/rq4.py
python scripts/analysis/rq5.py
python scripts/dashboard/plots_advanced.py            # results/figures/
python scripts/dashboard/plots_advanced.py --fig-dir /tmp/figs --dpi 300 --format pdf
```

A paleta dos dois tratamentos é a mesma de `plots.py` e passa nos seis checks de
contraste/daltonismo (ΔE CVD 24,7; ΔE visão normal 33,6); o heatmap usa rampa
sequencial de um único tom e as bolhas, rampa divergente com cinza neutro no
meio.
