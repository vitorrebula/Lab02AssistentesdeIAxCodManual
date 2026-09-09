# Ambiente do Experimento

Refs #6 — define e documenta a linguagem, a IDE e o assistente de IA usados em
todos os trials do experimento, para que o tratamento seja comparável entre
integrantes e reprodutível por terceiros.

## 1. Linguagem de programação

- **Linguagem:** Python 3.10+
- **Justificativa:** compatível com a ferramenta de métricas de complexidade
  ciclomática/LOC escolhida (Radon). CK foi descartado por exigir Java.
- **Versão a usar por todos os integrantes:** Python 3.10 ou superior
  (`python3 --version`).

## 2. IDE

- **IDE:** Visual Studio Code (VS Code)
- Extensões recomendadas (mesmas para todos, para não introduzir viés de
  autocomplete/lint entre integrantes):
  - Python (Microsoft) — syntax highlighting e execução de testes.
  - Claude Code (extensão oficial da Anthropic para VS Code).
- Nenhuma outra extensão de sugestão de código com IA (Copilot, Codeium,
  Tabnine, etc.) deve estar habilitada durante os trials, inclusive nos
  trials "manual" — para não contaminar o tratamento de controle.

## 3. Assistente de IA

- **Assistente:** Claude Code (CLI + extensão VS Code).
- **Interface usada nos trials com IA:** Claude Code no terminal integrado
  do VS Code e/ou via extensão — o assistente tem acesso de leitura/escrita
  ao repositório do trial e edita os arquivos diretamente (não é um chat
  externo com copiar/colar).
- **Regra fixa para todo o experimento:** todos os integrantes usam o mesmo
  assistente (Claude Code) e o mesmo agente (Sonnet), para manter o
  tratamento comparável entre trials. Não misturar com ChatGPT/Gemini/Copilot
  em nenhum trial "com IA".
- **Registrar em cada trial** (na Issue correspondente ou em nota no
  commit): modelo usado (ex.: Sonnet 5 / Opus 5, conforme selecionado no
  Claude Code no momento do trial) e, opcionalmente, o número de
  prompts/interações — métrica exploratória sugerida no enunciado para RQ1.
- **Ameaça à validade associada:** familiaridade prévia de cada integrante
  com o Claude Code. Antes da execução (Passo 3), cada integrante deve
  declarar seu nível de experiência prévio com a ferramenta (nenhum / básico
  / avançado) no Desenho do Experimento, para que essa variável possa ser
  discutida na análise.

## 4. Convenção de diretórios dos trials

Definida aqui para que o script de coleta de métricas estáticas (Issue #5) e
o script de cronometragem (issue de S01 correspondente) leiam/gravem dados no
mesmo lugar:

```
trials/
  <integrante>/
    <kata-id>_<tratamento>/     # tratamento = "ai" ou "manual"
      src/                      # código de solução do trial
      tests/                    # testes de aceitação da kata
```

Exemplo: `trials/vitor/kata2_ai/src/`, `trials/vitor/kata2_ai/tests/`.

## 5. Checklist de setup (repetir em cada máquina do grupo)

1. Instalar Python 3.10+ e criar um ambiente virtual na raiz do projeto:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Instalar as dependências do script de métricas estáticas:
   ```bash
   pip install -r scripts/metrics/requirements.txt
   ```
3. Instalar Node.js 18+ (necessário para `npx jscpd`, usado na detecção de
   duplicação de código — equivalente ao PMD CPD para Python).
4. Instalar e autenticar o Claude Code:
   ```bash
   npm install -g @anthropic-ai/claude-code
   claude login
   ```
5. Instalar a extensão "Claude Code" no VS Code e confirmar login com a
   mesma conta Pro usada pelo grupo.
6. Confirmar que nenhuma outra extensão de autocomplete com IA está ativa no
   VS Code.

## 6. Ferramentas de coleta

| Métrica | Ferramenta | Observação |
|---|---|---|
| Tempo (time-to-green) | script de cronometragem (Issue de S01 correspondente) | fora do escopo desta issue |
| Testes passando / falhando | `pytest` | testes de aceitação de cada kata |
| Complexidade ciclomática, LOC, Maintainability Index | Radon | ver `scripts/metrics/` (Issue #5) |
| Duplicação de código | jscpd | ver `scripts/metrics/` (Issue #5) |
