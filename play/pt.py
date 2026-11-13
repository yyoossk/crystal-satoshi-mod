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
        b.g.pokes(o + 0x22, [1, 0x5E, 1, 0x5E])               # HP 350/350
        b.g.pokes(o + 0x26, [0, 250] * 5)
def talk_map(b, skip=()):
    """talk to every person of the map's object table: walk near the start position, then talk to the nearest one"""
    k = b.where()[0]; got = []
    for o in b.db.objs(k):
        x0, y0 = o[2] - 4, o[1] - 4
        if (x0, y0) in skip: continue
        for dx, dy in ((0, 2), (0, -2), (2, 0), (-2, 0), (0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, -1), (0, 3), (3, 0)):
            if b.path(x0 + dx, y0 + dy) is not None and b.goto(x0 + dx, y0 + dy): break
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
        def gt(s, *a, **k):
            if getattr(s, 'norepel', False) is False and s.peek(0xFF70)[0] & 7 in (0, 1): s.g.poke(W_REPEL, 250)
            return og(s, *a, **k)
        _b.Bot.goto = gt
        ob = _b.Bot.battle
        def bt(s, *a, **k):
            r = ob(s, *a, **k)
            s.bank1(); n = s.peek(0xDC9D)[0]
            for i in range(min(n, 6)): s.g.pokes(0xDCA5 + 0x30 * i + 0x17, [0xE0] * 4)    # PP back (the bot keeps one move)
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
            snap(b); talk_map(b); b.g.save_state(ST % ('%s_%d_%d' % (b.tag, k[0], k[1])))
        if k == target: return True
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
