import sys
src=open('kg1.py').read()
src=src.replace("        if caught>=4: break","        if caught>=1: break")
src=src.replace("b.g.close()","""
# leave the park by the south gate and end the contest
for c in ((10,46),(10,47)):
    b.goto(*c)
for i in range(6):
    b.step('D'); b.wait(40)
    if b.where()[0]!=(3,16): break
S('gate'); print('gate', b.where())
for i in range(80):
    b.press('A',40)
    if i%10==0: S('res%d'%i)
b.wait(200); S('free'); print('free', b.where(), len(b.objpos()))
import json; json.dump(b.where(), open(O+'/b1pos.json','w'))
b.g.save_state(O+'/b1.st')
sheet(fs[-12:], b.out+'_b1.png', W=6)
b.g.close()""")
exec(src)
