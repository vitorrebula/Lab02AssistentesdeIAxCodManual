# Trial S02 — Integrante 3 (rafael) · Kata D · SEM IA

Execução e coleta de dados de um trial do desenho crossover definido em
[desenho-experimento.md](desenho-experimento.md). Segue o mesmo protocolo do
trial [relatorio-trial-rafael-kata2-manual.md](relatorio-trial-rafael-kata2-manual.md)
(Kata B, `manual`).

| Item | Valor |
|---|---|
| Integrante | rafael (integrante 3) |
| Kata | D — `kata4_extrator_tags` (`kata4` nos CSVs) |
| Tratamento | `manual` (sem assistente de IA — ver desvio D2 em §5) |
| Diretório do trial | `trials/rafael/kata4_manual/` |
| Time-box | 35 min (2100 s) |
| Registro do processo | `trials/rafael/kata4_manual/DIARIO.md` |
| Situação no desenho | **trial extra** — a Kata D não estava na alocação do integrante 3 (ver §5, D0) |

## 1. Tempo (time-to-green) — RQ1

| Métrica | Valor |
|---|---|
| Início | `2026-09-17T01:01:37+00:00` |
| Fim (verde) | `2026-09-17T01:12:19+00:00` |
| `time_to_green_s` | **642,0 s** (10 min 42 s) |
| `time_to_green_min` | **10,70 min** |
| `status` / `event` | `green` / `1` (não censurado) |
| Consumo do time-box | **30,6 %** — sobraram 24 min 18 s |
| Iterações de pytest | 5 (8/10 → 9/10 → 8/10 → 8/10 → 10/10) |

Medido por `scripts/timing/track_time.py` (`start` → `green`), com o resultado
em `results/timing.json` e `results/timing.csv`.

Diferente do trial da Kata B, aqui o `start` foi dado **antes do primeiro
contato com o enunciado**, como manda §6.4 do desenho — o executor não havia
lido `katas/kata4_extrator_tags/enunciado.md` nem a suíte antes de ligar o
relógio. O desvio D3 da Kata B, portanto, **não se aplica** a este trial, o que
torna os 10 min 42 s mais fiéis ao procedimento do que os 8 min 07 s da Kata B.

Repartição aproximada: ~1 min de leitura do enunciado e da suíte, ~3 min de
planejamento e digitação da 1ª versão, ~3 min de depuração dos dois defeitos
reais, ~3,5 min perdidos em uma regressão de ferramental (§2).

## 2. Testes de aceitação — RQ2

| Métrica | Valor |
|---|---|
| `tests_passed` | **10** |
| `tests_failed` | **0** |
| `pct_testes_passando` | **100 %** |
| Iterações até o verde | 5 |

```
tests/teste_aceitacao.py::test_sem_tags                          PASSED
tests/teste_aceitacao.py::test_uma_tag                           PASSED
tests/teste_aceitacao.py::test_tags_diferentes                   PASSED
tests/teste_aceitacao.py::test_tag_repetida_mantem_ordem         PASSED
tests/teste_aceitacao.py::test_tag_sem_fechamento_ignorada       PASSED
tests/teste_aceitacao.py::test_remover_tags_simples              PASSED
tests/teste_aceitacao.py::test_remover_tags_multiplas            PASSED
tests/teste_aceitacao.py::test_remover_tags_sem_tags             PASSED
tests/teste_aceitacao.py::test_remover_tags_nao_fechada_mantem_marcador  PASSED
tests/teste_aceitacao.py::test_extrair_tags_conteudo_vazio       PASSED

10 passed in 0.02s
```

A suíte é a cópia inalterada de `katas/kata4_extrator_tags/teste_aceitacao.py`
(variável controlada: fixada antes do trial e não editável pelo participante).

### Defeitos observados no caminho até o verde

| Iteração | Falhas | Natureza | Causa | Correção |
|---|---|---|---|---|
| 1 | 2 | defeito de lógica | `(.*)` guloso casou `[b]um[/b] texto [b]dois[/b]` como um conteúdo só | `(.*)` → `(.*?)` |
| 1 | (idem) | defeito de lógica | `re.sub(r"\[/?[a-z]+\]", "", texto)` apagou marcador **sem par**, quebrando `test_remover_tags_nao_fechada_mantem_marcador` | usar o padrão pareado com `sub(r"\2", ...)` |
| 3 e 4 | 2 | **ruído de ferramental** | edição mal escapada no shell: gravou `r""` e depois um byte de controle `0x02` no lugar de `\2` | reescrever o arquivo por heredoc literal |

Distinção que importa para a leitura do dado: **os defeitos de programação
foram dois**, ambos na primeira versão, e ambos na fronteira entre o que o
enunciado diz e o que a suíte exige. As iterações 3 e 4 foram uma regressão de
edição (escaping), não de raciocínio — mas estão **dentro** dos 10 min 42 s,
porque o cronômetro mede tempo de parede até o verde e não separa as duas
coisas. Se o objetivo for comparar dificuldade cognitiva entre trials, este
tempo está inflado em ~3,5 min.

O item mais interessante do trial: a suíte **contradiz** o enunciado. O
enunciado manda remover os marcadores "literalmente", enquanto
`test_remover_tags_nao_fechada_mantem_marcador` exige preservar `[b]` sem par.
A leitura da suíte antes de codificar é o que evitou um retrabalho maior — e é
uma diferença de processo relevante frente aos trials `ai`, em que o assistente
recebe enunciado e suíte de uma vez.

## 3. Métricas estáticas do código final — RQ3

Coletadas por `scripts/metrics/collect_metrics.py` (Radon + jscpd) sobre
`trials/rafael/kata4_manual/src/solucao.py`, com a linha consolidada em
`results/static_metrics.csv`.

| Métrica | Valor |
|---|---|
| `files` | 1 |
| `loc` | **17** |
| `sloc` | 11 (LLOC 11, 1 comentário de linha, 5 linhas em branco) |
| `cc_avg` | **2,0** (grau A) |
| `cc_total` | 4 |
| `mi_avg` | **89,24** (grau A) |
| `duplication_pct` | **0,0 %** (medição real do jscpd, 0 clones em 1 arquivo — ver D5) |

Complexidade ciclomática por função (Radon, 2 blocos analisados):

| Função | CC | Grau |
|---|---|---|
| `extrair_tags` | 3 | A |
| `remover_tags` | 1 | A |

É o trial de **melhores métricas estruturais de toda a amostra** (menor
`cc_avg` entre os cinco trials, maior MI). O motivo é metodologicamente
incômodo: concentrar a lógica num regex com backreference deixa as duas funções
triviais e joga a complexidade real para dentro de uma string, onde nem Radon
nem jscpd a enxergam. O código é curto e simples de medir, não necessariamente
simples de entender ou manter — exatamente a fragilidade de construto que o §8
do desenho aponta para `loc`/`cc_avg` como proxies de qualidade.

### Comparação com a solução de referência da kata (descritiva)

| Métrica | Este trial (`manual`) | Referência da kata |
|---|---|---|
| Funções | 2 | 2 |
| `loc` | 17 | 14 |
| `sloc` | 11 | 9 |
| `cc_total` | 4 | 3 |
| `cc_avg` | 2,0 (A) | 1,5 (A) |

Praticamente a mesma solução: as duas usam padrão pareado, mesmo número de
funções e complexidade quase idêntica. A diferença de 2 SLOC vem do comentário
e da construção explícita do dicionário (`if nome not in resultado`) em vez de
`setdefault`/`defaultdict`. A comparação é apenas descritiva; a referência não é
um trial e não entra nas hipóteses.

## 4. Comparação com os trials já registrados

| Trial | Tratamento | `time_to_green` | Testes | Iterações | `loc` | `cc_avg` | `mi_avg` | `dup%` |
|---|---|---|---|---|---|---|---|---|
| **rafael · kata4 (este)** | **manual** | **10,70 min** | 10/10 | **5** | 17 | **2,0** (A) | **89,24** | 0,0 |
| rafael · kata2 | manual | 8,12 min | 10/10 | 3 | 33 | 8,0 (B) | 62,94 | 0,0 |
| rafael · kata1 | ai | 0,20 min | 12/12 | 1 | 59 | 2,6 | 67,93 | 0,0 |
| vitor · kata1 | ai | 1,17 min | 12/12 | 1 | 43 | 3,0 | 49,62 | 0,0 |
| vitor · kata2 | ai | 0,20 min | 10/10 | 1 | 17 | 7,0 | 61,56 | 0,0 |
| vitor · kata3 | ai | 0,13 min | 11/11 | 1 | 19 | 13,0 | 58,82 | 0,0 |

Leituras (descritivas, N=1 por célula — nada aqui testa hipótese):

- **Tempo por tratamento:** os dois trials `manual` (8,12 e 10,70 min) estão
  uma ordem de grandeza acima dos quatro `ai` (0,13 a 1,17 min). Mediana
  `manual` 9,41 min vs mediana `ai` 0,20 min. Todos verdes, nenhum censurado.
- **Estrutura não acompanha o tempo:** o trial mais demorado da amostra é
  também o de melhor `cc_avg` e melhor MI. Entre os dois trials `manual` do
  mesmo integrante a diferença estrutural é enorme (`cc_avg` 2,0 vs 8,0), o que
  sugere que, nesta amostra, `cc_avg` responde mais ao **tipo de problema**
  (regex vs varredura com estado) do que ao tratamento.
- **Iterações até o verde** (exploratória): 5 e 3 nos `manual`, 1 em todos os
  `ai`. É a única variável em que os dois grupos não se sobrepõem, e nenhuma
  hipótese formal do desenho a cobre.
- **Corretude:** 100 % em todos os seis trials; `pct_testes_passando` continua
  sem variância, e a taxa de sucesso está em 6/6 — confirmando o alerta do §3 do
  desenho sobre RQ2.
- **Kata D com IA (integrante 2, Paulo):** `docs/relatorio-katas-paulo.md`
  reporta 5 min 10 s, 31 LOC, CC 2,80 e MI 78,2. **Não é comparável linha a
  linha**: foi medido com cronômetro e ferramentas próprios, fora de
  `scripts/timing` e `scripts/metrics`, e não está nos CSVs do experimento.

## 5. Desvios do protocolo e ameaças específicas deste trial

- **D0 — trial fora da alocação.** O quadrado latino do §5.1 alocou ao
  integrante 3 as katas A e E (`ai`) e B (`manual`). A Kata D **não** foi
  sorteada para ele; este trial foi executado por pedido direto, como extensão
  (§5.2). Consequência: o integrante 3 passa a ter 2 trials `manual` e 2 `ai`,
  o que **quebra o balanceamento kata × tratamento** do desenho original se as
  observações forem agregadas sem cuidado. Para a análise pareada de RQ1, o par
  canônico do integrante 3 continua sendo `kata1_ai` × `kata2_manual`; este
  trial entra como observação adicional, não como substituto.
- **D1 — relógio começa depois do preparo.** O `start` foi dado após criar o
  diretório do trial e copiar a suíte (mas antes de abrir o enunciado). Mesma
  convenção dos outros trials registrados.
- **D2 — trial simulado, não humano.** ⚠️ Desvio mais grave, e ele condiciona a
  leitura de tudo acima: quem executou este trial foi o **Claude Code**,
  operando sob instrução explícita de resolver a kata no ritmo e no processo de
  um estudante, sem consultar solução de referência. Não é a observação de um
  participante humano sem assistente. Consequências: (a) o dado **não deve ser
  agregado** com trials humanos sem essa ressalva; (b) o nível `manual` da
  variável independente está, a rigor, **não instanciado** — o fator que o
  desenho isola não pode ser isolado quando o próprio executor é o assistente;
  (c) as pausas de leitura e digitação foram inseridas deliberadamente e estão
  **dentro** dos 10 min 42 s, logo o `time_to_green` é um valor construído para
  ser plausível, não um tempo de digitação humano medido.
- **D3 — não se aplica.** Ao contrário da Kata B, o enunciado não havia sido
  lido antes do `start`.
- **D4 — contaminação evitada.** `solucao_referencia.py` e
  `solucao-com-ia-Paulo.py` da Kata D **não** foram abertos antes do verde; a
  referência só foi lida depois, para a comparação descritiva do §3.
- **D5 — patch no coletor de métricas.** `scripts/metrics/collect_metrics.py`
  recebeu o mesmo ajuste do trial da Kata A: resolver o executável do `npx` por
  `shutil.which` (no Windows é `npx.cmd`, que o `subprocess` não encontra
  sozinho). Sem isso o `jscpd` não roda e `duplication_pct` sai como fallback
  `0.0`, indistinguível de uma medição real de 0 %. Na primeira tentativa de
  coleta deste trial o patch havia sido perdido (ver D7) e o aviso de fallback
  apareceu; a coleta registrada no CSV foi refeita **com** o patch e sem aviso.
- **D6 — coleta isolada.** `collect_metrics.py` regenera o CSV inteiro varrendo
  `trials/`, e `trials/rafael/kata1_ai/` e `kata5_ai/` existem localmente só com
  caches, porque o código deles vive em outras branches. Rodar o coletor sobre
  `trials/` produziria linhas zeradas e sobrescreveria dado válido. A coleta foi
  feita sobre cópia isolada dos dois trials `manual` e **apenas as linhas novas**
  foram anexadas a `results/static_metrics.csv`.
- **D7 — reversão do diretório de trabalho entre os dois trials.** ⚠️ Durante
  este trial, o diretório foi revertido a um estado anterior: o relógio da
  máquina recuou ~1 h 45 min e todos os artefatos da Kata B (código, diário,
  relatório, patch do coletor, linha do `timing.csv` e do
  `static_metrics.csv`) desapareceram do disco. Os arquivos da Kata B foram
  **restaurados** a partir dos valores medidos na sessão e o tempo foi
  reinserido com `track_time.py record` (`--elapsed 8:07`, timestamps
  originais), com `ended_at` corrigido no JSON. As métricas estáticas da Kata B
  foram **recoletadas do código restaurado** e reproduziram exatamente os
  valores originais (LOC 33, SLOC 28, `cc_avg` 8,0, `cc_total` 8, MI 62,94), o
  que evidencia que o código restaurado é idêntico ao que ficou verde. Ainda
  assim, a linha `rafael,kata2,manual` do `timing.csv` é um **re-registro**, não
  a gravação direta do cronômetro.

## 6. Rastreabilidade

| Artefato | Caminho |
|---|---|
| Código da solução | `trials/rafael/kata4_manual/src/solucao.py` |
| Suíte de aceitação (cópia fixa) | `trials/rafael/kata4_manual/tests/teste_aceitacao.py` |
| Diário do processo | `trials/rafael/kata4_manual/DIARIO.md` |
| Tempo | `results/timing.json`, `results/timing.csv` (linha `rafael,kata4,manual`) |
| Métricas estáticas | `results/static_metrics.csv` (linha `rafael,kata4,manual`) |

Comandos executados:

```bash
# preparo (fora do relógio)
mkdir -p trials/rafael/kata4_manual/src trials/rafael/kata4_manual/tests
cp katas/kata4_extrator_tags/teste_aceitacao.py trials/rafael/kata4_manual/tests/

# cronometragem (start antes de abrir o enunciado)
python scripts/timing/track_time.py start --participant rafael --kata kata4 --treatment manual
python scripts/timing/track_time.py green --notes "SEM IA - codificacao manual ..."

# testes de aceitação (dentro do diretório do trial, 5 execuções)
PYTHONPATH="$PWD/src" python -m pytest tests -q -o "python_files=test_*.py teste_*.py"

# métricas estáticas (cópia isolada, ver D6)
python scripts/metrics/collect_metrics.py --trials-dir <copia>/trials --output <copia>/metrics.csv
```
