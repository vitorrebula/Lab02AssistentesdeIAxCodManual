# Justificativa das Katas — Fonte e Equivalência de Dificuldade

## 1. Fonte das katas

As 6 katas abaixo são **autorais**, criadas especificamente para este
experimento (grupo de pesquisa), e não correspondem a exercícios
publicados em plataformas indexadas por buscadores/crawlers (LeetCode,
HackerRank, Codewars, etc.). O objetivo é reduzir o risco de que o
assistente de IA reproduza, a partir de memorização de treinamento, uma
solução já vista para o exercício exato — o que inflaria artificialmente
o desempenho do tratamento "com IA" e comprometeria a validade interna do
experimento (ameaça listada no Passo 1: *vazamento de solução já
vista / memorização*).

| # | Kata | Domínio do problema |
|---|------|----------------------|
| 1 | Cesta de Compras | Regras de negócio (cálculo de total + cupons de desconto condicionais) |
| 2 | Escala de Plantões | Manipulação de intervalos de tempo (merge de intervalos sobrepostos) |
| 3 | Validador de Senha Corporativa | Validação de string com múltiplas regras independentes |
| 4 | Extrator de Tags | Parsing de texto com regex / pseudo-marcação |
| 5 | Controle de Estoque | Gerenciamento de estado (dict) com validações e consultas |
| 6 | Máquina de Catraca | Máquina de estados finita simples |

Cada kata testa uma habilidade distinta (regras condicionais, manipulação
de intervalos, validação, parsing, estado mutável, máquina de estados),
o que também ajuda a diversificar o tipo de tarefa avaliada nas RQs, e
reduz a chance de qualquer kata em particular já existir, com este
enunciado exato, em bases de treinamento públicas.

## 2. Validação da suíte de testes de aceitação

Cada kata possui uma solução de referência (`solucao_referencia.py`,
mantida em `gabarito_NAO_DISTRIBUIR/`, fora do pacote entregue aos
participantes) que foi executada contra a suíte `teste_aceitacao.py`
correspondente. **Todos os testes passam em todas as 6 katas**:

| Kata | Testes | Resultado |
|------|--------|-----------|
| 1 — Cesta de Compras | 12 | 12 passed |
| 2 — Escala de Plantões | 10 | 10 passed |
| 3 — Validador de Senha | 11 | 11 passed |
| 4 — Extrator de Tags | 10 | 10 passed |
| 5 — Controle de Estoque | 12 | 12 passed |
| 6 — Máquina de Catraca | 9 | 9 passed |

Isso confirma que a suíte de aceitação de cada kata é executável e
consistente com uma solução correta conhecida — condição necessária para
usá-la como critério objetivo de "time-to-green" no Passo 3.

## 3. Justificativa quantitativa de dificuldade equivalente

Como métrica objetiva e independente de julgamento subjetivo, medimos a
solução de referência de cada kata com **Radon** (a mesma ferramenta
usada em `collect_metrics.py` para o RQ3), obtendo nº de funções,
LOC/SLOC, complexidade ciclomática (CC) e Índice de Manutenibilidade (MI):

| Kata | Funções | LOC | SLOC | CC total | CC média | MI | Nº testes |
|------|---------|-----|------|----------|----------|-----|-----------|
| 1 — Cesta de Compras | 5 | 41 | 33 | 15 | 3.0 | 49.6 | 12 |
| 2 — Escala de Plantões | 3 | 33 | 23 | 9 | 3.0 | 57.9 | 10 |
| 3 — Validador de Senha | 1 | 24 | 19 | 12 | 12.0 | 57.9 | 11 |
| 4 — Extrator de Tags | 2 | 14 | 9 | 3 | 1.5 | 100.0 | 10 |
| 5 — Controle de Estoque | 4 | 27 | 21 | 10 | 2.5 | 56.3 | 12 |
| 6 — Máquina de Catraca | 1 | 21 | 19 | 6 | 6.0 | 63.7 | 9 |

**Leitura dos dados:**
- **SLOC** da solução de referência varia entre 9 e 33 linhas — todas
  resolvíveis dentro do time-box de 35 min por um estudante de graduação
  com conhecimento básico de Python.
- **CC total** varia entre 3 e 15, e **nº de testes de aceitação** entre 9
  e 12 — faixas relativamente próximas, indicando exigência comparável de
  cobertura de casos de borda.
- A kata 4 (Extrator de Tags) é a de menor complexidade estrutural (CC
  total = 3, MI = 100), pois sua solução de referência se apoia em uma
  única expressão regular. Optamos por mantê-la no conjunto porque (a)
  diversifica o tipo de raciocínio exigido (parsing/regex, ausente nas
  demais katas) e (b) seu número de testes de aceitação (10) e casos de
  borda (tag sem fechamento, tags repetidas, conteúdo vazio) é comparável
  às demais. Ainda assim, registramos como **limitação conhecida**: a
  variação de CC entre katas (1,5 a 12,0 de complexidade média) é maior
  que o ideal, e deve ser reportada como ameaça à validade de construto
  no Relatório Final — o desenho *within-subject* contrabalanceado
  (Passo 1) mitiga parcialmente esse desbalanceamento, pois cada
  participante passa por katas de ambos os "extremos" em tratamentos
  diferentes (com e sem IA), mas o grupo deve considerar isso na
  interpretação dos resultados de tempo por kata individual.

## 4. Divisão par para os tratamentos

As 6 katas permitem divisão exata: **3 katas resolvidas com IA e 3 sem
IA** por participante, em ordem contrabalanceada entre os integrantes do
grupo (ex.: metade dos participantes resolve as katas 1, 3, 5 com IA e
2, 4, 6 sem IA; a outra metade faz o inverso), controlando o efeito de
aprendizado entre katas e a familiaridade prévia com cada exercício.

## 5. Estrutura de entrega

```
katas/                          <- distribuído aos participantes
  kata1_cesta_compras/
    enunciado.md
    esqueleto.py                <- renomear/copiar para solucao.py
    teste_aceitacao.py
  kata2_escala_plantoes/ ...
  ...

gabarito_NAO_DISTRIBUIR/        <- uso exclusivo da equipe (correção/validação)
  kata1_cesta_compras/solucao_referencia.py
  ...
```

O diretório `gabarito_NAO_DISTRIBUIR/` **não deve** ser copiado para o
ambiente dos participantes durante os trials, para não comprometer o
experimento.
