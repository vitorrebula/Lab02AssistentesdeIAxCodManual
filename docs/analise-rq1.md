# RQ1 — O uso de IA reduz o tempo até passar nos testes?

## Dados e pareamento

Fonte: `dados/consolidado.csv`, gerado da S02. A análise principal usa as quatro katas comuns (1, 2, 4 e 5) por integrante, com dois trials de cada tratamento. Há 12 trials planejados, mas os quatro de Paulo têm `censurado` vazio e `time_to_green_s` nulo no bruto: seus horários foram derivados dos horários de Rafael e os testes foram conferidos depois. **Não representam observações independentes de time-to-green.** Restam oito trials de Rafael e Vitor (quatro com IA, quatro sem IA). As katas extras 3 e 6 de Vitor também ficam fora da comparação balanceada.

O desenho não tem pares **integrante × kata**: ninguém resolveu a mesma kata duas vezes, uma em cada tratamento. O Wilcoxon solicitado é portanto feito sobre **dois pares por integrante**: para cada pessoa, calculamos a mediana de suas duas katas com IA e a mediana de suas duas katas sem IA. Parear linhas por kata entre pessoas diferentes confundiria o tratamento com diferenças individuais. A diferença testada é `mediana_IA − mediana_manual`.

## Descritivos e teste

Nenhum dos oito trials elegíveis foi censurado aos 35 minutos. Assim, os quartis são os percentis lineares usuais dos tempos até o verde (minutos); `IQR = Q3 − Q1`.

| Tratamento | n | Mediana (min) | Q1 | Q3 | IQR | Censurados |
|---|---:|---:|---:|---:|---:|---:|
| Com IA | 4 | 0,24165 | 0,20000 | 0,50415 | 0,30415 | 0 |
| Sem IA | 4 | 10,70835 | 10,05417 | 13,07085 | 3,01668 | 0 |

| Integrante | Mediana com IA (min) | Mediana sem IA (min) | Diferença IA − manual (min) |
|---|---:|---:|---:|
| Rafael | 0,24165 | 9,40835 | −9,16670 |
| Vitor | 0,68335 | 15,42500 | −14,74165 |

**Hipóteses:** H0: a diferença pareada de time-to-green não se desloca de zero; H1: há diferença (bicaudal, α = 0,05, conforme o plano). **Wilcoxon de postos sinalizados exato:** `W = 0`, `n = 2` pares, `p = 0,500`; correlação bisserial dos postos `r_rb = −1,000` (direção IA mais rápida nos dois pares). **Decisão: não rejeitar H0.** Os tempos observados são menores com IA nesta amostra, mas dois pares não sustentam uma conclusão estatística de redução. Com `n = 2`, mesmo duas diferenças na mesma direção não produzem p bicaudal abaixo de 0,05.

## Censura e qualidade dos dados

O código trata `censurado=true` como observação censurada à direita em **35 min** quando `status=censored_timebox`; esse tempo **não é imputado como se o verde tivesse ocorrido aos 35 min**. Quando há censura, os quartis descritivos são extraídos da curva de Kaplan–Meier e podem ser não estimáveis. O Wilcoxon só usa integrantes cujos trials planejados têm verde observado em ambas as condições, pois substituir censurados por 35 min enviesaria os postos. Os registros com censura desconhecida também não entram no teste. Nesta versão não há censurados confirmados; o plano previa Kaplan–Meier/log-rank como análise principal **se houvesse censura**.

Os outliers de `dados/outliers.csv` foram **mantidos**. O `kata2_manual` de Rafael foi reconstituído após perda do registro original; o `kata4_manual` de Vitor registra 1208 s, mas seus timestamps abrangem 56.916 s. A exclusão de qualquer um remove a condição manual completa de um dos dois integrantes e impede o Wilcoxon balanceado com dois trials por tratamento. Portanto, a decisão sobre H0 depende de dados cuja proveniência precisa ser esclarecida. As notas de vários trials com IA mencionam um prompt do Claude Code; isto é apenas contexto qualitativo, sem registro padronizado suficiente para estimar efeito do número de prompts. Os trials com IA de Paulo indicam ChatGPT, diferente do assistente fixado no plano, além do problema dos tempos derivados.

## Reprodução

```bash
python -m pip install -r scripts/analysis/requirements.txt
python scripts/analysis/rq1.py
```

O script lê `dados/consolidado.csv` e gera `dados/rq1_resultados.json`, com descritivos, pares, censurados, omissões e resultado do teste. Não modifica os dados brutos. Se surgirem trials censurados ou novos dados cronometrados, regenerar antes o consolidado com `python scripts/analysis/consolidate_s02.py` e executar novamente esta análise.
