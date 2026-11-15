"""Red full color's palette per tile, from VRAM dumps taken in Red full color (play/akadump.py): the visible screen
(above the town-name sign) votes for each tile's palette."""
import pickle
from collections import Counter, defaultdict


def votes(paths, rows=13):
    v = defaultdict(Counter)
    for p in paths:
        d = pickle.load(open(p, 'rb'))
        sx, sy = d['scx'] // 8, d['scy'] // 8
        for ry in range(rows):
            for rx in range(20):
                i = ((sy + ry) % 32) * 32 + (sx + rx) % 32
                t = d['tm'][i]; a = d['at'][i]
                if t < 0x60 and not a & 8: v[t][a & 7] += 1
    return v


def palmap(paths, fallback):
    """fallback: the Pikachu full-color palette map (tile -> palette) for tiles never seen"""
    v = votes(paths)
    pal = [v[t].most_common(1)[0][0] if v[t] else fallback[t] for t in range(0x60)]
    return bytes((pal[2 * i + 1] << 4) | pal[2 * i] for i in range(0x30)) + b'\xff' * 16 + \
        bytes(((8 | pal[2 * i + 1]) << 4) | (8 | pal[2 * i]) for i in range(0x30)), v


def pals(path):
    d = pickle.load(open(path, 'rb'))
    return bytes.fromhex(d['pals'].split()[0][3:])[:64]


SC = '/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad'
# Red full color dumps of the Celadon Mansion (1F, 2F, 3F, roof) and the chief's house (Red's MANSION tileset)
import glob
MANSION_DUMPS = [SC + '/out/aka_m%s.pkl' % m for m in ('80', '81', '82', '83', '8b')] + sorted(glob.glob(SC + '/out/akd8[0-3b]_*.pkl'))


def apply(ts, paths):
    """ts (portlib.Tileset): Red full color's tiles, colors and palette per tile instead of the dump it was made from"""
    d = pickle.load(open(paths[0], 'rb'))
    ts.gfx_raw = d['t0'][0x1000:0x1600]
    ts.pals = pals(paths[0])
    fb = [ts.palmap[i // 2] >> (4 * (i & 1)) & 7 for i in range(0x60)]
    ts.palmap, _ = palmap(paths, fb)
    return ts
