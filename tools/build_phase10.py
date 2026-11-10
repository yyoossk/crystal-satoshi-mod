#!/usr/bin/env python3
"""Phase 10 (on top of phase 9 = 第7弾): new trainer classes with their own battle pictures.
  68 LORELEI  してんのう カンナ   (pic+colors from the Pikachu full-color hack)
  69 AGATHA   してんのう キクコ   (pic+colors from the Pikachu full-color hack)
  70 LANCE_K  してんのう ワタル   (Crystal's Lance picture)
  71 GIOVANNI ロケットだんボス サカキ (pic+colors from the Pikachu full-color hack)
  72 JJ       ロケットだん ムサシとコジロウ (pic+colors from the Pikachu full-color hack)
  73 JR_TRAINER_F ガールスカウト (Red's Jr. Trainer F, pic+colors from the Pikachu full-color hack; parties: later phases)
  74 TAMER    もうじゅうつかい (Red's Tamer, pic+colors from the Pikachu full-color hack; parties: later phases)
  BLUE (64) renamed ライバル: Shigeru (champion) uses Crystal's Blue picture.
Class-indexed tables are relocated to free space and every code reference is patched.
usage: build_phase10.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from jpchar import encode, decode

PKFC = SC + '/pkfc/pkfc.gbc'
PKMN = PR + '/tools/pkmncompress'
LZ = PC + '/tools/lzcompress'
NEWBANK = 0x7C

OLD_N = 67
NEW = ['LORELEI', 'AGATHA', 'LANCE_K', 'GIOVANNI', 'JJ', 'JR_TRAINER_F', 'TAMER']
NEW_N = OLD_N + len(NEW)
CID = {n: OLD_N + 1 + i for i, n in enumerate(NEW)}
# JP addresses (found by matching the US build)
T_GROUPS = 0x399BA
T_ATTR = 0x395BA;  R_ATTR = [(0x395A4, 0), (0x3801F, 5), (0x3811B, 5), (0x44142, 3)]
T_DVS = 0x2742F;   R_DVS = [0x27425]
T_PAL = 0xB08B;    R_PAL = [(0x9719, 4), (0x971D, 0), (0x972D, 0)]
T_PIC = 0x128000
GTP_CP = 0x512A8; GTP_LDHL = 0x512B1
PICSBANKS = 0x5126A; PICS_FIX_BASE = 0x12
NAMESPTR_TRAINER = 0x3389
T_GYMLEADERS = 0x3D12A; R_GYM = [0x3D11B]; R_KANTOGYM = [0x3D116]
# Pikachu full-color hack: trainer pics bank 0x13, palettes table (8 bytes / Gen I class)
PKFC_PICS = {'LORELEI': 0x7413, 'AGATHA': 0x76F1, 'GIOVANNI': 0x630F, 'JJ': 0x798D, 'JR_TRAINER_F': 0x4670, 'TAMER': 0x5B63}
PKFC_PAL_T = 0x26D71
PKFC_PAL_I = {'LORELEI': 44, 'AGATHA': 46, 'GIOVANNI': 29, 'JJ': 48, 'JR_TRAINER_F': 6, 'TAMER': 22}
CLASS_NAME = {'LORELEI': 'してんのう', 'AGATHA': 'してんのう', 'LANCE_K': 'してんのう',
              'GIOVANNI': 'ロケットだんボス', 'JJ': 'ロケットだん', 'JR_TRAINER_F': 'ガールスカウト', 'TAMER': 'もうじゅうつかい'}
COPY_FROM = {'LORELEI': 'KAREN', 'AGATHA': 'KAREN', 'LANCE_K': 'CHAMPION', 'GIOVANNI': 'BLAINE', 'JJ': 'GRUNTM',
             'JR_TRAINER_F': 'PICNICKER', 'TAMER': 'JUGGLER'}
OLDCLS = {'WILL': 11, 'BRUNO': 13, 'KAREN': 14, 'CHAMPION': 16, 'BLAINE': 46, 'GRUNTM': 31, 'BLUE': 64, 'PICNICKER': 53, 'JUGGLER': 49}

MON_ALIAS = {'MR_MIME': 'MR__MIME', 'FARFETCHD': 'FARFETCH_D'}
ESZ = {0: 2, 1: 6, 2: 3, 3: 7}


def gen1_pic_to_crystal(rom, bank, addr):
    with tempfile.TemporaryDirectory() as d:
        open(d + '/a.pic', 'wb').write(rom[bank * 0x4000 + addr - 0x4000:][:1500])
        subprocess.run([PKMN, '-u', d + '/a.pic', d + '/a.2bpp'], check=True)
        raw = open(d + '/a.2bpp', 'rb').read()
        w = int(round((len(raw) // 16) ** 0.5))
        assert w == 7, w
        col = b''.join(raw[(y * 7 + x) * 16:(y * 7 + x) * 16 + 16] for x in range(7) for y in range(7))
        open(d + '/c.2bpp', 'wb').write(col)
        subprocess.run([LZ, d + '/c.2bpp', d + '/c.lz'], check=True, stdout=subprocess.DEVNULL)
        return open(d + '/c.lz', 'rb').read(), raw


def red_parties():
    """pokered parties: class -> list of [(lv, species)]"""
    from collections import OrderedDict
    txt = open(PR + '/data/trainers/parties.asm', encoding='utf-8').read().split('\n')
    labels = [m.group(1) for l in txt for m in [re.match(r'\s*dw\s+(\w+Data)', l)] if m]
    consts = [m.group(1) for l in open(PR + '/constants/trainer_constants.asm', encoding='utf-8')
              for m in [re.match(r'\s*trainer_const\s+(\w+)', l)] if m][1:]
    lab2 = dict(zip(labels, consts)); data = {}; cur = None
    for l in txt:
        s = l.split(';')[0].strip()
        m = re.match(r'^(\w+Data):$', s)
        if m:
            cur = lab2.get(m.group(1)); data[cur] = []; continue
        m = re.match(r'db\s+(.*)', s)
        if m and cur:
            v = [x.strip() for x in m.group(1).split(',')]
            if v[0] in ('$FF', '$ff'):
                v = v[1:-1]; data[cur].append([(int(v[i]), v[i + 1]) for i in range(0, len(v), 2)])
            else:
                data[cur].append([(int(v[0]), x) for x in v[1:-1]])
    return data


def parse_groups(rom, last_end=None):
    bank = T_GROUPS // 0x4000
    ptr = [bank * 0x4000 + ((rom[T_GROUPS + 2 * g] | rom[T_GROUPS + 2 * g + 1] << 8) - 0x4000) for g in range(OLD_N)]
    out = []; end = None
    for g in range(OLD_N):
        o = ptr[g]; nxt = ptr[g + 1] if g + 1 < OLD_N else last_end; parties = []
        while (nxt is None and len(parties) < 1) or (nxt is not None and o < nxt):
            if rom[o] == 0xFF:
                o += 1; continue
            e = rom.index(0x50, o); name = rom[o:e + 1]; o = e + 1
            t = rom[o]; q = o + 1
            while rom[q] != 0xFF:
                q += ESZ[t]
            parties.append([bytes(name), bytes(rom[o:q + 1])]); o = q + 1
        out.append(parties); end = o
    return ptr[0], out, end


def main():
    src, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src, 'rb').read())
    pk = open(PKFC, 'rb').read()
    MON = load_consts(PC + '/constants/pokemon_constants.asm')
    RP = red_parties()
    log = []

    def w16(off, v): rom[off] = v & 0xFF; rom[off + 1] = v >> 8
    def r16(off): return rom[off] | rom[off + 1] << 8
    def gaddr(off): return 0x4000 + off % 0x4000

    # ---------------- new bank 0x7C layout
    assert not any(rom[NEWBANK * 0x4000:(NEWBANK + 1) * 0x4000])
    cur = [0x4000]
    def put7c(data):
        a = cur[0]; o = NEWBANK * 0x4000 + a - 0x4000
        rom[o:o + len(data)] = data; cur[0] += len(data); assert cur[0] <= 0x8000
        return a

    # pics
    assert rom[PICSBANKS:PICSBANKS + 24] == bytes(range(0x48, 0x60))
    rom[PICSBANKS + 24] = NEWBANK                     # overwrites unreferenced GS intro code
    PICBANK_STORED = PICS_FIX_BASE + 24
    pic_entry = {}
    for n, a in PKFC_PICS.items():
        lz, raw = gen1_pic_to_crystal(pk, 0x13, a)
        p = put7c(lz)
        pic_entry[n] = bytes([PICBANK_STORED, p & 0xFF, p >> 8])
        log.append('pic %s: %d bytes @7C:%04X' % (n, len(lz), p))
    old_pics = bytes(rom[T_PIC:T_PIC + OLD_N * 3])
    pic_entry['LANCE_K'] = old_pics[(OLDCLS['CHAMPION'] - 1) * 3:(OLDCLS['CHAMPION'] - 1) * 3 + 3]
    newpics = old_pics + b''.join(pic_entry[n] for n in NEW)
    tp = put7c(newpics)
    assert rom[GTP_CP:GTP_CP + 3] == bytes([0xFE, OLD_N + 1, 0xD0])
    rom[GTP_CP + 1] = NEW_N + 1
    assert rom[GTP_LDHL:GTP_LDHL + 3] == b'\x21\x00\x40'
    w16(GTP_LDHL + 1, tp)
    seg = rom[GTP_LDHL:GTP_LDHL + 40]
    ks = [m.start() for m in re.finditer(b'\x3e\x4a', bytes(seg))]
    assert len(ks) == 2, ks
    for k in ks:
        rom[GTP_LDHL + k + 1] = NEWBANK

    # class names
    nb = rom[NAMESPTR_TRAINER]; na = r16(NAMESPTR_TRAINER + 1)
    no = fo(nb, na); names = []; o = no
    for i in range(OLD_N):
        e = rom.index(0x50, o); names.append(bytes(rom[o:e + 1])); o = e + 1
    assert decode(names[OLDCLS['BLUE'] - 1]) == 'ジムりーダー@'
    names[OLDCLS['BLUE'] - 1] = encode('ライバル@')
    names += [encode(CLASS_NAME[n] + '@') for n in NEW]
    np_ = put7c(b''.join(names))
    rom[NAMESPTR_TRAINER] = NEWBANK; w16(NAMESPTR_TRAINER + 1, np_)

    # palettes (bank 2)
    pal = bytearray(rom[T_PAL:T_PAL + (OLD_N + 1) * 4])
    for n in NEW:
        if n in PKFC_PAL_I:
            e = pk[PKFC_PAL_T + 8 * PKFC_PAL_I[n]:PKFC_PAL_T + 8 * PKFC_PAL_I[n] + 8]
            assert e[0:2] == b'\xff\x7f'
            pal += e[2:6]
        else:
            c = OLDCLS[COPY_FROM[n]]; pal += rom[T_PAL + 4 * c:T_PAL + 4 * c + 4]
    fs, fl = bank_free_tail(rom, 2); fs += 1
    assert len(pal) < fl
    rom[fs:fs + len(pal)] = pal; npal = gaddr(fs)
    for off, d in R_PAL:
        assert r16(off + 1) == gaddr(T_PAL) + d, hex(off)
        w16(off + 1, npal + d)

    # DVs (bank 9)
    dvs = bytearray(rom[T_DVS:T_DVS + OLD_N * 2])
    for n in NEW:
        c = OLDCLS[COPY_FROM[n]]; dvs += rom[T_DVS + 2 * (c - 1):T_DVS + 2 * (c - 1) + 2]
    fs, fl = bank_free_tail(rom, 9); fs += 1
    assert len(dvs) < fl
    rom[fs:fs + len(dvs)] = dvs
    for off in R_DVS:
        assert r16(off + 1) == gaddr(T_DVS); w16(off + 1, gaddr(fs))

    # party data + attributes (bank 0x0E)
    start, G, old_end = parse_groups(bytes(rom))
    assert start == T_GROUPS + OLD_N * 2
    def pb(mons): return b'\x00' + b''.join(bytes([lv, MON[MON_ALIAS.get(s, s)]]) for lv, s in mons) + b'\xff'
    newG = {
        'LORELEI': [(encode('カンナ@'), pb(RP['LORELEI'][0]))],
        'AGATHA': [(encode('キクコ@'), pb(RP['AGATHA'][0]))],
        'LANCE_K': [(encode('ワタル@'), pb(RP['LANCE'][0]))],
        'GIOVANNI': [(encode('サカキ@'), pb(p)) for p in RP['GIOVANNI']],
        'JJ': [(encode('ムサシとコジロウ@'), pb(p)) for p in
               [[(14, 'EKANS'), (14, 'MEOWTH'), (14, 'KOFFING')], [(25, 'KOFFING'), (25, 'MEOWTH'), (25, 'EKANS')],
                [(27, 'MEOWTH'), (27, 'ARBOK'), (27, 'WEEZING')], [(31, 'WEEZING'), (31, 'ARBOK'), (31, 'MEOWTH')]]],
        'JR_TRAINER_F': [],
        'TAMER': [],
    }
    # Shigeru (champion) -> BLUE class, after Blue's own party
    shig = []
    for i in range(3):
        shig.append((encode('シゲル@'), pb(RP['RIVAL3'][i])))
    blue_first = len(G[OLDCLS['BLUE'] - 1]) + 1
    G[OLDCLS['BLUE'] - 1] += [list(x) for x in shig]
    for n in NEW:
        G.append([list(x) for x in newG[n]])
    tbl_end = T_GROUPS + NEW_N * 2
    out = bytearray(); ptrs = []
    for g in range(NEW_N):
        ptrs.append(tbl_end + len(out))
        for name, data in G[g]:
            out += name + data
    attr = bytearray(rom[T_ATTR:T_ATTR + OLD_N * 7])
    for n in NEW:
        c = OLDCLS[COPY_FROM[n]]; attr += rom[T_ATTR + 7 * (c - 1):T_ATTR + 7 * (c - 1) + 7]
    attr_off = tbl_end + len(out)
    limit = (T_GROUPS // 0x4000 + 1) * 0x4000
    assert attr_off + len(attr) <= limit, hex(attr_off + len(attr))
    clear_to = max(old_end, attr_off + len(attr))
    rom[T_GROUPS:clear_to] = bytes(clear_to - T_GROUPS)
    for g, p in enumerate(ptrs):
        w16(T_GROUPS + 2 * g, gaddr(p))
    rom[tbl_end:tbl_end + len(out)] = out
    rom[attr_off:attr_off + len(attr)] = attr
    for off, d in R_ATTR:
        assert r16(off + 1) == gaddr(T_ATTR) + d, (hex(off), hex(r16(off + 1)))
        w16(off + 1, gaddr(attr_off) + d)
    log.append('party data %X-%X, attributes @%X (bank end %X)' % (tbl_end, attr_off, attr_off + len(attr), limit))

    # gym leader lists (bank 0x0F): E4 classes -> Johto list, Giovanni -> Kanto list
    old = bytes(rom[T_GYMLEADERS:T_GYMLEADERS + 23]); assert old[-1] == 0xFF
    johto, kanto = old[:14], old[14:22]
    nl = johto + bytes([CID['LORELEI'], CID['AGATHA'], CID['LANCE_K']]) + kanto + bytes([CID['GIOVANNI'], 0xFF])
    fs, fl = bank_free_tail(rom, 0x0F); fs += 1
    rom[fs:fs + len(nl)] = nl
    for off in R_GYM:
        assert r16(off + 1) == gaddr(T_GYMLEADERS); w16(off + 1, gaddr(fs))
    for off in R_KANTOGYM:
        assert r16(off + 1) == gaddr(T_GYMLEADERS) + 14; w16(off + 1, gaddr(fs) + 17)

    # scripts: Elite Four + champion loadtrainer
    mb = MODBANK * 0x4000
    seg = bytes(rom[mb + 0x1400:mb + 0x2000])
    def repl(old, new, cnt=1):
        h = [m.start() for m in re.finditer(re.escape(old), seg)]
        assert len(h) == cnt, (old.hex(), h)
        for x in h:
            rom[mb + 0x1400 + x:mb + 0x1400 + x + len(new)] = new
    repl(bytes([0x5D, OLDCLS['KAREN'], 2]), bytes([0x5D, CID['LORELEI'], 1]))
    repl(bytes([0x5D, OLDCLS['KAREN'], 3]), bytes([0x5D, CID['AGATHA'], 1]))
    repl(bytes([0x5D, OLDCLS['WILL'], 2]), bytes([0x5D, CID['LANCE_K'], 1]))
    for i, k in enumerate([2, 3, 4]):
        repl(bytes([0x5D, OLDCLS['CHAMPION'], k]), bytes([0x5D, OLDCLS['BLUE'], blue_first + i]))
    log.append('Shigeru = BLUE class ids %d-%d; new class ids %s' % (blue_first, blue_first + 2, CID))

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    print('\n'.join(log))


if __name__ == '__main__':
    main()
