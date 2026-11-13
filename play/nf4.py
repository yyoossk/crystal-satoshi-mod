import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
ROM=sys.argv[1]
make_test_rom(SC+'/build/%s.gbc'%ROM)
b=Bot(state=SC+'/play/nf3_%s.st'%ROM, out=SC+'/run/nf4')
print(b.peek(0xD833)[0])
fs=[b.shot()]
b.wait(60); fs.append(b.shot())
b.step('D'); b.step('D'); fs.append(b.shot()); b.step('U'); fs.append(b.shot())
sheet(fs, SC+'/run/nf4.png', W=4)
