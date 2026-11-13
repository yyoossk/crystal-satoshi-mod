import sys; sys.path.insert(0,'sameboy-harness/python')
from gr import GR
g=GR('akafc/akafc.gbc')
g.wait(900); g.press('S',4,60); g.press('A',4,60); g.press('A',4,90)
for i in range(30):
    g.press('A',4,50)
    g.shot('run/akaint_%02d.png'%i)
    p=g.pals(); print(i, p.split()[0][3:3+64])
