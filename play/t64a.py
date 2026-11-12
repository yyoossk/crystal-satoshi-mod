from t64 import *
import glob
from PIL import Image
def strip(d, tag):
    fs=sorted(glob.glob(d+'/*.png'))
    cols=6; rows=(len(fs)+cols-1)//cols
    W=Image.new('RGB',(160*cols,144*rows),'white')
    for i,f in enumerate(fs): W.paste(Image.open(f),(160*(i%cols),144*(i//cols)))
    W.save(d+'_'+tag+'.png')
def settle(b, n=12):
    for i in range(n):
        b.press('A',40)
    for i in range(4): b.press('B',30)
if __name__=='__main__':
    b=Bot(state='postjhof2.st', out=OUT+'/a3')
    b.warp((24,4),13,7); b.wait(60); settle(b)
    b.shot('field')
    b.g.down('L'); xs=[]
    for i in range(20): b.g.wait(1); xs.append(b.peek(0xFF43)[0])
    b.g.up('L'); b.wait(30); print('walk', xs)
    b.g.down('LB'); xs=[]
    for i in range(20): b.g.wait(1); xs.append(b.peek(0xFF43)[0])
    b.g.up('LB'); b.wait(30); print('dash', xs)
    b.shot('after')
    b.press('S',40); b.shot('start')
    for i in range(8): b.press('D',15)
    b.shot('start_bottom')
    b.press('B',30)
    strip(b.out,'s')
