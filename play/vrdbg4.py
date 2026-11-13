import sys; sys.path.insert(0,'play'); from soko import *
b=Bot(state=SC+'/play/vr_carpet.st', out=SC+'/play/run/vrdbg4')
b.goto(9,17); b.face('U'); b.press('A',60); b.shot('a'); b.press('A',40); b.shot('b'); b.press('A',40); b.shot('c'); b.clear_text(shots=False)
b.g.down('U')
for j in range(12): b.wait(6)
b.g.up('U'); b.wait(40); print(b.where(), b.boulders())
# compare: push left from (10,16)? try from (8,16) R
b.g.load_state(SC+'/play/vr_carpet.st'); b.wait(5)
print(b.where()); b.g.down('R'); 
for j in range(12): b.wait(6)
b.g.up('R'); b.wait(40); print('R from 7,16?', b.where(), b.boulders())
print([hex(v) for v in b.peek(0xD84A,2)])
