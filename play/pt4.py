from pt import *
b = B('s3a', 's4')
for i in range(20):
    ev(b, 100)
    if b.where()[1:]==(4,3) and not b.textbox(): break
    b.wait(30)
print('intro done', b.where(), mus(b), b.objpos())
rv=[p for p in b.objpos() if p==(3,3)]
b.talk_to(3,3,n=0); snap(b); ev(b,10)
b.talk_to(4,2,n=0); snap(b); ev(b,10)    # Oak: which one?
# try leaving
b.goto(4,6); snap(b); ev(b,20); print('dontgo', b.where())
b.g.save_state(ST % 's4a')
done(b, last=96)
