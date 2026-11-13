import sys; sys.path.insert(0,'play'); sys.path.insert(0,'tools'); from bot import *
import build_phase14 as P
b=Bot(state=SC+'/play/k21.st', out=SC+'/play/run/silph2')
pn={l.split()[0]:tuple(map(int,l.split()[1].split(':'))) for l in open(SC+'/play/portnames.txt')}
k=pn['SilphCo5F']
b.warp(k,8,4); b.wait(60); b.shot('a')
b.face('L'); b.wait(10); print(b.where()); b.step('L'); b.wait(20); print('stepL',b.where()); b.shot('b')
b.face('L'); b.press('A',60); b.shot('c'); b.clear_text(shots=False)
b.giveitem(P.SILPH_CARD_KEY)
b.face('L'); b.press('A',60); b.shot('d'); b.press('A',60); b.shot('e'); b.clear_text(shots=False); b.wait(30); b.shot('f')
b.step('L'); b.wait(20); print(b.where()); b.step('L'); b.wait(20); print(b.where()); b.shot('g')
