# jsonmesin.py — Dekoder JSON otomaton bertabel.
#
# Ditulis ulang mengikuti tutorial di README proyek
# cheery/json-algorithm (MIT, Henri Tuhola):
# https://github.com/cheery/json-algorithm
#
# Idenya: tidak ada parser rekursif. Sebuah mesin state
# (tabel di tabel.py, dibangun dari diagram railroad
# json.org) membaca masukan SATU KARAKTER demi satu
# karakter. Tiap sel tabel mengemas aksi semantik (byte
# atas) dan transisi state (byte bawah; 0xFF = pop tumpukan
# state). Aksi dengan bit 0x80 adalah "shift": state goto
# didorong ke tumpukan dulu. Nilai dibangun di tiga
# tumpukan: ds (data), ss (string), es (escape \uXXXX).
from tabel import catcode, gotos, states


class GalatJSON(ValueError):
    """Galat dekode JSON. Pesannya persis tiga pesan
    panduan: 'syntax', 'truncated', 'too many objects'."""


# Escape satu huruf yang tidak trivial (panduan).
escape_characters = {'b': 8, 't': 9, 'n': 10, 'f': 12, 'r': 13}


def _aksi(action, ch, ds, ss, es):
    """14 aksi semantik panduan (0x1-0xE)."""
    if action == 0x1:                # push list
        ds.append([])
    elif action == 0x2:              # push object
        ds.append({})
    elif action == 0x3:              # pop & append
        val = ds.pop()
        ds[len(ds) - 1].append(val)
    elif action == 0x4:              # pop pop & setitem
        val = ds.pop()
        key = ds.pop()
        ds[len(ds) - 1][key] = val
    elif action == 0x5:              # push null
        ds.append(None)
    elif action == 0x6:              # push true
        ds.append(True)
    elif action == 0x7:              # push false
        ds.append(False)
    elif action == 0x8:              # push string
        ds.append("".join(ss))
        ss[:] = []                   # bersihkan ss dan es
        es[:] = []
    elif action == 0x9:              # push int
        ds.append(int("".join(ss)))
        ss[:] = []
    elif action == 0xA:              # push float
        ds.append(float("".join(ss)))
        ss[:] = []
    elif action == 0xB:              # push ch to ss
        ss.append(ch)
    elif action == 0xC:              # push ch to es
        es.append(ch)
    elif action == 0xD:              # push escape
        ss.append(chr(escape_characters[ch]))
    elif action == 0xE:              # push unicode point
        ss.append(chr(int("".join(es), 16)))
        es[:] = []
    else:  # titik tabrak panduan: jangan pernah sampai sini
        assert False, "JSON decoder bug"


def _parse_ch(cat, ch, stack, state, ds, ss, es, jejak=None):
    """Proses satu karakter; bisa beberapa transisi bila
    transisinya pop (0xFF) — karakter yang sama dinilai
    ulang di state hasil pop. `jejak` (bila diberi set)
    mencatat pasangan (state, cat) setiap transisi yang
    mendarat — instrumentasi cakupan meniru verifier.py
    penulis panduan."""
    while True:
        code = states[state][cat]
        action = code >> 8 & 0xFF
        code = code & 0xFF
        if action == 0xFF and code == 0xFF:
            raise GalatJSON("JSON decode error: syntax")
        elif action >= 0x80:         # shift
            stack.append(gotos[state])
            action -= 0x80
        if action > 0:
            _aksi(action, ch, ds, ss, es)
        if code == 0xFF:
            state = stack.pop()
        else:
            if jejak is not None:
                jejak.add((state, cat))
            return code


class Dekoder:
    """Dekoder inkremental — sifat khas algoritma panduan:
    mesin bisa diberi makan potongan demi potongan dan
    berhenti di karakter mana pun, lalu dilanjutkan.
    umpan() mengonsumsi teks; selesai() menutup aliran
    (menyuntikkan karakter pengaman penutup seperti
    panduan) dan mengembalikan nilai tunggalnya."""

    def __init__(self, jejak=None):
        self.stack = []
        self.state = 0x00
        self.ds = []  # data stack
        self.ss = []  # string stack
        self.es = []  # escape stack
        self.jejak = jejak
        self._tutup = False

    def umpan(self, teks):
        if self._tutup:
            raise GalatJSON("JSON decode error: decoder closed")
        for ch in teks:
            cat = catcode[min(ord(ch), 0x7E)]
            self.state = _parse_ch(cat, ch, self.stack,
                                   self.state, self.ds,
                                   self.ss, self.es, self.jejak)

    def _bilas(self):
        """Karakter pengaman penutup (spasi) panduan."""
        self.state = _parse_ch(catcode[32], '', self.stack,
                               self.state, self.ds, self.ss,
                               self.es, self.jejak)

    def selesai(self):
        """Tutup aliran dan kembalikan nilai tunggalnya.
        Terminal: dekoder tidak bisa dipakai lagi sesudahnya."""
        if self._tutup:
            raise GalatJSON("JSON decode error: decoder closed")
        self._tutup = True
        self._bilas()
        if self.state != 0x00:
            raise GalatJSON("JSON decode error: truncated")
        if len(self.ds) != 1:
            raise GalatJSON("JSON decode error: too many objects")
        return self.ds.pop()


def parse(teks, jejak=None):
    """Dekode satu dokumen JSON menjadi nilai Python
    (dict/list/str/int/float/bool/None), setara json.loads
    untuk JSON yang sah menurut spesifikasi. `jejak`
    diteruskan ke _parse_ch untuk uji cakupan."""
    d = Dekoder(jejak)
    d.umpan(teks)
    return d.selesai()


def baca_aliran(teks):
    """Baca BANYAK nilai JSON berurutan dari satu teks —
    modifikasi yang disarankan README panduan sendiri
    ("parse multiple objects as they appear in the stream").

    Cara kerja otomaton yang menentukan desainnya: sebuah
    nilai baru BENAR-BENAR terikat (committed) ke tumpukan
    data saat karakter BERIKUTNYA diproses — itu sebabnya
    panduan selalu menutup dengan karakter spasi, dan
    resep aliran di README menyuruh pengirim menyisipkan
    whitespace sesudah tiap pesan. Jadi fungsi ini memberi
    makan seluruh teks, membilas dengan spasi penutup,
    lalu memanen tumpukan data: urutannya persis urutan
    kemunculan nilai. Aliran yang terpotong di tengah
    nilai berakhir di state != 0 -> galat truncated."""
    d = Dekoder()
    d.umpan(teks)
    d._bilas()
    if d.state != 0x00:
        raise GalatJSON("JSON decode error: truncated")
    hasil = list(d.ds)
    d.ds[:] = []
    return hasil
