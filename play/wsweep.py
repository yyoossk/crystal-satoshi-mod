"""walk into every warp of the given maps; check arrival and that the player can move afterwards"""
import sys, json; sys.path.insert(0,'play'); from bot import *
part, nparts = int(sys.argv[1]), int(sys.argv[2])
STATE = SC + '/play/k27.st'
b = Bot(state=STATE, out=SC + '/play/run/ws%d' % part)
b.g.poke(0xD83F, b.peek(0xD83F)[0] | 4)          # flash
b.g.save_state(SC + '/play/ws_base%d.st' % part)
keys = sorted(k for k in b.db.maps if b.db.warps(k))
keys = keys[part::nparts]
D = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}
res = []
def moved_ok():
    k0 = b.where()
    for d in 'DULR':
        if b.step(d): return True
        if b.where() != k0: return True
    return False
for k in keys:
    G = grid_of(b.db.r, b.db.maps[k]['hdr']); H, W = len(G), len(G[0])
    for i, (wx, wy, idx, g, m) in enumerate(b.db.warps(k)):
        if (g, m) not in b.db.maps or idx == 255: continue
        dw = b.db.warps((g, m))
        if idx - 1 >= len(dw): res.append((k, i, 'bad idx')); continue
        ax, ay = dw[idx - 1][:2]
        ok = False; how = ''
        cands = [(d, wx - D[d][0], wy - D[d][1]) for d in 'UDLR']
        cands = [c for c in cands if 0 <= c[1] < W and 0 <= c[2] < H and G[c[2]][c[1]] in WALK and G[c[2]][c[1]] >> 4 != 7]
        tries = [('step', c) for c in cands] + [('on', (d, wx, wy)) for d in 'DULR']
        for kind, (d, x, y) in tries[:6]:
            b.g.load_state(SC + '/play/ws_base%d.st' % part); b.wait(5)
            b.warp(k, x, y, wait=120); b.wait(20)
            if b.textbox(): b.clear_text(n=8, shots=False)
            if b.where()[0] != k: continue
            b.g.down(d); b.wait(24); b.g.up(d); b.wait(90)
            if b.textbox(): b.clear_text(n=8, shots=False)
            w = b.where()
            if w[0] == k: continue
            if w[0] != (g, m):
                how = 'arrived %s %s' % (w[0], w[1:]); continue
            ok = True
            if abs(w[1] - ax) + abs(w[2] - ay) > 1: how = 'pos %s want %s' % (w[1:], (ax, ay))
            if not moved_ok(): how += ' STUCK'; b.shot('stuck_%d_%d_%d' % (k[0], k[1], i))
            break
        res.append((k, i, (wx, wy), (g, m), 'ok' if ok and not how else ('FAIL ' + (how or 'no warp'))))
        print(res[-1], flush=True)
json.dump([list(map(str, r)) for r in res], open(SC + '/play/run/ws%d.json' % part, 'w'))
