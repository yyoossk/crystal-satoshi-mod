from pt import *
b = B('s1b', 'dbg')
b.go_warp(b.ids['PalletTown']); b.wait(60)
print(b.objpos(), b.where())
p=b.objpos()[0]
b.talk_to(*p, n=0); print(b.where(), b.objpos(), b.peek(0xD03A)[0] if False else '')
for i in range(6):
    b.press('A',10); snap(b); b.wait(20); snap(b)
done(b)
