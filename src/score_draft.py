"""
score_draft.py — nilai draft terhadap profil manusia, tunjuk yang nyimpang.

Ini EDITOR, bukan generator. Tidak menulis ulang teks lu.
Dia bilang: metrik mana yang jauh dari tulisan manusia asli, dan saran arahnya.

Pakai:
  python3 -I score_draft.py --profile profiles/ilmiah_umum.json --draft draft.txt
"""
import argparse, json, sys
from style_metrics import compute_metrics

# ambang z-score: |z| > FLAG dianggap menyimpang
FLAG = 1.3
# metrik yang nilainya bergantung panjang teks; tak andal untuk teks pendek
SCALE_SENSITIVE = {"burstiness", "top_opener_share", "words_per_sent_stdev"}
MIN_SENT_SCALE = 12  # di bawah ini, metrik skala-sensitif dilewati (mis. abstrak)

# metrik -> (arah bahaya, saran kalau terlalu TINGGI, saran kalau terlalu RENDAH)
ADVICE = {
    "words_per_sent_mean": (
        "Kalimat kepanjangan — pecah jadi dua.",
        "Kalimat kependekan untuk ilmiah — gabung/perkaya."),
    "words_per_sent_stdev": (
        "Variasi panjang ekstrem (mungkin ada baris sampah).",
        "Panjang kalimat terlalu seragam — ciri khas AI. Variasikan!"),
    "burstiness": (
        "Loncatan panjang kalimat terlalu liar.",
        "Irama datar, tiap kalimat mirip panjang — paling kebaca AI. Selang-seling pendek-panjang."),
    "commas_per_sent": (
        "Terlalu banyak koma — kalimat bertele.",
        "Minim koma — tambah anak kalimat/perincian."),
    "top_opener_share": (
        "Satu kata pembuka dipakai berulang — monoton. Variasikan awal kalimat.",
        None),
    "formal_conn_per_sent": (
        None,
        "Kurang konjungsi formal (namun, oleh karena itu, sehingga)."),
    "informal_conn_per_sent": (
        "Ada bahasa santai (tapi/jadi/banget/nggak) — ganti ke formal.",
        None),
    "first_person_per_sent": (
        "Terlalu banyak 'aku/saya' — ilmiah impersonal, pakai pasif.",
        None),
    "passive_per_sent": (
        None,
        "Kurang kalimat pasif — ilmiah Indonesia cenderung pasif (di-)."),
    "fragment_rate": (
        "Banyak kalimat tak lengkap (<5 kata).",
        None),
    "ttr": (None, None),
    "hedge_per_sent": (None, None),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True)
    ap.add_argument("--draft", required=True)
    a = ap.parse_args()

    prof = json.load(open(a.profile, encoding="utf-8"))
    text = open(a.draft, encoding="utf-8", errors="ignore").read()
    m = compute_metrics(text)
    if not m:
        sys.exit("draft terlalu pendek (<3 kalimat).")

    print(f"Profil acuan : {prof.get('label')} ({prof['n_docs']} dok manusia)")
    print(f"Draft        : {m['n_sent']} kalimat, {m['n_word']} kata\n")
    print(f"{'METRIK':22s} {'DRAFT':>8s} {'MANUSIA':>9s} {'z':>6s}  CATATAN")

    short = m["n_sent"] < MIN_SENT_SCALE
    flags = []
    for k, adv in ADVICE.items():
        if k not in prof or k not in m:
            continue
        mean = prof[k]["mean"]
        sd = prof[k]["stdev"] or 1e-9
        val = m[k]
        z = (val - mean) / sd
        note = ""
        if short and k in SCALE_SENSITIVE:
            note = f"— dilewati (teks <{MIN_SENT_SCALE} kalimat, metrik ini butuh teks panjang)"
            print(f"{k:22s} {val:8.3f} {mean:9.3f} {z:+6.1f}  {note}")
            continue
        if z > FLAG and adv[0]:
            note = "⚠ " + adv[0]; flags.append(note)
        elif z < -FLAG and adv[1]:
            note = "⚠ " + adv[1]; flags.append(note)
        print(f"{k:22s} {val:8.3f} {mean:9.3f} {z:+6.1f}  {note}")

    if short:
        print(f"\n[info] teks pendek ({m['n_sent']} kalimat) — metrik skala-sensitif "
              f"({', '.join(sorted(SCALE_SENSITIVE))}) dilewati biar ga salah vonis.")

    # --- cek ambang ABSOLUT (andal walau teks pendek, tak bergantung profil noisy) ---
    CV_FLAG = 0.30        # di bawah ini: irama kalimat kelewat seragam
    PADDING_FLAG = 0.15   # padding/kalimat di atas ini: banyak frasa hampa
    print("\n--- CEK ABSOLUT (uniformity & padding) ---")
    cv = m["len_cv"]
    cv_note = ("⚠ Irama kalimat kelewat seragam (CV %.2f) — tiap kalimat panjang mirip, "
               "ciri templated/AI. Selipin kalimat pendek tegas." % cv) if cv < CV_FLAG else "oke"
    print(f"len_cv (keseragaman)   {cv:8.3f}  (ambang <{CV_FLAG})  {cv_note}")
    if cv < CV_FLAG:
        flags.append(cv_note)
    pad = m["padding_per_sent"]
    pad_note = ("⚠ Banyak frasa padding hampa (%.2f/kalimat) — mis. 'memiliki kemampuan yang "
                "signifikan', 'diharapkan dapat'. Ganti dengan isi konkret/angka." % pad) \
        if pad > PADDING_FLAG else "oke"
    print(f"padding/kalimat        {pad:8.3f}  (ambang >{PADDING_FLAG})  {pad_note}")
    if pad > PADDING_FLAG:
        flags.append(pad_note)
    SPEC_LOW = 0.30       # di bawah ini: tulisan generik, minim substansi konkret
    spec = m["specificity_per_sent"]
    spec_note = ("⚠ Minim substansi konkret (%.2f/kalimat) — sedikit angka/sitasi/istilah "
                 "spesifik. Tulisan terasa generik/awang-awang. Isi dengan data, nama metode, "
                 "sitasi, hasil nyata." % spec) if spec < SPEC_LOW else "oke (berisi)"
    print(f"substansi/kalimat      {spec:8.3f}  (ambang <{SPEC_LOW})  {spec_note}")
    if spec < SPEC_LOW:
        flags.append(spec_note)

    print("\n--- RINGKAS ---")
    if flags:
        print(f"{len(flags)} hal menyimpang dari tulisan manusia asli:")
        for f in flags:
            print("  " + f)
    else:
        print("Draft sudah dekat dengan profil manusia. Mantap.")
    print("\n(Catatan: ini alat bantu edit. Perbaikan tetap keputusan & tanganmu.)")


if __name__ == "__main__":
    main()
