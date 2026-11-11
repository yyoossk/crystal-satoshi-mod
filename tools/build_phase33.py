#!/usr/bin/env python3
"""Phase 33: Routes 24, 25, 9 and 10 as in Red / the Pikachu full-color hack:
 * Route 24: Nugget Bridge with Red's five trainers and the Team Rocket member who hands over the Nugget and asks the
   player to join (then battles), TM Thunder Wave, Red's wild Pokémon.
 * Route 25: Red's nine trainers, TM Seismic Toss, the hidden Ether / Elixir, the sign; Bill's house as before (Red's
   before the Hall of Fame, Crystal's afterwards).
 * Route 9: Red's nine trainers, TM Teleport, the hidden Ether, the sign.
 * Route 10 (Red's one long route on Crystal's Route 10 North; Crystal's Route 10 South is no longer used): the Pokémon
   Center, both Rock Tunnel entrances (Crystal's Rock Tunnel), the Power Plant (phase 20), Red's six trainers, hidden
   items, signs.  Lavender Town (Crystal's) is joined to it at the matching road.
 * Routekit: maps' blocks are kept in both tileset versions and every connection is re-pointed from its own fields.
usage: build_phase33.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import portmaps as PM
import redmap as RM
import redtexts as RT
from evedit import MapEvents
import build_phase12 as P12
import build_phase15 as P15
import build_phase17 as P17
import build_phase25 as P25
import build_phase26 as P26
import build_phase28 as P28
import build_phase30 as P30
import routekit as RK

FIRST_FLAG = 279                   # 267-278: phase 32
MAX26 = 99
BANK, BANK2 = 0x74, 0x75           # 74: free in the JP original
SPR = dict(P30.SPR)
SPR.update({'SPRITE_HIKER': 0x3B, 'SPRITE_ROCKET': P25.SPR.get('SPRITE_ROCKET', 0x3C)})
NUGGET = None
POWER_PLANT, BILLS_RED = (26, 62), (26, 51)
SPAWN_ROCK_TUNNEL = P26.SPAWN_TABLE + 4 * 6
# Red route -> the Crystal map that becomes it
ROUTES = {'Route24': 'Route24', 'Route25': 'Route25', 'Route9': 'Route9', 'Route10': 'Route10North'}
RED_ID = {'Route24': 0x23, 'Route25': 0x24, 'Route9': 0x14, 'Route10': 0x15}


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (BANK, 0x78):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    K = RK.Kit(rom, sp, BANK, FL, log, MAX26)
    cname = lambda n: ROUTES.get(n, n)
    got_nugget = FL.new()

    # ================= blocks / tileset variants (doors)
    mps = {}
    for rn in ROUTES:
        w, h = RK.red_dims(rn); mps[rn] = MapPort(rn, K.ow, w, h, rn + '.blk'); K.dims[cname(rn)] = (w, h)
    ov = {rn: {(x, y): P25.warp_override(K.ow, mps[rn], x, y) for x, y, d, wi in P25.red_objects(rn)[1]} for rn in ROUTES}
    K.overworld_variants(mps, ov)
    K.add_parties(list(ROUTES))

    # ================= events
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    labels = {}
    # Route 24: the Rocket at the end of the bridge (Red: talks when the player steps in front of him)
    rk = {}
    def rocket(a, texts, lab, o):
        gR = RED_ID['Route24']; t = [RM.crystal_text(0x14, p_) for p_ in (0x5CF6, 0x5D4D, 0x5DCF, 0x5DE0, 0x5D40)]
        texts.update({lab + 'c': t[0], lab + 'j': t[1], lab + 'w': t[2], lab + 'l': t[3], lab + 'f': t[4]})
        cid = PM.TCLS['ROCKET']; pid = K.party_of[('Route24', 0)][1]
        a.label(lab); a.faceplayer()
        a.label(lab + 'go'); a.opentext(); a.checkevent(got_nugget); a.iftrue(lab + 'g')
        a.writetext(lab + 'c'); a.promptbutton(); a.verbosegiveitem(PM.item_id('NUGGET'), 1); a.iffalse(lab + 'z')
        a.setevent(got_nugget); a.writetext(lab + 'j'); a.waitbutton(); a.closetext()
        a.winlosstext(lab + 'w', 0); a.loadtrainer(cid, pid); a.startbattle(); a.reloadmapafterbattle()
        a.opentext(); a.writetext(lab + 'l'); a.waitbutton(); a.closetext(); a.end()
        a.label(lab + 'g'); a.writetext(lab + 'l'); a.waitbutton(); a.closetext(); a.end()
        a.label(lab + 'z'); a.writetext(lab + 'f'); a.waitbutton(); a.closetext(); a.applymovement(0, lab + 'd'); a.end()
        a.label(lab + 'd'); a.db(0x0C, 0x47)
        a.label(lab + 'k'); a.checkevent(got_nugget); a.iftrue('rk_end'); a.turnobject(0, 3); a.sjump(lab + 'go')
        a.label('rk_end'); a.end()
        rk['coord'] = lab + 'k'
        return SPR['SPRITE_ROCKET'] if False else None, 0, 0xFFFF, 0
    built = {}
    for rn in ROUTES:
        special = {1: rocket} if rn == 'Route24' else {}
        ob, bgs = K.red_events(a, texts, rn, RED_ID[rn], rn[5:] + '_', special, SPR)
        built[rn] = (ob, bgs)
    K.put_texts(a, texts)
    # warps
    r10 = mapid('Route10North')
    w = {rn: [] for rn in ROUTES}
    w['Route25'] = [bytes([3, 45, 1, *BILLS_RED])]
    w['Route10'] = [bytes([19, 11, 1, *mapid('Route10Pokecenter1F')]), bytes([17, 8, 1, *mapid('RockTunnel1F')]),
                    bytes([53, 8, 2, *mapid('RockTunnel1F')]), bytes([39, 6, 1, *POWER_PLANT])]
    assert [(x, y) for x, y, *_ in P25.red_objects('Route10')[1]] == [(11, 19), (8, 17), (8, 53), (6, 39)]
    coords = {rn: [] for rn in ROUTES}; coords['Route24'] = [(0xFF, 15, 10, rk['coord'])]
    # Crystal's own callbacks (fly points) stay; Route 25's (phase 16's Bill's house switch) is made anew
    cbs = {}
    for rn in ROUTES:
        me = MapEvents(rom, cname(rn)); cbs[rn] = []
        if rn == 'Route25': continue
        for t_, r in me.callbacks:
            L_ = rn + 'cb%d' % t_; a.label(L_); a.farsjump(r[1], r[2]); cbs[rn].append((t_, L_))
    for rn in ROUTES:
        ob, bgs = built[rn]
        K.emit(a, rn, w[rn], coords[rn], bgs, ob, cbs[rn])
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    log.append('routes: Red events %X:%04X (%d bytes)' % (BANK, base, len(blob)))

    # ================= attributes + connections (Red's; Lavender (Crystal) matched to Route 10's road)
    lav_off = K.best_offset('south', K.red_walk(mps['Route10']), K.walk_grid('LavenderTown'), 0)
    log.append('Lavender joined to Route 10 at offset %d (Red: 0)' % lav_off)
    conns = {'Route24': [('south', 'CeruleanCity', -5), ('east', 'Route25', 0)],
             'Route25': [('west', 'Route24', 0)],
             'Route9': [('west', 'CeruleanCity', -4), ('east', 'Route10North', 0)],
             'Route10': [('south', 'LavenderTown', lav_off), ('west', 'Route9', 0)]}
    for rn in ROUTES:
        mp = mps[rn]
        K.new_attrs(cname(rn), mp.w, mp.h, border_of(rn), a.labels[rn + 'ms'], a.labels[rn + 'ev'], conns[rn])
        rom[hdr_index(cname(rn)) + 1] = RK.OVERWORLD_TS
    # the other side: Cerulean (Red) -> 24 (north), 9 (east); Lavender (Crystal) -> 10 (north, was Route 10 South)
    K.set_conn('CeruleanCity', 'north', 'Route24', 5)
    K.set_conn('CeruleanCity', 'east', 'Route9', 4)
    K.set_conn('LavenderTown', 'north', 'Route10North', -lav_off)
    # blocks of every map involved, both versions, all pointers
    for rn in ROUTES: K.place_blocks(cname(rn), mps[rn].blk, True)
    ca = attrs(rom, hdr_index('CeruleanCity'))
    K.place_blocks('CeruleanCity', bytes(rom[fo(ca['blkbank'], ca['blk']):][:ca['w'] * ca['h']]), True)
    la = attrs(rom, hdr_index('LavenderTown'))
    K.place_blocks('LavenderTown', bytes(rom[fo(la['blkbank'], la['blk']):][:la['w'] * la['h']]), False)

    # ================= warps back
    def fix_warps(name, fn):
        a_ = attrs(rom, hdr_index(name)); ev = parse_events(rom, a_['scbank'], a_['events']); n_ = 0
        for i, (o_, w_) in enumerate(ev['warps']):
            r_ = fn(i, w_)
            if r_: rom[o_ + 2] = r_[0]; rom[o_ + 3:o_ + 5] = bytes(r_[1]); n_ += 1
        return n_
    assert fix_warps('RockTunnel1F', lambda i, w_: (2, r10) if (w_[3], w_[4]) == mapid('Route9') else
                     ((3, r10) if (w_[3], w_[4]) == mapid('Route10South') else None)) == 2
    hp = GROUP26_END + 9 * (POWER_PLANT[1] - G26_COUNT - 1)
    a_ = attrs(rom, hp); ev = parse_events(rom, a_['scbank'], a_['events']); n_ = 0
    for o_, w_ in ev['warps']:
        if (w_[3], w_[4]) == r10: rom[o_ + 2] = 4; n_ += 1
    assert n_
    assert fix_warps('Route10Pokecenter1F', lambda i, w_: (1, r10) if (w_[3], w_[4]) == r10 else None) == 2
    rom[SPAWN_ROCK_TUNNEL:SPAWN_ROCK_TUNNEL + 4] = bytes([*r10, 11, 20])
    # Bill's house: Red's before the Hall of Fame, Crystal's afterwards (phase 16's switch, made anew)
    P15.install_hof_switch(rom, sp, 'Route25', {0: bytes([3, 45, 1, *mapid('BillsHouse')])}, log)

    # ================= wild Pokémon
    for rn in ROUTES: K.red_wild(mapid(cname(rn)), rn)

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    assert FL.i < 8 * (P28.SCENE_AREAS - 0xDA01)
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
