from pt import *
b = B('s6a', 's7')
b.go_warp(b.ids['PalletTown']); b.wait(40); print('pallet', mus(b)); snap(b)
b.go_warp((13,3)); b.wait(40); snap(b)
b.talk_to(5,3,n=0); snap(b); ev(b,20)    # Mom: heal
print('mom', b.where(), mus(b))
b.go_warp(b.ids['PalletTown']); b.wait(40)
b.travel('Route1'); b.wait(60); print('route1', b.where(), mus(b)); snap(b)
b.g.save_state(ST % 's7a')
talk_all(b); read_signs(b)
print('route1 done', b.where(), mus(b))
done(b, last=120)
