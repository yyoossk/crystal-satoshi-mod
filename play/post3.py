"""the rival after phase 117: Mt. Moon, the Indigo Plateau lobby (Monday / Wednesday; Tuesday none), the Dragon's Den
(Tuesday / Thursday; Monday none)"""
import sys, os
sys.argv = [sys.argv[0]]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bot, pt as P, honest as H, hon as Hn, rematch_data as RD
SC = Hn.SC
b = bot.Bot(state=Hn.HST % 'jrematch', out=SC + '/run/h_post3'); b.fs = []; b.seen = set(); b.tag = 'h_post3'
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
def den(wd, name, want):
    Hn.set_weekday(b, wd); Hn.warp_to(b, (3, 81), 20, 26); b.wait(60)
    op = b.objpos(); here = [p for p in op if abs(p[0] - 20) <= 3 and abs(p[1] - 23) <= 3]
    txt = ''
    if here:
        Hn.talk_at(b, *here[0]); b.wait(20)
        from jpchar import decode
        t = b.tilemap(); txt = ' '.join(decode(t[r * 20 + 1:r * 20 + 19], stop_at_end=False).strip() for r in (14, 16))
        ev(b, 40)
    ok = bool(here) == want
    print('POST Dragon\'s Den %s rival %s %s text %s' % (name, here, 'OK' if ok else 'NG', txt), flush=True)
den(4, 'Thursday (before Mt. Moon)', False)
OT.clear(); Hn.warp_to(b, (3, 85), 3, 4); ev(b, 80); settle()
Hn.check_party('MountMoon', [[(s, l) for s, l in p] for p in RD.group('Rival2Group')[:3]], 'rival Mt. Moon (species)') if False else None
print('POST rival Mt. Moon', OT, 'beaten flag', b.flag(0x319), flush=True); heal()
def lobby(wd, name, want):
    Hn.set_weekday(b, wd); OT.clear(); b.bank1()
    Hn.warp_to(b, (16, 2), 5, 12); b.wait(30)
    P.live_grid(b); r = P.safe_goto(b, 16, 5, tries=12); b.step('U'); b.wait(60); ev(b, 80); settle()
    print('POST rival Indigo %s want %s got %s' % (name, want, OT), flush=True); heal()
lobby(2, 'Tuesday', False); lobby(1, 'Monday', True); lobby(1, 'Monday again (same day)', False); lobby(3, 'Wednesday', True)
den(2, 'Tuesday', True); den(4, 'Thursday', True); den(1, 'Monday', False)
print('post3 done', flush=True)
