import sys
sys.path.insert(0,'/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad/sameboy-harness/python')
from gr import GR
D='/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad/play/run/pk/'
g=GR(D+'pk_jessie.gbc', state=D+'a.st')
for k in 'BBBBBB': g.press(k,4,40)
seq='RRRRRUUUUUUU'
for i,k in enumerate(seq):
    g.press(k,16,10); g.shot(D+'m%02d.png'%i)
g.wait(120); g.shot(D+'m99.png')
g.save_state(D+'b.st')
