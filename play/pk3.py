import sys
sys.path.insert(0,'/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad/sameboy-harness/python')
from gr import GR
D='/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad/play/run/pk/'
for rom in ('pk_jessie.gbc','pk_james.gbc'):
    g=GR(D+rom, state=D+'b.st')
    for k in 'RRRRUUU': g.press(k,16,10)
    g.wait(150)
    for k in 'LLL': g.press(k,16,10)
    g.wait(60); g.shot(D+'x_'+rom+'.png'); print(rom, g.pals()); print(g.oam()[:48].hex())
