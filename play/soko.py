"""live collision grid + boulder pushing (Strength) for the bot"""
from bot import *
from bot import _attrs, _PM, _Space, _GC
from collections import deque
SPR_BOULDER = 0x5A
def refresh_grid(s):
    k = s.where()[0]; h = s.db.maps[k]['hdr']; r = s.db.r
    a = _attrs(r, h); ts = r[h + 1]
    TS = _PM.Tilesets(r, _Space(r)); co = TS.coll_off(ts)
    w, hh = a['w'], a['h']; W = w + 6
    raw = s.peek(0xC800, W * (hh + 6))
    G = [[0] * (2 * w) for _ in range(2 * hh)]
    for by in range(hh):
        for bx in range(w):
            b = raw[(by + 3) * W + bx + 3]
            for q in range(4): G[2 * by + q // 2][2 * bx + q % 2] = r[co + 4 * b + q]
    _GC[h] = G; s.blocked = set(); return G
Bot.refresh_grid = refresh_grid
def boulders(s):
    out = []
    for i in range(1, 13):
        b = s.peek(0xD4C9 + 0x28 * i, 0x14)
        if b[0] == SPR_BOULDER: out.append((b[0x10] - 4, b[0x11] - 4))
    return out
Bot.boulders = boulders
NOSTAND = {0x71,0x72,0x7A,0x7B}
DV = {'R': (1, 0), 'L': (-1, 0), 'D': (0, 1), 'U': (0, -1)}
def _reach(G, start, block):
    H, W = len(G), len(G[0]); seen = {start}; q = deque([start])
    while q:
        x, y = q.popleft()
        for d, (dx, dy) in DV.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in seen and G[ny][nx] in WALK and G[ny][nx] not in NOSTAND \
               and (nx, ny) not in block and not wall_block(G, x, y, nx, ny, d):
                seen.add((nx, ny)); q.append((nx, ny))
    return seen
def solve(s, bpos, target):
    """BFS over pushes of one boulder: returns [(stand, dir)]"""
    G = s.refresh_grid(); me = s.where()[1:]
    others = set(s.objpos()) - {bpos}
    start = (bpos, me); prev = {(bpos, frozenset()): None}
    q = deque([(bpos, me)]); seenk = {}
    def key(b, p): return (b, min(_reach(G, p, others | {b})))
    seenk[key(bpos, me)] = None; parent = {}
    while q:
        b, p = q.popleft()
        if b == target: break
        R = _reach(G, p, others | {b})
        for d, (dx, dy) in DV.items():
            st = (b[0] - dx, b[1] - dy); nb = (b[0] + dx, b[1] + dy)
            if st not in R: continue
            if not (0 <= nb[1] < len(G) and 0 <= nb[0] < len(G[0])): continue
            if G[nb[1]][nb[0]] not in (0x00, 0x60) or nb in others: continue
            if wall_block(G, b[0], b[1], nb[0], nb[1], d): continue
            kk = key(nb, b)
            if kk in seenk: continue
            seenk[kk] = (b, p, st, d); parent[(nb, b)] = (b, p, st, d); q.append((nb, b))
    else:
        return None
    # rebuild
    out = []; cur = (b, p)
    while cur in parent:
        pb, pp, st, d = parent[cur]; out.append((st, d)); cur = (pb, pp)
    return out[::-1]
def push_to(s, bpos, target, strength=True):
    plan = solve(s, bpos, target)
    if plan is None: s.log.append('no push plan %s->%s' % (bpos, target)); return False
    used = False
    cur = bpos
    for st, d in plan:
        nxt = (cur[0] + DV[d][0], cur[1] + DV[d][1])
        moved = lambda: nxt in s.boulders() or (nxt == target and cur not in s.boulders())
        s.refresh_grid()
        bs = s.boulders()
        ok = False
        for t in range(3):
            s.clear_text(shots=False)
            if s.goto(*st): ok = True; break
            s.blocked = set(); s.wait(30)
        if not ok: s.log.append('push goto fail %s' % (st,)); return False
        for attempt in range(2):
            if not used:
                s.face(d)
                s.press('A', 60)
                for i in range(6):
                    if s.has('つかいますか') or s.has('はい'): break
                    s.press('A', 40)
                s.press('A', 60); s.clear_text(shots=False); s.wait(20); used = True
            before = s.boulders()
            s.g.down(d)
            for t in range(30):
                s.wait(4)
                if moved(): break
            s.g.up(d); s.wait(50)
            if moved(): break
            used = False; s.log.append('strength again at %s' % (st,))
        if not moved(): s.log.append('push failed at %s %s' % (st, d)); return False
        cur = nxt
    return True
Bot.push_to = push_to
