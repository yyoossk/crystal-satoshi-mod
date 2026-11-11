"""Generic porting of Gen I (Pikachu full-color hack / pokeyellow) maps into the JP Crystal MOD.
Used from phase 16 on."""
import re, os, json
from lib import *
from portlib import *
from jpchar import encode, decode
import pkmap
import build_phase10 as P10
import build_phase11 as P11
import build_phase12 as P12
import build_phase13 as P13
import build_phase14 as P14
import build_phase15 as P15

MON = load_consts(PC + '/constants/pokemon_constants.asm')
ITEM = load_consts(PC + '/constants/item_constants.asm')
TCLS = {}
for l in open(PC + '/constants/trainer_constants.asm', encoding='utf-8'):
    m = re.match(r'\s*trainerclass (\w+)\s*;\s*([0-9a-f]+)', l)
    if m: TCLS[m.group(1)] = int(m.group(2), 16)
TCLS['ROCKET'] = TCLS['GRUNTM']
TCLS['SWIMMER'] = TCLS['SWIMMERM']
TCLS['JR_TRAINER_F'] = 73                     # phase 10: ガールスカウト
TCLS['TAMER'] = 74                            # phase 10: もうじゅうつかい
TCLS.update({'JR_TRAINER_M': 75, 'ENGINEER': 76, 'CUE_BALL': 77, 'GAMBLER': 78, 'ROCKER': 79})   # phase 10 (added for phase 33)
TCLS['COOLTRAINER_M'] = TCLS['COOLTRAINERM']
TCLS['COOLTRAINER_F'] = TCLS['COOLTRAINERF']
TCLS['BLACKBELT'] = TCLS['BLACKBELT_T']
RED_DATA = {}
for l in open(PR + '/data/trainers/parties.asm', encoding='utf-8'):
    m = re.match(r'(\w+)Data:', l)
    if m: RED_DATA[re.sub(r'(?<!^)(?=[A-Z])', '_', m.group(1)).upper()] = m.group(1) + 'Data'
SPR = dict(P15.SPR)
SPR.update({'SPRITE_CAPTAIN': 0x46, 'SPRITE_SAILOR': 0x49, 'SPRITE_GENTLEMAN': 0x40, 'SPRITE_FISHER': 0x3A,
            'SPRITE_COOLTRAINER_M': 0x23, 'SPRITE_GIRL': 0x28, 'SPRITE_GRAMPS': 0x2F, 'SPRITE_MONSTER': 0x4C,
            'SPRITE_MIDDLE_AGED_MAN': 0x2D, 'SPRITE_BILL': 0x08})
for i, s in enumerate(P14.NEW_SPRITES):
    SPR[s[0]] = 0x67 + i
NAMEPOOL = ['タカシ', 'ヒロシ', 'マコト', 'ユウジ', 'ケンタ', 'ショウタ', 'ダイスケ', 'リョウ', 'ナオキ', 'カズヤ',
            'ユミ', 'アヤ', 'ミキ', 'サオリ', 'エミ', 'ナナ']
TM_NUM = {'TM_BODY_SLAM': 8, 'TM_REST': 44}
for _i, _m in enumerate(re.findall(r'^\s*add_tm (\w+)', open(PR + '/constants/item_constants.asm', encoding='utf-8').read(), re.M)):
    TM_NUM.setdefault('TM_' + _m, _i + 1)      # Gen I TM numbers (Crystal TM with the same number)


class Flags:
    def __init__(s, start): s.i = start
    def new(s):
        f = P15.EXT_FLAGS[s.i]; s.i += 1; return f


def item_id(n):
    if n in TM_NUM: return P12.tm_item(TM_NUM[n])
    if n.startswith('TM_') and n not in P12.GEN1_TM and n not in P14.TM_NUM and n not in P15.TM_NUM:
        raise KeyError('TM number unknown: ' + n)
    return P15.item_id(n)


def follow_farcall_texts(g, tid):
    """texts of a text_asm that only farcalls a printing routine"""
    b, p = pkmap.text_ptr(g, tid); k, o = pkmap.text_body(b, p)
    F = pkmap.F; out = []
    for i in range(o, o + 20):
        if F[i] in (0x3E, 0x06) and F[i + 2] == 0x21 and F[i + 5] in (0xCF, 0xCD):
            fb = F[i + 1]; fa = F[i + 3] | F[i + 4] << 8; q = pkmap.fo(fb, fa)
            for j in range(q, q + 400):
                if F[j] == 0x21:
                    pp = F[j + 1] | F[j + 2] << 8
                    if 0x4000 <= pp < 0x8000:
                        kk, bb = pkmap.text_body(fb, pp)
                        if kk == 'text' and bb not in out: out.append(bb)
            break
    return out


def end_battle_texts(g, span=0x900):
    """(win, lose) text pairs saved with SaveEndBattleTextPointers in the map's script"""
    h = pkmap.header(g); hb = h['bank']; s0 = pkmap.fo(hb, h['script']); F = pkmap.F; out = []
    for m in re.finditer(rb'\x21(..)\x11(..)\xcd', F[s0 - 0x100:s0 + span], re.S):
        p1 = m.group(1)[0] | m.group(1)[1] << 8; p2 = m.group(2)[0] | m.group(2)[1] << 8
        k1, t1 = pkmap.text_body(hb, p1); k2, t2 = pkmap.text_body(hb, p2)
        if k1 == 'text' and k2 == 'text': out.append((t1, t2))
    return out


TILESETS_BANK = 0x2D0E               # (phase 25 moves the table out of bank 0x13)


class Tilesets:
    """custom tilesets: table in bank 0x13 with fixed capacity (phase 15)"""
    def __init__(s, rom, sp):
        s.rom = rom; s.sp = sp
        assert rom[TILESETS_BANK - 1] == 0x3E                       # LoadTilesetHeader: ld a, BANK(Tilesets)
        s.tab = fo(rom[TILESETS_BANK], rom[R_TILESETS[0]] | rom[R_TILESETS[0] + 1] << 8)

    def count(s):
        n = 0
        while any(s.rom[s.tab + 15 * n:s.tab + 15 * n + 15]): n += 1
        return n

    def entry(s, i): return bytes(s.rom[s.tab + 15 * i:s.tab + 15 * i + 15])

    def coll_off(s, i):
        e = s.entry(i); return fo(e[6], e[7] | e[8] << 8)

    def add(s, ts, data_bank, log, anim_src=5):
        rom = s.rom; sp = s.sp
        i = s.count(); assert i < P15.TS_CAP
        gfx = lz(ts.gfx_raw)
        a_g = sp.put(data_bank, gfx); a_m = sp.put(data_bank, ts.blocks); a_c = sp.put(data_bank, bytes(ts.coll))
        lo, hi = P15.OLD_TS_HOLE
        hole = next((o for o in range(lo, hi - 0x70 + 1, 0x70) if not any(rom[o:o + 0x70])), None)
        if hole is not None:
            rom[hole:hole + 0x70] = ts.palmap; a_p = 0x4000 + hole % 0x4000
        else:
            a_p = sp.put(0x13, ts.palmap)
        anim = s.entry(anim_src)[9:11]
        rom[s.tab + 15 * i:s.tab + 15 * i + 15] = bytes([data_bank, a_g & 0xFF, a_g >> 8, data_bank, a_m & 0xFF, a_m >> 8,
                                                        data_bank, a_c & 0xFF, a_c >> 8]) + anim + b'\x00\x00' + bytes([a_p & 0xFF, a_p >> 8])
        # palettes hook in front of the previous ones
        def r16(o): return rom[o] | rom[o + 1] << 8
        prev = r16(LSMP + 1)
        hp = rom[HOUSEPAL_CALL:HOUSEPAL_CALL + 14]; wbg = hp[3:5]; fc = hp[12:14]
        ph = fo(0x12, prev); ld_ts = bytes(rom[ph:ph + 3])
        a_pal = sp.put(0x12, ts.pals)
        a = Asm(sp.here(0x12))
        a.raw(ld_ts); a.db(0xFE, i, 0x28, 0x03); a.db(0xC3); a.dw(prev)
        a.db(0x21); a.dw(a_pal); a.db(0x3E, 0x05, 0x11); a.raw(wbg); a.db(0x01, 0x40, 0x00, 0xCD); a.raw(fc); a.db(0x37, 0xC9)
        hk = sp.put(0x12, a.done()); rom[LSMP + 1] = hk & 0xFF; rom[LSMP + 2] = hk >> 8
        log.append('tileset %s id %d (gfx %d bytes, %d blocks)' % (ts.name, i, len(gfx), ts.nblocks))
        return i


def warp_collisions(maps, objs_of, log, coll_store):
    """set Crystal warp collision codes for every warp (coll_store: tileset -> bytearray)"""
    for n, mp in maps.items():
        objs, warps, skip = objs_of(n)
        ts = mp.ts; coll = coll_store[ts.name]
        for wi, (x, y, dest, wid) in enumerate(warps):
            if wi in skip: continue
            b_, q = mp.block_at(x, y); tile = ts.quad_tile(b_, q)
            below_ok = y + 1 < mp.h * 2 and ts.quad_tile(*mp.block_at(x, y + 1)) in ts.passable
            if tile in ts.warp_tiles and below_ok:      # arrival steps down off a staircase
                v = COLL_STAIRCASE
            elif y == mp.h * 2 - 1 or y == 0 or x == 0 or x == mp.w * 2 - 1:
                v = COLL_CARPET['down'] if y == mp.h * 2 - 1 else COLL_CARPET['up'] if y == 0 else \
                    COLL_CARPET['left'] if x == 0 else COLL_CARPET['right']
            else:
                v = None
                for d, (dx, dy) in (('down', (0, 1)), ('up', (0, -1)), ('left', (-1, 0)), ('right', (1, 0))):
                    nb_, nq = mp.block_at(x + dx, y + dy)
                    if ts.quad_tile(nb_, nq) not in ts.passable:
                        v = COLL_CARPET[d]; break
                assert v is not None, (n, x, y)
            old = coll[4 * b_ + q]
            if old in COLL_CARPET.values() and v in COLL_CARPET.values(): continue   # shared block: keep the first direction
            assert old in (COLL_FLOOR, COLL_WALL, v), (n, x, y, hex(old), hex(v))
            coll[4 * b_ + q] = v


def objects_of(mapname):
    objs, warps = P11.objects_of(mapname)
    src = open(PY + '/data/maps/objects/%s.asm' % mapname, encoding='utf-8').read()
    skip = set()
    for i, l in enumerate([l for l in src.split('\n') if re.match(r'\s*warp_event\s', l)]):
        if 'inaccessible' in l or 'UNUSED_MAP' in l: skip.add(i)
    bgs = [(int(x), int(y), t) for x, y, t in re.findall(r'bg_event\s+(\d+),\s*(\d+),\s*(\w+)', src)]
    return objs, warps, skip, bgs


def hidden_events(mapconst):
    src = open(PY + '/data/events/hidden_events.asm', encoding='utf-8').read()
    m = re.search(r'hidden_events_for %s\n(.*?)db -1' % mapconst, src, re.S)
    if not m: return []
    return [(int(x), int(y), fn, arg.strip()) for x, y, fn, arg in re.findall(r'hidden_event\s+(\d+),\s*(\d+),\s*(\w+),\s*([\w+]+)', m.group(1))]


def map_const(name):
    return re.sub(r'(?<!^)(?=[A-Z0-9][a-z])|(?<=[a-z])(?=[0-9])|(?<=[a-z])(?=[A-Z])', '_', name).upper().replace('S_S_', 'SS_')


def red_party(cls, k):
    return P11.red_parties(RED_DATA[cls])[k - 1]
