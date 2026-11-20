# humanizer-id — panduan agent (Codex / Claude / lainnya)

Repo ini alat **humanizer Bahasa Indonesia untuk tulisan ilmiah**: ubah draft kaku /
keluaran AI jadi prosa yang kebaca manusia **dan tetap bagus**. Fokus **mutu**, bukan
pengelabu detektor / penghapus watermark.

## Cara kerja (engine = agent host ini sendiri)
Agent (kamu) yang menulis ulang. Script Python hanya "wasit" kualitas.

Alur: **draft → tulis ulang pakai aturan gaya → skor (QC) → iterasi 2–3x → output.**

## Aturan gaya (ringkas; detail di `skills/humanize/SKILL.md`)
- Pertahankan makna, angka, istilah, sitasi. Jangan mengarang data.
- Tulis ulang level kalimat/paragraf, bukan tukar sinonim.
- Kalimat rata ~17 kata, **variasikan irama** (target `len_cv` > 0.35).
- Register formal, pasif/impersonal. Buang frasa padding hampa.

## Perintah QC
```bash
PYTHONPATH=src python3 src/score_draft.py --profile profiles/ilmiah_umum.json --draft HASIL.txt
```
Perbaiki sampai: `len_cv >= 0.30`, `padding/kalimat <= 0.15`, tidak ada flag berarti.

## Codex
Perintah khusus ada di `prompts/humanize.md` — salin ke `~/.codex/prompts/humanize.md`
agar bisa dipanggil `/humanize` di Codex CLI. Atau cukup arahkan Codex membaca file ini.

## Claude Code
Terpasang sebagai plugin (`.claude-plugin/plugin.json`): skill `humanize` + command
`/humanize` otomatis terbaca. Path script pakai `${CLAUDE_PLUGIN_ROOT}`.

## Etika
Alat menaikkan kualitas & kealamian. Bukan jaminan lolos detektor (detektor tak reliabel),
bukan untuk menyamarkan karya. Penulis tetap bertanggung jawab atas isinya.
