# Uji irisan 4 — asal-usul tabel, API inkremental, pembaca
# aliran, dan divergensi ketat vs json; plus regresi penuh.
import json
import random
import subprocess
import sys

import tabel
from jsonmesin import Dekoder, GalatJSON, baca_aliran, parse

lulus = 0


def cek(nama, kondisi):
    global lulus
    assert kondisi, f"GAGAL: {nama}"
    lulus += 1
    print(f"  ok {lulus:2d}. {nama}")


print("== asal-usul: tabel terbangun ulang byte-identik ==")
r = subprocess.run([sys.executable, "bangun_tabel.py"],
                   capture_output=True)
asli = open("json.txt", "rb").read()
cek("keluaran bangun_tabel.py == json.txt byte per byte",
    r.returncode == 0 and r.stdout == asli)
ns = {}
exec(r.stdout.decode(), ns)
cek("tabel hasil bangun ulang == tabel.py yang dipakai",
    ns["states"] == tabel.states and ns["gotos"] == tabel.gotos
    and ns["catcode"] == tabel.catcode)

print("== inkremental: umpan potongan == parse utuh ==")
DOK = ('{"nama": "boc0d3r", "nilai": [1, 2.5, {"x": "é\\n"}], '
       '"ok": true, "nol": null}')
utuh = parse(DOK)
d = Dekoder()
for ch in DOK:
    d.umpan(ch)
cek("umpan satu-satu karakter == parse utuh == json.loads",
    d.selesai() == utuh == json.loads(DOK))
rng = random.Random(4)
for percobaan in range(20):
    d = Dekoder()
    i = 0
    while i < len(DOK):
        langkah = rng.randint(1, 9)
        d.umpan(DOK[i:i + langkah])
        i += langkah
    if d.selesai() != utuh:
        break
else:
    percobaan = None
cek("umpan potongan acak (20 pola) == parse utuh", percobaan is None)
d = Dekoder()
d.umpan(DOK[:20])
cek("berhenti di tengah dokumen tanpa galat, lalu lanjut",
    d.umpan(DOK[20:]) is None and d.selesai() == utuh)
try:
    d.umpan(" ")
    cek("umpan sesudah selesai() ditolak", False)
except GalatJSON:
    cek("umpan sesudah selesai() ditolak (dekoder terminal)", True)

print("== pembaca aliran banyak-nilai ==")
cek("aliran campur terbaca berurutan",
    baca_aliran('{"a": 1} [1, 2] "teks" 42 true null 3.5')
    == [{"a": 1}, [1, 2], "teks", 42, True, None, 3.5])
cek("objek berdempet tanpa pemisah tetap terbaca dua",
    baca_aliran("{}{}") == [{}, {}])
cek("angka terakhir tanpa pemisah tuntas oleh bilasan",
    baca_aliran("1 2 3") == [1, 2, 3])
cek("aliran kosong / hanya whitespace -> []",
    baca_aliran("") == [] and baca_aliran("  \n ") == [])
try:
    baca_aliran('{"a": 1} {"b":')
    cek("aliran terpotong di nilai kedua -> truncated", False)
except GalatJSON as e:
    cek("aliran terpotong di nilai kedua -> truncated",
        str(e) == "JSON decode error: truncated")

print("== divergensi ketat: NaN & Infinity ==")
for t in ("NaN", "Infinity", "-Infinity"):
    try:
        parse(t)
        cek(f"{t} ditolak otomaton", False)
    except GalatJSON:
        cek(f"{t} ditolak otomaton (json.loads menerimanya "
            "sebagai ekstensi non-standar)", True)
cek("json.loads memang menerima ketiganya (pembanding jujur)",
    json.loads("NaN") != json.loads("NaN")
    and json.loads("Infinity") == float("inf"))

print("== regresi irisan 1-3 ==")
for n in (1, 2, 3):
    r = subprocess.run([sys.executable, f"uji_irisan{n}.py"],
                       capture_output=True, text=True)
    cek(f"uji_irisan{n} hijau penuh",
        r.returncode == 0 and "HIJAU" in r.stdout)

print(f"\nIRISAN 4 HIJAU: {lulus} pemeriksaan")
