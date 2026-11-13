"""kit check helpers (クリスタル バグ修正の確認キット)"""
import sys; sys.path.insert(0,'.')
from t64a import *
from bot import _ok_cell, grid_of
import os
O = SC + '/run/kt'
os.makedirs(O, exist_ok=True)

def start(rom='p66', state='blogbase2.st', out='x', sav=None):
    make_test_rom(SC + '/build/%s.gbc' % rom)
    return Bot(state=None if sav else state, sav=sav, out=O + '/' + out)

def edge_cell(b, d):
    k, x, y = b.where()
    G = grid_of(b.db.r, b.db.maps[k]['hdr']); H, W = len(G), len(G[0])
    if d == 'U': cand = [(i, 0) for i in range(W)]
    elif d == 'D': cand = [(i, H - 1) for i in range(W)]
    elif d == 'L': cand = [(0, i) for i in range(H)]
    else: cand = [(W - 1, i) for i in range(H)]
    ref = x if d in 'UD' else y
    cand = [c for c in cand if b.path(*c, allow_target=False) is not None]
    cand.sort(key=lambda c: abs((c[0] if d in 'UD' else c[1]) - ref))
    return cand

def hold(b, keys, frames, shots=None):
    """hold keys; per frame (scx, scy, map, x, y)"""
    rec = []
    b.g.down(keys)
    for f in range(frames):
        b.g.wait(1)
        sx, sy = b.peek(0xFF43)[0], b.peek(0xFF42)[0]
        b.bank1(); m = tuple(b.peek(W_MAP, 2)); y, x = b.peek(W_Y, 2)
        rec.append((sx, sy, m, x, y))
        if shots is not None and f in shots: b.g.shot('%s/f%03d.png' % (b.out, f))
    b.g.up(keys)
    return rec

def stall(rec):
    """longest run of frames with no scroll change"""
    best = cur = 0; at = 0
    for i in range(1, len(rec)):
        if rec[i][:2] == rec[i - 1][:2]:
            cur += 1
            if cur > best: best = cur; at = i
        else: cur = 0
    return best, at

def near_edge(b, m, d, dist=3):
    """a walkable cell `dist` from edge d with a straight walkable line to the edge"""
    k = b.mapk(m)
    G = grid_of(b.db.r, b.db.maps[k]['hdr']); H, W = len(G), len(G[0])
    dx, dy = {'L': (-1, 0), 'R': (1, 0), 'U': (0, -1), 'D': (0, 1)}[d]
    out = []
    if d in 'LR':
        ex = 0 if d == 'L' else W - 1
        for y in range(H):
            line = [(ex - dx * i, y) for i in range(dist + 1)]
            if all(_ok_cell(G, *p) for p in line): out.append((abs(y - H // 2), line[-1]))
    else:
        ey = 0 if d == 'U' else H - 1
        for x in range(W):
            line = [(x, ey - dy * i) for i in range(dist + 1)]
            if all(_ok_cell(G, *p) for p in line): out.append((abs(x - W // 2), line[-1]))
    out.sort()
    return [p for _, p in out]

def go_edge(b, m, d, dist=3):
    c = near_edge(b, m, d, dist)[0]
    b.warp(m, c[0], c[1]); b.wait(60); b.clear_text(); b.wait(30)
    return c

def sheet(files, out, W=8, scale=1):
    from PIL import Image
    im = Image.new('RGB', (162 * W, 146 * ((len(files) + W - 1) // W)), 'white')
    for i, f in enumerate(files): im.paste(Image.open(f), (162 * (i % W), 146 * (i // W)))
    if scale != 1: im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(out); return out

def seq(b, keys, frames, tag, every=1):
    """hold keys for frames, shot every `every` frames; returns file list"""
    fs = []
    b.g.down(keys)
    for f in range(frames):
        b.g.wait(1)
        if f % every == 0:
            p = '%s/%s_%03d.png' % (b.out, tag, f); b.g.shot(p); fs.append(p)
    b.g.up(keys)
    return fs

def crops(files, out, box=(40, 40, 120, 104), W=10, scale=3):
    from PIL import Image
    w, h = box[2] - box[0], box[3] - box[1]
    im = Image.new('RGB', ((w + 2) * W, (h + 2) * ((len(files) + W - 1) // W)), 'white')
    for i, f in enumerate(files): im.paste(Image.open(f).crop(box), ((w + 2) * (i % W), (h + 2) * (i // W)))
    im.resize((im.width * scale, im.height * scale), Image.NEAREST).save(out); return out

def straight(b, m, d, n):
    """start cell with n+1 walkable cells in direction d (and one cell behind)"""
    k = b.mapk(m); G = grid_of(b.db.r, b.db.maps[k]['hdr']); H, W = len(G), len(G[0])
    dx, dy = {'L': (-1, 0), 'R': (1, 0), 'U': (0, -1), 'D': (0, 1)}[d]
    objs = {(o[1], o[2]) for o in b.objs_of(k)}
    for y in range(2, H - 2):
        for x in range(2, W - 2):
            line = [(x + dx * i, y + dy * i) for i in range(-1, n + 2)]
            if all(_ok_cell(G, *p) and p not in objs for p in line): return x, y

def tap(b, k, frames, tag, every=1, hold=4):
    """press k for `hold` frames, then shoot every frame for `frames` frames"""
    fs = []
    b.g.down(k)
    for f in range(frames):
        if f == hold: b.g.up(k)
        b.g.wait(1)
        if f % every == 0:
            p = '%s/%s_%03d.png' % (b.out, tag, f); b.g.shot(p); fs.append(p)
    return fs

def uniq(fs):
    """drop consecutive identical frames"""
    from PIL import Image
    out = []; last = None
    for f in fs:
        d = Image.open(f).tobytes()
        if d != last: out.append(f); last = d
    return out

def start_menu(b, idx):
    """open the START menu and put the cursor on item idx (0 = ずかん)"""
    from PIL import Image
    b.press('S', 40)
    for t in range(12):
        p = b.out + '/_sm.png'; b.g.shot(p)
        im = Image.open(p).convert('RGB')
        cur = [i for i in range(8) if any(sum(im.getpixel((x, 14 + 16 * i + dy))) < 200 for x in range(102, 108) for dy in range(6))]
        if cur and cur[0] == idx: return True
        b.press('D', 12)
    return False
