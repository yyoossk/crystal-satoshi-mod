from kt import *
b = start('p68', out='kts')
for m in ('Route1','PalletTown','ViridianCity','Route22','PewterCity','CeruleanCity','Route24','Route25','Route3','Route9','VermilionCity','Route29','CherrygroveCity','Route30','Route46','NewBarkTown','Route45','Route26'):
    try:
        b.warp(m,4,4); b.wait(60); b.bank1(); print(m, b.peek(0xD1CA)[0])
    except Exception as e: print(m, e)
b.g.close()
