# Build Your Own JSON Decoder — Python (Otomaton Bertabel)

Dekoder JSON yang ditulis ulang dari nol di Python murni,
mengikuti **cheery (Henri Tuhola), "JSON Decoding
Algorithm"** — https://github.com/cheery/json-algorithm
(MIT); entri Python kategori Uncategorized di
build-your-own-x.

Ini **bukan** parser turunan-rekursif. Tidak ada fungsi
parse_object / parse_array. Yang ada sebuah **mesin state
42 × 28** yang membaca masukan satu karakter demi satu
karakter: tiap sel tabel mengemas aksi semantik (byte
atas — bangun nilai di tumpukan data/string/escape) dan
transisi (byte bawah — state berikut, atau 0xFF = pop
tumpukan state). Seluruh tata bahasa JSON tinggal di
tabel, dan tabelnya dibangun program lain dari diagram
railroad json.org.

## Contoh

```python
from jsonmesin import parse, baca_aliran, Dekoder

parse('{"a": [1, 2.5, true, null]}')
# {'a': [1, 2.5, True, None]}

# Inkremental: berhenti di karakter mana pun, lanjut kapan pun
d = Dekoder()
d.umpan('{"a": [1,')
d.umpan(' 2]}')
d.selesai()            # {'a': [1, 2]}

# Aliran banyak nilai (saran README panduan sendiri)
baca_aliran('{"a": 1} [1, 2] "teks" 42')
# [{'a': 1}, [1, 2], 'teks', 42]
```

## Rantai asal-usul tabel (semua terbukti di repo ini)

```
diagram json.org
  └─ bangun_tabel.py   (port Python 3 dari build_tables.py hulu)
       └─ json.txt     (berkas hulu, apa adanya)
            └─ buat_tabel.py  (reformatter — panduan melarang
                 memformat tabel dengan tangan)
                 └─ tabel.py  (yang diimpor jsonmesin.py)
```

`uji_irisan4.py` menjalankan `bangun_tabel.py` dan
membuktikan keluarannya **byte-identik** dengan
`json.txt`.

## Verifikasi

| Lapisan | Bukti |
|---|---|
| Skalar & galat | diferensial vs `json.loads` (nilai + tipe), tiga kelas galat panduan |
| Struktur | 300 dokumen acak terseed × 2 mode dumps, 0 selisih; pulang-pergi byte-stabil; sarang 5.000 tingkat |
| Cakupan | baterai 13 masukan penulis panduan: **169/169 transisi mendarat (100%)**, 42/42 state dimasuki |
| Asal-usul | tabel terbangun ulang byte-identik |

Total 83 pemeriksaan: `python3 uji_irisan1.py` …
`uji_irisan4.py`.

## Perilaku yang sengaja setia (bukan bug)

- **Pasangan surrogate** `\uD83D\uDE00` keluar sebagai dua
  titik kode terpisah; `json.loads` menggabungkannya.
  Otomaton tidak punya aksi penggabung.
- **Taksonomi galat** mengikuti karakter penutup spasi:
  terpotong di wadah/string → "truncated", terpotong di
  kata kunci/angka → "syntax", dan "01" → "too many
  objects" (0 tuntas sebagai nilai, 1 memulai nilai kedua).
- **NaN / Infinity ditolak** — itu ekstensi non-standar
  yang hanya diterima `json.loads` secara bawaan.
- Sebuah nilai baru terikat saat karakter berikutnya
  diproses; karena itu parse selalu menutup dengan satu
  spasi pengaman, persis seperti panduan.

Bagian dari seri **build-your-own-x** (fork
`codecrafters-io/build-your-own-x`): implementasi ulang
Python dari panduan-panduan klasik, dikerjakan irisan demi
irisan dengan uji di setiap langkah. Rencana dan pagar
kelengkapan ada di `RENCANA.md`; konsep per irisan dan
temuan selama pengerjaan ada di `CATATAN.md`.

## Lisensi & atribusi

Kode driver adalah penulisan ulang untuk belajar dari
tutorial di README proyek hulu. `json.txt` dan logika
`bangun_tabel.py` berasal dari cheery/json-algorithm,
**MIT License, Copyright (c) 2016 Henri Tuhola** — teks
lisensi lengkap ada di repo hulu:
https://github.com/cheery/json-algorithm/blob/master/LICENSE.md
