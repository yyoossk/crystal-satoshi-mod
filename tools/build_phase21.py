#!/usr/bin/env python3
"""Phase 21: Red's Seafoam Islands (1F-B4F, ported from the Pikachu full-color hack) before the Kanto Hall of Fame,
working like Red:
 * Strength boulders fall through the holes and show up on the floor below; the player falls through the holes too.
 * B3F/B4F strong currents (Red's forced surfing) until the boulders have blocked them; B3F/B4F bottom-edge water
   warps; on B4F, no surfing from the stairs at (7,11) until the B3F boulders have fallen ("current too fast").
 * Red's tile-pair collisions (elevation edges of the Cavern tileset) as Crystal side walls -- Mt. Moon gets them too.
 * Articuno (Lv 50): gone after the battle unless the player loses; B4F signs.
Reached from Red's Route 20 (phase 22), also after the Hall of Fame (as in the Pikachu full-color hack).
Also: Chris's back pic moves out of bank 0A to make room in the Kanto grass wild table; the map scene table moves to
bank 0x61 (B3F/B4F scene bytes DA63/DA64).
usage: build_phase21.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import pkmap
import portmaps as PM
import pairwalls
import redtexts as RT
import build_phase10 as P10
import build_phase12 as P12
import build_phase15 as P15
import build_phase20 as P20

FIRST_FLAG = 125
FIRST_MAP = 63                     # 26:62 = Power Plant (phase 20)
CAVERN_TS = 37
F1, B1, B2, B3, B4 = ('SeafoamIslands1F', 'SeafoamIslandsB1F', 'SeafoamIslandsB2F', 'SeafoamIslandsB3F',
                      'SeafoamIslandsB4F')
MAPS = [(F1, 0xC0), (B1, 0x9F), (B2, 0xA0), (B3, 0xA1), (B4, 0xA2)]
MOON = [('MtMoon1F', 0x3B), ('MtMoonB1F', 0x3C), ('MtMoonB2F', 0x3D)]
CONST = {'SEAFOAM_ISLANDS_1F': F1, 'SEAFOAM_ISLANDS_B1F': B1, 'SEAFOAM_ISLANDS_B2F': B2,
         'SEAFOAM_ISLANDS_B3F': B3, 'SEAFOAM_ISLANDS_B4F': B4}
# Red: SeafoamNHolesCoords and DungeonWarpData (where the player lands on the floor below)
HOLES = {F1: [(17, 6), (24, 6)], B1: [(18, 6), (23, 6)], B2: [(19, 6), (22, 6)], B3: [(3, 16), (6, 16)]}
BELOW = {F1: B1, B1: B2, B2: B3, B3: B4}
LAND = {B1: [(18, 7), (23, 7)], B2: [(19, 7), (22, 7)], B3: [(18, 7), (19, 7)], B4: [(4, 14), (5, 14)]}
# Red's toggleable boulders that are hidden at first: (map, object #) <- (map above, hole #)
APPEAR = {(B1, 1): (F1, 0), (B1, 2): (F1, 1), (B2, 1): (B1, 0), (B2, 2): (B1, 1),
          (B3, 5): (B2, 0), (B3, 6): (B2, 1), (B4, 1): (B3, 0), (B4, 2): (B3, 1)}
PAIRS = [(0x20, 0x05), (0x41, 0x05), (0x2A, 0x05), (0x05, 0x21), (0x14, 0x05)]   # Red: TilePairCollisions (CAVERN)
SPR_BOULDER, SPR_BIRD, MV_BOULDER, STD_BOULDER = 0x5A, 0x4E, 0x19, 0x0E
CHRIS_BACKPIC = (0x2BA3D, 0x2BBCD)
CHRIS_REFS = [(0x3FC39, 0x3FC3B), (0x8883D, 0x8883A)]      # (bank byte, address)
WATER = 0x14
COLL_PIT = 0x60
MON = PM.MON
# scenes
SCENES_REF = 0x210F                 # GetMapSceneID: ld a, BANK(MapScenes) ; rst Bankswitch ; ld hl, MapScenes
SCENE_BYTE = {B3: 0xDA63, B4: 0xDA64}
# script bits
D, U, L, R = 0x0C, 0x0D, 0x0E, 0x0F
MEND = 0x47
VAR_BATTLERESULT, VAR_MOVEMENT, VAR_FACING, VAR_X, VAR_Y = 0x02, 0x08, 0x09, 0x12, 0x13
SP_UPDATEPLAYERSPRITE, SP_PLAYMAPMUSIC = 0x38, 0x3C
W_SURFINGPLAYERSTATE, H_JOYDOWN = 0xD21C, 0xFFA8
PLAYER_SURF, PLAYER_SURF_PIKA = 4, 8
# surfing from B4F's stairs (Red: IsSurfingAllowed)
SURF_FN_CHECKDIR = 0xC95D           # SurfFunction.TrySurf: call CheckDirection ; jr c, .cannotsurf
SURF_OW_CHECKDIR = 0xCA3C           # TrySurfOW:            call CheckDirection ; jr c, .quit
CHECKDIRECTION, PRINTTEXT_MENU, CALLSCRIPT = 0x4A0B, 0x1D32, 0x25E2
W_MAPGROUP, W_MAPNUMBER, W_YCOORD, W_XCOORD = 0xDC7B, 0xDC7C, 0xDC7D, 0xDC7E
RED_CURRENT_TOO_FAST = (0xC5B5, 0xC5C5)       # aka: "ながれが はやくて ダメだ！" (ends with prompt)
RED_SIGNS = {(9, 15): 0x477B8, (23, 1): 0x477D1}


def flag_bit(f):
    assert 0x800 <= f < 0x800 + 95 * 8
    return P15.W_EXTFLAGS + ((f - 0x800) >> 3), f & 7


class S(Asm):
    def readvar(s, v): s.db(0x1C, v)
    def writevar(s, v): s.db(0x1D, v)
    def ifless(s, v, l): s.db(0x0B, v); s.dw(l)
    def writecmdqueue(s, l): s.db(0x7C); s.dw(l)
    def waitsfx(s): s.db(0x85)


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (0x03, 0x60, 0x61, 0x63, 0x75, 0x78, 0x79):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1, b * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)

    # ================= Chris's back pic -> bank 60
    lo_, hi_ = CHRIS_BACKPIC
    for bb, aa in CHRIS_REFS:
        assert rom[bb] == 0x0A and r16(aa) == 0x4000 + lo_ % 0x4000, hex(bb)
    na = sp.put(0x60, bytes(rom[lo_:hi_]))
    for bb, aa in CHRIS_REFS:
        rom[bb] = 0x60; w16(aa, na)
    rom[lo_:hi_] = bytes(hi_ - lo_)
    log.append('Chris back pic moved to 60:%04X' % na)

    # ================= map ids, Route 20's door
    mapids = {n: (G26, FIRST_MAP + i) for i, (n, g) in enumerate(MAPS)}
    r20 = mapid('Route20')                  # Red's Route 20 (phase 22): warps 1 / 2 = the two caves
    hc = hdr_index('SeafoamGym')

    # ================= flags
    hole_fl = {(n, k): FL.new() for n in HOLES for k in range(2)}
    objs_of = {n: PM.objects_of(n) for n, g in MAPS}
    obj_fl, gone_fl = {}, {}
    for n, g in MAPS:
        for i, o in enumerate(objs_of[n][0]):
            obj_fl[(n, i + 1)] = FL.new()
            if (n, i + 1) in APPEAR and o['face'] == 'BOULDER_MOVEMENT_BYTE_2': gone_fl[(n, i + 1)] = FL.new()

    # ================= Cavern tileset: water, warps, holes, Red's elevation edges (Mt. Moon + Seafoam)
    TS = PM.Tilesets(rom, sp)
    cav = Tileset('Cavern', 17, 'cavern.bst', SC + '/out/pk_cavern.pkl')
    e = TS.entry(CAVERN_TS)
    co, mo = fo(e[6], e[7] | e[8] << 8), fo(e[3], e[4] | e[5] << 8)
    coll = bytearray(rom[co:co + 4 * cav.nblocks]); meta = bytes(rom[mo:mo + 16 * cav.nblocks])
    assert meta == bytes(cav.blocks)
    for b in range(cav.nblocks):
        for q in range(4):
            if cav.quad_tile(b, q) == WATER: coll[4 * b + q] = COLL_WATER
    maps = {}
    for n, g in MAPS + MOON:
        h = pkmap.header(g); maps[n] = MapPort(n, cav, h['w'], h['h'], n + '.blk')
    for n, g in MAPS:                                   # same rule as Mt. Moon (phase 15): ladders are staircases
        mp = maps[n]
        for (x, y, dest, wid) in objs_of[n][1]:
            b_, q = mp.block_at(x, y); tile = cav.quad_tile(b_, q)
            if tile == WATER: continue                 # B3F/B4F bottom-edge water warps: handled by the scene scripts
            if tile in cav.warp_tiles: v = COLL_STAIRCASE
            elif y == mp.h * 2 - 1 or y == 0 or x == 0 or x == mp.w * 2 - 1:
                v = COLL_CARPET['down'] if y == mp.h * 2 - 1 else COLL_CARPET['up'] if y == 0 else \
                    COLL_CARPET['left'] if x == 0 else COLL_CARPET['right']
            else: raise AssertionError((n, x, y, hex(tile)))
            old = coll[4 * b_ + q]
            assert old in (COLL_FLOOR, COLL_WALL, v), (n, x, y, hex(old), hex(v))
            coll[4 * b_ + q] = v
    pits = {n: {p: COLL_PIT for p in HOLES[n]} for n in HOLES}
    meta2, coll2, blks = pairwalls.variants(cav, meta, bytes(coll), maps, PAIRS, pits)
    nb2 = len(coll2) // 4
    if nb2 > 128: pairwalls.fix_loadmetatiles(rom)
    am = sp.put(0x61, meta2); ac = sp.put(0x61, coll2)
    t0 = TS.tab + 15 * CAVERN_TS
    rom[t0 + 3] = 0x61; w16(t0 + 4, am); rom[t0 + 6] = 0x61; w16(t0 + 7, ac)
    log.append('Cavern tileset: %d blocks (+%d with side walls / holes), metatiles 61:%04X collision 61:%04X'
               % (nb2, nb2 - cav.nblocks, am, ac))
    # Mt. Moon's blocks (phase 15) in place
    u = US.get(); G = u.groups()
    moon_done = set()
    for gi in range(26):
        for k in range((G[gi + 1] - G[gi]) // 9 if gi + 1 < 26 else FIRST_MAP - 1):
            hdr = G[gi] + 9 * k
            if rom[hdr + 1] != CAVERN_TS: continue
            a_ = fo(rom[hdr], r16(hdr + 3)); bo = fo(rom[a_ + 3], r16(a_ + 4)); h_, w_ = rom[a_ + 1], rom[a_ + 2]
            for n, g in MOON:
                mp = maps[n]
                if (mp.h, mp.w) == (h_, w_) and bytes(rom[bo:bo + len(mp.blk)]) == mp.blk:
                    rom[bo:bo + len(mp.blk)] = blks[n]; moon_done.add(n)
    assert moon_done == {n for n, g in MOON}, moon_done

    # ================= headers 26:63-67
    lo, hi = GROUP26_END + 9 * (FIRST_MAP - G26_COUNT - 1), GROUP26_END + 9 * (FIRST_MAP - G26_COUNT - 1 + len(MAPS))
    for gi in range(26):
        n_ = (G[gi + 1] - G[gi]) // 9 if gi + 1 < 26 else FIRST_MAP - 1
        for k in range(n_):
            hdr = G[gi] + 9 * k
            ab = rom[hdr]; ap = r16(hdr + 3); ao = fo(ab, ap)
            nconn = bin(rom[ao + 11] & 0xF).count('1'); size = 12 + 12 * nconn
            if ao < hi and ao + size > lo:
                rom[hdr] = 0x79; w16(hdr + 3, sp.put(0x79, bytes(rom[ao:ao + size])))
    rom[lo:hi] = bytes(hi - lo)

    # warp lists: Red's warps, then the holes, then the landing spots (warp targets of the holes above)
    nred = {n: len(objs_of[n][1]) for n, g in MAPS}
    def land_warp(n, k): return nred[n] + len(HOLES.get(n, [])) + k + 1

    def both_set(a, fls, yes, no):
        a.checkevent(fls[0]); a.iffalse(no); a.checkevent(fls[1]); a.iffalse(no); a.sjump(yes)

    def surf_on(a, lab):
        """Red: CheckForceBikeOrSurf -- the landing spots in the water make the player surf"""
        a.label(lab); a.readvar(VAR_MOVEMENT); a.ifequal(PLAYER_SURF, lab + 'x'); a.ifequal(PLAYER_SURF_PIKA, lab + 'x')
        a.readmem(W_SURFINGPLAYERSTATE); a.writevar(VAR_MOVEMENT)
        a.special(SP_UPDATEPLAYERSPRITE); a.special(SP_PLAYMAPMUSIC)
        a.label(lab + 'x'); a.end()

    def walk_on(a):
        a.db(0x1E, VAR_MOVEMENT, 0); a.special(SP_UPDATEPLAYERSPRITE); a.special(SP_PLAYMAPMUSIC)

    def edge(a, lab, x, other):
        """Red: the B3F/B4F bottom-edge warps (taken when pushing down on them)"""
        a.label(lab); a.readvar(VAR_FACING); a.ifnotequal(0, 'end'); a.readmem(H_JOYDOWN); a.ifless(0x80, 'end')
        a.setmapscene(*mapids[other], 1); a.warp(*mapids[other], x, 17); a.end()

    def disarm(a):
        """scene 1: just arrived through an edge warp -- wait until DOWN is released"""
        a.label('scene1'); a.readmem(H_JOYDOWN); a.ifless(0x80, 'arm'); a.end()
        a.label('arm'); a.setscene(0); a.end()

    b2fl = [hole_fl[(B2, 0)], hole_fl[(B2, 1)]]
    b3fl = [hole_fl[(B3, 0)], hole_fl[(B3, 1)]]
    for n, g in MAPS:
        objs, warps, skip, bgl = objs_of[n]
        a = S(sp.here(0x63)); obj_bytes = []; movs = {}; scenes = []; callbacks = []; bgs = []
        a.label('end'); a.end()
        # ---- objects
        pushable = []
        for idx, o in enumerate(objs):
            lab = 'o%d' % (idx + 1); oid = idx + 2
            if o['sprite'] == 'SPRITE_BOULDER':
                mv = MV_BOULDER if o['face'] == 'BOULDER_MOVEMENT_BYTE_2' else P12.FACE['DOWN']
                if mv == MV_BOULDER: pushable.append(idx + 1)
                a.label(lab); a.jumpstd(STD_BOULDER)
                obj_bytes.append([SPR_BOULDER, o['y'] + 4, o['x'] + 4, mv, 0, 0xFF, 0xFF, 0, 0, lab, obj_fl[(n, idx + 1)]])
            elif o['sprite'] == 'SPRITE_BIRD':
                P20.red_wild(a, lab, oid, 'art', MON['ARTICUNO'], int(o['extra'][1]))
                a.label('art'); a.raw(P12.text(encode('{00}ギャーオ！')))
                obj_bytes.append([SPR_BIRD, o['y'] + 4, o['x'] + 4, P12.FACE['DOWN'], 0, 0xFF, 0xFF, 0, 0, lab,
                                  obj_fl[(n, idx + 1)]])
        # ---- boulders that show up after falling from above
        app = [(i, src) for (m, i), src in APPEAR.items() if m == n]
        if app:
            a.label('cb_obj')
            for i, (sm, sk) in sorted(app):
                h_ = obj_fl[(n, i)]; L_ = 'ap%d' % i
                a.checkevent(hole_fl[(sm, sk)]); a.iffalse(L_ + 'h')
                if (n, i) in gone_fl: a.checkevent(gone_fl[(n, i)]); a.iftrue(L_ + 'h')
                a.clearevent(h_); a.sjump(L_ + 'n')
                a.label(L_ + 'h'); a.setevent(h_)
                a.label(L_ + 'n')
            a.endcallback()
            callbacks.append((2, 'cb_obj'))                     # MAPCALLBACK_OBJECTS
        # ---- holes: boulders fall through (Crystal's stone table)
        if n in HOLES:
            a.label('cb_cq'); a.writecmdqueue('cq'); a.endcallback()
            a.label('cq'); a.db(2); a.dw('stones'); a.dw(0)       # CMDQUEUE_STONETABLE
            a.label('stones')
            for k in range(2):
                for i in pushable:
                    a.db(nred[n] + k + 1, i + 1); a.dw('fall%d_%d' % (k, i))
            a.db(0xFF)
            for k in range(2):
                for i in pushable:
                    a.label('fall%d_%d' % (k, i))
                    if (n, i) in gone_fl: a.setevent(gone_fl[(n, i)])
                    a.disappear(i + 1); a.setevent(hole_fl[(n, k)]); a.end()
            callbacks.append((3, 'cb_cq'))                      # MAPCALLBACK_CMDQUEUE
        # ---- B3F / B4F: Red's per-frame map scripts (currents, forced surfing, edge warps)
        if n == B3:
            a.label('scene0'); a.readvar(VAR_Y)
            a.ifequal(8, 'y8'); a.ifequal(7, 'y7'); a.ifequal(17, 'y17'); a.end()
            # Red: SeafoamIslandsB3FDefaultScript -- strong current from (15,8) into B4F
            a.label('y8'); a.readvar(VAR_X); a.ifnotequal(15, 'end'); both_set(a, b2fl, 'end', 'c0')
            a.label('c0'); a.applymovement(0, 'm_c0'); a.warp(*mapids[B4], 20, 17); a.end()
            movs['m_c0'] = [D] * 3 + [R] * 5 + [D] * 6
            # Red: SeafoamIslandsB3FMoveObjectScript -- fell into the water through B2F's holes
            a.label('y7'); a.readvar(VAR_X); a.ifequal(18, 'x18'); a.ifequal(19, 'x19'); a.end()
            for x_, mv_ in ((18, [D] * 4 + [R] * 2 + [D] * 6), (19, [L] + [D] * 4 + [R] * 2 + [D] * 6)):
                L_ = 'x%d' % x_
                a.label(L_); a.scall(L_ + 's'); both_set(a, b2fl, 'end', L_ + 'c')
                a.label(L_ + 'c'); a.applymovement(0, 'm_' + L_); a.warp(*mapids[B4], 20, 17); a.end()
                movs['m_' + L_] = mv_
                surf_on(a, L_ + 's')
            a.label('y17'); a.readvar(VAR_X); a.ifequal(20, 'e20'); a.ifequal(21, 'e21'); a.end()
            edge(a, 'e20', 20, B4); edge(a, 'e21', 21, B4)
            disarm(a)
            scenes = ['scene0', 'scene1']
        if n == B4:
            a.label('scene0'); a.readvar(VAR_Y)
            a.ifequal(17, 'y17'); a.ifequal(16, 'y16'); a.ifequal(14, 'y14'); a.end()
            # Red: SeafoamIslandsB4FDefaultScript -- the current pushes the player back up from the bottom edge
            a.label('y16'); a.readvar(VAR_X); a.ifequal(20, 'u1'); a.ifequal(21, 'u1'); a.end()
            a.label('u1'); both_set(a, b2fl, 'end', 'u1c')
            a.label('u1c'); a.applymovement(0, 'm_u1'); a.end(); movs['m_u1'] = [U]
            a.label('y17'); a.readvar(VAR_X); a.ifequal(20, 'b20'); a.ifequal(21, 'b21'); a.end()
            for x_ in (20, 21):
                L_ = 'b%d' % x_
                a.label(L_); both_set(a, b2fl, 'e%d' % x_, L_ + 'c')
                a.label(L_ + 'c'); a.applymovement(0, 'm_u2'); a.end()
                edge(a, 'e%d' % x_, x_, B3)
            movs['m_u2'] = [U, U]
            # Red: SeafoamIslandsB4FMoveObjectScript -- fell into the water through B3F's holes
            a.label('y14'); a.readvar(VAR_X); a.ifequal(4, 'x4'); a.ifequal(5, 'x5'); a.end()
            for x_, nr in ((4, 3), (5, 2)):
                L_ = 'x%d' % x_
                a.label(L_); a.scall(L_ + 's'); both_set(a, b3fl, 'end', L_ + 'c')
                a.label(L_ + 'c'); a.applymovement(0, 'm_' + L_ + 'a'); walk_on(a); a.applymovement(0, 'm_up2'); a.end()
                movs['m_' + L_ + 'a'] = [U] + [R] * nr + [U]
                surf_on(a, L_ + 's')
            movs['m_up2'] = [U, U]
            disarm(a)
            scenes = ['scene0', 'scene1']
            for (x_, y_), o_ in RED_SIGNS.items():
                L_ = 'sg%d' % x_; a.label(L_); a.jumptext(L_ + 't'); a.label(L_ + 't'); a.raw(P12.text(RT.raw(o_)))
                bgs.append((y_, x_, 0, L_))
        for k_, v in movs.items():
            a.label(k_); a.raw(bytes(v) + bytes([MEND]))
        # ---- header + events
        a.label('mapscripts'); a.db(len(scenes))
        for s_ in scenes: a.dw(s_); a.dw(0)
        a.db(len(callbacks))
        for t_, l_ in callbacks: a.db(t_); a.dw(l_)
        a.label('events'); a.db(0, 0)
        wl = []
        for x, y, dest, wid in warps:
            wl.append((y, x, wid, *r20) if dest == 'LAST_MAP' else (y, x, wid, *mapids[CONST[dest]]))
        for k, (x, y) in enumerate(HOLES.get(n, [])):
            wl.append((y, x, land_warp(BELOW[n], k), *mapids[BELOW[n]]))
        for k, (x, y) in enumerate(LAND.get(n, [])):
            up = [m for m, b_ in BELOW.items() if b_ == n][0]
            wl.append((y, x, nred[up] + k + 1, *mapids[up]))
        a.db(len(wl))
        for w_ in wl: a.db(*w_)
        a.db(0)
        a.db(len(bgs))
        for (y_, x_, t_, l_) in bgs: a.db(y_, x_, t_); a.dw(l_)
        a.db(len(obj_bytes))
        for ob in obj_bytes: a.db(*ob[:9]); a.dw(ob[9]); a.dw(ob[10])
        base = a.base; blob = a.done(); assert sp.put(0x63, blob) == base
        mp = maps[n]
        blkp = sp.put(0x60, blks[n])
        aa = sp.put(0x60, bytes([border_of(n), mp.h, mp.w, 0x60, blkp & 0xFF, blkp >> 8, 0x63, a.labels['mapscripts'] & 0xFF,
                                 a.labels['mapscripts'] >> 8, a.labels['events'] & 0xFF, a.labels['events'] >> 8, 0]))
        hh = GROUP26_END + 9 * (mapids[n][1] - G26_COUNT - 1)
        rom[hh:hh + 9] = bytes([0x60, CAVERN_TS, 4, aa & 0xFF, aa >> 8, rom[hc + 5], rom[hc + 6], 0x01, 0x00])
        log.append('%s -> map %d:%d  scripts 63:%04X (%d bytes)' % (n, *mapids[n], base, len(blob)))

    # ================= scene bytes for B3F/B4F (map scene table -> bank 0x61)
    assert rom[SCENES_REF - 1] == 0x3E and rom[SCENES_REF + 1] == 0xD7 and rom[SCENES_REF + 2] == 0x21
    tb = fo(rom[SCENES_REF], r16(SCENES_REF + 3)); n_ = 0
    while rom[tb + 4 * n_] != 0xFF: n_ += 1
    tab = bytes(rom[tb:tb + 4 * n_])
    for n in (B3, B4):
        tab += bytes([*mapids[n], SCENE_BYTE[n] & 0xFF, SCENE_BYTE[n] >> 8])
    at = sp.put(0x61, tab + b'\xff')
    rom[SCENES_REF] = 0x61; w16(SCENES_REF + 3, at)
    rom[tb:tb + 4 * n_ + 1] = b'\xff' * (4 * n_ + 1)        # old table: unused
    log.append('map scene table -> 61:%04X (%d entries)' % (at, n_ + 2))

    # ================= B4F: no surfing from the stairs at (7,11) before the B3F boulders fell (Red: IsSurfingAllowed)
    t_red = bytes(RT.R[RED_CURRENT_TOO_FAST[0]:RED_CURRENT_TOO_FAST[1]]); assert t_red[-1] == 0x58
    s_ = S(sp.here(0x63)); s_.label('s'); s_.jumptext('t'); s_.label('t'); s_.raw(P12.text(t_red[:-1]))
    sbase = s_.base; sblob = s_.done(); assert sp.put(0x63, sblob) == sbase
    (fa1, fb1), (fa2, fb2) = flag_bit(hole_fl[(B3, 0)]), flag_bit(hole_fl[(B3, 1)])
    code = bytearray(); fix = []
    def emit(*bs): code.extend(bs)
    base3 = sp.here(0x03)
    txt_at = base3 + len(code); emit(*t_red)
    blk_at = base3 + len(code)
    for addr, v in ((W_MAPGROUP, mapids[B4][0]), (W_MAPNUMBER, mapids[B4][1]), (W_XCOORD, 7), (W_YCOORD, 11)):
        emit(0xFA, addr & 0xFF, addr >> 8, 0xFE, v, 0x20); fix.append(len(code)); emit(0)       # jr nz, .no
    emit(0xFA, fa1 & 0xFF, fa1 >> 8, 0xCB, 0x47 | (fb1 << 3), 0x28); fix_yes = [len(code)]; emit(0)  # jr z, .yes
    emit(0xFA, fa2 & 0xFF, fa2 >> 8, 0xCB, 0x47 | (fb2 << 3), 0x28); fix_yes.append(len(code)); emit(0)
    no_at = len(code); emit(0xA7, 0xC9)                    # .no: and a ; ret
    yes_at = len(code); emit(0x37, 0xC9)                   # .yes: scf ; ret
    for p in fix: code[p] = (no_at - (p + 1)) & 0xFF
    for p in fix_yes: code[p] = (yes_at - (p + 1)) & 0xFF
    h1_at = base3 + len(code)                              # SurfFunction: print the text, fail
    emit(0xCD, CHECKDIRECTION & 0xFF, CHECKDIRECTION >> 8, 0xD8, 0xCD, blk_at & 0xFF, blk_at >> 8, 0xD0, 0xE1,
         0x21, txt_at & 0xFF, txt_at >> 8, 0xCD, PRINTTEXT_MENU & 0xFF, PRINTTEXT_MENU >> 8, 0x3E, 0x80, 0xC9)
    h2_at = base3 + len(code)                              # TrySurfOW (A on the water): the same text as a script
    emit(0xCD, CHECKDIRECTION & 0xFF, CHECKDIRECTION >> 8, 0xD8, 0xCD, blk_at & 0xFF, blk_at >> 8, 0xD0, 0xE1,
         0x3E, 0x63, 0x21, sbase & 0xFF, sbase >> 8, 0xCD, CALLSCRIPT & 0xFF, CALLSCRIPT >> 8, 0x37, 0xC9)
    assert sp.put(0x03, bytes(code)) == base3
    for o_, h_ in ((SURF_FN_CHECKDIR, h1_at), (SURF_OW_CHECKDIR, h2_at)):
        assert rom[o_] == 0xCD and r16(o_ + 1) == CHECKDIRECTION and rom[o_ + 3] == 0x38, hex(o_)
        w16(o_ + 1, h_)
    log.append('B4F stairs surf check 03:%04X (%d bytes)' % (base3, len(code)))

    # ================= wild Pokémon (Red) -> Kanto grass table
    p = P15.KANTO_GRASS
    while rom[p] != 0xFF: p += 47
    ent = b''
    for n, g in MAPS:
        t = open(PR + '/data/wild/maps/%s.asm' % n, encoding='utf-8').read()
        t = re.sub(r'IF DEF\(_BLUE\).*?ENDC', '', t, flags=re.S)
        rate = int(re.search(r'def_grass_wildmons (\d+)', t).group(1))
        slots = [(int(l), s) for l, s in re.findall(r'db\s+(\d+), (\w+)', t.split('end_grass_wildmons')[0])]
        assert len(slots) == 10, n
        pick = [slots[i] for i in (0, 1, 2, 3, 6, 8, 9)]
        ent += bytes([*mapids[n], rate, rate, rate]) + bytes(sum(([lv, MON[P10.MON_ALIAS.get(s, s)]] for lv, s in pick), [])) * 3
    assert not any(rom[p + 1:p + 1 + len(ent)])
    rom[p:p + len(ent) + 1] = ent + b'\xff'
    log.append('Seafoam Islands wild data (%d bytes)' % len(ent))

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    log.append('extended flags used up to %d' % FL.i)
    log.append('flags: holes %s' % {'%s/%d' % (k[0][-3:], k[1]): hex(v) for k, v in hole_fl.items()})
    print('\n'.join(log))


if __name__ == '__main__':
    main()
