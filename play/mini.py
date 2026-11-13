import sys, glob
from PIL import Image
d=sys.argv[1]; out=sys.argv[2]; step=int(sys.argv[3]) if len(sys.argv)>3 else 1
excl=sys.argv[4].split(',') if len(sys.argv)>4 else []
fs=sorted(glob.glob(d+'/*.png'))
fs=[f for f in fs if not any(f.endswith('_%s.png'%e) for e in excl)][::step]
cols=10; rows=(len(fs)+cols-1)//cols
W=Image.new('RGB',(160*cols,144*rows),'white')
for i,f in enumerate(fs): W.paste(Image.open(f),(160*(i%cols),144*(i//cols)))
(W.save(out) if fs else None); print(len(fs))
