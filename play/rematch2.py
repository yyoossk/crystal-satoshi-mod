"""the phone rematch trainers the walk could not reach: the player is put next to each (save-data edit), then the
same checks as hon.jrematch"""
import sys, os, json
sys.argv = [sys.argv[0]]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bot, pt as P, honest as H, hon as Hn, rematch_data as RD
SC = Hn.SC
b = bot.Bot(state=Hn.HST % 'jrematch', out=SC + '/run/h_rematch2'); b.fs = []; b.seen = set(); b.tag = 'h_rematch2'
P.LIVE[0] = True
H.honest_hms(b, cut=True, surf=True, strength=True, whirl=True, waterfall=True)
DONE = SC + '/run/rematch_done.json'; did = json.load(open(DONE))
WALK = bot.WALK
for e in RD.full():
    if e['who'] in did: continue
    k = b.mapk(e['map']); x, y = e['pos']
    G = bot.grid_of(b.db.r, b.db.maps[k]['hdr'])
    spot = None
    for dx, dy in ((0, 1), (-1, 0), (1, 0), (0, -1), (0, 2), (-2, 0), (2, 0)):
        nx, ny = x + dx, y + dy
        if 0 <= ny < len(G) and 0 <= nx < len(G[0]) and G[ny][nx] in WALK: spot = (nx, ny); break
    b.warp(k, *spot); b.wait(90); Hn.ev(b, 20)
    print('->', e['map'], e['who'], b.where(), flush=True)
    ra, rm = e['ready']
    for c in sorted(e['fights']):
        cl, tid, want = e['fights'][c]; got = None
        for t in range(3):
            b.bank1(); b.g.poke(e['count'], c); b.g.poke(ra, b.peek(ra)[0] | rm)
            Hn.OT_LOG.clear()
            if H.party(b)[0]['hp'] < H.party(b)[0]['maxhp'] // 2: H.heal_pc(b); b.warp(k, *spot); b.wait(90)
            Hn.talk_at(b, x, y); Hn.ev(b, 40)
            if Hn.OT_LOG:
                got = Hn.OT_LOG[-1]
                if [tuple(q) for q in got] == [tuple(q) for q in want] and not (b.peek(ra)[0] & rm): break
        after = b.peek(e['count'])[0]; still = bool(b.peek(ra)[0] & rm)
        ok = got is not None and [tuple(q) for q in got] == [tuple(q) for q in want] and not still
        print('REMATCH %s %s count %d -> %s %s %s after %d ready %s %s' % (e['map'], e['who'], c, tid, got, want, after, still, 'OK' if ok else 'NG'), flush=True)
        open(SC + '/run/rematch_results.txt', 'a').write('%s %s %d %s %s\n' % (e['map'], e['who'], c, tid, 'OK' if ok else 'NG %s %s' % (got, want)))
    did.append(e['who']); json.dump(did, open(DONE, 'w'))
print('rematch2 done', flush=True)
