# Lab02 Assistentes de IA vs. Codificação Manual

Experimento controlado (crossover within-subject) comparando o uso de
assistente de IA (Claude Code) e codificação manual, em relação a tempo de
resolução, defeitos e qualidade estrutural do código, em katas Python.

## Estrutura do repositório

```
docs/
  RELATORIO_FINAL.md        # Passo 5 — relatório final (estrutura do template da disciplina)
  checklist-entregaveis.md  # auditoria: o que está pronto, as ressalvas e o que falta
  desenho-experimento.md    # Issue #1 — RQ1..RQ5, hipóteses H0/H1, variáveis, desenho crossover
  ambiente-experimento.md   # Issue #6 — linguagem, IDE, assistente de IA, convenções
  katas_justificativa.md    # Issue #3 — fonte das katas e equivalência de dificuldade
  ameacas_validade.md       # Issue #2 — ameaças à validade
  revisao-dados-s02.md      # Issue #44 — cobertura, proveniência, censura, outliers
  analise-rq1..rq5.md       # uma análise por questão de pesquisa
scripts/
  metrics/                  # Issue #5 — coleta de métricas estáticas (Radon + jscpd)
  timing/                   # Issue #4 — cronometragem do time-to-green (time-box 35 min)
  analysis/                 # consolidação (#44) + testes estatísticos de RQ1..RQ5
  dashboard/                # Issue #48/#49 — carga/consolidação, figuras e notebook
  report/                   # Passo 5 — gera o .docx a partir do Markdown + template
trials/
  <participante>/<kata>_<ai|manual>/
    src/                    # código de cada trial (S02)
    tests/                  # testes de aceitação da kata
dados/
  consolidado.csv           # 14 trials, um por linha, com proveniência (gerado)
  outliers.csv              # sinalizações de Tukey e a decisão de cada uma (gerado)
  rq1..rq5_resultados.json  # saída dos testes estatísticos (gerado)
results/
  static_metrics.csv        # saída do script de métricas (gerado)
  timing.json / timing.csv  # saída do script de cronometragem (gerado)
  dashboard_dataset.csv     # dataset único do dashboard, um trial por linha (gerado)
  dashboard_paired.csv      # mesmo dataset pareado por integrante (gerado)
  figures/                  # 11 figuras, uma por RQ + as da issue #49 (gerado)
RelatorioFinal_Lab02.docx   # relatório no formato do template (gerado)
```

## Questões de pesquisa

| RQ | Pergunta | Gráfico | Análise |
|---|---|---|---|
| RQ1 | O uso de IA reduz o **tempo** (time-to-green)? | violino | [analise-rq1.md](docs/analise-rq1.md) |
| RQ2 | O uso de IA reduz **defeitos** (testes falhando)? | heatmap | [analise-rq2.md](docs/analise-rq2.md) |
| RQ3 | O uso de IA altera **complexidade/duplicação**? | box plot | [analise-rq3.md](docs/analise-rq3.md) |
| **RQ4** | Há associação entre **tempo e estrutura**? *(RQ extra)* | dispersão + Pearson | [analise-rq4.md](docs/analise-rq4.md) |
| **RQ5** | O efeito da IA é **homogêneo entre as katas**? *(diferencial)* | bolhas | [analise-rq5.md](docs/analise-rq5.md) |

## Desenho do experimento

Ver [docs/desenho-experimento.md](docs/desenho-experimento.md): questões de
pesquisa, hipóteses H0/H1 das três RQs (tempo, defeitos, estrutura),
variáveis independente/dependentes/controladas e o desenho **crossover
within-subject contrabalanceado** (quadrado latino 2×2), além da análise
estatística planejada e das ameaças à validade.

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

## Dashboard: carga e consolidação dos dados

Ver [scripts/dashboard/README.md](scripts/dashboard/README.md). Junta tempo,
taxa de sucesso e métricas estáticas em um DataFrame único (chave
`participant` + `kata` + `treatment`), pronto para os gráficos e os testes
estatísticos. Usa o consolidado da Issue #44 quando ele existir e, enquanto
não existir, monta o dataset a partir de `results/timing.json` +
`results/static_metrics.csv`.

```bash
pip install -r scripts/dashboard/requirements.txt
python scripts/dashboard/load_data.py \
  --output results/dashboard_dataset.csv \
  --paired-output results/dashboard_paired.csv
```

O notebook [scripts/dashboard/dashboard.ipynb](scripts/dashboard/dashboard.ipynb)
faz essa carga e organiza as seções de RQ1 a RQ5: descritivos, testes
estatísticos (lidos dos JSON de `dados/`), as 11 figuras e a tabela-síntese por
RQ do Relatório Final. Executa de ponta a ponta com *Run All* — e roda os
scripts de análise automaticamente se algum JSON estiver faltando.

## Análise da RQ3

Ver [docs/analise-rq3.md](docs/analise-rq3.md) para a comparação entre
tratamentos, normalização por LOC, mediana/IQR, Wilcoxon pareado e limitações.
Para reproduzir os cálculos: `python -m pip install -r scripts/analysis/requirements.txt`
e `python scripts/analysis/rq3.py`.

## Consolidação e revisão da S02

Execute `python scripts/analysis/consolidate_s02.py` para gerar
`dados/consolidado.csv` e `dados/outliers.csv` a partir dos registros brutos.
A cobertura, a proveniência dos tempos, a censura e as decisões sobre cada
outlier estão em [docs/revisao-dados-s02.md](docs/revisao-dados-s02.md).

## Análise da RQ1

A comparação de tempo até o verde, o pareamento por integrante, o Wilcoxon e
o tratamento de censura estão em [docs/analise-rq1.md](docs/analise-rq1.md).
Execute `python scripts/analysis/rq1.py` para reproduzir os resultados em
`dados/rq1_resultados.json`.

## Análise da RQ2

Ver [docs/analise-rq2.md](docs/analise-rq2.md) para a taxa percentual de testes
passando, falhas absolutas e Wilcoxon pareado. Execute
`python scripts/analysis/rq2.py` para gerar `dados/rq2_resultados.json`.

## Análise da RQ4 (RQ extra) e da RQ5 (diferencial do grupo)

**RQ4** troca a comparação entre tratamentos por uma medida de **associação**
entre tempo e estrutura (r de Pearson com IC 95%, ρ de Spearman, Holm sobre a
família de 5 métricas), reportada global **e dentro de cada tratamento** — ver
[docs/analise-rq4.md](docs/analise-rq4.md). **RQ5** reanalisa os mesmos dados
mudando a unidade de agregação de integrante para **kata**, com *speedup* e
ganho em minutos por kata — ver [docs/analise-rq5.md](docs/analise-rq5.md).

```bash
python scripts/analysis/rq4.py   # -> dados/rq4_resultados.json
python scripts/analysis/rq5.py   # -> dados/rq5_resultados.json
```

## Figuras: um tipo de gráfico por RQ

`scripts/dashboard/plots.py` gera as figuras da issue #49 (box plot, pares,
barras) e `scripts/dashboard/plots_advanced.py` gera **uma figura por RQ**, cada
uma no tipo adequado à pergunta: violino (RQ1), heatmap (RQ2), box plot das 4
métricas estruturais (RQ3), dispersão com r de Pearson (RQ4) e bolhas (RQ5). As
estatísticas anotadas nas figuras de RQ4 e RQ5 são **lidas dos JSON** dos
scripts de análise, de modo que figura, notebook e relatório não possam
divergir.

```bash
python scripts/dashboard/plots.py
python scripts/dashboard/plots_advanced.py    # results/figures/rq{1..5}_*.png
```

## Relatório Final

[docs/RELATORIO_FINAL.md](docs/RELATORIO_FINAL.md) segue a estrutura do
`Template_Relatorio_Laboratorio.docx` (introdução com hipóteses, contexto,
metodologia com desafios/decisões/etapas/ferramentas/tabela de métricas e
inovações, resultados com um gráfico por RQ, discussão, conclusão e
referências). Para gerar a versão `.docx` com os estilos do template e as
figuras embutidas:

```bash
python -m pip install -r scripts/report/requirements.txt
python scripts/report/build_docx.py     # -> RelatorioFinal_Lab02.docx
```

> Antes de entregar: preencher o **link do repositório/GitHub Projects**, a
> **data**, as **colunas e o limite de WIP do board** e o **print do Kanban** —
> os únicos campos marcados como `<preencher>`. As pendências de processo estão
> listadas em [docs/checklist-entregaveis.md](docs/checklist-entregaveis.md).
