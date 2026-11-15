#!/usr/bin/env python3
"""Phase 103: Jessie & James (ムサシとコジロウ) no longer vanish all at once after their battle.
As in the Pikachu version (pokeyellow MtMoonB2FScript14 ...: GBFadeOutToBlack / HideObject x2 / UpdateSprites /
GBFadeInFromBlack): after their last line the screen fades to black, they are removed, and it fades back in
(Crystal's way: special FadeOutToBlack / ReloadSpritesNoPalettes / disappear / pause / special FadeInFromBlack, as in
Crystal's Radio Tower 5F / Route 24 Rockets).  In Kanto (phases 11/12/14/15) the encounter music plays during the
fade and the map music comes back, as the Pikachu version plays its jingle then the default music.
Every J&J battle script ends with: loadtrainer JJ,n / startbattle / reloadmapafterbattle / opentext / writetext /
waitbutton / closetext / disappear a / disappear b / setevent f / end.  The disappear ... setevent part (7 bytes)
becomes a farsjump to the new script (in the same bank, or another one with room) (the `end` stays where it is: other branches jump to it).
usage: build_phase103.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

JJ = 0x48
SP_FADEOUT, SP_FADEIN, SP_RELOADSPR = 48, 50, 51
MUSIC_JJ = 0x39                    # the MOD's Jessie & James encounter music (phases 11/12/14/15)
KANTO_BANKS = (0x79, 0x7A, 0x7B)   # phases 11/12/14/15; Johto (phase 48): bank 5B


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read()); log = []
    pat = re.compile(rb'\x5d\x48.\x5e\x5f\x47\x4c..\x53\x49\x6d(.)\x6d(.)\x33(..)\x90', re.S)
    hits = []
    for b in range(0x40, len(rom) // 0x4000):
        s = fo(b, 0x4000)
        for m in pat.finditer(rom, s, s + 0x4000):
            hits.append((b, m))
    assert len(hits) == 7, [(hex(b), hex(m.start())) for b, m in hits]
    for b, m in hits:
        o1, o2, ev = m.group(1)[0], m.group(2)[0], m.group(3)
        kanto = b in KANTO_BANKS
        code = bytearray()
        if kanto: code += bytes([0x7E, MUSIC_JJ, 0x00])                            # playmusic
        code += bytes([0x0F, SP_FADEOUT, 0, 0x0F, SP_RELOADSPR, 0,                  # special FadeOutToBlack / ReloadSpritesNoPalettes
                       0x6D, o1, 0x6D, o2, 0x8A, 15,                                # disappear x2 / pause 15
                       0x0F, SP_FADEIN, 0, 0x33]) + ev                             # special FadeInFromBlack / setevent
        if kanto: code += b'\x81'                                                   # playmapmusic
        code += b'\x90'                                                             # end
        cb = b                                                                      # the map's script bank, or one with room
        f, n = bank_free_tail(rom, cb)
        if n < len(code) + 16:
            cb = next(x for x in list(range(0x40, 0x80)) + list(range(0x80, len(rom) // 0x4000))
                      if bank_free_tail(rom, x)[1] >= len(code) + 64)
            f, n = bank_free_tail(rom, cb)
        f += 4
        a = 0x4000 + f % 0x4000
        rom[f:f + len(code)] = code
        d = m.start(1) - 1                                                          # the first disappear
        rom[d:d + 7] = bytes([0x04, cb, a & 0xFF, a >> 8, 0x00, 0x00, 0x00])        # farsjump (rest unreachable)
        log.append('%02X:%04X J&J exit -> %02X:%04X (%s)' % (b, 0x4000 + d % 0x4000, cb, a, 'Kanto' if kanto else 'Johto'))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
