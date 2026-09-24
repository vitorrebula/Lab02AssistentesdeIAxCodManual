# Revisão dos dados da S02

## Cobertura e integridade

O comando `python scripts/analysis/consolidate_s02.py` gerou `dados/consolidado.csv` a partir de `results/timing.json`, `results/timing.csv` e `results/static_metrics.csv`. Ele exige chaves únicas `(integrante, kata, tratamento)` e correspondência entre os dois arquivos de tempo, as métricas e os diretórios de código em `trials/`.

| Integrante | Conjunto comum (katas 1, 2, 4 e 5) | Com IA | Sem IA | Extras preservados |
|---|---:|---:|---:|---|
| Paulo | 4/4 | 2 | 2 | Nenhum |
| Rafael | 4/4 | 2 | 2 | Nenhum |
| Vitor | 4/4 | 2 | 2 | `kata3_ai`, `kata6_manual` |
| **Total** | **12/12** | **6** | **6** | **2 (14 linhas ao todo)** |

As katas extras aparecem no consolidado com `no_plano_4_katas=false`. Mantê-las permite auditoria; análises que exigem exatamente quatro katas por integrante devem filtrar `no_plano_4_katas=true`. O campo `tratamento` usa apenas `com IA`/`sem IA`, `tempo_min` está em minutos decimais (quatro casas), e os testes são contagens inteiras. `testes_total = tests_passed + tests_failed` do registro bruto. Os 14 registros têm testes passando iguais ao total registrado, mas os testes de Paulo foram conferidos **posteriormente**, não no instante associado aos horários derivados.

`censurado` é um booleano **anulável**: `true` indica censura registrada, `false` indica verde registrado dentro do time-box, e célula vazia indica que os dados **não permitem determinar** a censura. O script atribui exatamente **35,0000 min** aos registros `censored_timebox` e mantém `true`; não há nenhum desse tipo nos brutos atuais. Existem 10 registros `false` e quatro vazios (Paulo). Não transformar vazios em `false`: isso inventaria observações de *time-to-green*. O campo `status` conserva a classificação original e `fonte_tempo` permite selecionar medições adequadas à análise de RQ1.

## Proveniência que afeta a análise

- Os quatro horários/intervalos de Paulo foram **derivados dos registros de Rafael**, conforme consta nas notas de `timing.json`. O `time_to_green_s` bruto e a censura são nulos. São preservados no dataset, mas **não devem entrar como quatro medições independentes de tempo**. O teste final foi conferido depois. O assistente registrado para esses trials é ChatGPT, enquanto o plano da S01 fixa Claude Code; comparar todos os trials “com IA” como se usassem uma única ferramenta exige ressalva.
- O tempo de Rafael em `kata2_manual` foi reconstituído após perda do registro original. `fonte_tempo=reconstituido`; preservar a linha e reportar análise de sensibilidade sem ela ao investigar RQ1.
- O registro `vitor/kata4_manual` contém `elapsed_s=1208`, mas a diferença entre `started_at` e `ended_at` é **56.916 s**. O consolidado conserva os 1208 s da medição declarada no bruto e o registro de outliers pede conferência da origem; não substituir por 56.916 s.

## Outliers: detecção e decisão

`dados/outliers.csv` registra as ocorrências e a decisão de cada uma. O critério exploratório de Tukey (`Q1 − 1,5 × IQR` e `Q3 + 1,5 × IQR`) foi calculado **separadamente por tratamento**, com os tempos que têm verde registrado e fonte não derivada: cinco com IA e cinco sem IA. Quartis por interpolação linear. Com amostras tão pequenas, as cercas variam muito; estar fora delas **não justifica exclusão automática**.

| Trial | Sinalização | Decisão |
|---|---|---|
| Rafael, kata 2, sem IA | 8,1167 min abaixo da cerca de 10,6250 min; registro reconstituído | **Manter e sinalizar.** Testar sensibilidade de RQ1 sem este registro, pela perda da medição original; não excluí-lo apenas por Tukey. |
| Vitor, kata 1, com IA | 1,1667 min acima da cerca de 0,4083 min | **Manter e sinalizar.** Variação entre katas e apenas cinco observações nesse tratamento; não há evidência de erro nesse tempo pelo critério estatístico isolado. |
| Vitor, kata 4, sem IA | 20,1333 min acima da cerca de 10,8250 min | **Manter e verificar** a divergência entre duração e timestamps antes de uma análise de tempo sensível a esse trial. |
| Vitor, kata 4, sem IA | `elapsed_s` 1208 contra intervalo entre horários de 56.916 s | **Manter e verificar** nos registros originais; a discrepância não autoriza escolher um dos dois números por conveniência. |

Nenhuma linha foi removida. Os tempos derivados de Paulo são um **problema de proveniência**, registrado acima, não outliers estatísticos independentes. Não há censurados de 35 minutos nos dados disponíveis; se forem adicionados depois, executar novamente o script e revisar o registro de outliers.

## Reprodução

```bash
python scripts/analysis/consolidate_s02.py
```

O script usa apenas a biblioteca padrão do Python e regrava os dois CSVs em `dados/` de modo determinístico. Ele interrompe a execução se faltar um trial em uma das fontes, houver duplicata, teste inválido, time-box diferente de 35 minutos ou desequilíbrio no conjunto comum de quatro katas.
