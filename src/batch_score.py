"""
batch_score.py — tabulasi metrik pembeda (CV, padding) untuk banyak teks sekaligus.
Buat kalibrasi ambang: bandingkan set 'manusia' vs 'era-AI'.

Pakai:
  python3 batch_score.py --dir corpus/samples
  python3 batch_score.py --files a.txt b.txt c.txt --label uji
"""
import argparse, glob, os
from style_metrics import compute_metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir")
    ap.add_argument("--files", nargs="*")
    ap.add_argument("--label", default="")
    a = ap.parse_args()

    paths = []
    if a.dir:
        paths += sorted(glob.glob(os.path.join(a.dir, "*.txt")))
    if a.files:
        paths += a.files
    if not paths:
        raise SystemExit("beri --dir atau --files")

    print(f"{'file':28s} {'nkal':>4s} {'kata/kal':>8s} {'CV':>6s} {'pad/kal':>8s}  tanda")
    rows = []
    for p in paths:
        t = open(p, encoding="utf-8", errors="ignore").read()
        m = compute_metrics(t)
        if not m:
            print(f"{os.path.basename(p)[:28]:28s}  (terlalu pendek)")
            continue
        cv, pad = m["len_cv"], m["padding_per_sent"]
        tag = []
        if cv < 0.30: tag.append("seragam")
        if pad > 0.15: tag.append("padding")
        print(f"{os.path.basename(p)[:28]:28s} {m['n_sent']:4d} "
              f"{m['words_per_sent_mean']:8.1f} {cv:6.2f} {pad:8.2f}  {','.join(tag)}")
        rows.append((cv, pad))
    if rows:
        import statistics
        cvs = [r[0] for r in rows]; pads = [r[1] for r in rows]
        print(f"\n{a.label or 'set'}: n={len(rows)}  "
              f"CV mean={statistics.mean(cvs):.3f} (min {min(cvs):.2f} max {max(cvs):.2f})  "
              f"padding mean={statistics.mean(pads):.3f}")


if __name__ == "__main__":
    main()
