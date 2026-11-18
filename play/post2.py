"""post-game battles, the player put next to each place (save-data edit): Sabrina (Saffron Gym's pads), the rival in
Mt. Moon, at the Indigo Plateau (Monday / Wednesday; Tuesday: none), the Elite Four again, the Dragon's Den
(Thursday), Hibiki on Mt. Silver"""
import sys, os
sys.argv = [sys.argv[0]]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bot, pt as P, honest as H, hon as Hn, rematch_data as RD
SC = Hn.SC
b = bot.Bot(state=Hn.HST % 'jrematch', out=SC + '/run/h_post2'); b.fs = []; b.seen = set(); b.tag = 'h_post2'
P.LIVE[0] = True; P.REPEL[0] = True
H.honest_hms(b, cut=True, surf=True, strength=True, whirl=True, waterfall=True)
OT = Hn.OT_LOG; ev = Hn.ev
def settle(n=10):
    for k in range(n):
        b.wait(60)
        if b.in_battle() or b.textbox(): ev(b, 80)
def heal():
    p = H.party(b)
    if p[0]['hp'] < p[0]['maxhp'] or any(q['hp'] == 0 for q in p): H.heal_pc(b)
# Sabrina, twice
for k in range(2):
    OT.clear(); Hn.warp_to(b, (25, 4), 9, 9); print('at', b.where(), flush=True)
    Hn.talk_at(b, 9, 8); ev(b, 60); settle()
    Hn.check_party('SaffronGym', RD.group('SabrinaGroup'), 'SaffronGym %d' % (k + 1)); heal()
# Mt. Moon: the rival's scene on entering
OT.clear(); Hn.warp_to(b, (3, 85), 3, 4); ev(b, 80); settle()
for t in range(10):
    if OT: break
    b.step('D'); b.wait(30); ev(b, 40); settle(3)
print('mt moon', b.where(), flush=True)
Hn.check_party('MountMoon', RD.group('Rival2Group')[:3], 'rival Mt. Moon'); heal()
# Indigo Plateau lobby: the rival steps in at (16,4)/(17,4) on Monday / Wednesday
def lobby(wd, name, want):
    Hn.set_weekday(b, wd); OT.clear()
    Hn.warp_to(b, (16, 2), 5, 12); b.wait(30)
    P.live_grid(b); r = P.safe_goto(b, 16, 5, tries=12); b.step('U'); b.wait(60); ev(b, 80); settle()
    print('lobby', name, r, b.where(), flush=True)
    if want: Hn.check_party('Indigo', RD.group('Rival2Group')[3:], 'rival Indigo Plateau %s' % name)
    else: print('POST rival Indigo %s %s' % (name, 'OK (none)' if not OT else 'NG battle %s' % OT), flush=True)
    heal()
lobby(1, 'Monday', True); lobby(3, 'Wednesday', True); lobby(2, 'Tuesday', False)
# the Elite Four and Lance again (league walks from the lobby)
OT.clear(); Hn.warp_to(b, (16, 2), 5, 12)
try: Hn.league(b)
except Exception as e: print('league error', e, flush=True)
print('POST E4 again', len(OT), 'parties', OT, b.where(), flush=True)
for i in range(14): b.press('A', 10); b.wait(120)
print('after credits', b.where(), flush=True)
# the Dragon's Den on Thursday: the rival is there (talk only)
Hn.set_weekday(b, 4); OT.clear()
Hn.warp_to(b, (3, 81), 20, 25); b.wait(30)
op = b.objpos(); print('den objs', op, flush=True)
near = min(op, key=lambda p: abs(p[0] - 20) + abs(p[1] - 23)) if op else (20, 23)
Hn.talk_at(b, *near); ev(b, 40); settle(4)
print('POST Dragon\'s Den Thursday rival-near', near, 'battles', OT, flush=True)
# Mt. Silver: Hibiki
OT.clear(); Hn.warp_to(b, (3, 76), 9, 12); Hn.talk_at(b, 9, 10); ev(b, 80); settle()
for k in range(10): ev(b, 40); b.wait(60)
print('POST Hibiki', OT, b.where(), flush=True)
b.g.save_state(Hn.HST % 'post2')
print('post2 done', flush=True)
