import sys; sys.path.insert(0,'play'); from soko import *
b=Bot(state=SC+'/play/vr_carpet.st', out=SC+'/play/run/vrdbg5')
def push(d):
    bb=b.boulders(); b.g.down(d)
    for j in range(12): b.wait(6)
    b.g.up(d); b.wait(40); return b.boulders()!=bb
for seq,d in [('LR','R'),('DRR','U'),('DLUR','R')]:
    b.g.load_state(SC+'/play/vr_carpet.st'); b.wait(5)
    for c in seq: b.step(c); b.wait(10)
    print(seq, b.where(), 'push', d, push(d))
