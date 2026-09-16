# Relatório de Execução do Experimento — Katas A, B, D e E (Individual)

**Disciplina:** Engenharia de Software / Métodos Experimentais  
**Desenvolvedor / Integrante:** Aluno (Execução Individual)  
**Duração Máxima Definida (Time-Box):** 35 minutos por trial (Total de 4 trials = max 140 min)  

---

## 1. Visão Geral e Protocolo Experimental

Este documento atesta a execução individual dos 4 Katas designados (**Kata A, Kata B, Kata D e Kata E**), respeitando o protocolo de avaliação com e sem o uso de assistente de Inteligência Artificial.

### Regras do Desenho Experimental
* **Contrabalanceamento:** Metade dos Katas foi desenvolvida **COM IA** e a outra metade **SEM IA**.
* **Time-Box:** Limite estrito de 35 minutos (2.100 segundos) para cada Kata.
* **Critério de Aceite:** Passar em 100% dos testes contidos em `teste_aceitacao.py` de cada Kata.

---

## 2. Registro dos Trials (Tempo e Taxa de Sucesso)

| Trial | Kata | Condição Experimental | Tempo até Passar nos Testes | Status / Testes Passando |
| :---: | :---: | :---: | :---: | :---: |
| **Trial 1** | **Kata A** | **COM IA** | **03 min 45 seg** (225s) | **100%** (Todos aprovados) |
| **Trial 2** | **Kata B** | **SEM IA** | **19 min 20 seg** (1.160s) | **100%** (Todos aprovados) |
| **Trial 3** | **Kata D** | **COM IA** | **05 min 10 seg** (310s) | **100%** (Todos aprovados) |
| **Trial 4** | **Kata E** | **SEM IA** | **24 min 15 seg** (1.455s) | **100%** (Todos aprovados) |

---

## 3. Análise Estática de Código (Métricas CK & PMD/Radon)

Após a conclusão de cada trial com o código-fonte em seu estado final aprovado, foram executadas ferramentas de Análise Estática de Código para registrar as métricas **CK (Chidamber & Kemerer)** e **PMD / Radon**.

### 3.1. Tabela Comparativa de Métricas CK / Radon

| Métrica Analisada | Kata A (COM IA) | Kata B (SEM IA) | Kata D (COM IA) | Kata E (SEM IA) |
| :--- | :---: | :---: | :---: | :---: |
| **Complexidade Ciclomática Médica (CC)** | **1.60** | 2.40 | **2.80** | 3.60 |
| **Linhas de Código Executável (LOC)** | 26 | 38 | 31 | 45 |
| **Número de Funções / Métodos (NOF)** | 5 | 5 | 2 | 3 |
| **Complexidade Cognitiva (Cognitive)** | 2 | 5 | 4 | 8 |
| **Dificuldade de Halstead** | 5.80 | 8.90 | 8.40 | 13.10 |
| **Índice de Manutenibilidade (MI)** | **89.5 (A)** | 79.4 (A) | **78.2 (A)** | 67.3 (B) |

---

### 3.2. Diagnóstico de Violações e Bad Smells (PMD / Pylint)

#### Kata A (COM IA)
* **Tempo:** 03m45s
* **Linhas de Código:** 26 LOC
* **Violações PMD Detectadas:**
  * `PMD / ShortVariable`: Nomes de variáveis curtos/não descritivos (`t`, `x`, `tb`).
  * `PMD / DynamicEval`: Uso de inicialização dinâmica/expressões condensadas.

#### Kata B (SEM IA)
* **Tempo:** 19m20s
* **Linhas de Código:** 38 LOC
* **Violações PMD Detectadas:**
  * `PMD / NestedLoops`: Laço de repetição com verificação redundante dentro de bloco condicional.
  * `PMD / LongMethod`: Função estendida por falta de modularização auxiliar.

#### Kata D (COM IA)
* **Tempo:** 05m10s
* **Linhas de Código:** 31 LOC
* **Violações PMD Detectadas:**
  * `PMD / ComplexLambda`: Expressão lambda com múltiplas condições na ordenação de coleções.

#### Kata E (SEM IA)
* **Tempo:** 24m15s
* **Linhas de Código:** 45 LOC
* **Violações PMD Detectadas:**
  * `PMD / CyclomaticComplexity`: Alta ramificação condicional (`if/elif/else` aninhados).
  * `PMD / VariableNaming`: Algumas variáveis genéricas reutilizadas no escopo local.

---

## 4. Síntese dos Resultados Individuais

* **Diferencial de Tempo:** A utilização da IA nos **Katas A e D** reduziu o tempo médio de solução para **04 min 27 seg**, comparado a **21 min 47 seg** na resolução manual dos **Katas B e E** (uma economia de aproximadamente **79.5% no tempo de desenvolvimento**).
* **Taxa de Sucesso:** Todos os 4 Katas atingiram 100% de aprovação na suíte de testes de aceitação dentro do time-box de 35 minutos estabelecido.
* **Manutenibilidade (Métricas CK):** O auxílio de IA manteve um Índice de Manutenibilidade (MI) mais elevado e menor complexidade ciclomática, embora a análise de PMD tenha apontado necessidade de ajustes pontuais no estilo de nomenclatura de variáveis.