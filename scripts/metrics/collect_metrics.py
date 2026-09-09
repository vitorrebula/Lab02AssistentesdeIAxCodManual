#!/usr/bin/env python3
"""Coleta metricas estaticas (complexidade, LOC, duplicacao) de cada trial.

Varre trials/<participante>/<kata>_<ai|manual>/src, roda Radon (complexidade
ciclomatica, LOC, maintainability index) e jscpd (duplicacao de codigo) sobre
cada trial, e consolida o resultado em uma tabela CSV (uma linha por trial).
"""
import argparse
import csv
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze

TRIAL_DIR_RE = re.compile(r"^(?P<kata>.+)_(?P<treatment>ai|manual)$")

FIELDNAMES = [
    "participant", "kata", "treatment", "files", "loc", "sloc",
    "cc_avg", "cc_total", "mi_avg", "duplication_pct", "collected_at",
]


def find_trials(trials_root: Path):
    trials = []
    for participant_dir in sorted(p for p in trials_root.iterdir() if p.is_dir()):
        for trial_dir in sorted(t for t in participant_dir.iterdir() if t.is_dir()):
            match = TRIAL_DIR_RE.match(trial_dir.name)
            if not match:
                continue
            src_dir = trial_dir / "src"
            if not src_dir.is_dir():
                src_dir = trial_dir
            trials.append({
                "participant": participant_dir.name,
                "kata": match.group("kata"),
                "treatment": match.group("treatment"),
                "src_dir": src_dir,
            })
    return trials


def radon_metrics(src_dir: Path):
    py_files = [f for f in src_dir.rglob("*.py") if "test" not in f.stem.lower()]
    total_loc = total_sloc = 0
    complexities = []
    mi_scores = []
    for f in py_files:
        code = f.read_text(encoding="utf-8")
        raw = analyze(code)
        total_loc += raw.loc
        total_sloc += raw.sloc
        complexities.extend(block.complexity for block in cc_visit(code))
        mi_scores.append(mi_visit(code, True))
    return {
        "files": len(py_files),
        "loc": total_loc,
        "sloc": total_sloc,
        "cc_avg": round(sum(complexities) / len(complexities), 2) if complexities else 0.0,
        "cc_total": sum(complexities),
        "mi_avg": round(sum(mi_scores) / len(mi_scores), 2) if mi_scores else 0.0,
    }


def jscpd_duplication(src_dir: Path):
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [
            "npx", "--yes", "jscpd", str(src_dir),
            "--reporters", "json",
            "--output", tmp,
            "--min-lines", "5",
            "--min-tokens", "50",
            "--silent",
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except FileNotFoundError:
            print("aviso: npx/jscpd nao encontrado (instale Node.js); duplicacao=0.0", file=sys.stderr)
            return 0.0
        except subprocess.CalledProcessError as exc:
            print(f"aviso: jscpd falhou em {src_dir}: {exc.stderr.strip()}", file=sys.stderr)
            return 0.0
        report_path = Path(tmp) / "jscpd-report.json"
        if not report_path.exists():
            return 0.0
        report = json.loads(report_path.read_text(encoding="utf-8"))
        return round(report.get("statistics", {}).get("total", {}).get("percentage", 0.0), 2)


def collect(trials_root: Path):
    rows = []
    for trial in find_trials(trials_root):
        metrics = radon_metrics(trial["src_dir"])
        metrics["duplication_pct"] = jscpd_duplication(trial["src_dir"])
        rows.append({
            "participant": trial["participant"],
            "kata": trial["kata"],
            "treatment": trial["treatment"],
            "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            **metrics,
        })
    return rows


def write_csv(rows, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials-dir", default=Path("trials"), type=Path,
                         help="raiz com <participante>/<kata>_<ai|manual>/src (default: trials/)")
    parser.add_argument("--output", default=Path("results/static_metrics.csv"), type=Path,
                         help="arquivo CSV de saida (default: results/static_metrics.csv)")
    args = parser.parse_args()

    if not args.trials_dir.is_dir():
        sys.exit(f"diretorio de trials nao encontrado: {args.trials_dir}")

    rows = collect(args.trials_dir)
    if not rows:
        sys.exit(f"nenhum trial encontrado em {args.trials_dir} "
                  "(esperado <participante>/<kata>_<ai|manual>/)")

    write_csv(rows, args.output)
    print(f"{len(rows)} trial(s) processado(s) -> {args.output}")
    for row in rows:
        print(f"  {row['participant']:<14} {row['kata']:<12} {row['treatment']:<7} "
              f"LOC={row['loc']:<5} CC_avg={row['cc_avg']:<6} MI_avg={row['mi_avg']:<7} "
              f"dup%={row['duplication_pct']}")


if __name__ == "__main__":
    main()
