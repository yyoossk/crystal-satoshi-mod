"""playthrough check: new game -> Pewter Gym, walking only (no warps / pokes)"""
import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
import bot as _bot
_bot.NOHEAL[0] = True
ROM = 'p75'
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
AVOID = tuple((20, i) for i in range(1, 8))
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
        p = b.plan(target, AVOID)
        if not p: print('no plan', k, flush=True); return False
        k0, kind, arg, d = p[0]
        if kind == 'warp':
            wx, wy = b.db.warps(k0)[arg][:2]; b.go_warp_xy(wx, wy)
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
def visit_town(b, town, skip=()):
    """the town's people and signs, then every building whose door is in the town (people, back out)"""
    town = b.mapk(town)
    if b.where()[0] != town: b.travel(town); b.wait(20)
    print('== town', town, b.where(), mus(b), flush=True)
    talk_map(b); read_signs(b)
    doors = []
    for w in b.db.warps(town):
        t = (w[3], w[4])
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
        blk = set(b.objpos()) | bad | ({(w[0], w[1]) for w in b.db.warps(k)} - {(tx, ty)})
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
def safe_goto(b, tx, ty, block=(), tries=8):
    """walk a path that never touches a warp tile (but the target) or the given tiles; replan when a step fails"""
    k = b.where()[0]
    for t in range(tries):
        if b.textbox() or b.in_battle(): ev(b, 20)
        k2, x, y = b.where()
        if k2 != k: return False
        if (x, y) == (tx, ty): return True
        av = ({(w[0], w[1]) for w in b.db.warps(k)} | set(block) | set(b.objpos())) - {(tx, ty), (x, y)}
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
        if k2 != k: return False
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
        if not found: return False
        path = []; p = (tx, ty)
        while prev[p]: p, d = prev[p][0], prev[p][1]; path.append((d, p))
        path.reverse()
        d, p = path[0]
        b.step(d); b.wait(30)
        for i in range(10):
            p0 = b.where(); b.wait(12)
            if b.where() == p0: break
        if b.where()[1:] == (x, y) and not b.textbox() and not b.in_battle():
            dx, dy = D[d]; bad.add((x + dx, y + dy))
    return b.where()[1:] == (tx, ty)
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
        if not sw: return False
        pressed = False
        for s in sw:
            if press_switch(b, *s):
                pressed = True; live_grid(b)
                if b.plan(target, AVOID): break
        if not pressed: return False
    return b.where()[0] == b.mapk(target)
