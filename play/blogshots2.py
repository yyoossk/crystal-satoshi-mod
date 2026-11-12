import sys; sys.path.insert(0,'.')
from t64c import *
make_test_rom(SC+'/build/p64.gbc')
O=SC+'/run/blog/ui'
import os; os.makedirs(O,exist_ok=True)
b=Bot(state='blogbase2.st', out=O+'/x')
def S(n): b.g.shot(O+'/'+n+'.png')
# start menu
b.press('S',40); S('start')
b.press('D',15); b.press('A',60); b.press('A',40); S('submenu')
for i in range(4): b.press('B',30)
# battle: move box
b.giveitem(0x05,30); setlast(b,0x05)
b.script([0x5C, 0x10, 5, 0x5E, 0x5F], 30)
for i in range(60): b.wait(10)
b.press('A',30); b.wait(300); b.press('A',60); b.wait(30); S('moves')
b.press('B',40); b.wait(30)
# quick ball
b.g.press('s',6,30); b.wait(40); S('ball')
for i in range(30):
    b.press('B',40)
b.wait(200)
for i in range(30):
    if not b.in_battle(): break
    b.press('B',40)
# TM shop
b.warp((26,128),16,7); b.wait(80); b.clear_text(shots=False)
b.talk_to(16,5,n=0)
for i in range(12):
    b.press('A',50)
    if b.has('わざマシン０１'): break
S('tm1')
for i in range(3): b.press('A',60)
S('tm2')
for i in range(8): b.press('B',40)
# daycare
k2=b.ids['DayCare']; b.warp(k2,2,5); b.wait(60); b.clear_text(shots=False)
b.talk_to(2,3,n=0)
for i in range(4): b.press('A',50)
S('daycare')
for i in range(8): b.press('B',40)
