#!/usr/bin/env python3
"""Figuras avancadas do dashboard -- um tipo de grafico por RQ.

Complementa plots.py (boxplot/pares, issue #49) com uma figura dedicada por
questao de pesquisa, cada uma em um tipo de grafico diferente, escolhido pelo
tipo de pergunta e nao por gosto:

    RQ1  tempo             -> violino   (forma da distribuicao + pares)
    RQ2  defeitos          -> heatmap   (matriz integrante x kata; teto de 100%)
    RQ3  estrutura         -> box plot  (mediana/IQR das 4 metricas estruturais)
    RQ4  tempo x estrutura -> dispersao + Pearson (associacao entre duas medidas)
    RQ5  efeito por kata   -> bolhas    (3 dimensoes: dificuldade, speedup, LOC)

Identidade visual, paleta e helpers de moldura vem de plots.py, para que as
figuras novas e as antigas saiam do mesmo sistema. A paleta dos tratamentos
passa nos seis checks de contraste/daltonismo (dE CVD 24,7; dE normal 33,6).

As estatisticas anotadas em RQ4 e RQ5 sao LIDAS de dados/rq4_resultados.json e
dados/rq5_resultados.json -- as figuras nao recalculam teste nenhum, para que
grafico, JSON e relatorio nunca discordem. Rode antes:

    python scripts/analysis/rq4.py
    python scripts/analysis/rq5.py

Uso:

    python scripts/dashboard/plots_advanced.py                 # grava todas
    python scripts/dashboard/plots_advanced.py --fig-dir /tmp  # destino custom
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

sys.path.insert(0, str(Path(__file__).resolve().parent))

from load_data import REPO_ROOT, build_dataset  # noqa: E402
from plots import (  # noqa: E402
    FIG_DIR_DEFAULT,
    GRID,
    INK,
    INK_MUTED,
    INK_SECONDARY,
    SURFACE,
    TREATMENT_COLORS,
    TREATMENT_LABELS,
    TREATMENT_ORDER,
    TREATMENT_SHORT,
    _clean_axes,
    _fmt,
    _frame_text,
    _repel,
    _source_note,
    apply_style,
    save_figure,
)

JITTER_SEED = 20260923  # mesmo seed de plots.py: figura reproduzivel
DERIVED_SOURCE = "derivado_ou_autodeclarado"

# Rampa sequencial de um unico tom (claro -> escuro) para o heatmap de RQ2:
# magnitude pede um hue so, com luminosidade monotona.
SEQUENTIAL = LinearSegmentedColormap.from_list(
    "azul_seq", ["#eef4fc", "#2a78d6", "#123a69"])
# Rampa divergente de RQ5: dois polos + cinza neutro no meio. Os polos reusam
# as cores dos tratamentos porque o significado e o mesmo -- laranja = o lado
# "com IA" e maior, azul = o lado "sem IA" e maior.
DIVERGING = LinearSegmentedColormap.from_list(
    "loc_div", [TREATMENT_COLORS["manual"], "#d8d7d2", TREATMENT_COLORS["ai"]])


# --------------------------------------------------------------------------- #
# Helpers locais                                                               #
# --------------------------------------------------------------------------- #
def _timed_mask(df: pd.DataFrame) -> pd.Series:
    """True onde o tempo foi cronometrado (exclui os tempos derivados de Paulo)."""
    if "fonte_tempo" not in df.columns:
        return pd.Series(True, index=df.index)
    return df["fonte_tempo"].astype("string").fillna("") != DERIVED_SOURCE


def _density(df: pd.DataFrame) -> pd.Series:
    """Densidade de complexidade: CC total por 100 LOC (RQ3/RQ4 normalizado)."""
    loc = pd.to_numeric(df["loc"], errors="coerce")
    return 100.0 * pd.to_numeric(df["cc_total"], errors="coerce") / loc.where(loc > 0)


def _load_results(repo_root: Path, name: str) -> dict:
    path = repo_root / "dados" / f"{name}_resultados.json"
    if not path.exists():
        raise SystemExit(
            f"{path} nao existe -- rode antes: python scripts/analysis/{name}.py")
    return json.loads(path.read_text(encoding="utf-8"))


def _jitter(n: int, spread: float = 0.055) -> np.ndarray:
    return np.random.default_rng(JITTER_SEED).uniform(-spread, spread, n)


def _treatment_handles(*, derived: bool = False) -> list[plt.Line2D]:
    handles = [
        plt.Line2D([], [], marker="o", linestyle="none", markersize=7,
                   markerfacecolor=TREATMENT_COLORS[t], markeredgecolor=SURFACE,
                   label=TREATMENT_LABELS[t])
        for t in TREATMENT_ORDER
    ]
    if derived:
        handles.append(plt.Line2D([], [], marker="o", linestyle="none", markersize=7,
                                  markerfacecolor=SURFACE, markeredgecolor=INK_SECONDARY,
                                  label="tempo derivado (fora do ajuste)"))
    return handles


# --------------------------------------------------------------------------- #
# RQ1 - violino                                                                #
# --------------------------------------------------------------------------- #
def figure_rq1_violin(df: pd.DataFrame) -> plt.Figure:
    """RQ1 em violino: a forma da distribuicao do time-to-green, nao so a caixa.

    O boxplot da issue #49 mostra mediana e IQR; o violino mostra onde a massa
    da distribuicao esta -- aqui, dois modos bem separados (segundos com IA,
    minutos sem IA). Eixo em log10 porque os tempos variam duas ordens de
    grandeza (0,13 a 20,13 min) e, em escala linear, todos os trials com IA
    colapsariam sobre o zero.
    """
    fig, ax = plt.subplots(figsize=(8.6, 5.9))
    _clean_axes(ax)

    groups, positions = {}, {"manual": 0.0, "ai": 1.0}
    for treatment in TREATMENT_ORDER:
        values = pd.to_numeric(
            df.loc[df["treatment"].astype("string") == treatment, "time_to_green_min"],
            errors="coerce").dropna()
        groups[treatment] = values[values > 0]

    for treatment, values in groups.items():
        if len(values) < 2:
            continue
        parts = ax.violinplot([np.log10(values)], positions=[positions[treatment]],
                              widths=0.62, showextrema=False, showmedians=False)
        for body in parts["bodies"]:
            body.set_facecolor(TREATMENT_COLORS[treatment])
            body.set_alpha(0.28)
            body.set_edgecolor(TREATMENT_COLORS[treatment])
            body.set_linewidth(1.2)

    # pares por integrante: uma linha ligando a mediana manual -> mediana com IA.
    # Tracejada quando o integrante tem tempo derivado (Paulo): a linha existe,
    # mas nao vale como medicao.
    frame = df.assign(t=df["treatment"].astype("string"), timed=_timed_mask(df))
    paired = frame.pivot_table(index="participant", columns="t",
                               values="time_to_green_min", aggfunc="median")
    derived_people = set(frame.loc[~frame["timed"], "participant"].dropna())
    labels: list[tuple[str, float]] = []
    for participant, row in paired.iterrows():
        if pd.isna(row.get("manual")) or pd.isna(row.get("ai")):
            continue
        y = [float(np.log10(row["manual"])), float(np.log10(row["ai"]))]
        ax.plot([positions["manual"], positions["ai"]], y, color=INK_MUTED,
                linewidth=1.0, alpha=0.8, zorder=2,
                linestyle=(0, (3, 2)) if participant in derived_people else "-")
        suffix = " (derivado)" if participant in derived_people else ""
        labels.append((f"{participant}{suffix}", y[1]))

    # rotulos dos integrantes, afastados entre si para nao colidirem
    if labels:
        span = 2.6  # altura util do eixo em decadas (log10 de 0,10 a 40)
        for (name, _), y in zip(labels, _repel([y for _, y in labels], span)):
            ax.annotate(name, (positions["ai"] + 0.36, y), color=INK_SECONDARY,
                        fontsize=8.5, va="center", ha="left")

    # cada trial como um ponto, com jitter deterministico
    tick_labels = []
    for treatment, values in groups.items():
        x = positions[treatment] + _jitter(len(values))
        ax.scatter(x, np.log10(values), s=42, color=TREATMENT_COLORS[treatment],
                   edgecolor=SURFACE, linewidth=1.0, zorder=3)
        median = float(values.median())
        q1, q3 = float(values.quantile(.25)), float(values.quantile(.75))
        ax.plot([positions[treatment] - 0.31, positions[treatment] + 0.31],
                [np.log10(median)] * 2, color=INK, linewidth=2.0, zorder=4)
        # valor da mediana fora do violino (a esquerda): nao briga com os pontos
        ax.annotate(f"{_fmt(median, 2)} min", (positions[treatment] - 0.34, np.log10(median)),
                    ha="right", va="center", fontsize=9.5, fontweight="bold",
                    color=INK, zorder=5)
        tick_labels.append(f"{TREATMENT_SHORT[treatment]}\nn = {len(values)} · "
                           f"IQR {_fmt(q3 - q1, 2)} min")

    ticks = [0.1, 0.25, 0.5, 1, 2.5, 5, 10, 20, 35]
    ax.set_yticks(np.log10(ticks))
    ax.set_yticklabels([_fmt(t, 2) if t < 1 else _fmt(t, 0) for t in ticks])
    ax.axhline(np.log10(35), color=INK_MUTED, linewidth=1.0, linestyle=(0, (4, 3)), zorder=1)
    ax.annotate("time-box 35 min (nenhum trial censurado)", (1.95, np.log10(35)),
                xytext=(0, 6), textcoords="offset points", ha="right",
                fontsize=8.5, color=INK_MUTED)
    ax.set_xticks(list(positions.values()))
    ax.set_xticklabels(tick_labels)
    ax.set_xlim(-0.75, 2.0)
    ax.set_ylim(np.log10(0.085), np.log10(42))
    ax.set_ylabel("Tempo até o verde (min, escala log₁₀)")

    _frame_text(
        fig,
        "RQ1 · Tempo até o verde: com IA vs. sem IA",
        "Violino = densidade da distribuição; ponto = 1 trial; linha cinza = o mesmo integrante nos dois\n"
        "tratamentos; traço preto = mediana. Escala log₁₀ (os tempos variam de 0,13 a 20,13 min).",
        _source_note(df, "Mediana e IQR, não média, pelo N pequeno (desenho, §7)."),
    )
    fig.legend(handles=_treatment_handles(), loc="lower left",
               bbox_to_anchor=(0.012, getattr(fig, "legend_bottom_y", 0.06)),
               ncol=2, labelcolor=INK_SECONDARY, handletextpad=0.5, columnspacing=1.6)
    return fig


# --------------------------------------------------------------------------- #
# RQ2 - heatmap                                                                #
# --------------------------------------------------------------------------- #
def figure_rq2_heatmap(df: pd.DataFrame) -> plt.Figure:
    """RQ2 em heatmap: a matriz integrante x kata dos testes de aceitacao.

    Escolha do tipo: RQ2 tem teto (todo trial fechado como verde tem 100% dos
    testes passando), entao um boxplot viraria uma linha reta. O heatmap mostra
    as duas informacoes que sobram e importam: o teto em si -- 14 celulas em
    100% -- e a COBERTURA do desenho (quem fez o que, em qual tratamento),
    incluindo as lacunas.
    """
    frame = df.copy()
    frame["t"] = frame["treatment"].astype("string")
    participants = sorted(frame["participant"].dropna().unique())
    katas = sorted(frame["kata"].dropna().unique())

    fig, ax = plt.subplots(figsize=(9.0, 5.9))
    grid = np.full((len(participants), len(katas)), np.nan)
    for _, row in frame.iterrows():
        pct = pd.to_numeric(pd.Series([row.get("pct_tests_passing")]), errors="coerce").iloc[0]
        if pd.notna(pct):
            grid[participants.index(row["participant"]), katas.index(row["kata"])] = pct

    ax.imshow(np.ma.masked_invalid(grid), cmap=SEQUENTIAL, vmin=0, vmax=100,
              aspect="auto")
    ax.set_facecolor("#f2f1ec")  # celulas sem trial

    for i, participant in enumerate(participants):
        for j, kata in enumerate(katas):
            hit = frame[(frame["participant"] == participant) & (frame["kata"] == kata)]
            if hit.empty:
                ax.annotate("—", (j, i), ha="center", va="center",
                            color=INK_MUTED, fontsize=11)
                continue
            row = hit.iloc[0]
            treatment = row["t"]
            passed, total = row.get("tests_passed"), row.get("tests_total")
            # anel de 2 px na cor do tratamento: identidade sem depender do preenchimento
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False,
                                       edgecolor=TREATMENT_COLORS.get(treatment, INK_MUTED),
                                       linewidth=2.4, zorder=3))
            ax.annotate(f"{_fmt(row.get('pct_tests_passing'), 0)}%", (j, i - 0.12),
                        ha="center", va="center", color=SURFACE, fontsize=11,
                        fontweight="bold", zorder=4)
            ax.annotate(f"{int(passed)}/{int(total)} · {TREATMENT_SHORT.get(treatment, '?')}",
                        (j, i + 0.22), ha="center", va="center", color=SURFACE,
                        fontsize=8.5, zorder=4)

    ax.set_xticks(range(len(katas)))
    ax.set_xticklabels([k.replace("kata", "Kata ") for k in katas])
    ax.set_yticks(range(len(participants)))
    ax.set_yticklabels([p.capitalize() for p in participants])
    ax.set_xticks(np.arange(-0.5, len(katas), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(participants), 1), minor=True)
    ax.grid(which="minor", color=SURFACE, linewidth=2.5)
    ax.grid(which="major", visible=False)
    ax.tick_params(length=0)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)

    failures = pd.to_numeric(frame.get("tests_failed"), errors="coerce").fillna(0).sum()
    _frame_text(
        fig,
        "RQ2 · Testes de aceitação aprovados por trial",
        "Cor = % de testes aprovados no fechamento do trial (rampa 0–100%); anel = tratamento;\n"
        "“—” = kata que o integrante não resolveu. Todas as 14 células estão em 100%.",
        _source_note(frame, f"Falhas absolutas somadas: {int(failures)} em {len(frame)} trials. "
                            "Efeito de teto: o registro fecha o trial como verde só quando\n"
                            "todos os testes passam, então a taxa quase não varia — ver docs/analise-rq2.md."),
        tick_lines=1,
    )
    fig.legend(handles=_treatment_handles(), loc="lower left",
               bbox_to_anchor=(0.012, getattr(fig, "legend_bottom_y", 0.06)),
               ncol=2, labelcolor=INK_SECONDARY, handletextpad=0.5, columnspacing=1.6)
    return fig


# --------------------------------------------------------------------------- #
# RQ3 - box plot                                                               #
# --------------------------------------------------------------------------- #
RQ3_PANELS = [
    ("cc_avg", "H3a · CC média por função", "CC média"),
    ("duplication_pct", "H3b · Linhas duplicadas", "Duplicação (%)"),
    ("loc", "H3c · Tamanho da solução", "LOC"),
    ("densidade_cc", "Controle · CC total por 100 LOC", "CC / 100 LOC"),
]


def figure_rq3_box(df: pd.DataFrame) -> plt.Figure:
    """RQ3 em box plot: as tres hipoteses estruturais + a normalizacao por LOC.

    O quarto painel e o controle que o enunciado exige: complexidade sem
    normalizar por tamanho engana, porque codigo gerado por IA pode ser mais
    verboso. Caixa = IQR, linha = mediana, hastes = min-max, e todos os trials
    aparecem como pontos (nenhum "outlier escondido").
    """
    frame = df.copy()
    frame["densidade_cc"] = _density(frame)
    frame["t"] = frame["treatment"].astype("string")

    fig, axes = plt.subplots(1, len(RQ3_PANELS), figsize=(11.4, 5.9))
    for ax, (metric, title, ylabel) in zip(axes, RQ3_PANELS):
        _clean_axes(ax)
        data, labels = [], []
        for index, treatment in enumerate(TREATMENT_ORDER):
            values = pd.to_numeric(frame.loc[frame["t"] == treatment, metric],
                                   errors="coerce").dropna()
            data.append(values.to_numpy())
            labels.append(f"{TREATMENT_SHORT[treatment]}\nn = {len(values)}")
            if len(values):
                x = index + 1 + _jitter(len(values), 0.075)
                ax.scatter(x, values, s=34, color=TREATMENT_COLORS[treatment],
                           edgecolor=SURFACE, linewidth=0.9, zorder=3, alpha=0.95)
        box = ax.boxplot(data, widths=0.5, showfliers=False, patch_artist=True,
                         medianprops={"color": INK, "linewidth": 2.0},
                         whiskerprops={"color": GRID, "linewidth": 1.0},
                         capprops={"color": GRID, "linewidth": 1.0}, zorder=2)
        for patch, treatment in zip(box["boxes"], TREATMENT_ORDER):
            patch.set_facecolor(TREATMENT_COLORS[treatment])
            patch.set_alpha(0.20)
            patch.set_edgecolor(TREATMENT_COLORS[treatment])
            patch.set_linewidth(1.2)
        for index, values in enumerate(data):
            if len(values):
                median = float(np.median(values))
                decimals = 0 if metric == "loc" else (1 if metric != "cc_avg" else 2)
                ax.annotate(_fmt(median, decimals), (index + 1, median),
                            xytext=(0, 9), textcoords="offset points", ha="center",
                            fontsize=9.5, fontweight="bold", color=INK, zorder=5)
        ax.set_xticks([1, 2])
        ax.set_xticklabels(labels)
        ax.set_title(title, color=INK, pad=8)
        ax.set_ylabel(ylabel)
        if metric == "duplication_pct":
            # metrica degenerada: 0% em todos os trials. Eixo ancorado em zero
            # (sem ticks negativos, que nao existem em percentual de linhas).
            ax.set_ylim(-0.06, 1.0)
            ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
            ax.annotate(f"0% nos {len(frame)} trials\n(jscpd; sem par a ordenar)", (1.5, 0.55),
                        ha="center", fontsize=8.5, color=INK_MUTED)

    _frame_text(
        fig,
        "RQ3 · Estrutura do código produzido, por tratamento",
        "Caixa = IQR (Q1–Q3), linha preta = mediana, hastes = mínimo–máximo; cada ponto é um trial.\n"
        "O 4º painel normaliza a complexidade pelo tamanho — sem isso, LOC e complexidade se confundem.",
        _source_note(frame, "Radon (cc_avg, cc_total, loc, mi_avg) e jscpd (duplication_pct); "
                            "Wilcoxon pareado por integrante com Holm em docs/analise-rq3.md."),
    )
    fig.legend(handles=_treatment_handles(), loc="lower left",
               bbox_to_anchor=(0.012, getattr(fig, "legend_bottom_y", 0.06)),
               ncol=2, labelcolor=INK_SECONDARY, handletextpad=0.5, columnspacing=1.6)
    fig.subplots_adjust(wspace=0.36)
    return fig


# --------------------------------------------------------------------------- #
# RQ4 - dispersao + Pearson                                                    #
# --------------------------------------------------------------------------- #
#           chave no JSON, coluna do dataset, rotulo do eixo, canto livre da caixa
RQ4_PANELS = [
    ("mi_medio", "mi_avg", "Maintainability Index médio (Radon)", (0.97, 0.03, "right", "bottom")),
    ("densidade_cc", "densidade_cc", "CC total por 100 LOC", (0.97, 0.97, "right", "top")),
]


def figure_rq4_scatter(df: pd.DataFrame, results: dict) -> plt.Figure:
    """RQ4 em dispersao: tempo no eixo x, estrutura no eixo y, r de Pearson anotado.

    A pergunta e de relacao entre duas medidas numericas -- o grafico proprio e
    a dispersao. A reta e o ajuste de minimos quadrados sobre os 10 trials
    cronometrados (os 4 tempos derivados entram como marca vazada, fora do
    ajuste). r, p, IC95 e p de Holm vem de dados/rq4_resultados.json.
    """
    frame = df.copy()
    frame["densidade_cc"] = _density(frame)
    frame["t"] = frame["treatment"].astype("string")
    frame["timed"] = _timed_mask(frame)

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 5.9))
    holm = results["primario"]["holm_global"]["pearson"]

    for ax, (json_key, column, ylabel, corner) in zip(axes, RQ4_PANELS):
        _clean_axes(ax, grid_axis="both")
        stat = results["primario"]["global"][json_key]
        for treatment in TREATMENT_ORDER:
            for timed in (True, False):
                subset = frame[(frame["t"] == treatment) & (frame["timed"] == timed)]
                if subset.empty:
                    continue
                ax.scatter(pd.to_numeric(subset["time_to_green_min"], errors="coerce"),
                           pd.to_numeric(subset[column], errors="coerce"),
                           s=64 if timed else 58,
                           color=TREATMENT_COLORS[treatment] if timed else SURFACE,
                           edgecolor=SURFACE if timed else TREATMENT_COLORS[treatment],
                           linewidth=1.2, zorder=3)
        fitted = frame[frame["timed"]]
        x = pd.to_numeric(fitted["time_to_green_min"], errors="coerce")
        y = pd.to_numeric(fitted[column], errors="coerce")
        mask = x.notna() & y.notna()
        if mask.sum() >= 3:
            slope, intercept = np.polyfit(x[mask], y[mask], 1)
            line_x = np.linspace(float(x[mask].min()), float(x[mask].max()), 50)
            ax.plot(line_x, slope * line_x + intercept, color=INK_SECONDARY,
                    linewidth=1.6, zorder=2)
        ic = stat.get("ic95_pearson")
        ic_text = f"IC95 [{_fmt(ic[0], 2)}; {_fmt(ic[1], 2)}]" if ic else "IC95 –"
        ax.annotate(
            f"r de Pearson = {_fmt(stat['pearson_r'], 2)}   (n = {stat['n']})\n"
            f"p = {_fmt(stat['pearson_p'], 3)} · Holm p = {_fmt(holm.get(json_key), 3)}\n"
            f"{ic_text} · ρ de Spearman = {_fmt(stat['spearman_rho'], 2)}",
            corner[:2], xycoords="axes fraction", ha=corner[2], va=corner[3],
            fontsize=9, color=INK_SECONDARY, linespacing=1.5, zorder=6,
            bbox={"facecolor": SURFACE, "edgecolor": GRID, "boxstyle": "round,pad=0.45"})
        ax.set_xlabel("Tempo até o verde (min)")
        ax.set_ylabel(ylabel)
        ax.set_title(f"Tempo × {ylabel.split(' (')[0]}", color=INK, pad=8)

    _frame_text(
        fig,
        "RQ4 · O ganho de velocidade vem com estrutura diferente?",
        "Cada ponto é um trial. Reta = ajuste de mínimos quadrados sobre os 10 trials cronometrados;\n"
        "marca vazada = tempo derivado (fora do ajuste). Os dois grupos formam duas nuvens separadas:\n"
        "a associação está confundida com o tratamento, e não é um efeito do tempo em si.",
        _source_note(frame, "Estatísticas de dados/rq4_resultados.json (scripts/analysis/rq4.py); "
                            "Holm sobre a família de 5 métricas estruturais."),
        tick_lines=3,  # espaco extra: estes paineis tem rotulo de eixo x
    )
    fig.legend(handles=_treatment_handles(derived=True), loc="lower left",
               bbox_to_anchor=(0.012, getattr(fig, "legend_bottom_y", 0.06)),
               ncol=3, labelcolor=INK_SECONDARY, handletextpad=0.5, columnspacing=1.6)
    fig.subplots_adjust(wspace=0.28)
    return fig


# --------------------------------------------------------------------------- #
# RQ5 - bolhas                                                                 #
# --------------------------------------------------------------------------- #
def figure_rq5_bubbles(results: dict) -> plt.Figure:
    """RQ5 em bolhas: tres dimensoes por kata em um plano.

    x = dificuldade da kata (mediana do tempo sem IA), y = speedup (quantas
    vezes a IA foi mais rapida), area = numero de testes de aceitacao, cor =
    razao de LOC (com IA / sem IA, divergente em torno de 1). Contorno tracejado
    marca as katas cujo tempo de um dos lados e derivado, nao cronometrado.
    """
    katas = results["primario"]["katas"]
    het = results["primario"]["heterogeneidade"]
    sensitivity = results["sensibilidade_so_cronometrados"]["heterogeneidade"]
    if not katas:
        raise SystemExit("RQ5: nenhuma kata com os dois tratamentos")

    fig, ax = plt.subplots(figsize=(9.4, 5.9))
    _clean_axes(ax, grid_axis="both")

    ratios = [k["razao_loc_ia_sobre_manual"] or 1.0 for k in katas]
    span = max(0.35, max(abs(np.log2(r)) for r in ratios))
    norm = TwoSlopeNorm(vmin=-span, vcenter=0.0, vmax=span)  # simetrica em log2

    for index, (kata, ratio) in enumerate(zip(katas, ratios)):
        x, y = kata["dificuldade_proxy_min"], kata["speedup"]
        dashed = kata["usa_tempo_derivado"]
        radius_pt = np.sqrt(110 * kata["testes_total"]) / 2.0
        ax.scatter([x], [np.log10(y)], s=110 * kata["testes_total"],
                   color=DIVERGING(norm(np.log2(ratio))),
                   edgecolor=INK_SECONDARY if dashed else SURFACE,
                   linewidth=1.6, linestyle="--" if dashed else "-",
                   zorder=3, alpha=0.92)
        # rotulo abaixo das bolhas altas e acima das baixas: nunca sai do eixo
        # rotulo ao lado da bolha, no centro dela. Vai para a esquerda quando
        # houver outra bolha logo a direita e na mesma faixa de altura -- e o
        # unico caso em que o rotulo a direita passaria por cima dela.
        x_span = max(k["dificuldade_proxy_min"] for k in katas) or 1.0
        blocked = any(
            other["dificuldade_proxy_min"] > x
            and other["dificuldade_proxy_min"] - x < 0.35 * x_span
            and abs(np.log10(other["speedup"]) - np.log10(y)) < 0.25
            for other in katas)
        ax.annotate(f"{kata['rotulo']}\n{_fmt(y, 2)}× · {_fmt(kata['ganho_min'], 1)} min",
                    (x, np.log10(y)),
                    xytext=(-(radius_pt + 10) if blocked else radius_pt + 10, 0),
                    textcoords="offset points",
                    ha="right" if blocked else "left", va="center",
                    fontsize=9, color=INK_SECONDARY, linespacing=1.4, zorder=4)

    ax.axhline(0.0, color=INK_MUTED, linewidth=1.0, linestyle=(0, (4, 3)), zorder=1)
    # margem a direita reservada para os rotulos das bolhas (calculada, nao fixa)
    x_max = max(k["dificuldade_proxy_min"] for k in katas)
    ax.set_xlim(-1.5, x_max * 1.55 + 2)
    ax.annotate("1× = sem ganho; abaixo da linha, a IA foi mais lenta",
                (ax.get_xlim()[1] - 0.4, 0.0), xytext=(0, -12),
                textcoords="offset points", ha="right", va="top",
                fontsize=8.5, color=INK_MUTED)

    ticks = [0.5, 1, 2, 5, 10, 20, 40]
    ax.set_yticks(np.log10(ticks))
    ax.set_yticklabels([f"{_fmt(t, 1) if t < 1 else _fmt(t, 0)}×" for t in ticks])
    ax.set_ylim(np.log10(0.3), np.log10(95))
    ax.set_xlabel("Dificuldade da kata — mediana do tempo sem IA (min)")
    ax.set_ylabel("Speedup: tempo sem IA ÷ tempo com IA (escala log₁₀)")

    bar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=DIVERGING), ax=ax,
                       pad=0.02, fraction=0.045)
    bar.set_label("log₂(LOC com IA ÷ LOC sem IA)", color=INK_SECONDARY, fontsize=9)
    bar.ax.tick_params(labelsize=8, length=0, colors=INK_SECONDARY)
    bar.outline.set_visible(False)

    size_handles = [
        plt.Line2D([], [], marker="o", linestyle="none",
                   markersize=np.sqrt(110 * n) / 3.4, markerfacecolor="#d8d7d2",
                   markeredgecolor=SURFACE, label=f"{n} testes de aceitação")
        for n in (min(k["testes_total"] for k in katas), max(k["testes_total"] for k in katas))
    ]
    size_handles.append(plt.Line2D([], [], marker="o", linestyle="none", markersize=9,
                                   markerfacecolor="#f2f1ec", markeredgecolor=INK_SECONDARY,
                                   label="usa tempo derivado (contorno tracejado)"))

    spearman = het.get("spearman_dificuldade_x_speedup", {})
    _frame_text(
        fig,
        "RQ5 · O efeito da IA é o mesmo em toda kata?",
        f"Uma bolha por kata resolvida nos dois tratamentos (n = {het['n_katas']}). Área = nº de testes;\n"
        f"cor = quanto a solução com IA é maior/menor em LOC. Speedup varia "
        f"{_fmt(het['speedup_min'], 2)}×–{_fmt(het['speedup_max'], 2)}× "
        f"(mediana {_fmt(het['speedup_mediana'], 2)}×; {_fmt(het['razao_max_min'], 0)}× entre extremos).",
        f"Fonte: dados/rq5_resultados.json (scripts/analysis/rq5.py). ρ de Spearman(dificuldade, "
        f"speedup) = {_fmt(spearman.get('rho'), 2)} "
        f"(p = {_fmt(spearman.get('p'), 2)}, n = {spearman.get('n')}) — sem associação detectada.\n"
        f"Só com trials cronometrados a heterogeneidade quase desaparece: "
        f"{_fmt(sensitivity['speedup_min'], 1)}×–{_fmt(sensitivity['speedup_max'], 1)}× "
        f"em {sensitivity['n_katas']} katas.\n"
        f"Contraste entre pessoas: ninguém resolveu a mesma kata nos dois tratamentos (desenho, §5).",
        tick_lines=3,
    )
    fig.legend(handles=size_handles, loc="lower left",
               bbox_to_anchor=(0.012, getattr(fig, "legend_bottom_y", 0.06)),
               ncol=3, labelcolor=INK_SECONDARY, handletextpad=0.8, columnspacing=1.8)
    return fig


# --------------------------------------------------------------------------- #
# Orquestracao                                                                 #
# --------------------------------------------------------------------------- #
FIGURE_NAMES = {
    "rq1_violino_tempo": "RQ1 — violino do time-to-green",
    "rq2_heatmap_testes": "RQ2 — heatmap dos testes aprovados",
    "rq3_boxplot_estrutura": "RQ3 — box plot das métricas estruturais",
    "rq4_dispersao_pearson": "RQ4 — dispersão tempo × estrutura (Pearson)",
    "rq5_bolhas_speedup": "RQ5 — bolhas do speedup por kata",
}


def build_advanced_figures(df: pd.DataFrame, repo_root: Path = REPO_ROOT) -> dict[str, plt.Figure]:
    """Uma figura por RQ, cada uma em um tipo de grafico diferente."""
    apply_style()
    return {
        "rq1_violino_tempo": figure_rq1_violin(df),
        "rq2_heatmap_testes": figure_rq2_heatmap(df),
        "rq3_boxplot_estrutura": figure_rq3_box(df),
        "rq4_dispersao_pearson": figure_rq4_scatter(df, _load_results(repo_root, "rq4")),
        "rq5_bolhas_speedup": figure_rq5_bubbles(_load_results(repo_root, "rq5")),
    }


def export_advanced(df: pd.DataFrame, fig_dir: Path, *, dpi: int = 200,
                    fmt: str = "png", repo_root: Path = REPO_ROOT,
                    close: bool = True) -> list[Path]:
    written = []
    for name, fig in build_advanced_figures(df, repo_root).items():
        written.append(save_figure(fig, Path(fig_dir) / f"{name}.{fmt}", dpi=dpi))
        if close:
            plt.close(fig)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--fig-dir", type=Path, default=None)
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--format", default="png", choices=["png", "pdf", "svg"])
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    plt.switch_backend("Agg")
    repo_root = args.repo_root.resolve()
    df = build_dataset(repo_root=repo_root)
    fig_dir = args.fig_dir if args.fig_dir is not None else repo_root / FIG_DIR_DEFAULT
    if not fig_dir.is_absolute():
        fig_dir = repo_root / fig_dir

    written = export_advanced(df, fig_dir, dpi=args.dpi, fmt=args.format, repo_root=repo_root)
    if not args.quiet:
        print(f"{len(df)} trials; {len(written)} figuras em {fig_dir}:")
        for path in written:
            print(f"  {path.name:<32} {FIGURE_NAMES.get(path.stem, '')} "
                  f"({path.stat().st_size / 1024:.0f} kB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
