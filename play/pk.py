import sys; sys.path.insert(0, sys.argv[2] if len(sys.argv)>2 else '')
sys.path.insert(0,'/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad/sameboy-harness/python')
from gr import GR
D='/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad/play/run/pk/'
g=GR(D+sys.argv[1])
g.wait(400)
n=0
for i in range(120):
    g.press('A' if i%5 else 'S',4,40)
    if i%10==0: g.shot(D+'s%03d.png'%i)
g.save_state(D+'a.st')
