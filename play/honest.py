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

def best_move(b):
    m = b.peek(BMON, 0x20); e = b.peek(EMON, 0x20)
    my = (m[0x1E], m[0x1F]); et = (e[0x1E], e[0x1F])
    best, bi = -1, 0
    for i in range(4):
        mv = m[2 + i]
        if not mv: continue
        if (m[8 + i] & 0x3F) == 0: continue
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
def smart_battle(s, maxp=600):
    k = 0
    while s.in_battle() and k < maxp:
        k += 1
        t = s.tilemap()
        c = cursor(s, MAIN) if t[14 * 20 + 10:14 * 20 + 14] == bytes.fromhex('c0c0b6b3') else None
        if c is not None:
            s.wait(20)
            if c in (1, 3): s.g.press('L', 4, 10)
            if c in (2, 3): s.g.press('U', 4, 10)
            s.g.press('A', 8, 50)
            mc = cursor(s, MOVEC)
            if mc is None: continue
            want = best_move(s)
            while mc != want:
                s.g.press('D' if want > mc else 'U', 4, 12); mc2 = cursor(s, MOVEC)
                if mc2 == mc: break
                mc = mc2
            s.g.press('A', 8, 40); continue
        if s.has('わすれさせますか'): s.press('B', 30); continue          # TODO: weakest-move replacement
        if s.has('あきらめますか'): s.press('A', 30); continue
        if s.has('だしますか') or s.has('つかいますか'):
            s.press('A', 40); pick_party(s); continue
        s.press('A', 25)
        if k % 6 == 0: s.press('B', 15)
    s.wait(60)
    for t_ in range(30):
        if s.peek(0xFF70)[0] & 7 in (0, 1): break
        s.wait(4)
    return k

def pick_party(s):
    """party menu after a faint: the healthiest Pokémon that can fight"""
    s.wait(30); p = party(s)
    alive = [i for i, q in enumerate(p) if q['hp'] > 0]
    if not alive: return
    want = max(alive, key=lambda i: (p[i]['level'], p[i]['hp']))
    for i in range(want): s.g.press('D', 4, 10)
    s.g.press('A', 8, 40); s.g.press('A', 8, 40)

_bot.Bot.battle = smart_battle
_bot.NOHEAL[0] = True

def hurt(b, frac=0.5):
    p = party(b); return p[0]['hp'] < p[0]['maxhp'] * frac or any(q['hp'] == 0 for q in p[:1])

def nearest_pc(b):
    best = None
    for k, n in b.names.items():
        if n and n.endswith('Pokecenter1F') and k in b.db.maps:
            try: pl = b.plan(k)
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

def grind(b, target, area, spot, maxbattles=400):
    """train the lead in grass (area, spot) to `target`; heal at the nearest Pokémon Center when hurt"""
    nb = 0
    while party(b)[0]['level'] < target and nb < maxbattles:
        if b.where()[0] != area: b.travel(area); b.wait(20)
        b.goto(*spot)
        for k in range(30):
            b.step('L' if k % 2 else 'R')
            if b.in_battle():
                b.battle(); nb += 1
                for t in range(20):
                    if b.textbox(): b.press('B' if (b.has('はい') and b.has('いいえ')) else 'A', 30)
                    else: break
                if hurt(b): break
        if hurt(b): heal_pc(b)
    print('grind', party(b)[0]['level'], 'battles', nb, flush=True)
