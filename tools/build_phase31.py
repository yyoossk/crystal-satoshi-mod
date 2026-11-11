#!/usr/bin/env python3
"""Phase 31: Route 22 as in Red / the Pikachu full-color hack:
 * Red's Route 22 (Gen I overworld tileset, ledges), its sign, Red's wild Pokémon; joined directly to Viridian City.
 * Shigeru waits on the road (Red's place) while a battle is due (after the Pokédex until the Boulder Badge; after
   the Earth Badge before the Hall of Fame) and comes over when the player reaches him (phase 17's battles and texts).
 * The gate building's door (Red's place) leads into Crystal's Victory Road Gate (which also joins Routes 26 / 28);
   its guard now asks for the Boulder Badge (Red's lines) instead of eight badges.
usage: build_phase31.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import portmaps as PM
import pairwalls
import redmap as RM
import redtexts as RT
from evedit import MapEvents
import build_phase10 as P10
import build_phase12 as P12
import build_phase15 as P15
import build_phase17 as P17
import build_phase22 as P22
import build_phase25 as P25
import build_phase27 as P27
import build_phase28 as P28
import build_phase29 as P29

P15.TS_CAP = P27.TS_CAP
BANK = 0x72                        # free in the JP original
OVERWORLD_TS = 40
RED_ROUTE22, RED_GATE = 0x21, 0xC1
EV_HOF = 0x34A
ENGINE_POKEDEX, ENGINE_BOULDER, ENGINE_EARTH = 0x0B, 0x23, 0x2A
R22_HIDE, R22_FIRST, R22_SECOND = (P15.EXT_FLAGS[i] for i in (61, 63, 64))    # phase 17
EV_FIRE, EV_WATER = 0x343, 0x344
BLUE = P17.BLUE
PARTY = {'r22a': {'grass': 13, 'fire': 11, 'water': 12}, 'r22b': {'grass': 19, 'fire': 17, 'water': 18}}  # phase 17
MUS_RIVAL, MUS_RIVAL_AFTER = P17.MUS_RIVAL, P17.MUS_RIVAL_AFTER
RIVAL_AT = (25, 5)
U, D, L, R_ = 0x0D, 0x0C, 0x0E, 0x0F
TU, TD, TL, TR = 1, 0, 2, 3
DOOR = (8, 5)
# the player reaches (29,4) or (29,5): Shigeru walks over to his left
RIVAL_IN = {4: [R_, R_, R_, U], 5: [R_, R_, R_]}
RIVAL_OUT = {4: [D, L, L, L, L, L], 5: [L, L, L, L, L]}


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    f, n = bank_free_tail(rom, BANK); sp.set_area(BANK, f + 1 if f > BANK * 0x4000 else f, BANK * 0x4000 + 0x4000)
    log = []
    r22, vir = mapid('Route22'), mapid('ViridianCity')
    TS = PM.Tilesets(rom, sp)

    def hl(mapid_, tid, **kw):
        return [RM.crystal_text(b, p) for b, p in RM.asm_hl(mapid_, tid, **kw) if RM.R[RM.fo(b, p)] in (0x00, 0x17)]
    def rt(mapid_, tid):
        b, p = RM.text_ptr(mapid_, tid); k, v = RM.text_body(b, p)
        if k == 'text': return RM.crystal_text(b, p)
        return hl(mapid_, tid)[0]
    def put_texts(a, texts):
        for k_, v in texts.items():
            assert k_ not in a.labels, k_
            a.label(k_); a.raw(v if v[-1] in (0x50, 0x57, 0x58) else P12.text(v))

    # ================= the overworld tileset: the gate door
    ow = Tileset('Overworld', 0, 'overworld.bst', SC + '/out/pk_overworld.pkl', water=0x14, grass=0x52)
    route = MapPort('Route22', ow, 20, 9, 'Route22.blk')
    e = TS.entry(OVERWORLD_TS); am_, ac_ = e[4] | e[5] << 8, e[7] | e[8] << 8
    assert e[3] == e[6]; nb0 = (ac_ - am_) // 16
    meta = bytes(rom[fo(e[3], am_):fo(e[3], am_) + 16 * nb0]); coll = bytes(rom[fo(e[6], ac_):fo(e[6], ac_) + 4 * nb0])
    ow.coll = bytearray(coll[:4 * ow.nblocks])
    meta2, coll2, blks = pairwalls.variants(ow, meta, coll, {'Route22': route}, [],
                                            {'Route22': {DOOR: P25.warp_override(ow, route, *DOOR)}})
    meta2, coll2, blks = P27.block0_copy(meta2, coll2, blks)
    assert len(coll2) // 4 <= 256
    am = sp.put(BANK, meta2 + coll2); t0 = TS.tab + 15 * OVERWORLD_TS
    rom[t0 + 3] = BANK; w16(t0 + 4, am); rom[t0 + 6] = BANK; w16(t0 + 7, am + len(meta2))
    route.blk = blks['Route22']
    log.append('tileset Overworld: %d blocks (+%d)' % (len(coll2) // 4, len(coll2) // 4 - nb0))

    # ================= Route 22
    objs, warps, bgl = P25.red_objects('Route22')
    assert [(x, y) for x, y, *_ in warps] == [DOOR] and (objs[0]['x'], objs[0]['y']) == RIVAL_AT
    me = MapEvents(rom, 'Route22')
    assert len(me.warps) == 1 and len(me.objs) == 1 and me.objs[0][0][0] == P17.SPR_BLUE
    old_w = me.warps[0]
    a = Asm(sp.here(BANK)); a.bank = BANK
    texts = {'r1i': P17.T(0x51682), 'r1a': P17.after(0x51682), 'r1w': P17.T(0x5175A), 'r1l': P17.T(0x5176D),
             'r2i': P17.T(0x517B8), 'r2a': P17.T(0x51842), 'r2w': P17.T(0x518B6), 'r2l': P17.T(0x518D7)}
    a.label('end'); a.end()
    me.objs = [[bytearray([P17.SPR_BLUE, RIVAL_AT[1] + 4, RIVAL_AT[0] + 4, P12.FACE['RIGHT'], 0, 0xFF, 0xFF, 0, 0, 0, 0,
                           R22_HIDE & 0xFF, R22_HIDE >> 8]), 'end']]
    rv = 2
    # which battle is due (0 = none): 1st after the Pokédex until the Boulder Badge, 2nd after the Earth Badge
    def due(a, tag, none, first, second):
        a.checkevent(EV_HOF); a.iftrue(none)
        a.checkflag(ENGINE_EARTH); a.iftrue(tag + '_e')
        a.checkevent(R22_FIRST); a.iftrue(none); a.checkflag(ENGINE_BOULDER); a.iftrue(none)
        a.checkflag(ENGINE_POKEDEX); a.iffalse(none); a.sjump(first)
        a.label(tag + '_e'); a.checkevent(R22_SECOND); a.iftrue(none); a.sjump(second)
    # objects callback: Shigeru stands there while a battle is due
    a.label('cb'); due(a, 'cbd', 'cb_h', 'cb_s', 'cb_s')
    a.label('cb_s'); a.clearevent(R22_HIDE); a.endcallback()
    a.label('cb_h'); a.setevent(R22_HIDE); a.endcallback()
    me.callbacks = [c for c in me.callbacks if c[0] != 2] + [(2, 'cb')]
    me.coords = []
    for y in (4, 5):
        L_ = 'c%d' % y; me.coords.append((0xFF, y, 29, L_))
        a.label(L_); due(a, L_ + 'd', 'end', L_ + '_1', L_ + '_2')
        for k, key, fl in (('1', 'r22a', R22_FIRST), ('2', 'r22b', R22_SECOND)):
            lab = '%s_%s' % (L_, k)
            a.label(lab); a.turnobject(0, TL); a.showemote(0, rv, 15); a.playmusic(MUS_RIVAL)
            a.applymovement(rv, 'in%d' % y); a.turnobject(rv, TR)
            a.opentext(); a.writetext('r%si' % k); a.waitbutton(); a.closetext()
            a.winlosstext('r%sw' % k, 'r%sl' % k); a.setlasttalked(rv)
            a.checkevent(EV_FIRE); a.iftrue(lab + 'f'); a.checkevent(EV_WATER); a.iftrue(lab + 'w')
            a.loadtrainer(BLUE, PARTY[key]['grass']); a.sjump(lab + 'go')
            a.label(lab + 'f'); a.loadtrainer(BLUE, PARTY[key]['fire']); a.sjump(lab + 'go')
            a.label(lab + 'w'); a.loadtrainer(BLUE, PARTY[key]['water'])
            a.label(lab + 'go'); a.startbattle(); a.dontrestartmapmusic(); a.reloadmapafterbattle()
            a.disappear(rv); a.moveobject(rv, 28, y); a.appear(rv); a.turnobject(rv, TR)     # redraw after the battle
            a.playmusic(MUS_RIVAL_AFTER); a.opentext(); a.writetext('r%sa' % k); a.waitbutton(); a.closetext()
            a.applymovement(rv, 'out%d' % y); a.disappear(rv); a.setevent(fl)
            a.moveobject(rv, *RIVAL_AT); a.playmapmusic(); a.end()
        a.label('in%d' % y); a.db(*RIVAL_IN[y], 0x47)
        a.label('out%d' % y); a.db(*RIVAL_OUT[y], 0x47)
    me.bgs = []
    for k, (x, y, tconst) in enumerate(bgl):
        L_ = 'sg%d' % k; a.label(L_); a.jumptext(L_ + 't'); texts[L_ + 't'] = rt(RED_ROUTE22, len(objs) + 1 + k)
        me.bgs.append((y, x, 0, L_))
    me.warps = [bytes([DOOR[1], DOOR[0]]) + old_w[2:]]
    put_texts(a, {k: P17.riv(v) for k, v in texts.items()})
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    me.install(a)
    log.append('Route22: Red events %X:%04X (%d bytes)' % (BANK, base, len(blob)))

    # ================= blocks; joined to Viridian City (Red, both)
    hr = hdr_index('Route22'); hv = hdr_index('ViridianCity'); ar, av = attrs(rom, hr), attrs(rom, hv)
    assert (ar['w'], ar['h']) == (20, 9) and av['blkbank'] == P29.BANK
    rblk = sp.put(BANK, route.blk)
    rom[hr + 1] = OVERWORLD_TS; ao = ar['attr_off']; rom[ao] = border_of('Route22'); rom[ao + 3] = BANK; w16(ao + 4, rblk)
    def conns(hdr):
        a_ = attrs(rom, hdr); o2 = a_['attr_off']
        return [o2 + 12 + 12 * k for k in range(bin(a_['conn'] & 0xF).count('1'))]
    n_ = 0
    for c in conns(hv):
        if (rom[c], rom[c + 1]) == r22:
            new = P22.connection('west', 20, 18, r22, 20, 9, 4, rblk + P22.strip_src('west', 20, 4))
            assert new[4:] == bytes(rom[c + 4:c + 12]); rom[c:c + 12] = new; n_ += 1
    for c in conns(hr):
        if (rom[c], rom[c + 1]) == vir:
            new = P22.connection('east', 20, 9, vir, 20, 18, -4, av['blk'] + P22.strip_src('east', 20, -4))
            assert new[4:] == bytes(rom[c + 4:c + 12]); rom[c:c + 12] = new; n_ += 1
    assert n_ == 2

    # ================= wild Pokémon (Red)
    kg = P27.kanto_grass(rom); p = kg
    while (rom[p], rom[p + 1]) != r22:
        assert rom[p] != 0xFF; p += 47
    t = open(PR + '/data/wild/maps/Route22.asm', encoding='utf-8').read()
    t = re.sub(r'IF DEF\(_BLUE\).*?ENDC', '', t, flags=re.S)
    rate = int(re.search(r'def_grass_wildmons (\d+)', t).group(1))
    slots = [(int(l_), s) for l_, s in re.findall(r'db\s+(\d+), (\w+)', t.split('end_grass_wildmons')[0])]
    pick = [slots[i] for i in (0, 1, 2, 3, 6, 8, 9)]
    rom[p:p + 47] = bytes([*r22, rate, rate, rate]) + bytes(sum(([lv, PM.MON[P10.MON_ALIAS.get(s, s)]] for lv, s in pick), [])) * 3

    # ================= the gate guard: the Boulder Badge (Red's Route 22 gate) instead of eight badges
    gate = MapEvents(rom, 'VictoryRoadGate')
    assert len(gate.coords) == 1 and gate.coords[0][:3] == (0, 11, 10)
    g = Asm(sp.here(BANK)); g.bank = BANK
    bg_, pg_ = RM.text_ptr(RED_GATE, 1)
    tx = {'gno': P28.jp(RM.fo(bg_, 0x749A)), 'gyes': RM.crystal_text(bg_, 0x74FB)}
    g.label('gc'); g.turnobject(0, TL); g.sjump('gq')
    g.label('gt'); g.faceplayer()
    g.label('gq'); g.opentext(); g.checkflag(ENGINE_BOULDER); g.iftrue('gy')
    g.writetext('gno'); g.waitbutton(); g.closetext(); g.applymovement(0, 'gd'); g.end()
    g.label('gy'); g.writetext('gyes'); g.waitbutton(); g.closetext(); g.setscene(1); g.end()
    g.label('gd'); g.db(D, 0x47)
    put_texts(g, tx)
    gate.coords = [(0, 11, 10, 'gc')]
    oi = [i for i, (o_, r) in enumerate(gate.objs) if r == ('far', gate.sb, 0x73B5)]; assert len(oi) == 1
    gate.objs[oi[0]][1] = 'gt'
    gate.write(g, sp)
    base = g.base; blob = g.done(); assert sp.put(BANK, blob) == base
    gate.install(g)
    log.append('VictoryRoadGate: guard (Boulder Badge) %X:%04X' % (BANK, base))

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    print('\n'.join(log))


if __name__ == '__main__':
    main()
