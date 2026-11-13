from pt import *
b = B('s2', 's3')
b.goto(10,1)
for i in range(10):
    b.step('U'); snap(b)
    if b.textbox(): break
for i in range(40):
    ev(b, 200)
    if b.where()[0]==b.ids.get('OaksLab',(13,6)) and not b.textbox():
        b.wait(60); 
        if not b.textbox(): break
print('in lab', b.where(), mus(b), b.objpos())
b.g.save_state(ST % 's3a')
done(b, last=96)
