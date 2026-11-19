# Uji irisan 2 — struktur: wadah bersarang, kunci duplikat,
# sarang dalam, galat struktural, dan diferensial acak
# terseed melawan json.loads.
import json
import random
import string

from jsonmesin import GalatJSON, parse

lulus = 0


def cek(nama, kondisi):
    global lulus
    assert kondisi, f"GAGAL: {nama}"
    lulus += 1
    print(f"  ok {lulus:2d}. {nama}")


def sama(teks):
    return parse(teks) == json.loads(teks)


print("== wadah dasar ==")
cek("array & objek kosong", parse("[]") == [] and parse("{}") == {})
cek("bersarang campur", sama('{"a": [1, {"b": [true, null]}], "c": []}'))
cek("kunci string kosong & nilai kosong", sama('{"": {"": []}}'))
cek("dokumen realistis",
    sama('{"nama": "boc0d3r", "skor": [9.5, 8, 7.25], '
         '"aktif": true, "meta": {"versi": 3, "label": ["x", "y"]}, '
         '"kosong": null}'))
cek("whitespace di semua celah", sama(' { "a" : [ 1 , 2 ] , "b" : { } } '))

print("== kunci: urutan & duplikat ==")
d = parse('{"z": 1, "a": 2, "m": 3}')
cek("urutan kunci dipertahankan seperti json",
    list(d) == list(json.loads('{"z": 1, "a": 2, "m": 3}')) == ["z", "a", "m"])
cek("kunci duplikat: yang terakhir menang, seperti json",
    parse('{"a": 1, "a": 2}') == json.loads('{"a": 1, "a": 2}') == {"a": 2})

print("== sarang dalam ==")
for n in (100, 1000):
    teks = "[" * n + "]" * n
    cek(f"array bersarang {n} tingkat == json", parse(teks) == json.loads(teks))
teks = "[" * 5000 + "]" * 5000
dalam = parse(teks)
kedalaman, simpul = 0, dalam
while isinstance(simpul, list) and simpul:
    kedalaman += 1
    simpul = simpul[0]
cek("otomaton menembus 5000 tingkat (tumpukan heap, "
    "tanpa rekursi)", kedalaman == 4999)

print("== galat struktural ==")
for t in ('{"a":}', '{"a" 1}', "[1 2]", '{"a":1,}', "{a:1}",
          "[}", "{]", '{"a":1]', "[1}", '{"a"}', "[,]", "{,}"):
    try:
        parse(t)
        cek(f"galat struktural {t!r}", False)
    except GalatJSON:
        cek(f"galat struktural {t!r} -> GalatJSON", True)

print("== diferensial acak terseed vs json.loads ==")
rng = random.Random(20261120)
ALFABET = (string.ascii_letters + string.digits + " _-."
           + "éü" + "中文" + "\n\t\"\\/")


def nilai(kedalaman):
    if kedalaman > 3:
        jenis = rng.choice(["null", "bool", "int", "float", "str"])
    else:
        jenis = rng.choice(["null", "bool", "int", "float", "str",
                            "list", "dict"])
    if jenis == "null":
        return None
    if jenis == "bool":
        return rng.random() < 0.5
    if jenis == "int":
        return rng.choice([rng.randint(-100, 100),
                           rng.randint(-10**25, 10**25)])
    if jenis == "float":
        return rng.choice([rng.uniform(-1e6, 1e6),
                           rng.random() * 10 ** rng.randint(-20, 20)])
    if jenis == "str":
        return "".join(rng.choice(ALFABET)
                       for _ in range(rng.randint(0, 12)))
    if jenis == "list":
        return [nilai(kedalaman + 1) for _ in range(rng.randint(0, 5))]
    return {"".join(rng.choice(string.ascii_lowercase)
                    for _ in range(rng.randint(1, 6))):
            nilai(kedalaman + 1) for _ in range(rng.randint(0, 5))}


gagal = 0
for i in range(300):
    v = nilai(0)
    teks = json.dumps(v)
    if parse(teks) != v or parse(teks) != json.loads(teks):
        gagal += 1
    teks2 = json.dumps(v, ensure_ascii=False)
    if parse(teks2) != v:
        gagal += 1
cek("300 dokumen acak x 2 mode dumps: parse == nilai asal "
    "== json.loads, 0 selisih", gagal == 0)

print("== pulang-pergi: dumps(parse(dumps(v))) stabil ==")
gagal = 0
for i in range(100):
    v = nilai(0)
    if json.dumps(parse(json.dumps(v))) != json.dumps(v):
        gagal += 1
cek("100 dokumen: teks hasil pulang-pergi byte-stabil", gagal == 0)

print("== regresi irisan 1 ==")
import subprocess
import sys
r = subprocess.run([sys.executable, "uji_irisan1.py"],
                   capture_output=True, text=True)
cek("uji_irisan1 hijau penuh", r.returncode == 0 and "HIJAU" in r.stdout)

print(f"\nIRISAN 2 HIJAU: {lulus} pemeriksaan")
