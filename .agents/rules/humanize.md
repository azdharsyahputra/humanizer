---
description: Humanizer B.Indo — tulis ulang draft jadi prosa ilmiah/profesional yang natural & berkualitas, lalu nilai dengan QC skor. Fokus mutu, bukan pengelabu detektor.
---

# Aturan: Humanize (Bahasa Indonesia)

Saat user minta "humanize", "bikin natural", "rapihin tulisan ilmiah", atau "/humanize":
tulis ulang teks jadi prosa yang **kebaca manusia DAN tetap bagus** — optimasi mutu,
bukan penyamaran detektor AI.

## Prinsip wajib
- Pertahankan makna, angka, istilah, dan sitasi. **Jangan mengarang data.**
- Tulis ulang di level kalimat/paragraf, bukan tukar sinonim kata.
- Ini editor. Untuk tugas akademik, penulisnya tetap user.

## Target gaya (korpus jurnal Indonesia pra-AI)
- Kalimat rata ~17 kata, **variasikan irama** (target `len_cv` > 0.35).
- Register formal, pasif/impersonal; buang frasa padding hampa.
- **Substansi konkret**: tiap klaim bersandar pada angka/sitasi/metode. Kalimat generik = kosong.
- Variasikan pembuka kalimat.
- Mode `profesional` (ala PMBOK): lugas, aktif, satu ide/kalimat — tapi kalimat tetap UTUH
  (dilarang fragmen gaya slide / tanda hubung dramatis).

## QC (jalankan setelah menulis ulang)
```bash
PYTHONPATH=src python3 src/score_draft.py --profile profiles/ilmiah_umum.json --draft HASIL.txt
```
Perbaiki sampai: `len_cv >= 0.30`, `padding/kalimat <= 0.15`, `substansi/kalimat >= 0.30`,
tidak ada flag berarti. Iterasi maks 3x. Detail lengkap di `skills/humanize/SKILL.md`.

Jangan klaim "0% AI" — skor ini ukuran mutu, bukan vonis mesin, dan detektor AI tidak reliabel.
