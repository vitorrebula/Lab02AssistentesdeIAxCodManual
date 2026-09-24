#!/usr/bin/env python3
"""Graficos por questao de pesquisa (Issue #49).

Gera as figuras que entram no Relatorio Final, comparando os dois tratamentos
(`manual` x `ai`) em cada RQ do desenho (docs/desenho-experimento.md):

    RQ1  tempo/time-to-green   -> boxplot (mediana/IQR) + pares por integrante,
                                  com os trials censurados sinalizados no teto
                                  do time-box de 35 min
    RQ2  taxa de sucesso       -> barras de taxa de sucesso (primaria) +
                                  boxplot de % de testes aprovados (secundaria)
    RQ3  complexidade,         -> um boxplot por metrica estrutural, mais um
         duplicacao e LOC         painel combinado das tres

Todos os numeros vem do DataFrame de `load_data.build_dataset()` -- nada e
digitado aqui. As figuras sao exportadas em PNG e tambem podem ser devolvidas
como objetos `Figure` para render inline no notebook do dashboard.

Uso como script:

    python scripts/dashboard/plots.py                      # grava em results/figures/
    python scripts/dashboard/plots.py --fig-dir /tmp/figs --dpi 300

Uso como modulo (notebook):

    from plots import figure_rq1, figure_rq2, figure_rq3_all, save_figure
    fig = figure_rq1(df)
    save_figure(fig, FIG_DIR / "rq1_time_to_green.png")
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from load_data import (  # noqa: E402
    REPO_ROOT,
    build_dataset,
    build_participant_summary,
    success_rate_by_treatment,
)

# --------------------------------------------------------------------------- #
# Identidade visual                                                            #
# --------------------------------------------------------------------------- #
# Dois tratamentos = duas cores categoricas (slots 1 e 2 da paleta de
# referencia), validadas para daltonismo: dE CVD 24.7 e dE normal 33.6 no par.
# A cor identifica o tratamento; numeros e rotulos usam sempre tinta de texto.
TREATMENT_ORDER = ["manual", "ai"]
TREATMENT_COLORS = {"manual": "#2a78d6", "ai": "#eb6834"}
TREATMENT_LABELS = {"manual": "Sem IA (manual)", "ai": "Com IA (Claude Code)"}
TREATMENT_SHORT = {"manual": "Sem IA", "ai": "Com IA"}

SURFACE = "#fcfcfb"        # fundo da figura
INK = "#0b0b0b"            # texto primario
INK_SECONDARY = "#52514e"  # eixos, rotulos
INK_MUTED = "#8a8a84"      # notas, linhas de referencia
GRID = "#e6e5e0"           # grade (um tom acima do fundo)

FIG_DIR_DEFAULT = Path("results") / "figures"
DATASET_SOURCE = "results/dashboard_dataset.csv"

# Metricas: titulo, rotulo do eixo e casas decimais dos rotulos.
METRIC_SPECS: dict[str, dict[str, object]] = {
    "time_to_green_min": {
        "title": "Tempo até o verde (time-to-green)",
        "axis": "Tempo até o verde (min)",
        "decimals": 2,
    },
    "pct_tests_passing": {
        "title": "Testes de aceitação aprovados",
        "axis": "Testes aprovados (%)",
        "decimals": 1,
    },
    "cc_avg": {
        "title": "Complexidade ciclomática média por função",
        "axis": "CC média por função",
        "decimals": 2,
    },
    "duplication_pct": {
        "title": "Duplicação de código",
        "axis": "Linhas duplicadas (%)",
        "decimals": 1,
    },
    "loc": {
        "title": "Tamanho da solução",
        "axis": "LOC (linhas de código)",
        "decimals": 0,
    },
    "sloc": {
        "title": "Tamanho da solução (sem brancos/comentários)",
        "axis": "SLOC",
        "decimals": 0,
    },
    "cc_total": {
        "title": "Complexidade ciclomática total",
        "axis": "CC total",
        "decimals": 1,
    },
    "mi_avg": {
        "title": "Maintainability Index médio",
        "axis": "MI médio",
        "decimals": 1,
    },
}

# Metricas estruturais com hipotese formal (H3a/H3b/H3c), na ordem do desenho.
RQ3_METRICS = ["cc_avg", "duplication_pct", "loc"]
RQ3_HYPOTHESES = {"cc_avg": "H3a", "duplication_pct": "H3b", "loc": "H3c"}

JITTER_SEED = 20260923  # jitter dos pontos e deterministico (figura reproduzivel)

# Rotulo em pt-BR do agregador dos trials de um integrante (parametro `agg`).
AGG_LABELS = {"median": "mediana", "mean": "média", "min": "mínimo", "max": "máximo"}

# Alturas relativas usadas na composicao (titulo/subtitulo/legenda/nota).
# Sao fracoes da altura da figura, calibradas para FIG_HEIGHT e os tamanhos de
# fonte definidos em apply_style(); _frame_text() as usa para reservar margem.
FIG_HEIGHT = 5.9
LINE = 0.030


def apply_style() -> None:
    """Estilo comum das figuras: marcas finas, grade discreta, fundo claro."""
    plt.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 10,
        "axes.titlesize": 10.5,
        "axes.labelsize": 10,
        "axes.edgecolor": GRID,
        "axes.linewidth": 0.8,
        "axes.labelcolor": INK_SECONDARY,
        "axes.titlecolor": INK,
        "text.color": INK,
        "xtick.color": INK_SECONDARY,
        "ytick.color": INK_SECONDARY,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "grid.linestyle": "-",
        "legend.frameon": False,
        "legend.fontsize": 9,
        "figure.dpi": 110,
        "savefig.dpi": 200,
    })


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #
def _fmt(value: float | None, decimals: int = 2) -> str:
    """Numero no padrao pt-BR (virgula decimal), para rotulos do relatorio."""
    if value is None or pd.isna(value):
        return "–"
    text = f"{float(value):,.{decimals}f}"
    return text.replace(",", " ").replace(".", ",")


def _fmt_auto(value: float | None, decimals: int = 2) -> str:
    """Como _fmt, mas nao esconde parte fracionaria em metricas inteiras (LOC)."""
    if value is not None and not pd.isna(value) and decimals == 0 \
            and not float(value).is_integer():
        decimals = 1
    return _fmt(value, decimals)


def _spec(metric: str) -> dict[str, object]:
    return METRIC_SPECS.get(metric, {"title": metric, "axis": metric, "decimals": 2})


def _clean_axes(ax: plt.Axes, *, grid_axis: str = "y") -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(True, axis=grid_axis, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def _numeric(frame: pd.DataFrame, metric: str) -> pd.Series:
    return pd.to_numeric(frame[metric], errors="coerce")


def _groups(df: pd.DataFrame, metric: str) -> dict[str, pd.DataFrame]:
    """Sub-frame por tratamento, so com as linhas que tem a metrica medida."""
    out: dict[str, pd.DataFrame] = {}
    for treatment in TREATMENT_ORDER:
        rows = df[df["treatment"].astype("string") == treatment].copy()
        rows[metric] = _numeric(rows, metric)
        out[treatment] = rows[rows[metric].notna()]
    return out


def _censored_mask(frame: pd.DataFrame) -> pd.Series:
    if "censored" not in frame.columns:
        return pd.Series(False, index=frame.index)
    return frame["censored"].fillna(False).astype(bool)


def _pad_limits(ax: plt.Axes, values: np.ndarray, *, floor_at_zero: bool = True) -> None:
    """Folga vertical; metrica constante (ex.: duplicacao 0%) ainda fica visivel."""
    if values.size == 0:
        return
    low, high = float(np.min(values)), float(np.max(values))
    spread = high - low
    pad = spread * 0.18 if spread > 0 else max(abs(high) * 0.08, 1.0)
    bottom = low - pad
    if floor_at_zero and low >= 0:
        bottom = max(0.0, low - pad) if low > 0 else -pad * 0.35
    ax.set_ylim(bottom, high + pad * 1.4)


def _annotate_inside(ax: plt.Axes, x: float, y: float, text: str, **kwargs) -> None:
    """Rotulo ao lado de uma marca, mantido dentro da area do eixo.

    Perto do piso/teto do eixo o alinhamento vertical troca, senao o texto sai
    da figura (foi o que acontecia com a mediana proxima de zero em RQ1).
    """
    bottom, top = ax.get_ylim()
    share = (y - bottom) / (top - bottom) if top > bottom else 0.5
    va = "bottom" if share < 0.12 else ("top" if share > 0.88 else "center")
    ax.annotate(text, xy=(x, y), ha="left", va=va, fontsize=9, color=INK,
                linespacing=1.35, zorder=5,
                bbox={"facecolor": SURFACE, "edgecolor": "none", "pad": 1.5},
                **kwargs)


def _repel(values: list[float], span: float, *, min_gap: float = 0.055) -> list[float]:
    """Desloca rotulos proximos para que nao se sobreponham (mesmo x, y perto)."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    adjusted = list(values)
    for previous, current in zip(order, order[1:]):
        gap = adjusted[current] - adjusted[previous]
        if gap < span * min_gap:
            adjusted[current] = adjusted[previous] + span * min_gap
    return adjusted


def _source_note(df: pd.DataFrame, extra: str = "") -> str:
    n_trials = len(df)
    n_participants = df["participant"].nunique()
    note = (f"Fonte: {DATASET_SOURCE} (gerado por scripts/dashboard/load_data.py) — "
            f"{n_trials} trials de {n_participants} integrantes.")
    return f"{note}\n{extra}".strip()


def _frame_text(fig: plt.Figure, title: str, subtitle: str, footnote: str,
                *, tick_lines: int = 2) -> None:
    """Titulo, subtitulo e nota de fonte, reservando a margem que cada um ocupa.

    A margem e calculada a partir do numero de linhas de cada bloco (em vez de
    valores fixos), para que titulo, subtitulo, rotulos de eixo, legenda e nota
    de fonte nunca se sobreponham -- a figura vai direto para o relatorio.
    """
    scale = FIG_HEIGHT / fig.get_size_inches()[1]
    line = LINE * scale
    sub_lines = subtitle.count("\n") + 1
    foot_lines = footnote.count("\n") + 1

    fig.text(0.012, 1 - 0.4 * line, title, fontsize=13.5, fontweight="bold",
             color=INK, ha="left", va="top")
    subtitle_y = 1 - 1.9 * line
    fig.text(0.012, subtitle_y, subtitle, fontsize=9.5, color=INK_SECONDARY,
             ha="left", va="top", linespacing=1.4)
    fig.text(0.012, 0.6 * line, footnote, fontsize=8.5, color=INK_MUTED,
             ha="left", va="bottom", linespacing=1.4)

    top = subtitle_y - sub_lines * 1.15 * line - 2.0 * line  # espaco do titulo do painel
    bottom = (0.6 + foot_lines + 1.9) * line + tick_lines * 1.05 * line
    fig.subplots_adjust(top=top, bottom=bottom, left=0.075, right=0.985)
    fig.legend_bottom_y = (0.6 + foot_lines + 0.5) * line  # usado por _treatment_legend


# --------------------------------------------------------------------------- #
# Paineis reutilizaveis                                                        #
# --------------------------------------------------------------------------- #
def boxplot_by_treatment(ax: plt.Axes, df: pd.DataFrame, metric: str, *,
                         title: str | None = None,
                         ylabel: str | None = None,
                         mark_censored: bool = False,
                         show_stats: bool = True) -> dict[str, pd.Series]:
    """Boxplot mediana/IQR de `metric` nos dois tratamentos, com os trials visiveis.

    Caixa = IQR (Q1-Q3), linha = mediana, hastes = minimo-maximo (nao ha
    "outlier escondido": todos os trials aparecem como pontos). A mediana e
    rotulada direto na figura e o IQR entra no rotulo do eixo x, junto do n.
    Com `mark_censored`, os trials censurados saem como triangulo vazado em vez
    de ponto, porque o valor deles e um piso ("pelo menos isso"), nao uma medida.
    """
    spec = _spec(metric)
    decimals = int(spec["decimals"])
    groups = _groups(df, metric)
    positions = {"manual": 1.0, "ai": 2.0}
    rng = np.random.default_rng(JITTER_SEED)
    all_values = [v for rows in groups.values() for v in rows[metric].tolist()]
    ax.set_xlim(0.5, 2.62)
    _pad_limits(ax, np.asarray(all_values, dtype=float))

    ticks = []
    for treatment in TREATMENT_ORDER:
        rows = groups[treatment]
        color = TREATMENT_COLORS[treatment]
        pos = positions[treatment]
        values = rows[metric].to_numpy(dtype=float)
        tick = f"{TREATMENT_LABELS[treatment]}\nn = {len(rows)} trials"

        if values.size == 0:
            ax.text(pos, 0.5, "sem dados", transform=ax.get_xaxis_transform(),
                    ha="center", va="center", fontsize=9, color=INK_MUTED)
            ticks.append(tick)
            continue

        # whis=(0,100): hastes vao ao minimo/maximo observados; sem fliers,
        # porque cada trial ja e desenhado como ponto logo abaixo.
        ax.boxplot(
            [values], positions=[pos], widths=0.44, showfliers=False, whis=(0, 100),
            patch_artist=True,
            boxprops={"facecolor": color, "alpha": 0.14, "edgecolor": color,
                      "linewidth": 1.4},
            medianprops={"color": color, "linewidth": 2.4, "solid_capstyle": "butt"},
            whiskerprops={"color": color, "linewidth": 1.2},
            capprops={"color": color, "linewidth": 1.2},
            zorder=2,
        )

        censored = _censored_mask(rows) if mark_censored else pd.Series(False, index=rows.index)
        for subset, marker, size, hollow in ((~censored, "o", 36, False),
                                             (censored, "^", 80, True)):
            picked = rows[subset]
            if picked.empty:
                continue
            jitter = rng.uniform(-0.11, 0.11, size=len(picked))
            ax.scatter(np.full(len(picked), pos) + jitter,
                       picked[metric].to_numpy(dtype=float),
                       marker=marker, s=size,
                       facecolor=SURFACE if hollow else color,
                       edgecolor=color if hollow else SURFACE,
                       linewidth=1.6 if hollow else 1.1,
                       zorder=4, clip_on=False)

        median = float(np.median(values))
        q1, q3 = float(np.percentile(values, 25)), float(np.percentile(values, 75))
        if show_stats:
            _annotate_inside(ax, pos + 0.26, median, f"md {_fmt_auto(median, decimals)}")
            tick += f"\nIQR {_fmt_auto(q1, decimals)}–{_fmt_auto(q3, decimals)}"
        if mark_censored:
            tick += f"\ncensurados: {int(censored.sum())}"
        ticks.append(tick)

    ax.set_xticks([positions[t] for t in TREATMENT_ORDER])
    ax.set_xticklabels(ticks)
    ax.set_ylabel(ylabel or str(spec["axis"]))
    if title:
        ax.set_title(title, loc="left", pad=10)
    _clean_axes(ax)
    return {t: groups[t][metric] for t in TREATMENT_ORDER}


def paired_panel(ax: plt.Axes, df: pd.DataFrame, metric: str, *,
                 agg: str = "median", title: str | None = None,
                 ylabel: str | None = None,
                 mark_censored: bool = False) -> pd.DataFrame:
    """Grafico de pares: uma linha por integrante ligando manual -> com IA.

    A unidade de analise do desenho crossover e o integrante (desenho, secao 5),
    e cada integrante fez mais de um trial por tratamento -- por isso os trials
    sao agregados pela `agg` (mediana por default, como nos descritivos).

    Com `mark_censored`, o ponto de um integrante cujo agregado inclui trial
    censurado sai como triangulo vazado: o valor agregado herda o piso do
    time-box e nao pode ser lido como tempo observado.
    """
    spec = _spec(metric)
    decimals = int(spec["decimals"])
    summary = build_participant_summary(df, agg=agg)
    if metric not in summary.columns:
        ax.text(0.5, 0.5, "métrica ausente no dataset", transform=ax.transAxes,
                ha="center", va="center", fontsize=9, color=INK_MUTED)
        _clean_axes(ax)
        return pd.DataFrame()

    wide = (summary.pivot(index="participant", columns="treatment", values=metric)
                   .reindex(columns=TREATMENT_ORDER))
    complete = wide.dropna()
    positions = {"manual": 1.0, "ai": 2.0}
    censored_pairs: set[tuple[str, str]] = set()
    if mark_censored:
        flags = df.assign(_censored=_censored_mask(df))
        grouped = flags.groupby(["participant", "treatment"], observed=True)["_censored"].any()
        censored_pairs = {(str(p), str(t)) for (p, t), flag in grouped.items() if flag}
    # folga a esquerda para o rotulo com o nome do integrante caber no eixo
    ax.set_xlim(0.12, 2.62)
    _pad_limits(ax, complete.to_numpy(dtype=float).ravel())

    span = ax.get_ylim()[1] - ax.get_ylim()[0]
    left_y = _repel([float(v) for v in complete["manual"]], span)
    right_y = _repel([float(v) for v in complete["ai"]], span)

    for i, (participant, row) in enumerate(complete.iterrows()):
        y_manual, y_ai = float(row["manual"]), float(row["ai"])
        ax.plot([positions["manual"], positions["ai"]], [y_manual, y_ai],
                color=INK_MUTED, linewidth=1.2, alpha=0.85, zorder=2)
        for treatment, y in (("manual", y_manual), ("ai", y_ai)):
            hollow = (str(participant), treatment) in censored_pairs
            ax.scatter([positions[treatment]], [y], marker="^" if hollow else "o",
                       s=80 if hollow else 46,
                       facecolor=SURFACE if hollow else TREATMENT_COLORS[treatment],
                       edgecolor=TREATMENT_COLORS[treatment] if hollow else SURFACE,
                       linewidth=1.6 if hollow else 1.4, zorder=4, clip_on=False)
        label_bbox = {"facecolor": SURFACE, "edgecolor": "none", "pad": 1.5}
        ax.annotate(f"{participant}  {_fmt_auto(y_manual, decimals)}",
                    xy=(positions["manual"] - 0.07, left_y[i]), ha="right", va="center",
                    fontsize=9, color=INK_SECONDARY, zorder=5, bbox=label_bbox)
        ax.annotate(_fmt_auto(y_ai, decimals),
                    xy=(positions["ai"] + 0.07, right_y[i]), ha="left", va="center",
                    fontsize=9, color=INK, zorder=5, bbox=label_bbox)

    incomplete = wide.index.difference(complete.index)
    if len(incomplete):
        ax.text(0.5, 0.02, "fora do par: " + ", ".join(str(p) for p in incomplete),
                transform=ax.transAxes, ha="center", va="bottom", fontsize=8.5,
                color=INK_MUTED)

    ax.set_xticks([positions[t] for t in TREATMENT_ORDER])
    ax.set_xticklabels([TREATMENT_SHORT[t] for t in TREATMENT_ORDER])
    ax.set_ylabel(ylabel or str(spec["axis"]))
    if title:
        ax.set_title(f"{title} · n = {len(complete)} integrantes", loc="left", pad=10)
    _clean_axes(ax)
    return complete


def success_rate_panel(ax: plt.Axes, df: pd.DataFrame, *,
                       title: str | None = None) -> pd.DataFrame:
    """Barras da taxa de sucesso por tratamento (variavel primaria de RQ2).

    Sucesso = trial que fechou no verde dentro do time-box. O denominador sao
    os trials com DESFECHO conhecido (`n_outcome`), conforme load_data: trial
    com tempo derivado e sem censura registrada e dado faltante, nao fracasso.
    """
    rates = success_rate_by_treatment(df)
    rates["treatment"] = rates["treatment"].astype("string")
    rates = rates.set_index("treatment").reindex(TREATMENT_ORDER)
    positions = np.arange(len(TREATMENT_ORDER), dtype=float)

    for pos, treatment in zip(positions, TREATMENT_ORDER):
        row = rates.loc[treatment]
        rate = row["success_rate"]
        height = 0.0 if pd.isna(rate) else float(rate) * 100.0
        ax.bar([pos], [height], width=0.34, color=TREATMENT_COLORS[treatment],
               edgecolor=SURFACE, linewidth=2, zorder=3)
        ax.annotate(f"{_fmt(height, 1)}%", xy=(pos, height), xytext=(0, 7),
                    textcoords="offset points", ha="center", va="bottom",
                    fontsize=12, fontweight="bold", color=INK)
        ax.annotate(f"{int(row['n_success'])}/{int(row['n_outcome'])} trials no verde",
                    xy=(pos, height), xytext=(0, 27), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, color=INK_SECONDARY)

    ax.set_xticks(positions)
    ax.set_xticklabels([
        f"{TREATMENT_LABELS[t]}\nn = {int(rates.loc[t, 'n_outcome'])} com desfecho"
        f" (de {int(rates.loc[t, 'n_trials'])})"
        f"\ncensurados: {int(rates.loc[t, 'n_censored'])}"
        for t in TREATMENT_ORDER])
    ax.set_xlim(-0.62, len(TREATMENT_ORDER) - 0.38)
    ax.set_ylim(0, 122)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("Taxa de sucesso (% dos trials no verde em 35 min)")
    if title:
        ax.set_title(title, loc="left", pad=10)
    _clean_axes(ax)
    return rates.reset_index()


def _treatment_legend(fig: plt.Figure, *, censored: bool = False,
                      trials: bool = True) -> None:
    """Legenda unica da figura: tratamentos + o que cada marca significa."""
    handles = [
        plt.Line2D([], [], marker="s", linestyle="none", markersize=8,
                   markerfacecolor=TREATMENT_COLORS[t], markeredgecolor=SURFACE,
                   label=TREATMENT_LABELS[t])
        for t in TREATMENT_ORDER
    ]
    if trials:
        handles.append(plt.Line2D([], [], marker="o", linestyle="none", markersize=6,
                                  markerfacecolor=INK_SECONDARY,
                                  markeredgecolor=SURFACE, label="1 trial"))
    if censored:
        handles.append(plt.Line2D([], [], marker="^", linestyle="none", markersize=9,
                                  markerfacecolor=SURFACE,
                                  markeredgecolor=INK_SECONDARY,
                                  label="trial censurado (tempo ≥ time-box)"))
    fig.legend(handles=handles, loc="lower left",
               bbox_to_anchor=(0.012, getattr(fig, "legend_bottom_y", 0.06)),
               ncol=len(handles), labelcolor=INK_SECONDARY, handletextpad=0.5,
               columnspacing=1.6)


# --------------------------------------------------------------------------- #
# RQ1 - tempo / time-to-green                                                  #
# --------------------------------------------------------------------------- #
def figure_rq1(df: pd.DataFrame, *, agg: str = "median") -> plt.Figure:
    """RQ1: distribuicao do time-to-green por tratamento + pares por integrante.

    Os trials censurados sao sinalizados de duas formas: triangulo vazado na
    altura do time-box e contagem explicita no rotulo de cada tratamento -- sem
    isso o boxplot leria o teto de 35 min como se fosse tempo observado.
    """
    apply_style()
    metric = "time_to_green_min"
    fig, axes = plt.subplots(1, 2, figsize=(11.6, FIG_HEIGHT),
                             gridspec_kw={"width_ratios": [1.15, 1.0], "wspace": 0.3})

    boxplot_by_treatment(axes[0], df, metric, mark_censored=True,
                         title="(a) Distribuição dos trials")
    paired_panel(axes[1], df, metric, agg=agg, mark_censored=True,
                 title=f"(b) Pares por integrante ({AGG_LABELS.get(agg, agg)} dos trials)")

    censored_total = int(_censored_mask(df).sum())
    timebox = pd.to_numeric(df.get("timebox_min"), errors="coerce").dropna()
    timebox_min = float(timebox.max()) if not timebox.empty else 35.0
    observed_max = float(_numeric(df, metric).max())

    # Referencia do time-box: entra no eixo quando ha censura (o teto passa a
    # ser um valor plotado); sem censura, vira nota -- esticar o eixo ate 35 min
    # achataria todos os tempos observados.
    if censored_total:
        for ax in axes:
            ax.set_ylim(ax.get_ylim()[0], max(ax.get_ylim()[1], timebox_min * 1.1))
            ax.axhline(timebox_min, color=INK_MUTED, linewidth=1.0,
                       linestyle=(0, (5, 3)), zorder=1)
            ax.annotate(f"time-box {_fmt(timebox_min, 0)} min",
                        xy=(ax.get_xlim()[1], timebox_min), xytext=(-2, 5),
                        textcoords="offset points", ha="right", va="bottom",
                        fontsize=8.5, color=INK_MUTED)
        censura = (f"{censored_total} trial(s) censurado(s) no time-box de "
                   f"{_fmt(timebox_min, 0)} min aparecem como triângulo vazado — o valor é "
                   "um piso, não um tempo observado.")
    else:
        censura = (f"Nenhum trial foi censurado: todos fecharam no verde antes do "
                   f"time-box de {_fmt(timebox_min, 0)} min (máximo observado: "
                   f"{_fmt(observed_max, 2)} min).")

    _frame_text(
        fig,
        "RQ1 — Tempo até o verde (time-to-green) por tratamento",
        "Caixa = IQR (Q1–Q3) · linha = mediana · hastes = mínimo e máximo · cada ponto é um trial.\n"
        + censura,
        _source_note(df, "Análise inferencial (Kaplan-Meier/log-rank e Wilcoxon pareado): "
                         "issue #45. Esta figura é descritiva."),
        tick_lines=4,
    )
    _treatment_legend(fig, censored=True)
    return fig


# --------------------------------------------------------------------------- #
# RQ2 - taxa de sucesso                                                        #
# --------------------------------------------------------------------------- #
def figure_rq2(df: pd.DataFrame) -> plt.Figure:
    """RQ2: taxa de sucesso (primaria) e % de testes aprovados (secundaria)."""
    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(11.6, FIG_HEIGHT),
                             gridspec_kw={"wspace": 0.28})

    rates = success_rate_panel(axes[0], df, title="(a) Taxa de sucesso (primária)")
    boxplot_by_treatment(axes[1], df, "pct_tests_passing", mark_censored=True,
                         title="(b) Testes aprovados no fechamento (secundária)")

    pct = _numeric(df, "pct_tests_passing").dropna()
    if not pct.empty and float(pct.min()) == float(pct.max()):
        axes[1].text(
            0.5, 0.88,
            "Sem variabilidade: os "
            f"{len(pct)} trials fecharam no verde, logo\n"
            f"% de testes aprovados = {_fmt(float(pct.iloc[0]), 0)}% por construção "
            "(desenho, §3)",
            transform=axes[1].transAxes, ha="center", va="top", fontsize=9.5,
            color=INK_SECONDARY, linespacing=1.5)

    distinct_rates = rates["success_rate"].dropna().unique()
    extra = ("Taxa de sucesso idêntica nos dois tratamentos: o teste de McNemar (issue #46) "
             "não tem par discordante para detectar efeito."
             if len(distinct_rates) == 1 else
             "Teste de McNemar sobre os pares por integrante: issue #46.")

    _frame_text(
        fig,
        "RQ2 — Taxa de sucesso e corretude funcional por tratamento",
        "Sucesso = trial que fechou no verde dentro do time-box de 35 min; denominador = trials com desfecho conhecido\n"
        "(os 4 trials de tempo derivado, sem censura registrada, entram como dado faltante, não como fracasso).\n"
        "Painel (b): caixa = IQR · linha = mediana · hastes = mínimo e máximo. A medida secundária só varia "
        f"entre trials censurados (nesta amostra: {int(_censored_mask(df).sum())}).",
        _source_note(df, extra),
        tick_lines=4,
    )
    _treatment_legend(fig, censored=True)
    return fig


# --------------------------------------------------------------------------- #
# RQ3 - complexidade, duplicacao e LOC                                         #
# --------------------------------------------------------------------------- #
def figure_rq3_metric(df: pd.DataFrame, metric: str, *, agg: str = "median") -> plt.Figure:
    """RQ3: uma metrica estrutural -- boxplot por tratamento + pares por integrante."""
    apply_style()
    spec = _spec(metric)
    hypothesis = RQ3_HYPOTHESES.get(metric)
    fig, axes = plt.subplots(1, 2, figsize=(11.6, FIG_HEIGHT),
                             gridspec_kw={"width_ratios": [1.15, 1.0], "wspace": 0.3})

    boxplot_by_treatment(axes[0], df, metric, title="(a) Distribuição dos trials")
    paired_panel(axes[1], df, metric, agg=agg,
                 title=f"(b) Pares por integrante ({AGG_LABELS.get(agg, agg)} dos trials)")

    values = _numeric(df, metric).dropna()
    constante = ""
    if not values.empty and float(values.min()) == float(values.max()):
        constante = (f" Todos os {len(values)} trials têm o mesmo valor "
                     f"({_fmt_auto(float(values.iloc[0]), int(spec['decimals']))}): "
                     "não há variação a comparar.")

    _frame_text(
        fig,
        f"RQ3 ({hypothesis}) — {spec['title']} por tratamento" if hypothesis
        else f"RQ3 — {spec['title']} por tratamento",
        "Caixa = IQR (Q1–Q3) · linha = mediana · hastes = mínimo e máximo · cada ponto é um trial."
        + constante,
        _source_note(df, "Wilcoxon pareado com correção de Holm-Bonferroni na família de RQ3: "
                         "issue #47."),
        tick_lines=3,
    )
    _treatment_legend(fig)
    return fig


def figure_rq3_overview(df: pd.DataFrame) -> plt.Figure:
    """RQ3: painel unico com as tres metricas com hipotese formal (H3a/H3b/H3c)."""
    apply_style()
    metrics = [m for m in RQ3_METRICS if m in df.columns]
    fig, axes = plt.subplots(1, len(metrics), figsize=(4.4 * len(metrics), FIG_HEIGHT),
                             gridspec_kw={"wspace": 0.38})
    axes = np.atleast_1d(axes)

    sem_variacao = []
    for ax, metric in zip(axes, metrics):
        spec = _spec(metric)
        hypothesis = RQ3_HYPOTHESES.get(metric, "")
        boxplot_by_treatment(ax, df, metric, title=f"{hypothesis} — {spec['title']}")
        values = _numeric(df, metric).dropna()
        if not values.empty and float(values.min()) == float(values.max()):
            ax.text(0.52, 0.5, "sem variação entre os trials", transform=ax.transAxes,
                    ha="center", va="center", fontsize=9, color=INK_MUTED)
            sem_variacao.append(str(spec["title"]).lower())

    nota = f" Sem variação entre os trials: {', '.join(sem_variacao)}." if sem_variacao else ""
    _frame_text(
        fig,
        "RQ3 — Qualidade estrutural do código por tratamento",
        "Caixa = IQR (Q1–Q3) · linha = mediana · hastes = mínimo e máximo · cada ponto é um trial.\n"
        "Eixos independentes: as três métricas têm unidades diferentes e não são comparáveis entre si."
        + nota,
        _source_note(df, "Família de três hipóteses (H3a/H3b/H3c) com correção de "
                         "Holm-Bonferroni: issue #47."),
        tick_lines=3,
    )
    _treatment_legend(fig)
    return fig


def figure_rq3_all(df: pd.DataFrame, *, agg: str = "median") -> dict[str, plt.Figure]:
    """Todas as figuras de RQ3: o painel combinado e uma figura por metrica."""
    figures = {"rq3_estrutura": figure_rq3_overview(df)}
    for metric in RQ3_METRICS:
        if metric in df.columns:
            figures[f"rq3_{metric}"] = figure_rq3_metric(df, metric, agg=agg)
    return figures


# --------------------------------------------------------------------------- #
# Exportacao                                                                   #
# --------------------------------------------------------------------------- #
def save_figure(fig: plt.Figure, path: Path, *, dpi: int = 200) -> Path:
    """Grava a figura (PNG por default) criando o diretorio se necessario."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, facecolor=SURFACE)
    return path


def build_figures(df: pd.DataFrame, *, agg: str = "median") -> dict[str, plt.Figure]:
    """Todas as figuras do relatorio, na ordem em que entram nele."""
    figures = {"rq1_time_to_green": figure_rq1(df, agg=agg),
               "rq2_taxa_sucesso": figure_rq2(df)}
    figures.update(figure_rq3_all(df, agg=agg))
    return figures


def export_all(df: pd.DataFrame, fig_dir: Path, *, dpi: int = 200,
               fmt: str = "png", agg: str = "median", close: bool = True) -> list[Path]:
    """Gera e grava todas as figuras em `fig_dir`; devolve os caminhos escritos."""
    written: list[Path] = []
    for name, fig in build_figures(df, agg=agg).items():
        written.append(save_figure(fig, Path(fig_dir) / f"{name}.{fmt}", dpi=dpi))
        if close:
            plt.close(fig)
    return written


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT,
                        help="raiz do repositorio (default: inferida a partir do script)")
    parser.add_argument("--fig-dir", type=Path, default=None,
                        help=f"destino das figuras (default: {FIG_DIR_DEFAULT})")
    parser.add_argument("--dpi", type=int, default=200, help="resolucao do PNG (default: 200)")
    parser.add_argument("--format", default="png", choices=["png", "pdf", "svg"],
                        help="formato de saida (default: png)")
    parser.add_argument("--agg", default="median", choices=["median", "mean", "min", "max"],
                        help="agregador dos trials de um integrante no grafico de pares")
    parser.add_argument("--quiet", action="store_true", help="nao imprime o resumo")
    args = parser.parse_args(argv)

    plt.switch_backend("Agg")  # geracao sem display (CLI/CI)

    repo_root = args.repo_root.resolve()
    df = build_dataset(repo_root=repo_root)
    fig_dir = args.fig_dir if args.fig_dir is not None else repo_root / FIG_DIR_DEFAULT
    if not fig_dir.is_absolute():
        fig_dir = repo_root / fig_dir

    written = export_all(df, fig_dir, dpi=args.dpi, fmt=args.format, agg=args.agg)

    if not args.quiet:
        print(f"{len(df)} trial(s) - fontes: {df.attrs.get('sources')}")
        print(f"censurados: {int(_censored_mask(df).sum())}")
        print(f"\n{len(written)} figura(s) em {fig_dir}:")
        for path in written:
            try:
                shown = path.relative_to(repo_root)
            except ValueError:
                shown = path
            print(f"  {shown}  ({path.stat().st_size / 1024:.0f} kB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
