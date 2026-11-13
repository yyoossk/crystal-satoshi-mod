import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
ROM=sys.argv[1]
make_test_rom(SC+'/build/%s.gbc'%ROM)
b=Bot(state=SC+'/play/vir_%s.st'%ROM, out=SC+'/run/nf9c')
def dump(tag):
    b.bank1()
    u=b.peek(0xD185,64); print(tag, ' '.join('%02x:%02x'%(u[2*i],u[2*i+1]) for i in range(32) if u[2*i]))
b.wait(30); print(b.where()); dump('vir')
r=b.travel('Route22'); print(b.where()); b.wait(30); dump('r22')
b.goto(30,5)
fs=seq(b,'L',30,'l',2)
for i in range(40):
    fs.append(b.shot())
    if b.in_battle():
        for j in range(14): b.wait(60); fs.append(b.shot()); print(b.pc())
        b.g.save_state(SC+'/play/r22b_%s.st'%ROM)
        break
    elif b.textbox(): b.press('A',30)
    else: b.wait(5)
for j in range(16): b.wait(50); fs.append(b.shot()); b.press('A',10)
print(b.pc())
sheet(uniq(fs)[-16:], SC+'/run/nf9c.png', W=8)
