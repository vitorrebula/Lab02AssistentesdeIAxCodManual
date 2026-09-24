#!/usr/bin/env python3
"""Consolida a S02 sem converter registros derivados em medições observadas."""

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

FIELDS = [
    "integrante", "kata", "tratamento", "tempo_min", "censurado",
    "testes_passando", "testes_total", "status", "fonte_tempo",
    "fonte_testes", "no_plano_4_katas", "cc_media", "cc_total",
    "duplicacao_pct", "loc", "mi_medio", "cobertura_pct",
]
OUTLIER_FIELDS = [
    "integrante", "kata", "tratamento", "campo", "valor", "limite_inferior",
    "limite_superior", "criterio", "decisao", "justificativa",
]


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def key(record):
    return record["participant"], record["kata"], record["treatment"]


def unique(rows, label):
    result = {}
    for row in rows:
        k = key(row)
        if k in result:
            raise ValueError(f"{label}: trial duplicado {k}")
        result[k] = row
    return result


def number(value, field, trial):
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{trial}: {field} ausente ou invalido") from None


def percentile(values, fraction):
    """Percentil linear, equivalente a numpy.percentile(method='linear')."""
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (position - lower) * (ordered[upper] - ordered[lower])


def consolidate(root):
    timing = unique(json.loads((root / "results/timing.json").read_text(encoding="utf-8")), "timing.json")
    timing_csv = unique(read_csv(root / "results/timing.csv"), "timing.csv")
    metrics = unique(read_csv(root / "results/static_metrics.csv"), "static_metrics.csv")
    trials = {}
    for src in (root / "trials").glob("*/*/src"):
        treatment = src.parent.name.rsplit("_", 1)
        if len(treatment) == 2 and treatment[1] in ("ai", "manual"):
            trials[(src.parent.parent.name, *treatment)] = src
    if set(timing) != set(timing_csv) or set(timing) != set(metrics) or set(timing) != set(trials):
        raise ValueError("chaves divergentes entre timing.json, timing.csv, metricas e diretorios trials")

    participants = sorted({k[0] for k in timing})
    common = set.intersection(*({k[1] for k in timing if k[0] == person} for person in participants))
    if len(common) != 4:
        raise ValueError(f"esperadas quatro katas comuns; encontradas {sorted(common)}")
    rows = []
    for k in sorted(timing):
        record, raw, metric = timing[k], timing_csv[k], metrics[k]
        if (record["status"] != raw["status"]
                or str(record.get("elapsed_s") or "") != str(raw.get("elapsed_s") or "")
                or str(record["tests_passed"]) != raw["tests_passed"]
                or str(record["tests_failed"]) != raw["tests_failed"]
                or str(record["timebox_s"]) != raw["timebox_s"]
                or str(record.get("time_to_green_s") or "") != str(raw.get("time_to_green_s") or "")):
            raise ValueError(f"timing JSON/CSV divergentes em {k}")
        count_passed = int(record["tests_passed"])
        count_failed = int(record["tests_failed"])
        if count_passed < 0 or count_failed < 0 or not count_passed + count_failed:
            raise ValueError(f"contagem de testes invalida em {k}")
        status = record["status"]
        timebox = number(record["timebox_s"], "timebox_s", k)
        if timebox != 2100:
            raise ValueError(f"time-box diferente de 35 minutos em {k}")
        if status == "green":
            seconds = number(record["time_to_green_s"], "time_to_green_s", k)
            censored, source = "false", "cronometro_ou_reconstituido"
            if seconds > timebox:
                raise ValueError(f"tempo verde excede time-box em {k}")
        elif status == "censored_timebox":
            seconds = timebox
            censored, source = "true", "cronometro_censurado_35min"
        elif status == "censored_aborted":
            seconds = number(record["elapsed_s"], "elapsed_s", k)
            censored, source = "true", "cronometro_censurado_aborto"
        elif status in ("derived_from_reference", "self_reported", "estimated"):
            seconds = number(record["elapsed_s"], "elapsed_s", k)
            censored, source = "", "derivado_ou_autodeclarado"
        else:
            raise ValueError(f"status desconhecido {status!r} em {k}")
        if seconds < 0:
            raise ValueError(f"tempo negativo em {k}")
        notes = record.get("notes", "").lower()
        if status == "green" and ("re-registro" in notes or "reconstitu" in notes):
            source = "reconstituido"
        for field in ("cc_avg", "cc_total", "duplication_pct", "loc", "mi_avg", "coverage_pct"):
            number(metric[field], field, k)
        rows.append({
            "integrante": k[0], "kata": k[1], "tratamento": "com IA" if k[2] == "ai" else "sem IA",
            "tempo_min": f"{seconds / 60:.4f}", "censurado": censored,
            "testes_passando": count_passed, "testes_total": count_passed + count_failed,
            "status": status, "fonte_tempo": source,
            "fonte_testes": "verificacao_posterior" if source == "derivado_ou_autodeclarado" else "registro_trial",
            "no_plano_4_katas": "true" if k[1] in common else "false",
            "cc_media": metric["cc_avg"], "cc_total": metric["cc_total"],
            "duplicacao_pct": metric["duplication_pct"], "loc": metric["loc"],
            "mi_medio": metric["mi_avg"], "cobertura_pct": metric["coverage_pct"],
        })

    for person in participants:
        planned = [r for r in rows if r["integrante"] == person and r["no_plano_4_katas"] == "true"]
        counts = Counter(r["tratamento"] for r in planned)
        if len(planned) != 4 or counts != {"com IA": 2, "sem IA": 2}:
            raise ValueError(f"cobertura desbalanceada para {person}: {counts}")
    return rows, timing, common, participants


def review(rows, timing):
    flagged = []
    for treatment in ("com IA", "sem IA"):
        eligible = [r for r in rows if r["tratamento"] == treatment and r["censurado"] == "false"
                    and r["fonte_tempo"] != "derivado_ou_autodeclarado"]
        if len(eligible) < 4:
            continue
        values = [float(r["tempo_min"]) for r in eligible]
        q1, q3 = percentile(values, .25), percentile(values, .75)
        low, high = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
        for row in eligible:
            value = float(row["tempo_min"])
            if low <= value <= high:
                continue
            flagged.append({
                "integrante": row["integrante"], "kata": row["kata"], "tratamento": treatment,
                "campo": "tempo_min", "valor": row["tempo_min"],
                "limite_inferior": f"{low:.4f}", "limite_superior": f"{high:.4f}",
                "criterio": "Tukey 1.5xIQR por tratamento; apenas tempos nao derivados",
                "decisao": "manter_sinalizado",
                "justificativa": "Amostra pequena e katas distintas; nao excluir somente pelo criterio estatistico.",
            })
    for row in rows:
        k = (row["integrante"], row["kata"], "ai" if row["tratamento"] == "com IA" else "manual")
        original = timing[k]
        if not original.get("started_at") or not original.get("ended_at"):
            continue
        actual = (datetime.fromisoformat(original["ended_at"]) - datetime.fromisoformat(original["started_at"])).total_seconds()
        elapsed = float(original["elapsed_s"])
        if row["fonte_tempo"] == "derivado_ou_autodeclarado" or abs(actual - elapsed) <= max(5, elapsed * .01):
            continue
        flagged.append({
            "integrante": row["integrante"], "kata": row["kata"], "tratamento": row["tratamento"],
            "campo": "duracao_vs_horarios_s", "valor": f"{elapsed:g} vs {actual:g}",
            "limite_inferior": "", "limite_superior": "",
            "criterio": "diferenca > max(5 s, 1% do tempo registrado)",
            "decisao": "manter_sinalizado_verificar_origem",
            "justificativa": "Divergencia dos horarios brutos; preservar elapsed_s e solicitar verificacao antes da analise temporal.",
        })
    return sorted(flagged, key=lambda r: (r["integrante"], r["kata"], r["campo"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    rows, timing, common, participants = consolidate(root)
    outliers = review(rows, timing)
    write_csv(root / "dados/consolidado.csv", FIELDS, rows)
    write_csv(root / "dados/outliers.csv", OUTLIER_FIELDS, outliers)
    print(f"{len(rows)} trials; {len(participants)} integrantes x 4 katas comuns "
          f"({', '.join(sorted(common))}) = {len(participants)*4} planejados; "
          f"{len(rows)-len(participants)*4} extras; {len(outliers)} sinalizacoes")
    print(f"Censurados 35 min: {sum(r['status']=='censored_timebox' for r in rows)}; "
          f"censura desconhecida: {sum(not r['censurado'] for r in rows)}")


if __name__ == "__main__":
    main()
