# Diário do trial — rafael · Kata D (`kata4`) · SEM IA

Equivalente manual do `PROMPTS.md` dos trials `ai`: registra o que foi
consultado, as iterações de pytest e os defeitos encontrados, já que aqui não
existe histórico de prompts para auditar.

## Condições declaradas

| Item | Valor |
|---|---|
| Tratamento | `manual` |
| Assistente de IA | nenhum (sem chat, sem autocomplete com IA, sem LLM externo) |
| Consulta permitida | enunciado da kata e suíte de aceitação |
| Consulta **não** feita | `katas/kata4_extrator_tags/solucao_referencia.py` e `katas/kata4_extrator_tags/solucao-com-ia-Paulo.py` (evitar contaminação) |
| Suíte de aceitação | cópia byte a byte de `katas/kata4_extrator_tags/teste_aceitacao.py`, não editada |
| Início do relógio | `2026-09-17T01:01:37+00:00` (**antes** do primeiro contato com o enunciado) |
| Fim (verde) | `2026-09-17T01:12:19+00:00` |

> ⚠️ Este trial foi **simulado** (executor: Claude Code sob instrução de
> resolver no ritmo de um estudante, sem usar conhecimento de assistente).
> Ver desvio **D2** em `docs/relatorio-trial-rafael-kata4-manual.md`: o dado
> não deve ser lido como observação de um participante humano.

## Leitura do enunciado — a pegadinha da suíte

O enunciado diz que `remover_tags` deve remover os marcadores
"literalmente", mas `test_remover_tags_nao_fechada_mantem_marcador` exige que
`[b]` **permaneça** no texto quando não há fechamento. Ou seja: não se pode
apagar marcador cegamente; só o par correspondente sai. Isso foi percebido na
leitura da suíte, antes de digitar, e determinou a abordagem.

## Abordagem escolhida (antes de digitar)

1. um único regex com **backreference**: `\[([a-z]+)\](.*?)\[/\1\]` — resolve de
   uma vez par correspondente, tag sem fechamento (não casa) e conteúdo vazio;
2. `extrair_tags`: `findall` + acumular num dict, preservando ordem de aparição;
3. `remover_tags`: `sub` do **mesmo** padrão, trocando o casamento pelo grupo do
   conteúdo (`\2`) — evita manter dois regexes que podem divergir.

## Iterações até o verde

| # | Momento | Resultado | Causa | Correção |
|---|---|---|---|---|
| 1 | ~4 min | **8 passaram, 2 falharam** | (a) `(.*)` **guloso**: `[b]um[/b] texto [b]dois[/b]` casou como um conteúdo só (`um[/b] texto [b]dois`); (b) `re.sub(r"\[/?[a-z]+\]", "", texto)` apagou o `[b]` sem par | — |
| 2 | ~7 min | **9 passaram, 1 falhou** | defeito (a) corrigido | `(.*)` → `(.*?)` (lazy) |
| 3 | ~9 min | **8 passaram, 2 falharam** | **regressão de ferramenta**, não de lógica: a edição do replacement foi mal escapada pelo shell e gravou `r""` | — |
| 4 | ~10 min | **8 passaram, 2 falharam** | mesma regressão: a segunda tentativa de patch gravou um **byte de controle `0x02`** no lugar de `\2` | — |
| 5 | ~10,5 min | **10 passaram, 0 falharam** → verde | arquivo reescrito por heredoc literal, sem escaping | `PADRAO.sub(r"\2", texto)` |

Os **defeitos de raciocínio foram dois** (quantificador guloso e remoção cega
de marcador), ambos na primeira versão. As iterações 3 e 4 são ruído de
ferramental (escaping de shell na edição do arquivo) e estão contadas no
`time_to_green`, mas não devem ser lidas como defeito de programação — ver §2
do relatório.

## Observação sobre a estrutura do código final

Concentrar tudo num regex pareado deixou as duas funções triviais
(`extrair_tags` CC 3, `remover_tags` CC 1, `cc_avg` 2,0 grau A, MI 89,24) — o
oposto do que aconteceu na Kata B, onde a solução manual saiu monolítica com
`cc_avg` 8,0. A complexidade aqui está dentro do regex, que nenhuma das
métricas estáticas do experimento consegue ver.
