from pt import *
b = B('s14a', 'g1')
print('start lv', lv(b), hp(b))
grind(b, 14, area='Route1', spot=(12,6))
b.travel('ViridianCity')
b.g.save_state(ST % 'g1a')
print('done lv', lv(b), b.where())
