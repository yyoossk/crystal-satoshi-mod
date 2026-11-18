"""playthrough check: new game -> Pewter Gym, walking only (no warps / pokes)"""
import os
import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
import bot as _bot
_bot.NOHEAL[0] = True
ROM = os.environ.get('PTROM', 'p115')
make_test_rom(SC+'/build/%s.gbc' % ROM)
ST = SC + '/play/pt_%s.st'
def B(prev, tag):
    b = Bot(state=ST % prev if prev else SC+'/play/ng_%s.st' % ROM, out=SC+'/run/pt_'+tag)
    b.tag = tag; b.fs = []; return b
def mus(b): return '%02x/%02x' % (b.peek(0xC101)[0], b.peek(0xC2C0)[0])
def snap(b, k=1):
    for i in range(k): b.fs.append(b.shot()); 
def ev(b, n=80, yes=True):
    """go through text / battles; answer yes/no with A (yes) or B"""
    q = 0
    for i in range(n):
        if b.in_battle(): b.battle(); snap(b); q = 0; continue
        if b'\xb4\xd7\xde' in b.tilemap()[14 * 20:]: b.press('B', 30); b.press('B', 30); snap(b); q = 0; continue
        if b.has('ニックネームは'): b.press('S', 30); b.press('A', 40); snap(b); q = 0; continue
        if b.textbox():
            if b.has('はい') and b.has('いいえ') and not yes: b.press('B', 40)
            else: b.press('A', 40)
            snap(b); q = 0
        else:
            q += 1; b.wait(20); snap(b)
            if q >= 3: break
def done(b, W=8, last=64):
    u = uniq(b.fs)
    sheet(u[-last:], SC+'/run/pt_%s.png' % b.tag, W=W)
    b.g.save_state(ST % b.tag)
    print(b.tag, 'at', b.where(), 'music', mus(b), 'frames', len(u))
from lib import attrs, parse_events
def bgs_of(b, k=None):
    k = k or b.where()[0]; h = b.db.maps[k]['hdr']; a = attrs(b.db.r, h)
    ev = parse_events(b.db.r, a['scbank'], a['events'])
    return [(bg[1], bg[0], bg[2]) for _, bg in ev['bgs']]
def talk_all(b, skip=()):
    done_ = set()
    for t in range(12):
        ps = [p for p in b.objpos() if p not in done_ and p not in skip]
        if not ps: break
        x, y = ps[0]; done_.add((x, y))
        b.talk_to(x, y, n=0); snap(b); ev(b, 30)
def read_signs(b):
    for x, y, t in bgs_of(b):
        if t >= 7: continue
        for (dx, dy, d) in ((0, 1, 'U'), (0, -1, 'D'), (1, 0, 'L'), (-1, 0, 'R')):
            if b.goto(x + dx, y + dy):
                b.face(d); b.press('A', 40); snap(b); ev(b, 20); break
def lv(b): b.bank1(); return b.peek(0xDCA5 + 0x1F)[0]
def hp(b):
    b.bank1(); h = b.peek(0xDCA5 + 0x22, 4); return (h[0] << 8 | h[1]), (h[2] << 8 | h[3])
def heal(b, pc=(23, 9), town='ViridianCity'):
    b.travel(pc); b.wait(30)
    b.goto(3, 3); b.face('U'); b.press('A', 40)
    for i in range(30):
        if b.textbox(): b.press('A', 40)
        else: b.wait(20)
    b.travel(town); b.wait(30)
def grind(b, target, area='Route1', spot=(10, 3), pc=(23, 9), town='ViridianCity', maxsteps=4000):
    n = 0
    while lv(b) < target and n < maxsteps:
        if b.where()[0] != b.ids[area] if isinstance(area, str) else b.where()[0] != area:
            b.travel(area); b.wait(20)
        b.goto(*spot)
        for k in range(20):
            b.step('L' if k % 2 else 'R'); n += 1
            if b.in_battle():
                b.battle()
                for t in range(20):
                    if b.textbox(): b.press('B' if (b.has('はい') and b.has('いいえ')) else 'A', 30)
                    else: break
                h, m = hp(b)
                if h * 3 < m or b.where()[0] == pc: break
        h, m = hp(b)
        if h * 3 < m or b.where()[0] == pc:
            heal(b, pc, town)
        print('lv', lv(b), 'hp', hp(b), b.where(), flush=True)
DRAGONBREATH = 0xE1
def maxparty(b, move=DRAGONBREATH):
    """user's request: every party Pokémon Lv100, with a move that hits every type (Dragon)"""
    b.bank1(); n = b.peek(0xDC9D)[0]
    for i in range(min(n, 6)):
        o = 0xDCA5 + 0x30 * i
        b.g.pokes(o + 2, [move] * 4)
        b.g.pokes(o + 0x08, [0x13, 0x12, 0xD0])            # exp 1,250,000
        b.g.pokes(o + 0x17, [0xE0] * 4)                      # PP 32
        b.g.poke(o + 0x1F, 100); b.g.poke(o + 0x20, 0)
        b.g.pokes(o + 0x22, [3, 0xE7, 3, 0xE7])               # HP 999/999
        b.g.pokes(o + 0x26, [3, 0xE7] * 5)                    # stats 999
def talk_map(b, skip=()):
    """talk to every person of the map's object table: walk near the start position, then talk to the nearest one"""
    k = b.where()[0]; got = []; SPIN = bool(spinners(b, k))
    WT = {(w[0], w[1]) for w in b.db.warps(k)}
    for o in b.db.objs(k):
        x0, y0 = o[2] - 4, o[1] - 4
        if (x0, y0) in skip: continue
        for dx, dy in ((0, 2), (0, -2), (2, 0), (-2, 0), (0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, -1), (0, 3), (3, 0)):
            if (x0 + dx, y0 + dy) in WT: continue
            if b.where()[0] != k: break
            if (SPIN or b.path(x0 + dx, y0 + dy) is not None) and b.goto(x0 + dx, y0 + dy, tries=8): break
        if b.where()[0] != k: print('  left the map', b.where(), flush=True); break
        ps = b.objpos()
        if not ps: print('  no one near', (x0, y0), flush=True); continue
        x, y = min(ps, key=lambda p: abs(p[0] - x0) + abs(p[1] - y0))
        print('  talk', (x0, y0), '->', (x, y), flush=True)
        b.talk_to(x, y, n=0); snap(b); ev(b, 30); got.append((x0, y0))
    return got
W_OPTIONS, W_REPEL = 0xCFC0, 0xDC67
def fast(b, wild=False):
    """faster checking: text speed fast, battle animations off ("set" style); with the party at Lv100 a Repel keeps every
    wild Pokémon away (refreshed on every travel) unless wild=True"""
    b.g.poke(W_OPTIONS, 0xC1)
    if not wild: b.bank1(); b.g.poke(W_REPEL, 250)
    import bot as _b
    if not getattr(_b.Bot, '_fastwrap', False):
        ot = _b.Bot.travel
        def tr(s, *a, **k):
            if getattr(s, 'norepel', False) is False: s.bank1(); s.g.poke(W_REPEL, 250)
            return ot(s, *a, **k)
        _b.Bot.travel = tr; _b.Bot._fastwrap = True
        og = _b.Bot.goto
        SPC = {}
        def gt(s, *a, **k):
            if getattr(s, 'norepel', False) is False and s.peek(0xFF70)[0] & 7 in (0, 1): s.g.poke(W_REPEL, 250)
            m = s.where()[0]
            if LIVE[0]: live_grid(s)
            if m not in SPC: SPC[m] = bool(spinners(s, m))
            if SPC[m] and len(a) >= 2: return sgoto(s, a[0], a[1], tries=k.get('tries', 60))
            return og(s, *a, **k)
        _b.Bot.goto = gt
        ob = _b.Bot.battle
        def bt(s, *a, **k):
            r = ob(s, *a, **k)
            s.bank1(); n = s.peek(0xDC9D)[0]
            for i in range(min(n, 6)):
                s.g.pokes(0xDCA5 + 0x30 * i + 0x17, [0xE0] * 4)    # PP back (the bot keeps one move)
                s.g.pokes(0xDCA5 + 0x30 * i + 0x20, [0, 0, 3, 0xE7])  # status, HP back
            return r
        _b.Bot.battle = bt
AVOID = tuple((20, i) for i in range(1, 8)) + ((19, 1),)   # Route 28 (Silver Cave): its gate guard lets the player by only after the Johto story
def tour(b, target, visit=True, hops=60, skipmaps=()):
    """travel hop by hop; on each new map talk to everyone (trainers, people) and print what happened"""
    if not hasattr(b, 'seen'): b.seen = set()
    seen = b.seen; target = b.mapk(target)
    for i in range(hops):
        k = b.where()[0]
        if visit and k not in seen and k not in skipmaps:
            seen.add(k); print('== map', k, b.where(), mus(b), 'objs', [(o[2]-4, o[1]-4, o[0]) for o in b.db.objs(k)], flush=True)
            snap(b); talk_map(b)
            if DOORS[0]: open_doors(b)
            b.g.save_state(ST % ('%s_%d_%d' % (b.tag, k[0], k[1])))
        if k == target: return True
        if LIVE[0]: live_grid(b)
        if REPEL[0]: __import__('honest').use_repel(b)
        p = b.plan(target, AVOID)
        if not p: print('no plan', k, flush=True); return False
        k0, kind, arg, d = p[0]
        if kind == 'warp':
            W_ = b.db.warps(k0); wx, wy = W_[arg][:2]
            if not b.go_warp_xy(wx, wy) and b.where()[0] == k0:
                for v in W_:                       # a twin warp to the same map (one tile of a two-warp door is a wall)
                    if (v[3], v[4]) == (W_[arg][3], W_[arg][4]) and v[:2] != (wx, wy) and b.go_warp_xy(v[0], v[1]): break
        else:
            b.cross({'N': 'U', 'S': 'D', 'W': 'L', 'E': 'R'}[arg])
        b.clear_text(shots=False)
        if b.where()[0] == k: print('stuck', b.where(), p[0], flush=True); ev(b, 30)
    return False
def hms(b, cut=True, flash=False, surf=False, strength=False):
    """field moves in the lead's slots 2-4 (HMs got in the playthrough), the bot may use them"""
    import bot as _b
    b.bank1(); o = 0xDCA5
    if cut: b.g.poke(o + 5, 0x0F); _b.CAN_CUT[0] = True
    if flash: b.g.poke(o + 4, 0x94)
    if surf: b.g.poke(o + 3, 0x39); _b.CAN_SURF[0] = True
    if strength: b.g.poke(o + 3 if not surf else o + 4, 0x46)
SKIPGYM = [False]
def visit_town(b, town, skip=()):
    """the town's people and signs, then every building whose door is in the town (people, back out)"""
    town = b.mapk(town)
    if b.where()[0] != town: b.travel(town); b.wait(20)
    print('== town', town, b.where(), mus(b), flush=True)
    talk_map(b); read_signs(b)
    doors = []
    for w in b.db.warps(town):
        t = (w[3], w[4])
        if SKIPGYM[0] and (b.names.get(t) or '').endswith('Gym'): continue
        if t not in doors and t not in skip and t in b.db.maps and t not in AVOID: doors.append(t)
    for t in doors:
        if b.db.maps[t]['w'] > 12: continue          # routes / caves: not a building
        b.travel(t); b.wait(20)
        if b.where()[0] != t: print('  could not enter', t, flush=True); continue
        print('== bldg', t, b.where(), mus(b), [(o[2]-4, o[1]-4, o[0]) for o in b.db.objs(t)], flush=True)
        snap(b); talk_map(b); read_signs(b)
        b.travel(town); b.wait(20)
MV = {0x18: (0, 1), 0x19: (0, -1), 0x1A: (-1, 0), 0x1B: (1, 0)}
def spinners(b, k=None):
    """coord events that push the player (Red's spinner arrows, ported as applymovement 0, slides): {(x, y): (x2, y2)}"""
    k = k or b.where()[0]; m = b.db.maps[k]; r = b.db.r; out = {}
    for off, c in m['ev']['coords']:
        y, x = c[1], c[2]; a = m['scbank'] * 0x4000 + (c[4] | c[5] << 8) - 0x4000
        if r[a] != 0x68 or r[a + 1] != 0: continue
        q = m['scbank'] * 0x4000 + (r[a + 2] | r[a + 3] << 8) - 0x4000
        xx, yy = x, y
        while r[q] in MV: dx, dy = MV[r[q]]; xx += dx; yy += dy; q += 1
        if r[q] == 0x47 and (xx, yy) != (x, y): out[(x, y)] = (xx, yy)
    return out
def sgoto(b, tx, ty, tries=60):
    """goto that knows the spinner arrows"""
    import bot as _b
    from collections import deque
    k = b.where()[0]; SP = spinners(b, k)
    G = _b.grid_of(b.db.r, b.db.maps[k]['hdr'])
    def ok(x, y): return 0 <= y < len(G) and 0 <= x < len(G[0]) and G[y][x] in _b.WALK
    D = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}
    bad = set()
    for t in range(tries):
        if b.textbox() or b.in_battle(): ev(b, 20)
        k2, x, y = b.where()
        if k2 != k: return False
        if (x, y) == (tx, ty): return True
        blk = (set(b.objpos()) | {(o[2] - 4, o[1] - 4) for o in b.db.objs(k)} | bad | (b.live_warps(k) - {(tx, ty)})) - {(tx, ty)}   # (people off screen too)
        prev = {(x, y): None}; q = deque([(x, y)]); found = False
        while q:
            p = q.popleft()
            if p == (tx, ty): found = True; break
            for d, (dx, dy) in D.items():
                n = (p[0] + dx, p[1] + dy)
                if not ok(*n) or n in blk: continue
                n2 = SP.get(n, n)
                if n2 not in prev: prev[n2] = (p, d); q.append(n2)
        if not found: return False
        path = []; p = (tx, ty)
        while prev[p]: p, d = prev[p][0], prev[p][1]; path.append((d, p))
        path.reverse()
        d, p = path[0]
        b.step(d)
        for i in range(30):
            p0 = b.where(); b.wait(12)
            if b.where() == p0: break
        if b.where()[1:] == (x, y) and not b.textbox() and not b.in_battle():
            dx, dy = D[d]; bad.add((x + dx, y + dy))
    return b.where()[1:] == (tx, ty)
def hop(b, target):
    """go through a warp of this map that leads to target (spinner-aware)"""
    k = b.where()[0]
    for w in b.db.warps(k):
        if (w[3], w[4]) == target:
            if spinners(b, k): sgoto(b, w[0], w[1])
            else: b.go_warp_xy(w[0], w[1])
            b.wait(30); b.clear_text(shots=False)
            if b.where()[0] == target: return True
    print('  hop failed', k, '->', target, b.where(), flush=True); return False
CARPET = [False]
def carpet_fix(b, k, G):
    """Red's Silph Co. floor tiles have collision $70 (carpet warp): without a warp there they are plain floor"""
    ws = {(w[0], w[1]) for w in b.db.warps(k)}
    for y, row in enumerate(G):
        for x, c in enumerate(row):
            if c == 0x70 and (x, y) not in ws: row[x] = 0
    return G



# doors opened by scripts stay open: their blocks as the game has them once the condition holds (the bot's grids are
# built from the ROM's blocks, so a door opened on an earlier visit would otherwise still be a wall when planning)
def _keyitem(b, i): b.bank1(); return i in b.peek(0xD8B0, 0x1B)
KNOWN_DOORS = [('RadioTower3F', lambda b: _keyitem(b, 0x7F) and __import__('honest').has_hm(b, 6) and _keyitem(b, 0x46), [(14, 2, 0x2A), (14, 4, 0x01)]),
               ('TeamRocketBaseB3F', lambda b: __import__('honest').has_hm(b, 6), [(10, 8, 0x07)]),
               ('TeamRocketBaseB2F', lambda b: __import__('honest').has_hm(b, 6), [(14, 12, 0x07)]),
               ('GoldenrodUnderground', lambda b: _keyitem(b, 0x7F), [(18, 6, 0x2E)])]
def patch_blocks(b, name, blocks):
    import bot as _b
    k = b.mapk(name); m = b.db.maps.get(k)
    if not m: return
    h = m['hdr']; G = _b._GC.get(h) or _b.grid_of(b.db.r, h)
    TS = _b._PM.Tilesets(b.db.r, _b._Space(b.db.r)); co = TS.coll_off(b.db.r[h + 1])
    for (x, y, blk) in blocks:
        for q in range(4):
            yy, xx = y + q // 2, x + q % 2
            if 0 <= yy < len(G) and 0 <= xx < len(G[0]): G[yy][xx] = b.db.r[co + 4 * blk + q]
    _b._GC[h] = G
def known_doors(b):
    for name, cond, blocks in KNOWN_DOORS:
        try:
            if cond(b): patch_blocks(b, name, blocks)
        except Exception as e: print('  known door', name, e, flush=True)

def live_grid(b):
    """the current map's collision from the blocks in RAM (doors opened / closed by scripts), into the bot's grid cache"""
    import bot as _b
    k = b.where()[0]; m = b.db.maps.get(k)
    if not m: return None
    h = m['hdr']; a = _b._attrs(b.db.r, h); w, hh = a['w'], a['h']
    x = b.peek(0xC800, (w + 6) * (hh + 6))
    TS = _b._PM.Tilesets(b.db.r, _b._Space(b.db.r)); co = TS.coll_off(b.db.r[h + 1])
    old = _b._GC.get(h) or _b.grid_of(b.db.r, h)
    G = _b._Grid([0] * (2 * w) for _ in range(2 * hh)); G.red = getattr(old, 'red', False)
    for by in range(hh):
        for bx in range(w):
            blk = x[(by + 3) * (w + 6) + 3 + bx]
            for q in range(4): G[2 * by + q // 2][2 * bx + q % 2] = b.db.r[co + 4 * blk + q]
    if CARPET[0]: carpet_fix(b, k, G)
    _b._GC[h] = G
    if hasattr(b, '_reach'): b._reach = {}
    return G
LIVE = [False]
DOORS = [False]
def open_doors(b):
    """Silph Co.: open every card-key door of this floor (bg events: checkevent, ..., checkitem card key)"""
    import bot as _b
    k = b.where()[0]; m = b.db.maps[k]; r = b.db.r; doors = {}
    for _, c in m['ev']['bgs']:
        y, x = c[0], c[1]; a = m['scbank'] * 0x4000 + (c[3] | c[4] << 8) - 0x4000
        if bytes([0x21, 0x89]) in r[a:a + 12]: doors.setdefault(r[a + 1] | r[a + 2] << 8, []).append((x, y))
    D = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}
    for fl, tiles in doors.items():
        G = live_grid(b); done_ = False
        for (x, y) in tiles:
            for d, (dx, dy) in D.items():
                sx, sy = x - dx, y - dy
                if (sx, sy) in tiles or not (0 <= sy < len(G) and 0 <= sx < len(G[0])) or G[sy][sx] not in _b.WALK: continue
                if b.path(sx, sy, extra_block={(w[0], w[1]) for w in b.db.warps(k)}, ignore_objs=True) is None: continue
                if safe_goto(b, sx, sy, tries=3):
                    b.face(d); b.press('A', 40); ev(b, 10); done_ = True; break
            if done_: break
        print('  door', hex(fl), tiles[0], 'opened' if done_ else 'not reached', flush=True)
    live_grid(b)
def safe_goto(b, tx, ty, block=(), tries=8, allow=()):
    """walk a path that never touches a warp tile (but the target) or the given tiles; replan when a step fails"""
    k = b.where()[0]
    for t in range(tries):
        if b.textbox() or b.in_battle(): ev(b, 20)
        k2, x, y = b.where()
        if k2 != k: return False
        if (x, y) == (tx, ty): return True
        import bot as _bw
        Gw = _bw.grid_of(b.db.r, b.db.maps[k]['hdr'])
        realw = {(w[0], w[1]) for w in b.db.warps(k) if 0 <= w[1] < len(Gw) and 0 <= w[0] < len(Gw[0]) and Gw[w[1]][w[0]] != 0}
        av = (realw - set(allow) | set(block) | set(b.objpos())) - {(tx, ty), (x, y)}
        p = b.path(tx, ty, extra_block=av, ignore_objs=True)
        if p is None: return False
        for d in p:
            if not b.step(d):
                if b.textbox() or b.in_battle(): ev(b, 20)
                break
    return b.where()[1:] == (tx, ty)
def fly(b, k, x, y):
    """move like Fly / an Escape Rope (a warp script) to map k at (x, y): for places already checked on foot"""
    b.script([0x3C, k[0], k[1], x, y], 120); b.wait(60); ev(b, 10)
    return b.where()
def wgoto(b, tx, ty, tries=80):
    """goto inside a map whose warps lead to the same map (Saffron Gym's pads): BFS over walking + pads"""
    import bot as _b
    from collections import deque
    k = b.where()[0]; W = b.db.warps(k)
    PAD = {}
    for w in W:
        if (w[3], w[4]) == k:
            dw = W[w[2] - 1]; PAD[(w[0], w[1])] = (dw[0], dw[1])
    OUT = {(w[0], w[1]) for w in W if (w[3], w[4]) != k}
    G = _b.grid_of(b.db.r, b.db.maps[k]['hdr'])
    def ok(x, y): return 0 <= y < len(G) and 0 <= x < len(G[0]) and G[y][x] in _b.WALK
    D = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}
    bad = set()
    for t in range(tries):
        if b.textbox() or b.in_battle(): ev(b, 20)
        k2, x, y = b.where()
        if k2 != k:
            if WDEBUG[0]: print('   wgoto: left the map', b.where(), flush=True)
            return False
        if (x, y) == (tx, ty): return True
        blk = set(b.objpos()) | bad | (OUT - {(tx, ty)})
        prev = {(x, y): None}; q = deque([(x, y)]); found = False
        while q:
            p = q.popleft()
            if p == (tx, ty): found = True; break
            for d, (dx, dy) in D.items():
                n = (p[0] + dx, p[1] + dy)
                if not ok(*n) or n in blk: continue
                n2 = PAD.get(n, n) if n != (tx, ty) else n
                if n2 not in prev: prev[n2] = (p, d); q.append(n2)
        if not found:
            if WDEBUG[0]: print('   wgoto: no path from', (x, y), 'blk', sorted(blk), flush=True)
            return False
        path = []; p = (tx, ty)
        while prev[p]: p, d = prev[p][0], prev[p][1]; path.append((d, p))
        path.reverse()
        d, p = path[0]
        if WDEBUG[0]: print('   wgoto step', d, (x, y), '->', p, 'path', len(path), flush=True)
        b.step(d); b.wait(30)
        for i in range(10):
            p0 = b.where(); b.wait(12)
            if b.where() == p0: break
        if b.where()[1:] == (x, y) and not b.textbox() and not b.in_battle():
            dx, dy = D[d]; bad.add((x + dx, y + dy))
            if WDEBUG[0]: print('   wgoto bad', (x + dx, y + dy), 'from', (x, y), flush=True)
    return b.where()[1:] == (tx, ty)
WDEBUG = [False]
def switches(b):
    """bg events facing up that ask a question (the Pokémon Mansion's secret switches): [(x, y)]"""
    k = b.where()[0]; m = b.db.maps[k]; out = []
    for _, c in m['ev']['bgs']:
        if c[2] == 1: out.append((c[1], c[0]))
    return out
def press_switch(b, x, y):
    import bot as _b
    for sx, sy, d in ((x, y + 1, 'U'),):
        if safe_goto(b, sx, sy, tries=4):
            b.face(d); b.press('A', 40)
            for i in range(8):
                if b.textbox(): b.press('A', 40)
                else: break
            live_grid(b); return True
    return False
def solve_to(b, target, rounds=8):
    """tour to target; when there is no plan, press this map's switches one by one"""
    import itertools
    for r in range(rounds):
        live_grid(b)
        if b.plan(target, AVOID):
            if tour(b, target): return True
        k = b.where()[0]
        sw = switches(b); print('  no plan from', b.where(), 'switches', sw, flush=True)
        pressed = False
        for s in sw:
            if press_switch(b, *s):
                pressed = True; live_grid(b)
                if b.plan(target, AVOID): break
        if not pressed:
            # this floor's switches are out of reach: go to another floor of the same building and press its switch
            # (the Pokémon Mansion's switches all toggle the same flag)
            here = b.where()[0]; tk = b.mapk(target)
            near = []
            for m in SWITCH_MAPS:
                if m == here: continue
                pl = b.plan(m, AVOID)
                if pl: near.append((len(pl), m))
            for _, m in sorted(near):
                if not tour(b, m): continue
                live_grid(b)
                for s in switches(b):
                    if press_switch(b, *s): pressed = True; print('  pressed a switch on', b.where(), flush=True); break
                if pressed:
                    for m2 in SWITCH_MAPS:         # the other floors' blocks change too: forget their cached grids
                        _bot._GC.pop(b.db.maps[m2]['hdr'], None)
                    break
        if not pressed: return False
    return b.where()[0] == b.mapk(target)
SWITCH_MAPS = [(26, 57), (26, 58), (26, 59), (26, 60)]

# ---- the Pokémon Mansion: plan over (floor, switch on/off) with the floors' blocks as Red's scripts set them
MANSION_REPL = {  # map: (switch off, switch on) [(block x, block y, block)]  (pokered scripts/PokemonMansion*.asm)
    (26, 57): ([(12, 6, 0x0E), (8, 3, 0x2D), (10, 8, 0x2D), (13, 13, 0x2D)], [(12, 6, 0x2D), (8, 3, 0x0E), (10, 8, 0x0E), (13, 13, 0x0E)]),
    (26, 58): ([(4, 2, 0x0E), (9, 4, 0x54), (3, 11, 0x5F)], [(4, 2, 0x5F), (9, 4, 0x0E), (3, 11, 0x0E)]),
    (26, 59): ([(7, 2, 0x0E), (7, 5, 0x5F)], [(7, 2, 0x5F), (7, 5, 0x0E)]),
    (26, 60): ([(13, 8, 0x0E), (6, 11, 0x0E), (4, 3, 0x5F), (8, 8, 0x54)], [(13, 8, 0x2D), (6, 11, 0x5F), (4, 3, 0x0E), (8, 8, 0x0E)])}
MANSION_ARRIVE = {((26, 57), 16, 14), ((26, 58), 18, 14)}   # where the 3F holes land (not warps)
def mansion_grid(b, k, on):
    import bot as _b
    r = b.db.r; h = b.db.maps[k]['hdr']; a = _b._attrs(r, h); w, hh = a['w'], a['h']
    bo = a['blkbank'] * 0x4000 + a['blk'] - 0x4000
    blk = {(i % w, i // w): r[bo + i] for i in range(w * hh)}
    for x, y, v in MANSION_REPL[k][on]: blk[(x, y)] = v
    co = _b._PM.Tilesets(r, _b._Space(r)).coll_off(r[h + 1])
    G = _b._Grid([0] * (2 * w) for _ in range(2 * hh))
    for (bx, by), v in blk.items():
        for q in range(4): G[2 * by + q // 2][2 * bx + q % 2] = r[co + 4 * v + q]
    return G
def mansion_state(b):
    k = b.where()[0]; L = live_grid(b)
    for on in (0, 1):
        if [list(r) for r in mansion_grid(b, k, on)] == [list(r) for r in L]: return on
    d = [sum(x != y for r1, r2 in zip(mansion_grid(b, k, on), L) for x, y in zip(r1, r2)) for on in (0, 1)]
    return 0 if d[0] <= d[1] else 1
def mansion_plan(b, target, on, cells=None):
    import bot as _b
    from collections import deque
    k, x, y = b.where(); GG = {}
    def G(k, on):
        if (k, on) not in GG: GG[(k, on)] = mansion_grid(b, k, on)
        return GG[(k, on)]
    def node(k, on, starts):
        R = _b._reach_set(G(k, on), list(starts)); return (k, on, min(R)), R
    n0, R0 = node(k, on, [(x, y)]); prev = {n0: None}; q = deque([(n0, R0)])
    while q:
        n, R = q.popleft(); k, on, _ = n
        if k == target and (not cells or any(c in R for c in cells)):
            path = []
            while prev[n]: p, act = prev[n]; path.append(act); n = p
            return path[::-1]
        near = lambda x, y: any((x + dx, y + dy) in R for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)))
        nxt = []
        for i, (wx, wy, idx, g, m) in enumerate(b.db.warps(k)):
            if (k, wx, wy) in MANSION_ARRIVE: continue
            if (g, m) not in MANSION_REPL or not near(wx, wy) or idx - 1 >= len(b.db.warps((g, m))): continue
            ax, ay = b.db.warps((g, m))[idx - 1][:2]
            nxt.append((('warp', k, wx, wy, on), (g, m), on, [(ax, ay)]))
        for sx, sy in [(c[1], c[0]) for _, c in b.db.maps[k]['ev']['bgs'] if c[2] == 1]:
            if (sx, sy + 1) in R: nxt.append((('press', k, sx, sy, on), k, 1 - on, [(sx, sy + 1)]))
        for act, k2, on2, st in nxt:
            n2, R2 = node(k2, on2, st)
            if n2 not in prev: prev[n2] = (n, act); q.append((n2, R2))
    return None
def mansion_solve(b, target=(26, 60), steps=40, cells=None):
    import bot as _b
    for i in range(steps):
        k = b.where()[0]
        if k == target and (not cells or (on_ := mansion_state(b)) is not None and
                            any(c in __import__('bot')._reach_set(mansion_grid(b, k, on_), [b.where()[1:]]) for c in cells)): return True
        if k not in MANSION_REPL: tour(b, (26, 57)); continue
        on = mansion_state(b); p = mansion_plan(b, target, on, cells)
        print('  mansion', b.where(), 'switch', on, 'plan', [a[0] + str(a[2:4]) for a in (p or [])], flush=True)
        if not p: return False
        for m in MANSION_REPL: _b._GC[b.db.maps[m]['hdr']] = mansion_grid(b, m, on)
        a = p[0]
        if a[0] == 'warp': b.go_warp_xy(a[2], a[3])
        else: press_switch(b, a[2], a[3])
        b.clear_text(shots=False); ev(b, 10)
        print('   ->', a[0], a[2:4], 'now', b.where(), flush=True)
    return b.where()[0] == target

# ---- region-aware planning inside a building (Silph Co.'s pads, rooms behind doors): which floor *and which room*
def region_plan(b, target, cells, maps, people=True):
    import bot as _b
    from collections import deque
    k, x, y = b.where()
    def node(k, starts):
        G0 = _b.grid_of(b.db.r, b.db.maps[k]['hdr']); G = _b._Grid([list(r) for r in G0])
        stop = {(w[0], w[1]) for w in b.db.warps(k)} | ({(o[2] - 4, o[1] - 4) for o in b.db.objs(k)} if people else set())   # pads move you on; people stand
        for (sx, sy) in stop - set(starts):
            if 0 <= sy < len(G) and 0 <= sx < len(G[0]): G[sy][sx] = 0x07
        R = _b._reach_set(G, list(starts)); return (k, min(R), len(R)), R      # (a pad's landing spot reaches more)
    n0, R0 = node(k, [(x, y)]); prev = {n0: None}; q = deque([(n0, R0)])
    while q:
        n, R = q.popleft(); k = n[0]
        if k == target and any(c in R for c in cells):
            path = []
            while prev[n]: p, act = prev[n]; path.append(act); n = p
            return path[::-1]
        near = lambda x, y: any((x + dx, y + dy) in R for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)))
        LW = b.live_warps(k)
        for wx, wy, idx, g, m in b.db.warps(k):
            if (g, m) not in maps or not near(wx, wy) or idx - 1 >= len(b.db.warps((g, m))): continue
            if (wx, wy) not in LW: continue                  # (a warp on plain floor is only an arrival spot)
            ax, ay = b.db.warps((g, m))[idx - 1][:2]
            n2, R2 = node((g, m), [(ax, ay)])
            if n2 not in prev: prev[n2] = (n, (k, wx, wy)); q.append((n2, R2))
    return None
def region_go(b, target, cells, maps, steps=20, people=True, town='SaffronCity'):
    """walk floor by floor (pads, stairs, holes) to the room of `target` that holds one of `cells`"""
    for i in range(steps):
        if b.where()[0] not in maps:
            entry = [m for m in maps if any((w[3], w[4]) == m for w in b.db.warps(b.mapk(town)))]
            tour(b, entry[0] if entry else target, visit=False)
        import bot as _bb
        for m in maps:                                   # other floors: their rooms as built (doors open once the key is had)
            if m != b.where()[0]: _bb._GC.pop(b.db.maps[m]['hdr'], None)
        known_doors(b)
        if REPEL[0]: __import__('honest').use_repel(b)
        live_grid(b)
        p = region_plan(b, target, cells, maps, people)
        if p is None and DOORS[0]:            # (opening doors walks about: only when there is no way yet)
            open_doors(b); p = region_plan(b, target, cells, maps)
        print('  region', b.where(), None if p is None else [a[1:] for a in p], flush=True)
        if p is None: return False
        if not p: return True
        k, wx, wy = p[0]; b.go_warp_xy(wx, wy); b.clear_text(shots=False); ev(b, 10)
    return False

# ---- Strength boulders (Victory Road): a small Sokoban search over the live grid
SPR_BOULDER = 0x5A
REPEL = [False]      # keep a Max Repel working (Victory Road)
def boulder_plan(b, boulders, goal, others=(), limit=60000):
    """pushes [(bx, by, d)] that bring one of the boulders onto `goal` (or None)"""
    import bot as _b
    from collections import deque
    k, x, y = b.where(); G = _b.grid_of(b.db.r, b.db.maps[k]['hdr'])
    warps = {(w[0], w[1]) for w in b.db.warps(k)        # (a carpet: stand on it; a floor arrival spot: not a warp at all)
             if 0x70 <= G[w[1]][w[0]] <= 0x7F and G[w[1]][w[0]] not in (0x70, 0x76, 0x78, 0x7E)}
    def free(c, bs): return (0 <= c[1] < len(G) and 0 <= c[0] < len(G[0]) and G[c[1]][c[0]] in _b.WALK
                            and c not in bs and c not in others)
    def region(p, bs):
        seen = {p}; q = deque([p])
        while q:
            c = q.popleft()
            for d, (dx, dy) in (('U', (0, -1)), ('D', (0, 1)), ('L', (-1, 0)), ('R', (1, 0))):
                n = (c[0] + dx, c[1] + dy)
                if n in seen or not free(n, bs) or n in warps: continue
                if _b.wall_block(G, c[0], c[1], n[0], n[1], d): continue
                seen.add(n); q.append(n)
        return seen
    D = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}
    start = (frozenset(boulders), (x, y))
    R0 = region((x, y), start[0]); key0 = (start[0], min(R0))
    prev = {key0: None}; q = deque([(start[0], R0, key0)])
    while q and len(prev) < limit:
        bs, R, kk = q.popleft()
        if goal in bs:
            path = []
            while prev[kk]: kk, act = prev[kk]; path.append(act)
            return path[::-1]
        for (bx, by) in bs:
            for d, (dx, dy) in D.items():
                if (bx - dx, by - dy) not in R: continue
                t = (bx + dx, by + dy)
                if t != goal and (not free(t, bs) or t in warps): continue     # (the goal may be a hole)
                if _b.wall_block(G, bx, by, t[0], t[1], d): continue
                nb = frozenset(bs - {(bx, by)} | {t}); R2 = region((bx, by), nb); k2 = (nb, min(R2))
                if k2 in prev: continue
                prev[k2] = (kk, (bx, by, d)); q.append((nb, R2, k2))
    return None
def push_boulders(b, boulders, goal, others=(), minhp=0.55):
    """carry out boulder_plan: walk behind the boulder, use Strength (A on it: yes), push"""
    D = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}
    live_grid(b)
    p = boulder_plan(b, boulders, goal, others)
    print('  boulder plan to', goal, None if p is None else len(p), flush=True)
    if p is None: return None
    bs = set(boulders)
    import honest as _H
    k0map = b.where()[0]
    for (bx, by, d) in p:
        p0 = _H.party(b)[0]
        if p0['hp'] < p0['maxhp'] * minhp:
            print('  boulders: the lead is worn out', p0['hp'], flush=True); return 'heal'
        dx, dy = D[d]; sx, sy = bx - dx, by - dy; moved = False
        if REPEL[0]: _H.use_repel(b)
        for attempt in range(6):
            if b.in_battle(): b.battle()
            if b.textbox(): ev(b, 10)
            p0 = _H.party(b)[0]
            if p0['hp'] < p0['maxhp'] * minhp or b.where()[0] != k0map:
                print('  boulders: the lead is worn out', p0['hp'], b.where(), flush=True); return 'heal'
            if not safe_goto(b, sx, sy, block=bs | set(others), tries=12, allow={(sx, sy)}):
                continue
            b.face(d); b.wait(10)
            b.press('A', 40)                      # 「かいりきを つかいますか？」 -> はい (or its text when already used)
            for i in range(8):
                if b.in_battle(): break
                if b.has('はい') and b.has('いいえ'): b.press('A', 40); continue
                if b.textbox(): b.press('A', 30); continue
                break
            if b.in_battle(): continue
            for t in range(3):
                b.g.down(d); b.wait(8); b.g.up(d)
                for w in range(10):                    # the boulder slides for a while: wait until it stands still
                    b.wait(12); op = b.objpos()
                    if (bx, by) not in op: break
                b.wait(30)
                if b.in_battle(): break
                if b.textbox(): ev(b, 10)
                op = b.objpos()
                if (bx, by) not in op: moved = (bx + dx, by + dy) in op or True; break
            if moved: break
        if not moved:
            print('  boulder did not move', (bx, by), d, b.where(), b.objpos(), flush=True); return False
        bs.discard((bx, by)); bs.add((bx + dx, by + dy))
        live_grid(b)
    return True
