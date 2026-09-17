# Registro de prompts — rafael / kata1 (Cesta de Compras) / tratamento `ai`

Refs #23 — métrica exploratória de RQ1 (nº de prompts/interações com o
assistente), prevista em `docs/desenho-experimento.md` §4.2 e
`docs/ambiente-experimento.md` §3.

## Configuração do assistente

| Item | Valor |
|---|---|
| Assistente | Claude Code (CLI, terminal integrado) |
| Modelo | **Opus 5 (1M context)** (`claude-opus-5[1m]`) |
| Acesso | leitura/escrita direta nos arquivos do trial (sem copiar/colar) |
| Experiência prévia do integrante com a ferramenta | básica |
| Nº de prompts do integrante durante o trial | **1** |
| Iterações de correção após rodar os testes | **0** (verde na 1ª execução) |
| Intervenções manuais no código gerado | **0** |

## Prompt 1 (único)
> Execute a Kata A (1) para mim, colete o tempo de resolução
> métricas estáticas do código final e garanta que passe
> por todos os testes

1. leitura do enunciado (`katas/kata1_cesta_compras/enunciado.md`), da suíte
   de aceitação e do protocolo (`docs/desenho-experimento.md` §6);
2. preparo de `trials/rafael/kata1_ai/` com `tests/` copiado da kata (sem
   edição) e `src/` vazio;
3. início do cronômetro (`track_time.py start`);
4. implementação de `src/solucao.py` (5 funções, uma escrita, nenhuma
   iteração de correção — verde na primeira execução dos testes);
5. fechamento do trial (`track_time.py green`) e coleta das métricas
   estáticas (`collect_metrics.py`, Radon + jscpd).

Observação sobre a contagem: uma primeira formulação deste mesmo prompt foi
interrompida pelo integrante e reenviada corrigindo "Kata E" para "Kata A" no
corpo da issue. A correção é de escopo (qual kata executar), não de conteúdo
técnico da solução — nenhuma orientação sobre implementação foi dada em
nenhum dos dois envios. Contabilizado como **1 prompt**.

## Notas de execução (para a análise)

- **Fora do cronômetro:** varredura do repositório, leitura do protocolo,
  criação dos diretórios do trial e cópia dos testes de aceitação. O
  cronômetro cobriu a escrita da solução até o verde, como nos trials do
  integrante 1 (`vitor`), mantendo a comparabilidade da medida entre trials
  `ai`.
- **Sem contaminação por solução pronta:** o assistente **não** abriu
  `katas/kata1_cesta_compras/solucao_referencia.py`,
  `katas/kata1_cesta_compras/solucao-sem-ia-paulo.py` nem
  `trials/vitor/kata1_ai/src/solucao.py` (a solução do integrante 1 para a
  mesma kata) em nenhum momento — antes ou depois do início do cronômetro. A
  implementação saiu do enunciado e da suíte de aceitação. Diferença relevante
  em relação ao trial `rafael/kata5_ai` (issue #25), onde a leitura do
  gabarito foi declarada como ameaça.
- **Desvio de variável controlada:** `docs/ambiente-experimento.md` §3 fixa
  **Sonnet** como agente para todos os trials `ai`; este trial rodou em
  **Opus 5**, modelo já configurado na sessão. O desvio está registrado aqui
  para ser discutido na análise ou corrigido com uma re-execução em Sonnet.
  Mesmo desvio já registrado no trial `rafael/kata5_ai`.
- **Correção de instrumentação (após o verde, sem efeito no tempo medido):**
  `scripts/metrics/collect_metrics.py` chamava `npx` via `subprocess` sem
  resolver o executável, o que no Windows sempre levantava `FileNotFoundError`
  (o executável é `npx.cmd`) e fazia o script cair no fallback silencioso
  `duplication_pct = 0.0`. Com a correção o jscpd roda de fato e a duplicação
  passa a ser **medida**. Para este trial o valor medido é o mesmo (0.0%,
  confirmado por execução manual do jscpd: 0 clones em 59 linhas), mas os
  valores de `duplication_pct` coletados **antes** desta correção — inclusive
  os dos trials do integrante 1 — eram fallback, não medição.
