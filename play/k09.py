import sys; sys.path.insert(0,'play'); from bot import *
import os
os.environ['GBWATCHLOG']=SC+'/play/run/watch.log'
b=Bot(state=SC+'/play/k09a.st', out=SC+'/play/run/k09')
b.g.cmd('watch DCC4 1')
orig=Bot.battle
def battle(s, maxp=300):
    lv=s.peek(0xDCC4)[0]; r=orig(s,maxp); lv2=s.peek(0xDCC4)[0]
    if lv!=lv2: print('LEVEL CHANGED', lv, lv2, s.where()); s.g.cmd('wflush'); sys.stdout.flush()
    return r
Bot.battle=battle
b.cross('U'); print(b.where(), b.names.get(b.where()[0])); b.shot()
print(b.db.warps(b.where()[0]), b.log)
b.g.save_state(SC+'/play/k09b.st')
b.sheet('a',8)
