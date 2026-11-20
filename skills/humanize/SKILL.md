---
name: humanize
description: Tulis ulang teks (terutama draft/keluaran AI) menjadi prosa ilmiah Bahasa Indonesia yang natural, enak dibaca, dan tetap berkualitas. Pakai saat user minta "humanize", "bikin natural", "rapihin tulisan ilmiah", "biar ga kaku/kebaca AI", atau /humanize. Memandu penulisan ulang dengan profil tulisan manusia asli lalu mengukur hasilnya dengan skor kualitas. BUKAN alat pengelabu detektor / penghapus watermark.
---

# Humanize (Bahasa Indonesia, register ilmiah)

Tujuan: ubah draft kaku/templated/keluaran-AI jadi tulisan yang **kebaca manusia DAN tetap bagus** — bukan sekadar lolos detektor. Optimasi ke **mutu**, bukan penyamaran.

## Prinsip (jangan dilanggar)
1. **Pertahankan makna, angka, istilah teknis, dan sitasi.** Dilarang mengarang data/hasil. Kalau draft bilang "akurasi 61%", hasil juga 61%.
2. **Tulis ulang di level kalimat/paragraf**, bukan tukar-sinonim kata. Itu yang bikin humanizer lain jadi tulisan anak SD.
3. Ini alat bantu. Kalau untuk tugas akademik, penulisnya tetap user — jangan dipakai mengklaim karya yang bukan hasil pemikirannya.

## Target gaya (dari korpus jurnal Indonesia PRA-AI, 3000 dok / 12jt kata)
- **Panjang kalimat**: rata-rata ~17 kata. Jangan semua ~17 — **variasikan**.
- **Irama (paling penting)**: selang-seling pendek–panjang. Target `len_cv` (stdev/mean panjang) **> 0.35**. Teks AI biasanya 0.2 (semua kalimat sama panjang = ketahuan templated).
- **Register formal**: konjungsi baku (namun, oleh karena itu, sehingga, selain itu). Hindari lisan (tapi, jadi, banget, nggak).
- **Impersonal & pasif**: minim "saya/aku"; pakai bentuk pasif (di-) khas ilmiah.
- **Buang padding hampa**: "memiliki kemampuan yang signifikan", "menjadi semakin penting", "diharapkan dapat", "berperan penting". Ganti dengan isi konkret.
- **Substansi konkret (paling menentukan)**: tiap klaim idealnya bersandar pada angka, nama metode/model, dataset, sitasi, atau hasil nyata. Kalimat generik tanpa isi (`specificity_per_sent` rendah) = terasa kosong & kebaca mesin. JANGAN mengarang untuk menaikkan ini — ambil dari materi riset user. Kalau draft memang belum punya data, tandai ke user bahwa bagian itu perlu diisi substansi, jangan dipoles seolah berisi.
- **Variasikan pembuka kalimat**: jangan "Penelitian ini..." berulang.

## Mode gaya (opsional, pilih sesuai kebutuhan user)
Default = **ilmiah** (aturan di atas). Jika user minta gaya "profesional/jelas/PMBOK":

**Mode PROFESIONAL (ala PMBOK) — jernih & lugas:**
- Kalimat **deklaratif, aktif, langsung**: subjek–kata kerja–objek. Kurangi pasif berlebih.
- **Satu ide per kalimat.** Kalau satu kalimat punya 2 gagasan, pecah.
- **Kata lugas**, buang jargon yang bisa disederhanakan. Hindari nominalisasi bertumpuk.
- Buka tiap bagian/paragraf dengan **kalimat definitif tegas** ("X adalah penentu utama Y.").
- Gunakan **struktur paralel** dan daftar berpoin untuk rangkaian hal.
- Irama: median ~17 kata, `len_cv` tetap > 0.7 (selipkan kalimat pendek tegas 6–10 kata).
- Nada **percaya diri**, minim hedging ("mungkin", "sepertinya", "cenderung").
- **GUARDRAIL (wajib di konteks ilmiah):** semua kalimat harus **utuh** (punya subjek + kata
  kerja). DILARANG fragmen gaya slide ("Pendekatannya: X.") dan tanda hubung dramatis
  ("Tujuannya satu — Y."). "Pendek & tegas" artinya **ringkas tanpa lemak**, BUKAN memotong
  jadi penggalan. Target: 2 kalimat utuh yang jernih, bukan 3 penggalan iklan.
- CATATAN: gaya ini jernih tapi lebih "aktif/langsung" daripada skripsi konservatif. Untuk
  tugas akademik formal, konfirmasi ke user apakah penguji menerima gaya aktif/kalimat pendek;
  untuk laporan, proposal, dokumen profesional, gaya ini ideal.

## Alur kerja
1. **Ambil draft**: dari file yang disebut user, atau teks yang dipaste. Simpan ke file sementara bila perlu.
2. **Tulis ulang** mengikuti Target gaya di atas. Pertahankan struktur argumen & semua fakta.
3. **Ukur (QC)** dengan skor:
   ```bash
   PYTHONPATH="<root>/src" python3 "<root>/src/score_draft.py" \
     --profile "<root>/profiles/ilmiah_umum.json" --draft hasil.txt
   ```
   (`<root>` = `${CLAUDE_PLUGIN_ROOT}` bila terpasang sebagai plugin, atau akar repo ini.)
4. **Baca hasil skor**:
   - `len_cv < 0.30` → irama masih seragam. Pecah/gabung kalimat, selipin kalimat pendek tegas.
   - `padding/kalimat > 0.15` → masih ada frasa hampa. Ganti dengan substansi.
   - `substansi/kalimat < 0.30` → tulisan generik/kosong. Minta user isi data konkret; jangan dikarang.
   - flag "kalimat kepanjangan" / "bahasa santai" → perbaiki sesuai catatan.
5. **Iterasi** langkah 2–4 maksimal 3x sampai tidak ada flag berarti (abaikan metrik yang "dilewati" karena teks pendek).
6. **Tampilkan** ke user: hasil akhir + ringkas skor sebelum/sesudah. Jangan klaim "0% AI" — skor ini ukuran mutu, bukan vonis mesin.

## Catatan jujur ke user (sertakan sekali, singkat)
Alat ini menaikkan kualitas & kealamian tulisan. Bukan jaminan lolos detektor AI (detektor memang tidak reliabel), dan bukan untuk menyamarkan karya.
