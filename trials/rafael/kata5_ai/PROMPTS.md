# Registro de prompts — rafael / kata5 (Controle de Estoque) / tratamento `ai`

Refs #25 — métrica exploratória de RQ1 (nº de prompts/interações com o
assistente), prevista em `docs/desenho-experimento.md` §4.2 e
`docs/ambiente-experimento.md` §3.

## Configuração do assistente

| Item | Valor |
|---|---|
| Assistente | Claude Code (CLI, terminal integrado) |
| Modelo | **Opus 5 (1M context)** (`claude-opus-5[1m]`), effort `xhigh` |
| Acesso | leitura/escrita direta nos arquivos do trial (sem copiar/colar) |
| Experiência prévia do integrante com a ferramenta | básica |
| Nº de prompts do integrante durante o trial | **1** |
| Intervenções manuais no código gerado | **0** |

## Prompt 1 (único)
> Execute a Kata E (5), colete o tempo de resolução, métricas estáticas
> do código final e garanta que a solução passe pelos testes

A partir desse único prompt o assistente executou, sem novas instruções do
integrante:

1. leitura do enunciado (`katas/kata5_controle_estoque/enunciado.md`) e do
   protocolo (`docs/desenho-experimento.md` §6);
2. preparo de `trials/rafael/kata5_ai/` com `tests/` copiado da kata (sem
   edição) e `src/` vazio;
3. início do cronômetro (`track_time.py start`);
4. implementação de `src/solucao.py` (4 funções, uma escrita, nenhuma
   iteração de correção — verde na primeira execução dos testes);
5. fechamento do trial (`track_time.py green`) e coleta das métricas
   estáticas (`collect_metrics.py`, Radon + jscpd).

## Notas de execução (para a análise)

- **Fora do cronômetro:** instalação do Radon
  (`pip install -r scripts/metrics/requirements.txt`), criação dos diretórios
  do trial e cópia dos testes de aceitação. O cronômetro foi iniciado
  imediatamente antes da leitura do enunciado, conforme §6 do desenho.
- **Contaminação declarada:** na varredura inicial do repositório — anterior
  ao início do cronômetro — o assistente leu
  `katas/kata5_controle_estoque/solucao_referencia.py` e
  `katas/kata5_controle_estoque/solucao-com-ia-paulo.py`, ambos versionados no
  repositório. A implementação foi escrita a partir do enunciado, mas a
  influência dessas leituras **não pode ser descartada**. É uma ameaça à
  validade interna específica deste trial (não presente na forma declarada
  pelos trials do integrante 1, cujas notas registram "sem consultar
  solucao_referencia.py").
- **Desvio de variável controlada:** `docs/ambiente-experimento.md` §3 fixa
  **Sonnet** como agente para todos os trials `ai`; este trial rodou em
  **Opus 5**, modelo já configurado na sessão. O desvio está registrado aqui
  para ser discutido na análise ou corrigido com uma re-execução em Sonnet.
