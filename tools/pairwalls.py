"""Red's tile-pair collisions (TilePairCollisionsLand / TilePairCollisionsWater: the player may not cross between two
given tiles; Red uses them for differences in elevation) as Crystal side walls.

Crystal collision is per block quad and shared by every map of the tileset, while a crossing is forbidden or not
depending on the neighbouring block.  So every block that needs walls at a given place gets a copy of its own (same
tiles, other collision), and the map uses that copy there.  The same copies also carry per-place collision overrides
(holes and the like).

variants(ts, meta, coll, maps, pairs, overrides) -> (meta, coll, {mapname: new blk})
  meta/coll: the tileset's current metatiles / collision (bytes); new blocks are appended
  maps: {name: MapPort}
  pairs: [(tile1, tile2)]
  overrides: {name: {(x, y): collision}}"""
from portlib import COLL_FLOOR, COLL_WATER

DIRS = {'R': (1, 0), 'L': (-1, 0), 'U': (0, -1), 'D': (0, 1)}
OPP = {'R': 'L', 'L': 'R', 'U': 'D', 'D': 'U'}
WALL = {frozenset('R'): 0xB0, frozenset('L'): 0xB1, frozenset('U'): 0xB2, frozenset('D'): 0xB3,
        frozenset('DR'): 0xB4, frozenset('DL'): 0xB5, frozenset('UR'): 0xB6, frozenset('UL'): 0xB7}
BUOY = 0x10                                   # COLL_*_BUOY = water with a side wall = COLL_*_WALL + 0x10


def place_walls(ts, mp, coll, pairs, water_tiles):
    """{(x, y): set of wall directions} for one map"""
    P = {frozenset(p) for p in pairs}
    common = set.intersection(*(set(p) for p in pairs)); prefer = min(common) if common else None
    walk = set(ts.passable) | set(water_tiles)
    W, H = mp.w * 2, mp.h * 2
    tile = lambda x, y: ts.quad_tile(*mp.block_at(x, y))
    walls = {}
    for y in range(H):
        for x in range(W):
            t = tile(x, y)
            if t not in walk: continue
            for d in ('R', 'D'):
                dx, dy = DIRS[d]; nx, ny = x + dx, y + dy
                if nx >= W or ny >= H: continue
                t2 = tile(nx, ny)
                if t2 not in walk or frozenset((t, t2)) not in P: continue
                # the wall goes on the side of the tile all the pairs share (the raised ground), if it can
                a, b = ((x, y), d), ((nx, ny), OPP[d])
                first = a if t == prefer else b
                second = b if first is a else a
                for (p, dd) in (first, second):
                    s = walls.setdefault(p, set()) | {dd}
                    if frozenset(s) in WALL and coll_ok(ts, mp, coll, p):
                        walls[p] = s; break
                else:
                    raise AssertionError('%s: cannot wall %r' % (mp.name, (a, b)))
    return walls


def coll_ok(ts, mp, coll, p):
    b, q = mp.block_at(*p)
    return coll[4 * b + q] in (COLL_FLOOR, COLL_WATER)


def variants(ts, meta, coll, maps, pairs, overrides=None, water_tiles=(0x14,)):
    meta = bytearray(meta); coll = bytearray(coll); nb = len(coll) // 4
    overrides = overrides or {}
    cache = {}; out = {}
    for name, mp in maps.items():
        walls = place_walls(ts, mp, coll, pairs, water_tiles)
        ov = dict(overrides.get(name, {}))
        for p, ds in walls.items():
            b, q = mp.block_at(*p)
            base = coll[4 * b + q]
            ov[p] = WALL[frozenset(ds)] + (BUOY if base == COLL_WATER else 0)
        blk = bytearray(mp.blk)
        for by in range(mp.h):
            for bx in range(mp.w):
                b = blk[by * mp.w + bx]
                c = list(coll[4 * b:4 * b + 4])
                for q in range(4):
                    p = (2 * bx + q % 2, 2 * by + q // 2)
                    if p in ov: c[q] = ov[p]
                c = tuple(c)
                if c == tuple(coll[4 * b:4 * b + 4]): continue
                k = (b, c)
                if k not in cache:
                    cache[k] = nb + len(cache)
                    assert cache[k] < 256, 'too many blocks'
                    meta += meta[16 * b:16 * b + 16]
                    coll += bytes(c)
                blk[by * mp.w + bx] = cache[k]
        out[name] = bytes(blk)
    return bytes(meta), bytes(coll), out
