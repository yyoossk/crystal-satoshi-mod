"""Honest playthrough driver: from the honest state s14v (new game -> Route 22 rival, no pokes) onward.
No memory writes, no warps: only button presses. Levels are trained in grass, HMs taught from the bag,
healing at Pokémon Centers. Each stage loads the previous stage's state and saves its own (pt_h_<name>.st).
usage: python3 play/hon.py FIRST_STAGE [LAST_STAGE]"""
import sys, time, os
sys.path.insert(0, '/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad/play')
import pt as P
from pt import *
import honest as H
import bot as _bot

HST = SC + '/play/pt_h_%s.st'
ISSUES = open(SC + '/run/hon_issues.log', 'a')
def issue(*a):
    s = ' '.join(str(x) for x in a); print('ISSUE', s, flush=True); ISSUES.write(time.strftime('%H:%M ') + s + '\n'); ISSUES.flush()

# --- healing hook: before any travel, heal when the lead is hurt or anyone fainted
_tr = _bot.Bot.travel
_busy = [False]
def travel(s, *a, **k):
    if not _busy[0]:
        p = H.party(s)
        if p and (p[0]['hp'] < p[0]['maxhp'] * 0.45 or any(q['hp'] == 0 for q in p) or H.lowpp(p[0])):
            _busy[0] = True
            try: H.heal_pc(s)
            except Exception as e: issue('heal failed', e)
            _busy[0] = False
    return _tr(s, *a, **k)
_bot.Bot.travel = travel
_ob = _bot.Bot.battle
def _bt(s, *a, **k):
    t = time.time(); e = s.peek(H.EMON, 14); r = _ob(s, *a, **k); p = H.party(s)
    print('  battle %.0fs lv%d hp%d/%d %s vs %d lv%d' % (time.time() - t, p[0]['level'], p[0]['hp'], p[0]['maxhp'], s.where(), e[0], e[13]), flush=True); return r
_bot.Bot.battle = _bt
_oh = H.heal_pc
def _hp(b, *a):
    if b.where()[0] in ((26, 68), (26, 69), (26, 70)): H.escape_rope(b)      # Victory Road: a rope, not the long walk
    t = time.time(); _busy[0] = True
    try: r = _oh(b, *a)
    finally: _busy[0] = False
    print('  heal %.0fs' % (time.time() - t), b.where(), flush=True); return r
H.heal_pc = _hp

# --- a picture (the museum's fossils) closes with B, not A: close anything left open after the talk
def menu_up(b):
    """an info menu (a cursor in the upper half: the badge talk, shop / PC menus) - leave it with B"""
    t = b.tilemap()
    if b.has('かけますか') or b.has('コインが　たりません') or b.has('コインが たりません'): return True   # slot machines
    return any(c == 0xED for c in t[:7 * 20])
_bev = _bot.Bot.ev
def bev(s, n=120, quiet=3, shots=True, key='A'):
    q = 0; k = 0
    while k < min(n, 60):
        if s.in_battle(): s.battle(); q = 0; continue
        if s.textbox():
            s.press('B' if menu_up(s) else key, 40); k += 1; q = 0
        else:
            q += 1
            if q >= quiet: break
            s.wait(50)
    return k
_bot.Bot.ev = bev
def ev2(b, n=80, yes=True):
    """pt.ev, plus: a talk that keeps coming back to the same text/menu (an info menu) is left with B"""
    q = 0; seen = {}
    for i in range(n):
        if b.in_battle(): b.battle(); snap(b); q = 0; continue
        if b.textbox() and menu_up(b): b.press('B', 30); b.press('B', 30); snap(b); continue
        t = bytes(b.tilemap()[12 * 20:])
        if b.textbox() or 0xED in t:
            seen[t] = seen.get(t, 0) + 1
            if seen[t] > 3: b.press('B', 30); b.press('B', 30); snap(b); continue
        if b'\xb4\xd7\xde' in b.tilemap()[14 * 20:]: b.press('B', 30); b.press('B', 30); snap(b); q = 0; continue
        if b.has('ニックネームは'): b.press('S', 30); b.press('A', 40); snap(b); q = 0; continue
        if b.textbox():
            if b.has('はい') and b.has('いいえ') and not yes: b.press('B', 40)
            else: b.press('A', 40)
            snap(b); q = 0
        else:
            q += 1; b.wait(20); snap(b)
            if q >= 3: break
    b.press('B', 20); b.press('B', 20)
P.ev = ev2

# --- heal before talking to a map's people (trainers) when the lead is hurt
_tm = P.talk_map
def talk_map2(b, *a, **k):
    p = H.party(b)
    if p and (p[0]['hp'] < p[0]['maxhp'] * 0.6 or H.lowpp(p[0])):
        here = b.where()[0]; H.heal_pc(b); b.travel(here); b.wait(20)
    return _tm(b, *a, **k)
P.talk_map = talk_map2

# --- goto that knows Red's spinner arrows (pt.fast used to install it; fast is a no-op here)
_og = _bot.Bot.goto
_SPC = {}
def _gt(s, *a, **k):
    m = s.where()[0]
    if m not in _SPC: _SPC[m] = bool(P.spinners(s, m))
    if _SPC[m] and len(a) >= 2: return P.sgoto(s, a[0], a[1], tries=k.get('tries', 60))
    if m not in _PAD: _PAD[m] = any((w[3], w[4]) == m for w in s.db.warps(m))     # Saffron Gym: pads to the same map
    if _PAD[m] and len(a) >= 2: return P.wgoto(s, a[0], a[1], tries=k.get('tries', 80))
    return _og(s, *a, **k)
_PAD = {}
_bot.Bot.goto = _gt

# --- the Pokémon Center 2F (Crystal's link room): its stairs lead back to whichever center, which the planner can't see
PC2F = (20, 1)
def leave_pc2f(b):
    if b.where()[0] == PC2F:
        w = b.db.warps(PC2F)[0]; b.go_warp_xy(w[0], w[1]); b.wait(40); print('left PC 2F', b.where(), flush=True)
_tour = P.tour
def tour2(b, *a, **k):
    leave_pc2f(b); return _tour(b, *a, **k)
P.tour = tour2; tour = tour2
_tr2 = _bot.Bot.travel
def travel3(s, *a, **k):
    leave_pc2f(s)
    if s.where()[0] in P.MANSION_REPL and s.mapk(a[0]) not in P.MANSION_REPL:   # out of the Mansion: its switches
        P.mansion_solve(s, (26, 57), cells=[(5, 26), (6, 26), (26, 26), (27, 26)])
    return _tr2(s, *a, **k)
_bot.Bot.travel = travel3

# --- the old helpers become honest
P.maxparty = lambda b, *a, **k: None
P.fast = lambda b, *a, **k: None
P.SKIPGYM[0] = True
def badges(b): b.bank1(); return bin(b.peek(0xD84B)[0]).count('1')
LV = [16, 24, 28, 34, 42, 46, 50, 54, 62]          # lead level wanted before the next leader (by badge count)
def train(b, extra=0):
    t = LV[min(badges(b), 8)] + extra
    if H.party(b)[0]['level'] < t:
        print('train to', t, flush=True); back = b.where()[0]
        H.ensure(b, t, badges(b))
        b.travel(back); b.wait(20)
        b.g.save_state(HST % (b.tag[2:] + '_tr')); print('saved', b.tag[2:] + '_tr', flush=True)

STAGES = []
def stage(f): STAGES.append(f); return f
def run(name, prev):
    f = [g for g in STAGES if g.__name__ == name][0]
    st = (HST % prev) if prev != 's14v' else ST % 's14v'
    if os.path.exists(HST % (name + '_tr')): st = HST % (name + '_tr'); print('resume after training', flush=True)
    b = Bot(state=st, out=SC + '/run/h_' + name)
    b.tag = 'h_' + name; b.fs = []; b.seen = set()
    t0 = time.time(); print('#### stage', name, 'from', prev, b.where(), [(q['species'], q['level']) for q in H.party(b)], flush=True)
    if H.has_hm(b, 1): H.honest_hms(b, cut=True)          # the bot may cut trees once a party member knows Cut
    if H.has_hm(b, 3) and H.badges_ok_surf(b): H.honest_hms(b, cut=True, surf=True)
    if H.has_hm(b, 4) and badges(b) >= 4: H.honest_hms(b, cut=True, surf=H.has_hm(b, 3) and H.badges_ok_surf(b), strength=True)
    f(b)
    b.g.save_state(HST % name)
    print('#### end', name, b.where(), mus(b), 'badges', badges(b), [(q['species'], q['level']) for q in H.party(b)],
          '%.0fs' % (time.time() - t0), flush=True)
    if b.fs: done(b, last=120, W=12)

# ------------------------------------------------------------------ stages
@stage
def pewter(b):
    train(b)
    tour(b, 'PewterCity'); visit_town(b, 'PewterCity')
@stage
def brock(b):
    if badges(b) >= 1: return
    train(b, 2); H.heal_pc(b)
    gym_try(b, 'PewterGym')
    if badges(b) < 1: issue('no Boulder Badge after the Pewter Gym')
@stage
def mtmoon(b):
    train(b)
    tour(b, 'Route4', skipmaps=[(26, 99)])
@stage
def cerulean(b):
    train(b)
    tour(b, 'CeruleanCity', skipmaps=[(26, 99)]); visit_town(b, 'CeruleanCity', skip=[(7, 17), (26, 72)])
@stage
def misty(b):
    if badges(b) >= 2: return
    train(b, 2); H.heal_pc(b)
    gym_try(b, 'CeruleanGym')
    if badges(b) < 2: issue('no Cascade Badge')

@stage
def bill(b):
    train(b)
    tour(b, (7, 16), skipmaps=[(7, 17)])                 # Route 24 (Nugget Bridge, the rival), Route 25
    tour(b, (26, 51)); print('bill house', b.where(), b.objpos(), flush=True)
    for r in range(3):
        talk_map(b); read_signs(b); ev(b, 30)
    print('after bill', b.where(), b.objpos(), flush=True)
@stage
def rocket(b):
    train(b)
    tour(b, 'CeruleanCity', skipmaps=[(26, 51), (7, 16), (7, 15)])
    tour(b, (26, 72), visit=False); print('house', b.where(), b.objpos(), flush=True); snap(b)
    talk_map(b)
    W = b.db.warps((26, 72)); print('warps', W, flush=True)
    back = [w for w in W if w[1] < 3]
    if back: b.go_warp_xy(back[0][0], back[0][1]); b.wait(40)
    print('yard', b.where(), b.objpos(), flush=True); snap(b); ev(b, 40)
    ps = [p for p in b.objpos() if abs(p[0] - 30) < 4 and p[1] < 12]
    if ps: b.talk_to(*ps[0], n=0); snap(b)
    else: issue('rocket in the yard not found', b.where(), b.objpos())
    for i in range(4): ev(b, 40)
@stage
def vermilion(b):
    train(b)
    tour(b, 'VermilionCity', skipmaps=[(7, 17), (26, 139)])
    visit_town(b, 'VermilionCity')
@stage
def ssanne(b):
    train(b)
    def cabins(K, C):
        ws = [w for w in b.db.warps(K) if (w[3], w[4]) == C]
        for w in ws:
            if b.where()[0] != K: b.travel(K)
            b.go_warp_xy(w[0], w[1]); b.wait(30); b.clear_text(shots=False)
            if b.where()[0] != C: print('  not in', b.where(), flush=True); continue
            print('  room', b.where(), b.objpos(), flush=True); snap(b)
            talk_all(b); ev(b, 20)
            b.travel(K); b.wait(20)
    tour(b, (26, 40), skipmaps=[(12, 3)])
    for K, C in [((26, 41), (26, 48)), ((26, 41), (26, 46)), ((26, 44), (26, 50)), ((26, 42), (26, 49))]:
        tour(b, K, visit=False); print('== corridor', K, b.where(), flush=True)
        if C == (26, 46): tour(b, C); continue
        cabins(K, C)
    tour(b, (26, 45)); tour(b, (26, 47)); ev(b, 60)
    if not H.has_hm(b, 1): issue('no HM01 after the captain')
    tour(b, (26, 40), visit=False)
    for i in range(60):
        if b.textbox(): b.press('A', 30)
        else: b.wait(15)
@stage
def surge(b):
    if badges(b) >= 3: return
    train(b, 2)
    H.honest_hms(b, cut=True)
    b.travel('VermilionCity'); b.wait(30)
    b.goto(15, 17); b.face('D'); b.press('A', 40); ev(b, 30)
    b.goto(15, 19); print('past tree', b.where(), flush=True)
    H.heal_pc(b)
    b.travel('VermilionGym'); b.wait(30)
    solve_cans(b)
    talk_map(b); ev(b, 40)
    if badges(b) < 3: issue('no Thunder Badge')

@stage
def diglett(b):
    train(b)
    H.honest_hms(b, cut=True)
    for t in ['Route11', 'DiglettsCave', 'Route2']:
        r = tour(b, t, skipmaps=[(12, 11), (12, 3)]); print('->', t, r, b.where(), flush=True)
    tour(b, (26, 81)); print('gate', b.where(), b.objpos(), flush=True)
    b.goto(4, 1)
    for i in range(2): b.step('U'); b.wait(20)
    if b.where()[0] != (26, 81) or b.where()[2] == 0: issue('Route 2 gate: stepped into the wall beside the door', b.where())
@stage
def lavender(b):
    train(b)
    H.honest_hms(b, cut=True)
    old = P.AVOID; P.AVOID = P.AVOID + ((18, 2), (26, 104), (26, 106), (25, 2), (26, 100), (26, 101), (26, 102), (26, 103))   # Route 12 (Snorlax), Saffron (guards): Rock Tunnel's way
    r = tour(b, 'LavenderTown', skipmaps=[(12, 11), (12, 3)]); print('->', r, b.where(), flush=True)
    if not r: issue('Lavender not reached', b.where())
    visit_town(b, 'LavenderTown'); P.AVOID = old

@stage
def celadon(b):
    train(b)
    H.honest_hms(b, cut=True)
    gates = [k for k in b.db.maps if k[0] == 26 and any((w[3], w[4]) == b.mapk('SaffronCity') for w in b.db.warps(k))]
    old = P.AVOID; P.AVOID = P.AVOID + tuple(gates) + (b.mapk('SaffronCity'),)
    r = tour(b, 'CeladonCity', skipmaps=[(12, 11), (12, 3)]); print('->', r, b.where(), flush=True)
    visit_town(b, 'CeladonCity')
    P.AVOID = old
@stage
def erika(b):
    if badges(b) >= 4: return
    train(b, 2); H.honest_hms(b, cut=True); H.heal_pc(b)
    gym_try(b, 'CeladonGym')
    if badges(b) < 4: issue('no Rainbow Badge')

@stage
def hideout(b):
    if b.where()[0] not in [(26, i) for i in range(21, 26)]:        # (a resumed run already inside: the elevator)
        train(b, 2); H.honest_hms(b, cut=True); H.heal_pc(b)
        tour(b, (21, 19)); talk_map(b); read_signs(b); ev(b, 20)   # the poster's switch opens the stairs
        if not tour(b, (26, 21)): issue('hideout stairs not reached (poster switch?)', b.where()); return
        tour(b, (26, 24))                                          # B2F, B3F (spin floors), B4F west: the Lift Key
        print('b4f', b.where(), b.objpos(), flush=True)
    # the elevator: from B2F (B1F's elevator room is closed by a door until its Rocket is beaten from inside, as in Red)
    tour(b, (26, 22), visit=False)
    for wx in (24, 25):
        if b.where()[0] == (26, 22): b.go_warp_xy(wx, 19); b.wait(30)
    print('lift', b.where(), flush=True)
    if b.where()[0] != (26, 25): issue('elevator not reached from B2F', b.where()); return
    lift(b, 'ちか4かい', 6)                                       # menu rows: B1F 2, B2F 4, B4F 6, やめる 8
    b.go_warp_xy(3, 1); b.wait(40); ev(b, 10); print('out', b.where(), b.objpos(), flush=True)
    if b.where()[0] != (26, 24): issue('elevator did not reach B4F', b.where()); return
    for p in [(24, 11), (25, 4)]:
        b.goto(*p); ev(b, 40)
    if (25, 3) in b.objpos(): b.talk_to(25, 3, n=0); ev(b, 40)
    for i in range(4): ev(b, 20)
    print('after giovanni', b.where(), b.objpos(), flush=True)
    if (25, 3) in b.objpos(): issue('Giovanni still in the hideout')
@stage
def hideout_out(b):
    if b.where()[0] != (26, 24): return
    if (25, 2) in b.objpos(): b.talk_to(25, 2, n=0); ev(b, 20)       # the Silph Scope he left
    print('scope?', b.objpos(), flush=True)
    # out: the elevator to B1F (its room's Rocket is fought there, then the door opens)
    for p in [(24, 15), (25, 15)]:
        b.go_warp_xy(*p); b.wait(30)
        if b.where()[0] == (26, 25): break
    lift(b, 'ちか1かい', 2)
    b.go_warp_xy(3, 1); b.wait(40); ev(b, 20); print('B1F', b.where(), b.objpos(), flush=True)
    talk_map(b); ev(b, 20)
    tour(b, (21, 4), visit=False); print('out of the hideout', b.where(), flush=True)

def lift(b, floor, row):
    for p in [(1, 2), (2, 2)]:
        if b.goto(*p): break
    b.face('U'); b.press('A', 60)
    for i in range(6):
        t = b.tilemap()
        if t[row * 20 + 1] == 0xED: break
        b.g.press('D', 6, 30)
    b.press('A', 60)
    for i in range(6):
        if b.textbox(): b.press('A', 40)
@stage
def tower(b):
    train(b, 2); H.heal_pc(b)
    tour(b, (26, 20)); print('7F', b.where(), b.objpos(), flush=True)
    for i in range(6): ev(b, 30)
    print('after fuji', b.where(), b.objpos(), flush=True)
    talk_map(b); ev(b, 30)

@stage
def fuchsia(b):
    train(b)
    old = P.AVOID; P.AVOID = tuple(a for a in P.AVOID if a not in ((18, 2), (26, 104), (26, 106))) + ((25, 2),)
    if b.where()[0] == b.mapk('FuchsiaCity'):                  # resumed in the town
        visit_town(b, 'FuchsiaCity'); P.AVOID = old; return
    r = tour(b, (18, 2), skipmaps=[(18, 4)]); print('route12', r, b.where(), b.objpos(), flush=True)
    # Route 13 -> 14: rows 4 and 6 end at bird keepers standing in one-tile passages (as in Red); row 12 is the way
    if b.where()[0] != (17, 1): b.travel((17, 1)); b.wait(20)
    if b.where()[0] == (17, 1) and b.goto(0, 12):
        b.step('L'); b.wait(20); print('route14 via row 12', b.where(), flush=True)
    r = tour(b, 'FuchsiaCity'); print('->', r, b.where(), flush=True)
    if not r: issue('Fuchsia not reached (Snorlax / Poke Flute?)', b.where())
    else: visit_town(b, 'FuchsiaCity')
    P.AVOID = old
@stage
def koga(b):
    if badges(b) >= 5: return
    train(b, 2); H.heal_pc(b)
    gym_try(b, 'FuchsiaGym')
    if badges(b) < 5: issue('no Soul Badge')

@stage
def safari(b):
    train(b); H.heal_pc(b)
    tour(b, (26, 87)); ev(b, 30); print('gate', b.where(), flush=True)
    b.seen |= {(26, 88), (26, 89), (26, 90), (26, 91), (26, 92), (26, 93), (26, 95), (26, 97), (26, 98)}
    r = tour(b, (26, 94)); print('west', r, b.where(), flush=True)
    r = tour(b, (26, 96)); print('house', r, b.where(), flush=True)
    for i in range(4): ev(b, 20)
    if not H.has_hm(b, 3): issue('no HM03 (Surf) from the Safari Zone house', b.where())
    for i in range(3):
        if b.where()[0] == (26, 96) or b.where()[0][0] == 26 and 87 <= b.where()[0][1] <= 98:
            tour(b, 'FuchsiaCity', visit=False)
    b.travel((17, 12)); b.wait(20); b.talk_to(2, 4, n=0); ev(b, 30)
    if not H.has_hm(b, 4): issue('no HM04 (Strength) from the warden (Gold Teeth?)', b.where())

@stage
def cinnabar(b):
    train(b); H.heal_pc(b)
    # by sea from Pallet Town (Route 21); Route 20 is cut in two by the Seafoam Islands (their boulders: later)
    old = P.AVOID; P.AVOID = P.AVOID + ((25, 2), (6, 5), (6, 6))
    r = b.where()[0] == b.mapk('CinnabarIsland') or tour(b, 'CinnabarIsland'); print('cinnabar', r, b.where(), P.mus(b), flush=True)
    P.AVOID = old
    if not r: issue('Cinnabar Island not reached', b.where()); return
    visit_town(b, 'CinnabarIsland', skip=[(26, 61)])            # the gym (locked: the Secret Key)
@stage
def mansion(b):
    train(b); H.heal_pc(b)
    P.LIVE[0] = True
    r = P.mansion_solve(b, (26, 60)); print('mansion b1f', r, b.where(), flush=True)
    kx, ky = 5, 13                                   # Red: the Secret Key's ball on B1F
    r = P.mansion_solve(b, (26, 60), cells=[(kx + 1, ky), (kx - 1, ky), (kx, ky + 1), (kx, ky - 1)])
    print('mansion key reachable', r, b.where(), flush=True)
    b.talk_to(kx, ky); ev(b, 20)
    print('took the key ball', b.where(), flush=True)
    P.LIVE[0] = False
@stage
def blaine(b):
    if badges(b) >= 6: return
    train(b, 2); H.heal_pc(b); P.LIVE[0] = True
    for t in range(4):
        tour(b, (26, 61)); talk_map(b); read_signs(b); ev(b, 30)
        for p, d in [((3, 4), 'U'), ((4, 3), 'L'), ((2, 3), 'R')]:
            if P.safe_goto(b, *p): b.face(d); b.press('A', 40); ev(b, 40); break
        if badges(b) >= 6: break
        print('blaine retry', t, b.where(), flush=True); H.heal_pc(b); b.seen.discard((26, 61))
    P.LIVE[0] = False
    if badges(b) < 6: issue('no Volcano Badge')

ROOF = (26, 131)                                                   # Celadon Dept. Store roof (Red's map, phase 41)
def buy_drink(b):
    """the roof's vending machine: おいしいみず (the first row)"""
    if not tour(b, ROOF): issue('Dept. Store roof not reached', b.where()); return False
    for t in range(3):
        if P.safe_goto(b, 10, 2): break
    b.face('U'); b.press('A', 60)
    for i in range(8):
        if b.has('やめる'): break
        b.press('A', 50)
    if not b.has('やめる'): issue('vending machine menu not shown', b.where()); return False
    b.press('A', 60)
    for i in range(12):
        if b.has('やめる'): break
        b.press('A', 50)
    ok = b.has('やめる'); b.press('B', 40); ev(b, 10)
    print('bought a drink', ok, flush=True); return ok
@stage
def saffron(b):
    train(b); H.heal_pc(b)
    gates = [k for k in b.db.maps if k[0] == 26 and any((w[3], w[4]) == b.mapk('SaffronCity') for w in b.db.warps(k))]
    old = P.AVOID; P.AVOID = P.AVOID + tuple(gates) + (b.mapk('SaffronCity'), (6, 5), (6, 6))   # Routes 19/20: Seafoam's boulders (later)
    buy_drink(b); P.AVOID = old
    r = tour(b, 'SaffronCity'); print('-> saffron', r, b.where(), flush=True)
    if not r: issue('Saffron not reached (the guards?)', b.where()); return
    P.SKIPGYM[0] = True; visit_town(b, 'SaffronCity', skip=[(25, 10)])
SILPH = {f: (26, 24 + f) for f in range(2, 12)}; SILPH[1] = (25, 10)
@stage
def silph(b):
    if 0x39 not in H.party(b)[0]['moves']: H.teach(b, 3, 0)     # the lead gets Surf (its weakest move goes)
    train(b, 2); H.heal_pc(b)
    P.LIVE[0] = True; P.DOORS[0] = True
    tour(b, SILPH[5])                                  # 5F: the Card Key (its talks may step on a pad: go back for it)
    for t in range(4):
        if has_card_key(b): break
        P.region_go(b, SILPH[5], [(20, 16), (22, 16)], set(SILPH.values()) | {(26, 36)})
        if b.where()[0] == SILPH[5]: pick_ball(b, 21, 16)
        print('card key', has_card_key(b), b.where(), flush=True)
    if not has_card_key(b): issue('Silph Co. card key not got')
    for p in range(1):
        for f in range(1, 12):
            r = tour(b, SILPH[f]); print('### silph floor', f, r, b.where(), flush=True)
            if r: talk_map(b); ev(b, 10)
        b.seen -= set(SILPH.values())
    silph_gio(b)
    P.LIVE[0] = False; P.DOORS[0] = False
def has_card_key(b):
    b.bank1(); return 0x89 in b.peek(0xD8B0, 0x1B)       # the key items pocket
def pick_ball(b, x, y):
    """walk next to an item ball without touching warp tiles (pads) and pick it up"""
    k = b.where()[0]
    still = {(o[2] - 4, o[1] - 4) for o in b.db.objs(k)} - {(x, y)}     # people standing still (off screen too)
    for (dx, dy, d) in ((0, 1, 'U'), (0, -1, 'D'), (1, 0, 'L'), (-1, 0, 'R')):
        if P.safe_goto(b, x + dx, y + dy, block=still, tries=15):
            b.face(d); b.press('A', 40); ev(b, 20); return (x, y) not in b.objpos()
    return False
def silph_gio(b):
    """11F's boardroom (Giovanni) is reached only by 7F's warp pad (as in Red): the stairs / elevator end in a corridor"""
    # Red's way: 3F's pad (11,11) -> 7F (5,3), the pad (5,7) -> 11F (3,2): the room of 11F with Giovanni's door
    for t in range(4):
        P.region_go(b, SILPH[11], [(3, 3), (2, 2), (4, 2), (3, 1)], set(SILPH.values()) | {(26, 36)})
        print('-> 11F', b.where(), flush=True)
        p0 = H.party(b)[0]
        if p0['hp'] >= p0['maxhp'] * 0.8 or t == 3: break
        H.heal_pc(b)                                   # the rival on 7F wore the lead down: heal before Giovanni
    if b.where()[0] != SILPH[11]: issue('Silph 7F pad to 11F not reached', b.where()); return
    P.live_grid(b); P.open_doors(b); P.live_grid(b)
    talk_map(b); ev(b, 30)
    print('after 11F', b.where(), b.objpos(), flush=True)
    if not b.flag(0x606): issue('Giovanni not beaten in Silph Co. 11F (flag 0x606)')
@stage
def sabrina(b):
    if badges(b) >= 7: return
    train(b, 2); H.heal_pc(b); P.SKIPGYM[0] = False
    for t in range(3):
        if badges(b) >= 7: break
        tour(b, 'SaffronGym', visit=False)
        pad_talks(b, [(17, 13), (17, 7), (17, 1), (10, 1), (3, 1), (3, 7), (3, 13), (9, 8)])   # Red's trainers, then Sabrina
        ev(b, 30)
        if badges(b) < 7: print('gym retry SaffronGym', t, b.where(), flush=True); H.heal_pc(b)
    if badges(b) < 7: issue('no Marsh Badge')

@stage
def viridian(b):
    if badges(b) >= 8: return
    train(b, 2); H.heal_pc(b); P.SKIPGYM[0] = False
    old = P.AVOID; P.AVOID = P.AVOID + ((7, 12),)       # Route 4 from Cerulean: Red's ledges make it one way
    tour(b, 'ViridianCity'); P.AVOID = old
    P.LIVE[0] = True
    gym_try(b, 'ViridianGym')
    P.LIVE[0] = False
    if badges(b) < 8: issue('no Earth Badge')

VR1, VR2, VR3 = (26, 68), (26, 69), (26, 70)
def boulders_here(b):
    k = b.where()[0]
    return ([(o[2] - 4, o[1] - 4) for o in b.db.objs(k) if o[0] == P.SPR_BOULDER],
            [(o[2] - 4, o[1] - 4) for o in b.db.objs(k) if o[0] != P.SPR_BOULDER])
def live_boulders(b, guess):
    """boulders now: the ones on screen, the rest where we last saw them"""
    op = set(b.objpos()); return [p for p in guess if p in op] + [p for p in op if p not in guess and p in guess]
@stage
def victory(b):
    """Victory Road as in Red: 1F's switch, 2F's first switch, 3F's switch and its hole (a boulder falls to 2F),
    2F's second switch; then Route 23's top and the Indigo Plateau.  (A floor's boulders go back to their places
    when the player leaves it, as in Red: after healing that floor starts again; the switches stay pressed.)"""
    at_sw2 = b.where()[0] in (VR2, VR3) and b.flag(2241)                  # resumed after the hole: stay in the cave
    if not at_sw2:
        if b.where()[0] in (VR1, VR2, VR3): H.escape_rope(b)          # (walking out past the boulders: no)
        train(b, 2); H.heal_pc(b)
    P.LIVE[0] = True
    H.FLEE[0] = True
    # the user (2026-11-17): use Repel -- Max Repels put in the bag (save-data edit), used from the bag
    if H.MAX_REPEL not in [i for i, _ in H.items(b)]: H.add_item(b, H.MAX_REPEL, 30)
    P.REPEL[0] = True
    _tr0 = _bot.Bot.travel
    def trr(s, *a, **k):
        if s.where()[0] in (VR1, VR2, VR3, (16, 1), (23, 2)): H.use_repel(s)
        return _tr0(s, *a, **k)
    _bot.Bot.travel = trr                                      # run from the wild Pokémon in the cave (trainers: fight)
    def floor(k, goal, enter):
        for t in range(4):
            enter()
            if b.where()[0] != k: continue
            bs, ob = boulders_here(b)
            r = P.push_boulders(b, bs, goal, ob, minhp=0.15 if goal == (23, 15) else 0.55)   # (the hole: one push)
            print('VR', k, goal, r, b.where(), flush=True)
            if r is True or (goal == (23, 15) and (b.flag(2241) or b.where()[0] == VR2)): return True   # (fell down with it)
            if r is None: return None
            if b.where()[0] in (VR1, VR2, VR3): H.escape_rope(b)     # out of the cave first (walking back is long)
            H.heal_pc(b)
        return False
    def to3f():
        for t in range(3):
            if b.where()[0] == VR3: return
            if b.where()[0] not in (VR2, VR3):
                # Red: entering 2F resets 1F's switch -- coming back from a Pokémon Center, push 1F's boulder again
                tour(b, VR1, visit=False)
                if b.where()[0] == VR1:
                    bs, ob = boulders_here(b); P.push_boulders(b, bs, (17, 13), ob)
            tour(b, VR2, visit=False)
            if b.where()[0] == VR2: b.go_warp_xy(23, 7); b.wait(30); ev(b, 10)
    SW2A, SW2B, SW3, HOLE = 2212, 2213, 2214, 2241      # phase 23's flags (p23_flags.json): what is done already
    def save(): b.g.save_state(HST % 'victory_tr')
    if not b.flag(SW2A):
        floor(VR1, (17, 13), lambda: tour(b, VR1, visit=False))
        floor(VR2, (1, 16), lambda: tour(b, VR2, visit=False)); save()
    if not b.flag(SW3):
        floor(VR3, (3, 5), to3f); save()
    if not b.flag(SW2B):
        if not b.flag(HOLE): floor(VR3, (23, 15), to3f)
        if b.where()[0] == VR3 and P.safe_goto(b, 23, 14, tries=12): b.step('D'); b.wait(60); ev(b, 10)   # follow it down
        print('VR after the hole', b.where(), flush=True); save()
        for t in range(3):
            if b.flag(SW2B): break
            if b.where()[0] != VR2: tour(b, VR2, visit=False)
            bs = [(23, 16)] + [p for p in boulders_here(b)[0] if p != (23, 16)]
            r = P.push_boulders(b, bs, (9, 16), boulders_here(b)[1], minhp=0.25); print('VR 2F switch 2', r, b.where(), flush=True)
            if r == 'heal':
                if b.where()[0] in (VR1, VR2, VR3): H.escape_rope(b)
                H.heal_pc(b)
            elif r is None: break
        save()
    _busy[0] = True                                   # (no walking back to heal: the Indigo Plateau has its own center)
    try: r = tour(b, (16, 2), visit=False)
    finally: _busy[0] = False
    print('-> Indigo Plateau', r, b.where(), flush=True)
    if b.where()[0] != (16, 2): issue('Indigo Plateau not reached', b.where())
    H.FLEE[0] = False; P.REPEL[0] = False; _bot.Bot.travel = _tr0
    P.LIVE[0] = False

E4_ROOMS = [(16, 3), (16, 4), (16, 5), (16, 6)]
@stage
def league(b):
    """the user's wish (2026-11-17): at the Indigo Plateau the party becomes six Pokémon at Lv 100 (team.py, written
    into the save data), then the Elite Four and the champion, walking and talking only"""
    import team as T
    if b.where()[0] != (16, 2): tour(b, (16, 2))
    T.install(b); b.wait(30); H.heal_pc(b, (16, 2))
    print('team', [(q['species'], q['level']) for q in H.party(b)], flush=True)
    P.LIVE[0] = True
    for room in E4_ROOMS + [(16, 7)]:
        r = tour(b, room, visit=False); ev(b, 20); print('room', room, r, b.where(), flush=True)
        if b.where()[0] != room: issue('league room not reached', room, b.where()); return
        top = 3 if room == (16, 7) else 7
        for t in range(3):
            P.live_grid(b)
            if P.safe_goto(b, 5, top + 1, tries=12) or b.where()[1:] == (5, top + 1): break
            ev(b, 20)
        b.face('U'); b.wait(10); b.press('A', 40); ev(b, 80)
        for k in range(6):
            b.wait(60)
            if b.in_battle() or b.textbox(): ev(b, 80)
        print('  beat', room, b.where(), 'lead hp', H.party(b)[0]['hp'], flush=True)
        if b.where()[0] != room: break
    for t in range(10):
        if b.where()[0] == (16, 8): break
        ev(b, 40); b.wait(60)
    print('hall of fame?', b.where(), flush=True)
    for k in range(30): ev(b, 40); b.wait(60)
    P.LIVE[0] = False

def pad_talks(b, people):
    """Saffron Gym: walk by the pads (wgoto) next to each person and talk"""
    for (x, y) in people:
        if (x, y) not in [(o[2] - 4, o[1] - 4) for o in b.db.objs(b.where()[0])]: continue
        for dx, dy, d in ((0, 1, 'U'), (1, 0, 'L'), (-1, 0, 'R'), (0, -1, 'D')):
            if P.wgoto(b, x + dx, y + dy):
                b.wait(30)
                for k_ in range(3):
                    b.face(d); b.wait(10); b.press('A', 40)
                    if b.textbox() or b.in_battle(): break
                ev(b, 60)
                for k_ in range(6):                    # (Sabrina's battle transition is long: wait for the battle)
                    b.wait(60)
                    if b.in_battle() or b.textbox(): ev(b, 60)
                break
        print('  pad talk', (x, y), b.where(), 'badges', badges(b), flush=True)
        if b.where()[0] != b.mapk('SaffronGym'): return
def gym_try(b, gym, tries=3):
    """the gym's trainers and leader; after a loss (or a worn-out lead) heal and go again"""
    n0 = badges(b)
    for t in range(tries):
        tour(b, gym); talk_map(b); ev(b, 40)
        if badges(b) > n0: return True
        print('gym retry', gym, t, b.where(), flush=True); H.heal_pc(b)
        b.seen.discard(b.mapk(gym))
    return False

def solve_cans(b):
    from jpchar import decode
    def scr():
        t = b.tilemap(); return ' '.join(decode(t[r * 20 + 1:r * 20 + 19], stop_at_end=False).strip() for r in (14, 16))
    def check1(i):
        x, y = 1 + 2 * (i // 3), 7 + 2 * (i % 3)
        for dx, dy, d in ((0, 1, 'U'), (0, -1, 'D'), (1, 0, 'L'), (-1, 0, 'R')):
            if b.goto(x + dx, y + dy): break
        else: return 'unreach'
        b.face(d); b.press('A', 40); txt = []
        for k in range(15):
            if b.in_battle(): b.battle(); continue
            if b.textbox(): txt.append(scr()); b.press('A', 40)
            else: break
        return ' | '.join(txt)
    def check(i):
        for k_ in range(3):
            ev(b, 10); t = check1(i)
            if t and t != 'unreach': return t
        return t
    NB = {0: (1, 3), 1: (0, 2, 4), 2: (1, 5), 3: (0, 4, 6), 4: (1, 3, 5, 7), 5: (2, 4, 8), 6: (3, 7, 9), 7: (4, 6, 8, 10), 8: (5, 7, 11),
          9: (6, 10, 12), 10: (7, 9, 11, 13), 11: (8, 10, 14), 12: (9, 13), 13: (10, 12, 14), 14: (11, 13)}
    done_ = False; tries = 0
    while not done_ and tries < 80:
        first = None
        for i in range(15):
            t = check(i); tries += 1
            if 'たい1' in t: first = i; break
        if first is None: issue('trash cans: no first switch'); return False
        for j in NB[first]:
            t = check(j); tries += 1; print('  can', j, t[-40:], flush=True)
            if 'たい2' in t: done_ = True; break
            if 'もとって' in t: break
    print('cans solved', done_, tries, flush=True)
    if not done_: issue('trash cans not solved')
    return done_

def main():
    names = [f.__name__ for f in STAGES]
    a = sys.argv[1]; z = sys.argv[2] if len(sys.argv) > 2 else names[-1]
    i = names.index(a)
    for j in range(i, names.index(z) + 1):
        prev = names[j - 1] if j else 's14v'
        run(names[j], prev)
if __name__ == '__main__': main()
