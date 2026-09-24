#!/usr/bin/env python3
"""Pipeline de importacao e consolidacao dos dados para o dashboard (Issue #48).

Le os artefatos de dados do repositorio e devolve um DataFrame unico (tidy,
uma linha por trial) pronto para plotagem e para os testes estatisticos:

    consolidado (#44, se existir)  ->  tempo + censura + testes
    results/timing.json            ->  tempo, censura, contagem de testes (RQ1/RQ2)
    results/static_metrics.csv     ->  LOC, complexidade, duplicacao, MI (RQ3)

A chave de juncao e a tripla (participant, kata, treatment), conforme
docs/desenho-experimento.md secao 4.2. Todos os caminhos sao relativos a raiz
do repositorio (inferida a partir deste arquivo), sem nenhum dado embutido no
codigo: se um arquivo de entrada nao existir, a coluna correspondente fica
vazia em vez de ser inventada.

Uso como script:

    python scripts/dashboard/load_data.py                      # inspeciona
    python scripts/dashboard/load_data.py --output results/dashboard_dataset.csv

Uso como modulo (notebook do dashboard):

    from load_data import build_dataset, describe_dataset
    df = build_dataset()
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

# Raiz do repositorio: scripts/dashboard/load_data.py -> parents[2]
REPO_ROOT = Path(__file__).resolve().parents[2]

# Caminhos default, sempre relativos a raiz do repo (reprodutibilidade).
TIMING_JSON = Path("results/timing.json")
TIMING_CSV = Path("results/timing.csv")
STATIC_METRICS_CSV = Path("results/static_metrics.csv")

# Saida da Issue #44 (dataset consolidado). Ainda nao existe no repo; quando
# existir, passa a ser a fonte preferencial para tempo/censura/testes.
CONSOLIDATED_CANDIDATES = (
    Path("dados/consolidado.csv"),
    Path("data/consolidado.csv"),
    Path("results/consolidado.csv"),
)

KEYS = ["participant", "kata", "treatment"]
TREATMENTS = ["manual", "ai"]  # ordem usada em eixos e legendas dos graficos
TIMEBOX_S_DEFAULT = 2100  # 35 min, docs/desenho-experimento.md secao 4.3

# Nomes alternativos (pt-BR, como pedido nos critetios da #44) -> nome canonico.
COLUMN_ALIASES = {
    "integrante": "participant",
    "participante": "participant",
    "tratamento": "treatment",
    "tempo": "time_to_green_min",
    "tempo_min": "time_to_green_min",
    "tempo_s": "time_to_green_s",
    "tempo_segundos": "time_to_green_s",
    "censurado": "censored",
    "evento": "event",
    "testes_passando": "tests_passed",
    "testes_falhando": "tests_failed",
    "testes_total": "tests_total",
    "total_testes": "tests_total",
    "sucesso": "success",
    # metricas estaticas como saem do consolidado da #44 (pt-BR)
    "cc_media": "cc_avg",
    "cc_medio": "cc_avg",
    "duplicacao_pct": "duplication_pct",
    "mi_medio": "mi_avg",
    "observacoes": "notes",
    "notas": "notes",
}

TREATMENT_ALIASES = {
    "ai": "ai",
    "com_ia": "ai",
    "com ia": "ai",
    "ia": "ai",
    "manual": "manual",
    "sem_ia": "manual",
    "sem ia": "manual",
}

# Tipos do DataFrame final. Contagens usam Int64 (nullable) porque a juncao
# externa pode deixar celulas vazias quando um trial esta em so uma das fontes.
DTYPES = {
    "trial_id": "string",
    "participant": "string",
    "kata": "string",
    "treatment": "category",
    "time_to_green_s": "float64",
    "time_to_green_min": "float64",
    "elapsed_s": "float64",
    "elapsed_min": "float64",
    "censored": "boolean",
    "event": "Int64",
    "status": "string",
    "timebox_s": "float64",
    "timebox_min": "float64",
    "tests_passed": "Int64",
    "tests_failed": "Int64",
    "tests_total": "Int64",
    "pct_tests_passing": "float64",
    "success": "boolean",
    "files": "Int64",
    "loc": "Int64",
    "sloc": "Int64",
    "cc_avg": "float64",
    "cc_total": "float64",
    "mi_avg": "float64",
    "duplication_pct": "float64",
    "started_at": "datetime64[ns, UTC]",
    "ended_at": "datetime64[ns, UTC]",
    "recorded_at": "datetime64[ns, UTC]",
    "collected_at": "datetime64[ns, UTC]",
    "has_timing": "boolean",
    "has_metrics": "boolean",
    "notes": "string",
}

COLUMN_ORDER = list(DTYPES)

DATETIME_COLUMNS = [c for c, t in DTYPES.items() if str(t).startswith("datetime64")]

# Dicionario de dados (colunas do DataFrame final). Serve de documentacao viva:
# e impresso pelo CLI (--dictionary) e reaproveitado no README e no notebook.
DATA_DICTIONARY = {
    "trial_id": ("identificacao", "chave legivel do trial: <participant>/<kata>_<treatment>"),
    "participant": ("identificacao", "integrante que executou o trial"),
    "kata": ("identificacao", "identificador da kata (kata1..kata6)"),
    "treatment": ("identificacao", "fator do experimento: 'manual' ou 'ai' (categoria ordenada manual < ai)"),
    "time_to_green_s": ("RQ1 tempo", "tempo ate o verde em segundos, censurado no time-box"),
    "time_to_green_min": ("RQ1 tempo", "idem em minutos; variavel dependente primaria de RQ1"),
    "elapsed_s": ("RQ1 tempo", "tempo bruto medido, sem cortar no time-box"),
    "elapsed_min": ("RQ1 tempo", "idem em minutos"),
    "censored": ("RQ1 tempo", "True se o verde nao foi observado dentro do time-box"),
    "event": ("RQ1 tempo", "indicador de sobrevivencia: 1 = verde observado, 0 = censurado"),
    "status": ("RQ1 tempo", "'green', 'censored_timebox' ou 'censored_aborted'"),
    "timebox_s": ("RQ1 tempo", "time-box aplicado ao trial, em segundos (2100 = 35 min)"),
    "timebox_min": ("RQ1 tempo", "idem em minutos"),
    "tests_passed": ("RQ2 defeitos", "testes de aceitacao que passaram no fechamento do trial"),
    "tests_failed": ("RQ2 defeitos", "testes de aceitacao que falharam no fechamento do trial"),
    "tests_total": ("RQ2 defeitos", "tests_passed + tests_failed"),
    "pct_tests_passing": ("RQ2 defeitos", "100 * tests_passed / tests_total; medida continua secundaria"),
    "success": ("RQ2 defeitos", "True se o trial atingiu o verde dentro do time-box; base da taxa de sucesso (teste primario de RQ2)"),
    "files": ("RQ3 estrutura", "numero de arquivos .py de solucao analisados"),
    "loc": ("RQ3 estrutura", "linhas de codigo da solucao (H3c)"),
    "sloc": ("RQ3 estrutura", "linhas de codigo sem brancos/comentarios"),
    "cc_avg": ("RQ3 estrutura", "complexidade ciclomatica media por funcao (H3a)"),
    "cc_total": ("RQ3 estrutura", "complexidade ciclomatica total do trial (exploratoria)"),
    "mi_avg": ("RQ3 estrutura", "Maintainability Index medio (exploratoria)"),
    "duplication_pct": ("RQ3 estrutura", "percentual de linhas duplicadas (H3b)"),
    "started_at": ("metadado", "inicio do cronometro (UTC)"),
    "ended_at": ("metadado", "fim do cronometro (UTC)"),
    "recorded_at": ("metadado", "gravacao do registro de tempo (UTC)"),
    "collected_at": ("metadado", "coleta das metricas estaticas (UTC)"),
    "has_timing": ("metadado", "True se o trial tem registro de tempo"),
    "has_metrics": ("metadado", "True se o trial tem metricas estaticas"),
    "notes": ("metadado", "observacao livre registrada no trial (desvios, re-registros, etc.)"),
}


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #
def _resolve(path: Path | str, repo_root: Path) -> Path:
    """Resolve um caminho relativo contra a raiz do repo (absoluto passa direto)."""
    path = Path(path)
    return path if path.is_absolute() else repo_root / path


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {}
    for col in df.columns:
        key = str(col).strip().lower().replace(" ", "_")
        renamed[col] = COLUMN_ALIASES.get(key, key)
    return df.rename(columns=renamed)


def _normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza a tripla de juncao: minusculas, sem espacos, tratamento canonico."""
    for col in ("participant", "kata"):
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip().str.lower()
    if "treatment" in df.columns:
        treatment = df["treatment"].astype("string").str.strip().str.lower()
        df["treatment"] = treatment.map(lambda v: TREATMENT_ALIASES.get(v, v) if pd.notna(v) else v)
    return df


def _to_bool(series: pd.Series) -> pd.Series:
    """Converte 'True'/'true'/'1'/1/True -> boolean nullable."""
    if series.dtype == "bool" or str(series.dtype) == "boolean":
        return series.astype("boolean")
    mapping = {
        "true": True, "1": True, "1.0": True, "yes": True, "sim": True,
        "false": False, "0": False, "0.0": False, "no": False, "nao": False, "": pd.NA,
    }
    return (series.astype("string").str.strip().str.lower().map(mapping)).astype("boolean")


def _merge_prefer_left(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
    """Juncao externa pela tripla; em colunas presentes nos dois lados, o valor
    da esquerda (fonte preferencial) vence e o da direita so preenche vazios."""
    merged = left.merge(right, on=KEYS, how="outer", suffixes=("", "__right"))
    for col in [c for c in merged.columns if c.endswith("__right")]:
        base = col[: -len("__right")]
        merged[base] = merged[base].where(merged[base].notna(), merged[col])
        merged = merged.drop(columns=[col])
    return merged


# --------------------------------------------------------------------------- #
# Carga das fontes                                                             #
# --------------------------------------------------------------------------- #
def load_timing(path: Path | str | None = None, repo_root: Path = REPO_ROOT) -> pd.DataFrame:
    """Carrega os registros de tempo (Issue #4).

    Usa results/timing.json, que o script de cronometragem trata como fonte da
    verdade; cai para results/timing.csv se o JSON nao existir.
    """
    if path is not None:
        source = _resolve(path, repo_root)
        frame = (pd.read_json(source) if source.suffix == ".json"
                 else pd.read_csv(source, keep_default_na=True))
    else:
        json_path = _resolve(TIMING_JSON, repo_root)
        csv_path = _resolve(TIMING_CSV, repo_root)
        if json_path.exists():
            source, frame = json_path, pd.read_json(json_path)
        elif csv_path.exists():
            source, frame = csv_path, pd.read_csv(csv_path)
        else:
            return pd.DataFrame(columns=KEYS)

    if frame.empty:
        return pd.DataFrame(columns=KEYS)

    frame = _normalize_keys(_normalize_columns(frame))
    frame.attrs["source"] = str(source)
    return frame


def load_static_metrics(path: Path | str | None = None, repo_root: Path = REPO_ROOT) -> pd.DataFrame:
    """Carrega as metricas estaticas por trial (Issue #5: Radon + jscpd)."""
    source = _resolve(path or STATIC_METRICS_CSV, repo_root)
    if not source.exists():
        return pd.DataFrame(columns=KEYS)
    frame = _normalize_keys(_normalize_columns(pd.read_csv(source)))
    frame.attrs["source"] = str(source)
    return frame


def find_consolidated(repo_root: Path = REPO_ROOT) -> Path | None:
    """Localiza o dataset consolidado da Issue #44, se ja estiver no repo."""
    for candidate in CONSOLIDATED_CANDIDATES:
        resolved = _resolve(candidate, repo_root)
        if resolved.exists():
            return resolved
    return None


def load_consolidated(path: Path | str | None = None,
                      repo_root: Path = REPO_ROOT) -> pd.DataFrame | None:
    """Carrega o consolidado da Issue #44 (ou None enquanto ele nao existir)."""
    source = _resolve(path, repo_root) if path is not None else find_consolidated(repo_root)
    if source is None:
        return None
    if not source.exists():
        raise FileNotFoundError(f"consolidado nao encontrado: {source}")
    frame = (pd.read_json(source) if source.suffix == ".json" else pd.read_csv(source))
    frame = _normalize_keys(_normalize_columns(frame))
    frame.attrs["source"] = str(source)
    return frame


# --------------------------------------------------------------------------- #
# Consolidacao                                                                 #
# --------------------------------------------------------------------------- #
def _derive_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Completa as colunas derivadas (tempo em minutos, total de testes, sucesso)."""
    if "censored" in df.columns:
        df["censored"] = _to_bool(df["censored"])

    # tempo: s <-> min (o que vier faltando e calculado a partir do outro)
    for seconds, minutes in (("time_to_green_s", "time_to_green_min"),
                              ("elapsed_s", "elapsed_min"),
                              ("timebox_s", "timebox_min")):
        has_s, has_min = seconds in df.columns, minutes in df.columns
        if has_s and not has_min:
            df[minutes] = df[seconds] / 60.0
        elif has_min and not has_s:
            df[seconds] = df[minutes] * 60.0
        elif has_s and has_min:
            df[minutes] = df[minutes].where(df[minutes].notna(), df[seconds] / 60.0)
            df[seconds] = df[seconds].where(df[seconds].notna(), df[minutes] * 60.0)

    if "timebox_s" not in df.columns or df["timebox_s"].isna().all():
        df["timebox_s"] = float(TIMEBOX_S_DEFAULT)
        df["timebox_min"] = TIMEBOX_S_DEFAULT / 60.0

    # censura <-> event: um preenche o outro quando so um dos dois vem na fonte
    if "event" in df.columns and "censored" in df.columns:
        df["censored"] = df["censored"].where(
            df["censored"].notna(), _to_bool(df["event"].astype("string")).map({True: False, False: True}))
    if "censored" in df.columns:
        if "event" not in df.columns:
            df["event"] = pd.NA
        derived_event = df["censored"].map({True: 0, False: 1}).astype("Int64")
        df["event"] = pd.to_numeric(df["event"], errors="coerce").astype("Int64")
        df["event"] = df["event"].where(df["event"].notna(), derived_event)

    # RQ2: total de testes e proporcao de testes passando
    if "tests_passed" in df.columns:
        passed = pd.to_numeric(df["tests_passed"], errors="coerce").astype("float64")
        failed = (pd.to_numeric(df["tests_failed"], errors="coerce").astype("float64")
                  if "tests_failed" in df.columns
                  else pd.Series(float("nan"), index=df.index))
        total = (pd.to_numeric(df["tests_total"], errors="coerce").astype("float64")
                 if "tests_total" in df.columns
                 else pd.Series(float("nan"), index=df.index))
        # total so e derivado quando ha alguma contagem; trial sem registro de
        # tempo fica com tests_total vazio, nao zero.
        counted = passed.notna() | failed.notna()
        total = total.where(total.notna(), (passed.fillna(0) + failed.fillna(0)).where(counted))
        df["tests_total"] = total
        df["pct_tests_passing"] = 100.0 * passed / total.where(total > 0)

    # RQ2 primario: sucesso = atingiu o verde dentro do time-box
    if "success" in df.columns:
        df["success"] = _to_bool(df["success"])
    elif "event" in df.columns:
        df["success"] = (df["event"] == 1).astype("boolean").where(df["event"].notna())
    elif "censored" in df.columns:
        df["success"] = (~df["censored"].astype("boolean"))

    df["trial_id"] = (df["participant"].astype("string") + "/"
                      + df["kata"].astype("string") + "_"
                      + df["treatment"].astype("string"))
    return df


def _apply_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Garante presenca, tipo e ordem das colunas documentadas em DATA_DICTIONARY."""
    for col in COLUMN_ORDER:
        if col not in df.columns:
            df[col] = pd.NA

    for col in DATETIME_COLUMNS:
        df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)

    for col, dtype in DTYPES.items():
        if col in DATETIME_COLUMNS:
            continue
        if dtype == "category":
            continue
        if dtype in ("Int64", "float64"):
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(dtype)
        elif dtype == "boolean":
            df[col] = _to_bool(df[col])
        else:
            df[col] = df[col].astype(dtype)

    df["treatment"] = pd.Categorical(df["treatment"], categories=TREATMENTS, ordered=True)

    extra = [c for c in df.columns if c not in COLUMN_ORDER]
    return df[COLUMN_ORDER + extra]


def build_dataset(timing_path: Path | str | None = None,
                  metrics_path: Path | str | None = None,
                  consolidated_path: Path | str | None = None,
                  use_consolidated: bool = True,
                  repo_root: Path = REPO_ROOT) -> pd.DataFrame:
    """Monta o DataFrame unico do dashboard: uma linha por trial.

    Ordem de precedencia das fontes de tempo/testes:
      1. dataset consolidado da Issue #44, quando existir (ou --consolidated);
      2. results/timing.json (fonte da verdade do script de cronometragem);
      3. results/timing.csv (fallback).
    As metricas estaticas (RQ3) vem sempre de results/static_metrics.csv e sao
    juncao externa, para que um trial presente em so uma das fontes apareca no
    dataset com as colunas da outra vazias (em vez de desaparecer).
    """
    sources: dict[str, str] = {}

    consolidated = None
    if use_consolidated or consolidated_path is not None:
        consolidated = load_consolidated(consolidated_path, repo_root)

    timing = load_timing(timing_path, repo_root)
    metrics = load_static_metrics(metrics_path, repo_root)

    if consolidated is not None and not consolidated.empty:
        sources["consolidado"] = consolidated.attrs.get("source", "?")
        base = _merge_prefer_left(consolidated, timing) if not timing.empty else consolidated
        if not timing.empty:
            sources["timing"] = timing.attrs.get("source", "?")
    else:
        base = timing
        if not timing.empty:
            sources["timing"] = timing.attrs.get("source", "?")

    if base.empty and metrics.empty:
        raise SystemExit(
            "nenhuma fonte de dados encontrada; rode os scripts de coleta antes:\n"
            "  python scripts/timing/track_time.py export\n"
            "  python scripts/metrics/collect_metrics.py"
        )

    base = base.copy()
    base["has_timing"] = True
    if not metrics.empty:
        sources["static_metrics"] = metrics.attrs.get("source", "?")
        metrics = metrics.copy()
        metrics["has_metrics"] = True
        # _merge_prefer_left, e nao merge cru: consolidado (#44) e
        # static_metrics compartilham nomes de coluna (loc, cc_total). Um merge
        # cru geraria loc_x/loc_y e deixaria `loc` vazia, apagando H3c.
        df = _merge_prefer_left(base, metrics) if not base.empty else metrics
    else:
        df = base
        df["has_metrics"] = False

    df["has_timing"] = _to_bool(df.get("has_timing", pd.Series(pd.NA, index=df.index))).fillna(False)
    df["has_metrics"] = _to_bool(df.get("has_metrics", pd.Series(pd.NA, index=df.index))).fillna(False)

    df = _apply_schema(_derive_columns(df))
    df = df.sort_values(["participant", "kata", "treatment"]).reset_index(drop=True)
    df.attrs["sources"] = sources
    return df


# --------------------------------------------------------------------------- #
# Esqueletos para a epica de analise (#42: issues #45, #46, #47)                #
# --------------------------------------------------------------------------- #
#
# A unidade de analise do desenho crossover e o INTEGRANTE, com observacoes
# pareadas ai x manual (docs/desenho-experimento.md secao 5). Como cada
# integrante executou mais de um trial por tratamento, o pareamento exige
# agregar os trials de um mesmo integrante dentro de cada tratamento. A escolha
# do agregador (mediana por default, coerente com os descritivos declarados na
# secao 7 do desenho) fica explicita como parametro, e a decisao final -- assim
# como o tratamento dos censurados -- pertence as issues de analise.

METRIC_COLUMNS = [
    "time_to_green_min",   # RQ1
    "pct_tests_passing",   # RQ2 (secundaria)
    "cc_avg",              # RQ3 / H3a
    "duplication_pct",     # RQ3 / H3b
    "loc",                 # RQ3 / H3c
    "sloc",
    "cc_total",
    "mi_avg",
]


def build_participant_summary(df: pd.DataFrame, agg: str = "median") -> pd.DataFrame:
    """Agrega os trials por (participant, treatment) -- base do teste pareado.

    Devolve uma linha por integrante x tratamento com o agregador escolhido nas
    metricas continuas, mais n_trials, n_success e success_rate (RQ2).
    """
    metrics = [c for c in METRIC_COLUMNS if c in df.columns]
    grouped = df.groupby(["participant", "treatment"], observed=True)
    summary = grouped[metrics].agg(agg)
    summary["n_trials"] = grouped.size()
    summary["n_timed"] = grouped["has_timing"].apply(lambda s: int(s.fillna(False).sum()))
    summary["n_success"] = grouped["success"].apply(lambda s: int(s.fillna(False).sum()))
    summary["n_censored"] = grouped["censored"].apply(lambda s: int(s.fillna(False).sum()))
    # denominador = trials com DESFECHO conhecido (verde ou censura registrada).
    # Trial sem desfecho -- tempo derivado e censura vazia, como os de Paulo --
    # e dado faltante, nao fracasso: conta-lo no denominador derruba a taxa de
    # sucesso para 0% onde o correto e "nao observado".
    summary["n_outcome"] = grouped["success"].apply(lambda s: int(s.notna().sum()))
    summary["success_rate"] = (summary["n_success"] / summary["n_outcome"]).where(summary["n_outcome"] > 0)
    return summary.round(4).reset_index()


def build_paired_frame(df: pd.DataFrame, agg: str = "median") -> pd.DataFrame:
    """Formato largo (um integrante por linha) com <metrica>_manual/_ai/_diff.

    Entrada direta dos testes pareados planejados (Wilcoxon/McNemar). A coluna
    _diff e sempre ai - manual, entao valores negativos em tempo significam
    "mais rapido com IA".
    """
    summary = build_participant_summary(df, agg=agg)
    value_cols = [c for c in summary.columns if c not in ("participant", "treatment")]
    wide = summary.pivot(index="participant", columns="treatment", values=value_cols)
    wide.columns = [f"{metric}_{treatment}" for metric, treatment in wide.columns]
    # diferenca pareada so faz sentido nas metricas de resposta (nao em contagens)
    diff_cols = [c for c in value_cols if c in METRIC_COLUMNS or c == "success_rate"]
    for metric in diff_cols:
        ai, manual = f"{metric}_ai", f"{metric}_manual"
        if ai in wide.columns and manual in wide.columns:
            wide[f"{metric}_diff"] = wide[ai] - wide[manual]
    ordered = [c for metric in value_cols
               for c in (f"{metric}_manual", f"{metric}_ai", f"{metric}_diff")
               if c in wide.columns]
    return wide[ordered].round(4).reset_index()


def success_rate_by_treatment(df: pd.DataFrame) -> pd.DataFrame:
    """Taxa de sucesso por tratamento (variavel primaria de RQ2, issue #46)."""
    grouped = df.groupby("treatment", observed=True)
    out = pd.DataFrame({
        "n_trials": grouped.size(),
        "n_timed": grouped["has_timing"].apply(lambda s: int(s.fillna(False).sum())),
        "n_success": grouped["success"].apply(lambda s: int(s.fillna(False).sum())),
        "n_censored": grouped["censored"].apply(lambda s: int(s.fillna(False).sum())),
        # desfecho conhecido: verde ou censura registrada. Ver a nota em
        # build_participant_summary -- trial sem desfecho nao e fracasso.
        "n_outcome": grouped["success"].apply(lambda s: int(s.notna().sum())),
    })
    out["success_rate"] = (out["n_success"] / out["n_outcome"]).where(out["n_outcome"] > 0)
    return out.reset_index()


def descriptives_by_treatment(df: pd.DataFrame,
                              metrics: list[str] | None = None) -> pd.DataFrame:
    """Mediana/IQR por tratamento -- descritivos declarados na secao 7 do desenho."""
    metrics = [c for c in (metrics or METRIC_COLUMNS) if c in df.columns]
    rows = []
    for treatment, group in df.groupby("treatment", observed=True):
        for metric in metrics:
            values = pd.to_numeric(group[metric], errors="coerce").dropna()
            if values.empty:
                continue
            q1, q3 = values.quantile(0.25), values.quantile(0.75)
            rows.append({
                "treatment": treatment, "metric": metric, "n": int(values.size),
                "median": values.median(), "q1": q1, "q3": q3, "iqr": q3 - q1,
                "min": values.min(), "max": values.max(),
                "mean": values.mean(), "std": values.std(ddof=1) if values.size > 1 else pd.NA,
            })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Integridade e documentacao                                                   #
# --------------------------------------------------------------------------- #
def validate_dataset(df: pd.DataFrame) -> list[str]:
    """Checagens de integridade da juncao. Nao exclui nada -- so avisa.

    Decisoes sobre outliers e trials incompletos pertencem a Issue #44.
    """
    warnings: list[str] = []

    only_timing = df.loc[df["has_timing"].fillna(False) & ~df["has_metrics"].fillna(False), "trial_id"]
    only_metrics = df.loc[~df["has_timing"].fillna(False) & df["has_metrics"].fillna(False), "trial_id"]
    if len(only_timing):
        warnings.append(f"trial(s) com tempo e sem metricas estaticas: {', '.join(only_timing)}")
    if len(only_metrics):
        warnings.append(f"trial(s) com metricas estaticas e sem tempo: {', '.join(only_metrics)}")

    duplicated = df.loc[df.duplicated(subset=KEYS, keep=False), "trial_id"]
    if len(duplicated):
        warnings.append(f"tripla (participant,kata,treatment) duplicada: {', '.join(duplicated.unique())}")

    for participant, group in df.groupby("participant", observed=True):
        present = set(group.loc[group["has_timing"].fillna(False), "treatment"].dropna().astype(str))
        missing = set(TREATMENTS) - present
        if missing:
            warnings.append(
                f"{participant} nao tem trial em: {', '.join(sorted(missing))} "
                "(sem par completo, fica fora do teste pareado)")
        repeated = group.loc[group["kata"].duplicated(keep=False), "kata"].unique()
        if len(repeated):
            warnings.append(
                f"{participant} repetiu kata(s) {', '.join(repeated)} -- o desenho "
                "crossover pede katas diferentes por integrante (carryover)")

    inconsistent = df[df["tests_total"].notna() & (df["tests_total"] <= 0)]
    if len(inconsistent):
        warnings.append(f"trial(s) com tests_total <= 0: {', '.join(inconsistent['trial_id'])}")

    green_but_failing = df[(df["success"].fillna(False)) & (df["tests_failed"].fillna(0) > 0)]
    if len(green_but_failing):
        warnings.append(
            "trial(s) marcados como verdes com testes falhando: "
            f"{', '.join(green_but_failing['trial_id'])}")

    over_timebox = df[df["time_to_green_s"].notna() & df["timebox_s"].notna()
                      & (df["time_to_green_s"] > df["timebox_s"])]
    if len(over_timebox):
        warnings.append(
            "time_to_green acima do time-box (deveria estar censurado em 35 min): "
            f"{', '.join(over_timebox['trial_id'])}")
    return warnings


def describe_dataset(df: pd.DataFrame) -> str:
    """Tabela coluna/tipo/nao-nulos/grupo/descricao do DataFrame final."""
    lines = [f"{'coluna':<20} {'tipo':<22} {'nao-nulos':>9}  {'grupo':<14} descricao",
             "-" * 110]
    for col in df.columns:
        group, description = DATA_DICTIONARY.get(col, ("", ""))
        lines.append(f"{col:<20} {str(df[col].dtype):<22} {df[col].notna().sum():>9}  "
                     f"{group:<14} {description}")
    return "\n".join(lines)


def write_dataset(df: pd.DataFrame, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix == ".json":
        df.to_json(output, orient="records", indent=2, date_format="iso")
    else:
        df.to_csv(output, index=False)


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT,
                        help="raiz do repositorio (default: inferida a partir do script)")
    parser.add_argument("--timing", type=Path, default=None,
                        help="registros de tempo (default: results/timing.json, "
                             "com fallback para results/timing.csv)")
    parser.add_argument("--static-metrics", type=Path, default=None,
                        help="CSV de metricas estaticas (default: results/static_metrics.csv)")
    parser.add_argument("--consolidated", type=Path, default=None,
                        help="dataset consolidado da issue #44 (default: procura em "
                             + ", ".join(str(c) for c in CONSOLIDATED_CANDIDATES) + ")")
    parser.add_argument("--no-consolidated", action="store_true",
                        help="ignora o consolidado e monta direto dos brutos")
    parser.add_argument("--output", type=Path, default=None,
                        help="grava o dataset final (.csv ou .json)")
    parser.add_argument("--paired-output", type=Path, default=None,
                        help="grava tambem o formato pareado por integrante (.csv ou .json)")
    parser.add_argument("--agg", default="median", choices=["median", "mean", "min", "max"],
                        help="agregador dos trials de um integrante por tratamento (default: median)")
    parser.add_argument("--dictionary", action="store_true",
                        help="imprime o dicionario de dados e sai")
    parser.add_argument("--quiet", action="store_true", help="so imprime avisos e erros")
    args = parser.parse_args(argv)

    if args.dictionary:
        width = max(len(c) for c in DATA_DICTIONARY)
        for col, (group, description) in DATA_DICTIONARY.items():
            print(f"{col:<{width}}  {str(DTYPES[col]):<22} {group:<14} {description}")
        return 0

    df = build_dataset(timing_path=args.timing,
                       metrics_path=args.static_metrics,
                       consolidated_path=args.consolidated,
                       use_consolidated=not args.no_consolidated,
                       repo_root=args.repo_root.resolve())

    if not args.quiet:
        print("fontes:")
        for name, path in df.attrs.get("sources", {}).items():
            try:
                shown = Path(path).relative_to(args.repo_root.resolve())
            except ValueError:
                shown = Path(path)
            print(f"  {name:<16} {shown}")
        if "consolidado" not in df.attrs.get("sources", {}):
            print("  (consolidado da issue #44 ainda nao existe; montado a partir dos brutos)")

        print(f"\n{len(df)} trial(s) x {len(df.columns)} coluna(s)\n")
        print(describe_dataset(df))

        print("\ntrials por tratamento:")
        print(success_rate_by_treatment(df).to_string(index=False))

        print("\ndescritivos por tratamento (mediana/IQR):")
        print(descriptives_by_treatment(df).to_string(index=False))

        print(f"\npareado por integrante (agg={args.agg}), colunas de RQ1/RQ2:")
        paired = build_paired_frame(df, agg=args.agg)
        cols = ["participant"] + [c for c in paired.columns
                                  if c.startswith(("time_to_green_min", "success_rate"))]
        print(paired[cols].to_string(index=False))

    warnings = validate_dataset(df)
    if warnings:
        print("\navisos de integridade (nenhum dado foi excluido):", file=sys.stderr)
        for warning in warnings:
            print(f"  - {warning}", file=sys.stderr)

    if args.output:
        output = _resolve(args.output, args.repo_root.resolve())
        write_dataset(df, output)
        print(f"\ndataset -> {output}")
    if args.paired_output:
        paired_output = _resolve(args.paired_output, args.repo_root.resolve())
        write_dataset(build_paired_frame(df, agg=args.agg), paired_output)
        print(f"pareado -> {paired_output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
