import sys, json; sys.path.insert(0,'play'); from mlib import *
log=json.load(open(SC+'/play/k11_log.json'))
b=Bot(state=SC+'/play/k11_30.st', out=SC+'/play/run/replay')
for i,c in enumerate(log):
    b.g.cmd(c)
    p=b.pc()
    if 'sp=c' not in p and 'sp=d' not in p:
        print('crash after cmd', i, c, p); break
    if i%10==0: b.g.save_state(SC+'/play/rp_%d.st'%i)
print(log[max(0,i-12):i+1])
