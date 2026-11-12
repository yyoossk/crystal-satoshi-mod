"""phase 57 checks: wild encounters per map (and time of day), fishing"""
import sys, collections, json, random
sys.path.insert(0, '/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad/play')
from bot import *
import portmaps as PM
INV = {}
for k, v in PM.MON.items():
    if not k.startswith('UNOWN_') and v not in INV: INV[v] = k
W_WILD = 0xD25F            # wTempWildMonSpecies (US D22E + 31)
W_TOD = 0xD29A             # wTimeOfDay
W_STARTHOUR = 0xD4AF       # wStartHour (US D4B7 - 8)
GRASS = {0x18, 0x14}


def set_tod(b, want):
    """0 morn 1 day 2 nite"""
    for h in range(0, 24, 2):
        b.bank1(); b.g.poke(W_STARTHOUR, h); b.wait(10); b.bank1()
        if b.peek(W_TOD)[0] == want: return h
    raise Exception('tod %d' % want)


def cells(b, k, cave):
    G = grid_of(b.db.r, b.db.maps[k]['hdr'])
    out = []
    for y in range(len(G)):
        for x in range(len(G[0]) - 1):
            c, d = G[y][x], G[y][x + 1]
            if (cave and c == 0 and d == 0) or (not cave and c in GRASS and d in GRASS): out.append((x, y))
    return out


def run_away(b):
    b.battle()
    for i in range(20):
        if not b.in_battle() and not b.textbox(): return
        b.press('B', 30)


def sample(b, k, n=10, cave=False, tod=None, at=None, water=False):
    cs = [at] if at else cells(b, k, cave)
    assert cs, k
    x, y = cs[len(cs) // 2]
    b.warp(k, x, y, 120)
    for i in range(10):
        if b.textbox(): b.press('B', 20)
    if tod is not None: set_tod(b, tod)
    got = collections.Counter(); steps = 0
    while sum(got.values()) < n and steps < 1500:
        for d in ('R', 'L') if not water else ('U', 'D'):
            b.wait(random.randint(1, 40)); b.step(d); steps += 1
            if b.textbox() and not b.in_battle(): b.ev(40, shots=False)
            if b.in_battle():
                b.wait(30); b.bank1(); got[INV.get(b.peek(W_WILD)[0], b.peek(W_WILD)[0])] += 1
                run_away(b)
                if tod is not None: set_tod(b, tod)
    return dict(got)


if __name__ == '__main__':
    make_test_rom(SC + '/build/p57.gbc')
    b = Bot(state='postjhof2.st', out=SC + '/run/t57')
    print(b.where())
    print('tod', b.peek(W_TOD)[0], 'starthour', b.peek(W_STARTHOUR)[0])
    for h in range(0, 24, 3):
        b.g.poke(W_STARTHOUR, h); b.wait(4); print(h, b.peek(W_TOD)[0])
