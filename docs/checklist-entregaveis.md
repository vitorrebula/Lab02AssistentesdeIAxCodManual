# Checagem de entregáveis — Lab02

Auditoria do repositório contra o enunciado do Laboratório 02 (20 pontos).
Legenda: **✔ pronto** · **⚠ pronto com ressalva** · **✘ faltava** (e o que foi
feito) · **◻ só verificável no GitHub Projects**.

Data da checagem: 23/09/2026. Estado do repositório: 14 trials, 3 integrantes,
6 katas, 5 RQs, 11 figuras.

---

## 1. Passos 1–2 — Lab02S01 (desenho + preparação, 5 pts)

| Item do enunciado | Status | Evidência |
|---|---|---|
| (A) Hipóteses nula e alternativa | ✔ | [desenho §3](desenho-experimento.md) — H1, H2, H3a–c e agora H4, H5, todas bicaudais e declaradas *a priori* |
| (B) Variáveis dependentes | ✔ | desenho §4.2 — definição operacional, unidade, instrumento e arquivo de leitura de cada uma |
| (C) Variável independente | ✔ | desenho §4.1 |
| (D) Tratamentos | ✔ | `ai` / `manual`, com regra explícita de que consulta a doc/web é permitida nos dois |
| (E) Objetos experimentais (katas equivalentes) | ✔ | 6 katas **autorais** em `katas/`, com suíte de aceitação e solução de referência; equivalência justificada em [katas_justificativa.md](katas_justificativa.md) |
| (F) Tipo de projeto experimental | ✔ | crossover within-subject contrabalanceado (quadrado latino 2×2), desenho §5 |
| (G) Quantidade de medições | ⚠ | planejado 4 katas × 3 integrantes = 12; executado 14 (2 extras de Vitor). O enunciado pede 4 **ou** 6 katas por integrante — cada um resolveu 4, com Vitor em 6 |
| (H) Ameaças à validade | ✔ | [ameacas_validade.md](ameacas_validade.md) (166 linhas, inclui memorização e baixa indexação) + desenho §8 |
| Ambiente (linguagem, IDE, assistente, cronômetro, scripts) | ⚠ | [ambiente-experimento.md](ambiente-experimento.md); ressalva de protocolo no item 5 abaixo |
| Script de cronometragem | ✔ | `scripts/timing/track_time.py` (time-box 35 min, censura registrada, não descarta) |
| Script de métricas estáticas | ✔ | `scripts/metrics/collect_metrics.py` (Radon + jscpd; CK descartado por exigir Java) |

## 2. Passo 3 — Lab02S02 (execução + coleta, 5 pts)

| Item | Status | Evidência |
|---|---|---|
| Metade das katas com IA, metade sem, por integrante | ✔ | 7 trials `ai` e 7 `manual`; cada integrante 2+2 no plano |
| Ordem contrabalanceada | ✔ | kata1: Paulo manual / Rafael IA / Vitor IA; kata4: inverso — nenhuma kata cai sempre no mesmo tratamento |
| Time-box de 35 min respeitado | ✔ | `timebox_s = 2100` em todos os 14 registros; nenhum trial censurado |
| Tempo até o verde registrado | ⚠ | 10 de 14 cronometrados. Os 4 de Paulo têm horários **derivados dos de Rafael** — ver item 5 |
| Nº de testes passando ao final | ✔ | 14/14 trials com 100% dos testes aprovados; **reexecutado nesta auditoria**: 12, 10, 10, 12, 12, 10, 10, 12, 12, 10, 11, 10, 12, 9 — todos passam |
| Métricas estáticas sobre o código final | ✔ | `results/static_metrics.csv`, 14 linhas |
| Código de cada trial no repositório | ✘→✔ | **faltavam 2 trials** (`vitor/kata3_ai`, `vitor/kata6_manual`), apagados por engano no commit `9415324`; restaurados do histórico e validados (11/11 e 9/9 testes) |

## 3. Passo 4 — análise de resultados (parte dos 5 pts de S03)

| Item | Status | Evidência |
|---|---|---|
| Revisão dos dados e outliers | ✔ | [revisao-dados-s02.md](revisao-dados-s02.md) + `dados/outliers.csv` (4 sinalizações, critério de Tukey, decisão justificada para cada) |
| RQ1 — teste estatístico | ✔ | [analise-rq1.md](analise-rq1.md), `scripts/analysis/rq1.py` → Wilcoxon pareado, censura tratada explicitamente |
| RQ2 — teste estatístico | ✔ | [analise-rq2.md](analise-rq2.md), `rq2.py` → Wilcoxon degenerado documentado como tal (efeito de teto) |
| RQ3 — teste estatístico | ✔ | [analise-rq3.md](analise-rq3.md), `rq3.py` → Wilcoxon + Holm + normalização por LOC |
| Wilcoxon pareado (exigido pelo enunciado) | ✔ | usado em RQ1, RQ2 e RQ3, sempre exato e bicaudal |
| Mediana e IQR em vez de média/desvio | ✔ | política aplicada em todas as tabelas e figuras |
| Trials censurados registrados, não descartados | ✔ | política implementada no `track_time.py` e no consolidador (não há censurados nesta amostra) |

## 4. Passos 5–6 — relatório e dashboard

| Item | Status | Evidência |
|---|---|---|
| Dashboard (Pandas + Matplotlib) | ✔ | `scripts/dashboard/dashboard.ipynb` — executa de ponta a ponta, sem erro, e exporta as 11 figuras |
| Gráficos comparando tempo, taxa de sucesso e métricas estáticas | ✔ | `plots.py` (box/pares/barras) + `plots_advanced.py` (um tipo por RQ) |
| Testes estatísticos dentro do notebook | ✘→✔ | o notebook tinha `TODO(#45)`, `TODO(#46)`, `TODO(#47)` e `TODO(#50)`; agora lê os JSON dos scripts de análise e imprime os testes, mais a tabela-síntese por RQ |
| **RQ extra (RQ4)** | ✘→✔ | [analise-rq4.md](analise-rq4.md), `rq4.py`, figura de dispersão + Pearson |
| **RQ diferencial do grupo (RQ5)** | ✘→✔ | [analise-rq5.md](analise-rq5.md), `rq5.py`, figura de bolhas |
| Um tipo de gráfico diferente por RQ | ✘→✔ | violino (RQ1) · heatmap (RQ2) · box plot (RQ3) · dispersão + Pearson (RQ4) · bolhas (RQ5) |
| **Relatório Final** | ✘→✔ | [RELATORIO_FINAL.md](RELATORIO_FINAL.md), na estrutura do `Template_Relatorio_Laboratorio.docx` |
| Link do repositório/GitHub Projects no relatório | ◻ | campo marcado como `<preencher>` no relatório — **o grupo precisa colar o link do board** |

## 5. Ressalvas de protocolo (não são falta de entrega, mas contam na correção)

Estas são as fragilidades reais do experimento. Todas já estão documentadas nos
docs de análise e reaparecem no Relatório Final — o risco não é o professor
descobrir, é o relatório *não* admitir.

1. **Os 4 trials de Paulo não têm cronometragem independente.** Os horários
   foram derivados dos de Rafael na mesma kata ("início 6 s antes, fim 4 s
   depois"), e os testes foram conferidos depois. Efeito: o Wilcoxon de RQ1
   roda com **2 pares** (Rafael e Vitor), não 3. Consequência prática: nenhum
   teste do laboratório tem poder para detectar nada — o que está dito em todas
   as conclusões.
2. **Assistente de IA divergente do protocolo.** O ambiente fixa **Claude Code**
   para todos os trials `ai`; os trials de Paulo registram **ChatGPT**. O
   enunciado exige o mesmo assistente em todos os trials. Isso quebra a
   comparabilidade interna do tratamento e precisa constar como ameaça — está
   em `analise-rq1.md`, `analise-rq3.md` e no relatório.
3. **Modelo divergente dentro do próprio Claude Code.** `ambiente-experimento.md`
   fixa "mesmo agente (Sonnet)"; os trials de Rafael registram **Opus 5**.
   Menos grave que o item 2, mas é a mesma classe de problema.
4. **`kata2_manual` de Rafael foi reconstituído** após perda do registro
   original (`fonte_tempo=reconstituido`).
5. **`kata4_manual` de Vitor tem `elapsed_s = 1208` contra 56.916 s entre os
   timestamps.** Mantido com sinalização em `dados/outliers.csv`; a origem
   precisa ser esclarecida pelo participante.
6. **Documentação internamente inconsistente:** `ameacas_validade.md` descreve
   "3 katas com IA e 3 sem" por participante (plano de 6 katas), enquanto o
   desenho e a execução usam 2+2 (plano de 4). Vale alinhar o texto das ameaças
   com o que foi de fato executado.
7. **Efeito de teto em RQ2.** Como o registro só fecha um trial como verde
   quando **todos** os testes passam, a taxa de aprovação é 100% por construção
   em todo trial verde — e nenhum trial foi censurado. RQ2, como está
   operacionalizada, não consegue distinguir os tratamentos. Isso é limitação
   de desenho, já declarada no próprio desenho (§3), não erro de execução.
8. **Duplicação 0,0% nos 14 trials.** Pode ser medição real (arquivos pequenos,
   acima do limiar do jscpd) ou *fallback* silencioso do coletor quando o jscpd
   não está disponível. Conferir os logs de execução do `collect_metrics.py`
   antes de afirmar "não houve duplicação".

## 6. Defeitos de pipeline encontrados e corrigidos nesta auditoria

| Defeito | Sintoma | Correção |
|---|---|---|
| Trials apagados, métricas mantidas | `consolidate_s02.py` abortava com *"chaves divergentes entre timing.json, timing.csv, metricas e diretorios trials"* — **o consolidado de S03 não era reproduzível** | restaurados `trials/vitor/kata3_ai` e `kata6_manual` e os 2 registros de tempo perdidos; `dados/consolidado.csv` e `dados/outliers.csv` regenerados **byte a byte idênticos** aos versionados |
| Colisão de colunas na junção do dashboard | `loc` e `cc_total` saíam **vazias** em `results/dashboard_dataset.csv` (viravam `loc_x`/`loc_y`), apagando H3c do dashboard | `load_data.py`: junção com `_merge_prefer_left` + apelidos pt-BR (`cc_media`, `duplicacao_pct`, `mi_medio`) |
| Taxa de sucesso com denominador errado | RQ2 exibia **71,4% (5/7)** em vez de 100%, porque trials sem desfecho registrado entravam como fracasso | denominador passou a ser "trials com desfecho conhecido"; Paulo aparece como dado faltante (`NaN`), não como 0% |
| RQ3 sem saída estruturada | `rq3.py` só imprimia texto, então o notebook e o relatório teriam de redigitar os números | passa a gravar `dados/rq3_resultados.json`, como as demais RQs |

## 7. Itens que só o grupo pode fechar (GitHub Projects)

O enunciado corrige **a partir do board**, e nada disso é verificável do
repositório:

- ◻ **Colunas do board** (mínimo Backlog → To Do → Doing → Review → Done) e
  **limite de WIP** declarado; print do board no relatório (§3.3).
- ◻ **Uma Issue por trial** (kata × tratamento), com **Assignee** do responsável.
- ⚠ **Cada integrante como Assignee de ao menos uma Issue com código commitado
  em cada sprint** (S01, S02, S03) — a ausência **zera a parcela individual**
  daquele integrante na sprint. Pelo histórico de commits:

  | Sprint | Paulo Assis | Rafael Franco | Vitor Rebula |
  |---|---|---|---|
  | **S01** | ✔ 6 katas + testes + justificativa (#3); ameaças à validade (#2) | ✔ desenho do experimento (#1); script de cronometragem (#4) | ✔ script de métricas estáticas (#5); doc de ambiente (#6) |
  | **S02** | ✔ soluções das 6 katas + `relatorio-katas-paulo.md`; organização dos trials | ✔ 4 trials + 4 relatórios de trial | ✔ 6 trials (katas 1–6) + correção do `timing.json` |
  | **S03** | ✔ consolidação/outliers (#44), RQ1 (#45), RQ2 (#46), RQ3 (#47) | ✔ pipeline do dashboard (#48), gráficos (#49) | **✘ nenhum commit em S03** |

  **Ação necessária antes da entrega:** Vitor precisa ser Assignee de uma Issue
  de S03 **com artefato de código commitado**. O enunciado até sugere o papel —
  "o terceiro monta o dashboard" —, e há trabalho de S03 disponível para
  assumir: fechar a ressalva 8 da seção 5 (conferir os logs do jscpd e
  confirmar se os 0% de duplicação são medição ou *fallback*), ou assumir a
  figura de uma das RQs. Distribuição total de commits: Paulo 26, Rafael 23,
  Vitor 14 — este último em **dois nomes de autor** ("Vitor Rebula" e "Vitor
  Rebula Nogueira"), que vale unificar via `.mailmap` para o board e o
  `git log` concordarem.
- ⚠ **Referência à Issue nas mensagens de commit.** Apenas **10 de 36** commits
  sem merge citam `#<número>`; o enunciado diz que commits sem referência **não
  serão considerados**. Não há como reescrever o histórico com segurança agora,
  mas dá para (i) comentar na Issue correspondente com o hash de cada commit
  relevante e (ii) citar `#<número>` daqui para frente.
- ◻ **Link do repositório/board** no Relatório Final e no campo do enunciado.

## 8. Como reproduzir tudo, do zero

```bash
python -m pip install -r scripts/analysis/requirements.txt \
                      -r scripts/dashboard/requirements.txt \
                      -r scripts/metrics/requirements.txt

python scripts/metrics/collect_metrics.py          # results/static_metrics.csv
python scripts/analysis/consolidate_s02.py         # dados/consolidado.csv + outliers.csv
python scripts/analysis/rq1.py                     # dados/rq1_resultados.json
python scripts/analysis/rq2.py
python scripts/analysis/rq3.py
python scripts/analysis/rq4.py                     # RQ extra
python scripts/analysis/rq5.py                     # diferencial
python scripts/dashboard/load_data.py --output results/dashboard_dataset.csv \
                                      --paired-output results/dashboard_paired.csv
python scripts/dashboard/plots.py                  # figuras da issue #49
python scripts/dashboard/plots_advanced.py         # uma figura por RQ
jupyter lab scripts/dashboard/dashboard.ipynb      # Run All
```

Verificação rápida dos trials (a suíte de aceitação usa `teste_*.py`, que o
pytest não coleta por padrão):

```bash
cd trials/<integrante>/<kata>_<tratamento>
PYTHONPATH=src python -m pytest tests -q -o "python_files=test_*.py teste_*.py *_test.py"
```
