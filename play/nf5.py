import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
ROM=sys.argv[1]
make_test_rom(SC+'/build/%s.gbc'%ROM)
b=Bot(state=SC+'/play/nf3_%s.st'%ROM, out=SC+'/run/nf5')
r=b.travel((26,97)); print('travel', r, b.where(), b.log[-5:])
b.ev()
print(b.where())
b.g.save_state(SC+'/play/nf5_%s.st'%ROM)
