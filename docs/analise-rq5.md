# RQ5 — O efeito da IA é o mesmo em toda kata? (diferencial do grupo)

**Questão (RQ própria do grupo):** o efeito do assistente de IA sobre o tempo é
homogêneo entre as katas, ou depende da tarefa? Em caso afirmativo, o ganho
cresce com a dificuldade intrínseca da kata?

**Por que essa pergunta.** RQ1–RQ4 tratam "IA" como um efeito único e médio. Um
resultado médio, porém, pode esconder o que mais interessa na prática: *para
que tipo de tarefa* o assistente ajuda. A literatura de experimentos com
assistentes de código relata ganhos muito desiguais por tipo de tarefa, e o
nosso desenho — 6 katas de domínios deliberadamente distintos
([katas_justificativa.md](katas_justificativa.md)) — permite olhar isso sem
coletar nada novo. RQ5 é, portanto, uma **reanálise dos mesmos dados sob outra
unidade de agregação**: a kata, não o integrante.

**Hipóteses.** H5₀: o *speedup* é o mesmo em todas as katas e não se associa à
dificuldade. H5₁: o *speedup* varia entre katas e/ou cresce com a dificuldade
(bicaudal, α = 0,05). Declaradamente **exploratória** — ver a limitação de
pareamento abaixo.

## Métricas

Para cada kata resolvida nos **dois** tratamentos:

| Métrica | Definição operacional | Unidade |
|---|---|---|
| `speedup` | `mediana(tempo sem IA) ÷ mediana(tempo com IA)` | vezes (×) |
| `ganho_min` | `mediana(tempo sem IA) − mediana(tempo com IA)` | minutos |
| `dificuldade_proxy_min` | `mediana(tempo sem IA)` da kata — quanto mais demorada na mão, mais difícil para este grupo | minutos |
| `razao_loc_ia_sobre_manual` | `LOC mediana com IA ÷ LOC mediana sem IA` | adimensional |

O *speedup* (razão) e o ganho (diferença) respondem a coisas diferentes: 41× em
uma kata de 8 min economiza 8 minutos; 1,4× em uma kata de 15 min economiza 4,5.
Os dois entram na tabela por isso.

## Limitação que define o método

**Não há pares "mesma pessoa, mesma kata".** Pelo desenho (§5), ninguém resolveu
a mesma kata duas vezes — justamente para evitar *carryover* de já conhecer a
solução. A consequência é que, ao agregar **por kata**, o contraste é **entre
pessoas**: o tempo "com IA" da kata 2 é do Vitor e o "sem IA" é do Rafael.
Habilidade individual e tratamento não são separáveis nesse corte.

Isso não invalida a pergunta — invalida a leitura causal. RQ5 mede **quanta
dispersão existe** no efeito e de onde ela vem, não "o efeito causal da IA na
kata 2".

## Resultados — 4 katas do plano (12 trials)

| Kata | Domínio | Testes | Sem IA (mediana) | Com IA (mediana) | Speedup | Ganho | LOC IA ÷ manual |
|---|---|---:|---:|---:|---:|---:|---:|
| 2 | Escala de Plantões | 10 | 8,20 min | 0,20 min | **41,00×** | +8,00 min | 0,52 |
| 5 | Controle de Estoque | 12 | 10,72 min | 0,39 min | **27,36×** | +10,32 min | 1,32 |
| 4 | Extrator de Tags | 10 | 15,42 min | 10,87 min | **1,42×** | +4,55 min | 1,19 |
| 1 | Cesta de Compras | 12 | 0,40 min | 0,68 min | **0,59×** | −0,28 min | 1,28 |

Katas fora do contraste: **kata 3** (Validador de Senha) só tem trial com IA e
**kata 6** (Máquina de Catraca) só tem trial manual — sem o outro lado, não há
razão a calcular. Ambas seguem no consolidado marcadas como
`no_plano_4_katas=false`.

**Heterogeneidade:** speedup mediano **14,39×**, variando de **0,59× a 41,00×** —
uma razão de **70×** entre os extremos. Em uma das quatro katas (Cesta de
Compras) a condição "com IA" foi **mais lenta** que a manual.

**Associação com a dificuldade:** ρ de Spearman(dificuldade, speedup) = **+0,20**
(`p = 0,80`, n = 4). **Não rejeitamos H5₀** na parte da associação: não há
evidência de que katas mais difíceis se beneficiem mais. Com quatro pontos, o
menor `p` bicaudal possível no Spearman exato é 0,083 — o teste **não poderia**
dar significativo nem com ordenação perfeita. O número está no relatório como
transparência, não como evidência.

## A heterogeneidade é real ou é artefato de proveniência?

Aqui está o achado que justifica a RQ. Refazendo a mesma conta **somente com
trials cronometrados** (excluindo os 4 tempos derivados de Paulo):

| Kata | Sem IA | Com IA | Speedup |
|---|---:|---:|---:|
| 2 — Escala de Plantões | 8,12 min (Rafael) | 0,20 min (Vitor) | 40,58× |
| 5 — Controle de Estoque | 10,72 min (Vitor) | 0,28 min (Rafael) | 37,83× |

Sobram duas katas, e a dispersão **desaparece**: 37,8× e 40,6×, razão de
**1,07×** entre extremos, contra 70× na análise primária. As duas katas com
speedup baixo na tabela anterior são exatamente aquelas em que **um dos lados é
tempo derivado**:

- **kata 1** — o lado "sem IA" é o trial de Paulo, com 0,40 min (24 s) de tempo
  derivado. Nenhuma pessoa escreve uma solução de 12 testes na mão em 24
  segundos; esse número é o que faz a kata 1 aparecer como "IA mais lenta".
- **kata 4** — o lado "com IA" é o trial de Paulo, 10,87 min, também derivado
  (e com ChatGPT, não com o assistente fixado no protocolo).

**Conclusão metodológica:** a heterogeneidade aparente entre katas, nesta
amostra, é explicada pela **proveniência dos dados**, não pelo tipo de tarefa.
RQ5 não encontrou variação de efeito por kata; encontrou o rastro de um
problema de coleta — e o localizou com precisão, trial por trial. Foi a análise
por kata, e só ela, que tornou esse rastro visível: nas RQ1–RQ3, agregadas por
integrante, os quatro trials derivados se diluem na mediana de Paulo.

## Resposta à RQ5

Com os dados confiáveis disponíveis (2 katas), **não há evidência de efeito
heterogêneo por kata**: o ganho de tempo foi praticamente o mesmo (≈38–41×) nas
duas katas com contraste cronometrado, e não se associou à dificuldade
(ρ = +0,20; p = 0,80; n = 4 na análise primária). A dispersão de 70× observada
na análise primária é **artefato dos tempos derivados**, não sinal.

Como diferencial, RQ5 entregou três coisas que as RQs do enunciado não
entregam: (i) uma medida de efeito **por tarefa** (speedup e ganho em minutos,
mais interpretáveis que "mediana por tratamento"); (ii) um **teste de robustez
cruzado** que localizou o dado frágil; (iii) a constatação de que, para
responder a RQ5 de verdade, faltam trials — cada kata precisaria dos dois
tratamentos, cronometrados, de pessoas diferentes em ordem contrabalanceada.
Essa é a recomendação de coleta que levamos para a conclusão.

## Reprodução

```bash
python -m pip install -r scripts/analysis/requirements.txt
python scripts/analysis/rq5.py              # -> dados/rq5_resultados.json
python scripts/dashboard/plots_advanced.py  # -> results/figures/rq5_bolhas_speedup.png
```

O script lê `dados/consolidado.csv`, não altera dado bruto e grava, por kata,
os tempos medianos, speedup, ganho, razão de LOC, quais integrantes entraram em
cada lado e a marca `usa_tempo_derivado`, além dos dois blocos de
heterogeneidade (primário e sensibilidade). A figura de bolhas lê esse JSON.
