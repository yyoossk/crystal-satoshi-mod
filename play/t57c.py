"""fishing statistics per map (calls the fishing routine as 03:51F3 does), and wild samples"""
from t57 import *
import sys
make_test_rom(SC + '/build/p57.gbc')
r = open(SC + '/build/p57.gbc', 'rb').read()
fc = r[0xD1F3:0xD1F9]; assert fc[0] == 0x3E and fc[5] == 0xCF
def fishstats(b, k, rod, n=60):
    if b.where()[0] != (13, 2):
        for t in range(4):
            b.warp((13, 2), 5, 8, 120)
            if b.where()[0] == (13, 2): break
    asm = bytes([0x3E, k[0], 0xEA, 0x7B, 0xDC, 0x3E, k[1], 0xEA, 0x7C, 0xDC])
    asm += bytes([0x16, 0x01, 0x1E, rod]) + fc + bytes([0x7A, 0xEA, 0xDD, 0xC2, 0x3E, 13, 0xEA, 0x7B, 0xDC, 0x3E, 2, 0xEA, 0x7C, 0xDC, 0xC9])
    for i, v in enumerate(asm): b.g.cmd('rpoke %x %d' % (SOFF + 0x40 + i, v))
    c = collections.Counter()
    for i in range(n):
        b.script([0x0E, SB, (SA + 0x40) & 0xFF, (SA + 0x40) >> 8], 6)
        b.bank1(); v = b.peek(0xC2DD)[0]; c[INV.get(v, v) if v else '-'] += 1
    return dict(c)
if __name__ == '__main__':
    b = Bot(state='postjhof2.st', out=SC + '/run/t57c')
    import build_phase57 as P
    old, good, sup, fmaps = P.kit_fish()
    for name in sys.argv[1:] or ['PALLET_TOWN', 'ROUTE_12', 'SAFARI_ZONE_CENTER', 'SEAFOAM_ISLANDS_B4F', 'CERULEAN_CAVE_B1F', 'FUCHSIA_CITY']:
        k = P.KIT_MAP[name]
        exp = sorted(set(INV[s] for _, s, _ in sup[fmaps[name]]))
        print(name, k, 'super', fishstats(b, k, 2), 'expect', exp, flush=True)
    print('old', fishstats(b, P.KIT_MAP['ROUTE_12'], 0, 20), flush=True)
    print('good', fishstats(b, P.KIT_MAP['ROUTE_12'], 1, 30), flush=True)
    print('johto route 32 (Crystal)', fishstats(b, (10, 1), 2, 20), flush=True)
