from t57b import act, act2, party, INV
from t57 import *
make_test_rom(SC + '/build/p58.gbc')
b = Bot(state='postjhof2.st', out=SC + '/run/t58')
b.g.poke(0xDC9D, 1)
for tag, k, x, y, d in (('mel', (26, 73), 3, 2, 'U'), ('mel2', (26, 73), 3, 2, 'U'), ('bul', (26, 73), 4, 2, 'U'),
                        ('odd', (26, 73), 1, 5, 'U'), ('san', (26, 73), 5, 4, 'U'),
                        ('dam', (7, 15), 6, 6, 'U'), ('dam2', (7, 15), 6, 6, 'U'),
                        ('jen', (12, 3), 19, 16, 'U'), ('jen2', (12, 3), 19, 16, 'U')):
    act(b, k, x, y, d, tag); act2(b, tag); print(tag, party(b), b.objpos(), flush=True)
