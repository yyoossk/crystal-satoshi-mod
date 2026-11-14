#!/usr/bin/env python3
"""Phase 86: the Magnet Train runs after the Johto League; Saffron City's station and Crystal's Copycat.
 In Crystal the train starts once the Power Plant's machine part is returned (EVENT_RETURNED_MACHINE_PART /
 EVENT_RESTORED_POWER_TO_KANTO), and the Copycat gives the rail PASS for her lost doll (the Pokémon Fan Club in
 Vermilion has it).  This MOD's Kanto is Red's: there is no machine part to return, and Red's Saffron City has no
 station, so the train never ran ("the train doesn't come!") and Saffron's station could not be entered.
 * After the Johto Hall of Fame (Lance's room, with all eight Johto badges) both events are set: the train runs, the
   Copycat / Fan Club / Kanto towns go on as in Crystal after the machine part.
 * Saffron City: the house right of Red's Copycat house gets a door; it is the Magnet Train station's entrance.
 * The Copycat: once the train runs she talks as in Crystal (her lost Clefairy doll, which the Fan Club in
   Vermilion has; the rail PASS for it).  Before that: Red's Copycat (Poké Doll -> TM Mimic), as in the Kanto story.
usage: build_phase86.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import Space
from evedit import MapEvents

EV_MACHINE_PART, EV_POWER = 0xC9, 0xCD
ENGINE_RISINGBADGE = 0x22
W_WARP_COUNT, W_WARPS_PTR = 0xDBC1, 0xDBC2      # wCurMapWarpCount / wCurMapWarpsPointer
SAFFRON_BLK = (0x6B, 0x7586); SAFFRON_W = 20
DOOR_BLOCKS = (0xAC, 0x3D)                       # Red's Copycat house front (its door: the left block's bottom-right)
STATION_HOUSE = (5, 2)                           # block (x, y): the house right of the Copycat's
STATION_DOOR = (11, 5)
SAFFRON, STATION, COPYCAT_1F = (25, 2), (25, 9), (25, 11)
HOF_HOOK = bytes([0x68, 0x00, 0xB4, 0x72, 0x14, 0x01, 0x8A, 0x0F])   # applymovement PLAYER ; setscene 1 ; pause 15
MAPCALLBACK_NEWMAP = 5
CRYSTAL_COPYCAT = (0x16, 0x7949)


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    BANKS = []
    for b in (0x63, 0x5B, 0x6F, 0x71, 0x7B):
        f, n = bank_free_tail(rom, b)
        if n > 64: sp.set_area(b, f + 1, b * 0x4000 + 0x4000); BANKS.append(b)
    log = []
    # ---- the Johto Hall of Fame sets the "machine part returned" events
    seg = bytes(rom[0x1D * 0x4000:0x1E * 0x4000]); i = seg.find(HOF_HOOK); assert i > 0 and seg.count(HOF_HOOK) == 1
    hook = 0x1D * 0x4000 + i + 4
    BANK = max(BANKS, key=lambda b: sp.cur[b][1] - sp.cur[b][0])
    a = Asm(sp.here(BANK)); a.bank = BANK
    a.label('hof'); a.db(0x14, 0x01, 0x8A, 0x0F)                          # setscene 1 ; pause 15 (moved)
    a.checkflag(ENGINE_RISINGBADGE); a.iffalse('hof_end')
    a.setevent(EV_MACHINE_PART); a.setevent(EV_POWER)
    a.label('hof_end'); a.end()
    # ---- Saffron City: the station door and the Copycat door
    blk = fo(*SAFFRON_BLK)
    bx, by = STATION_HOUSE; o = blk + by * SAFFRON_W + bx
    assert rom[o:o + 2] == bytes([0x10, 0xAD]), rom[o:o + 2].hex()
    assert rom[blk + by * SAFFRON_W + 3:blk + by * SAFFRON_W + 5] == bytes(DOOR_BLOCKS)
    rom[o:o + 2] = bytes(DOOR_BLOCKS)
    me = MapEvents(rom, 'SaffronCity')
    assert me.warps[0][:2] == bytes([5, 7]) and len(me.warps) == 8
    me.warps.append(bytes([STATION_DOOR[1], STATION_DOOR[0], 1, STATION[0], STATION[1]]))
    station_idx = len(me.warps)
    alt = [bytes(w) for w in me.warps]; alt[0] = bytes([5, 7, 1, COPYCAT_1F[0], COPYCAT_1F[1]])
    old = [i for i, (t, r) in enumerate(me.callbacks) if t == MAPCALLBACK_NEWMAP]
    assert len(old) <= 1
    a.label('saf_cb'); a.checkevent(EV_MACHINE_PART); a.iffalse('saf_end')
    a.callasm(BANK, 'saf_asm')
    a.label('saf_end')
    if old:                                                               # then Saffron's own new-map callback
        r = me.callbacks[old[0]][1]; assert r[0] == 'far'; a.farsjump(r[1], r[2])
    else: a.endcallback()
    a.label('saf_asm')
    a.db(0x21); a.dw('saf_warps')                                         # ld hl, alt table
    a.db(0x7D, 0xEA, W_WARPS_PTR & 0xFF, W_WARPS_PTR >> 8, 0x7C, 0xEA, (W_WARPS_PTR + 1) & 0xFF, (W_WARPS_PTR + 1) >> 8, 0xC9)
    a.label('saf_warps')
    for w in alt: a.raw(w)
    if old: me.callbacks[old[0]] = (MAPCALLBACK_NEWMAP, 'saf_cb')
    else: me.callbacks.append((MAPCALLBACK_NEWMAP, 'saf_cb'))
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    me.install(a)
    rom[hook:hook + 4] = bytes([0x01, BANK, a.labels['hof'] & 0xFF, a.labels['hof'] >> 8])  # farscall
    # the station's exits -> the new door
    st = MapEvents(rom, 'SaffronMagnetTrainStation'); ws = parse_events(rom, st.sb, st.a['events'])['warps']
    n = 0
    for off, w in ws:
        if (w[3], w[4]) == SAFFRON: rom[off + 2] = station_idx; n += 1
    assert n == 2, n
    # the Copycat (this MOD's house is Red's: Poké Doll -> TM Mimic): once the train runs, Crystal's Copycat script
    # (lost doll -> the rail PASS; she is the house's first object, as in Crystal)
    c2 = MapEvents(rom, 'CopycatsHouse2F'); ev = parse_events(rom, c2.sb, c2.a['events'])
    off, ob = ev['objs'][0]; red = ob[9] | ob[10] << 8
    assert rom[fo(c2.sb, red)] == 0x6A and rom[fo(*CRYSTAL_COPYCAT):fo(*CRYSTAL_COPYCAT) + 5] == bytes([0x6A, 0x31, 0xD1, 0x00, 0x09])
    f, n = bank_free_tail(rom, c2.sb); sp.set_area(c2.sb, f + 1, c2.sb * 0x4000 + 0x4000)
    c = Asm(sp.here(c2.sb)); c.bank = c2.sb
    c.label('cc'); c.checkevent(EV_MACHINE_PART); c.iffalse('cc_red'); c.farsjump(*CRYSTAL_COPYCAT)
    c.label('cc_red'); c.farsjump(c2.sb, red)
    cb = c.base; assert sp.put(c2.sb, c.done()) == cb
    rom[off + 9] = cb & 0xFF; rom[off + 10] = cb >> 8
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('Hall of Fame hook %02X:%04X; Saffron events %02X:%04X (station door %s = warp %d)' %
          (BANK, a.labels['hof'], BANK, base, STATION_DOOR, station_idx))


if __name__ == '__main__':
    main()
