import sys,os; sys.path.insert(0,'/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad/sameboy-harness/python')
os.environ['GBWATCHLOG']='/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad/run/op/wsid.log'
from gr import GR
g=GR(sys.argv[1]); g.cmd('watch c102 1'); g.wait(1200); g.cmd('wflush'); g.close()
