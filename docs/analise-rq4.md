# RQ4 — O ganho de velocidade cobra um preço estrutural?

**Questão (RQ extra, além das três do enunciado):** existe associação entre o
tempo até o verde (*time-to-green*) e as métricas estruturais do código
entregue — LOC, complexidade ciclomática (média e total), densidade de
complexidade e *Maintainability Index*?

RQ1 e RQ3 comparam **tratamentos**; RQ4 muda a unidade de leitura: cada trial é
um ponto no plano *tempo × estrutura*, e a pergunta é se as duas coisas andam
juntas. É a pergunta que o enunciado deixa implícita ao exigir LOC como
variável de controle — "código gerado por IA pode ser mais verboso" — mas não
formaliza.

**Hipóteses.** H4₀: `ρ(tempo, métrica estrutural) = 0`. H4₁: `ρ ≠ 0`
(bicaudal, α = 0,05). Cinco métricas formam uma família, corrigida por
**Holm-Bonferroni** — sem correção, a chance de pelo menos um `p < 0,05`
por acaso passa de 20%.

## Dados e método

Fonte: `dados/consolidado.csv`. A análise primária usa os **10 trials com tempo
cronometrado** (4 de Rafael, 6 de Vitor). Os 4 trials de Paulo têm horários
derivados dos de Rafael (ver [revisao-dados-s02.md](revisao-dados-s02.md)) e
entrariam na correlação como pontos que não medem tempo nenhum; eles aparecem
apenas na análise de sensibilidade e, na figura, como marca vazada fora do
ajuste.

Duas medidas de associação, por razões diferentes:

- **r de Pearson** — associação **linear**; é a métrica pedida explicitamente.
  Reportado com IC 95% pela transformação *z* de Fisher.
- **ρ de Spearman** — associação **monotônica** sobre postos; robusto a
  outliers e a escala, o que importa com `n = 10` e tempos que variam de 0,13 a
  20,13 min.

A densidade de complexidade (`100 × cc_total / loc`) é derivada na análise, não
no consolidado: `cc_total` cresce com o tamanho do arquivo, então sem
normalizar não se separa "código complexo" de "código grande".

## Resultados (n = 10 trials cronometrados)

| Métrica estrutural | r de Pearson | IC 95% | p | p (Holm) | ρ de Spearman | p |
|---|---:|---:|---:|---:|---:|---:|
| **MI médio** | **+0,715** | [+0,15; +0,93] | **0,020** | 0,101 | **+0,723** | **0,018** |
| **CC total / 100 LOC** | **−0,675** | [−0,92; −0,08] | **0,032** | 0,128 | **−0,730** | **0,017** |
| LOC | +0,433 | [−0,27; +0,83] | 0,212 | 0,635 | +0,369 | 0,294 |
| CC total | −0,364 | [−0,81; +0,34] | 0,301 | 0,635 | −0,370 | 0,293 |
| CC média por função | −0,303 | [−0,78; +0,40] | 0,394 | 0,635 | −0,348 | 0,325 |

Leitura direta: **trials mais demorados entregaram código com MI mais alto e
complexidade menos densa**. O MI explica cerca de metade da variância do tempo
(`r² = 0,51`); a densidade, cerca de 46%. As duas associações são as únicas com
`p < 0,05` sem correção — e **nenhuma sobrevive a Holm** (`p` ajustado 0,101 e
0,128). Formalmente, portanto, **não rejeitamos H4₀** para nenhuma das cinco
métricas.

LOC não mostrou associação detectável com o tempo: a hipótese informal de que
"IA escreve mais rápido e mais longo" não aparece como correlação nesta amostra.

## A associação é do tempo ou do tratamento?

Esta é a parte que muda a interpretação. Repetindo as correlações **dentro de
cada tratamento** (n = 5 de cada lado), o efeito global se dissolve:

| Métrica | Global (n = 10) | Só com IA (n = 5) | Só sem IA (n = 5) |
|---|---:|---:|---:|
| MI médio | +0,715 (p = 0,020) | −0,828 (p = 0,083) | +0,327 (p = 0,591) |
| CC total / 100 LOC | −0,675 (p = 0,032) | −0,290 (p = 0,637) | −0,871 (p = 0,055) |
| LOC | +0,433 (p = 0,212) | +0,334 (p = 0,583) | +0,876 (p = 0,051) |

Dentro do tratamento com IA, a correlação com MI **troca de sinal**. Isso é o
desenho da figura [rq4_dispersao_pearson.png](../results/figures/rq4_dispersao_pearson.png)
tornado explícito: os pontos formam **duas nuvens separadas** (segundos com IA,
minutos sem IA), e a reta global apenas liga os dois centros de nuvem. A
associação observada é, em boa medida, **o efeito do tratamento reaparecendo
disfarçado de correlação** — um caso clássico de confundimento por variável
omitida. Reportar `r = +0,72` como "demorar mais produz código mais
manutenível" seria errado.

Tendência interna que merece registro: **sem IA**, quanto mais tempo o
integrante levou, maior o código (`r = +0,88`) e menos densa a complexidade
(`r = −0,87`) — compatível com a ideia de que, na mão, mais tempo é gasto
escrevendo mais linhas, não lógica mais intrincada. Com `n = 5` e `p ≈ 0,05`
antes de qualquer correção, é hipótese para um estudo maior, não achado.

## Sensibilidade: incluindo os tempos derivados (n = 14)

| Métrica | r de Pearson | p | ρ de Spearman | p |
|---|---:|---:|---:|---:|
| MI médio | +0,673 | 0,008 | +0,698 | 0,006 |
| CC total / 100 LOC | −0,594 | 0,025 | −0,669 | 0,009 |
| CC total | −0,475 | 0,086 | −0,472 | 0,089 |
| LOC | +0,257 | 0,376 | +0,339 | 0,237 |
| CC média | −0,206 | 0,479 | −0,331 | 0,248 |

Os `p` caem (efeito do `n` maior, não de evidência nova) e **MI e densidade
passariam por Holm** nesta variante (`p` ajustado 0,083 para as duas, ainda
acima de 0,05). A direção e a ordem das métricas não mudam, o que é o ponto da
sensibilidade: **a conclusão de RQ4 não depende dos tempos derivados** — mas a
análise primária continua sendo a dos 10 trials cronometrados, porque quatro
dos catorze pontos não são medições de tempo.

## Resposta à RQ4

**Não detectamos associação estatisticamente sustentada** entre tempo até o
verde e estrutura do código, depois da correção para as cinco comparações. O
padrão bruto mais forte — trials mais demorados com MI mais alto e complexidade
menos densa — é **confundido com o tratamento**: ele desaparece, e no caso do
MI inverte, quando se olha dentro de cada tratamento. A leitura honesta é que
**este desenho não separa "efeito do tempo" de "efeito da IA"**, porque tempo e
tratamento são quase colineares na amostra (todos os trials com IA fecharam em
menos de 1,2 min, exceto o de tempo derivado; todos os manuais cronometrados
levaram mais de 8 min).

Para separá-los seria preciso variar o tempo **dentro** do tratamento — por
exemplo, trials manuais com tarefas de dificuldades muito diferentes, ou um
tratamento "com IA, mas com revisão obrigatória" que gaste minutos.

## Reprodução

```bash
python -m pip install -r scripts/analysis/requirements.txt
python scripts/analysis/rq4.py          # -> dados/rq4_resultados.json
python scripts/dashboard/plots_advanced.py  # -> results/figures/rq4_dispersao_pearson.png
```

O script lê `dados/consolidado.csv`, não modifica dado bruto, e grava
descritivos, correlações (global, por tratamento e sensibilidade), IC 95%, `p`
de Holm e a lista dos pontos em `dados/rq4_resultados.json`. A figura lê esse
JSON para anotar as estatísticas, de modo que gráfico e texto não possam
divergir.
