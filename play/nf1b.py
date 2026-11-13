import sys; sys.path.insert(0,'play')
from t64a import *
from kt import seq, uniq, sheet
ROM=sys.argv[1]
make_test_rom(SC+'/build/%s.gbc'%ROM)
b=Bot(state=SC+'/play/ng_%s.st'%ROM, out=SC+'/run/nf1b')
print(b.where())
b.goto(7,1); print(b.where())
fs=seq(b,'U',120,'u',3)
print(b.where())
sheet(uniq(fs)[:40], SC+'/run/nf1b.png', W=8)
