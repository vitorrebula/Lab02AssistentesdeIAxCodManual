# RQ3 — Estrutura do código com e sem assistente de IA

**Questão:** o uso de assistente de IA altera a complexidade ciclomática ou a duplicação do código produzido? A análise também compara o tamanho (LOC), conforme o plano em `docs/desenho-experimento.md`.

## Dados e método

Fonte: `results/static_metrics.csv` da S02, com **14 trials**, sete com IA e sete manuais, de **três participantes**. A linguagem fixada na S01 é Python: o coletor usa Radon para `cc_avg`, `cc_total`, `loc` e `mi_avg`, e jscpd para `duplication_pct`. CK e PMD CPD para Java não se aplicam a este código. Cada trial contém um arquivo de solução; testes não entram nas métricas.

Para controlar o tamanho do código, além da CC média por função, calculamos **densidade de complexidade = `100 × cc_total / loc`**, expressa em pontos de CC por 100 LOC. A CC média por função não deve ser simplesmente dividida outra vez por LOC: seu denominador já é o número de funções; a densidade usa a soma das complexidades. A duplicação já é medida como **percentual de linhas** pelo jscpd, isto é, já está normalizada pelo tamanho analisado. Dividir esse percentual novamente por LOC não teria interpretação útil. LOC é apresentada separadamente como controle. `mi_avg` é uma análise opcional, não uma quarta hipótese primária.

Os quartis abaixo são os percentis 25 e 75 dos **trials** (interpolação linear do NumPy); `IQR = Q3 − Q1`. Para Wilcoxon, a unidade de análise é o **participante**: calculamos a mediana dos trials de cada participante em cada tratamento e então comparamos os três pares. O teste é bicaudal, exato, com α = 0,05. O tamanho de efeito `r_rb` é a correlação bisserial dos postos das diferenças IA − manual (de −1 a +1). As três hipóteses primárias planejadas são CC média, duplicação e LOC; Holm ajusta os testes primários que têm diferenças não nulas. A densidade e o MI são análises secundárias.

## Resultados descritivos

| Métrica | Manual: mediana [Q1; Q3], IQR | IA: mediana [Q1; Q3], IQR | Wilcoxon pareado (n = 3); `r_rb` |
|---|---:|---:|---:|
| CC média por função | 3,60 [2,62; 6,50], 3,88 | 2,60 [2,50; 5,00], 2,50 | W = 3; p = 1,000; `r_rb = 0,000` |
| CC total / 100 LOC | 23,53 [21,01; 25,63], 4,63 | 34,88 [17,77; 42,33], 24,55 | W = 3; p = 1,000; `r_rb = 0,000` (secundário) |
| Linhas duplicadas (%) | 0,00 [0,00; 0,00], 0,00 | 0,00 [0,00; 0,00], 0,00 | Não aplicável: todos os pares empatados |
| LOC | 34,00 [30,50; 37,00], 6,50 | 43,00 [21,00; 61,50], 40,50 | W = 2; p = 0,750; `r_rb = +0,333` |
| MI (opcional) | 73,19 [65,72; 77,70], 11,98 | 61,56 [59,03; 69,50], 10,47 | W = 1; p = 0,500; `r_rb = −0,667` (exploratório) |

Após Holm para as duas hipóteses primárias testáveis, **p ajustado = 1,000** tanto para CC média quanto para LOC. Não atribuímos p-valor à duplicação: os 14 valores são zero e o Wilcoxon não possui diferenças não nulas a ordenar.

As medianas individuais abaixo mostram por que não basta comparar as 14 linhas como se fossem independentes. Cada célula é **manual → IA**; a densidade é CC total por 100 LOC.

| Participante | CC média | Densidade de CC | LOC |
|---|---:|---:|---:|
| Paulo | 5,30 → 2,50 | 34,62 → 10,66 | 35,50 → 69,00 |
| Rafael | 5,00 → 2,55 | 23,89 → 32,76 | 25,00 → 41,00 |
| Vitor | 2,75 → 7,00 | 21,43 → 41,18 | 37,00 → 19,00 |

## Resposta à RQ3

**Não foi detectada diferença estatística** na CC média nem em LOC entre tratamentos neste conjunto. A mediana bruta de CC média é menor com IA, mas a densidade por LOC é maior e apresenta dispersão muito maior; as direções individuais também divergem. Portanto, a conclusão de que IA reduz a complexidade não é sustentada quando controlamos o tamanho. O jscpd registrou 0% de duplicação nos dois tratamentos; esse resultado não permite distinguir tratamentos nem comprova ausência de repetições menores que os limiares da ferramenta.

A inferência é **exploratória**: há apenas três pares, e até uma direção uniforme nos três participantes teria p bicaudal mínimo de 0,25 no Wilcoxon exato. Katas diferentes são resolvidas em condições diferentes, inclusive as katas 3 e 6 aparecem somente em um tratamento no CSV; diferenças de dificuldade podem se confundir com o efeito da IA. Há ainda divergência entre o assistente fixado na S01 (`Claude Code`) e o registro de Paulo com `ChatGPT` nos arquivos de timing; o tratamento “IA” não representa necessariamente uma única ferramenta. A porcentagem de duplicação pode sair como **0,0 por fallback** se o jscpd falhar no coletor: para interpretar os zeros como medições, conferir os logs da execução e a disponibilidade da ferramenta. Não inferimos RQ3 a partir dos tempos declarados em `results/timing.csv`.

## Reprodução

Na raiz do repositório:

```bash
python -m pip install -r scripts/analysis/requirements.txt
python scripts/analysis/rq3.py
```

O script lê o CSV existente sem alterá-lo, valida duplicidade de trials e imprime quartis, pares, testes exatos e ajuste de Holm. Para recolher métricas de código após alterações nas soluções, executar antes `python scripts/metrics/collect_metrics.py`; verificar os avisos do jscpd e comparar o novo CSV ao versionado.
