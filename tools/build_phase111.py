#!/usr/bin/env python3
"""Phase 111: gates (2026-11-16 report 「ゲートの判定がおかしい」).
 * Red's two-tile doorways (the Viridian Forest gates, Route 2's gate, the route gates of Routes 6, 7, 16, Celadon's
   building) have a warp on each tile, but in Red only one of the two tiles is walkable: the other is a wall tile
   (the doorway graphics are one tile wide).  The port gave every warp a warp collision, so the player could step
   into the wall beside the door (and had to press the direction once more to leave), while the real door tile
   warped at once.
   Now a Red warp whose tile is not walkable in Red, next to a walkable warp to the same map, is a wall again
   (its block quadrant's collision -> $07), as in Red.  Only quadrants used nowhere else are changed.
usage: build_phase111.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'play'))
from lib import *
from portlib import *
import portmaps as PM

TSN = {37: 'Cavern', 33: 'Cemetery', 45: 'Club', 52: 'Dojo', 34: 'Facility', 49: 'Forest', 48: 'ForestGate', 47: 'Gate',
       44: 'House', 36: 'Interior', 42: 'Lab', 35: 'Lobby', 50: 'Mansion', 46: 'Museum', 40: 'Overworld', 43: 'Plateau',
       41: 'Pokecenter', 38: 'Ship', 39: 'ShipPort', 51: 'Underground'}     # this MOD's tileset ids of Red's tilesets
WALL = 0x07


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    from mapdb import DB
    db = DB(src_rom)
    TSO = PM.Tilesets(rom, Space(rom))
    PAS = {n: set(gen1_coll(n)) for n in set(TSN.values())}
    log = []

    def lay(k):
        m = db.maps[k]; a = attrs(rom, m['hdr']); ts = rom[m['hdr'] + 1]
        e = TSO.entry(ts); mo = fo(e[3], e[4] | e[5] << 8)
        bo = a['blkbank'] * 0x4000 + a['blk'] - 0x4000
        return m, a, ts, mo, bo
    def cell(k, x, y):
        m, a, ts, mo, bo = lay(k)
        if not (0 <= x < a['w'] * 2 and 0 <= y < a['h'] * 2): return None
        b = rom[bo + (y // 2) * a['w'] + x // 2]; q = (y % 2) * 2 + x % 2
        tile = rom[mo + 16 * b + (2 * (q // 2) + 1) * 4 + 2 * (q % 2)]      # the quadrant's lower-left tile (as Red's)
        return dict(blk=b, q=q, ts=ts, tile=tile, coll=rom[TSO.coll_off(ts) + 4 * b + q])

    targets = {}
    for k in sorted(db.maps):
        ts = rom[db.maps[k]['hdr'] + 1]
        if ts not in TSN: continue
        pas = PAS[TSN[ts]]; W = db.warps(k)
        for w in W:
            c = cell(k, w[0], w[1])
            if c is None or c['tile'] in pas or not (0x70 <= c['coll'] <= 0x7F): continue
            mate = [v for v in W if (v[3], v[4]) == (w[3], w[4]) and abs(v[0] - w[0]) + abs(v[1] - w[1]) == 1]
            mate = [v for v in mate if (cell(k, v[0], v[1]) or {}).get('tile') in pas]
            if not mate: log.append('kept (no walkable twin): %s %s' % (k, w[:2])); continue
            targets.setdefault((c['ts'], c['blk'], c['q']), []).append((k, w[0], w[1]))
    for (ts, blk, q), uses in sorted(targets.items()):
        ok = set(uses); bad = []
        for k2, m2 in db.maps.items():
            if rom[m2['hdr'] + 1] != ts: continue
            a2 = attrs(rom, m2['hdr']); b3 = a2['blkbank'] * 0x4000 + a2['blk'] - 0x4000
            for i in range(a2['w'] * a2['h']):
                if rom[b3 + i] == blk:
                    xx, yy = (i % a2['w']) * 2 + q % 2, (i // a2['w']) * 2 + q // 2
                    if (k2, xx, yy) not in ok: bad.append((k2, xx, yy))
        if bad: log.append('NOT changed (block quadrant used elsewhere): ts %d blk %02X q %d %s %s' % (ts, blk, q, uses, bad[:4])); continue
        o = TSO.coll_off(ts) + 4 * blk + q
        log.append('wall beside a door: ts %d blk %02X q %d ($%02X -> $07) %s' % (ts, blk, q, rom[o], uses))
        rom[o] = WALL

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
