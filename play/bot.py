"""Fast-play bot for the MOD: SELECT runs a script written into ROM (test ROM only), plus input helpers."""
import os, sys, shutil
SC = '/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad'
sys.path.insert(0, SC + '/sameboy-harness/python'); sys.path.insert(0, SC + '/tools'); sys.path.insert(0, SC + '/play')
from gr import GR
from jpchar import encode, decode
from mapdb import DB, crystal_names, connections

SB, SA = 0x2E, 0x7F00                 # script area (test ROM)
SOFF = SB * 0x4000 + SA - 0x4000
W_MAP, W_Y, W_X = 0xDC7B, 0xDC7D, 0xDC7E
W_BATTLE = 0xD25E
TEST = SC + '/build/test_play.gbc'


def make_test_rom(src=SC + '/build/p55.gbc'):
    r = bytearray(open(src, 'rb').read())
    o = 0x25 * 0x4000 + 0x6B4E - 0x4000
    assert r[o:o + 5] == bytes([0x3E, 0x25, 0x21, 0x5F, 0x6B])
    r[o:o + 5] = bytes([0x3E, SB, 0x21, SA & 0xFF, SA >> 8])
    r[SOFF] = 0x90
    open(TEST, 'wb').write(r)
    return TEST


class Bot:
    def __init__(s, state=None, sav=None, out='run', rom=None):
        s.g = GR(rom or TEST, state=state, sav=sav)
        s.out = out; os.makedirs(out, exist_ok=True)
        s.n = 0; s.log = []; s.blocked = set(); s.talked = 0
        s.db = DB(rom or TEST)
        s.names = crystal_names(); s.ids = {v: k for k, v in s.names.items()}

    # ---------------- basics
    def wait(s, n): s.g.wait(n)
    def press(s, k, w=30): s.g.press(k, 4, w)
    def shot(s, tag=''):
        f = '%s/%05d%s.png' % (s.out, s.n, ('_' + tag) if tag else ''); s.n += 1
        s.g.shot(f); return f
    def peek(s, a, n=1): return s.g.peek(a, n)
    def where(s):
        for i in range(40):
            g, m = s.peek(W_MAP, 2); y, x = s.peek(W_Y, 2)
            if (g, m) in s.db.maps: break
            s.wait(10)
        return (g, m), x, y
    def in_battle(s): return s.peek(W_BATTLE)[0] != 0
    def pc(s): return s.g.pc()

    # ---------------- scripts
    def script(s, b, wait=120):
        b = bytes(b) + b'\x90'
        s.wait(30)
        if s.textbox(): s.clear_text()
        for i, v in enumerate(b): s.g.cmd('rpoke %x %d' % (SOFF + i, v))
        s.press('s', 10); s.wait(wait)

    def mapk(s, m):
        return s.ids[m] if isinstance(m, str) else m

    def warp(s, m, x, y, wait=200):
        g, n = s.mapk(m)
        s.script([0x3C, g, n, x, y], wait)

    def setev(s, *fl):
        b = []
        for f in fl: b += [0x33, f & 0xFF, f >> 8]
        s.script(b, 30)

    def clrev(s, *fl):
        b = []
        for f in fl: b += [0x32, f & 0xFF, f >> 8]
        s.script(b, 30)

    def setflag(s, *fl):
        b = []
        for f in fl: b += [0x36, f & 0xFF, f >> 8]
        s.script(b, 30)

    def givepoke(s, species, level):
        s.script([0x2D, species, level, 0, 0], 120)
        for i in range(40):
            s.press('B', 40)
            if not s.textbox(): break

    def giveitem(s, item, n=1):
        s.script([0x1F, item, n], 30)

    # ---------------- moving / talking
    def step(s, d, n=1):
        ok = True
        for i in range(n):
            p0 = s.peek(W_MAP, 4); s.g.down(d); moved = False
            for f in range(14):
                s.wait(2)
                if s.peek(W_MAP, 4) != p0: moved = True; break
            s.g.up(d); s.wait(16 if moved else 4)
            ok = ok and moved
        return ok

    def face(s, d):
        s.g.down(d); s.wait(5); s.g.up(d); s.wait(14)

    def mash(s, n=10, every=40, shots=True, b_every=0, tag=''):
        """press A n times; every b_every-th press also B; screenshot each"""
        fs = []
        for i in range(n):
            if s.in_battle():
                s.battle(); continue
            s.press('A', every)
            if b_every and i % b_every == b_every - 1: s.press('B', 20)
            if shots: fs.append(s.shot(tag))
        return fs

    def battle(s, maxp=300):
        """fight with the first move until the battle ends"""
        k = 0
        while s.in_battle() and k < maxp:
            s.press('A', 30); k += 1
            if k % 4 == 0: s.shot('b')
            if k % 7 == 0: s.press('B', 20)
        s.wait(60)
        s.g.pokes(0xDCA5 + 0x17, [0xFF, 0xFF, 0xFF, 0xFF])
        return k


def _tm(s):
    return bytes(s.peek(0xC4A0, 360))
Bot.tilemap = _tm
def _has(s, txt):
    return encode(txt).rstrip(b'\x50') in s.tilemap()
Bot.has = _has
def _until_text(s, txt, n=80, key='A', w=40):
    for i in range(n):
        if s.has(txt): return True
        s.press(key, w)
    return s.has(txt)
Bot.until_text = _until_text


# ---------------- path walking on the static collision grid
from collections import deque
import portmaps as _PM
from portlib import Space as _Space
from lib import attrs as _attrs
WALK = {0x00, 0x18, 0x14, 0x10, 0x70, 0x71, 0x7A, 0xB0, 0xB1, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6, 0xB7, 0x7B, 0x7C, 0x7D, 0x7E, 0x72, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79}
_GC = {}
def grid_of(rom, h):
    if h in _GC: return _GC[h]
    a = _attrs(rom, h); ts = rom[h + 1]
    TS = _PM.Tilesets(rom, _Space(rom)); co = TS.coll_off(ts)
    w, hh = a['w'], a['h']; bo = a['blkbank'] * 0x4000 + a['blk'] - 0x4000
    G = [[0] * (2 * w) for _ in range(2 * hh)]
    for by in range(hh):
        for bx in range(w):
            b = rom[bo + by * w + bx]
            for q in range(4):
                G[2 * by + q // 2][2 * bx + q % 2] = rom[co + 4 * b + q]
    _GC[h] = G; return G

def _objpos(s):
    out = []
    for i in range(1, 13):
        b = s.peek(0xD4C9 + 0x28 * i, 0x14)
        if b[0]: out.append((b[0x10] - 4, b[0x11] - 4))
    return out
Bot.objpos = _objpos

def _path(s, tx, ty, extra_block=(), allow_target=True, ignore_objs=False):
    k, x, y = s.where()
    G = grid_of(s.db.r, s.db.maps[k]['hdr'])
    H, W = len(G), len(G[0])
    block = (set() if ignore_objs else set(s.objpos())) | set(extra_block)
    prev = {(x, y): None}; q = deque([(x, y)])
    D = {(1, 0): 'R', (-1, 0): 'L', (0, 1): 'D', (0, -1): 'U'}
    while q:
        p = q.popleft()
        if p == (tx, ty): break
        for (dx, dy), d in D.items():
            nx, ny = p[0] + dx, p[1] + dy
            if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in prev: continue
            c = G[ny][nx]
            ok = c in WALK or ((nx, ny) == (tx, ty) and allow_target)
            if c == 0xA3 and dy == 1 and ny + 1 < H and G[ny + 1][nx] in WALK: nx, ny, ok = nx, ny + 1, True
            elif c == 0xA0 and dx == 1 and nx + 1 < W and G[ny][nx + 1] in WALK: nx, ok = nx + 1, True
            elif c == 0xA1 and dx == -1 and G[ny][nx - 1] in WALK: nx, ok = nx - 1, True
            if (nx, ny) in prev: continue
            if (k, p, d) in s.blocked: continue
            if ok and ((nx, ny) not in block or (nx, ny) == (tx, ty)):
                prev[(nx, ny)] = (p, d); q.append((nx, ny))
    if (tx, ty) not in prev: return None
    out = []; p = (tx, ty)
    while prev[p]: p, d = prev[p]; out.append(d)
    return out[::-1]
Bot.path = _path

def _goto(s, tx, ty, tries=40, stop_battle=True):
    for t in range(tries):
        k, x, y = s.where()
        if (x, y) == (tx, ty): return True
        p = s.path(tx, ty)
        if p is None:
            p2 = s.path(tx, ty, ignore_objs=True)
            if p2 is None or s.talked > 6:
                s.log.append('no path %s -> %s' % ((k, x, y), (tx, ty))); return False
            # walk until an object is in the way, then talk to it
            objs = set(s.objpos()); D = {'R': (1, 0), 'L': (-1, 0), 'D': (0, 1), 'U': (0, -1)}
            for d in p2:
                k1, x1, y1 = s.where(); nx, ny = x1 + D[d][0], y1 + D[d][1]
                if (nx, ny) in objs:
                    s.face(d); s.press('A', 40); s.shot('obj'); s.ev(); s.talked += 1; break
                if not s.step(d): break
                if s.in_battle(): s.battle()
            continue
        for d in p:
            k0 = s.where()
            if not s.step(d) and not s.step(d) and s.where() == k0 and not s.textbox() and not s.in_battle():
                s.blocked.add((k0[0], k0[1:], d))
            if s.in_battle(): s.battle()
            if s.where()[0] != k0[0]: return s.where()[1:] == (tx, ty)
            if s.where() == k0:                 # blocked / text started
                s.clear_text(); break
    return s.where()[1:] == (tx, ty)
Bot.goto = _goto


def _go_warp(s, dest, dirs='DULR', only=None):
    """walk to a warp of this map leading to dest (g,m) and take it"""
    k, x, y = s.where(); dest = s.mapk(dest)
    ws = [w for i, w in enumerate(s.db.warps(k)) if (w[3], w[4]) == dest and (only is None or i in only)]
    ws.sort(key=lambda w: s.path(w[0], w[1]) is None)
    for wx, wy, idx, g, m in ws:
        for t in range(3):
            if s.goto(wx, wy) or s.where()[0] != k: break
        s.wait(50)
        if s.where()[0] != k: s.wait(60); return True
        for d in dirs:
            s.step(d); s.wait(40)
            if s.where()[0] != k: s.wait(60); return True
    s.log.append('go_warp failed %s -> %s' % (k, dest)); return False
Bot.go_warp = _go_warp

def _sheet(s, tag, cols=6):
    import glob
    from PIL import Image
    fs = sorted(glob.glob(s.out + '/*.png'))[s._sheet0 if hasattr(s, '_sheet0') else 0:]
    s._sheet0 = len(sorted(glob.glob(s.out + '/*.png')))
    if not fs: return None
    rows = (len(fs) + cols - 1) // cols
    W = Image.new('RGB', (160 * cols, 144 * rows), 'white')
    for i, f in enumerate(fs): W.paste(Image.open(f), (160 * (i % cols), 144 * (i // cols)))
    o = s.out + '_' + tag + '.png'; W.save(o); return o
Bot.sheet = _sheet

def _flag(s, f):
    return s.peek(0xDA65 + (f >> 3))[0] >> (f & 7) & 1
Bot.flag = _flag

def _talk(s, n=12, tag='t'):
    """A until the text box closes (no box border on the bottom rows)"""
    fs = []
    for i in range(n):
        s.press('A', 40)
        if s.in_battle(): s.battle()
        fs.append(s.shot(tag))
        t = s.tilemap()
        if t[20 * 12] != 0x79 and i > 0: break
    return fs
Bot.talk = _talk


def _textbox(s):
    t = s.tilemap(); return t[20 * 12] == 0x79 or t[20 * 13] == 0x79 or t[20*12] == 0xEE
Bot.textbox = _textbox
def _clear_text(s, n=60, shots=True):
    k = 0
    while k < n and (s.textbox() or s.in_battle()):
        if s.in_battle(): s.battle(); continue
        s.press('A', 40); k += 1
        if shots: s.shot('c')
    return k
Bot.clear_text = _clear_text


def _swap01(s):
    def sw(a, n):
        x = s.peek(a, n); y = s.peek(a + n, n)
        s.g.pokes(a, y); s.g.pokes(a + n, x)
    sw(0xDC9F, 1) if False else None
    sp = s.peek(0xDC9E, 2); s.g.pokes(0xDC9E, sp[::-1])
    sw(0xDCA5, 0x30); sw(0xDDC5, 6); sw(0xDDE9, 6)
Bot.swap01 = _swap01

def _strong(s, species=150, level=100):
    s.wait(200)
    s.givepoke(species, level)
    s.swap01()
Bot.strong = _strong

def _warp_near(s, m, x, y):
    s.warp(m, x, y); s.clear_text()
Bot.warp_near = _warp_near


def _ev(s, n=120, quiet=3, shots=True, key='A'):
    """press A through an event until nothing happens for `quiet` checks"""
    q = 0; k = 0
    while k < n:
        if s.in_battle(): s.battle(); q = 0; continue
        if s.textbox() or s.peek(0xFF00)[0] is None:
            s.press(key, 40); k += 1; q = 0
            if shots: s.shot()
        else:
            q += 1
            if q >= quiet: break
            s.wait(50)
            if shots and q == 1: s.shot()
    return k
Bot.ev = _ev


def _cross(s, d, hint=None):
    """walk off the map edge in direction d (U/D/L/R); hint = preferred coordinate along the edge"""
    k, x, y = s.where()
    G = grid_of(s.db.r, s.db.maps[k]['hdr']); H, W = len(G), len(G[0])
    if d == 'U': cand = [(i, 0) for i in range(W)]
    elif d == 'D': cand = [(i, H - 1) for i in range(W)]
    elif d == 'L': cand = [(0, i) for i in range(H)]
    else: cand = [(W - 1, i) for i in range(H)]
    cand = [c for c in cand if G[c[1]][c[0]] in WALK and s.path(*c, allow_target=False) is not None]
    ref = hint if hint is not None else (x if d in 'UD' else y)
    cand.sort(key=lambda c: abs((c[0] if d in 'UD' else c[1]) - ref))
    for c in cand[:6]:
        r = s.goto(*c)
        if s.where()[0] != k: s.wait(40); return True
        if r:
            for i in range(3):
                s.step(d); s.wait(30)
                if s.where()[0] != k: s.wait(40); return True
    s.log.append('cross failed %s %s' % (k, d)); return False
Bot.cross = _cross


def _talk_to(s, ox, oy, n=200):
    """walk next to the object at (ox,oy), face it, talk through the event"""
    for (dx, dy, d) in ((0, 1, 'U'), (0, -1, 'D'), (1, 0, 'L'), (-1, 0, 'R')):
        if s.path(ox + dx, oy + dy, allow_target=False) is not None:
            s.goto(ox + dx, oy + dy)
            if s.where()[1:] == (ox + dx, oy + dy):
                s.face(d); s.press('A', 40); s.shot('talk'); return s.ev(n)
    s.log.append('talk_to failed %s' % ((ox, oy),)); return -1
Bot.talk_to = _talk_to

def _objs_of(s, k=None):
    k = k or s.where()[0]
    return [(o[0], o[2] - 4, o[1] - 4) for o in s.db.objs(k)]   # sprite, x, y
Bot.objs_of = _objs_of

BADGES = 0xD857


# ---------------- multi-map travel planner
from mapdb import connections as _conns
def _reach_set(G, starts):
    H, W = len(G), len(G[0]); seen = set(starts); q = deque(starts)
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < W and 0 <= ny < H): continue
            c = G[ny][nx]; t = None
            if c in WALK: t = (nx, ny)
            elif c == 0xA3 and dy == 1 and ny + 1 < H and G[ny + 1][nx] in WALK: t = (nx, ny + 1)
            elif c == 0xA0 and dx == 1 and nx + 1 < W and G[ny][nx + 1] in WALK: t = (nx + 1, ny)
            elif c == 0xA1 and dx == -1 and nx - 1 >= 0 and G[ny][nx - 1] in WALK: t = (nx - 1, ny)
            if t and t not in seen: seen.add(t); q.append(t)
    return seen

def _edge_cells(G, d):
    H, W = len(G), len(G[0])
    if d == 'N': c = [(i, 0) for i in range(W)]
    elif d == 'S': c = [(i, H - 1) for i in range(W)]
    elif d == 'W': c = [(0, i) for i in range(H)]
    else: c = [(W - 1, i) for i in range(H)]
    return [p for p in c if G[p[1]][p[0]] in WALK]

OPP = {'N': 'S', 'S': 'N', 'W': 'E', 'E': 'W'}
def _hops(s, k, starts):
    """possible moves from map k when standing anywhere in starts: [(kind, arg, dest, dest_starts)]"""
    G = grid_of(s.db.r, s.db.maps[k]['hdr']); R = _reach_set(G, starts); out = []
    near = lambda x, y: any((x + dx, y + dy) in R for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)))
    for i, (wx, wy, idx, g, m) in enumerate(s.db.warps(k)):
        if (g, m) not in s.db.maps or not near(wx, wy): continue
        dw = s.db.warps((g, m))
        if idx - 1 >= len(dw): continue
        ax, ay = dw[idx - 1][:2]
        out.append(('warp', i, (g, m), [(ax, ay)]))
    for d, t in _conns(s.db, k):
        if t not in s.db.maps: continue
        if any(p in R for p in _edge_cells(G, d)):
            G2 = grid_of(s.db.r, s.db.maps[t]['hdr'])
            out.append(('cross', d, t, _edge_cells(G2, OPP[d])))
    return out
Bot.hops = _hops

def _plan(s, target, avoid=()):
    target = s.mapk(target)
    k, x, y = s.where()
    def key(k, st):
        G = grid_of(s.db.r, s.db.maps[k]['hdr']); return (k, min(_reach_set(G, list(st))))
    n0 = (k, ((x, y),)); prev = {key(*n0): None}; q = deque([n0]); end = None
    while q:
        k0, st = q.popleft()
        if k0 == target: end = (k0, st); break
        for kind, arg, d, ds in s.hops(k0, list(st)):
            if d in avoid or not ds: continue
            kk = key(d, ds)
            if kk in prev: continue
            prev[kk] = ((k0, st), kind, arg); q.append((d, tuple(ds)))
    if end is None: return None
    path = []; c = end
    while prev[key(*c)]:
        pn, kind, arg = prev[key(*c)]; path.append((pn[0], kind, arg, c[0])); c = pn
    return path[::-1]
Bot.plan = _plan

def _travel(s, target, maxhops=40, avoid=()):
    target = s.mapk(target)
    for i in range(maxhops):
        k = s.where()[0]
        if k == target: return True
        p = s.plan(target, avoid)
        if not p: s.log.append('travel: no plan %s -> %s' % (k, target)); return False
        k0, kind, arg, d = p[0]
        if kind == 'warp':
            wx, wy = s.db.warps(k0)[arg][:2]
            s.go_warp_xy(wx, wy)
        else:
            s.cross({'N': 'U', 'S': 'D', 'W': 'L', 'E': 'R'}[arg])
        s.clear_text(shots=False)
    return s.where()[0] == target
Bot.travel = _travel

def _go_warp_xy(s, wx, wy, dirs='DULR'):
    k = s.where()[0]
    for t in range(3):
        if s.goto(wx, wy) or s.where()[0] != k: break
    s.wait(50)
    if s.where()[0] != k: s.wait(60); return True
    for d in dirs:
        s.step(d); s.wait(40)
        if s.where()[0] != k: s.wait(60); return True
    s.log.append('go_warp_xy failed %s %s' % (k, (wx, wy))); return False
Bot.go_warp_xy = _go_warp_xy
