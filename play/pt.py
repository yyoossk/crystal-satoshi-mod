"""playthrough check: new game -> Pewter Gym, walking only (no warps / pokes)"""
import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
import bot as _bot
_bot.NOHEAL[0] = True
ROM = 'p72'
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
