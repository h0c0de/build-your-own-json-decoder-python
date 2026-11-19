# Rencana — Build Your Own JSON Decoder (Python)

Sumber: entri **JSON Decoding Algorithm** oleh **cheery
(Henri Tuhola)** di build-your-own-x →
https://github.com/cheery/json-algorithm (MIT). Bukan parser
rekursif biasa: ini **otomaton pushdown bertabel** — tabel
transisi yang dibangun dari diagram railroad json.org oleh
program `build_tables.py`, dijalankan oleh driver kecil
dengan tiga tumpukan (data, string, escape) dan 14 aksi
semantik (`do_action`). Wasit: modul `json` bawaan Python.

## Adaptasi yang dicatat di muka

- Driver & aksi ditulis ulang Python 3 dari kode tutorial
  di README panduan (`unichr` → `chr`); pesan galat panduan
  dipertahankan persis ("syntax" / "truncated" /
  "too many objects") tetapi dibungkus kelas `GalatJSON`
  (turunan ValueError) agar bisa ditangkap secara wajar.
- Tabel TIDAK disalin dengan tangan (peringatan panduan):
  `json.txt` hulu diambil apa adanya, `buat_tabel.py`
  memformatnya menjadi `tabel.py` secara programatis.
- Bukti asal-usul tabel: port Python 3 dari
  `build_tables.py` (`bangun_tabel.py`, irisan 4) harus
  menghasilkan `json.txt` yang byte-identik — sudah diuji
  saat setup 20 Nov 2026: keluaran port = 10.505 byte,
  `cmp` identik. Tabel: 42 state × 28 catcode, 42 goto.
- Perilaku pasangan surrogate `\uXXXX` mengikuti otomaton
  apa adanya (dua titik kode terpisah, berbeda dari
  `json.loads` yang menggabungkannya) — didokumentasikan
  sebagai temuan, bukan diam-diam diubah.

## Irisan

- [x] Irisan 1 — Tabel + driver + aksi: buat_tabel.py
      menghasilkan tabel.py; jsonmesin.py dengan parse()
      lengkap mengikuti tutorial panduan. Baterai skalar:
      null/true/false, int (besar, negatif, -0), float
      (eksponen), string (semua escape + \uXXXX), dan tiga
      kelas galat panduan. Diferensial vs json.loads.
- [x] Irisan 2 — Struktur: array/objek bersarang, kontainer
      kosong, sarang dalam, kunci duplikat; diferensial
      acak terseed vs json.loads (ratusan dokumen hasil
      generator, dibuang & dibandingkan nilainya).
- [x] Irisan 3 — Baterai penulisnya + cakupan state:
      masukan uji dari verifier.py penulis dijalankan ke
      parse() kita; instrumentasi membuktikan baterai itu
      mengunjungi seluruh 42 state — ide verifikasi penulis
      sendiri.
- [x] Irisan 4 — Asal-usul + aliran + terbit: bangun_tabel.py
      (port build_tables.py) membuktikan json.txt
      byte-identik; API inkremental umpan() per karakter ==
      parse utuh; pembaca aliran banyak-nilai (saran README
      panduan sendiri); baterai galat vs json termasuk
      divergensi NaN/Infinity; terbit ke
      `build-your-own-json-decoder-python`.

## Pagar selesai

- [x] Diferensial vs json.loads bersih pada korpus valid
      (di luar divergensi surrogate yang didokumentasikan).
- [x] Seluruh 42 state terbukti terunjungi baterai penulis.
- [x] Tabel terbukti hasil bangun ulang byte-identik.
- [x] `CATATAN.md` satu halaman per irisan: konsep inti + temuan.
- [x] Repo GitHub publik `build-your-own-json-decoder-python`
      terbit & terverifikasi.
