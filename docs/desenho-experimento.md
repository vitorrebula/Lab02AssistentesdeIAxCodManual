# Desenho do Experimento

Refs #1 — define as questões de pesquisa, as hipóteses (H0/H1), as variáveis
(independente, dependentes, controladas e de confusão) e o tipo de desenho
experimental usado na comparação entre uso de assistente de IA e codificação
manual.

Complementa [ambiente-experimento.md](ambiente-experimento.md) (Issue #6),
que fixa linguagem, IDE, assistente e convenção de diretórios.

## 1. Objetivo

Seguindo o formato de *goal template* de Wohlin et al.:

> **Analisar** o uso de um assistente de IA de codificação (Claude Code)
> **com o propósito de** avaliar seu efeito
> **com respeito a** tempo de resolução, corretude funcional e qualidade
> estrutural do código produzido
> **do ponto de vista** do desenvolvedor
> **no contexto de** katas de programação em Python resolvidas por
> integrantes do grupo, com time-box de 35 minutos por trial.

## 2. Questões de pesquisa

| ID | Questão |
|---|---|
| **RQ1** (tempo) | O uso de assistente de IA altera o tempo até todos os testes de aceitação passarem (*time-to-green*) na resolução de uma kata? |
| **RQ2** (defeitos) | O uso de assistente de IA altera a corretude funcional da solução, medida pela proporção de testes de aceitação que passam? |
| **RQ3** (estrutura) | O uso de assistente de IA altera a qualidade estrutural do código produzido, medida por complexidade ciclomática, duplicação e tamanho (LOC)? |

## 3. Hipóteses

Notação: para uma métrica *X*, `θ(X_ia)` e `θ(X_manual)` denotam a tendência
central (mediana) de *X* nos trials com assistente de IA e nos trials manuais,
respectivamente. As hipóteses são **pareadas por integrante** (cada integrante
contribui com uma observação em cada tratamento — ver §5).

Todos os testes são declarados a priori como **bicaudais** (`≠`): o grupo não
assume a direção do efeito, mesmo onde a literatura sugere uma. A direção
esperada é registrada apenas como leitura secundária, e mudar para teste
unicaudal depois de ver os dados seria *p-hacking*.

### RQ1 — Tempo (time-to-green)

- **H1₀ (nula):** `θ(time_to_green_ia) = θ(time_to_green_manual)` — o uso de
  assistente de IA não altera o time-to-green.
- **H1₁ (alternativa):** `θ(time_to_green_ia) ≠ θ(time_to_green_manual)` — o
  uso de assistente de IA altera o time-to-green.
- *Direção esperada (secundária):* redução do tempo com IA.

### RQ2 — Defeitos (corretude funcional)

- **H2₀ (nula):** `θ(pct_testes_passando_ia) = θ(pct_testes_passando_manual)`
  — o uso de assistente de IA não altera a proporção de testes de aceitação
  que passam.
- **H2₁ (alternativa):** `θ(pct_testes_passando_ia) ≠
  θ(pct_testes_passando_manual)`.
- *Direção esperada (secundária):* nenhuma; há argumentos nas duas direções
  (mais código gerado por unidade de tempo pode aumentar ou reduzir defeitos).

> ⚠️ **Cuidado de operacionalização em RQ2.** Um trial só fecha como `green`
> quando **todos** os testes passam, então, por construção,
> `pct_testes_passando = 100%` em todo trial verde. A variável só varia entre
> os trials **censurados** (que estouraram o time-box). Consequência: o teste
> primário de RQ2 é sobre a **taxa de sucesso** — a proporção de trials que
> atingem o verde dentro dos 35 min, variável binária pareada — e
> `pct_testes_passando` entra como medida contínua secundária, informativa
> sobre *quão perto* do verde os trials censurados chegaram. Ver §7.

### RQ3 — Estrutura do código

Família de três hipóteses, uma por métrica estrutural (correção para
comparações múltiplas em §7):

- **H3a₀:** `θ(cc_avg_ia) = θ(cc_avg_manual)` · **H3a₁:** `θ(cc_avg_ia) ≠ θ(cc_avg_manual)`
  — complexidade ciclomática média por função.
- **H3b₀:** `θ(duplication_pct_ia) = θ(duplication_pct_manual)` · **H3b₁:** `≠`
  — percentual de linhas duplicadas.
- **H3c₀:** `θ(loc_ia) = θ(loc_manual)` · **H3c₁:** `≠`
  — tamanho da solução em linhas de código.
- *Direção esperada (secundária):* nenhuma direção assumida; a hipótese
  informal do grupo é que o código gerado com IA tende a ser mais longo e mais
  duplicado, mas isso não é assumido no teste.

## 4. Variáveis

### 4.1 Variável independente (fator)

| | |
|---|---|
| **Fator** | Uso de assistente de IA na resolução da kata |
| **Tipo** | Categórica nominal, 2 níveis (tratamentos) |
| **Nível `ai`** | Kata resolvida **com** Claude Code, que lê e edita os arquivos do trial diretamente |
| **Nível `manual`** | Kata resolvida **sem** qualquer assistente de IA — nenhum autocomplete com IA habilitado, nenhum chat externo, nenhuma consulta a LLM |
| **Manipulação** | Atribuída pelo desenho (§5), não escolhida pelo participante |
| **Registro** | Sufixo do diretório do trial (`<kata>_ai` / `<kata>_manual`) e coluna `treatment` nos dois CSVs de saída |

Consulta a documentação, Stack Overflow e busca web **é permitida nos dois
tratamentos** — o fator isolado é o assistente de IA, não o acesso a
informação. Isso precisa ser dito ao participante antes do trial manual.

### 4.2 Variáveis dependentes (resposta)

| Variável | Definição operacional | Unidade / escala | Instrumento | Onde é lida |
|---|---|---|---|---|
| `time_to_green_min` | Tempo do início do trial até todos os testes de aceitação passarem; **censurado em 35 min** se o time-box estourar | minutos, razão (censurada à direita) | script de cronometragem (Issue #4) | `results/timing.csv` |
| `event` | 1 se o verde foi observado dentro do time-box, 0 se censurado | binária | idem | `results/timing.csv` |
| `pct_testes_passando` | `tests_passed / (tests_passed + tests_failed)` no fechamento do trial | %, razão \[0,100] | `pytest`, via script de cronometragem | derivada de `results/timing.csv` |
| `cc_avg` | Complexidade ciclomática média por função/método do código de solução | adimensional, razão | Radon (Issue #5) | `results/static_metrics.csv` |
| `duplication_pct` | Percentual de linhas duplicadas no código de solução | %, razão | jscpd (Issue #5) | `results/static_metrics.csv` |
| `loc` | Linhas de código do código de solução (`sloc` como variante sem brancos/comentários) | linhas, razão | Radon (Issue #5) | `results/static_metrics.csv` |

Variáveis **exploratórias** (coletadas, sem hipótese formal — não entram na
correção para comparações múltiplas):

- `mi_avg` — Maintainability Index médio (Radon).
- `cc_total` — complexidade ciclomática total do trial.
- Número de prompts/interações com o assistente nos trials `ai` (sugerido no
  enunciado como métrica exploratória para RQ1; registrar na issue do trial).

Nas duas fontes de dados a chave é a tripla `participant` + `kata` +
`treatment`, o que permite juntar tempo e estrutura por trial sem tradução.

### 4.3 Variáveis controladas (mantidas fixas)

Fixadas para todos os trials, conforme `ambiente-experimento.md`:

- Linguagem e versão: Python 3.10+.
- IDE: VS Code, com o mesmo conjunto de extensões.
- Assistente e modelo: Claude Code, mesmo modelo em todos os trials `ai`.
- Time-box: 35 minutos corridos, sem pausa.
- Suíte de testes de aceitação: a mesma para os dois tratamentos de uma kata,
  fixada antes do trial e **não editável** pelo participante.
- Ausência de qualquer outro autocomplete com IA, inclusive nos trials
  manuais.

### 4.4 Variáveis de confusão e como são tratadas

| Confundidor | Risco | Tratamento no desenho |
|---|---|---|
| Habilidade do participante | Diferenças individuais dominarem o efeito do tratamento | Desenho **within-subject**: cada integrante é seu próprio controle |
| Dificuldade da kata | Kata mais fácil cair sistematicamente em um tratamento | **Contrabalanceamento** kata × tratamento (§5); katas validados como equivalentes em escopo na Issue #3 |
| Efeito de ordem / aprendizado | Melhora por aquecimento no segundo trial | Contrabalanceamento da **ordem** dos tratamentos (AB/BA) |
| Aprender o problema | Resolver a mesma kata duas vezes torna o segundo trial trivial | Cada integrante resolve **katas diferentes** em cada tratamento (§5) |
| Familiaridade prévia com Claude Code | Ganho com IA depender da experiência prévia | Declarada por cada integrante antes da execução (§3 do doc de ambiente) e reportada na análise |
| Fadiga | Queda de desempenho no segundo trial | Intervalo (*washout*) de pelo menos 10 min entre trials do mesmo integrante |
| Efeito Hawthorne | Saber-se medido alterar o esforço | Não eliminável; declarado como ameaça (§8) |

## 5. Tipo de desenho experimental

**Desenho crossover (within-subject) contrabalanceado**, 2 tratamentos × 2
katas, com atribuição aleatória dos integrantes aos grupos de sequência.

- **Unidade experimental:** o trial (um integrante resolvendo uma kata sob um
  tratamento).
- **Unidade de análise:** o integrante — as observações são **pareadas**
  (`ai` vs `manual` do mesmo integrante).
- **Cada integrante executa 2 trials:** um com IA e um manual, em **katas
  diferentes**. Ninguém repete kata, o que elimina o principal risco do
  crossover em experimentos de programação (o *carryover* de já conhecer a
  solução do problema).

### 5.1 Quadrado latino 2×2

Os integrantes são divididos aleatoriamente em dois grupos de sequência, com
tamanhos o mais iguais possível:

| Grupo | Trial 1 | Trial 2 |
|---|---|---|
| **G1** | Kata A **com IA** | Kata B **manual** |
| **G2** | Kata A **manual** | Kata B **com IA** |

Propriedades garantidas por esse arranjo:

- Cada tratamento aparece o mesmo número de vezes em cada **posição** (1ª e
  2ª) → ordem não fica confundida com tratamento.
- Cada tratamento aparece o mesmo número de vezes em cada **kata** → a
  dificuldade da kata não fica confundida com o tratamento.
- Cada integrante contribui com um par completo → o teste pareado é aplicável.

Katas A e B saem do conjunto validado na Issue #3. A alocação
integrante → grupo é sorteada e **registrada antes da execução** (na issue de
execução dos trials), junto com a semente ou o método do sorteio.

### 5.2 Extensão para mais katas

Se o grupo optar por mais de dois trials por integrante, o mesmo princípio se
mantém com um quadrado latino maior (4 katas → 4 sequências, 2 rodadas de
`ai`/`manual` por integrante), desde que se preserve: nenhuma kata repetida
por integrante e tratamentos balanceados entre posições e katas.

### 5.3 Cegamento

Não é possível cegar o participante (ele sabe se está usando o assistente).
A coleta das variáveis dependentes, porém, é **automatizada** (Issues #4 e
#5), sem julgamento humano — o que remove o viés do avaliador na medição.

## 6. Procedimento de um trial

1. Sortear/consultar a alocação do integrante (grupo, kata, tratamento).
2. Preparar `trials/<integrante>/<kata>_<tratamento>/` com `tests/` já
   populado pelos testes de aceitação da kata e `src/` vazio.
3. Confirmar o ambiente: extensões de IA desligadas no trial manual; modelo do
   Claude Code registrado no trial com IA.
4. Iniciar o cronômetro **imediatamente antes** de o integrante abrir o
   enunciado:
   ```bash
   python scripts/timing/track_time.py watch --participant <integrante> \
     --kata <kata> --treatment <ai|manual>
   ```
5. Resolver a kata. O script fecha o trial sozinho no verde ou no estouro dos
   35 min (registrando censura).
6. Após todos os trials, coletar as métricas estruturais:
   ```bash
   python scripts/metrics/collect_metrics.py
   ```
7. Commitar o código do trial e os CSVs de resultado.

## 7. Análise estatística planejada

Declarada antes da coleta, para não escolher o teste depois de ver os dados.

- **Nível de significância:** α = 0,05.
- **Teste pareado padrão (RQ2 secundário e RQ3):** Wilcoxon signed-rank,
  escolhido por não assumir normalidade e ser robusto com amostra pequena. Se
  Shapiro-Wilk não rejeitar a normalidade das diferenças, o teste t pareado é
  reportado em paralelo.
- **RQ1 (tempo, com censura):** o time-to-green é **censurado à direita** em
  35 min, então tratá-lo como número comum enviesa a comparação (os
  censurados não valem "exatamente 35"). Análise primária: **Kaplan-Meier**
  por tratamento + **log-rank**, ou *restricted mean survival time* em 35 min.
  O Wilcoxon sobre `time_to_green_min` é reportado como análise secundária,
  explicitando que é conservador. O número de trials censurados por tratamento
  é sempre reportado.
- **RQ2 (primário):** taxa de sucesso (atingiu o verde dentro do time-box)
  comparada com **teste de McNemar** sobre os pares.
- **Tamanho de efeito:** Cliff's delta (não paramétrico) ou Cohen's d quando
  o teste t for aplicável — reportado sempre, junto do p-valor.
- **Comparações múltiplas:** dentro da família de RQ3 (3 hipóteses), correção
  de **Holm-Bonferroni**. RQ1 e RQ2 são famílias separadas, com uma hipótese
  primária cada.
- **Descritivos:** mediana e IQR por tratamento, mais o gráfico de pares
  (cada integrante como uma linha ligando `manual` → `ai`).
- **Poder estatístico:** com o N de um grupo de laboratório, o estudo é
  **subdimensionado** para detectar efeitos pequenos. Resultados não
  significativos devem ser lidos como "não detectamos diferença", nunca como
  "não há diferença", e todo o estudo é reportado como exploratório.

## 8. Ameaças à validade

**Validade interna**

- Efeito de ordem e fadiga — mitigados pelo contrabalanceamento e pelo
  intervalo entre trials, não eliminados.
- Dificuldade desigual entre katas — mitigada pelo contrabalanceamento e pela
  validação das katas (Issue #3).
- Efeito Hawthorne e expectativa do experimentador: os integrantes conhecem a
  hipótese informal do estudo, o que pode enviesar o esforço em cada
  tratamento.
- Censura em 35 min: se muitos trials forem censurados, o efeito em RQ1 fica
  parcialmente escondido pelo teto do time-box.

**Validade de construto**

- "Verde" ≠ "correto": a suíte de aceitação é o proxy de corretude, e um
  código pode passar nos testes com defeitos fora do que eles cobrem. Uma
  extensão possível é rodar uma suíte estendida (não vista pelo participante)
  sobre o código final e contar defeitos residuais.
- `loc` e `duplication_pct` são proxies grosseiros de qualidade estrutural;
  `duplication_pct` é sensível ao tamanho do arquivo, o que pode acoplar H3b
  a H3c.
- Time-to-green mede velocidade até o verde, não qualidade do processo.

**Validade externa**

- Katas são problemas pequenos, autocontidos e com testes prontos — bem
  distantes de manutenção em base de código legada. Os resultados não se
  generalizam diretamente para trabalho profissional.
- Um único assistente e um único modelo: os resultados falam do Claude Code no
  modelo registrado, não de "assistentes de IA" em geral.

**Validade de conclusão**

- N pequeno e baixo poder estatístico (§7).
- Múltiplas variáveis dependentes aumentam o risco de falso positivo —
  endereçado pela correção de Holm em RQ3.

## 9. Rastreabilidade

| Elemento do desenho | Instrumento | Issue |
|---|---|---|
| Conjunto de katas e sua validação | katas + suítes de aceitação | #3 |
| `time_to_green_min`, `event`, `pct_testes_passando` | `scripts/timing/` | #4 |
| `cc_avg`, `duplication_pct`, `loc`, `mi_avg` | `scripts/metrics/` | #5 |
| Linguagem, IDE, assistente, convenção de diretórios | `docs/ambiente-experimento.md` | #6 |
| Hipóteses, variáveis e desenho (este documento) | `docs/desenho-experimento.md` | #1 |
