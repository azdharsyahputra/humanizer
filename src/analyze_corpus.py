"""
analyze_corpus.py — bangun profil gaya manusia dari korpus.

Sumber bisa:
  - file .arrow dari HuggingFace save_to_disk (mis. id_scholar shard)
  - folder berisi .txt

Pakai:
  python3 -I analyze_corpus.py --arrow corpus/id_scholar_raw/shard0.arrow \
      --out profiles/ilmiah_umum.json --label "ilmiah_umum" --sample 3000
  python3 -I analyze_corpus.py --txtdir corpus/mytxt --out profiles/x.json --label x
"""
import argparse, json, os, re, random, sys
from style_metrics import compute_metrics, build_profile

MIN_WORDS = 150   # buang entri terlalu pendek (judul/metadata)


def iter_arrow(path, sample, seed=13):
    from datasets import Dataset
    ds = Dataset.from_file(path)
    # deteksi kolom teks
    cols = ds.column_names
    text_col = None
    for cand in ("text", "content", "body", "abstract", "full_text", "isi"):
        if cand in cols:
            text_col = cand
            break
    if text_col is None:  # ambil kolom string pertama
        for c in cols:
            if isinstance(ds[0][c], str):
                text_col = c
                break
    if text_col is None:
        sys.exit(f"tidak nemu kolom teks. kolom: {cols}")
    print(f"[info] kolom teks = '{text_col}', total baris = {len(ds)}")
    idx = list(range(len(ds)))
    random.Random(seed).shuffle(idx)
    taken = 0
    for i in idx:
        if taken >= sample:
            break
        t = ds[i][text_col]
        if isinstance(t, str) and len(t.split()) >= MIN_WORDS:
            taken += 1
            yield t


def iter_txtdir(path):
    for root, _, files in os.walk(path):
        for f in files:
            if f.lower().endswith(".txt"):
                try:
                    t = open(os.path.join(root, f), encoding="utf-8", errors="ignore").read()
                except Exception:
                    continue
                if len(t.split()) >= MIN_WORDS:
                    yield t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arrow")
    ap.add_argument("--txtdir")
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--sample", type=int, default=3000)
    a = ap.parse_args()

    if a.arrow:
        docs = iter_arrow(a.arrow, a.sample)
    elif a.txtdir:
        docs = iter_txtdir(a.txtdir)
    else:
        sys.exit("beri --arrow atau --txtdir")

    metrics, used = [], 0
    for t in docs:
        m = compute_metrics(t)
        if m:
            metrics.append(m)
            used += 1
            if used % 500 == 0:
                print(f"[info] diproses {used} dok")
    prof = build_profile(metrics)
    if not prof:
        sys.exit("tidak ada dokumen valid")
    prof["label"] = a.label
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    json.dump(prof, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[ok] profil '{a.label}' dari {prof['n_docs']} dok "
          f"({prof['total_word']:,} kata) -> {a.out}")
    print(f"     kata/kalimat {prof['words_per_sent_mean']['mean']}, "
          f"burstiness {prof['burstiness']['mean']}, "
          f"fragmen {prof['fragment_rate']['mean']}")


if __name__ == "__main__":
    main()
