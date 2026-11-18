import sys,os; R=sys.argv[1]; sys.argv=['x']; sys.path.insert(0,'play'); os.environ['PTROM']=R
import bot
bot.TEST='/tmp/ft/test.gbc'; bot.make_test_rom(bot.SC+'/build/%s.gbc'%R)
import pt as P, hon as Hn, honest as H
from bot import grid_of
b=bot.Bot(state='play/pt_h_jrematch.st', out='/tmp/ftx'); b.fs=[]; b.seen=set(); b.tag='f'
for i in range(6): b.press('B',20)
n=[0]
def sh(t):
    b.g.shot('/tmp/ft/%02d_%s.png'%(n[0],t)); n[0]+=1
res={}
def find_tile(k, coll):
    G=grid_of(b.db.r,b.db.maps[k]['hdr'])
    for y in range(1,len(G)-1):
        for x in range(1,len(G[0])-1):
            if G[y][x] in coll:
                for d,(dx,dy) in (('U',(0,-1)),('D',(0,1)),('L',(-1,0)),('R',(1,0))):
                    if G[y-dy][x-dx] in bot.WALK and G[y-dy][x-dx] not in (0x29,):
                        return (x-dx,y-dy,d)
    return None
# surf: Pallet water (coll 0x29 water)
k=(13,2); a=find_tile(k,{0x29}); print('surf at',a)
Hn.warp_to(b,k,a[0],a[1]); b.face(a[2]); b.wait(10); b.press('A',40); sh('surfq')
for i in range(5): b.press('A',40)
b.wait(60); b.bank1(); res['surf']=(b.peek(0xD950)[0], b.where()); sh('surf')
for i in range(4): b.press('B',20)
# save / continue
Hn.warp_to(b,(23,3),20,20); b.wait(30); pos=b.where()
b.press('S',40)
for i in range(12):
    t=b.tilemap(); rows=[y for y in range(18) if t[y*20+13]==0xED]
    if rows and b.has('レポート') and rows[0]==14: break
    b.press('D',15)
sh('menu'); b.press('A',60)
for i in range(14):
    if b.has('はい'): b.press('A',60)
    elif b.textbox(): b.press('A',40)
    else: b.wait(30)
sh('saved')
b.g.cmd('reset'); b.wait(500)
for i in range(12): b.press('A',60)
b.wait(200); sh('cont'); res['save']=(pos,b.where())
print(res)
