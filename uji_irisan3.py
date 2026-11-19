# Uji irisan 3 — baterai penulisnya + cakupan: 13 masukan
# dari verifier.py penulis panduan dijalankan ke parse()
# kita; cakupan diukur dengan metrik penulis sendiri
# (pasangan (state, cat) pada transisi yang mendarat) dan
# dilengkapi bukti seluruh state dimasuki.
import json
import subprocess
import sys

import jsonmesin
import tabel
from jsonmesin import parse

lulus = 0


def cek(nama, kondisi):
    global lulus
    assert kondisi, f"GAGAL: {nama}"
    lulus += 1
    print(f"  ok {lulus:2d}. {nama}")


# 13 masukan dari verifier.py (cheery/json-algorithm, MIT),
# disalin sebagai data — berkas py2 aslinya tidak diimpor.
MASUKAN_PENULIS = [
    '\n        true\n    ',
    '\n        false\n    ',
    '\n        null\n    ',
    '\n        "hello"\n    ',
    '\n        -5\n    ',
    '\n        5\n    ',
    '\n        0\n    ',
    '\n        { }\n    ',
    '\n        [ 22.0e+02, "+,-./0:E[]bnstu{}\\b\\f\\t", 1100, 100.01, -0.2e00 ]\n    ',
    '\n        { "":43, "fo\\u006Fo" : 41E2, "":"", "":[],\n          "\\uAAAA\\uEEEE\\uaaaa\\ubbbb\\ueeee\\uffff\\u0000\\u111101":true, "":false, "":null, "":{} }\n    ',
    '\n        [ -21, -32e+3, 2.3E-1, {"":true},\n            {"":false}, {"":null}, 0.20e0\n        ]\n    ',
    '\n        [ [true], [false], [{"":-1}], {"":[]} ]\n    ',
    '\n        [\n            [ "hello\\u0020world\\r\\n" ],\n            null,    true,     false,\n            [                    ],\n            [ "\\/\\\\hello \\"world\\""  ],\n            [ null, 123, "hllo", 0, {"":0.00}, [0E-0] ],\n            { "a" : {\n                "x": "y",\n                "z": -1.5,\n                "w": 12e3,\n                "q": 0e1\n            }},\n            true\n        ]\n    ',
]

print("== baterai penulis: nilai ==")
jejak = set()
semua_sama = True
for t in MASUKAN_PENULIS:
    if parse(t, jejak) != json.loads(t):
        semua_sama = False
cek("13 masukan penulis: parse == json.loads untuk semuanya",
    semua_sama and len(MASUKAN_PENULIS) == 13)

print("== cakupan metrik penulis ==")
total = sum(1 for row in tabel.states for code in row
            if code & 0xFF != 0xFF)
cek(f"transisi mendarat terunjungi {len(jejak)}/{total} = 100%",
    len(jejak) == total)

print("== seluruh state dimasuki ==")


class TabelLacak(list):
    """Proxy tabel yang mencatat indeks baris yang dibaca
    driver — yaitu state yang sedang dimasuki."""

    def __getitem__(self, i):
        if isinstance(i, int):
            dimasuki.add(i)
        return super().__getitem__(i)


dimasuki = set()
asli = jsonmesin.states
jsonmesin.states = TabelLacak(asli)
try:
    for t in MASUKAN_PENULIS:
        parse(t)
finally:
    jsonmesin.states = asli
cek(f"state dimasuki {len(dimasuki)}/42 (7 state hanya "
    "keluar lewat pop — tetap dimasuki & bekerja)",
    dimasuki == set(range(42)))

print("== regresi irisan 1-2 ==")
for n in (1, 2):
    r = subprocess.run([sys.executable, f"uji_irisan{n}.py"],
                       capture_output=True, text=True)
    cek(f"uji_irisan{n} hijau penuh",
        r.returncode == 0 and "HIJAU" in r.stdout)

print(f"\nIRISAN 3 HIJAU: {lulus} pemeriksaan")
