"""Translate map blocks between Crystal's Kanto tileset and the Gen I overworld tileset (Pikachu full-color hack), so
that a map on one tileset can show its neighbour's edge (connection strip) drawn with its own tileset.
Each block is matched to the block of the other tileset that walks the same way (floor / wall / water, per quarter)
and looks the most alike (colours of the rendered 16x16 picture)."""
import re
from lib import *
from portlib import COLL_FLOOR, COLL_WALL, COLL_WATER, COLL_TALL_GRASS

KANTO_TS = 3
CPAL = ['GRAY', 'RED', 'GREEN', 'WATER', 'YELLOW', 'BROWN', 'ROOF', 'TEXT']


def tiles2bpp(data):
    out = []
    for t in range(len(data) // 16):
        px = []
        for r in range(8):
            lo, hi = data[16 * t + 2 * r], data[16 * t + 2 * r + 1]
            px.append([((lo >> (7 - c)) & 1) | (((hi >> (7 - c)) & 1) << 1) for c in range(8)])
        out.append(px)
    return out


def walk_class(c):
    if c in (COLL_FLOOR, COLL_TALL_GRASS, 0x14) or 0x70 <= c <= 0x7F: return 'P'
    if 0x20 <= c <= 0x2F or c in (0x33, 0x32, 0x34, 0x35): return 'S'
    return 'W'


class Side:
    def __init__(s, meta, coll, tiles, tile_pal, pals):
        s.meta = meta; s.coll = coll; s.n = len(coll) // 4
        s.img = [s.render(b, tiles, tile_pal, pals) for b in range(s.n)]
        s.cls = [tuple(walk_class(coll[4 * b + q]) for q in range(4)) for b in range(s.n)]

    def render(s, b, tiles, tile_pal, pals):
        out = []
        for i in range(16):
            t = s.meta[16 * b + i]
            if t >= len(tiles): t = 0
            p = pals[tile_pal[t] & 7]
            for row in tiles[t]:
                out.extend(p[v] for v in row)
        return out


def crystal_side(rom, TS):
    e = TS.entry(KANTO_TS)
    mo, co = fo(e[3], e[4] | e[5] << 8), fo(e[6], e[7] | e[8] << 8)
    meta = bytes(rom[mo:mo + 16 * 128]); coll = bytes(rom[co:co + 4 * 128])
    tiles = tiles2bpp(open(PC + '/gfx/tilesets/kanto.2bpp', 'rb').read())
    names = []
    for l in open(PC + '/gfx/tilesets/kanto_palette_map.asm'):
        m = re.match(r'\s*tilepal 0,(.*)', l)
        if m: names += [x.strip() for x in m.group(1).split(',')]
    tile_pal = [CPAL.index(n) for n in names[:len(tiles)]]
    txt = open(PC + '/gfx/tilesets/bg_tiles.pal').read()
    day = txt.split('; day')[1].split('; nite')[0]
    pals = []
    for m in re.finditer(r'RGB ([\d, ]+);', day):
        v = [int(x) for x in m.group(1).replace(' ', '').split(',')]
        pals.append([(v[3 * k], v[3 * k + 1], v[3 * k + 2]) for k in range(4)])
    return Side(meta, coll, tiles, tile_pal, pals)


def gen1_side(ts, coll):
    tiles = tiles2bpp(ts.gfx_raw)
    tile_pal = []
    for i in range(0x30):
        tile_pal += [ts.palmap[i] & 7, (ts.palmap[i] >> 4) & 7]
    pals = []
    for p in range(8):
        cols = []
        for k in range(4):
            v = ts.pals[8 * p + 2 * k] | ts.pals[8 * p + 2 * k + 1] << 8
            cols.append((v & 31, (v >> 5) & 31, (v >> 10) & 31))
        pals.append(cols)
    n = len(coll) // 4
    return Side(bytes(ts.blocks[:16 * n]), bytes(coll[:4 * n]), tiles, tile_pal, pals)


def table(src, dst, used):
    """{src block: dst block} for the blocks in `used`"""
    out = {}
    plain = [b for b in range(dst.n) if all(dst.coll[4 * b + q] in (COLL_FLOOR, COLL_WALL, COLL_WATER, COLL_TALL_GRASS)
                                            for q in range(4))]
    for b in sorted(set(used)):
        best = None
        for d in plain:
            miss = sum(x != y for x, y in zip(src.cls[b], dst.cls[d]))
            dist = sum((a[0] - c[0]) ** 2 + (a[1] - c[1]) ** 2 + (a[2] - c[2]) ** 2 for a, c in zip(src.img[b], dst.img[d]))
            k = (miss, dist)
            if best is None or k < best[0]: best = (k, d)
        out[b] = best[1]
    return out


def translate(blk, src, dst):
    t = table(src, dst, blk)
    return bytes(t[b] for b in blk)
