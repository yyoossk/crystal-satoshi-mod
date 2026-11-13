import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k07.st', out=SC+'/play/run/k08')
print(b.peek(0xD84A,2))
b.go_warp('PewterGym'); print(b.where(), b.objs_of())
br=[o for o in b.objs_of()][0]
b.talk_to(br[1],br[2])
print(b.where(), b.peek(0xD84A,2), b.log)
b.g.save_state(SC+'/play/k08.st')
b.sheet('a',8)
