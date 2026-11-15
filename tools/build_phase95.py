#!/usr/bin/env python3
"""Phase 95: walking from Pallet Town to Route 1 stopped for about a second at the edge (and the same on other map
connections).  Phase 89's cause, on every map group: the 23-entry outdoor sprite set plus the follower does not fit
in the first sprite table, a walking sprite of the next map lands in the second table, and the follower code
(kit Fw_MapSpritesOK -> Fw_RefreshConn / Fw_RefreshAll) reloads every sprite at the connection.
Same fix as phase 89 for all the other groups: entries that no outdoor map of the group(s) using the list needs are
replaced by a copy of one that is needed (AddSpriteGFX skips duplicates); a needed sprite missing from the list
(the MOD's new sprites $67-$EF) takes such a slot.
usage: build_phase95.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import build_phase17 as P17
from build_phase17 import US, attrs, parse_events

DONE = (12, 18, 21, 25)            # phase 89


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read()); log = []
    u = US.get(); G = u.groups(); tab = fo(*P17.OUTDOOR_SPRITES_PTR)
    ng = len(G) - 1
    def lp_of(gi): return fo(5, rom[tab + 2 * gi] | rom[tab + 2 * gi + 1] << 8)
    def used_of(gi):
        used = set()
        for k in range((G[gi + 1] - G[gi]) // 9):
            hdr = G[gi] + 9 * k
            if rom[hdr + 2] not in (1, 2): continue
            a = attrs(rom, hdr); ev = parse_events(rom, a['scbank'], a['events'])
            used |= {o[0] for _, o in ev['objs']}
        return used
    lists = {}
    for gi in range(ng): lists.setdefault(lp_of(gi), []).append(gi)
    for lp, gis in sorted(lists.items()):
        if any(gi + 1 in DONE for gi in gis): continue
        used = set().union(*(used_of(gi) for gi in gis))
        lst = list(rom[lp:lp + 23])
        keep = [x for x in lst if x in used]
        if not keep: continue                          # no outdoor maps / objects: leave it
        miss = sorted(x for x in used - set(lst) if 0x67 <= x < 0xF0)
        new = []
        for x in lst:
            if x in used: new.append(x)
            elif miss: new.append(miss.pop(0))
            else: new.append(keep[0])
        assert not miss, (gis, miss)
        if new != lst:
            rom[lp:lp + 23] = bytes(new)
            log.append('groups %s: %s -> %s' % ([g + 1 for g in gis], bytes(lst).hex(' '), bytes(new).hex(' ')))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
