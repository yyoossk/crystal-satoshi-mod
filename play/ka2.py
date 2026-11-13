from kt import *
rom = sys.argv[1]; m, d = sys.argv[2], sys.argv[3]; keys = sys.argv[4] if len(sys.argv)>4 else ''
b = start(rom, state=('kitbase.st' if rom=='kit60' else 'blogbase2.st'), out='a2_%s_%s_%s%s'%(rom,m,d,keys))
go_edge(b, m, d, 3)
rec = hold(b, d + keys, 110, shots=set(range(110)))
maps = [r[2] for r in rec]; ch = next((i for i in range(1,len(maps)) if maps[i]!=maps[i-1]), None)
print('mapchange', ch, 'stall', stall(rec[3:]))
from PIL import Image
fs=['%s/f%03d.png'%(b.out,i) for i in range(ch-8, ch+24)]
W=8; im=Image.new('RGB',(162*W,146*((len(fs)+W-1)//W)),'white')
for i,f in enumerate(fs): im.paste(Image.open(f),(162*(i%W),146*(i//W)))
im.save(b.out+'.png'); print(b.out+'.png')
b.g.close()
