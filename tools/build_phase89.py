#!/usr/bin/env python3
"""Phase 89: leaving a building into Vermilion City / Lavender Town / Celadon / Saffron City took about a second longer than
elsewhere.  Those map groups' outdoor sprite sets (23 entries) plus the follower no longer fit in VRAM, so the
follower code (kit Fw_FixOverflow / Fw_RefreshAll) dropped entries and loaded every sprite again with the screen on
(2 frames each).  Entries that no outdoor map of the group uses are replaced by a copy of an entry that is used
(AddSpriteGFX skips duplicates), so the set fits and the extra reload never happens.
usage: build_phase89.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import build_phase17 as P17
from build_phase17 import US, attrs, parse_events

GROUPS = (12, 18, 21, 25)          # Vermilion, Lavender, Celadon, Saffron (outdoor maps using the MOD's new sprites)


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read()); log = []
    u = US.get(); G = u.groups(); tab = fo(*P17.OUTDOOR_SPRITES_PTR)
    for g in GROUPS:
        gi = g - 1
        lp = fo(5, rom[tab + 2 * gi] | rom[tab + 2 * gi + 1] << 8)
        lst = list(rom[lp:lp + 23]); used = set()
        for k in range((G[gi + 1] - G[gi]) // 9):
            hdr = G[gi] + 9 * k
            if rom[hdr + 2] not in (1, 2): continue
            a = attrs(rom, hdr); ev = parse_events(rom, a['scbank'], a['events'])
            used |= {o[0] for _, o in ev['objs']}
        keep = [x for x in lst if x in used]; assert keep
        # the MOD's new sprites ($67-$EF, phases 14/56/58) were never in the set: a map using one (Lavender's,
        # Vermilion's Officer Jenny, Saffron's) made Fw_MapSpritesOK fail -> Fw_RefreshAll (the slow reload)
        miss = sorted(x for x in used - set(lst) if 0x67 <= x < 0xF0)
        new = []
        for x in lst:
            if x in used: new.append(x)
            elif miss: new.append(miss.pop(0))
            else: new.append(keep[0])
        assert not miss, (g, miss)
        # another group must not share this list
        assert sum(1 for j in range(len(G) - 1) if fo(5, rom[tab + 2 * j] | rom[tab + 2 * j + 1] << 8) == lp) == 1
        rom[lp:lp + 23] = bytes(new)
        log.append('group %d: %s -> %s' % (g, bytes(lst).hex(' '), bytes(new).hex(' ')))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
