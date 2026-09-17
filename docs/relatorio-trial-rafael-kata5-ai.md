# Trial S02 — Integrante 3 (rafael) · Kata E · COM IA

Refs #25 — execução do trial da **Kata E** (`kata5_controle_estoque`) sob o
tratamento `ai`, com time-box de 35 min, seguindo o procedimento de
`docs/desenho-experimento.md` §6.

| Item | Valor |
|---|---|
| Integrante | rafael (integrante 3) |
| Kata | E — `kata5_controle_estoque` (`kata5` nos CSVs) |
| Tratamento | `ai` (Claude Code, Opus 5 — ver desvio em §5) |
| Diretório do trial | `trials/rafael/kata5_ai/` |
| Time-box | 35 min (2100 s) |

## 1. Tempo (time-to-green) — RQ1

| Métrica | Valor |
|---|---|
| Início | `2026-09-17T01:47:07+00:00` |
| Fim (verde) | `2026-09-17T01:47:27+00:00` |
| `time_to_green_s` | **17,0 s** (0 min 17 s) |
| `time_to_green_min` | **0,28 min** |
| `status` / `event` | `green` / `1` (não censurado) |
| Nº de prompts | 1 (ver `trials/rafael/kata5_ai/PROMPTS.md`) |

Registrado por `scripts/timing/track_time.py` em `results/timing.json` e
`results/timing.csv` (linha `rafael,kata5,ai`). O tempo cobre da leitura do
enunciado até o verde; o preparo do ambiente (instalação do Radon, criação dos
diretórios e cópia dos testes) ficou fora do cronômetro.

## 2. Testes de aceitação — RQ2

| Métrica | Valor |
|---|---|
| `tests_passed` | **12** |
| `tests_failed` | **0** |
| `pct_testes_passando` | **100 %** |
| Iterações até o verde | 1 (verde na primeira execução do pytest) |

Suíte usada: `trials/rafael/kata5_ai/tests/teste_aceitacao.py`, cópia
byte-a-byte de `katas/kata5_controle_estoque/teste_aceitacao.py` (verificado
com `diff`; não editada pelo participante, conforme §4.3 do desenho).

```
12 passed in 0.02s
```

Os 12 casos cobrem: estoque vazio; entrada em SKU novo e soma em SKU
existente; entrada com `qtd <= 0`; saída normal; saída em SKU inexistente
(`KeyError`); saída com estoque insuficiente sem alterar o estoque; saída com
`qtd` inválida; alerta abaixo do mínimo; alerta de SKU ausente do estoque;
SKU sem limite ignorado; ordenação alfabética dos alertas.

## 3. Métricas estáticas do código final — RQ3

Código analisado: `trials/rafael/kata5_ai/src/solucao.py` (1 arquivo).
Coleta por `scripts/metrics/collect_metrics.py` (Radon + jscpd) →
`results/static_metrics.csv`.

| Métrica | Valor |
|---|---|
| `files` | 1 |
| `loc` | **23** |
| `sloc` | 17 (LLOC 16, 0 comentários, 6 linhas em branco) |
| `cc_avg` | **2,5** (grau A) |
| `cc_total` | 10 |
| `mi_avg` | **59,25** (grau A) |
| `duplication_pct` | **0,0 %** (0 clones em 23 linhas) |

Complexidade ciclomática por função (Radon `cc -s`):

| Função | CC | Grau |
|---|---|---|
| `registrar_saida` | 4 | A |
| `verificar_alertas` | 3 | A |
| `registrar_entrada` | 2 | A |
| `criar_estoque` | 1 | A |

## 4. Comparação com os demais trials `ai` já registrados

| Trial | `time_to_green` | Testes | `loc` | `cc_avg` | `mi_avg` | `dup%` |
|---|---|---|---|---|---|---|
| rafael · kata5 · ai | 0,28 min | 12/12 | 23 | 2,5 | 59,25 | 0,0 |
| vitor · kata1 · ai | 1,17 min | 12/12 | 43 | 3,0 | 49,62 | 0,0 |
| vitor · kata2 · ai | 0,20 min | 10/10 | 17 | 7,0 | 61,56 | 0,0 |
| vitor · kata3 · ai | 0,13 min | 11/11 | 19 | 13,0 | 58,82 | 0,0 |

Comparação apenas descritiva: os testes pareados de §7 do desenho exigem o
par `ai` × `manual` do mesmo integrante, e o trial `manual` do integrante 3
ainda não foi executado.

## 5. Desvios e ameaças à validade deste trial

1. **Modelo fora da variável controlada.** `docs/ambiente-experimento.md` §3
   fixa **Sonnet** como agente de todos os trials `ai`; este trial rodou em
   **Opus 5 (1M context)**, já configurado na sessão. Efeito esperado: viés
   *a favor* do tratamento `ai` (modelo mais capaz). Opções: registrar o
   desvio na análise ou re-executar o trial em Sonnet.
2. **Leitura prévia da solução de referência.** Antes do início do cronômetro,
   na varredura do repositório, o assistente leu
   `katas/kata5_controle_estoque/solucao_referencia.py` e a solução do
   integrante 2 para a mesma kata. A implementação foi escrita a partir do
   enunciado, mas a influência não pode ser descartada — viés também *a favor*
   do tratamento `ai`. Mitigação para trials futuros: manter as soluções de
   referência fora do diretório visível ao assistente durante o trial.
3. **Tempo de execução muito abaixo do time-box.** 17 s contra 2100 s de
   time-box: o piso de medição (latência de escrita do arquivo + execução do
   pytest) passa a dominar o tempo medido, o que comprime a variância dos
   trials `ai` e reduz o poder do teste de RQ1 — já previsto como limitação de
   katas pequenas em §8 (validade externa).
4. **`duplication_pct` não medido pelo script neste ambiente.** No Windows,
   `collect_metrics.py` chama `npx` sem extensão e a chamada falha com
   `FileNotFoundError`, caindo no fallback `duplicação = 0.0` (aviso
   "npx/jscpd nao encontrado" impresso para os 4 trials). O valor **0,0 %
   deste trial foi confirmado à parte**, rodando `npx.cmd jscpd` manualmente
   (0 clones exatos, 0,00 % de linhas duplicadas em 23 linhas). As linhas de
   `vitor` no CSV foram regeradas pela mesma coleta e carregam o fallback, não
   uma medição.

## 6. Como reproduzir

```bash
pip install -r scripts/metrics/requirements.txt
python scripts/timing/track_time.py start --participant rafael --kata kata5 --treatment ai
# implementar trials/rafael/kata5_ai/src/solucao.py
python scripts/timing/track_time.py green
python scripts/metrics/collect_metrics.py
```

## 7. Artefatos gerados

| Arquivo | Conteúdo |
|---|---|
| `trials/rafael/kata5_ai/src/solucao.py` | código final do trial |
| `trials/rafael/kata5_ai/tests/teste_aceitacao.py` | suíte de aceitação da kata (cópia inalterada) |
| `trials/rafael/kata5_ai/PROMPTS.md` | prompts, modelo e notas de execução |
| `results/timing.json` · `results/timing.csv` | tempo e testes do trial |
| `results/static_metrics.csv` | métricas estáticas do código final |
| `docs/relatorio-trial-rafael-kata5-ai.md` | este relatório |
