#!/usr/bin/env python3
"""Reproduz a analise pareada da RQ3 a partir de results/static_metrics.csv."""

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, wilcoxon

METRICS = {
    "cc_avg": "CC media por funcao",
    "cc_per_100_loc": "CC total / 100 LOC",
    "duplication_pct": "Linhas duplicadas (%)",
    "loc": "LOC",
    "mi_avg": "MI (exploratorio)",
}


def load(path):
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    keys = [(r["participant"], r["kata"], r["treatment"]) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("trials duplicados no CSV")
    for row in rows:
        for field in ("cc_avg", "cc_total", "duplication_pct", "loc", "mi_avg"):
            row[field] = float(row[field])
        if row["loc"] <= 0 or row["treatment"] not in ("ai", "manual"):
            raise ValueError(f"trial invalido: {row}")
        row["cc_per_100_loc"] = 100 * row["cc_total"] / row["loc"]
    return rows


def summary(rows, metric, treatment):
    values = [r[metric] for r in rows if r["treatment"] == treatment]
    q1, median, q3 = np.percentile(values, [25, 50, 75])
    return len(values), q1, median, q3


def pairs(rows, metric):
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["participant"], row["treatment"])].append(row[metric])
    names = sorted({r["participant"] for r in rows})
    if any(not grouped[(name, condition)] for name in names for condition in ("manual", "ai")):
        raise ValueError("participante sem os dois tratamentos")
    return [(name, float(np.median(grouped[(name, "manual")])),
             float(np.median(grouped[(name, "ai")]))) for name in names]


def exact_test(paired):
    differences = [ai - manual for _, manual, ai in paired]
    if not any(differences):
        return None  # todos os pares empatados: Wilcoxon indefinido
    nonzero = [d for d in differences if d]
    if len(nonzero) < 2:
        return None
    result = wilcoxon(nonzero, alternative="two-sided", method="exact")
    ranks = rankdata(np.abs(nonzero))
    rank_sum = sum(ranks)
    rank_biserial = sum(rank if diff > 0 else -rank for rank, diff in zip(ranks, nonzero)) / rank_sum
    return float(result.statistic), float(result.pvalue), len(nonzero), float(rank_biserial)


def holm(pvalues):
    """Ajuste de Holm apenas para hipoteses testaveis da familia primaria."""
    ordered = sorted(pvalues, key=pvalues.get)
    output = {}
    previous = 0.0
    for index, metric in enumerate(ordered):
        previous = max(previous, min(1.0, (len(ordered) - index) * pvalues[metric]))
        output[metric] = previous
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("results/static_metrics.csv"))
    args = parser.parse_args()
    rows = load(args.input)
    print(f"Trials: {len(rows)}; participantes: {len(set(r['participant'] for r in rows))}")
    print("Quartis: percentis 25/50/75 com interpolacao linear (NumPy).")
    tests = {}
    for metric, label in METRICS.items():
        print(f"\n{label}")
        for treatment in ("manual", "ai"):
            n, q1, median, q3 = summary(rows, metric, treatment)
            print(f"  {treatment}: n={n}, mediana={median:.2f}, Q1={q1:.2f}, "
                  f"Q3={q3:.2f}, IQR={q3-q1:.2f}")
        paired = pairs(rows, metric)
        print("  pares (participante: manual -> IA; diferenca IA-manual):")
        for name, manual, ai in paired:
            print(f"    {name}: {manual:.2f} -> {ai:.2f}; {ai-manual:+.2f}")
        test = exact_test(paired)
        if test:
            statistic, p, n, effect = test
            print(f"  Wilcoxon exato bicaudal: W={statistic:.2f}, n={n}, p={p:.3f}, "
                  f"r_rb={effect:+.3f}")
            if metric in ("cc_avg", "duplication_pct", "loc"):
                tests[metric] = p
        else:
            print("  Wilcoxon nao aplicavel (diferencas nulas/pares insuficientes)")
    print("\nHolm (familia primaria testavel):", holm(tests))


if __name__ == "__main__":
    main()
