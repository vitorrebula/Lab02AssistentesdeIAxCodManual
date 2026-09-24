#!/usr/bin/env python3
"""Gera o Relatorio Final em .docx a partir do Markdown, usando o template da disciplina.

Entrada : docs/RELATORIO_FINAL.md  +  Template_Relatorio_Laboratorio.docx
Saida   : RelatorioFinal_Lab02.docx (na raiz do repositorio)

Por que existir: o professor entrega um template .docx e o relatorio precisa sair
nesse formato, mas manter o texto em Markdown no repositorio e o que permite
revisar por diff e citar arquivos/figuras por caminho relativo. Este script
resolve os dois: le o Markdown, reaproveita os ESTILOS do template (fontes,
cabecalhos, tabela) e monta o .docx com as figuras embutidas.

O corpo do template e limpo antes da escrita -- os paragrafos de "ORIENTACAO"
sao instrucoes de preenchimento, nao conteudo -- mas a parte de estilos e a
secao de pagina (margens, tamanho) do template sao preservadas.

Uso:
    python -m pip install python-docx
    python scripts/report/build_docx.py
    python scripts/report/build_docx.py --input docs/RELATORIO_FINAL.md --output /tmp/r.docx
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

REPO_ROOT = Path(__file__).resolve().parents[2]

# Inline: **negrito**, *italico*, `codigo`, [texto](link), ![alt](img)
INLINE = re.compile(r"(\*\*.+?\*\*|(?<!\*)\*[^*]+?\*(?!\*)|`[^`]+`|\[[^\]]+\]\([^)]+\))")
IMAGE = re.compile(r"^!\[(?P<alt>[^\]]*)\]\((?P<src>[^)]+)\)\s*$")
HEADING = re.compile(r"^(?P<level>#{1,6})\s+(?P<text>.+?)\s*$")
BULLET = re.compile(r"^(?P<indent>\s*)[-*]\s+(?P<text>.+?)\s*$")
ORDERED = re.compile(r"^(?P<indent>\s*)(?P<num>\d+)\.\s+(?P<text>.+?)\s*$")
TABLE_SEP = re.compile(r"^\|[\s:|-]+\|$")

CODE_FONT = "Consolas"
LINK_COLOR = RGBColor(0x1F, 0x5C, 0xA8)
CODE_COLOR = RGBColor(0x66, 0x33, 0x99)


def clear_body(document: Document) -> Document:
    """Remove o conteudo do template, preservando estilos e a secao de pagina."""
    body = document.element.body
    keep = body.find(
        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sectPr")
    for child in list(body):
        if child is not keep:
            body.remove(child)
    return document


def add_runs(paragraph, text: str) -> None:
    """Escreve `text` no paragrafo interpretando a formatacao inline do Markdown."""
    for piece in INLINE.split(text):
        if not piece:
            continue
        if piece.startswith("**") and piece.endswith("**"):
            paragraph.add_run(piece[2:-2]).bold = True
        elif piece.startswith("*") and piece.endswith("*"):
            paragraph.add_run(piece[1:-1]).italic = True
        elif piece.startswith("`") and piece.endswith("`"):
            run = paragraph.add_run(piece[1:-1])
            run.font.name = CODE_FONT
            run.font.size = Pt(9.5)
            run.font.color.rgb = CODE_COLOR
        elif piece.startswith("["):
            label, _, target = piece[1:-1].partition("](")
            run = paragraph.add_run(label)
            run.font.color.rgb = LINK_COLOR
            run.underline = True
            # caminho relativo/URL fica visivel: o .docx e lido fora do repo
            if target.startswith("http"):
                paragraph.add_run(f" ({target})").font.size = Pt(8)
        else:
            paragraph.add_run(piece)


def add_image(document: Document, src: str, alt: str, base: Path) -> None:
    path = (base / src).resolve() if not Path(src).is_absolute() else Path(src)
    if not path.exists():
        document.add_paragraph(f"[figura ausente: {src}]").italic = True
        return
    document.add_picture(str(path), width=Inches(6.3))
    document.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if alt:
        caption = document.add_paragraph()
        caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = caption.add_run(alt)
        run.italic = True
        run.font.size = Pt(9)


def add_table(document: Document, rows: list[list[str]]) -> None:
    table = document.add_table(rows=len(rows), cols=max(len(r) for r in rows))
    try:
        table.style = "Table Grid"
    except KeyError:
        pass  # template sem o estilo: tabela sai sem bordas, mas sai
    for i, row in enumerate(rows):
        for j, cell_text in enumerate(row):
            cell = table.cell(i, j)
            cell.text = ""
            paragraph = cell.paragraphs[0]
            add_runs(paragraph, cell_text)
            for run in paragraph.runs:
                run.font.size = Pt(9)
                if i == 0:
                    run.bold = True
    document.add_paragraph()


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def convert(markdown: str, document: Document, base: Path) -> None:
    lines = markdown.splitlines()
    index, in_code = 0, False
    code_buffer: list[str] = []

    while index < len(lines):
        line = lines[index]

        # blocos de codigo cercados por ```
        if line.lstrip().startswith("```"):
            if in_code:
                paragraph = document.add_paragraph()
                run = paragraph.add_run("\n".join(code_buffer))
                run.font.name = CODE_FONT
                run.font.size = Pt(8.5)
                paragraph.paragraph_format.left_indent = Inches(0.25)
                code_buffer, in_code = [], False
            else:
                in_code = True
            index += 1
            continue
        if in_code:
            code_buffer.append(line)
            index += 1
            continue

        if not line.strip():
            index += 1
            continue

        if line.strip() in ("---", "***", "___"):
            document.add_paragraph()
            index += 1
            continue

        image = IMAGE.match(line.strip())
        if image:
            add_image(document, image.group("src"), image.group("alt"), base)
            index += 1
            continue

        heading = HEADING.match(line)
        if heading:
            level = len(heading.group("level"))
            document.add_heading(re.sub(r"[*`]", "", heading.group("text")),
                                 level=min(level, 4))
            index += 1
            continue

        # tabela: linha de cabecalho + separador |---|---|
        if line.strip().startswith("|") and index + 1 < len(lines) \
                and TABLE_SEP.match(lines[index + 1].strip()):
            rows = [split_row(line)]
            index += 2
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append(split_row(lines[index]))
                index += 1
            add_table(document, rows)
            continue

        if line.lstrip().startswith(">"):
            paragraph = document.add_paragraph()
            paragraph.paragraph_format.left_indent = Inches(0.3)
            add_runs(paragraph, line.lstrip().lstrip(">").strip())
            for run in paragraph.runs:
                run.italic = True
            index += 1
            continue

        bullet = BULLET.match(line)
        if bullet:
            style = "List Bullet" if len(bullet.group("indent")) < 2 else "List Bullet 2"
            paragraph = document.add_paragraph(style=style)
            add_runs(paragraph, bullet.group("text"))
            index += 1
            continue

        ordered = ORDERED.match(line)
        if ordered:
            paragraph = document.add_paragraph(style="List Number")
            add_runs(paragraph, ordered.group("text"))
            index += 1
            continue

        # paragrafo: junta as linhas seguintes ate a proxima linha em branco
        buffer = [line.strip()]
        index += 1
        while index < len(lines) and lines[index].strip() \
                and not lines[index].strip().startswith(("#", "|", ">", "-", "*", "```")) \
                and not ORDERED.match(lines[index]):
            buffer.append(lines[index].strip())
            index += 1
        add_runs(document.add_paragraph(), " ".join(buffer))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=REPO_ROOT / "docs/RELATORIO_FINAL.md")
    parser.add_argument("--template", type=Path,
                        default=REPO_ROOT / "Template_Relatorio_Laboratorio.docx")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "RelatorioFinal_Lab02.docx")
    args = parser.parse_args()

    markdown = args.input.read_text(encoding="utf-8")
    document = clear_body(Document(str(args.template))) if args.template.exists() \
        else Document()
    if not args.template.exists():
        print(f"aviso: template {args.template} nao encontrado; usando estilos padrao")

    convert(markdown, document, base=args.input.parent)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    document.save(str(args.output))

    figuras = sum(1 for line in markdown.splitlines() if IMAGE.match(line.strip()))
    print(f"{args.output.relative_to(REPO_ROOT) if args.output.is_relative_to(REPO_ROOT) else args.output}"
          f" ({args.output.stat().st_size / 1024:.0f} kB) — "
          f"{len(document.paragraphs)} paragrafos, {len(document.tables)} tabelas, "
          f"{figuras} figuras")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
