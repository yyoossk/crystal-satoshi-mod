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
    t = time.time(); r = _ob(s, *a, **k); p = H.party(s)
    print('  battle %.0fs lv%d hp%d/%d %s' % (time.time() - t, p[0]['level'], p[0]['hp'], p[0]['maxhp'], s.where()), flush=True); return r
_bot.Bot.battle = _bt
_oh = H.heal_pc
def _hp(b, *a):
    t = time.time(); _busy[0] = True
    try: r = _oh(b, *a)
    finally: _busy[0] = False
    print('  heal %.0fs' % (time.time() - t), b.where(), flush=True); return r
H.heal_pc = _hp

# --- a picture (the museum's fossils) closes with B, not A: close anything left open after the talk
def ev2(b, n=80, yes=True):
    """pt.ev, plus: a talk that keeps coming back to the same text/menu (an info menu) is left with B"""
    q = 0; seen = {}
    for i in range(n):
        if b.in_battle(): b.battle(); snap(b); q = 0; continue
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
    tour(b, 'PewterGym'); talk_map(b); ev(b, 40)
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
    tour(b, 'CeruleanGym'); talk_map(b); ev(b, 40)
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
