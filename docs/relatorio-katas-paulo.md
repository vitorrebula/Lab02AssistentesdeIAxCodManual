# Relatório dos trials de Paulo — Katas A, B, D e E

## Código e condições

| Kata | Trial | Condição | Código final |
|---|---|---|---|
| A | `trials/paulo/kata1_manual` | Sem IA | `src/solucao.py` |
| B | `trials/paulo/kata2_manual` | Sem IA | `src/solucao.py` |
| D | `trials/paulo/kata4_ai` | Com IA | `src/solucao.py` |
| E | `trials/paulo/kata5_ai` | Com IA | `src/solucao.py` |

Os arquivos em `trials/paulo/` são cópias das soluções entregues em `katas/`, organizadas na convenção do experimento. Os testes de aceitação também foram copiados para `tests/`. A distribuição encontrada é duas katas manuais (A e B) e duas com IA (D e E).

## Métricas estáticas

Coleta executada com `python scripts/metrics/collect_metrics.py` sobre os códigos em `trials/paulo/`. Radon 6.0.1 mede LOC, SLOC, complexidade ciclomática média e índice de manutenibilidade; jscpd 5.3.2 mede duplicação. Fonte: `results/static_metrics.csv`.

| Kata | Condição | LOC | SLOC | CC média | CC total | MI | Duplicação |
|---|---|---:|---:|---:|---:|---:|---:|
| A | Sem IA | 37 | 33 | 3.6 | 18 | 47.31 | 0.0% |
| B | Sem IA | 34 | 25 | 7.0 | 7 | 73.19 | 0.0% |
| D | Com IA | 64 | 17 | 2.5 | 5 | 71.07 | 0.0% |
| E | Com IA | 74 | 22 | 2.5 | 10 | 72.48 | 0.0% |

Os valores anteriores de CK, dificuldade de Halstead, complexidade cognitiva e supostas violações PMD/Pylint não foram produzidos pela coleta definida no protocolo e foram removidos. A duplicação de 0% significa que o jscpd não identificou clones com os parâmetros do coletor; não demonstra ausência de toda repetição.

## Tempo e validade

O registro anterior informava A = 3m45s, B = 19m20s, D = 5m10s e E = 24m15s, porém esses tempos foram digitados manualmente, sem cronometragem verificável por `track_time.py`. **Não são observações de `time_to_green`** e não foram acrescentados a `results/timing.csv` ou `results/timing.json`. A correspondência entre os rótulos de condição do registro antigo e os arquivos finais também divergia para A e E. Não calcular economia de tempo ou efeito causal a partir desses valores. Os testes de aceitação foram executados separadamente sobre cada trial: A 12/12, B 10/10, D 10/10 e E 12/12 aprovados. Essa verificação atual não comprova quando o verde foi atingido durante a execução original.

Para o relatório final, tratar os tempos de Paulo como dados ausentes da análise quantitativa de RQ1, documentando a falta de cronometragem. O tempo de Rafael em `kata2_manual` foi perdido e reconstituído de memória após a perda do registro original; sinalizar essa proveniência e fazer uma análise de sensibilidade que exclua essa linha de RQ1. Nenhum desses valores pode ser apresentado como medição contemporânea verificável.
