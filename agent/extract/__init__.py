"""Turn any supported file into plain text, safely.

Supported: .txt .csv .pdf .docx .xlsx .png .jpg .jpeg
Every extractor is wrapped with safety limits so one bad or hostile file
cannot crash or hang the scanner.
"""
import csv
import io
import shutil
import zipfile
from pathlib import Path

MAX_FILE_BYTES = 20 * 1024 * 1024        # 20 MB per file
MAX_UNZIPPED_BYTES = 100 * 1024 * 1024   # docx/xlsx are zip files: cap the unpacked size
MAX_ZIP_RATIO = 100                       # unpacked / packed above this = likely zip bomb
MAX_PDF_PAGES = 200
MAX_XLSX_CELLS = 500_000
OCR_TIMEOUT_SECONDS = 30


class ExtractionError(Exception):
    """A file could not be read safely. The scanner logs it and moves on."""


# ---------- safety checks ----------
def _check_size(path: Path) -> None:
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        raise ExtractionError(f"too large ({size // 1024 // 1024} MB)")


def _check_zip_bomb(path: Path) -> None:
    """Office files are zip archives. Reject ones that unpack to something huge."""
    try:
        with zipfile.ZipFile(path) as z:
            unpacked = sum(info.file_size for info in z.infolist())
    except zipfile.BadZipFile:
        raise ExtractionError("corrupt office file")
    packed = max(path.stat().st_size, 1)
    if unpacked > MAX_UNZIPPED_BYTES or unpacked / packed > MAX_ZIP_RATIO:
        raise ExtractionError("possible zip bomb")


# ---------- extractors ----------
def _txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _csv(path: Path) -> str:
    with path.open(encoding="utf-8", errors="ignore", newline="") as f:
        return "\n".join(" ".join(row) for row in csv.reader(f))


def _pdf(path: Path) -> str:
    import pdfplumber
    parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages[:MAX_PDF_PAGES]:
            parts.append(page.extract_text() or "")
    return "\n".join(parts)


def _docx(path: Path) -> str:
    import docx
    _check_zip_bomb(path)
    d = docx.Document(path)
    parts = [p.text for p in d.paragraphs]
    for table in d.tables:                      # text inside tables too
        for row in table.rows:
            parts.append(" ".join(cell.text for cell in row.cells))
    return "\n".join(parts)


def _xlsx(path: Path) -> str:
    import openpyxl
    _check_zip_bomb(path)
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    parts, cells = [], 0
    try:
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                cells += len(row)
                if cells > MAX_XLSX_CELLS:
                    raise ExtractionError("too many cells")
                parts.append(" ".join(str(v) for v in row if v is not None))
    finally:
        wb.close()
    return "\n".join(parts)


def _image(path: Path) -> str:
    import pytesseract
    from PIL import Image
    if not tesseract_available():
        raise ExtractionError("Tesseract OCR not installed")
    with Image.open(path) as img:
        if img.width * img.height > 40_000_000:     # decompression-bomb guard
            raise ExtractionError("image too large")
        try:
            return pytesseract.image_to_string(img, lang="eng", timeout=OCR_TIMEOUT_SECONDS)
        except RuntimeError:                         # pytesseract raises this on timeout
            raise ExtractionError("OCR timed out")


EXTRACTORS = {
    ".txt": _txt, ".csv": _csv, ".pdf": _pdf, ".docx": _docx,
    ".xlsx": _xlsx, ".png": _image, ".jpg": _image, ".jpeg": _image,
}
SUPPORTED = set(EXTRACTORS)


def tesseract_available() -> bool:
    """Find tesseract.exe: TESSERACT_CMD setting, then PATH, then the default Windows folder."""
    import os
    import pytesseract
    candidates = [
        os.environ.get("TESSERACT_CMD", ""),
        shutil.which("tesseract") or "",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    ]
    for c in candidates:
        if c and Path(c).exists():
            pytesseract.pytesseract.tesseract_cmd = c
            return True
    return False


def extract_text(path: Path) -> str:
    """Return the text of a file, or raise ExtractionError."""
    extractor = EXTRACTORS.get(path.suffix.lower())
    if extractor is None:
        raise ExtractionError("unsupported file type")
    _check_size(path)
    try:
        return extractor(path)
    except ExtractionError:
        raise
    except Exception as e:       # any parser crash = skip this file, never crash the scan
        raise ExtractionError(f"{e.__class__.__name__}")
