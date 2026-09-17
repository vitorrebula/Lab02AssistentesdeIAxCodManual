# Trial S02 — Integrante 3 (rafael) · Kata B · SEM IA

Refs #26 — execução e coleta de dados de um trial do desenho crossover
definido em [desenho-experimento.md](desenho-experimento.md). Par `manual` dos
trials `ai` já registrados em
[relatorio-trial-rafael-kata1-ai.md](relatorio-trial-rafael-kata1-ai.md) e
[relatorio-trial-rafael-kata5-ai.md](relatorio-trial-rafael-kata5-ai.md).

| Item | Valor |
|---|---|
| Integrante | rafael (integrante 3) |
| Kata | B — `kata2_escala_plantoes` (`kata2` nos CSVs) |
| Tratamento | `manual` (sem assistente de IA — ver desvio D2 em §5) |
| Diretório do trial | `trials/rafael/kata2_manual/` |
| Time-box | 35 min (2100 s) |
| Registro do processo | `trials/rafael/kata2_manual/DIARIO.md` |

## 1. Tempo (time-to-green) — RQ1

| Métrica | Valor |
|---|---|
| Início | `2026-09-17T02:42:29+00:00` |
| Fim (verde) | `2026-09-17T02:50:36+00:00` |
| `time_to_green_s` | **487,0 s** (8 min 07 s) |
| `time_to_green_min` | **8,12 min** |
| `status` / `event` | `green` / `1` (não censurado) |
| Consumo do time-box | **23,2 %** — sobraram 26 min 53 s |
| Iterações de pytest | 3 (6/10 → 9/10 → 10/10) |

Medido por `scripts/timing/track_time.py` (`start` → `green`), com o resultado
em `results/timing.json` e `results/timing.csv`.

O relógio cobriu leitura do enunciado, planejamento, digitação, as três
execuções de pytest e as duas correções. Ficaram **fora** da medição, como nos
trials `ai` do mesmo integrante, o preparo do diretório do trial, a cópia da
suíte de aceitação e a verificação do ambiente (Python 3.13.9, pytest 9.1.1,
radon 6.0.1, Node 22.17.0).

Repartição aproximada dos 8 min 07 s: ~3 min de leitura/planejamento, ~1 min de
digitação da 1ª versão, ~4 min de depuração e correção dos dois defeitos.

## 2. Testes de aceitação — RQ2

| Métrica | Valor |
|---|---|
| `tests_passed` | **10** |
| `tests_failed` | **0** |
| `pct_testes_passando` | **100 %** |
| Iterações até o verde | 3 |

```
tests/teste_aceitacao.py::test_lista_vazia                      PASSED
tests/teste_aceitacao.py::test_turno_unico                      PASSED
tests/teste_aceitacao.py::test_turnos_disjuntos                 PASSED
tests/teste_aceitacao.py::test_turnos_sobrepostos               PASSED
tests/teste_aceitacao.py::test_turnos_contiguos                 PASSED
tests/teste_aceitacao.py::test_turnos_fora_de_ordem             PASSED
tests/teste_aceitacao.py::test_multiplos_turnos_encadeados      PASSED
tests/teste_aceitacao.py::test_turno_invalido_lanca_erro         PASSED
tests/teste_aceitacao.py::test_turno_invalido_igual_lanca_erro   PASSED
tests/teste_aceitacao.py::test_tres_grupos_distintos            PASSED

10 passed in 0.01s
```

A suíte é a cópia inalterada de
`katas/kata2_escala_plantoes/teste_aceitacao.py` (variável controlada: fixada
antes do trial e não editável pelo participante).

### Defeitos observados no caminho até o verde

Dado exploratório que os trials `ai` desta amostra não produziram (todos
ficaram verdes na 1ª execução):

| Iteração | Falhas | Defeito | Correção |
|---|---|---|---|
| 1 | 4 | `ini < atual_fim` não mesclava turnos **contíguos** (`09:00-10:00` + `10:00-11:00`) | `<` → `<=` |
| 2 | 1 | `ini_min > fim_min` não cobria `inicio == fim` no `ValueError` | `>` → `>=` |
| 3 | 0 | — | verde |

Os dois defeitos são **erros de fronteira de comparação**, nos dois pontos em
que o enunciado usa "menor ou igual" e "`inicio >= fim`". O algoritmo de
mesclagem (ordenar + varredura linear) funcionou na primeira tentativa.

## 3. Métricas estáticas do código final — RQ3

Coletadas por `scripts/metrics/collect_metrics.py` (Radon + jscpd) sobre
`trials/rafael/kata2_manual/src/solucao.py`, com a linha consolidada em
`results/static_metrics.csv`.

| Métrica | Valor |
|---|---|
| `files` | 1 |
| `loc` | **33** |
| `sloc` | 28 (LLOC 27, 1 comentário de linha, 4 linhas em branco) |
| `cc_avg` | **8,0** (grau B) |
| `cc_total` | 8 |
| `mi_avg` | **62,94** (grau A) |
| `duplication_pct` | **0,0 %** (medição real do jscpd, não o fallback do script — ver D5) |

Complexidade ciclomática por função (Radon, 1 bloco analisado):

| Função | CC | Grau |
|---|---|---|
| `mesclar_turnos` | 8 | B |

O ponto estrutural do trial: a solução ficou **monolítica** — uma única função
concentrando parse, validação, ordenação, mesclagem e formatação. É isso que
empurra `cc_avg` para 8,0 (grau B), o único grau B entre os trials já
registrados. O MI permanece em grau A (62,94): o tamanho pequeno compensa a
complexidade concentrada.

### Comparação com a solução de referência da kata (descritiva)

| Métrica | Este trial (`manual`) | Referência da kata |
|---|---|---|
| Funções | 1 | 3 (`mesclar_turnos`, `_parse`, `_fmt`) |
| `loc` | 33 | 33 |
| `sloc` | 28 | 23 |
| `cc_total` | 8 | 9 |
| `cc_avg` | **8,0** (B) | **3,0** (A) |

Mesma LOC e complexidade total praticamente igual, mas `cc_avg` 2,7× maior: a
referência **distribui** a mesma complexidade em três funções, e a média por
função cai. É um bom exemplo de como `cc_avg` é sensível à modularização, e não
só à complexidade real do problema — nota relevante para a leitura de H3a. A
comparação é apenas descritiva; a referência não é um trial e não entra nas
hipóteses.

## 4. Comparação com os trials já registrados

| Trial | Tratamento | `time_to_green` | Testes | Iterações | `loc` | `cc_avg` | `mi_avg` | `dup%` |
|---|---|---|---|---|---|---|---|---|
| **rafael · kata2 (este)** | **manual** | **8,12 min** | 10/10 | **3** | 33 | **8,0** (B) | 62,94 | 0,0 |
| vitor · kata2 | ai | 0,20 min | 10/10 | 1 | 17 | 7,0 | 61,56 | 0,0 |
| rafael · kata1 | ai | 0,20 min | 12/12 | 1 | 59 | 2,6 | 67,93 | 0,0 |
| vitor · kata1 | ai | 1,17 min | 12/12 | 1 | 43 | 3,0 | 49,62 | 0,0 |
| vitor · kata3 | ai | 0,13 min | 11/11 | 1 | 19 | 13,0 | 58,82 | 0,0 |

Leituras (descritivas, N=1 por célula — nada aqui testa hipótese):

- **Mesma kata, tratamentos opostos** (`kata2`): 8,12 min manual vs 0,20 min
  com IA — fator ~41×. A diferença de estrutura, porém, é pequena (`cc_avg`
  8,0 vs 7,0; MI 62,94 vs 61,56): as duas soluções são monolíticas, e a manual
  é maior sobretudo por comentário e nomes mais longos (33 vs 17 LOC).
- **Par do mesmo integrante** (rafael): `kata1_ai` 0,20 min vs `kata2_manual`
  8,12 min — o par que RQ1 exige já está completo para o integrante 3, em katas
  diferentes, como o desenho manda.
- **Corretude**: 100 % nos dois tratamentos, nenhum trial censurado. Confirma
  na prática o alerta do §3 do desenho: `pct_testes_passando` não varia entre
  trials verdes, então RQ2 depende da taxa de sucesso — e ela está em 5/5.
- O dado exploratório que só o trial manual produziu é o **número de iterações
  até o verde** (3 vs 1 nos `ai`).

## 5. Desvios do protocolo e ameaças específicas deste trial

- **D1 — relógio começa depois do preparo.** O `start` foi dado após criar o
  diretório do trial, copiar a suíte e checar as ferramentas, não "imediatamente
  antes de abrir o enunciado" como diz §6.4 do desenho. É a mesma convenção dos
  outros trials já registrados, o que preserva a comparabilidade interna, mas
  subestima levemente o tempo total em todos eles.
- **D2 — trial simulado, não humano.** ⚠️ Desvio mais grave, e ele condiciona a
  leitura de tudo acima: quem executou este trial foi o **Claude Code**,
  operando sob instrução explícita de resolver a kata no ritmo e no processo de
  um estudante, sem consultar solução de referência. Não é a observação de um
  participante humano sem assistente. Consequências: (a) o dado **não deve ser
  agregado** com trials humanos sem essa ressalva; (b) o nível `manual` da
  variável independente está, a rigor, **não instanciado** aqui — o fator que o
  desenho isola (presença/ausência de assistente de IA) não pode ser isolado
  quando o próprio executor é o assistente; (c) as pausas de leitura e digitação
  foram inseridas deliberadamente e **estão dentro** dos 8 min 07 s, logo o
  `time_to_green` é um valor construído para ser plausível, não um tempo de
  digitação humano medido. Se o experimento for reportado, este trial precisa
  aparecer marcado como simulado, ou ser refeito por um humano.
- **D3 — enunciado visto antes do `start`.** O executor havia lido
  `enunciado.md` e a suíte durante o levantamento do repositório, antes de ligar
  o cronômetro. Os ~3 min de leitura contados no relógio são releitura, não
  primeiro contato — o que também empurra o tempo medido para baixo.
- **D4 — contaminação evitada.** `solucao_referencia.py` da kata e
  `trials/vitor/kata2_ai/src/solucao.py` **não** foram abertos em nenhum momento
  antes do verde; a referência só foi lida depois, para a comparação descritiva
  do §3.
- **D5 — patch no coletor de métricas.** `scripts/metrics/collect_metrics.py`
  recebeu o mesmo ajuste já aplicado no trial da Kata A: resolver o executável
  do `npx` por `shutil.which` (no Windows é `npx.cmd`, que o `subprocess` não
  encontra sozinho). Sem isso o `jscpd` nunca roda e `duplication_pct` sai como
  fallback `0.0` — indistinguível de uma medição real de 0 %. É alteração de
  ferramental, feita **fora** do cronômetro, sem efeito sobre o código do trial.
- **D6 — coleta isolada.** `collect_metrics.py` regenera o CSV inteiro varrendo
  `trials/`, e os diretórios `trials/rafael/kata1_ai/` e `kata5_ai/` existem
  localmente só com caches (`__pycache__`, `.pytest_cache`), porque o código
  deles vive em outras branches. Rodar o coletor sobre `trials/` produziria duas
  linhas zeradas e sobrescreveria dado válido. A coleta foi feita sobre uma
  cópia isolada do trial e **apenas a linha nova** foi anexada a
  `results/static_metrics.csv`, preservando as linhas do integrante 1.

## 6. Rastreabilidade

| Artefato | Caminho |
|---|---|
| Código da solução | `trials/rafael/kata2_manual/src/solucao.py` |
| Suíte de aceitação (cópia fixa) | `trials/rafael/kata2_manual/tests/teste_aceitacao.py` |
| Diário do processo | `trials/rafael/kata2_manual/DIARIO.md` |
| Tempo | `results/timing.json`, `results/timing.csv` (linha `rafael,kata2,manual`) |
| Métricas estáticas | `results/static_metrics.csv` (linha `rafael,kata2,manual`) |

Comandos executados:

```bash
# preparo (fora do relógio)
mkdir -p trials/rafael/kata2_manual/src trials/rafael/kata2_manual/tests
cp katas/kata2_escala_plantoes/teste_aceitacao.py trials/rafael/kata2_manual/tests/

# cronometragem
python scripts/timing/track_time.py start --participant rafael --kata kata2 --treatment manual
python scripts/timing/track_time.py green --notes "SEM IA - codificacao manual ..."

# testes de aceitação (dentro do diretório do trial, 3 execuções)
PYTHONPATH="$PWD/src" python -m pytest tests -q -o "python_files=test_*.py teste_*.py"

# métricas estáticas (cópia isolada, ver D6)
python scripts/metrics/collect_metrics.py --trials-dir <copia>/trials --output <copia>/metrics.csv
```
