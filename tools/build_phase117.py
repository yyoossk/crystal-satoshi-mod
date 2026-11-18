#!/usr/bin/env python3
"""Phase 117: the rival in Mt. Moon after the Johto League (found by the post-game check of 2026-11-18).
 The MOD's first base (phases 1-9) had turned Crystal's Mt. Moon rival off (scene 0 -> the no-op scene, the rival's
 object hidden by an always-set flag), so the rival never appeared there after the Johto League, and with no Mt. Moon
 battle (EVENT_BEAT_RIVAL_IN_MT_MOON) his Indigo Plateau rematches (Monday / Wednesday) never came either.
 Crystal's Mt. Moon (map 3:85) is reached in this MOD after the Kanto Hall of Fame, before the Johto League too, so:
 * scene 0: after the Johto Elite Four (EVENT_BEAT_ELITE_FOUR) Crystal's own battle script (sdefer), else nothing;
 * the rival's object uses Crystal's flag (EVENT_MT_MOON_RIVAL) again, and a MAPCALLBACK_OBJECTS hides him before the
   Johto League and shows him after it until he is beaten (Crystal's script hides him and sets the beaten flag).
usage: build_phase117.py IN.gbc OUT.gbc OUT.ips
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

MAP = (3, 85)
EV_BEAT_E4, EV_MT_MOON_RIVAL, EV_BEAT_RIVAL_MT_MOON, EV_ALWAYS = 0x44, 0x77A, 0x319, 0x36
BATTLE = 0x6BED                                   # Crystal's MountMoonRivalBattleScript (JP 1F:6BED)
NOOP = 0x6BEC
MGP = 0x94000


def header(rom, g, m):
    G = rom[MGP + 2 * (g - 1)] | rom[MGP + 2 * (g - 1) + 1] << 8
    return fo(0x25, G) + 9 * (m - 1)


def main():
    src, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src, 'rb').read())
    at = attrs(rom, header(rom, *MAP))
    B = at['scbank']; so = fo(B, at['scripts'])
    assert B == 0x1F and rom[so] == 2 and rom[so + 9] == 0, rom[so:so + 10].hex()
    assert (rom[so + 1] | rom[so + 2] << 8) == NOOP and (rom[so + 5] | rom[so + 6] << 8) == NOOP
    assert rom[fo(B, BATTLE) - 5:fo(B, BATTLE)] == bytes([0x8C, 0xED, 0x6B, 0x90, 0x90])     # Crystal's scene 0 / noop
    # the rival's object: Crystal's flag again
    ev = parse_events(rom, at['scbank'], at['events'])
    (oo, ob), = [(o, b) for o, b in ev['objs'] if b[0] == 4]                                  # SPRITE_RIVAL
    assert (ob[11] | ob[12] << 8) == EV_ALWAYS, ob.hex()
    rom[oo + 11] = EV_MT_MOON_RIVAL & 0xFF; rom[oo + 12] = EV_MT_MOON_RIVAL >> 8
    o = bank_free_tail(rom, B)[0] + 16
    base = 0x4000 + (o - B * 0x4000)
    a = Asm(base)
    a.label('hdr'); a.db(2); a.dw('scene0'); a.dw(0); a.dw(NOOP); a.dw(0)
    a.db(1); a.db(2); a.dw('cb_obj')                                                         # MAPCALLBACK_OBJECTS
    a.label('scene0'); a.checkevent(EV_BEAT_E4); a.iffalse('s0_end'); a.db(0x8C); a.dw(BATTLE)   # sdefer
    a.label('s0_end'); a.end()
    a.label('cb_obj')
    a.checkevent(EV_BEAT_E4); a.iffalse('hide')
    a.checkevent(EV_BEAT_RIVAL_MT_MOON); a.iftrue('hide')
    a.clearevent(EV_MT_MOON_RIVAL); a.endcallback()
    a.label('hide'); a.setevent(EV_MT_MOON_RIVAL); a.endcallback()
    blob = a.done()
    assert o + len(blob) <= (B + 1) * 0x4000 and not any(rom[o:o + len(blob)])
    rom[o:o + len(blob)] = blob
    p = at['attr_off'] + 7; rom[p] = a.labels['hdr'] & 0xFF; rom[p + 1] = a.labels['hdr'] >> 8
    print('Mt. Moon rival: scripts %02X:%04X (%d bytes)' % (B, base, len(blob)))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)


if __name__ == '__main__':
    main()
