import sys; sys.path.insert(0,'play'); import soko; from mlib import *
b=Bot(state=SC+'/play/vr3.st', out=SC+'/play/run/vr4d')
b.refresh_grid(); plan=solve(b,(22,3),(3,5))[:18]
soko.solve=lambda s,bp,t: plan
print(b.push_to((22,3),(8,1)), b.log[-3:], b.where(), b.boulders())
b.g.save_state(SC+'/play/vr4d.st')
G=b.refresh_grid(); print([[hex(G[y][x]) for x in range(4,10)] for y in range(0,3)])
print(b.goto(7,0), b.where()); b.step('L'); print(b.where()); b.shot('a')
