# Trial S02 — Integrante 3 (rafael) · Kata A · COM IA

Refs #23 — execução e coleta de dados de um trial do desenho crossover
definido em [desenho-experimento.md](desenho-experimento.md).

| Item | Valor |
|---|---|
| Integrante | rafael (integrante 3) |
| Kata | A — `kata1_cesta_compras` (`kata1` nos CSVs) |
| Tratamento | `ai` (Claude Code, Opus 5 — ver desvio em §5) |
| Diretório do trial | `trials/rafael/kata1_ai/` |
| Time-box | 35 min (2100 s) |

## 1. Tempo (time-to-green) — RQ1

| Métrica | Valor |
|---|---|
| Início | `2026-09-17T02:10:55+00:00` |
| Fim (verde) | `2026-09-17T02:11:09+00:00` |
| `time_to_green_s` | **12,0 s** (0 min 12 s) |
| `time_to_green_min` | **0,20 min** |
| `status` / `event` | `green` / `1` (não censurado) |
| Nº de prompts | 1 (ver `trials/rafael/kata1_ai/PROMPTS.md`) |

Medido por `scripts/timing/track_time.py` (start → green), com o resultado
gravado em `results/timing.json` e `results/timing.csv`. Consumiu **0,6 %** do
time-box de 35 min; sobraram 34 min 48 s.

O que o cronômetro cobre está declarado em `PROMPTS.md`: a varredura do
repositório, a leitura do protocolo e o preparo dos diretórios ficaram fora da
medição, e o relógio cobriu a escrita da solução até o verde — mesma
convenção dos trials `ai` do integrante 1, o que preserva a comparabilidade
entre os trials `ai`.

## 2. Testes de aceitação — RQ2

| Métrica | Valor |
|---|---|
| `tests_passed` | **12** |
| `tests_failed` | **0** |
| `pct_testes_passando` | **100 %** |
| Iterações até o verde | 1 (verde na primeira execução do pytest) |

```
tests/teste_aceitacao.py::test_carrinho_vazio                    PASSED
tests/teste_aceitacao.py::test_adicionar_item_simples            PASSED
tests/teste_aceitacao.py::test_adicionar_item_duplicado_soma_qtd PASSED
tests/teste_aceitacao.py::test_adicionar_item_preco_invalido     PASSED
tests/teste_aceitacao.py::test_adicionar_item_qtd_invalida       PASSED
tests/teste_aceitacao.py::test_cupom_promo10_nao_atinge_minimo   PASSED
tests/teste_aceitacao.py::test_cupom_promo10_atinge_minimo       PASSED
tests/teste_aceitacao.py::test_cupom_promo20_atinge_minimo       PASSED
tests/teste_aceitacao.py::test_cupom_none                        PASSED
tests/teste_aceitacao.py::test_cupom_invalido                    PASSED
tests/teste_aceitacao.py::test_checkout_sem_cupom                PASSED
tests/teste_aceitacao.py::test_checkout_com_cupom_efetivo        PASSED

12 passed in 0.02s
```

A suíte é a cópia inalterada de `katas/kata1_cesta_compras/teste_aceitacao.py`
(variável controlada: suíte fixada antes do trial e não editável pelo
participante).

## 3. Métricas estáticas do código final — RQ3

Coletadas por `scripts/metrics/collect_metrics.py` (Radon + jscpd) sobre
`trials/rafael/kata1_ai/src/solucao.py`, com o resultado em
`results/static_metrics.csv`.

| Métrica | Valor |
|---|---|
| `files` | 1 |
| `loc` | **59** |
| `sloc` | 35 (LLOC 38, 5 comentários de linha, 4 docstrings, 15 linhas em branco) |
| `cc_avg` | **2,6** (grau A) |
| `cc_total` | 13 |
| `mi_avg` | **67,93** (grau A) |
| `duplication_pct` | **0,0 %** (0 clones em 59 linhas, jscpd 5.2.1) |

Complexidade ciclomática por função (Radon, 5 blocos analisados):

| Função | CC | Grau |
|---|---|---|
| `adicionar_item` | 5 | A |
| `aplicar_cupom` | 4 | A |
| `total_sem_desconto` | 2 | A |
| `criar_carrinho` | 1 | A |
| `checkout` | 1 | A |

Todas as funções caem no grau A de complexidade e o MI fica em grau A. As duas
funções de maior CC são exatamente as que concentram as regras do enunciado
(validação + deduplicação de item; dois cupons com piso de valor), e o
`duplication_pct` de 0 % é medição real do jscpd, não o fallback do script
(ver §5).

### Comparação com a solução de referência da kata

`docs/katas_justificativa.md` §3 mede a solução de referência da Kata A em
5 funções, LOC 41, SLOC 33, CC total 15, CC média 3,0 e MI 49,6. O código
deste trial tem o mesmo número de funções e SLOC praticamente igual (35 vs
33), CC total um pouco menor (13 vs 15) e MI mais alto (67,9 vs 49,6) — a
diferença de MI vem sobretudo das docstrings e da tabela `CUPONS`, que
substitui ramificação por dado. O LOC maior (59 vs 41) é efeito das docstrings
e linhas em branco, não de código extra: em SLOC as duas soluções são
equivalentes. A comparação é apenas descritiva — a referência não é um trial
do experimento e não entra em nenhuma das hipóteses.

## 4. Comparação com os demais trials `ai` já registrados

| Trial | `time_to_green` | Testes | `loc` | `cc_avg` | `mi_avg` | `dup%` |
|---|---|---|---|---|---|---|
| rafael · kata1 · ai (este) | 0,20 min | 12/12 | 59 | 2,6 | 67,93 | 0,0 |
| vitor · kata1 · ai | 1,17 min | 12/12 | 43 | 3,0 | 49,62 | 0,0 |
| vitor · kata2 · ai | 0,20 min | 10/10 | 17 | 7,0 | 61,56 | 0,0 |
| vitor · kata3 · ai | 0,13 min | 11/11 | 19 | 13,0 | 58,82 | 0,0 |

Os dois trials da **mesma kata** (A) sob o mesmo tratamento saíram com
corretude idêntica (12/12) e estrutura próxima (CC média 2,6 vs 3,0); este
trial ficou com MI mais alto e LOC maior, o que é coerente com o volume de
docstrings. Comparar tempos entre integrantes aqui não é informativo: o par
válido do desenho é `ai` vs `manual` **do mesmo integrante** (§5 do desenho),
e o trial `manual` do integrante 3 ainda não foi executado.

Nenhuma conclusão sobre as hipóteses é possível com este trial isolado: RQ1 e
RQ3 exigem o par completo por integrante, e RQ2 é degenerada em trial verde
(`pct_testes_passando` = 100 % por construção — ver §3 do desenho).

## 5. Desvios e ameaças à validade deste trial

- **Desvio de variável controlada (modelo).**
  `docs/ambiente-experimento.md` §3 fixa **Sonnet** como agente de todos os
  trials `ai`; este trial rodou em **Opus 5 (1M context)**, modelo já
  configurado na sessão. Registrado para ser discutido na análise ou corrigido
  com re-execução em Sonnet. Mesmo desvio do trial `rafael/kata5_ai` (#25).
- **Sem contaminação por solução pronta.** O gabarito
  (`katas/kata1_cesta_compras/solucao_referencia.py`), a solução manual de
  outro integrante (`solucao-sem-ia-paulo.py`) e a solução do integrante 1
  para a mesma kata (`trials/vitor/kata1_ai/src/solucao.py`) **não** foram
  abertos em nenhum momento do trial. A comparação com a referência em §3 usa
  apenas os números já publicados em `docs/katas_justificativa.md`, obtidos
  depois do verde.
- **Time-to-green muito abaixo do time-box.** 12 s contra 2100 s disponíveis.
  Com trials `ai` nessa ordem de grandeza, a variância do tempo passa a ser
  dominada por latência de ferramenta e não por esforço de resolução, o que
  limita o que RQ1 consegue enxergar no braço `ai` — vale registrar no
  relatório final junto da censura do braço `manual`.
- **Correção de instrumentação durante a coleta (depois do verde).**
  `collect_metrics.py` invocava `npx` por `subprocess` sem resolver o
  executável; no Windows isso sempre falhava com `FileNotFoundError` (o
  executável é `npx.cmd`) e o script caía no fallback silencioso
  `duplication_pct = 0.0`. A chamada passou a resolver o executável via
  `shutil.which`, então o jscpd roda de fato. Consequência para os dados: os
  `duplication_pct` coletados **antes** desta correção (linhas do integrante 1)
  eram fallback, não medição, e devem ser recoletados. O valor deste trial
  (0,0 %) é medição confirmada — execução manual do jscpd 5.2.1 reportou
  0 clones em 59 linhas.
- **Linha artefatual removida do CSV.** A varredura do `collect_metrics.py`
  encontrou um diretório residual `trials/rafael/kata5_ai/` (apenas
  `__pycache__` e `.approval_tests_temp` nesta branch; o trial real está
  commitado na branch da issue #25) e emitiu uma linha `rafael,kata5,ai` com
  `files=0` e zeros em todas as métricas. Essa linha foi excluída de
  `results/static_metrics.csv` por ser artefato de varredura, não um trial. O
  dado real do Kata E entra pelo PR da issue #25.

## 6. Como reproduzir

```bash
python scripts/timing/track_time.py start --participant rafael --kata kata1 --treatment ai
# implementar trials/rafael/kata1_ai/src/solucao.py
python scripts/timing/track_time.py green
python scripts/metrics/collect_metrics.py
```

## 7. Artefatos gerados

| Arquivo | Conteúdo |
|---|---|
| `trials/rafael/kata1_ai/src/solucao.py` | código final do trial |
| `trials/rafael/kata1_ai/tests/teste_aceitacao.py` | suíte de aceitação da kata (cópia inalterada) |
| `trials/rafael/kata1_ai/PROMPTS.md` | prompts, modelo e notas de execução |
| `results/timing.json` · `results/timing.csv` | tempo e testes do trial |
| `results/static_metrics.csv` | métricas estáticas do código final |
| `scripts/metrics/collect_metrics.py` | correção da resolução do `npx` (§5) |
| `docs/relatorio-trial-rafael-kata1-ai.md` | este relatório |
