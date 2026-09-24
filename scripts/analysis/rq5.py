#!/usr/bin/env python3
"""Analisa RQ5: o efeito da IA e homogeneo entre as katas?

RQ5 (diferencial do grupo) -- RQ1..RQ4 tratam "IA" como um efeito unico, medio.
RQ5 pergunta se esse efeito medio esconde heterogeneidade: o ganho de tempo
depende da tarefa? Para cada kata resolvida nos DOIS tratamentos calculamos

    speedup_kata = mediana(tempo sem IA) / mediana(tempo com IA)      [vezes]
    ganho_min    = mediana(tempo sem IA) - mediana(tempo com IA)      [minutos]

e testamos, com rho de Spearman, se o speedup acompanha a dificuldade
intrinseca da kata (proxy: a propria mediana do tempo sem IA -- quanto mais
demorada a kata na mao, mais dificil ela e para este grupo).

Atencao ao pareamento: como nenhum integrante resolveu a mesma kata duas vezes
(ver desenho, secao 5), a comparacao por kata e ENTRE PESSOAS. Isso confunde o
tratamento com a habilidade individual e e o motivo de RQ5 ser exploratoria: ela
descreve a dispersao do efeito, nao estima o efeito causal por kata.

Fonte: dados/consolidado.csv. Saida: dados/rq5_resultados.json.
"""

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

TREATMENTS = ("com IA", "sem IA")
DERIVED_SOURCE = "derivado_ou_autodeclarado"
# Dominio de cada kata (docs/katas_justificativa.md) -- rotulo das bolhas.
KATA_LABELS = {
    "kata1": "Cesta de Compras",
    "kata2": "Escala de Plantoes",
    "kata3": "Validador de Senha",
    "kata4": "Extrator de Tags",
    "kata5": "Controle de Estoque",
    "kata6": "Maquina de Catraca",
}


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"{path}: consolidado vazio")
    for row in rows:
        if row["tratamento"] not in TREATMENTS:
            raise ValueError(f"tratamento invalido: {row['tratamento']!r}")
        row["tempo_min"] = float(row["tempo_min"])
        row["loc"] = float(row["loc"])
        row["cc_total"] = float(row["cc_total"])
        row["testes_total"] = int(row["testes_total"])
        if row["tempo_min"] <= 0:
            raise ValueError(f"tempo nao positivo em {row['integrante']}/{row['kata']}")
    return rows


def median(values):
    return float(np.median(values)) if values else None


def per_kata(rows):
    """Uma linha por kata que tenha os dois tratamentos; katas com um so ficam fora."""
    katas, incompletas = [], []
    for kata in sorted({r["kata"] for r in rows}):
        group = [r for r in rows if r["kata"] == kata]
        ai = [r for r in group if r["tratamento"] == "com IA"]
        manual = [r for r in group if r["tratamento"] == "sem IA"]
        if not ai or not manual:
            incompletas.append({
                "kata": kata, "rotulo": KATA_LABELS.get(kata, kata),
                "n_com_ia": len(ai), "n_sem_ia": len(manual),
                "motivo": "kata resolvida em apenas um tratamento; sem contraste possivel",
            })
            continue
        t_ai, t_manual = median([r["tempo_min"] for r in ai]), median([r["tempo_min"] for r in manual])
        loc_ai, loc_manual = median([r["loc"] for r in ai]), median([r["loc"] for r in manual])
        katas.append({
            "kata": kata,
            "rotulo": KATA_LABELS.get(kata, kata),
            "testes_total": group[0]["testes_total"],
            "n_com_ia": len(ai), "n_sem_ia": len(manual),
            "tempo_mediano_com_ia": round(t_ai, 4),
            "tempo_mediano_sem_ia": round(t_manual, 4),
            "dificuldade_proxy_min": round(t_manual, 4),
            "speedup": round(t_manual / t_ai, 4),
            "ganho_min": round(t_manual - t_ai, 4),
            "loc_mediana_com_ia": loc_ai,
            "loc_mediana_sem_ia": loc_manual,
            "razao_loc_ia_sobre_manual": round(loc_ai / loc_manual, 4) if loc_manual else None,
            # transparencia: a kata usa algum tempo derivado (Paulo) em algum lado?
            "usa_tempo_derivado": any(r["fonte_tempo"] == DERIVED_SOURCE for r in group),
            "tempo_derivado_em": sorted({r["tratamento"] for r in group
                                         if r["fonte_tempo"] == DERIVED_SOURCE}),
            "integrantes_com_ia": sorted(r["integrante"] for r in ai),
            "integrantes_sem_ia": sorted(r["integrante"] for r in manual),
        })
    return katas, incompletas


def heterogeneity(katas):
    """Dispersao do efeito entre katas + Spearman(dificuldade, speedup)."""
    if len(katas) < 2:
        return {"n_katas": len(katas), "obs": "menos de 2 katas com contraste; sem analise"}
    speedups = [k["speedup"] for k in katas]
    difficulty = [k["dificuldade_proxy_min"] for k in katas]
    out = {
        "n_katas": len(katas),
        "speedup_min": min(speedups),
        "speedup_max": max(speedups),
        "speedup_mediana": round(float(np.median(speedups)), 4),
        "speedup_iqr": round(float(np.percentile(speedups, 75) - np.percentile(speedups, 25)), 4),
        "razao_max_min": round(max(speedups) / min(speedups), 4),
        "katas_com_ia_mais_lenta": [k["kata"] for k in katas if k["speedup"] < 1],
        "ganho_min_mediano": round(float(np.median([k["ganho_min"] for k in katas])), 4),
    }
    if len(katas) >= 3 and np.ptp(speedups) > 0 and np.ptp(difficulty) > 0:
        rho, p = spearmanr(difficulty, speedups)
        out["spearman_dificuldade_x_speedup"] = {
            "rho": round(float(rho), 4), "p": round(float(p), 4), "n": len(katas),
            "leitura": ("rho > 0 indica que katas mais demoradas na mao sao as que mais "
                        "se beneficiam da IA"),
        }
    else:
        out["spearman_dificuldade_x_speedup"] = {
            "rho": None, "p": None, "n": len(katas),
            "obs": "n < 3 katas ou variancia nula: correlacao nao definida",
        }
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    rows = read_rows(root / "dados/consolidado.csv")

    planned = [r for r in rows if r["no_plano_4_katas"] == "true"]
    timed = [r for r in rows if r["fonte_tempo"] != DERIVED_SOURCE]

    katas, incompletas = per_kata(planned)
    katas_timed, incompletas_timed = per_kata(timed)

    results = {
        "questao": ("RQ5 (diferencial) -- o efeito do assistente de IA sobre o tempo e "
                    "homogeneo entre as katas, ou depende da dificuldade da tarefa?"),
        "hipoteses": {
            "H5_0": "o speedup e o mesmo em todas as katas e nao se associa a dificuldade",
            "H5_1": ("o speedup varia entre katas e/ou cresce com a dificuldade "
                     "(bicaudal, alfa = 0,05, exploratoria)"),
        },
        "metricas": {
            "speedup": "mediana(tempo sem IA) / mediana(tempo com IA), em vezes",
            "ganho_min": "mediana(tempo sem IA) - mediana(tempo com IA), em minutos",
            "dificuldade_proxy_min": "mediana(tempo sem IA) da kata, em minutos",
            "razao_loc_ia_sobre_manual": "LOC mediana com IA / LOC mediana sem IA",
        },
        "aviso_pareamento": ("contraste entre pessoas: ninguem resolveu a mesma kata nos dois "
                             "tratamentos, entao habilidade individual e tratamento nao sao "
                             "separaveis por kata"),
        "primario": {
            "conjunto": "12 trials do plano de 4 katas (inclui os tempos derivados de Paulo)",
            "n_trials": len(planned),
            "katas": katas,
            "heterogeneidade": heterogeneity(katas),
            "katas_sem_contraste": incompletas,
        },
        "sensibilidade_so_cronometrados": {
            "conjunto": "apenas trials com tempo cronometrado (exclui os 4 derivados)",
            "n_trials": len(timed),
            "katas": katas_timed,
            "heterogeneidade": heterogeneity(katas_timed),
            "katas_sem_contraste": incompletas_timed,
        },
    }

    output = root / "dados/rq5_resultados.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"RQ5: {len(katas)} katas com os dois tratamentos (de {len({r['kata'] for r in planned})} no plano)")
    for kata in katas:
        flag = " [tempo derivado]" if kata["usa_tempo_derivado"] else ""
        print(f"  {kata['kata']} {kata['rotulo']:<20} sem IA={kata['tempo_mediano_sem_ia']:>8.4f} min  "
              f"com IA={kata['tempo_mediano_com_ia']:>8.4f} min  speedup={kata['speedup']:>8.2f}x"
              f"  ganho={kata['ganho_min']:>8.2f} min{flag}")
    het = results["primario"]["heterogeneidade"]
    print(f"  speedup: mediana={het['speedup_mediana']}x, de {het['speedup_min']}x a {het['speedup_max']}x "
          f"(razao max/min = {het['razao_max_min']}x)")
    print(f"  Spearman(dificuldade, speedup) = {het['spearman_dificuldade_x_speedup']}")
    print(f"-> {output.relative_to(root)}")


if __name__ == "__main__":
    main()
