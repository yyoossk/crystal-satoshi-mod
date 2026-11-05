#!/usr/bin/env python3
"""Phase 11: Pokémon Tower 1F-7F ported from the Pikachu full-color hack (tileset graphics, colors,
blocks) with Pikachu-version events: channelers (Red parties), items, Shigeru on 2F (Red), Jessie & James
and Mr. Fuji on 7F (Pikachu). Entrance: Lavender's tower door.
usage: build_phase11.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode, decode
import pkmap

ITEM = load_consts(PC + '/constants/item_constants.asm')
MON = load_consts(PC + '/constants/pokemon_constants.asm')
FREE_EV = json.load(open(SC + '/out/free_events.json'))
EVI = [0]
def newflag():
    f = FREE_EV[EVI[0]]; EVI[0] += 1; return f

MEDIUM, BLUE, JJ = 57, 64, 72
SILPH_SCOPE, LIFT_KEY = 0x87, 0x88
EV_OAK_GOT = {'fire': 0x343, 'water': 0x344, 'grass': 0x345}
SPR = {'SPRITE_CHANNELER': 0x30, 'SPRITE_LINK_RECEPTIONIST': 0x38, 'SPRITE_MIDDLE_AGED_WOMAN': 0x2E,
       'SPRITE_BALDING_GUY': 0x2D, 'SPRITE_GIRL': 0x28, 'SPRITE_BLUE': 0x07, 'SPRITE_POKE_BALL': 0x54,
       'SPRITE_JESSIE': 0x36, 'SPRITE_JAMES': 0x35, 'SPRITE_MR_FUJI': 0x2F}
FACE = {'DOWN': 6, 'UP': 7, 'LEFT': 8, 'RIGHT': 9, 'NONE': 6, 'ANY_DIR': 2}

TOWER = [  # name, gen1 map id, blk
    ('PokemonTower1F', 0x8E), ('PokemonTower2F', 0x8F), ('PokemonTower3F', 0x90), ('PokemonTower4F', 0x91),
    ('PokemonTower5F', 0x92), ('PokemonTower6F', 0x93), ('PokemonTower7F', 0x94)]

YELLOW_CHANNELER = None


def yellow_parties(cls_label):
    txt = open(PY + '/data/trainers/parties.asm', encoding='utf-8').read()
    m = re.search(r'(?m)^' + cls_label + r':\n(.*?)\n\n', txt, re.S)
    out = []
    for l in m.group(1).split('\n'):
        s = l.split(';')[0].strip()
        mm = re.match(r'db\s+(.*)', s)
        if mm:
            v = [x.strip() for x in mm.group(1).split(',')]
            if v[0] in ('$FF', '$ff'):
                v = v[1:-1]; out.append([(int(v[i]), v[i + 1]) for i in range(0, len(v), 2)])
            else:
                out.append([(int(v[0]), x) for x in v[1:-1]])
    return out


def red_parties(cls_label):
    txt = open(PR + '/data/trainers/parties.asm', encoding='utf-8').read()
    m = re.search(r'(?m)^' + cls_label + r':\n(.*?)\n\n', txt, re.S)
    out = []
    for l in m.group(1).split('\n'):
        s = l.split(';')[0].strip()
        mm = re.match(r'db\s+(.*)', s)
        if mm:
            v = [x.strip() for x in mm.group(1).split(',')]
            if v[0] in ('$FF', '$ff'):
                v = v[1:-1]; out.append([(int(v[i]), v[i + 1]) for i in range(0, len(v), 2)])
            else:
                out.append([(int(v[0]), x) for x in v[1:-1]])
    return out


def objects_of(mapname):
    out = []
    for l in open(PY + '/data/maps/objects/%s.asm' % mapname, encoding='utf-8'):
        s = l.split(';')[0].strip()
        m = re.match(r'object_event\s+(.*)', s)
        if m:
            v = [x.strip() for x in m.group(1).split(',')]
            out.append(dict(x=int(v[0]), y=int(v[1]), sprite=v[2], move=v[3], face=v[4], text=v[5], extra=v[6:]))
    w = []
    for l in open(PY + '/data/maps/objects/%s.asm' % mapname, encoding='utf-8'):
        m = re.match(r'\s*warp_event\s+(\d+),\s*(\d+),\s*(\w+),\s*(\d+)', l)
        if m:
            w.append((int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4))))
    return out, w


def main():
    src, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    log = []

    # ---------------- free areas
    f13, n13 = bank_free_tail(rom, 0x13); sp.set_area(0x13, f13 + 1, 0x13 * 0x4000 + 0x4000)
    f12, n12 = bank_free_tail(rom, 0x12); sp.set_area(0x12, f12 + 1, 0x12 * 0x4000 + 0x4000)
    f7c, _ = bank_free_tail(rom, 0x7C); sp.set_area(0x7C, f7c + 1, 0x7C * 0x4000 + 0x4000)
    f7b, _ = bank_free_tail(rom, 0x7B); sp.set_area(0x7B, f7b + 1, 0x7B * 0x4000 + 0x4000)
    f25, _ = bank_free_tail(rom, 0x25)

    # ---------------- tileset
    ts = Tileset('Cemetery', 15, 'cemetery.bst', SC + '/out/pk_cemetery.pkl')
    maps = [MapPort(n, ts, pkmap.header(g)['w'], pkmap.header(g)['h'], n + '.blk') for n, g in TOWER]
    # warp collisions
    for mp, (n, g) in zip(maps, TOWER):
        objs, warps = objects_of(n)
        for (x, y, dest, wid) in warps:
            b, q = mp.block_at(x, y)
            tile = ts.quad_tile(b, q)
            if tile in ts.warp_tiles:
                v = COLL_STAIRCASE
            else:
                v = COLL_CARPET['down'] if y == mp.h * 2 - 1 else COLL_CARPET['up'] if y == 0 else \
                    COLL_CARPET['left'] if x == 0 else COLL_CARPET['right']
            old = ts.coll[4 * b + q]
            assert old in (COLL_FLOOR, COLL_WALL, v), (n, x, y, hex(old), hex(v))
            ts.coll[4 * b + q] = v
    gfx = lz(ts.gfx_raw)
    a_gfx = sp.put(0x7C, gfx); a_meta = sp.put(0x7C, ts.blocks); a_coll = sp.put(0x7C, bytes(ts.coll))
    a_pal = sp.put(0x13, ts.palmap)
    old_tab = bytes(rom[T_TILESETS:T_TILESETS + 15 * N_TILESETS])
    anim_none = old_tab[15 * 5 + 9:15 * 5 + 11]            # a tileset with no animation
    entry = bytes([0x7C, a_gfx & 0xFF, a_gfx >> 8, 0x7C, a_meta & 0xFF, a_meta >> 8, 0x7C, a_coll & 0xFF, a_coll >> 8]) + \
        anim_none + b'\x00\x00' + bytes([a_pal & 0xFF, a_pal >> 8])
    TS_ID = N_TILESETS
    new_tab = old_tab + entry
    a_tab = sp.put(0x13, new_tab)
    for off in R_TILESETS:
        assert r16(off) == 0x4000 + T_TILESETS % 0x4000; w16(off, a_tab)
    log.append('tileset Cemetery id %d (gfx %d bytes, %d blocks)' % (TS_ID, len(gfx), ts.nblocks))

    # ---------------- palettes hook (bank 0x12)
    hp = rom[HOUSEPAL_CALL:HOUSEPAL_CALL + 14]
    assert hp[0] == 0x3E and hp[2] == 0x11 and hp[5] == 0x21 and hp[11] == 0xCD
    wbgpals = hp[3:5]; farcopy = hp[12:14]
    orig3 = bytes(rom[LSMP:LSMP + 3]); assert orig3[0] == 0xFA
    a_pals = sp.put(0x12, ts.pals)
    a = Asm(sp.here(0x12))
    a.raw(orig3)                                   # ld a, [wMapTileset]
    a.db(0xFE, TS_ID, 0x28, 0x03)                  # cp TS ; jr z, +3
    a.db(0xC3); a.dw(0x4000 + (LSMP + 3) % 0x4000)  # jp original+3
    a.db(0x3E, 0x05, 0x11); a.raw(wbgpals); a.db(0x21); a.dw(a_pals); a.db(0x01, 0x40, 0x00, 0xCD); a.raw(farcopy)
    a.db(0x37, 0xC9)                               # scf ; ret
    hook = sp.put(0x12, a.done())
    rom[LSMP] = 0xC3; w16(LSMP + 1, hook)

    # ---------------- map ids in group 26 (bank 0x25): relocate following attribute blocks
    u = US.get(); G = u.groups()
    need = 9 * len(maps)
    lo, hi = GROUP26_END, GROUP26_END + need
    moved = 0
    for g in range(26):
        n = (G[g + 1] - G[g]) // 9 if g + 1 < 26 else G26_COUNT
        for k in range(n):
            hdr = G[g] + 9 * k
            ab = rom[hdr]; ap = r16(hdr + 3); ao = fo(ab, ap)
            nconn = bin(rom[ao + 11] & 0xF).count('1'); size = 12 + 12 * nconn
            if ao < hi and ao + size > lo:
                na = sp.put(0x7C, bytes(rom[ao:ao + size]))
                rom[hdr] = 0x7C; w16(hdr + 3, na); moved += 1
    rom[lo:hi] = bytes(need)
    log.append('moved %d attribute blocks out of bank 0x25' % moved)
    mapids = {mp.name: (G26, G26_COUNT + 1 + i) for i, mp in enumerate(maps)}

    # ---------------- crystal map ids we connect to
    lav = mapid('LavenderTown'); fuji = mapid('MrFujisHouse')
    lav_a = attrs(rom, hdr_index('LavenderTown')); lav_ev = parse_events(rom, lav_a['scbank'], lav_a['events'])
    door = None
    for i, (off, wv) in enumerate(lav_ev['warps']):
        if (wv[1], wv[0]) == (14, 5):
            door = (i + 1, off)
    assert door
    rom[door[1] + 2] = 1; rom[door[1] + 3] = mapids['PokemonTower1F'][0]; rom[door[1] + 4] = mapids['PokemonTower1F'][1]

    # ---------------- trainer parties (bank 0x0E): append and re-lay
    import build_phase10 as P10
    P10.OLD_N = 72
    attr_cur0 = fo(0x0E, r16(0x395A5))
    start, Gp, old_end = P10.parse_groups(bytes(rom), attr_cur0)
    assert len(Gp[71]) == 4, len(Gp[71])
    chan = yellow_parties('ChannelerData'); riv = red_parties('Rival2Data')
    def pb(mons): return b'\x00' + b''.join(bytes([lv, MON[s]]) for lv, s in mons) + b'\xff'
    def add_party(cls, name, mons):
        Gp[cls - 1].append([encode(name + '@'), pb(mons)]); return len(Gp[cls - 1])
    names = ['ミツコ', 'ハナコ', 'ヨシコ', 'カズコ', 'トミコ', 'ウメコ', 'マツコ', 'タケコ', 'キクエ', 'フサエ',
             'ハルエ', 'ナツエ', 'アキエ', 'フユエ', 'サダコ', 'テルコ']
    trainer_party = {}
    ni = 0
    for n, g in TOWER:
        objs, _ = objects_of(n)
        for o in objs:
            if o['extra'] and o['extra'][0] == 'OPP_CHANNELER':
                k = int(o['extra'][1])
                trainer_party[(n, o['text'])] = (MEDIUM, add_party(MEDIUM, names[ni % len(names)], chan[k - 1])); ni += 1
    riv_ids = {key: add_party(BLUE, 'シゲル', riv[3 + i]) for i, key in enumerate(['fire', 'water', 'grass'])}
    # re-lay parties + attributes
    T_G = P10.T_GROUPS; NN = 72
    attr_ref = 0x395A4; attr_cur = fo(0x0E, r16(attr_ref + 1))
    attr = bytes(rom[attr_cur:attr_cur + NN * 7])
    tbl_end = T_G + NN * 2
    out = bytearray(); ptrs = []
    for gi in range(NN):
        ptrs.append(tbl_end + len(out))
        for nm, d in Gp[gi]:
            out += nm + d
    attr_off = tbl_end + len(out)
    assert attr_off + len(attr) <= 0x3C000, hex(attr_off + len(attr))
    clear_to = max(old_end, attr_cur + len(attr))
    rom[T_G:clear_to] = bytes(clear_to - T_G)
    for gi, p in enumerate(ptrs):
        w16(T_G + 2 * gi, 0x4000 + p % 0x4000)
    rom[tbl_end:tbl_end + len(out)] = out; rom[attr_off:attr_off + len(attr)] = attr
    old_a = 0x4000 + attr_cur % 0x4000; new_a = 0x4000 + attr_off % 0x4000
    for off, d in P10.R_ATTR:
        assert r16(off + 1) == old_a + d; w16(off + 1, new_a + d)
    log.append('trainer data end %X (bank end 3C000)' % (attr_off + len(attr)))

    # ---------------- per-map scripts/events (bank 0x7B), blocks (bank 0x7C)
    def text(body): return bytes(body) + b'\x57'
    for mp, (n, g) in zip(maps, TOWER):
        objs, warps = objects_of(n)
        hdr = pkmap.header(g)
        a = Asm(sp.here(0x7B))
        a.db(0x00, 0x00)                                     # no scenes, no callbacks
        scr_ptrs = {}; texts = {}
        obj_bytes = []
        for idx, o in enumerate(objs):
            tid = idx + 1
            sprite = SPR[o['sprite']]; mv = FACE.get(o['face'], 6) if o['move'] == 'STAY' else 2
            flag = 0xFFFF; typ = 0; sight = 0
            lab = 'o%d' % tid
            if o['sprite'] == 'SPRITE_POKE_BALL':
                flag = newflag(); typ = 1
                a.label(lab); a.db(ITEM[o['extra'][0]], 1)
            elif o['extra'] and o['extra'][0] == 'OPP_CHANNELER':
                b, p = pkmap.text_ptr(g, tid); k, so = pkmap.text_body(b, p)
                hptr = pkmap.F[so + 2] | pkmap.F[so + 3] << 8
                h = pkmap.fo(b, hptr); hb = pkmap.F[h:h + 12]
                sight = hb[1] >> 4; typ = 2
                k1, seen = pkmap.text_body(b, hb[4] | hb[5] << 8)
                k2, aft = pkmap.text_body(b, hb[6] | hb[7] << 8)
                k3, win = pkmap.text_body(b, hb[8] | hb[9] << 8)
                cls, tidn = trainer_party[(n, o['text'])]
                fl = newflag()
                a.label(lab); a.dw(fl); a.db(cls, tidn); a.dw(lab + 's'); a.dw(lab + 'w'); a.dw(0); a.dw(lab + 'x')
                a.label(lab + 'x'); a.endifjustbattled(); a.opentext(); a.writetext(lab + 'a'); a.waitbutton(); a.closetext(); a.end()
                texts[lab + 's'] = seen; texts[lab + 'w'] = win; texts[lab + 'a'] = aft
            elif n == 'PokemonTower2F' and o['sprite'] == 'SPRITE_BLUE':
                flag = newflag()
                b, p = pkmap.text_ptr(g, tid); k, so = pkmap.text_body(b, p)
                ptrs_ = []
                for i in range(so, so + 80):
                    if pkmap.F[i] == 0x21:
                        pp = pkmap.F[i + 1] | pkmap.F[i + 2] << 8
                        kk, bb = pkmap.text_body(b, pp) if 0x4000 <= pp < 0x8000 else ('x', 0)
                        if kk == 'text': ptrs_.append(bb)
                after, intro, win = ptrs_[0], ptrs_[1], ptrs_[2]
                def riv(bb): return bytes(bb).replace(b'\x53', encode('シゲル'))
                a.label(lab)
                a.faceplayer(); a.opentext(); a.writetext(lab + 'i'); a.waitbutton(); a.closetext()
                a.winlosstext(lab + 'w', 0)
                a.checkevent(EV_OAK_GOT['fire']); a.iftrue(lab + 'f')
                a.checkevent(EV_OAK_GOT['water']); a.iftrue(lab + 'v')
                a.loadtrainer(BLUE, riv_ids['grass']); a.sjump(lab + 'g')
                a.label(lab + 'f'); a.loadtrainer(BLUE, riv_ids['fire']); a.sjump(lab + 'g')
                a.label(lab + 'v'); a.loadtrainer(BLUE, riv_ids['water'])
                a.label(lab + 'g'); a.startbattle(); a.reloadmapafterbattle()
                a.opentext(); a.writetext(lab + 'a'); a.waitbutton(); a.closetext()
                a.disappear(tid + 1); a.setevent(flag); a.end()
                texts[lab + 'i'] = riv(intro); texts[lab + 'w'] = riv(win); texts[lab + 'a'] = riv(after)
            elif n == 'PokemonTower7F' and o['sprite'] in ('SPRITE_JESSIE', 'SPRITE_JAMES'):
                flag = 0  # set below (shared)
                a.label(lab); a.sjump('jj')
            elif n == 'PokemonTower7F' and o['sprite'] == 'SPRITE_MR_FUJI':
                b, p = pkmap.text_ptr(g, tid); k, so = pkmap.text_body(b, p)
                pp = pkmap.F[so + 2] | pkmap.F[so + 3] << 8; kk, fuji_t = pkmap.text_body(b, pp)
                a.label(lab); a.faceplayer(); a.opentext(); a.writetext(lab + 't'); a.waitbutton(); a.closetext()
                a.warp(fuji[0], fuji[1], 2, 4); a.end()
                texts[lab + 't'] = fuji_t
            else:
                b, p = pkmap.text_ptr(g, tid); k, body = pkmap.text_body(b, p)
                assert k == 'text', (n, tid)
                a.label(lab); a.jumptextfaceplayer(lab + 't'); texts[lab + 't'] = body
            obj_bytes.append([sprite, o['y'] + 4, o['x'] + 4, mv, 0, 0xFF, 0xFF, typ, sight, lab, flag])
        if n == 'PokemonTower7F':
            jjflag = newflag()
            for ob in obj_bytes:
                if ob[10] == 0:
                    ob[10] = jjflag
            k4, t_wait = pkmap.text_body(*pkmap.text_ptr(g, 4))
            k5, t_main = pkmap.text_body(*pkmap.text_ptr(g, 5))
            k6, t_bye = pkmap.text_body(*pkmap.text_ptr(g, 6))
            o5 = pkmap.fo(*pkmap.text_ptr(g, 5))
            j = o5
            while pkmap.F[j] != 0x57: j += 1
            q = j + 1
            while pkmap.F[q] not in (0x57, 0x58): q += 1
            t_lose = pkmap.F[j + 1:q]
            jj_idx = [i + 1 for i, o in enumerate(objs) if o['sprite'] in ('SPRITE_JESSIE', 'SPRITE_JAMES')]
            a.label('jj')
            a.opentext(); a.writetext('jjw'); a.waitbutton(); a.writetext('jjm'); a.waitbutton(); a.closetext()
            a.winlosstext('jjl', 0); a.loadtrainer(JJ, 3); a.startbattle(); a.reloadmapafterbattle()
            a.opentext(); a.writetext('jjb'); a.waitbutton(); a.closetext()
            for oi in jj_idx:
                a.disappear(oi + 1)
            a.setevent(jjflag); a.end()
            texts['jjw'] = t_wait; texts['jjm'] = t_main; texts['jjl'] = t_lose; texts['jjb'] = t_bye
        coords = []
        if n == 'PokemonTower5F':
            # purified zone (Red): entering the 2x2 zone heals the party once; the ring around it re-arms it
            zf = FREE_EV[22]
            k7, t_zone = pkmap.text_body(*pkmap.text_ptr(g, 7))
            a.label('zone'); a.checkevent(zf); a.iftrue('zend'); a.setevent(zf)
            a.opentext(); a.writetext('zt'); a.waitbutton(); a.closetext(); a.special(27)
            a.label('zend'); a.end()
            a.label('zout'); a.clearevent(zf); a.end()
            texts['zt'] = t_zone
            for y in range(7, 11):
                for x in range(9, 13):
                    coords.append((y, x, 'zone' if (10 <= x <= 11 and 8 <= y <= 9) else 'zout'))
        if n == 'PokemonTower6F':
            # ghost Marowak at (10,16): needs the Silph Scope (Red)
            mf = FREE_EV[23]
            k6_, t_begone = pkmap.text_body(*pkmap.text_ptr(g, 6))
            o7 = pkmap.fo(*pkmap.text_ptr(g, 7))
            dep = []
            for i in range(o7, o7 + 40):
                if pkmap.F[i] == 0x21:
                    pp = pkmap.F[i + 1] | pkmap.F[i + 2] << 8
                    kk, bb = pkmap.text_body(o7 // 0x4000, pp)
                    if kk == 'text': dep.append(bb)
            a.label('mw'); a.checkevent(mf); a.iftrue('mwe')
            # Red: the ghost battle starts either way; without the Silph Scope it is the unidentifiable
            # ghost (phase 13 battle hooks), and the player is pushed back after running away
            a.opentext(); a.writetext('mwb'); a.waitbutton()
            a.checkitem(SILPH_SCOPE); a.iffalse('mwn')
            a.writetext('mws'); a.waitbutton()
            a.label('mwn'); a.closetext()
            a.loadwildmon(MON['MAROWAK'], 30); a.startbattle(); a.reloadmapafterbattle()
            a.readmem(0xD0AE); a.ifnotequal(0, 'mwp')
            a.setevent(mf)
            a.opentext(); a.writetext('mwd1'); a.waitbutton(); a.writetext('mwd2'); a.waitbutton(); a.closetext()
            a.label('mwe'); a.end()
            a.label('mwp'); a.applymovement(0, 'mwm'); a.end()
            a.label('mwm'); a.db(0x0F, 0x47)               # step RIGHT, step_end
            texts['mwb'] = t_begone
            texts['mws'] = encode('{00}シルフスコープで　ゆうれいの<LINE>しょうたいが　みえた！')
            texts['mwd1'] = dep[0]; texts['mwd2'] = dep[1]
            coords.append((16, 10, 'mw'))
        for k_, v in texts.items():
            a.label(k_); a.raw(text(v))
        a.label('events')
        a.db(0, 0)
        a.db(len(warps))
        for (x, y, dest, wid) in warps:
            if dest == 'LAST_MAP':
                a.db(y, x, door[0], lav[0], lav[1])
            else:
                dn = re.sub(r'(^|_)(\w)', lambda m: m.group(2).upper(), dest.lower()).replace('Pokemon', 'Pokemon')
                dn = 'PokemonTower' + dest.split('_')[-1]
                a.db(y, x, wid, mapids[dn][0], mapids[dn][1])
        a.db(len(coords))
        for (y, x, lab_) in coords:
            a.db(0xFF, y, x, 0); a.dw(lab_); a.db(0, 0)
        a.db(0)
        a.db(len(obj_bytes))
        for ob in obj_bytes:
            a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])
        code = a.done()
        base = sp.put(0x7B, code)
        assert base == a.base
        blk = sp.put(0x7C, mp.blk)
        attr = bytes([border_of(n), mp.h, mp.w, 0x7C, blk & 0xFF, blk >> 8, 0x7B, base & 0xFF, base >> 8,
                      a.labels['events'] & 0xFF, a.labels['events'] >> 8, 0])
        aa = sp.put(0x7C, attr)
        gnum = mapids[n][1]
        h = GROUP26_END + 9 * (gnum - G26_COUNT - 1)
        landmark = rom[hdr_index('LavenderTown') + 5]
        rom[h:h + 9] = bytes([0x7C, TS_ID, 7, aa & 0xFF, aa >> 8, landmark, 0x0E, 0x01, 0x00])
        log.append('%s -> map %d:%d  scripts 7B:%04X (%d bytes)' % (n, G26, gnum, base, len(code)))

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    log.append('flags used %d' % EVI[0])
    print('\n'.join(log))


if __name__ == '__main__':
    main()
