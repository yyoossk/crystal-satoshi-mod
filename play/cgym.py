import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k21.st', out=SC+'/play/run/cgym')
k=(26,61)
print('badges', b.peek(0xD857,2))
b.warp(k,16,16); b.wait(60); b.shot('in')
Q=[(15,7,False),(10,1,True),(9,7,True),(9,13,True),(1,13,False),(1,7,True)]
for i,(qx,qy,ans) in enumerate(Q):
    r=b.goto(qx,qy+1); print('q',i+1,'goto',r,b.where(), b.log[-1:] )
    b.face('U'); b.press('A',60)
    for j in range(8):
        b.press('A',40)
        if b.has('はい'): break
    wrong = (i==1)
    pick = (ans != wrong)  # answer yes?
    b.shot('q%d'%i)
    if not pick: b.press('D',20)
    b.press('A',60); b.shot('a%d'%i)
    b.ev(shots=False)
    if b.in_battle(): b.battle(); b.ev(shots=False)
    print('  after', b.where(), 'battle?', b.in_battle())
r=b.talk_to(3,3); print('blaine', r, b.where(), b.log[-3:])
for i in range(5): b.ev(shots=False)
print('badges', b.peek(0xD857,2)); b.shot('end')
b.g.save_state(SC+'/play/cgym.st')
