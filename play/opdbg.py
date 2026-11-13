import sys; sys.path.insert(0,'/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad/sameboy-harness/python')
from gr import GR
g=GR(sys.argv[1])
for f in (300,480,600,900,1200):
    g.wait(f-(0 if f==300 else prev)) if False else None
prev=0
for f in (300,480,600,900,1200):
    g.wait(f-prev); prev=f
    print(f, 'C100', hex(g.peek(0xc100)[0]), 'ram', bytes(g.peek(0xc101,0x30)).hex(), 'NR', bytes(g.peek(0xff24,3)).hex(), g.pc())
g.close()
