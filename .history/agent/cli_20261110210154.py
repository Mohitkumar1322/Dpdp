"""Scan a folder and write a findings report.

Usage:
    python -m agent.cli testdata
    python -m agent.cli testdata --out report.json
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from agent.detect.rules import mask, scan_text

SCANNABLE = {".txt"}            # Phase 2 will add .pdf, .docx, .xlsx ...
MAX_FILE_BYTES = 10 * 1024 * 1024   # skip files over 10 MB (safety limit)


def walk(root: Path):
    """Yield every scannable file under root."""
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in SCANNABLE:
            yield path


def scan_file(path: Path) -> dict:
    """Scan one file. Returns counts + masked samples, never raw values."""
    if path.stat().st_size > MAX_FILE_BYTES:
        return {"file": str(path), "skipped": "too large"}
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        return {"file": str(path), "skipped": f"read error: {e.__class__.__name__}"}

    found = scan_text(text)
    return {
        "file": str(path),
        "counts": {kind: len(values) for kind, values in found.items()},
        "samples": {kind: [mask(v) for v in values[:3]] for kind, values in found.items() if values},
    }


def scan_folder(root: Path) -> dict:
    files = [scan_file(p) for p in walk(root)]
    totals: dict[str, int] = {}
    for f in files:
        for kind, n in f.get("counts", {}).items():
            totals[kind] = totals.get(kind, 0) + n
    return {
        "scanned_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "root": str(root),
        "files_scanned": sum(1 for f in files if "counts" in f),
        "files_skipped": sum(1 for f in files if "skipped" in f),
        "files_with_personal_data": sum(1 for f in files if any(f.get("counts", {}).values())),
        "totals": totals,
        "files": files,
    }


def main():
    parser = argparse.ArgumentParser(description="Scan a folder for personal data")
    parser.add_argument("folder", type=Path)
    parser.add_argument("--out", type=Path, default=Path("report.json"))
    args = parser.parse_args()

    if not args.folder.is_dir():
        parser.error(f"not a folder: {args.folder}")

    report = scan_folder(args.folder)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Scanned {report['files_scanned']} files "
          f"({report['files_skipped']} skipped), "
          f"{report['files_with_personal_data']} contain personal data")
    for kind, n in report["totals"].items():
        print(f"  {kind:<8} {n}")
    print(f"Report written to {args.out}")


if __name__ == "__main__":
    main()