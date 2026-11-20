# humanizer-id — editor gaya tulisan Bahasa Indonesia

Alat bantu menulis yang mengukur draft kamu terhadap **profil tulisan manusia asli**
(korpus jurnal Indonesia pra-AI), lalu menunjukkan bagian mana yang terbaca kaku,
seragam, atau "mesin" — supaya kamu perbaiki. Dirancang sebagai **skill/plugin** yang
jalan di Claude Code maupun Codex: agent host yang menulis ulang, script di sini jadi
gerbang kualitas.

## Apa ini & apa BUKAN

- ✅ **Editor kualitas.** Menaikkan kealamian & mutu tulisan (irama, substansi, register).
- ❌ **BUKAN generator** teks otomatis.
- ❌ **BUKAN pengelabu detektor AI / penghapus watermark.**

> **Soal detektor AI (penting):** detektor seperti ZeroGPT/Turnitin/GPTZero **tidak reliabel**.
> Dalam pengujian repo ini, paragraf jurnal **manusia asli tahun 2011** terdeteksi **72% AI**,
> dan satu paragraf manusia lain **100% AI**. Skornya mengukur *kemulusan/ketebakan* teks
> (perplexity), **bukan** apakah teks ditulis AI. Mengejar skor rendah = mengejar angka rusak,
> dan caranya selalu dengan **merusak** tulisan. Tool ini sengaja **tidak** mengejar itu.

## Yang diukur (6 dimensi mutu)

| Dimensi | Metrik | Sinyal |
|---|---|---|
| Napas/irama | `burstiness`, `len_cv` | AI datar; manusia naik-turun (target CV > 0.35) |
| Panjang kalimat | `words_per_sent_mean` | ~17; jangan semua seragam |
| Padding | `padding_per_sent` | frasa hampa ("memiliki kemampuan yang signifikan") → ~0 |
| Register ilmiah | konjungsi formal, pasif, no-slang | formal & impersonal |
| **Substansi** | `specificity_per_sent` | angka/sitasi/istilah per kalimat — generik = kosong |
| Variasi | `ttr`, `top_opener_share` | jangan ulang diksi/pembuka |

## Dua mode gaya

- **ilmiah** (default): formal, pasif, kalimat lengkap — untuk skripsi/jurnal.
- **profesional** (ala PMBOK): lugas, aktif, satu ide per kalimat — untuk laporan/proposal/dokumen
  kerja. Guardrail: tetap kalimat utuh, dilarang fragmen gaya slide.

## Struktur

```
src/style_metrics.py   # fungsi metrik gaya
src/analyze_corpus.py  # bangun profil .json dari korpus (.arrow HF / folder .txt)
src/score_draft.py     # nilai draft terhadap profil + cek absolut (CV, padding, substansi)
src/batch_score.py     # tabulasi banyak teks (kalibrasi)
skills/humanize/SKILL.md   # aturan rewrite + QC loop (Claude Code)
commands/humanize.md       # /humanize
AGENTS.md, prompts/humanize.md   # Codex / portable
profiles/ilmiah_umum.json  # profil dari 3000 artikel / 12jt kata (pra-AI)
```

Korpus mentah (`corpus/`) tidak di-commit (besar + hak cipta). Profil dibangun dari
[`Wikidepia/id_scholar`](https://huggingface.co/datasets/Wikidepia/id_scholar) (CC-BY-SA-4.0).

## Pakai

Bangun profil:
```bash
PYTHONPATH=src python3 src/analyze_corpus.py --arrow <shard.arrow> \
  --out profiles/ilmiah_umum.json --label ilmiah_umum --sample 3000
```
Nilai draft:
```bash
PYTHONPATH=src python3 src/score_draft.py --profile profiles/ilmiah_umum.json --draft draft.txt
```

## Prinsip

Tulisan yang baik = **bermutu + punya kamu**. Pakai AI sebagai editor atas ide & data riil
kamu, bukan ghostwriter. Tool menandai yang kosong/kaku; substansi tetap dari risetmu.
