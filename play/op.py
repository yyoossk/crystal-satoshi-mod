import sys; sys.path.insert(0,'/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad/sameboy-harness/python')
from gr import GR
rom, tag, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
O='/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad/run/op/'+tag
g=GR(rom)
g.rec(O); g.wait(n); g.stop(); g.close()
