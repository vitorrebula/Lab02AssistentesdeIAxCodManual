# RQ2 — O uso de IA reduz defeitos observados nos testes de aceitação?

## Métrica e dados

Para cada trial, calculamos **taxa de testes passando = 100 × `testes_passando / testes_total`**, em porcentagem, e **falhas absolutas = `testes_total − testes_passando`**. Isso permite comparar katas com 10 ou 12 testes sem confundir a quantidade de casos com a taxa de aprovação. A métrica mede apenas a corretude coberta pela suíte de aceitação; zero falhas nessa suíte não prova ausência de defeitos no código.

Fonte: `dados/consolidado.csv`. O conjunto comum tem 12 trials (três integrantes × quatro katas, dois tratamentos por integrante). Para a pergunta sobre o **fim do time-box**, usamos os oito registros cuja fonte de testes é `registro_trial`: quatro de Rafael e quatro de Vitor. Os quatro testes de Paulo foram conferidos **posteriormente** (`fonte_testes=verificacao_posterior`) e aparecem separadamente. As duas katas extras de Vitor permanecem no consolidado, fora do conjunto balanceado.

## Descritivos e falhas

| Fonte e tratamento | Trials | Mediana da taxa | Q1 | Q3 | IQR | Falhas absolutas (soma) |
|---|---:|---:|---:|---:|---:|---:|
| No trial, com IA | 4 | 100% | 100% | 100% | 0 p.p. | 0 |
| No trial, sem IA | 4 | 100% | 100% | 100% | 0 p.p. | 0 |
| Conferência posterior, com IA (Paulo) | 2 | 100% | 100% | 100% | 0 p.p. | 0 |
| Conferência posterior, sem IA (Paulo) | 2 | 100% | 100% | 100% | 0 p.p. | 0 |

Nos oito trials usados no teste, **cada trial tem zero testes falhando**. Os quatro de Paulo também apresentam zero falhas na conferência posterior, sem comprovar a taxa no instante de encerramento do trial.

## Wilcoxon pareado

Não existem pares “mesmo integrante, mesma kata” com e sem IA: cada kata foi resolvida uma vez por integrante. Seguimos a unidade de análise do desenho experimental, **o integrante**, calculando a mediana de suas duas katas em cada tratamento. Rafael: 100% com IA e 100% sem IA; Vitor: 100% e 100%. As duas diferenças pareadas (IA − manual) são exatamente zero.

**H0:** não há diferença na taxa de testes passando entre tratamentos. **H1:** há diferença (bicaudal, α = 0,05). A chamada ao Wilcoxon exato retorna **W = 0, p = 1,000, n = 2 pares**, sob a convenção para o caso degenerado de todos os postos nulos. **Decisão: não rejeitar H0.** Como não existe nenhuma diferença não nula para ordenar, esse p-valor é uma convenção de teste degenerado, **não uma estimativa de ausência de efeito**. A taxa binária de trials verdes também é 100% nos dois tratamentos; sem pares discordantes, o McNemar primário previsto no desenho igualmente não distinguiria tratamentos.

O procedimento de registro encerra um trial como `green` quando todos os testes passam. Isso seleciona registros verdes com 100% de aprovação por construção; a taxa só ajudaria a comparar tratamentos se houvesse trials encerrados no time-box com testes falhando. Não há censurados aos 35 minutos nos dados atuais. O resultado não sustenta a afirmação de que a IA reduziu defeitos, nem a de que os tratamentos sejam equivalentes. O `kata2_manual` de Rafael é um re-registro após perda do dado original, e os testes de Paulo foram conferidos depois; manter essas diferenças de proveniência visíveis em qualquer síntese final.

## Reprodução

```bash
python -m pip install -r scripts/analysis/requirements.txt
python scripts/analysis/rq2.py
```

O script gera `dados/rq2_resultados.json` com mediana, Q1, Q3, IQR, falhas por trial e por tratamento, pares, estatística, p-valor e decisão. Ele valida os denominadores e não modifica o consolidado ou os registros brutos.
