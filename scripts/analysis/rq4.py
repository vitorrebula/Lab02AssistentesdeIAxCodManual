#!/usr/bin/env python3
"""Analisa RQ4: associacao entre time-to-green e estrutura do codigo entregue.

RQ4 (RQ extra) -- "O ganho de velocidade cobra um preco estrutural?" Em vez de
comparar tratamentos (RQ1/RQ3), RQ4 olha o trial como um ponto no plano
tempo x estrutura e mede a ASSOCIACAO entre as duas coisas, com r de Pearson
(linear) e rho de Spearman (monotonico, robusto a outliers e a escala).

Fonte: dados/consolidado.csv (saida de consolidate_s02.py). Nenhum dado e
embutido no codigo; nada e reescrito fora de dados/rq4_resultados.json.

Analise primaria: apenas trials com tempo cronometrado (fonte_tempo diferente
de derivado_ou_autodeclarado) -- os quatro trials de Paulo tem horarios
derivados dos de Rafael e nao sao medicoes independentes de tempo, entao
entrariam na correlacao como pontos inventados. Eles aparecem so na analise de
sensibilidade, explicitamente rotulada.
"""

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import pearsonr, spearmanr

TREATMENTS = ("com IA", "sem IA")
# Metricas estruturais confrontadas com o tempo. densidade_cc e derivada aqui
# (nao existe no consolidado) porque cc_total sozinha cresce com o tamanho.
STRUCTURE_FIELDS = ("loc", "cc_media", "cc_total", "mi_medio", "densidade_cc")
DERIVED_SOURCE = "derivado_ou_autodeclarado"


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"{path}: consolidado vazio")
    seen = set()
    for row in rows:
        key = (row["integrante"], row["kata"], row["tratamento"])
        if key in seen:
            raise ValueError(f"trial duplicado: {key}")
        seen.add(key)
        if row["tratamento"] not in TREATMENTS:
            raise ValueError(f"tratamento invalido em {key}: {row['tratamento']!r}")
        row["tempo_min"] = float(row["tempo_min"])
        for field in ("loc", "cc_media", "cc_total", "mi_medio"):
            row[field] = float(row[field])
        if row["loc"] <= 0:
            raise ValueError(f"loc invalida em {key}")
        # densidade: complexidade total por 100 linhas, para nao confundir
        # "codigo complexo" com "codigo grande" (mesma normalizacao da RQ3).
        row["densidade_cc"] = 100.0 * row["cc_total"] / row["loc"]
    return rows


def fisher_ci(r, n, confidence=0.95):
    """IC de Pearson pela transformacao z de Fisher; None se n < 4."""
    if n < 4 or abs(r) >= 1:
        return None
    z = math.atanh(r)
    # 1.959964 = quantil 0.975 da normal padrao (evita dependencia extra)
    half = 1.959963984540054 / math.sqrt(n - 3)
    return [round(math.tanh(z - half), 4), round(math.tanh(z + half), 4)]


def correlate(rows, field):
    time = np.array([r["tempo_min"] for r in rows], dtype=float)
    structure = np.array([r[field] for r in rows], dtype=float)
    n = len(rows)
    if n < 3 or np.ptp(time) == 0 or np.ptp(structure) == 0:
        return {"n": n, "pearson_r": None, "pearson_p": None, "ic95_pearson": None,
                "spearman_rho": None, "spearman_p": None,
                "obs": "variancia nula ou n < 3: correlacao nao definida"}
    r, p_r = pearsonr(time, structure)
    rho, p_rho = spearmanr(time, structure)
    return {
        "n": n,
        "pearson_r": round(float(r), 4),
        "pearson_p": round(float(p_r), 4),
        "ic95_pearson": fisher_ci(float(r), n),
        "spearman_rho": round(float(rho), 4),
        "spearman_p": round(float(p_rho), 4),
        "r2": round(float(r) ** 2, 4),
    }


def holm(pvalues):
    """Holm-Bonferroni: p ajustados, monotonos, para a familia de correlacoes.

    Cinco metricas estruturais confrontadas com o mesmo tempo formam uma
    familia; sem ajuste, a chance de pelo menos um p < 0,05 por acaso passa de
    20%. Chaves sem p-valor ficam de fora do ajuste.
    """
    items = sorted(((k, p) for k, p in pvalues.items() if p is not None), key=lambda kv: kv[1])
    total, adjusted, running = len(items), {}, 0.0
    for index, (name, p) in enumerate(items):
        running = max(running, min(1.0, p * (total - index)))
        adjusted[name] = round(running, 4)
    return adjusted


def block(rows, label):
    """Correlacoes de um conjunto de trials: global e dentro de cada tratamento."""
    out = {"conjunto": label, "n_trials": len(rows), "global": {}, "por_tratamento": {}}
    for field in STRUCTURE_FIELDS:
        out["global"][field] = correlate(rows, field)
    out["holm_global"] = {
        "pearson": holm({f: out["global"][f]["pearson_p"] for f in STRUCTURE_FIELDS}),
        "spearman": holm({f: out["global"][f]["spearman_p"] for f in STRUCTURE_FIELDS}),
    }
    for treatment in TREATMENTS:
        group = [r for r in rows if r["tratamento"] == treatment]
        out["por_tratamento"][treatment] = {
            "n_trials": len(group),
            **{field: correlate(group, field) for field in STRUCTURE_FIELDS},
        }
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    rows = read_rows(root / "dados/consolidado.csv")

    timed = [r for r in rows if r["fonte_tempo"] != DERIVED_SOURCE]
    derived = [r for r in rows if r["fonte_tempo"] == DERIVED_SOURCE]

    results = {
        "questao": ("RQ4 -- existe associacao entre o tempo ate o verde e as metricas "
                    "estruturais do codigo entregue (LOC, complexidade, manutenibilidade)?"),
        "hipoteses": {
            "H4_0": "rho(tempo, metrica estrutural) = 0",
            "H4_1": "rho(tempo, metrica estrutural) != 0 (bicaudal, alfa = 0,05)",
        },
        "n_total_consolidado": len(rows),
        "n_primario_cronometrado": len(timed),
        "n_excluidos_tempo_derivado": len(derived),
        "excluidos": [f"{r['integrante']}/{r['kata']} ({r['tratamento']})" for r in derived],
        "primario": block(timed, "trials com tempo cronometrado"),
        "sensibilidade_com_derivados": block(rows, "todos os trials (inclui tempos derivados)"),
        "pontos": [
            {"integrante": r["integrante"], "kata": r["kata"], "tratamento": r["tratamento"],
             "tempo_min": round(r["tempo_min"], 4), "loc": r["loc"], "cc_media": r["cc_media"],
             "cc_total": r["cc_total"], "mi_medio": r["mi_medio"],
             "densidade_cc": round(r["densidade_cc"], 4),
             "tempo_cronometrado": r["fonte_tempo"] != DERIVED_SOURCE}
            for r in sorted(timed + derived, key=lambda r: (r["integrante"], r["kata"]))
        ],
    }

    output = root / "dados/rq4_resultados.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"RQ4: {len(timed)} trials cronometrados (+{len(derived)} derivados so na sensibilidade)")
    holm_p = results["primario"]["holm_global"]["pearson"]
    for field in STRUCTURE_FIELDS:
        stat = results["primario"]["global"][field]
        print(f"  tempo x {field:<13} n={stat['n']:>2} "
              f"Pearson r={stat['pearson_r']} (p={stat['pearson_p']}, Holm={holm_p.get(field)}, "
              f"IC95={stat['ic95_pearson']}) "
              f"Spearman rho={stat['spearman_rho']} (p={stat['spearman_p']})")
    print(f"-> {output.relative_to(root)}")


if __name__ == "__main__":
    main()
