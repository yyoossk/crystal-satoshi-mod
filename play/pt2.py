from pt import *
b = B('s1b', 's2')
b.go_warp(b.ids['PalletTown']); b.wait(60); snap(b)
print('pallet', mus(b), b.objpos())
talk_all(b); read_signs(b)
print('signs done', b.where())
b.g.save_state(ST % 's2a')
# Blue's house before the Pokedex
b.go_warp((13,5)); b.wait(30); snap(b); talk_all(b); read_signs(b)
b.go_warp(b.ids['PalletTown']); b.wait(30)
# Oak's lab before
b.go_warp((13,6)); b.wait(30); snap(b); talk_all(b); read_signs(b)
print('lab before', mus(b))
b.go_warp(b.ids['PalletTown']); b.wait(30)
done(b, last=96)
