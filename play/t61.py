from t57b import act, act2, party, INV
from t57 import *
from lib import mapid
import sys
make_test_rom(SC + '/build/p61.gbc')
what = sys.argv[1:]
ILEX, LAB = mapid('IlexForest'), (24, 5)
def flags(b): b.bank1(); return [hex(x) for x in b.peek(0xD836, 2)]
if 'celebi' in what:
    b = Bot(state='postjhof2.st', out=SC + '/run/t61/celebi')
    print('flags', flags(b))
    act(b, ILEX, 8, 23, 'U', 'c1'); b.wait(200); b.bank1()
    print('battle', b.in_battle(), INV.get(b.peek(W_WILD)[0]), 'lv?', b.peek(0xD25F - 0x31 + 0x14C - 0x14C, 1))
    b.shot('cb'); run_away(b); b.shot('ca'); act2(b, 'ca'); print('after', flags(b))
    act(b, ILEX, 8, 23, 'U', 'c2'); act2(b, 'c2'); print('again battle', b.in_battle())
if 'prehof' in what:
    b = Bot(state='postjhof2.st', out=SC + '/run/t61/prehof')
    b.clrev(0x44); act(b, ILEX, 8, 23, 'U', 'p'); act2(b, 'p'); print('prehof battle', b.in_battle())
if 'elm' in what:
    b = Bot(state='postjhof2.st', out=SC + '/run/t61/elm')
    b.g.poke(0xDC9D, 1); print('flags', flags(b), b.flag(0x1a), b.flag(0x1b), b.flag(0x1c), b.flag(0x1d))
    act(b, LAB, 5, 3, 'U', 'e1'); act2(b, 'e1'); print('elm1', party(b), flags(b))
    act(b, LAB, 5, 3, 'U', 'e2'); act2(b, 'e2'); print('elm2', party(b), flags(b))
    b.g.save_state(SC + '/play/t61elm.st')
if 'new' in what:
    b = Bot(state='j01.st', out=SC + '/run/t61/new')
    print('got', b.flag(0x1a), party(b), b.where()); b.shot('start')
    b.step('R'); b.step('R'); b.step('R'); print(b.where()); b.face('U'); b.press('A', 40); act2(b, 'pick', 60)
    print('pick', party(b), flags(b), [b.flag(x) for x in (0x1a, 0x1b, 0x1c, 0x1d)])
    b.g.save_state(SC + '/play/t61new.st')
