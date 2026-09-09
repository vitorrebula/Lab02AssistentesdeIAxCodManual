#!/usr/bin/env python3
"""Cronometra o time-to-green de cada trial e registra o tempo medido.

Marca o inicio do trial, verifica com pytest quando todos os testes de
aceitacao da kata passam (time-to-green) e grava o resultado em
results/timing.json (fonte da verdade) + results/timing.csv (para o
dashboard). Trials que estouram o time-box de 35 minutos sao registrados
como CENSURADOS em 35 min -- nunca descartados.
"""
import argparse
import csv
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import sleep

TIMEBOX_MIN = 35
TREATMENTS = ("ai", "manual")

STATE_PATH = Path("results/timing_state.json")
RECORDS_PATH = Path("results/timing.json")
CSV_PATH = Path("results/timing.csv")

STATUS_GREEN = "green"
STATUS_TIMEBOX = "censored_timebox"
STATUS_ABORTED = "censored_aborted"

FIELDNAMES = [
    "participant", "kata", "treatment", "started_at", "ended_at",
    "elapsed_s", "elapsed_min", "time_to_green_s", "time_to_green_min",
    "censored", "event", "status", "timebox_s", "tests_passed",
    "tests_failed", "notes", "recorded_at",
]

PYTEST_COUNT_RE = re.compile(r"(\d+) (passed|failed|error|errors)")


# --------------------------------------------------------------------------- #
# utilitarios
# --------------------------------------------------------------------------- #
def now():
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(dt):
    return dt.isoformat(timespec="seconds")


def parse_iso(text):
    return datetime.fromisoformat(text)


def fmt_duration(seconds):
    seconds = int(round(seconds))
    return f"{seconds // 60}m{seconds % 60:02d}s"


def parse_elapsed(text):
    """Aceita 'MM:SS', 'HH:MM:SS' ou minutos decimais ('12.5'). Retorna segundos."""
    if ":" in text:
        parts = [float(p) for p in text.split(":")]
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        raise argparse.ArgumentTypeError(f"formato de tempo invalido: {text}")
    return float(text) * 60


def load_json(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def trial_id(participant, kata, treatment):
    return f"{participant}/{kata}_{treatment}"


def trial_paths(trials_root, participant, kata, treatment, tests_dir=None):
    root = trials_root / participant / f"{kata}_{treatment}"
    return root, (tests_dir if tests_dir else root / "tests")


# --------------------------------------------------------------------------- #
# resolucao do trial ativo
# --------------------------------------------------------------------------- #
def resolve_active(state, args, required=True):
    """Devolve (tid, entry). Sem flags, usa o unico trial ativo, se houver."""
    active = state.get("active", {})
    if args.participant and args.kata and args.treatment:
        tid = trial_id(args.participant, args.kata, args.treatment)
    elif not active:
        if required:
            sys.exit("nenhum trial em andamento (rode 'start' primeiro)")
        return None, None
    elif len(active) == 1:
        tid = next(iter(active))
    else:
        sys.exit("mais de um trial em andamento; informe --participant/--kata/--treatment:\n  "
                 + "\n  ".join(sorted(active)))
    entry = active.get(tid)
    if entry is None and required:
        sys.exit(f"trial '{tid}' nao esta em andamento (rode 'start' primeiro)")
    return tid, entry


# --------------------------------------------------------------------------- #
# execucao dos testes de aceitacao
# --------------------------------------------------------------------------- #
def run_pytest(trial_root, tests_dir):
    """Roda pytest nos testes de aceitacao. Retorna dict com green/passed/failed."""
    if not tests_dir.is_dir():
        return {"green": False, "passed": 0, "failed": 0,
                "detail": f"diretorio de testes nao encontrado: {tests_dir}"}

    env = dict(os.environ)
    extra = [str(trial_root.resolve()), str((trial_root / "src").resolve())]
    if env.get("PYTHONPATH"):
        extra.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(extra)

    cmd = [sys.executable, "-m", "pytest", str(tests_dir.resolve()),
           "-q", "--no-header", "-p", "no:cacheprovider"]
    proc = subprocess.run(cmd, cwd=trial_root, env=env, capture_output=True, text=True)

    counts = {"passed": 0, "failed": 0}
    for value, label in PYTEST_COUNT_RE.findall(proc.stdout):
        key = "passed" if label == "passed" else "failed"
        counts[key] += int(value)

    detail = ""
    if proc.returncode == 5:
        detail = "pytest nao coletou nenhum teste"
    elif proc.returncode not in (0, 1):
        detail = f"pytest terminou com codigo {proc.returncode}"

    return {
        "green": proc.returncode == 0 and counts["passed"] > 0,
        "passed": counts["passed"],
        "failed": counts["failed"],
        "detail": detail,
    }


# --------------------------------------------------------------------------- #
# gravacao do resultado
# --------------------------------------------------------------------------- #
def build_record(entry, ended_at, elapsed_s, status, tests, notes):
    """Monta a linha do trial. Censurados fixam time_to_green no time-box."""
    timebox_s = entry["timebox_s"]
    censored = status != STATUS_GREEN
    if status == STATUS_TIMEBOX:
        time_to_green_s = float(timebox_s)
    else:
        time_to_green_s = float(min(elapsed_s, timebox_s))
    return {
        "participant": entry["participant"],
        "kata": entry["kata"],
        "treatment": entry["treatment"],
        "started_at": entry["started_at"],
        "ended_at": iso(ended_at),
        "elapsed_s": round(elapsed_s, 1),
        "elapsed_min": round(elapsed_s / 60, 2),
        "time_to_green_s": round(time_to_green_s, 1),
        "time_to_green_min": round(time_to_green_s / 60, 2),
        "censored": censored,
        "event": 0 if censored else 1,
        "status": status,
        "timebox_s": timebox_s,
        "tests_passed": tests["passed"],
        "tests_failed": tests["failed"],
        "notes": notes or "",
        "recorded_at": iso(now()),
    }


def append_record(record, records_path, csv_path):
    """Grava o trial no JSON (substituindo repeticao do mesmo trial) e regera o CSV."""
    def is_same_trial(r):
        return (r["participant"] == record["participant"]
                and r["kata"] == record["kata"]
                and r["treatment"] == record["treatment"])

    records = [r for r in load_json(records_path, []) if not is_same_trial(r)]
    records.append(record)
    records.sort(key=lambda r: (r["participant"], r["kata"], r["treatment"]))
    save_json(records_path, records)
    write_csv(records, csv_path)
    return records


def write_csv(records, csv_path):
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            # 'event' foi adicionado depois; deriva de 'censored' em registros antigos
            row = {"event": 0 if record["censored"] else 1, **record}
            writer.writerow(row)


def finish(state, tid, entry, elapsed_s, status, tests, args):
    record = build_record(entry, now(), elapsed_s, status, tests, args.notes)
    state.get("active", {}).pop(tid, None)
    save_json(args.state, state)
    append_record(record, args.records, args.csv)

    label = "VERDE" if status == STATUS_GREEN else "CENSURADO"
    print(f"[{label}] {tid}: decorrido {fmt_duration(elapsed_s)} | "
          f"time_to_green={fmt_duration(record['time_to_green_s'])} | status={status}")
    if status == STATUS_TIMEBOX:
        print(f"  time-box de {entry['timebox_s'] // 60} min estourado -> "
              "registrado como censurado (nao descartado)")
    print(f"  testes: {tests['passed']} passaram, {tests['failed']} falharam")
    print(f"  gravado em {args.records} e {args.csv}")
    return record


# --------------------------------------------------------------------------- #
# comandos
# --------------------------------------------------------------------------- #
def cmd_start(args):
    state = load_json(args.state, {"active": {}})
    state.setdefault("active", {})
    tid = trial_id(args.participant, args.kata, args.treatment)
    if tid in state["active"] and not args.restart:
        started = state["active"][tid]["started_at"]
        sys.exit(f"trial '{tid}' ja esta em andamento (inicio {started}); "
                 "use --restart para reiniciar o cronometro")

    trial_root, tests_dir = trial_paths(args.trials_dir, args.participant, args.kata,
                                        args.treatment, args.tests_dir)
    if not tests_dir.is_dir():
        print(f"aviso: {tests_dir} nao existe ainda; crie os testes de aceitacao "
              "antes de verificar o time-to-green", file=sys.stderr)

    state["active"][tid] = {
        "participant": args.participant,
        "kata": args.kata,
        "treatment": args.treatment,
        "started_at": iso(now()),
        "timebox_s": int(args.timebox * 60),
        "trial_root": str(trial_root),
        "tests_dir": str(tests_dir),
    }
    save_json(args.state, state)
    print(f"cronometro iniciado: {tid} | inicio {state['active'][tid]['started_at']} | "
          f"time-box {args.timebox} min")
    print(f"  ao terminar: python {Path(__file__).name} green")


def cmd_status(args):
    state = load_json(args.state, {"active": {}})
    active = state.get("active", {})
    if not active:
        print("nenhum trial em andamento")
    for tid, entry in sorted(active.items()):
        elapsed = (now() - parse_iso(entry["started_at"])).total_seconds()
        remaining = entry["timebox_s"] - elapsed
        flag = "TIME-BOX ESTOURADO" if remaining <= 0 else f"restam {fmt_duration(remaining)}"
        print(f"em andamento: {tid} | decorrido {fmt_duration(elapsed)} | {flag}")

    records = load_json(args.records, [])
    if records:
        greens = sum(1 for r in records if not r["censored"])
        print(f"registrados: {len(records)} trial(s) -- {greens} verde(s), "
              f"{len(records) - greens} censurado(s) ({args.records})")


def cmd_green(args):
    state = load_json(args.state, {"active": {}})
    tid, entry = resolve_active(state, args)
    elapsed = (now() - parse_iso(entry["started_at"])).total_seconds()

    if args.no_verify:
        tests = {"green": True, "passed": 0, "failed": 0, "detail": "verificacao pulada"}
    else:
        tests = run_pytest(Path(entry["trial_root"]), Path(entry["tests_dir"]))
        if tests["detail"]:
            print(f"aviso: {tests['detail']}", file=sys.stderr)

    over_timebox = elapsed >= entry["timebox_s"]
    if tests["green"] and not over_timebox:
        status = STATUS_GREEN
    elif over_timebox:
        status = STATUS_TIMEBOX
    elif args.force_censor:
        status = STATUS_ABORTED
    else:
        print(f"testes ainda nao estao verdes ({tests['passed']} passaram, "
              f"{tests['failed']} falharam) e faltam "
              f"{fmt_duration(entry['timebox_s'] - elapsed)} de time-box.")
        sys.exit("cronometro mantido em andamento; use --abort para encerrar como censurado")
    finish(state, tid, entry, elapsed, status, tests, args)


def cmd_watch(args):
    state = load_json(args.state, {"active": {}})
    tid, entry = resolve_active(state, args, required=False)
    if entry is None:
        if not (args.participant and args.kata and args.treatment):
            sys.exit("nenhum trial em andamento; informe --participant/--kata/--treatment")
        cmd_start(args)
        state = load_json(args.state, {"active": {}})
        tid, entry = resolve_active(state, args)

    trial_root, tests_dir = Path(entry["trial_root"]), Path(entry["tests_dir"])
    print(f"verificando '{tid}' a cada {args.interval}s ate ficar verde ou estourar o "
          "time-box (Ctrl+C interrompe sem gravar)")
    while True:
        elapsed = (now() - parse_iso(entry["started_at"])).total_seconds()
        if elapsed >= entry["timebox_s"]:
            tests = run_pytest(trial_root, tests_dir)
            finish(state, tid, entry, elapsed, STATUS_TIMEBOX, tests, args)
            return
        tests = run_pytest(trial_root, tests_dir)
        if tests["green"]:
            finish(state, tid, entry, elapsed, STATUS_GREEN, tests, args)
            return
        remaining = entry["timebox_s"] - elapsed
        print(f"  {fmt_duration(elapsed)} decorridos | {tests['passed']} passaram, "
              f"{tests['failed']} falharam | restam {fmt_duration(remaining)}")
        sleep(max(1, min(args.interval, remaining)))


def cmd_record(args):
    """Registro manual (fallback de planilha/cronometro externo)."""
    entry = {
        "participant": args.participant,
        "kata": args.kata,
        "treatment": args.treatment,
        "started_at": args.started_at or "",
        "timebox_s": int(args.timebox * 60),
    }
    if args.status:
        status = args.status
    elif args.elapsed >= entry["timebox_s"]:
        status = STATUS_TIMEBOX
    else:
        status = STATUS_GREEN
    tests = {"passed": args.tests_passed, "failed": args.tests_failed}
    record = build_record(entry, now(), args.elapsed, status, tests, args.notes)
    append_record(record, args.records, args.csv)
    print(f"registrado {trial_id(args.participant, args.kata, args.treatment)}: "
          f"time_to_green={fmt_duration(record['time_to_green_s'])} status={status}")
    print(f"  gravado em {args.records} e {args.csv}")


def cmd_export(args):
    records = load_json(args.records, [])
    if not records:
        sys.exit(f"nenhum trial registrado em {args.records}")
    write_csv(records, args.csv)
    print(f"{len(records)} trial(s) -> {args.csv}")
    for r in records:
        mark = "censurado" if r["censored"] else "verde"
        print(f"  {r['participant']:<14} {r['kata']:<12} {r['treatment']:<7} "
              f"{fmt_duration(r['time_to_green_s']):<8} {mark}")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def add_trial_flags(parser, required=False):
    parser.add_argument("--participant", required=required, help="integrante que executa o trial")
    parser.add_argument("--kata", required=required, help="identificador da kata (ex.: kata2)")
    parser.add_argument("--treatment", required=required, choices=TREATMENTS,
                        help="tratamento: 'ai' ou 'manual'")


def add_common_flags(parser):
    parser.add_argument("--trials-dir", default=Path("trials"), type=Path,
                        help="raiz dos trials (default: trials/)")
    parser.add_argument("--tests-dir", default=None, type=Path,
                        help="sobrescreve o diretorio de testes de aceitacao do trial")
    parser.add_argument("--timebox", default=TIMEBOX_MIN, type=float,
                        help=f"time-box em minutos (default: {TIMEBOX_MIN})")
    parser.add_argument("--state", default=STATE_PATH, type=Path,
                        help=f"arquivo de trials em andamento (default: {STATE_PATH})")
    parser.add_argument("--records", default=RECORDS_PATH, type=Path,
                        help=f"JSON com os tempos registrados (default: {RECORDS_PATH})")
    parser.add_argument("--csv", default=CSV_PATH, type=Path,
                        help=f"CSV consolidado para o dashboard (default: {CSV_PATH})")
    parser.add_argument("--notes", default="", help="observacao livre sobre o trial")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    subs = parser.add_subparsers(dest="command", required=True)

    p_start = subs.add_parser("start", help="inicia o cronometro de um trial")
    add_trial_flags(p_start, required=True)
    add_common_flags(p_start)
    p_start.add_argument("--restart", action="store_true",
                         help="reinicia o cronometro de um trial ja em andamento")
    p_start.set_defaults(func=cmd_start)

    p_status = subs.add_parser("status", help="mostra trials em andamento e registrados")
    add_trial_flags(p_status)
    add_common_flags(p_status)
    p_status.set_defaults(func=cmd_status)

    p_green = subs.add_parser("green", help="encerra o trial verificando os testes com pytest")
    add_trial_flags(p_green)
    add_common_flags(p_green)
    p_green.add_argument("--no-verify", action="store_true",
                         help="grava como verde sem rodar pytest (use so se ja validou na mao)")
    p_green.add_argument("--abort", dest="force_censor", action="store_true",
                         help="encerra antes do time-box como censurado (trial abandonado)")
    p_green.set_defaults(func=cmd_green)

    p_watch = subs.add_parser("watch", help="roda pytest em intervalos ate verde ou time-box")
    add_trial_flags(p_watch)
    add_common_flags(p_watch)
    p_watch.add_argument("--interval", default=15, type=int,
                         help="intervalo entre verificacoes, em segundos (default: 15)")
    p_watch.add_argument("--restart", action="store_true",
                         help="reinicia o cronometro se o trial ja estiver em andamento")
    p_watch.set_defaults(func=cmd_watch)

    p_record = subs.add_parser("record", help="registra um tempo medido fora do script")
    add_trial_flags(p_record, required=True)
    add_common_flags(p_record)
    p_record.add_argument("--elapsed", required=True, type=parse_elapsed,
                          help="tempo decorrido: 'MM:SS', 'HH:MM:SS' ou minutos decimais")
    p_record.add_argument("--status", choices=(STATUS_GREEN, STATUS_TIMEBOX, STATUS_ABORTED),
                          help="default: green, ou censored_timebox se estourou o time-box")
    p_record.add_argument("--started-at", help="timestamp ISO do inicio (opcional)")
    p_record.add_argument("--tests-passed", default=0, type=int,
                          help="nº de testes de aceitacao que passaram")
    p_record.add_argument("--tests-failed", default=0, type=int,
                          help="nº de testes de aceitacao que falharam")
    p_record.set_defaults(func=cmd_record)

    p_export = subs.add_parser("export", help="regera o CSV a partir do JSON de registros")
    add_common_flags(p_export)
    p_export.set_defaults(func=cmd_export)

    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        sys.exit("\ninterrompido; o cronometro segue em andamento (veja 'status')")


if __name__ == "__main__":
    main()
