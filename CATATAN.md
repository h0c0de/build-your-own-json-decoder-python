# Catatan — JSON Decoder (otomaton bertabel)

Satu halaman per irisan: konsep inti + temuan selama
pengerjaan. Panduan: cheery, "JSON Decoding Algorithm".

## Konsep besar (sebelum irisan 1)

Parser ini kebalikan dari parser turunan-rekursif: tidak ada
fungsi parse_object/parse_array. Yang ada sebuah mesin state
42 baris × 28 kategori karakter; tiap sel mengemas dua hal —
aksi semantik (byte atas: bangun nilai di tumpukan data /
string / escape) dan transisi (byte bawah: state berikut,
atau 0xFF = pop tumpukan state). Shift ditandai bit 0x80
pada aksi: state goto didorong sebelum aksi jalan. Seluruh
tata bahasa JSON tinggal di tabel, dan tabelnya sendiri
dibangun program lain dari diagram json.org — jadi build ini
punya dua lapis untuk dibuktikan: tabelnya benar (bangkitkan
ulang, bandingkan byte), dan driver-nya setia (diferensial
melawan json bawaan Python).

## Irisan 1 — Tabel + driver + aksi

Konsep inti: **seluruh tata bahasa tinggal di tabel.**
Driver-nya generik total — ia hanya membaca sel
[state][catcode], membongkar aksi (byte atas) dan transisi
(byte bawah), menjalankan satu dari 14 aksi semantik, dan
mengulang bila transisinya pop. Tidak ada satu pun aturan
JSON di kode driver; mengganti tabel berarti mengganti
bahasanya.

Temuan:
- Taksonomi galat otomaton tidak intuitif tetapi konsisten:
  ia ditentukan oleh karakter pengaman penutup (spasi yang
  disuntikkan di akhir parse). Spasi legal di tengah
  wadah/string → masukan terpotong di sana berujung
  "truncated"; spasi ilegal di tengah kata kunci/angka →
  "tru" dan "1e" berujung "syntax". Dan "01" berujung
  "too many objects": '0' sudah tuntas sebagai nilai,
  '1' memulai nilai kedua — mesin ini pada dasarnya
  pembaca aliran, cek satu-nilai di parse() yang menahan
  sifat itu.
- Pasangan surrogate \uD83D\uDE00 keluar sebagai dua titik
  kode terpisah; json.loads menggabungkannya menjadi satu
  karakter. Otomaton tidak punya aksi penggabung — dicatat
  sebagai divergensi yang disengaja-setia, bukan bug.
- Angka berperilaku persis seperti json: -0 int, -0.0
  bertanda, int sebarang-besar eksak, 1e999 → inf di kedua
  parser.

## Irisan 2 — Struktur

Konsep inti: **bersarang = tumpukan, bukan rekursi.**
Aksi shift mendorong state goto setiap kali wadah dibuka;
aksi pop & append (0x3) dan pop pop & setitem (0x4)
menyelesaikan nilai ke wadah tepat di bawahnya di tumpukan
data. Kedalaman sarang hanya sepanjang memori tumpukan.

Temuan:
- Nol perubahan implementasi: keempat aksi wadah dari
  irisan 1 langsung lulus seluruh baterai struktur.
- Diferensial acak: 300 dokumen terseed × 2 mode dumps
  (ASCII dan UTF-8 mentah) — 0 selisih nilai melawan nilai
  asal dan json.loads; 100 dokumen pulang-pergi
  dumps→parse→dumps byte-stabil.
- Otomaton menembus sarang 5.000 tingkat karena tumpukannya
  di heap; parser rekursif akan menyerahkan batasnya pada
  batas rekursi bahasa.

## Irisan 3 — Baterai penulisnya + cakupan state

Konsep inti: **cara memverifikasi tabel bukanlah menguji
keluaran saja, melainkan membuktikan setiap transisi
pernah berjalan.** Penulis merancang 13 masukan yang
memicu seluruh mesin; metriknya adalah pasangan
(state, catcode) pada transisi yang mendarat (transisi
pop tidak dihitung — ia tidak mengonsumsi karakter).

Temuan:
- Ke-13 masukan penulis menghasilkan nilai yang sama
  dengan json.loads di driver kita.
- Cakupan metrik penulis: 169/169 transisi mendarat =
  100%. Baterainya memang lengkap untuk tabelnya sendiri.
- Halus: hanya 35 state yang muncul sebagai sumber
  transisi mendarat; 7 state sisanya hanya keluar lewat
  pop. Dengan proxy tabel yang mencatat baris terbaca,
  terbukti ke-42 state benar-benar dimasuki dan bekerja —
  metrik penulis tidak salah, hanya tidak menghitung
  pintu keluar jenis itu.

## Irisan 4 — Asal-usul + aliran + terbit

Konsep inti: **sebuah nilai baru terikat (commit) saat
karakter berikutnya diproses.** State "selesai" tidak
unik — objek tuntas di state 25, array di 17, string di
33 — dan pada string/kata kunci nilainya bahkan belum
naik ke tumpukan data sampai karakter pemisah tiba.
Itulah sebabnya panduan selalu menutup parse dengan satu
spasi pengaman, dan resep alirannya menyuruh pengirim
menyisipkan whitespace sesudah tiap pesan.

Temuan:
- Rantai asal-usul tertutup di dalam repo: port Python 3
  pembangun tabel (hanya blok print yang berubah dari
  Python 2 aslinya) menghasilkan json.txt byte-identik.
- Desain baca_aliran pertamaku (terbitkan nilai begitu
  state kembali ke 0) SALAH untuk nilai berdempet tanpa
  pemisah ("{}{}" hanya terbaca satu) — jejak state
  membuktikan kenapa, dan bentuk benarnya justru lebih
  sederhana: beri makan semua, bilas, panen tumpukan data.
- Dekoder inkremental lulus umpan per karakter dan 20
  pola potongan acak melawan parse utuh.
- NaN/Infinity ditolak otomaton: ia patuh spesifikasi,
  json.loads yang longgar (ekstensi bawaan Python).
- Total seri uji build ini: 83 pemeriksaan (35+25+5+18).
