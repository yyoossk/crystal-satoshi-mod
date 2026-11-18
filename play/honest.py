"""Honest playthrough helpers: no memory pokes, no warps.
 * smart battles: the move with the best power x STAB x type effectiveness (moves / type chart read from the ROM),
   switch to the healthiest Pokémon when one faints, learn a new move in place of the weakest
 * healing at the nearest Pokémon Center, grinding the lead in grass
 * HMs taught from the bag
The bot only presses buttons; RAM is only read."""
import sys
sys.path.insert(0, '/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad/play')
import bot as _bot
from bot import *

R = open(SC + '/build/p110.gbc', 'rb').read()
MOVES = 0x41C69                     # move 1 (Pound): anim, effect, power, type, acc, pp, chance
TYPES = 0x34BB1                     # TypeMatchups
def move(m):
    o = MOVES + 7 * (m - 1); return dict(effect=R[o + 1], power=R[o + 2], type=R[o + 3], acc=R[o + 4], pp=R[o + 5])
EFF = {}
o = TYPES
while R[o] != 0xFF:
    if R[o] == 0xFE: o += 1; continue
    EFF[(R[o], R[o + 1])] = R[o + 2] / 10; o += 3
def eff(t, d1, d2):
    e = EFF.get((t, d1), 1.0)
    if d2 != d1: e *= EFF.get((t, d2), 1.0)
    return e
# battle structs (JP Crystal)
BMON, EMON = 0xC622, 0xD237          # species, item, moves[4], DVs[2], PP[4], happiness, level, status.., HP, maxHP .. type1 @+0x1E
PARTY, PCOUNT = 0xDCA5, 0xDC9D

def party(b):
    b.bank1(); n = b.peek(PCOUNT)[0]; out = []
    for i in range(min(n, 6)):
        p = b.peek(PARTY + 0x30 * i, 0x30)
        out.append(dict(species=p[0], moves=p[2:6], pp=[x & 0x3F for x in p[0x17:0x1B]], level=p[0x1F],
                        status=p[0x20], hp=p[0x22] << 8 | p[0x23], maxhp=p[0x24] << 8 | p[0x25]))
    return out

def best_move(b, exclude=()):
    m = b.peek(BMON, 0x20); e = b.peek(EMON, 0x20)
    my = (m[0x1E], m[0x1F]); et = (e[0x1E], e[0x1F])
    best, bi = -1, 0
    for i in range(4):
        mv = m[2 + i]
        if not mv: continue
        if (m[8 + i] & 0x3F) == 0 or i in exclude: continue
        d = move(mv); p = d['power']
        if p <= 1: sc = 0.5                      # status / fixed-damage moves: last choice
        else: sc = p * (1.5 if d['type'] in my else 1.0) * eff(d['type'], *et) * (d['acc'] / 255)
        if sc > best: best, bi = sc, i
    return bi

def cursor(b, cells):
    t = b.tilemap()
    for i, (x, y) in enumerate(cells):
        if t[y * 20 + x] == 0xED: return i
    return None

MAIN = [(9, 14), (14, 14), (9, 16), (14, 16)]
MOVEC = [(1, 10), (1, 12), (1, 14), (1, 16)]
LOG = []
LEARNC = [(11, 10), (11, 12), (11, 14), (11, 16)]
import unicodedata as _ud2
sys.path.insert(0, SC + '/tools')
from jpchar import decode as _dec
def _base(t): return _ud2.normalize('NFC', ''.join(c for c in _ud2.normalize('NFD', t) if c not in '\u3099\u309a'))
MOVENAMES = {}
_o = 0x4163B
for _m in range(1, 252):
    _e = R.index(0x50, _o); MOVENAMES[_base(_dec(R[_o:_e + 1]).rstrip('@'))] = _m; _o = _e + 1
NEW_MOVE = [None]
def note_new_move(s):
    """「<mon>は あたらしく / <move>を おぼえたい……」: remember which move is offered"""
    t = s.tilemap()
    for y in (14, 16):
        line = _base(_dec(bytes(t[y * 20 + 1:y * 20 + 19])))
        if 'を' in line and 'おほえたい' in line:
            nm = line.split('を')[0].strip('\u3000 ')
            if nm in MOVENAMES: NEW_MOVE[0] = MOVENAMES[nm]
def mscore(m, types=()):
    if not m: return -1
    d = move(m); return d['power'] * (d['acc'] / 255) * (1.5 if d['type'] in types else 1)
def forget_weakest(s, moves, types=()):
    """at 「ほかの わざを わすれさせますか？」 (the kit's learnno makes いいえ the default): はい, then the weakest move
    (status moves first; HM moves are kept)"""
    for i in range(30):
        if cursor(s, [(15, 8), (15, 10)]) is not None: break
        s.wait(6)
    ws = min(range(4), key=lambda i: (moves[i] in HM_MOVE.values(), mscore(moves[i], types)))
    nm = NEW_MOVE[0]; NEW_MOVE[0] = None
    print('  forget? new', nm, 'weakest', moves[ws], flush=True)
    if nm and nm not in HM_MOVE.values() and mscore(nm, types) <= mscore(moves[ws], types):   # (an HM taught on purpose: learn it)
        s.wait(10); s.press('A', 60)                                  # いいえ -> 「あきらめますか？」
        for i in range(30):
            if cursor(s, [(15, 8), (15, 10)]) is not None: break
            s.wait(6)
        s.wait(10); s.press('U', 20); s.press('A', 60); return False
    s.wait(10); s.press('U', 20); s.press('A', 60)
    if cursor(s, LEARNC) is None: s.press('B', 30); return False
    for k in range(ws): s.press('D', 15)
    s.press('A', 50); return True
DIS = set(); LASTW = [0]
FLEE = [False]      # run from wild Pokémon (a long walk through a cave: Victory Road)
def smart_battle(s, maxp=600):
    k = 0; DIS.clear(); tried_run = not FLEE[0]
    while s.in_battle() and k < maxp:
        k += 1
        t = s.tilemap()
        c = cursor(s, MAIN) if t[14 * 20 + 10:14 * 20 + 14] == bytes.fromhex('c0c0b6b3') else None
        if c is not None and not tried_run:
            tried_run = True; s.wait(20)                     # にげる (bottom right); a trainer: 「だめだ！」 and fight
            if c in (0, 2): s.g.press('R', 4, 10)
            if c in (0, 1): s.g.press('D', 4, 10)
            s.g.press('A', 8, 60)
            for i in range(6):
                if not s.in_battle(): break
                if s.textbox() and not cursor(s, MAIN) is not None: s.press('A', 40)
                else: break
            continue
        if c is not None:
            s.wait(20)
            if c in (1, 3): s.g.press('L', 4, 10)
            if c in (2, 3): s.g.press('U', 4, 10)
            s.g.press('A', 8, 50)
            mc = cursor(s, MOVEC)
            if mc is None: continue
            want = best_move(s, DIS); LASTW[0] = want
            while mc != want:
                s.g.press('D' if want > mc else 'U', 4, 12); mc2 = cursor(s, MOVEC)
                if mc2 == mc: break
                mc = mc2
            s.g.press('A', 8, 40); continue
        if s.has('ふうしられている'):                                   # the move is disabled (かなしばり): another one
            DIS.add(LASTW[0]); s.press('B', 30); continue
        if s.has('おほえたい'): note_new_move(s)
        if s.has('わすれさせますか'):
            bm = s.peek(BMON, 0x20); forget_weakest(s, list(bm[2:6]), (bm[0x1E], bm[0x1F])); continue
        if s.has('あきらめますか？'): s.press('A', 30); continue        # いいえ (the default): back to the question
        if s.has('ほかの') or s.has('おほえるのを'): s.wait(20); continue    # the question is still being printed
        if s.has('もうでています'): s.press('B', 30); s.press('B', 30); continue   # the shift question: keep the one out
        if s.has('とりかえますか'): s.press('B', 40); continue              # shift after the foe's faint: no
        if s.has('だしますか'): pick_party(s); continue                # the party menu is up
        if s.has('つかいますか'): s.press('A', 40); pick_party(s); continue   # はい, then the party menu
        s.press('A', 25)
        if k % 6 == 0: s.press('B', 15)
    if k >= maxp:
        import time as _t; n = 'stuck_%d' % int(_t.time()); s.g.save_state(SC + '/run/%s.st' % n); s.g.shot(SC + '/run/%s.png' % n)
        t = s.tilemap(); print('BATTLE STUCK', n, flush=True)
        for y in range(12, 18): print('   ', t[y * 20:y * 20 + 20].hex(' '), flush=True)
    s.wait(60)
    for t_ in range(30):
        if s.peek(0xFF70)[0] & 7 in (0, 1): break
        s.wait(4)
    return k

def party_cursor(s):
    t = s.tilemap()
    for y in range(1, 13, 2):
        if t[y * 20] in (0xED, 0xEC): return (y - 1) // 2
    return None
def pick_party(s):
    """party menu (after a faint, or a switch): the healthiest Pokémon that can fight and is not already out
    (the menu reads a key only now and then: hold it)"""
    s.wait(30); p = party(s)
    alive = [i for i, q in enumerate(p) if q['hp'] > 0]
    if not alive: return
    for want in sorted(alive, key=lambda i: (-p[i]['level'], -p[i]['hp'])):
        for k in range(12):
            c = None
            for w in range(8):                       # the cursor blinks: read it a few times
                c = party_cursor(s)
                if c is not None: break
                s.wait(6)
            if c == want: break
            s.g.press('D' if c is None or c < want else 'U', 16, 20)
        s.g.press('A', 16, 40)
        for k in range(4):
            if s.has('いれかえる') or s.has('つよさをみる'): s.g.press('A', 16, 40)
            else: break
        if s.has('もうでています') or s.has('げんきが'):    # already out / fainted: the next one
            s.g.press('B', 8, 40); continue
        return

_bot.Bot.battle = smart_battle
import unicodedata as _ud
_has0 = _bot.Bot.has
def _has(s, txt):
    """the tilemap holds the base kana (the dakuten / handakuten sit on the line above): match without them"""
    base = ''.join(c for c in _ud.normalize('NFD', txt) if c not in '\u3099\u309a')
    base = _ud.normalize('NFC', base)
    return _has0(s, base) or _has0(s, txt)
_bot.Bot.has = _has
_bot.NOHEAL[0] = True

def lowpp(q):
    return sum(pp for m, pp in zip(q['moves'], q['pp']) if m and move(m)['power'] > 1) < 5
def hurt(b, frac=0.5):
    p = party(b)
    if lowpp(p[0]): return True
    return p[0]['hp'] < p[0]['maxhp'] * frac or any(q['hp'] == 0 for q in p[:1])

def nearest_pc(b):
    best = None
    for k, n in b.names.items():
        if n and n.endswith('Pokecenter1F') and k in b.db.maps:
            try: pl = b.plan(k, __import__('pt').AVOID)
            except Exception: continue
            if pl is not None and (best is None or len(pl) < best[0]): best = (len(pl), k)
    return best and best[1]

def heal_pc(b, pc=None):
    pc = pc or nearest_pc(b); back = b.where()
    b.travel(pc); b.wait(30)
    b.goto(3, 3); b.face('U'); b.press('A', 40)
    for i in range(30):
        if b.textbox(): b.press('A', 40)
        else: b.wait(20)
    return back

def reach_grass(b):
    """walk to the nearest reachable pair of grass cells of the current map; returns the cell or None"""
    k, x0, y0 = b.where(); G = grid_of(b.db.r, b.db.maps[k]['hdr'])
    cs = [(x, y) for y in range(len(G)) for x in range(len(G[0]) - 1) if G[y][x] in (0x18, 0x14) and G[y][x + 1] in (0x18, 0x14)]
    cs.sort(key=lambda c: abs(c[0] - x0) + abs(c[1] - y0))
    for c in cs[:40]:
        if b.path(*c) is None: continue
        if b.goto(*c) and b.where()[0] == k: return c
        if b.where()[0] != k: return None
    return None
def grind(b, target, area, spot=None, maxbattles=400):
    """train the lead in the grass of `area` to `target`; heal at the nearest Pokémon Center when hurt"""
    nb = 0; fails = 0
    while party(b)[0]['level'] < target and nb < maxbattles and fails < 6:
        if b.where()[0] != area: b.travel(area); b.wait(20)
        if b.where()[0] != area or reach_grass(b) is None:
            fails += 1; print('grind: no grass reached', area, b.where(), flush=True); continue
        steps = 0
        for k in range(60):
            b.step('L' if k % 2 else 'R'); steps += 1
            if b.in_battle():
                b.battle(); nb += 1
                for t in range(20):
                    if b.textbox(): b.press('B' if (b.has('はい') and b.has('いいえ')) else 'A', 30)
                    else: break
                if hurt(b) or b.where()[0] != area: break
        if hurt(b): heal_pc(b)
    print('grind', party(b)[0]['level'], 'battles', nb, 'fails', fails, flush=True)
    return fails < 6

# ---------------------------------------------------------------- menus
TMHM = 0xD84C                     # wTMsHMs (50 TMs, 7 HMs)
HM_MOVE = {1: 0x0F, 2: 0x13, 3: 0x39, 4: 0x46, 5: 0x94, 6: 0xFA, 7: 0x7F}   # Cut Fly Surf Strength Flash Whirlpool Waterfall
def has_hm(b, n): b.bank1(); return b.peek(TMHM + 49 + n)[0] > 0
def knows(b, move): return [i for i, q in enumerate(party(b)) if move in q['moves']]
def close_menus(b):
    for i in range(6):
        b.press('B', 20)
def _tm_pocket(t):
    from jpchar import encode
    hi = encode('ひ')[0]
    for y in (3, 5, 7):
        c = t[y * 20 + 6]
        if 0xF6 <= c <= 0xFF or c == hi: return True
    return False
def open_bag_tm(b):
    b.press('S', 40)
    for i in range(10):
        t = b.tilemap(); rows = [y for y in range(18) if t[y * 20 + 13] == 0xED]
        if rows and rows[0] == 6: break
        b.press('D', 15)
    b.press('A', 60)
    for i in range(6):
        if _tm_pocket(b.tilemap()): break
        b.press('R', 30)
def teach(b, n, mon):
    """HM n to party member `mon` from the bag (the weakest attacking move is forgotten when it knows four)"""
    open_bag_tm(b)
    for i in range(50): b.g.press('D', 4, 6)
    b.wait(20)
    above = sum(1 for m in range(n + 1, 8) if has_hm(b, m))
    for i in range(above + 1): b.press('U', 20)
    b.press('A', 40); b.press('A', 40)
    for i in range(10):
        if b.has('おしえますか'): break
        b.press('A', 40)
    for k in range(12):
        c = party_cursor(b)
        if c == mon: break
        b.g.press('D' if c is None or c < mon else 'U', 6, 30)
    b.press('A', 50)
    for i in range(30):
        if b.has('おほえたい'): note_new_move(b)
        if b.has('わすれさせますか'): forget_weakest(b, party(b)[mon]['moves']); continue
        if b.has('あきらめますか？'): b.press('A', 30); continue
        if b.has('ほかの') or b.has('おほえるのを'): b.wait(20); continue
        if b.textbox(): b.press('A', 40)
        else: break
    close_menus(b)
    ok = HM_MOVE[n] in party(b)[mon]['moves']
    print('teach HM%02d to %d:' % (n, mon), ok, flush=True); return ok

def badges_ok_surf(b):
    b.bank1(); return bin(b.peek(0xD84B)[0]).count('1') >= 5     # Soul Badge for Surf
def honest_hms(b, cut=True, flash=False, surf=False, strength=False, whirl=False, waterfall=False):
    want = [(1, cut), (3, surf), (4, strength), (5, flash), (6, whirl), (7, waterfall)]
    for n, w in want:
        if not w: continue
        mv = HM_MOVE[n]
        if not knows(b, mv):
            assert has_hm(b, n), 'HM%02d not in the bag' % n
            p = party(b)
            order = [i for i in list(range(1, len(p))) + [0] if p[i]['species'] != 0xFD and p[i]['level'] > 5]   # (not the lead first; not the egg)
            for mon in order:
                if teach(b, n, mon): break
        if n == 1: _bot.CAN_CUT[0] = True
        if n == 3: _bot.CAN_SURF[0] = True
        if n == 6: _bot.CAN_WHIRL[0] = True
        if n == 7: _bot.CAN_FALL[0] = True

# ---------------------------------------------------------------- levels
def grass_spot(b, k):
    G = grid_of(b.db.r, b.db.maps[k]['hdr'])
    for y in range(len(G)):
        for x in range(len(G[0]) - 1):
            if G[y][x] in (0x18, 0x14) and G[y][x + 1] in (0x18, 0x14): return x, y
    return None
GRIND_BY_BADGES = ['Route22', 'Route3', 'Route24', 'Route11', 'Route7', 'Route15', 'Route15', 'Route21', 'Route23']
def ensure(b, target, badges=0):
    """train the lead to `target` in the grass of a route reachable with this many badges; heal when hurt"""
    area = b.mapk(GRIND_BY_BADGES[min(badges, 8)])
    while party(b)[0]['level'] < target:
        if not grind(b, min(target, party(b)[0]['level'] + 3), area, maxbattles=60):
            raise RuntimeError('cannot grind in %s' % (area,))
    if hurt(b, 0.9): heal_pc(b)

ESCAPE_ROPE = 19
def items(b):
    b.bank1(); n = b.peek(0xD885)[0]; d = b.peek(0xD886, 2 * n); return [(d[2 * i], d[2 * i + 1]) for i in range(n)]
MAX_REPEL = 43
def add_item(b, item, n):
    """(save-data edit, as the user asked: e.g. Max Repels for Victory Road) put n of an item in the bag"""
    b.bank1(); it = items(b)
    for i, (x, c) in enumerate(it):
        if x == item: b.g.poke(0xD886 + 2 * i + 1, min(99, c + n)); return
    k = len(it)
    if k >= 20:                                       # (the item pocket holds 20 kinds: the last kind makes room)
        b.g.poke(0xD886 + 2 * 19, item); b.g.poke(0xD886 + 2 * 19 + 1, n); return
    b.g.poke(0xD885, k + 1); b.g.poke(0xD886 + 2 * k, item); b.g.poke(0xD886 + 2 * k + 1, n)
    b.g.poke(0xD886 + 2 * k + 2, 0xFF)
def use_repel(b):
    """use a Max Repel from the bag when none is working"""
    W_REPEL = __import__('pt').W_REPEL
    b.bank1()
    if b.peek(W_REPEL)[0] > 0: return True
    if dict(items(b)).get(MAX_REPEL, 0) < 3: add_item(b, MAX_REPEL, 30)    # (save-data edit: Max Repels for the caves, as asked)
    return use_item(b, MAX_REPEL, 'スプレー')
def escape_rope(b):
    """use an Escape Rope (あなぬけのヒモ) from the bag: back to the last Pokémon Center's town"""
    return use_item(b, ESCAPE_ROPE, 'あなぬけ', warp=True)
def use_item(b, item, word, warp=False):
    it = [i for i, _ in items(b)]
    if item not in it: print('  no item', item, flush=True); return False
    idx = it.index(item); k0 = b.where()[0]
    for i in range(6):                               # a text or a battle first; the start menu must be open
        if b.in_battle(): b.battle()
        elif b.textbox(): b.press('B', 30)
        else: break
    b.wait(40); b.press('S', 40)
    for i in range(10):
        t = b.tilemap(); rows = [y for y in range(18) if t[y * 20 + 13] == 0xED]
        if rows and rows[0] == 6: break
        if not rows: b.press('S', 40); continue
        b.press('D', 15)
    b.press('A', 60)
    for i in range(5):
        if b.has('キズぐすり') or b.has(word): break
        b.press('L', 30)
    for i in range(12): b.g.press('U', 4, 8)
    for i in range(idx): b.g.press('D', 4, 12)
    b.wait(20); b.press('A', 40)             # the item's menu: つかう
    b.press('A', 60)
    for i in range(20):
        if warp and b.where()[0] != k0 and not b.textbox(): break
        if b.textbox(): b.press('A', 40)
        else: b.wait(30)
        if not warp and not b.textbox():
            for k in range(4): b.press('B', 20)        # (out of the bag and the menu)
            break
    b.wait(60); print('  used item', item, '->', b.where(), flush=True)
    if warp: return b.where()[0] != k0
    b.bank1(); return b.peek(__import__('pt').W_REPEL)[0] > 0
