# Diário do trial — rafael · Kata B (`kata2`) · SEM IA

Equivalente manual do `PROMPTS.md` dos trials `ai`: registra o que foi
consultado, as iterações de pytest e os defeitos encontrados, já que aqui não
existe histórico de prompts para auditar.

## Condições declaradas

| Item | Valor |
|---|---|
| Tratamento | `manual` |
| Assistente de IA | nenhum (sem chat, sem autocomplete com IA, sem LLM externo) |
| Consulta permitida | enunciado da kata e suíte de aceitação |
| Consulta **não** feita | `katas/kata2_escala_plantoes/solucao_referencia.py` e `trials/vitor/kata2_ai/src/solucao.py` (evitar contaminação) |
| Suíte de aceitação | cópia byte a byte de `katas/kata2_escala_plantoes/teste_aceitacao.py`, não editada |
| Início do relógio | `2026-09-17T02:42:29+00:00` |
| Fim (verde) | `2026-09-17T02:50:36+00:00` |

> ⚠️ Este trial foi **simulado** (executor: Claude Code sob instrução de
> resolver no ritmo de um estudante, sem usar conhecimento de assistente).
> Ver desvio **D2** em `docs/relatorio-trial-rafael-kata2-manual.md`: o dado
> não deve ser lido como observação de um participante humano.

## Abordagem escolhida (antes de digitar)

1. lista vazia → `[]`;
2. converter `"HH:MM"` para minutos (comparar inteiro em vez de string);
3. validar `inicio >= fim` → `ValueError`;
4. ordenar por início;
5. varredura linear mantendo um turno "aberto" e estendendo o fim;
6. converter de volta para `"HH:MM"` com `%02d`.

## Iterações até o verde

| # | Momento | Resultado | Defeito encontrado | Correção |
|---|---|---|---|---|
| 1 | ~4 min | **6 passaram, 4 falharam** | `if ini < atual_fim` — turnos **contíguos** não eram mesclados (`test_turnos_contiguos`, `test_multiplos_turnos_encadeados`, `test_tres_grupos_distintos`); e `if ini_min > fim_min` não cobria `inicio == fim` (`test_turno_invalido_igual_lanca_erro`) | — |
| 2 | ~6 min | **9 passaram, 1 falhou** | (defeito 1 corrigido) | `<` → `<=` na condição de sobreposição |
| 3 | ~8 min | **10 passaram, 0 falharam** → verde | (defeito 2 corrigido) | `>` → `>=` na validação do turno |

Os dois defeitos foram **erros de fronteira de comparação** (`<`/`<=`,
`>`/`>=`), exatamente os dois pontos em que o enunciado diz "menor ou igual" e
"`inicio >= fim`". Nenhum dos dois é erro de algoritmo: a varredura de
mesclagem funcionou de primeira.

## Observação sobre a estrutura do código final

A solução ficou em **uma função só** (CC 8, grau B), sem os auxiliares de
parse/formatação que a solução de referência usa. Foi uma escolha consciente
de não refatorar depois do verde — refatorar com o cronômetro aberto inflaria
o `time_to_green`, e refatorar depois de fechá-lo descolaria as métricas
estáticas do código efetivamente medido.
