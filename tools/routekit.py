"""Helpers for porting Red's routes (phase 33 on): blocks with both tileset versions, connections recomputed from
their own fields, Crystal neighbours' offsets matched to Red's roads, Red's objects / trainers / items / signs."""
import re
from lib import *
from portlib import *
from jpchar import encode
import portmaps as PM
import pairwalls
import blockxlat as X
import redmap as RM
import build_phase10 as P10
import build_phase12 as P12
import build_phase13 as P13
import build_phase15 as P15
import build_phase22 as P22
import build_phase24 as P24
import build_phase25 as P25
import build_phase27 as P27
import collmap

P15.TS_CAP = P27.TS_CAP
OVERWORLD_TS = 40
GEN1_OUTDOOR_TS = {40}
DIRS = [('north', 8), ('south', 4), ('west', 2), ('east', 1)]
PAD = 3


def r16(rom, o): return rom[o] | rom[o + 1] << 8


def conn_list(rom, hdr):
    """[(direction, offset of the 12-byte entry)] in the map's attributes"""
    a = attrs(rom, hdr); o2 = a['attr_off']; out = []; k = 0
    for d, bit in DIRS:
        if a['conn'] & bit: out.append((d, o2 + 12 + 12 * k)); k += 1
    return out


def strip_offset(rom, d, c, tgt_w, tgt_h):
    """offset (in the target's blocks) of the strip a connection entry shows, from the entry's own fields"""
    if d in ('north', 'south'):
        x = rom[c + 9]; x = x - 256 if x > 127 else x; off = -x // 2
    else:
        y = rom[c + 8]; y = y - 256 if y > 127 else y; off = -y // 2
    src = max(0, -(off + PAD))
    return {'north': tgt_w * (tgt_h - PAD) + src, 'south': src, 'west': tgt_w * src + tgt_w - PAD, 'east': tgt_w * src}[d]


def connection(d, cur_w, cur_h, tgt, tgt_w, tgt_h, off, tgt_blocks):
    if d in ('north', 'south'): return P24.connection(d, cur_w, cur_h, tgt, tgt_w, tgt_h, off, tgt_blocks)
    return P22.connection(d, cur_w, cur_h, tgt, tgt_w, tgt_h, off, tgt_blocks + P22.strip_src(d, tgt_w, off))


class Kit:
    def __init__(s, rom, sp, bank, FL, log, max26):
        s.rom = rom; s.sp = sp; s.bank = bank; s.FL = FL; s.log = log; s.max26 = max26; s.dims = {}
        s.TS = PM.Tilesets(rom, sp)
        s.ow = Tileset('Overworld', 0, 'overworld.bst', SC + '/out/pk_overworld.pkl', water=0x14, grass=0x52)
        s.party_of = {}
        u = US.get(); s.G = u.groups()
        s.names = {}
        for k in u.S:
            if k.endswith('_MapAttributes'):
                try: s.names[mapid(k[:-14])] = k[:-14]
                except Exception: pass

    def w16(s, o, v): s.rom[o] = v & 0xFF; s.rom[o + 1] = v >> 8

    # ---------------------------------------------------------------- tileset
    def overworld_variants(s, maps, overrides):
        """variant blocks of the Gen I overworld tileset for the doors / edges of maps {name: MapPort}"""
        rom = s.rom; e = s.TS.entry(OVERWORLD_TS); am_, ac_ = e[4] | e[5] << 8, e[7] | e[8] << 8
        assert e[3] == e[6]; nb0 = (ac_ - am_) // 16
        meta = bytes(rom[fo(e[3], am_):fo(e[3], am_) + 16 * nb0]); coll = bytes(rom[fo(e[6], ac_):fo(e[6], ac_) + 4 * nb0])
        s.ow.coll = bytearray(coll[:4 * s.ow.nblocks])
        meta2, coll2, blks = pairwalls.variants(s.ow, meta, coll, maps, [], overrides)
        meta2, coll2, blks = P27.block0_copy(meta2, coll2, blks)
        assert len(coll2) // 4 <= 256
        am = s.sp.put(s.bank, meta2 + coll2); t0 = s.TS.tab + 15 * OVERWORLD_TS
        rom[t0 + 3] = s.bank; s.w16(t0 + 4, am); rom[t0 + 6] = s.bank; s.w16(t0 + 7, am + len(meta2))
        for n in maps: maps[n].blk = blks[n]
        s.ow_meta, s.ow_coll = meta2, coll2
        s.log.append('tileset Overworld: %d blocks (+%d)' % (len(coll2) // 4, len(coll2) // 4 - nb0))
        s.g1side = gen1_side_all(s.ow, meta2, coll2); s.crside = crystal_side_all(rom, s.TS)

    # ---------------------------------------------------------------- trainers
    def add_parties(s, names):
        groups = P13.read_groups7e(s.rom); ti = len(s.party_of)
        def pb(mons): return b'\x00' + b''.join(bytes([lv, PM.MON[P10.MON_ALIAS.get(x, x)]]) for lv, x in mons) + b'\xff'
        for nm in names:
            for i, o in enumerate(P25.red_objects(nm)[0]):
                if o['extra'] and o['extra'][0].startswith('OPP_'):
                    c = o['extra'][0][4:]; k = int(o['extra'][1]); cid = PM.TCLS[c]
                    groups[cid - 1].append([encode(PM.NAMEPOOL[(ti + 7) % len(PM.NAMEPOOL)] + '@'), pb(PM.red_party(c, k))])
                    s.party_of[(nm, i)] = (cid, len(groups[cid - 1])); ti += 1
        s.log.append('trainer parties added (bank 7E free %d)' % P13.write_groups7e(s.rom, groups))

    # ---------------------------------------------------------------- texts
    @staticmethod
    def hl(g, tid, **kw):
        return [RM.crystal_text(b, p) for b, p in RM.asm_hl(g, tid, **kw) if RM.R[RM.fo(b, p)] in (0x00, 0x17)]

    @staticmethod
    def rt(g, tid):
        b, p = RM.text_ptr(g, tid); k, v = RM.text_body(b, p)
        if k == 'text': return RM.crystal_text(b, p)
        return Kit.hl(g, tid)[0]

    @staticmethod
    def put_texts(a, texts):
        for k_, v in texts.items():
            assert k_ not in a.labels, k_
            a.label(k_); a.raw(v if v[-1] in (0x50, 0x57, 0x58) else P12.text(v))

    # ---------------------------------------------------------------- Red's objects / signs / hidden items
    def red_events(s, a, texts, nm, g, pre, special=None, spr=None):
        """objects of Red's map nm (Red map id g): trainers, items, plain people; special {tid: fn(a, texts, lab, o)
        -> (sprite or None, typ, flag, sight) or None to skip}; returns obj_bytes, bgs"""
        special = special or {}; spr = spr or P25.SPR
        objs, warps, bgl = P25.red_objects(nm)
        obj_bytes = []; bgs = []
        for idx, o in enumerate(objs):
            tid = idx + 1; lab = '%so%d' % (pre, tid); fl = 0xFFFF; typ = 0; sight = 0; sp_ = spr[o['sprite']] if o['sprite'] in spr else None
            mv, rng = P25.face((0, 0, 0, o['move'], o['face']))
            if tid in special:
                r = special[tid](a, texts, lab, o)
                if r is None: continue
                sp2, typ, fl, sight = r; sp_ = sp2 or sp_
            elif o['sprite'] == 'SPRITE_POKE_BALL':
                typ = 1; fl = s.FL.new(); a.label(lab); a.db(PM.item_id(o['extra'][0]), 1)
            elif o['extra'] and o['extra'][0].startswith('OPP_'):
                sight, seen, aft, win = P27.red_trainer_texts(g, tid)
                fl = s.FL.new(); cid, pid = s.party_of[(nm, idx)]; typ = 2
                a.label(lab); a.dw(fl); a.db(cid, pid); a.dw(lab + 's'); a.dw(lab + 'w'); a.dw(0); a.dw(lab + 'x')
                a.label(lab + 'x'); a.endifjustbattled(); a.opentext(); a.writetext(lab + 'a'); a.waitbutton(); a.closetext(); a.end()
                texts[lab + 's'] = seen; texts[lab + 'w'] = win; texts[lab + 'a'] = aft
            else:
                a.label(lab); a.jumptextfaceplayer(lab + 't'); texts[lab + 't'] = s.rt(g, tid)
            obj_bytes.append([sp_, o['y'] + 4, o['x'] + 4, mv, rng, 0xFF, 0xFF, typ, sight, lab, fl])
        for k, (x, y, tconst) in enumerate(bgl):
            L_ = '%sbg%d' % (pre, k); a.label(L_); a.jumptext(L_ + 't'); texts[L_ + 't'] = s.rt(g, len(objs) + k + 1)
            bgs.append((y, x, 0, L_))
        for k, (x, y, fn, arg) in enumerate(P25.hidden(PM.map_const(nm))):
            assert fn == 'HiddenItems', (nm, fn)
            L_ = '%shi%d' % (pre, k); a.label(L_); a.dw(s.FL.new()); a.db(PM.item_id(arg)); bgs.append((y, x, 7, L_))
        return obj_bytes, bgs

    @staticmethod
    def emit(a, label, warps, coords, bgs, objs, callbacks, scenes=()):
        a.label(label + 'ms'); a.db(len(scenes))
        for sc in scenes: a.dw(sc); a.dw(0)
        a.db(len(callbacks))
        for t_, l_ in callbacks: a.db(t_); a.dw(l_)
        a.label(label + 'ev'); a.db(0, 0)
        a.db(len(warps))
        for w_ in warps: a.raw(bytes(w_))
        a.db(len(coords))
        for (sc, y, x, l_) in coords: a.db(sc, y, x, 0); a.dw(l_); a.db(0, 0)
        a.db(len(bgs))
        for (y_, x_, t_, l_) in bgs: a.db(y_, x_, t_); a.dw(l_)
        a.db(len(objs))
        for ob in objs: a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])

    # ---------------------------------------------------------------- passability (for matching Crystal neighbours)
    def walk_grid(s, name):
        """tile passability of a map as it is in the ROM now"""
        G = collmap.grid(s.rom, name)
        return [[c in (0x00, 0x18, 0x14) or 0xA0 <= c <= 0xA7 for c in r] for r in G]

    def red_walk(s, mp):
        nb = len(s.ow_coll) // 4; out = []
        for y in range(2 * mp.h):
            row = []
            for x in range(2 * mp.w):
                b = mp.blk[(y // 2) * mp.w + x // 2]; q = (y % 2) * 2 + x % 2
                row.append(s.ow_coll[4 * b + q] in (0x00, 0x18, 0x14) or 0xA0 <= s.ow_coll[4 * b + q] <= 0xA7)
            out.append(row)
        return out

    @staticmethod
    def best_offset(d, rg, ng, off0, span=4):
        """the offset (blocks) near Red's whose edge best joins the road of route grid rg to neighbour grid ng"""
        best = None
        for off in range(off0 - span, off0 + span + 1):
            sc = 0
            if d in ('north', 'south'):
                rr = rg[0] if d == 'north' else rg[-1]; nr = ng[-1] if d == 'north' else ng[0]
                for x, p in enumerate(rr):
                    xn = x - 2 * off
                    q = 0 <= xn < len(nr) and nr[xn]
                    sc += 2 if (p and q) else (-1 if p != q and 0 <= xn < len(nr) else 0)
            else:
                rc = [r[0] for r in rg] if d == 'west' else [r[-1] for r in rg]
                nc = [r[-1] for r in ng] if d == 'west' else [r[0] for r in ng]
                for y, p in enumerate(rc):
                    yn = y - 2 * off
                    q = 0 <= yn < len(nc) and nc[yn]
                    sc += 2 if (p and q) else (-1 if p != q and 0 <= yn < len(nc) else 0)
            key = (sc, -abs(off - off0))
            if best is None or key > best[0]: best = (key, off)
        return best[1]

    # ---------------------------------------------------------------- blocks of a map, both versions, all pointers
    def place_blocks(s, name, blk, red):
        """blocks of map name in s.bank (native + the other tileset's translation); its attributes point to them and
        every connection that shows it is re-pointed (Gen I owners -> Gen I version)"""
        rom = s.rom; h = hdr_index(name); a = attrs(rom, h)
        assert len(blk) == a['w'] * a['h'], (name, len(blk), a['w'], a['h'])
        if red: g1, cr = blk, X.translate(blk, s.g1side, s.crside)
        else: cr, g1 = blk, X.translate(blk, s.crside, s.g1side)
        pn = s.sp.put(s.bank, g1 if red else cr); px = s.sp.put(s.bank, cr if red else g1)
        p_g1, p_cr = (pn, px) if red else (px, pn)
        ao = a['attr_off']; rom[ao + 3] = s.bank; s.w16(ao + 4, pn)
        tgt = mapid(name); n_ = 0
        for hdr in s.all_headers():
            g1owner = rom[hdr + 1] in GEN1_OUTDOOR_TS
            for d, c in conn_list(rom, hdr):
                if (rom[c], rom[c + 1]) == tgt:
                    s.w16(c + 2, (p_g1 if g1owner else p_cr) + strip_offset(rom, d, c, a['w'], a['h'])); n_ += 1
        return n_

    def all_headers(s):
        rom = s.rom; G = s.G; out = []
        for gi in range(len(G)):
            n_ = (G[gi + 1] - G[gi]) // 9 if gi + 1 < len(G) else s.max26
            for k in range(n_):
                hdr = G[gi] + 9 * k
                if rom[hdr] and attrs(rom, hdr)['scbank']: out.append(hdr)
        return out

    def dim(s, name):
        if name in s.dims: return s.dims[name]
        a = attrs(s.rom, hdr_index(name)); return a['w'], a['h']

    def set_conn(s, name, d, tgt_name, off):
        """(re)write map name's connection d to tgt_name with offset off (the entry must exist for that direction;
        its pointer is fixed by place_blocks of tgt)"""
        rom = s.rom; h = hdr_index(name); w, hh = s.dim(name); tw, th = s.dim(tgt_name)
        for dd, c in conn_list(rom, h):
            if dd == d:
                rom[c:c + 12] = connection(d, w, hh, mapid(tgt_name), tw, th, off, 0); return
        raise KeyError((name, d))

    def new_attrs(s, name, w, h, border, mscripts, events, conns):
        """new attributes for map name: conns [(direction, target name, offset)] (pointers fixed by place_blocks)"""
        rom = s.rom; hdr = hdr_index(name); bits = 0; body = b''
        order = {d: i for i, (d, b) in enumerate(DIRS)}
        for d, tn, off in sorted(conns, key=lambda c: order[c[0]]):
            bits |= dict(DIRS)[d]; tw, th = s.dim(tn)
            body += connection(d, w, h, mapid(tn), tw, th, off, 0)
        at = s.sp.put(s.bank, bytes([border, h, w, s.bank, 0, 0, s.bank, mscripts & 0xFF, mscripts >> 8,
                                     events & 0xFF, events >> 8, bits]) + body)
        rom[hdr] = s.bank; s.w16(hdr + 3, at)

    # ---------------------------------------------------------------- wild Pokémon (Red, grass)
    def red_wild(s, mp, red_name):
        rom = s.rom; kg = P27.kanto_grass(rom); p = kg
        while (rom[p], rom[p + 1]) != mp:
            assert rom[p] != 0xFF, red_name; p += 47
        t = open(PR + '/data/wild/maps/%s.asm' % red_name, encoding='utf-8').read()
        t = re.sub(r'IF DEF\(_BLUE\).*?ENDC', '', t, flags=re.S)
        rate = int(re.search(r'def_grass_wildmons (\d+)', t).group(1))
        if rate == 0: return
        slots = [(int(l_), x) for l_, x in re.findall(r'db\s+(\d+), (\w+)', t.split('end_grass_wildmons')[0])]
        pick = [slots[i] for i in (0, 1, 2, 3, 6, 8, 9)]
        rom[p:p + 47] = bytes([*mp, rate, rate, rate]) + bytes(sum(([lv, PM.MON[P10.MON_ALIAS.get(x, x)]] for lv, x in pick), [])) * 3


def gen1_side_all(ts, meta, coll):
    """blockxlat's Gen I side with every block of the tileset (variants too)"""
    tiles = X.tiles2bpp(ts.gfx_raw); tile_pal = []
    for i in range(0x30): tile_pal += [ts.palmap[i] & 7, (ts.palmap[i] >> 4) & 7]
    pals = []
    for p in range(8):
        cols = []
        for k in range(4):
            v = ts.pals[8 * p + 2 * k] | ts.pals[8 * p + 2 * k + 1] << 8
            cols.append((v & 31, (v >> 5) & 31, (v >> 10) & 31))
        pals.append(cols)
    return X.Side(bytes(meta), bytes(coll), tiles, tile_pal, pals)


def crystal_side_all(rom, TS):
    """blockxlat's Crystal side with every block of the Kanto tileset (later phases' extra blocks too)"""
    side = X.crystal_side(rom, TS)
    e = TS.entry(X.KANTO_TS); am, ac = e[4] | e[5] << 8, e[7] | e[8] << 8
    if e[3] == e[6] and ac > am:
        n = (ac - am) // 16
        if n > side.n:
            mo, co = fo(e[3], am), fo(e[6], ac)
            side.meta = bytes(rom[mo:mo + 16 * n]); side.coll = bytes(rom[co:co + 4 * n])
            tiles = X.tiles2bpp(open(PC + '/gfx/tilesets/kanto.2bpp', 'rb').read())
            names = []
            for l in open(PC + '/gfx/tilesets/kanto_palette_map.asm'):
                m = re.match(r'\s*tilepal 0,(.*)', l)
                if m: names += [x.strip() for x in m.group(1).split(',')]
            tile_pal = [X.CPAL.index(nm) for nm in names[:len(tiles)]]
            txt = open(PC + '/gfx/tilesets/bg_tiles.pal').read(); day = txt.split('; day')[1].split('; nite')[0]
            pals = []
            for m in re.finditer(r'RGB ([\d, ]+);', day):
                v = [int(x) for x in m.group(1).replace(' ', '').split(',')]
                pals.append([(v[3 * k], v[3 * k + 1], v[3 * k + 2]) for k in range(4)])
            side = X.Side(side.meta, side.coll, tiles, tile_pal, pals)
    return side


def red_dims(name):
    cs = open(PY + '/constants/map_constants.asm').read()
    c = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', name).upper()
    c = re.sub(r'(?<=[A-Z])(?=[0-9])', '_', c)
    m = re.search(r'map_const %s,\s*(\d+),\s*(\d+)' % c, cs)
    return int(m.group(1)), int(m.group(2))


def red_conns(name):
    t = open(PR + '/data/maps/headers/%s.asm' % name).read()
    return [(d, n, int(o)) for d, n, c, o in re.findall(r'connection (\w+), (\w+), (\w+), (-?\d+)', t)]
