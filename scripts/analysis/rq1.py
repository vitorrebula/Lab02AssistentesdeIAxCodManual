#!/usr/bin/env python3
"""Analisa RQ1 com pares por integrante e censura de 35 minutos explicita."""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, wilcoxon

TREATMENTS = ("com IA", "sem IA")


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    seen = set()
    for row in rows:
        key = (row["integrante"], row["kata"], row["tratamento"])
        if key in seen:
            raise ValueError(f"trial duplicado: {key}")
        seen.add(key)
        if row["tratamento"] not in TREATMENTS or row["censurado"] not in ("true", "false", ""):
            raise ValueError(f"tratamento/censura invalido: {key}")
        row["tempo_min"] = float(row["tempo_min"])
        if row["tempo_min"] < 0:
            raise ValueError(f"tempo negativo: {key}")
        if row["censurado"] == "true" and row["status"] == "censored_timebox":
            if not np.isclose(row["tempo_min"], 35, atol=.0001):
                raise ValueError(f"censura no time-box deve ocorrer em 35 min: {key}")
    return rows


def km_quantiles(rows):
    """Quartis KM: primeiro tempo em que S(t) <= 1-q; None se nao estimavel."""
    survival = 1.0
    quantiles = {}
    times = sorted({r["tempo_min"] for r in rows})
    for time in times:
        risk = sum(r["tempo_min"] >= time for r in rows)
        events = sum(r["tempo_min"] == time and r["censurado"] == "false" for r in rows)
        survival *= (1 - events / risk)
        for q in (.25, .5, .75):
            if q not in quantiles and survival <= 1 - q + 1e-12:
                quantiles[q] = time
    return [quantiles.get(q) for q in (.25, .5, .75)]


def descriptives(rows):
    results = {}
    for treatment in TREATMENTS:
        group = [r for r in rows if r["tratamento"] == treatment]
        censored = sum(r["censurado"] == "true" for r in group)
        if censored:
            q1, median, q3 = km_quantiles(group)
            method = "Kaplan-Meier (quartis em degraus; NA se nao estimavel)"
        else:
            q1, median, q3 = map(float, np.percentile([r["tempo_min"] for r in group], [25, 50, 75]))
            method = "percentis lineares (sem censura)"
        fmt = lambda value: round(value, 5) if value is not None else None
        results[treatment] = {"n": len(group), "censurados": censored, "q1": fmt(q1),
                              "mediana": fmt(median), "q3": fmt(q3),
                              "iqr": fmt(q3 - q1) if q1 is not None and q3 is not None else None,
                              "metodo": method}
    return results


def participant_pairs(rows):
    """Wilcoxon somente com todos os trials planejados observados em ambos tratamentos."""
    by_person = defaultdict(list)
    for row in rows:
        by_person[row["integrante"]].append(row)
    pairs = []
    omitted = {}
    for person, trials in sorted(by_person.items()):
        if any(r["censurado"] != "false" for r in trials):
            omitted[person] = "censura ou tempo nao observado"
            continue
        values = [[r["tempo_min"] for r in trials if r["tratamento"] == treatment]
                  for treatment in TREATMENTS]
        if len(values[0]) != 2 or len(values[1]) != 2:
            omitted[person] = "nao possui duas katas por tratamento no conjunto comum"
            continue
        pairs.append((person, float(np.median(values[0])), float(np.median(values[1]))))
    return pairs, omitted


def signed_rank(pairs):
    differences = [ai - manual for _, ai, manual in pairs]
    nonzero = [d for d in differences if not np.isclose(d, 0)]
    if len(nonzero) < 2:
        return None
    test = wilcoxon(nonzero, alternative="two-sided", method="exact")
    ranks = rankdata(np.abs(nonzero))
    effect = sum(rank if delta > 0 else -rank for rank, delta in zip(ranks, nonzero)) / sum(ranks)
    return {"W": float(test.statistic), "p": float(test.pvalue),
            "n_pares": len(nonzero), "r_rank_biserial": float(effect)}


def analyze(rows):
    core = [r for r in rows if r["no_plano_4_katas"] == "true"]
    eligible = [r for r in core if r["censurado"] != ""]
    unverified = [r for r in core if r["censurado"] == ""]
    person_kata = defaultdict(set)
    for row in core:
        person_kata[(row["integrante"], row["kata"])].add(row["tratamento"])
    same_kata_pairs = sum(len(v) == 2 for v in person_kata.values())
    pairs, omitted = participant_pairs(core)
    return {
        "n_core": len(core), "n_eligible": len(eligible),
        "n_unverified": len(unverified), "same_person_kata_pairs": same_kata_pairs,
        "descritivos": descriptives(eligible),
        "pares": [{"integrante": p, "ia_min": round(ai, 5), "manual_min": round(manual, 5),
                   "diferenca_ia_menos_manual": round(ai - manual, 5)} for p, ai, manual in pairs],
        "omitidos_wilcoxon": omitted, "wilcoxon": signed_rank(pairs),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("dados/consolidado.csv"))
    parser.add_argument("--output", type=Path, default=Path("dados/rq1_resultados.json"))
    args = parser.parse_args()
    result = analyze(read_rows(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
