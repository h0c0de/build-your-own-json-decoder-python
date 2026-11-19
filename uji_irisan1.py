# Uji irisan 1 — tabel + driver + aksi: baterai skalar,
# diferensial vs json.loads, tiga kelas galat panduan, dan
# divergensi surrogate yang didokumentasikan.
import json
import math

from jsonmesin import GalatJSON, parse

lulus = 0


def cek(nama, kondisi):
    global lulus
    assert kondisi, f"GAGAL: {nama}"
    lulus += 1
    print(f"  ok {lulus:2d}. {nama}")


def sama(teks):
    """parse() harus sama persis (nilai DAN tipe) dgn json."""
    a, b = parse(teks), json.loads(teks)
    return a == b and type(a) is type(b)


def galat(teks, pesan=None):
    try:
        parse(teks)
    except GalatJSON as e:
        return pesan is None or str(e) == pesan
    return False


print("== tabel terbangkitkan dari reformatter ==")
import tabel
cek("42 state x 28 catcode, 42 goto, 127 catcode",
    len(tabel.states) == 42 and len(tabel.states[0]) == 28
    and len(tabel.gotos) == 42 and len(tabel.catcode) == 127)

print("== literal & whitespace ==")
cek("null/true/false", parse("null") is None
    and parse("true") is True and parse("false") is False)
cek("whitespace mengapit diterima", sama(" \t\r\n true \n "))

print("== int ==")
for t in ("0", "123", "-987654321", "10000000000000000000000000000000000000000"):
    cek(f"int {t[:20]}: nilai & tipe == json", sama(t))
cek("-0 menjadi int 0 seperti json", parse("-0") == 0
    and type(parse("-0")) is int)

print("== float ==")
for t in ("3.14", "-0.5", "1e2", "1E+2", "2.5e-3", "0.1", "6.02e23"):
    cek(f"float {t}: nilai & tipe == json", sama(t))
cek("-0.0 bertanda negatif seperti json",
    math.copysign(1, parse("-0.0")) == -1.0)
cek("1e999 -> inf di kedua parser", parse("1e999") == float("inf")
    and json.loads("1e999") == float("inf"))

print("== string & escape ==")
cek("string polos & kosong", sama('"halo dunia"') and sama('""'))
cek('semua escape satu huruf: \\" \\\\ \\/ \\b \\f \\n \\r \\t',
    parse(r'"\"\\\/\b\f\n\r\t"') == "\"\\/\b\f\n\r\t"
    and sama(r'"\"\\\/\b\f\n\r\t"'))
cek("\\u0041 -> 'A', \\u00e9 -> 'é'", sama(r'"Aé"'))
cek("karakter non-ASCII mentah di string", sama('"kopi é"'))
cek("surrogate lepas sama dengan json", sama(r'"\ud83d"'))

print("== divergensi surrogate (terdokumentasi) ==")
pasangan = parse(r'"\ud83d\ude00"')
cek("pasangan surrogate keluar sebagai DUA titik kode",
    pasangan == "\ud83d\ude00" and len(pasangan) == 2)
cek("json.loads menggabungkannya jadi satu (beda!): "
    "otomaton setia pada desain panduan",
    json.loads(r'"\ud83d\ude00"') == "\U0001F600"
    and pasangan != json.loads(r'"\ud83d\ude00"'))

print("== galat: tiga kelas panduan ==")
cek("terpotong wadah/string: '{', '[1,', '\"abc'",
    galat("{", "JSON decode error: truncated")
    and galat("[1,", "JSON decode error: truncated")
    and galat('"abc', "JSON decode error: truncated"))
cek("terpotong kata/angka -> 'syntax' (temuan: karakter "
    "pengaman penutup adalah spasi, dan spasi memang ilegal "
    "di tengah kata kunci/angka, jadi mesin melapor sintaks)",
    galat("tru", "JSON decode error: syntax")
    and galat("nul", "JSON decode error: syntax")
    and galat("1e", "JSON decode error: syntax")
    and galat("-", "JSON decode error: syntax"))
cek("sintaks: 'nulL'", galat("nulL", "JSON decode error: syntax"))
cek("'01' -> 'too many objects' (temuan: '0' tuntas sebagai "
    "nilai, '1' mulai nilai kedua — otomaton membaca aliran)",
    galat("01", "JSON decode error: too many objects"))
cek("sintaks: '+1'", galat("+1", "JSON decode error: syntax"))
cek("sintaks: '.5'", galat(".5", "JSON decode error: syntax"))
cek("kelebihan objek: '1 2'",
    galat("1 2", "JSON decode error: too many objects"))
cek("kelebihan objek: '{} {}'",
    galat("{} {}", "JSON decode error: too many objects"))
cek("masukan kosong -> GalatJSON (too many objects, "
    "mengikuti logika panduan)", galat("", "JSON decode error: too many objects"))
cek("semua masukan rusak lain -> GalatJSON juga",
    all(galat(t) for t in ("[1,]", "{,}", "'kutip'", "1ee2",
                            "--1", "0x10", '"\\u12"', '"\\x"')))
cek("GalatJSON adalah ValueError", issubclass(GalatJSON, ValueError))

print(f"\nIRISAN 1 HIJAU: {lulus} pemeriksaan")
