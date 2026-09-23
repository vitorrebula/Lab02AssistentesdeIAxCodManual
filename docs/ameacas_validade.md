# Ameaças à Validade do Experimento

Contexto: desenho crossover *within-subject* contrabalanceado, com as 6
katas autorais já criadas (`katas_experimento.zip`), cada participante
resolvendo 3 katas com assistente de IA e 3 sem, em time-box de 35 min
por trial.

---

## 1. Efeito de aprendizado entre katas (*learning effect*)

**Descrição.** Como cada participante resolve várias katas em sequência
dentro do mesmo experimento, ele tende a ficar mais rápido/eficiente ao
longo dos trials — não necessariamente por causa do tratamento (com ou
sem IA), mas simplesmente por já estar "aquecido": mais familiarizado
com o ambiente, a linguagem, o formato dos testes de aceitação, e até
com o próprio ato de ser cronometrado. Se, por coincidência de ordem,
todas as katas "sem IA" caírem no início da sessão de um participante e
as "com IA" no final, o tratamento "com IA" pareceria artificialmente
mais rápido só por efeito de prática, não pelo uso da ferramenta.

**Risco/impacto.** Ameaça à **validade interna**: confunde o efeito do
tratamento (IA vs. manual) com o efeito de ordem/prática, inflando ou
subestimando RQ1 (tempo) e possivelmente RQ2 (defeitos, se o participante
também erra menos por estar mais concentrado nas últimas katas).

**Mitigação aplicada neste grupo.**
- **Desenho crossover contrabalanceado**: cada participante resolve 3
  katas com IA e 3 sem IA, mas a **ordem é balanceada entre
  participantes** — metade do grupo resolve as katas {1,3,5} com IA e
  {2,4,6} sem IA; a outra metade faz o inverso. Assim, cada kata aparece
  tanto cedo quanto tarde na sessão, tanto com quanto sem IA, em
  proporções equivalentes agregando todos os participantes.
- Registrar a **ordem/posição do trial** (1ª, 2ª, 3ª... kata resolvida)
  como covariável nos dados coletados (o CSV de time-to-green já prevê
  o campo "ordem do trial"), permitindo checar estatisticamente, no
  Passo 4, se há tendência de queda no tempo apenas pela posição,
  independente do tratamento.
- Alternar também a **ordem de tratamento** dentro da sessão de cada
  participante (não fazer sempre "3 com IA seguidas, depois 3 sem IA";
  intercalar quando possível) para reduzir o efeito de fadiga
  concentrada em um único tratamento.

---

## 2. Familiaridade prévia com a ferramenta de IA escolhida

**Descrição.** Os integrantes do grupo podem ter níveis muito diferentes
de experiência com o assistente de IA escolhido (ex.: GitHub Copilot,
ChatGPT, Claude). Quem já usa a ferramenta no dia a dia tende a escrever
prompts mais eficazes, aceitar/rejeitar sugestões mais rápido e navegar
a interface sem atrito — o que infla o desempenho do tratamento "com IA"
para esse participante, independentemente da capacidade real da
ferramenta de ajudar.

**Risco/impacto.** Ameaça à **validade interna** (variável de confusão
por participante) e à **generalização dos resultados** (validade
externa): o efeito medido pode refletir "familiaridade com a ferramenta"
mais do que "efeito do uso de IA" em si.

**Mitigação aplicada neste grupo.**
- Como o desenho já é *within-subject* (cada participante passa pelos
  dois tratamentos), a familiaridade prévia de cada indivíduo afeta os
  dois braços do seu próprio par com/sem IA de forma mais controlada do
  que em um desenho *between-subject* — mas ainda pode inflar
  especificamente o braço "com IA" desse participante.
- Levantar, **antes do experimento**, um questionário curto de
  autoavaliação de familiaridade prévia com a ferramenta escolhida
  (ex.: escala 1–5, "nunca usei" a "uso diariamente") para cada
  integrante, e registrar isso como metadado do participante.
- No Relatório Final, reportar o tempo por participante **estratificado
  por nível de familiaridade** (ex.: comparar o Δ tempo com/sem IA entre
  quem já usava a ferramenta e quem não usava), e discutir se o efeito
  observado é consistente entre os grupos ou concentrado em quem já
  tinha experiência prévia.
- Se possível, fazer um **treinamento/nivelamento rápido** (ex.: 10 min
  de demonstração da ferramenta) para todos os integrantes antes do
  primeiro trial, reduzindo a variância de familiaridade inicial.

---

## 3. Vazamento de solução já vista pelo modelo (*solution leakage*)

**Descrição.** Diferente de memorização de treinamento (ameaça 4), aqui
o vazamento ocorre **dentro da sessão do próprio experimento**: se o
mesmo participante (ou colegas) já resolveu uma kata antes — em um
trial anterior, numa tentativa de piloto, ou mesmo numa conversa prévia
com o assistente sobre aquela mesma kata —, o histórico de conversa ou a
memória do participante pode "vazar" a solução para o trial "oficial",
inflando artificialmente o desempenho (com ou sem IA).

**Risco/impacto.** Ameaça à **validade interna**: o tempo/qualidade
medidos deixam de refletir a capacidade de resolver a kata do zero e
passam a refletir reaproveitamento de solução já conhecida.

**Mitigação aplicada neste grupo.**
- Cada kata é resolvida **uma única vez por participante** em todo o
  experimento (nunca repetida em piloto e depois no trial oficial pelo
  mesmo indivíduo) — reservar katas de piloto/teste **separadas** das 6
  katas oficiais, se for necessário validar o ambiente antes.
- Ao usar assistente de IA baseado em chat com histórico persistente
  (ex.: ChatGPT/Claude com memória de conversas anteriores), **iniciar
  uma conversa nova (sem contexto prévio)** a cada trial, para que o
  modelo não tenha acesso a soluções de katas anteriores do mesmo
  participante na mesma sessão.
- Orientar os participantes a não discutir as katas entre si antes de
  todos terem completado seus trials (evitar vazamento entre colegas,
  já que o grupo inteiro usa o mesmo conjunto de 6 katas).
- Registrar, na coleta de dados, se o participante indicou já ter visto
  aquela kata específica antes (flag de autorrelato), para permitir
  excluir ou marcar esse trial na análise se necessário.

---

## 4. Risco de memorização (o assistente reproduzir uma solução do treinamento em vez de ajudar de fato)

**Descrição.** Se as katas usadas forem exercícios muito conhecidos e
amplamente indexados (ex.: clássicos do LeetCode/HackerRank/Codewars com
centenas de milhares de resoluções), o assistente de IA pode já ter
"visto" o enunciado e a solução durante seu treinamento, e apenas
reproduzir uma resposta memorizada — em vez de efetivamente raciocinar
sobre o problema e ajudar o participante. Isso infla artificialmente o
desempenho do tratamento "com IA", que deixaria de medir "ajuda de IA na
resolução de um problema novo" e passaria a medir "capacidade de
recuperação de treinamento".

**Risco/impacto.** É a ameaça de **maior risco à validade de construto**
do experimento: se não mitigada, o RQ1/RQ2 deixam de medir o que o
Goal do GQM propõe medir.

**Mitigação aplicada neste grupo (já implementada).**
- As 6 katas usadas são **100% autorais**, criadas especificamente para
  este experimento (`Cesta de Compras`, `Escala de Plantões`, `Validador
  de Senha Corporativa`, `Extrator de Tags`, `Controle de Estoque`,
  `Máquina de Catraca`) — nenhuma delas existe em plataformas públicas
  indexadas (LeetCode/HackerRank/Codewars) nem em repositórios do
  GitHub, portanto **não pode estar no corpus de treinamento** de
  nenhum assistente de IA anterior à data de criação deste experimento.
  Essa é a mitigação mais forte possível contra essa ameaça — mais forte
  do que apenas escolher katas "pouco indexadas" de plataformas
  públicas, que ainda têm alguma (mesmo que pequena) chance de exposição.
- Como evidência adicional de originalidade, os enunciados e as suítes
  de testes de aceitação (`teste_aceitacao.py`) foram escritos e
  validados neste próprio processo, com solução de referência conferida
  100% (64/64 testes passando) — não são adaptações de exercícios
  existentes.
- **Ressalva a registrar no Relatório Final**: mesmo katas autorais
  podem, em tese, se assemelhar estruturalmente a padrões genéricos e
  amplamente vistos em treinamento (ex.: "validador de regras",
  "máquina de estados simples", "merge de intervalos" são padrões de
  programação comuns, mesmo com enunciado e nomes de variáveis
  originais). Isso não configura vazamento de solução específica, mas
  pode facilitar a IA por reconhecimento de padrão geral — uma
  limitação diferente de memorização literal, que deve ser mencionada
  como discussão qualitativa (RQ1/RQ2), não como falha do desenho.

---

## Resumo (para incluir em `desenho-experimento.md`)

| # | Ameaça | Tipo de validade afetada | Mitigação principal |
|---|--------|---------------------------|----------------------|
| 1 | Efeito de aprendizado entre katas | Interna | Crossover contrabalanceado + registro de ordem do trial |
| 2 | Familiaridade prévia com a ferramenta de IA | Interna / Externa | Questionário de autoavaliação + análise estratificada |
| 3 | Vazamento de solução já vista (dentro da sessão) | Interna | Kata resolvida uma única vez; conversa de IA sem histórico prévio |
| 4 | Memorização (solução vista no treinamento do modelo) | Construto | Katas 100% autorais, não indexadas publicamente |
