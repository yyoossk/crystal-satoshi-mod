from t57 import *
import build_phase57 as P
make_test_rom(SC + '/build/p57.gbc')
b = Bot(state='postjhof2.st', out=SC + '/run/t57w')
G = {n: (r, m) for n, r, m in P.kit_grass()}
jobs = [('VIRIDIAN_FOREST', [1]), ('POKEMON_MANSION_1F', [1]), ('POKEMON_MANSION_B1F', [0, 1, 2]), ('CERULEAN_CAVE_1F', [0, 1, 2]),
        ('POWER_PLANT', [1]), ('ROUTE_8', [1]), ('SEAFOAM_ISLANDS_B2F', [2]), ('ROUTE_23', [0])]
for name, tods in jobs:
    k = P.KIT_MAP[name]; cave = k[0] == 26 and name != 'VIRIDIAN_FOREST' and not name.startswith('SAFARI')
    for t in tods:
        exp = set(INV[s] for lv, s in G[name][1][t * 7:t * 7 + 7])
        got = sample(b, k, n=12, cave=cave, tod=t)
        print(name, t, got, 'OK' if set(got) <= exp and got else 'BAD', sorted(exp), flush=True)
