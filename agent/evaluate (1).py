"""Score the scanner against the answer key (testdata/labels.json).

Usage:
    python -m agent.evaluate testdata
"""
import argparse
import json
from pathlib import Path

from agent.cli import scan_folder


def evaluate(folder: Path) -> dict:
    labels = json.loads((folder / "labels.json").read_text(encoding="utf-8"))
    report = scan_folder(folder)

    scanned = {Path(f["file"]).name: f for f in report["files"]}

    stats: dict[str, dict[str, int]] = {}
    mistakes = []
    # Loop over the ANSWER KEY, not the report: a file the scanner never
    # read still counts. Its personal data was missed (false negatives).
    for name, label in labels.items():
        f = scanned.get(name)
        if f is None:
            mistakes.append(f"{name}: not scanned (unsupported type?)")
            counts = {}
        elif "skipped" in f:
            mistakes.append(f"{name}: skipped ({f['skipped']})")
            counts = {}
        else:
            counts = f["counts"]
        for kind, want in label["expected"].items():
            got = counts.get(kind, 0)
            s = stats.setdefault(kind, {"tp": 0, "fp": 0, "fn": 0})
            s["tp"] += min(got, want)          # correctly found
            s["fp"] += max(got - want, 0)      # flagged but not real  -> false positive
            s["fn"] += max(want - got, 0)      # real but missed       -> false negative
            if f is not None and "counts" in f and got != want:
                mistakes.append(f"{name}: {kind} expected {want}, found {got}")

    results = {}
    for kind, s in stats.items():
        precision = s["tp"] / (s["tp"] + s["fp"]) if s["tp"] + s["fp"] else 1.0
        recall = s["tp"] / (s["tp"] + s["fn"]) if s["tp"] + s["fn"] else 1.0
        results[kind] = {**s, "precision": precision, "recall": recall}
    return {"results": results, "mistakes": mistakes}


def main():
    parser = argparse.ArgumentParser(description="Evaluate scanner accuracy")
    parser.add_argument("folder", type=Path)
    args = parser.parse_args()

    out = evaluate(args.folder)
    print(f"{'TYPE':<8} {'TP':>5} {'FP':>5} {'FN':>5} {'PRECISION':>10} {'RECALL':>8}")
    for kind, r in out["results"].items():
        print(f"{kind:<8} {r['tp']:>5} {r['fp']:>5} {r['fn']:>5} "
              f"{r['precision']:>9.1%} {r['recall']:>8.1%}")
    if out["mistakes"]:
        print(f"\n{len(out['mistakes'])} mistakes (first 10):")
        for m in out["mistakes"][:10]:
            print("  " + m)
    else:
        print("\nNo mistakes. Every file matches the answer key.")


if __name__ == "__main__":
    main()
