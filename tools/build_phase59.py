#!/usr/bin/env python3
"""Phase 59: the Celadon prize room's Pokémon as in the Pikachu version / the Pikachu full-color hack (no Gen II
Pokémon in Kanto): Abra 230 (Lv 15), Vulpix 1000 (Lv 18), Wigglytuff 2680 (Lv 22), Scyther 6500 (Lv 30),
Pinsir 6500 (Lv 30), Porygon 9999 (Lv 26) instead of Crystal's Pikachu, Porygon and Larvitar.  Crystal's counter
shows the first three, 「つぎへ」 the other three (the Pikachu version's two counters); Crystal's lines and coin box.
usage: build_phase59.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
from evedit import MapEvents

PB = 0x47
COIN_CASE = 0x36
PRIZES = [[('ケーシィ', 63, 15, 230), ('ロコン', 37, 18, 1000), ('プクリン', 40, 22, 2680)],
          [('ストライク', 123, 30, 6500), ('カイロス', 127, 30, 6500), ('ポリゴン', 137, 26, 9999)]]
# Crystal's (JP) prize room script, bank 1A: the Pokémon counter and the routines it uses
VENDOR = 0x74C6
INTRO, ASK, HERE = 0x75FC, 0x762F, 0x7649
ASKBUY, NOT_ENOUGH, NO_ROOM, CANCEL, NO_CASE = 0x7469, 0x7479, 0x747F, 0x7485, 0x748B
SPECIAL_COINS = 0x004F
SFX_TRANSACTION = 0x0022


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    f, n = bank_free_tail(rom, PB); sp.set_area(PB, f + 16, PB * 0x4000 + 0x4000)
    me = MapEvents(rom, 'CeladonGameCornerPrizeRoom'); sb = me.a['scbank']
    assert ('far', sb, VENDOR) in [b[3] for b in me.bgs]
    v = fo(sb, VENDOR)
    assert rom[v:v + 12] == bytes([0x6A, 0x47, 0x4C, INTRO & 0xFF, INTRO >> 8, 0x53, 0x21, COIN_CASE, 0x08, NO_CASE & 0xFF, NO_CASE >> 8, 0x4C])
    a = Asm(sp.here(PB)); a.bank = PB
    def far(op, l): a.db(op, sb); a.dw(l)
    a.label('v'); a.faceplayer(); a.opentext(); far(0x4B, INTRO); a.waitbutton()
    a.checkitem(COIN_CASE); a.iftrue('p0'); far(0x04, NO_CASE)
    for k, page in enumerate(PRIZES):
        a.label('p%d' % k); far(0x4B, ASK); a.special(SPECIAL_COINS)
        a.db(0x4F); a.dw('mh%d' % k); a.db(0x58, 0x50)                       # loadmenu / verticalmenu / closewindow
        for i in range(3): a.ifequal(i + 1, 'g%d%d' % (k, i))
        if k == 0: a.ifequal(4, 'p1')
        far(0x04, CANCEL)
        for i, (nm, mon, lv, coins) in enumerate(page):
            a.label('g%d%d' % (k, i))
            a.db(0x27); a.dw(coins); a.ifequal(2, 'ne')                       # checkcoins / HAVE_LESS
            a.db(0x1C, 0x01); a.ifequal(6, 'nr')                               # readvar VAR_PARTYCOUNT / PARTY_LENGTH
            a.db(0x40, mon, 0x00); far(0x01, ASKBUY); a.iffalse('cn')         # getmonname / farscall askbuy
            a.waitsfx(); a.playsound(SFX_TRANSACTION); far(0x4B, HERE); a.waitbutton()
            a.givepoke(mon, lv); a.db(0x26); a.dw(coins); a.sjump('p%d' % k)   # takecoins
    a.label('ne'); far(0x04, NOT_ENOUGH)
    a.label('nr'); far(0x04, NO_ROOM)
    a.label('cn'); far(0x04, CANCEL)
    for k, page in enumerate(PRIZES):
        a.label('mh%d' % k); a.db(0x40, 0x02, 0x00, 0x0B, 0x0F); a.dw('md%d' % k); a.db(0x01)
        a.label('md%d' % k); a.db(0x80, 0x04)
        for nm, mon, lv, coins in page:
            a.raw(encode(nm + '　' * (8 - len(nm)) + ('%4d' % coins).replace(' ', '　') + '@'))
        a.raw(encode(('つぎへ' if k == 0 else 'やめる') + '@'))
    base = a.base; blob = a.done(); assert sp.put(PB, blob) == base
    lv_ = a.labels['v']; rom[v:v + 4] = bytes([0x04, PB, lv_ & 0xFF, lv_ >> 8])
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    print('prize room Pokémon counter -> %02X:%04X (%d bytes)' % (PB, base, len(blob)))


if __name__ == '__main__':
    main()
