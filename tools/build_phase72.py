#!/usr/bin/env python3
"""Phase 72: what the playthrough check (new game -> Pewter Gym, walking, compared with Red) found:
 * Red's room (Crystal's RedsHouse2F): the PC is the player's PC (Red: his own PC with a Potion; Crystal's room PC script
   PlayersHouse2F's, special PlayersHousePC) instead of "it hasn't been used for a long time"; the game console reads
   Red's line ("<PLAYER>は ファミコンを してる！ …… …… よし！ そろそろ でかけよう！").
 * Oak's lab: the PC's e-mail is Red's (the Pokémon League's invitation; Crystal's showed Elm's mail), read facing up
   from (0, 2) / (1, 2) as in Red.
 * Red's house 1F: the TV shows Red's film (from the front; "みえない……" from the side) instead of Crystal's line.
usage: build_phase72.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
from evedit import MapEvents
import redtexts as RT
import redmap as RM

BANK = 0x62
BGEVENT_READ, BGEVENT_UP = 0, 1
RED_SNES_TEXT = 0x5F8DF            # JP Red
RED_TV_TEXT, RED_TV_SIDE = 0x48293, 0x482CE
VAR_FACING = 0x09


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    f, n = bank_free_tail(rom, BANK); sp.set_area(BANK, f + 1, BANK * 0x4000 + 0x4000)
    log = []

    # ================= Red's room: the player's PC, Red's console line
    ph = MapEvents(rom, 'PlayersHouse2F')
    pc = [r for y, x, t, r in ph.bgs if (x, y) == (2, 1) and t == BGEVENT_UP]; assert len(pc) == 1 and pc[0][0] == 'far'
    q = fo(pc[0][1], pc[0][2]); assert rom[q:q + 4] == bytes([0x47, 0x0F, 0x1D, 0x00])     # opentext / special PlayersHousePC
    me = MapEvents(rom, 'RedsHouse2F')
    assert sorted((x, y) for y, x, t, r in me.bgs) == [(0, 1), (3, 5)]
    snes = RT.raw(RED_SNES_TEXT) + b'\x57'; assert RT.R[RED_SNES_TEXT + len(snes) - 1] == 0x57
    assert encode('ファミコンを') in snes
    a = Asm(sp.here(BANK)); a.bank = BANK
    a.label('pc'); a.farsjump(pc[0][1], pc[0][2])
    a.label('snes'); a.jumptext('snes_t')
    a.label('snes_t'); a.raw(snes)
    me.bgs = [(1, 0, BGEVENT_UP, 'pc'), (5, 3, BGEVENT_READ, 'snes')]
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    me.install(a)
    log.append('RedsHouse2F: events %X:%04X (%d bytes)' % (BANK, base, len(blob)))

    # ================= Red's house 1F: the TV
    me = MapEvents(rom, 'RedsHouse1F')
    tv = [i for i, (y, x, t, r) in enumerate(me.bgs) if (x, y) == (2, 1)]; assert len(tv) == 1
    a = Asm(sp.here(BANK)); a.bank = BANK
    a.label('tv'); a.db(0x1C, VAR_FACING); a.ifnotequal(1, 'tv_side'); a.jumptext('tv_t')
    a.label('tv_side'); a.jumptext('tv_s')
    a.label('tv_t'); a.raw(RT.raw(RED_TV_TEXT) + b'\x57')
    a.label('tv_s'); a.raw(RT.raw(RED_TV_SIDE) + b'\x57')
    y, x, t, r = me.bgs[tv[0]]; me.bgs[tv[0]] = (y, x, t, 'tv')
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    me.install(a)
    log.append('RedsHouse1F: events %X:%04X (%d bytes)' % (BANK, base, len(blob)))

    # ================= Oak's lab: Red's e-mail
    me = MapEvents(rom, 'OaksLab')
    pcs = [i for i, (y, x, t, r) in enumerate(me.bgs) if (x, y) == (0, 1)]; assert len(pcs) == 1
    assert not [1 for y, x, t, r in me.bgs if (x, y) == (1, 1)]
    a = Asm(sp.here(BANK)); a.bank = BANK
    a.label('mail'); a.jumptext('mail_t')
    a.label('mail_t'); a.raw(RM.crystal_text(7, 0x7F27))
    del me.bgs[pcs[0]]; me.bgs += [(1, 0, BGEVENT_UP, 'mail'), (1, 1, BGEVENT_UP, 'mail')]
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    me.install(a)
    log.append('OaksLab: events %X:%04X (%d bytes)' % (BANK, base, len(blob)))

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
