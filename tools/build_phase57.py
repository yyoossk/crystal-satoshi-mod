#!/usr/bin/env python3
"""Phase 57: all 151 Pokémon in Kanto, as in the Pikachu full-color hack's "151" version (kit
kit151/ピカチュウ_151匹そろう版_クリスタルのカントー).
 * Wild Pokémon: Crystal's Kanto grass / cave and surfing tables are replaced by the kit's (kanto_grass_151.asm,
   kanto_water_151.asm), the kit's (pokeyellow) map names given this MOD's maps (Red's maps ported from the Pikachu
   full-color hack: Viridian Forest, Mt. Moon, Rock Tunnel, Diglett's Cave, Power Plant, Pokémon Tower, Seafoam
   Islands, Victory Road, Pokémon Mansion, the Safari Zone's four areas, Cerulean Cave).  Crystal's entries that the
   kit has no map for stay (Mt. Moon after the Hall of Fame, Tohjo Falls, Routes 26, 27, 28).
   The grass table grows (60 maps): the player's back picture after it in bank 0A is moved to another bank.
   The Pokémon Mansion: wild Pokémon on every floor tile as in Red (environment DUNGEON: no bicycle, Escape Rope / Dig).
 * Fishing (kanto_fish_151.asm): on the kit's 31 Kanto maps the rods give the kit's Pokémon (Old Rod: Magikarp Lv 5,
   Good Rod: Goldeen / Poliwag Lv 10, Super Rod: the map's four), bite 50% as Crystal's groups; elsewhere as before
   (Crystal's fishing groups).  The maps without a fishing group get one, so the rods work there.
 * Mt. Moon: the fossil maniac gives both fossils (「カセキは　ふたつとも　おまえに　やるよ！」).
 * Fighting Dojo: both Hitmonlee and Hitmonchan can be taken.
 * Celadon Mansion roof room: three Eevees (the ball stays until the third is taken).
 * Kadabra, Machoke, Graveler and Haunter evolve at Lv 37 instead of by trade (Crystal's other trade evolutions stay).
 * No Gen II Pokémon in Kanto: Crystal's Mt. Moon (after the Hall of Fame) has the kit's Mt. Moon 1F; Routes 14 and 16
   (water without the kit's fishing): Old / Good Rod only; Crystal's Vermilion port fishes as the Vermilion dock.
 * Pikachu where Red / Green / Blue have it: Viridian Forest (4% Lv 3, 1% Lv 5) and the Power Plant (10% Lv 20,
   morning and day); every kind of the kit's stays in those maps.
 * Mew (Lv 50, after the Hall of Fame, after reading the Mansion B1F diary, until caught): phase 19 already.
 * Fixes found on the way: the MOD's gift balls (Lapras, the Magikarp seller, Eevee, the Dojo) read givepoke's result
   the wrong way (0 = given), so the ball stayed and could be taken again and again; Viridian Forest had a Johto
   landmark (Ilex Forest's), so no wild Pokémon appeared there (now Route 2's).
usage: build_phase57.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import portmaps as PM
import build_phase10 as P10
from build_phase28 import JAsm

KIT = glob.glob(SC + '/kit151/*/')[0]
PB = 0x47                          # new scripts, texts, the fishing routine, the moved back picture
FIRST_FLAG = 512                   # 503-511: phase 55
G26 = 26
# kit (pokeyellow) map name -> this MOD's map
KIT_MAP = {'ROUTE_1': (13, 1), 'ROUTE_2': (23, 1), 'ROUTE_3': (14, 1), 'ROUTE_4': (7, 12), 'ROUTE_5': (25, 1),
           'ROUTE_6': (12, 1), 'ROUTE_7': (21, 1), 'ROUTE_8': (18, 1), 'ROUTE_9': (7, 13), 'ROUTE_10': (7, 14),
           'ROUTE_11': (12, 2), 'ROUTE_12': (18, 2), 'ROUTE_13': (17, 1), 'ROUTE_14': (17, 2), 'ROUTE_15': (17, 3),
           'ROUTE_16': (21, 2), 'ROUTE_17': (21, 3), 'ROUTE_18': (17, 4), 'ROUTE_19': (6, 5), 'ROUTE_20': (6, 6),
           'ROUTE_21': (6, 7), 'ROUTE_22': (23, 2), 'ROUTE_23': (16, 1), 'ROUTE_24': (7, 15), 'ROUTE_25': (7, 16),
           'PALLET_TOWN': (13, 2), 'VIRIDIAN_CITY': (23, 3), 'CERULEAN_CITY': (7, 17), 'VERMILION_CITY': (12, 3),
           'CELADON_CITY': (21, 4), 'FUCHSIA_CITY': (17, 5), 'CINNABAR_ISLAND': (6, 8),
           'VERMILION_DOCK': (G26, 40),
           'POKEMON_TOWER_3F': (G26, 16), 'POKEMON_TOWER_4F': (G26, 17), 'POKEMON_TOWER_5F': (G26, 18),
           'POKEMON_TOWER_6F': (G26, 19), 'POKEMON_TOWER_7F': (G26, 20),
           'MT_MOON_1F': (G26, 37), 'MT_MOON_B1F': (G26, 38), 'MT_MOON_B2F': (G26, 39),
           'POKEMON_MANSION_1F': (G26, 57), 'POKEMON_MANSION_2F': (G26, 58), 'POKEMON_MANSION_3F': (G26, 59),
           'POKEMON_MANSION_B1F': (G26, 60),
           'POWER_PLANT': (G26, 62),
           'SEAFOAM_ISLANDS_1F': (G26, 63), 'SEAFOAM_ISLANDS_B1F': (G26, 64), 'SEAFOAM_ISLANDS_B2F': (G26, 65),
           'SEAFOAM_ISLANDS_B3F': (G26, 66), 'SEAFOAM_ISLANDS_B4F': (G26, 67),
           'VICTORY_ROAD_1F': (G26, 68), 'VICTORY_ROAD_2F': (G26, 69), 'VICTORY_ROAD_3F': (G26, 70),
           'CERULEAN_CAVE_1F': (G26, 76), 'CERULEAN_CAVE_2F': (G26, 77), 'CERULEAN_CAVE_B1F': (G26, 78),
           'VIRIDIAN_FOREST': (G26, 84),
           'SAFARI_ZONE_CENTER': (G26, 88), 'SAFARI_ZONE_EAST': (G26, 90), 'SAFARI_ZONE_NORTH': (G26, 92),
           'SAFARI_ZONE_WEST': (G26, 94),
           'ROCK_TUNNEL_1F': (G26, 147), 'ROCK_TUNNEL_B1F': (G26, 148), 'DIGLETTS_CAVE': (G26, 149)}
KEEP = [(3, 83), (24, 1), (24, 2), (19, 1)]      # Crystal's: Tohjo Falls, Routes 26-28 (the Johto side)
CRYSTAL_MT_MOON = (3, 85)          # Crystal's Mt. Moon (after the Hall of Fame): the kit's Mt. Moon 1F
# Kanto water the kit has no fishing for: Old / Good Rod as everywhere, the Super Rod catches nothing (as in the
# Pikachu version); Crystal's Vermilion port: as the Vermilion dock next to it
EXTRA_FISH = {(17, 2): 0xFF, (21, 2): 0xFF, (15, 2): 'VERMILION_DOCK'}
PIKACHU = 25
MANSION = [(G26, 57), (G26, 58), (G26, 59), (G26, 60)]
ENV_DUNGEON = 7
KANTO_LANDMARK = 0x2F             # Pallet Town: the first Kanto landmark (IsInJohto)
# bank 0A
KANTO_GRASS = 0x7140
BACKPIC, BACKPIC_END = 0x7BCD, 0x7D05            # LZ, loaded by 0F:7C17 (ld b, 0A / ld hl, 7BCD / call 7FB8)
BACKPIC_REF = 0x3FC17
KANTO_WATER, KANTO_WATER_END = 0x7D05, 0x7DDE    # up to the swarm table
H_FISH = 0xD1F3                    # 03:51F3  farcall (phase 28: the Safari Zone's rods, then Crystal's Fish)
RANDOM = 0x2F5E
W_MAP_GROUP, W_MAP_NUMBER = 0xDC7B, 0xDC7C
MAGIKARP, GOLDEEN, POLIWAG, EEVEE, HITMONLEE, HITMONCHAN = 129, 118, 60, 133, 106, 107
DOME_FOSSIL, HELIX_FOSSIL = 0x8E, 0x8D
TRADE_EVOS = [(64, 65), (67, 68), (75, 76), (93, 94)]   # Kadabra, Machoke, Graveler, Haunter
EVOLVE_LEVEL, EVOLVE_TRADE = 1, 3


def pct(s):
    """rgbds 'N percent [+ k]' -> byte"""
    m = re.fullmatch(r'\s*(\d+)\s*percent\s*(?:\+\s*(\d+))?\s*', s)
    return int(m.group(1)) * 0xFF // 100 + int(m.group(2) or 0)


def mon(s): return PM.MON[P10.MON_ALIAS.get(s, s)]


def strip(l): return l.split(';')[0].strip()


def kit_grass():
    """the kit's grass, with Pikachu where Red / Green / Blue have it (Viridian Forest 4% Lv 3 + 1% Lv 5, as Red's
    5%; the Power Plant 10% Lv 20 in the morning and the day), keeping every kind of the kit's in the map"""
    out = kit_grass_raw()
    for name, rates, mons in out:
        if name == 'VIRIDIAN_FOREST':
            pg, pgt = mons[4], mons[5]; assert pg[1] == 16 and pgt[1] == 17
            for t in range(3):
                mons[t * 7 + 5] = (3, PIKACHU); mons[t * 7 + 6] = (5, PIKACHU)
                mons[t * 7 + 4] = pgt if t == 2 else pg               # Pidgeotto (was 4%) at night in Pidgey's slot
        if name == 'POWER_PLANT':
            for t in range(2):
                assert mons[t * 7 + 3][1] == 88; mons[t * 7 + 3] = (20, PIKACHU)   # Grimer stays at night (and on 1F-)
    return out


def kit_grass_raw():
    out = []; cur = None
    for l in open(KIT + 'kanto_grass_151.asm', encoding='utf-8'):
        t = strip(l)
        m = re.match(r'def_grass_wildmons (\w+)', t)
        if m: cur = [m.group(1), None, []]; continue
        if t == 'end_grass_wildmons':
            assert len(cur[2]) == 21, cur[0]; out.append(cur); cur = None; continue
        if cur and t.startswith('db '):
            a = [x.strip() for x in t[3:].split(',')]
            if cur[1] is None: cur[1] = [pct(x) for x in a]
            else: cur[2].append((int(a[0]), mon(a[1])))
    return out


def kit_water():
    out = []; cur = None
    for l in open(KIT + 'kanto_water_151.asm', encoding='utf-8'):
        t = strip(l)
        m = re.match(r'def_water_wildmons (\w+)', t)
        if m: cur = [m.group(1), None, []]; continue
        if t == 'end_water_wildmons':
            assert len(cur[2]) == 3, cur[0]; out.append(cur); cur = None; continue
        if cur and t.startswith('db '):
            a = [x.strip() for x in t[3:].split(',')]
            if cur[1] is None: cur[1] = pct(a[0])
            else: cur[2].append((int(a[0]), mon(a[1])))
    return out


def kit_fish():
    """-> (old, good, supers {n: [(thr, sp, lv)]}, {map: n})"""
    lab = None; tabs = {}; maps = {}
    for l in open(KIT + 'kanto_fish_151.asm', encoding='utf-8'):
        m = re.match(r';\s+(\w+)\s+FISHGROUP_KANTO151_(\d+)', l)
        if m: maps[m.group(1)] = int(m.group(2)); continue
        t = strip(l)
        m = re.match(r'\.Kanto151_(\w+):', t)
        if m: lab = m.group(1); tabs[lab] = []; continue
        if lab and t.startswith('db '):
            a = [x.strip() for x in t[3:].split(',')]
            tabs[lab].append((pct(a[0]), mon(a[1]), int(a[2])))
    sup = {int(k[5:]): v for k, v in tabs.items() if k.startswith('Super')}
    return tabs['Old'], tabs['Good'], sup, maps


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    f, n = bank_free_tail(rom, PB); sp.set_area(PB, f + 16, PB * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    G = US.get().groups()
    def hdr(g, n_): return G[g - 1] + 9 * (n_ - 1)

    # ================= the back picture out of bank 0A
    assert rom[BACKPIC_REF:BACKPIC_REF + 8] == bytes([0x06, 0x0A, 0x21, BACKPIC & 0xFF, BACKPIC >> 8, 0xCD, 0xB8, 0x7F])
    pic = bytes(rom[fo(0x0A, BACKPIC):fo(0x0A, BACKPIC_END)])
    pa = sp.put(PB, pic)
    rom[BACKPIC_REF + 1] = PB; w16(BACKPIC_REF + 3, pa)
    rom[fo(0x0A, BACKPIC):fo(0x0A, BACKPIC_END)] = bytes(BACKPIC_END - BACKPIC)
    log.append('back picture 0A:%04X -> %02X:%04X (%d bytes)' % (BACKPIC, PB, pa, len(pic)))

    # ================= grass / caves
    g0 = fo(0x0A, KANTO_GRASS)
    old = {}; o_ = g0
    while rom[o_] != 0xFF:
        old[(rom[o_], rom[o_ + 1])] = bytes(rom[o_:o_ + 47]); o_ += 47
    tab = bytearray(); seen = set()
    for name, rates, mons in kit_grass():
        mp = KIT_MAP[name]; assert mp not in seen; seen.add(mp)
        tab += bytes([*mp, *rates]) + b''.join(bytes([lv, s]) for lv, s in mons)
    for mp in KEEP:
        tab += old[mp]
    tab += tab[[i for i in range(0, len(tab), 47) if tuple(tab[i:i + 2]) == KIT_MAP['MT_MOON_1F']][0]:][:47]
    tab[-47:-45] = bytes(CRYSTAL_MT_MOON)
    tab += b'\xff'
    assert len(tab) <= fo(0x0A, BACKPIC_END) - g0, len(tab)
    rom[g0:fo(0x0A, BACKPIC_END)] = bytes(tab) + bytes(fo(0x0A, BACKPIC_END) - g0 - len(tab))
    log.append('Kanto grass: %d maps (kit %d + Crystal %d), %d bytes' % (len(seen) + len(KEEP) + 1, len(seen), len(KEEP), len(tab)))
    for mp in MANSION:
        rom[hdr(*mp) + 2] = ENV_DUNGEON
    # Viridian Forest had Crystal's Ilex Forest landmark (phase 27's header): a Johto landmark, so the wild Pokémon
    # were looked up in the Johto table (none there): Route 2's landmark
    vf, r2 = hdr(*KIT_MAP['VIRIDIAN_FOREST']), hdr(*KIT_MAP['ROUTE_2'])
    assert rom[vf + 5] < KANTO_LANDMARK <= rom[r2 + 5]
    rom[vf + 5] = rom[r2 + 5]
    for name, mp in KIT_MAP.items():
        assert rom[hdr(*mp) + 5] >= KANTO_LANDMARK, name

    # ================= surfing
    w0 = fo(0x0A, KANTO_WATER)
    oldw = {}; o_ = w0
    while rom[o_] != 0xFF:
        oldw[(rom[o_], rom[o_ + 1])] = bytes(rom[o_:o_ + 9]); o_ += 9
    assert o_ == fo(0x0A, KANTO_WATER_END) - 1
    tab = bytearray()
    for name, rate, mons in kit_water():
        tab += bytes([*KIT_MAP[name], rate]) + b''.join(bytes([lv, s]) for lv, s in mons)
    for mp in KEEP:
        if mp in oldw: tab += oldw[mp]
    tab += b'\xff'
    rom[w0:fo(0x0A, KANTO_WATER_END)] = bytes(tab) + bytes(fo(0x0A, KANTO_WATER_END) - w0 - len(tab))
    log.append('Kanto water: %d bytes' % len(tab))

    # ================= fishing: d = fishing group, e = rod (0 old, 1 good, 2 super) -> d = species (0: no bite), e = level
    oldt, good, sup, fmaps = kit_fish()
    assert all(x[1:] == (MAGIKARP, 5) for x in oldt)
    assert [x[:2] for x in good] == [(63, GOLDEEN), (127, POLIWAG), (191, GOLDEEN), (255, POLIWAG)] and all(x[2] == 10 for x in good)
    for k, v in sup.items(): assert [x[0] for x in v] == [63, 127, 191, 255], k
    prev = bytes(rom[H_FISH:H_FISH + 6]); assert prev[0] == 0x3E and prev[2] == 0x21 and prev[5] == 0xCF
    a = JAsm(sp.here(PB)); a.bank = PB
    a.label('fish')
    a.db(0xFA); a.dw(W_MAP_GROUP); a.db(0x47); a.db(0xFA); a.dw(W_MAP_NUMBER); a.db(0x4F)          # b, c = map
    a.db(0x21); a.dw('maps')
    a.label('lp'); a.db(0x2A, 0xFE, 0xFF); a.jr(0x28, 'prev')
    a.db(0xB8); a.jr(0x20, 's2'); a.db(0x2A, 0xB9); a.jr(0x20, 's1'); a.db(0x7E, 0x47); a.jr(0x18, 'found')
    a.label('s2'); a.db(0x23)
    a.label('s1'); a.db(0x23); a.jr(0x18, 'lp')
    a.label('prev'); a.raw(prev); a.db(0xC9)                                                      # as before
    a.label('found')                                                                             # b = Super Rod group
    a.db(0xCD); a.dw(RANDOM); a.db(0xFE, 0x80); a.jr(0x30, 'none')                                 # bite: 50%
    a.db(0x7B, 0xA7); a.jr(0x28, 'old'); a.db(0x3D); a.jr(0x28, 'good')
    a.db(0x78, 0xFE, 0xFF); a.jr(0x28, 'none')                                                   # no Super Rod data
    a.db(0xCD); a.dw(RANDOM); a.db(0x07, 0x07, 0xE6, 0x03, 0x87, 0x4F)                            # c = (r >> 6) * 2
    a.db(0x78, 0x87, 0x87, 0x87, 0x81, 0x5F, 0x16, 0x00, 0x21); a.dw('sup'); a.db(0x19)              # hl = sup + b * 8 + c
    a.db(0x56, 0x23, 0x5E, 0xC9)                                                                  # d = species, e = level
    a.label('old'); a.db(0x16, MAGIKARP, 0x1E, 5, 0xC9)
    a.label('good'); a.db(0xCD); a.dw(RANDOM); a.db(0x16, GOLDEEN, 0x1E, 10, 0xCB, 0x77, 0xC8, 0x16, POLIWAG, 0xC9)
    a.label('none'); a.db(0x16, 0x00, 0xC9)
    a.label('maps')
    nfix = 0
    for name, k in fmaps.items():
        mp = KIT_MAP[name]; a.db(*mp, k)
        h = hdr(*mp)
        if rom[h + 8] == 0: rom[h + 8] = 1; nfix += 1                                            # the rods work there
    for mp, k in EXTRA_FISH.items():
        a.db(*mp, fmaps[k] if isinstance(k, str) else k); assert rom[hdr(*mp) + 8]
    a.db(0xFF)
    a.label('sup')
    for k in range(len(sup)):
        for thr, s, lv in sup[k]: a.db(s, lv)
    base = a.base; blob = a.fin(); assert sp.put(PB, blob) == base
    rom[H_FISH:H_FISH + 6] = bytes([0x3E, PB, 0x21, a.labels['fish'] & 0xFF, a.labels['fish'] >> 8, 0xCF])
    log.append('fishing: %d maps, %d Super Rod groups (%02X:%04X); fishing group given to %d maps' % (len(fmaps), len(sup), PB, base, nfix))

    # ================= scripts (bank PB)
    s = Asm(sp.here(PB)); texts = {}
    # ---- Mt. Moon B2F: both fossils
    fos = {}
    for item in (DOME_FOSSIL, HELIX_FOSSIL):
        pat = bytes([0x9D, item, 1, 0x08]); o_ = rom.find(pat); assert o_ > 0 and rom.find(pat, o_ + 1) < 0
        assert rom[o_ + 6] == 0x49 and rom[o_ + 7] == 0x6D and rom[o_ + 9] == 0x00
        tgt = fo(o_ // 0x4000, r16(o_ + 10))
        assert rom[tgt] == 0x33 and rom[tgt + 3] == 0x33 and rom[tgt + 6] == 0x90
        tail = o_ + 12
        assert rom[tail] == 0x47 and rom[tail + 1] == 0x4C and rom[tail + 4:tail + 7] == bytes([0x53, 0x49, 0x6D]) and rom[tail + 8] == 0x90
        fos[item] = dict(obj=rom[o_ + 8], taken=r16(tgt + 1), flag=r16(tgt + 4), tail=tail, mine=r16(tail + 2))
    for item, other in ((DOME_FOSSIL, HELIX_FOSSIL), (HELIX_FOSSIL, DOME_FOSSIL)):
        L = 'fos%02X' % item; O = fos[other]
        s.label(L); s.checkevent(O['flag']); s.iftrue(L + 'e')
        s.opentext(); s.writetext('both'); s.waitbutton()
        s.verbosegiveitem(other, 1); s.iffalse(L + 'f'); s.closetext()
        s.disappear(O['obj']); s.setevent(O['taken']); s.setevent(O['flag'])
        s.label(L + 'e'); s.end()
        s.label(L + 'f'); s.closetext(); s.end()
    texts['both'] = encode('{00}カセキは　ふたつとも<LINE>おまえに　やるよ！') + b'\x57'
    # the maniac's line after the battle (Red: one each) -> both
    mb = 0x79
    k1 = encode('{00}ぼくと　おまえで<LINE>カセキを　1こ　ずつ　だ！<CONT>ひとり　じめは　ダメだぞ！') + b'\x57'
    o_ = rom.find(k1, mb * 0x4000, mb * 0x4000 + 0x4000); assert o_ > 0
    nt = texts['both']; assert len(nt) <= len(k1)
    rom[o_:o_ + len(k1)] = nt + bytes(len(k1) - len(nt))
    # ---- Celadon Mansion roof room: three Eevees
    pat = bytes([0x2D, EEVEE, 25, 0, 0, 0x08]); o_ = rom.find(pat); assert o_ > 0 and rom.find(pat, o_ + 1) < 0
    ev = o_ + 8; assert rom[ev] == 0x49 and rom[ev + 1] == 0x6D and rom[ev + 3] == 0x33 and rom[ev + 6] == 0x90
    eobj, egone = rom[ev + 2], r16(ev + 4)
    e1, e2 = FL.new(), FL.new()
    s.label('eevee'); s.checkevent(e1); s.iftrue('eevee2'); s.setevent(e1); s.end()
    s.label('eevee2'); s.checkevent(e2); s.iftrue('eevee3'); s.setevent(e2); s.end()
    s.label('eevee3'); s.disappear(eobj); s.setevent(egone); s.end()
    # ---- Fighting Dojo: both balls
    ndojo = 0
    for m_ in (HITMONLEE, HITMONCHAN):
        pat = bytes([0x2D, m_, 30, 0, 0, 0x08]); o_ = rom.find(pat); assert o_ > 0 and rom.find(pat, o_ + 1) < 0
        k = rom.rfind(bytes([0x31]), o_ - 40, o_)
        while not (rom[k + 3] == 0x09 and fo(o_ // 0x4000, r16(k + 4)) > o_): k = rom.rfind(bytes([0x31]), o_ - 40, k)
        assert rom[fo(o_ // 0x4000, r16(k + 4))] == 0x52                                         # jumptext (greedy)
        nxt = 0x4000 + (k + 6) % 0x4000; w16(k + 4, nxt); ndojo += 1
    # ---- texts
    for t, b in texts.items(): s.label(t); s.raw(b)
    base = s.base; blob = s.done(); assert sp.put(PB, blob) == base
    L = s.labels
    for item in (DOME_FOSSIL, HELIX_FOSSIL):
        t_ = fos[item]['tail']; l_ = L['fos%02X' % item]
        rom[t_:t_ + 9] = bytes([0x04, PB, l_ & 0xFF, l_ >> 8]) + b'\x90' * 5
    rom[ev + 1:ev + 7] = bytes([0x04, PB, L['eevee'] & 0xFF, L['eevee'] >> 8, 0x90, 0x90])
    log.append('fossils both, Eevee x3 (flags %X %X), Dojo both (%d), scripts %02X:%04X' % (e1, e2, ndojo, PB, base))

    # ================= the MOD's "givepoke / iffalse": givepoke leaves wScriptVar 0 (party), 1 (box) or 2 (no room),
    # so iffalse took the "no room" way after a Pokémon had been given (the ball stayed: Lapras, Magikarp, Eevee and
    # the Dojo's balls again and again).  checkscene / farscall (givepoke, then wScriptVar = given) / iffalse.
    g = Asm(sp.here(PB))
    g.label('fix'); g.raw(bytes([0xFA, 0xDD, 0xC2, 0xFE, 0x02, 0x3E, 0x00, 0x28, 0x01, 0x3C, 0xEA, 0xDD, 0xC2, 0xC9]))
    sites = [mm.start() for mm in re.finditer(rb'\x2d(.)(.)\x00\x00\x08', rom, re.S) if rom[mm.start():mm.start() + 6] != orig[mm.start():mm.start() + 6]]
    assert len(sites) == 5, sites
    for o_ in sites:
        l_ = 'gp%X' % o_; g.label(l_); g.raw(bytes(rom[o_:o_ + 5])); g.callasm(PB, 'fix'); g.end()
    base = g.base; blob = g.done(); assert sp.put(PB, blob) == base
    for o_ in sites:
        l_ = g.labels['gp%X' % o_]
        rom[o_:o_ + 5] = bytes([0x13, 0x01, PB, l_ & 0xFF, l_ >> 8])                            # checkscene / farscall
    log.append('givepoke results fixed at %d places' % len(sites))

    # ================= Lv 37 instead of trade
    for frm, to in TRADE_EVOS:
        pat = bytes([EVOLVE_TRADE, 0xFF, to, 0]); o_ = rom.find(pat, 0x40000, 0x44000)
        assert o_ > 0 and rom.find(pat, o_ + 1, 0x44000) < 0
        rom[o_:o_ + 2] = bytes([EVOLVE_LEVEL, 37])
    log.append('Lv 37 evolutions: Kadabra, Machoke, Graveler, Haunter')

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    print('\n'.join(log))


if __name__ == '__main__':
    main()
