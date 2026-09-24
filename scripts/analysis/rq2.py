#!/usr/bin/env python3
"""Analisa RQ2: percentual de testes passando e falhas por tratamento."""

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

TREATMENTS = ("com IA", "sem IA")


def load(path):
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    seen = set()
    for row in rows:
        key = (row["integrante"], row["kata"], row["tratamento"])
        if key in seen:
            raise ValueError(f"trial duplicado: {key}")
        seen.add(key)
        if row["tratamento"] not in TREATMENTS:
            raise ValueError(f"tratamento desconhecido: {key}")
        passed = int(row["testes_passando"])
        total = int(row["testes_total"])
        if total <= 0 or not 0 <= passed <= total:
            raise ValueError(f"contagem de testes invalida: {key}")
        row["taxa_sucesso_pct"] = 100 * passed / total
        row["testes_falhando"] = total - passed
    return rows


def describe(rows):
    output = {}
    for treatment in TREATMENTS:
        group = [r for r in rows if r["tratamento"] == treatment]
        if not group:
            raise ValueError(f"tratamento sem trials: {treatment}")
        q1, median, q3 = map(float, np.percentile([r["taxa_sucesso_pct"] for r in group], [25, 50, 75]))
        output[treatment] = {
            "n_trials": len(group), "q1_pct": round(q1, 5),
            "mediana_pct": round(median, 5), "q3_pct": round(q3, 5),
            "iqr_pontos_percentuais": round(q3 - q1, 5),
            "falhas_absolutas_soma": sum(r["testes_falhando"] for r in group),
            "falhas_por_trial": [r["testes_falhando"] for r in group],
        }
    return output


def paired_test(rows):
    grouped = defaultdict(lambda: defaultdict(list))
    for row in rows:
        grouped[row["integrante"]][row["tratamento"]].append(row["taxa_sucesso_pct"])
    pairs = []
    for person, treatments in sorted(grouped.items()):
        if any(len(treatments[t]) != 2 for t in TREATMENTS):
            raise ValueError(f"{person}: esperado 2 trials por tratamento")
        ai = float(np.median(treatments["com IA"]))
        manual = float(np.median(treatments["sem IA"]))
        pairs.append({"integrante": person, "ia_pct": ai, "manual_pct": manual,
                      "diferenca_ia_menos_manual": ai - manual})
    deltas = [p["diferenca_ia_menos_manual"] for p in pairs]
    # Todas as diferenças zero: algumas versões do SciPy devolvem NaN ou
    # lançam ValueError. A distribuição exata degenerada tem W=0, p=1 por
    # convenção; não há postos não nulos nem evidência de efeito.
    degenerate = all(d == 0 for d in deltas)
    try:
        result = wilcoxon(deltas, zero_method="wilcox", alternative="two-sided", method="exact")
        statistic, pvalue = float(result.statistic), float(result.pvalue)
    except ValueError:
        if not degenerate:
            raise
        statistic, pvalue = 0.0, 1.0
    if degenerate and (math.isnan(pvalue) or math.isnan(statistic)):
        statistic, pvalue = 0.0, 1.0
    return pairs, {"W": statistic, "p": pvalue,
                   "n_pares": len(pairs), "n_diferencas_nao_nulas": sum(d != 0 for d in deltas),
                   "resultado_degenerado": degenerate,
                   "decisao_alpha_0_05": "nao_rejeitar_H0" if pvalue >= .05 else "rejeitar_H0"}


def analyze(rows):
    core = [r for r in rows if r["no_plano_4_katas"] == "true"]
    verified = [r for r in core if r["fonte_testes"] == "registro_trial"]
    posterior = [r for r in core if r["fonte_testes"] != "registro_trial"]
    # Não inferir resultado ao fim do time-box de teste executado posteriormente.
    pairs, test = paired_test(verified)
    return {"n_planejados": len(core), "n_verificados_no_trial": len(verified),
            "n_conferidos_posteriormente": len(posterior),
            "descritivos_verificados": describe(verified), "pares_por_integrante": pairs,
            "wilcoxon": test, "descritivos_posteriores": describe(posterior) if posterior else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("dados/consolidado.csv"))
    parser.add_argument("--output", type=Path, default=Path("dados/rq2_resultados.json"))
    args = parser.parse_args()
    result = analyze(load(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
