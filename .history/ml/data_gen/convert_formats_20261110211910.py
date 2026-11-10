"""Convert the fake .txt documents into PDF, DOCX, XLSX and PNG copies.

Reads  testdata/*.txt + testdata/labels.json
Writes testdata_mixed/ with every document in a random format + a new labels.json

Usage:
    python ml/data_gen/convert_formats.py
    python ml/data_gen/convert_formats.py --no-images     (if Tesseract is not installed)
"""
import argparse
import json
import random
from pathlib import Path

import docx
import openpyxl
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

SRC = Path("testdata")
OUT = Path("testdata_mixed")


def to_pdf(text: str, dest: Path) -> None:
    c = canvas.Canvas(str(dest), pagesize=A4)
    y = 800
    for line in text.splitlines():
        c.drawString(50, y, line)
        y -= 18
    c.save()


def to_docx(text: str, dest: Path) -> None:
    d = docx.Document()
    lines = text.splitlines()
    d.add_heading(lines[0] if lines else "Document", level=1)
    # Put "Label: value" lines in a table, like real forms; the rest as paragraphs
    pairs = [l.split(":", 1) for l in lines[1:] if ":" in l]
    others = [l for l in lines[1:] if ":" not in l]
    for l in others:
        d.add_paragraph(l)
    if pairs:
        table = d.add_table(rows=0, cols=2)
        for k, v in pairs:
            row = table.add_row().cells
            row[0].text, row[1].text = k.strip(), v.strip()
    d.save(dest)


def to_xlsx(text: str, dest: Path) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    for line in text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            ws.append([k.strip(), v.strip()])
        else:
            ws.append([line])
    wb.save(dest)


def _font():
    for f in [r"C:\Windows\Fonts\arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if Path(f).exists():
            return ImageFont.truetype(f, 28)
    return ImageFont.load_default()


def to_png(text: str, dest: Path) -> None:
    """A 'scanned' document: text drawn on an image, so only OCR can read it."""
    lines = text.splitlines()
    img = Image.new("RGB", (1700, 60 + 44 * len(lines)), "white")
    draw = ImageDraw.Draw(img)
    font = _font()
    for i, line in enumerate(lines):
        draw.text((40, 30 + 44 * i), line, fill="black", font=font)
    img.save(dest)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-images", action="store_true")