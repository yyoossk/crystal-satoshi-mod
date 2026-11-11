#!/usr/bin/env python3
"""Phase 49: Johto's lines for a player who comes from Kanto (the Kanto champion, his mother in Pallet Town):
 * Prof. Elm: the Pokémon he gives is the player's partner in Johto (not his first); "tell your mother in Pallet";
   the ship ticket after the Elite Four: "now you can go home to Kanto any time" (the player already holds a ticket:
   it is taken first, so Elm's gift works).
 * Elm's aide (Poké Balls): the player knows how to catch Pokémon.
 * New Bark Town: the woman who stops the player before he has seen Elm, and her line afterwards.
 * Mom's first phone call: she heard from Prof. Oak that he reached Johto.
 * A phone caller saw the player's mother in Pallet Town (Crystal: New Bark Town).
 * "Team Rocket was disbanded by a boy three years ago" -> "the other day".
usage: build_phase49.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
from evedit import copy_text
import build_phase17 as P17

S_S_TICKET = 0x44
ELM_TICKET = (0x1B, 0x6448)        # Elm: verbosegiveitem S_S_TICKET (after the Elite Four)


def T(s): return encode('{00}' + s) + b'\x57'


TEXTS = {
    (0x1B, 0x67B0): 'そだてて　ほしい　<POKEMON>が<LINE>この　ボールに　はいっているよ！<PARA>{14}の　ジョウトでの<LINE>'
                    'パートナーだよ<PARA>さあ　えらんでよ！',
    (0x1B, 0x6B6F): '<……>　{14}<LINE>ジョウトの　たびも<CONT>ながく　なると　おもう<PARA>'
                    'マサラの　おかあさんにも<LINE>れんらく　しておくんだよ',
    (0x1B, 0x6E91): 'ウツギ{72}やあ　{14}<LINE>まっていたよ！<PARA>きょう　きみを　よんだのは<LINE>あげたいものが　あるからなんだ！<PARA>'
                    'ほら！<LINE>ふねのチケット<PARA>これで　いつでも<LINE>カントーに　かえれるね！',
    (0x1B, 0x7044): '{14}　なら<LINE>つかいかたは　わかってますよね！<PARA>ジョウトの　<POKEMON>も<LINE>どんどん　つかまえて　くださいね！',
    (0x27, 0x412C): 'まって！<LINE>ウツギはかせが<CONT>きみを　まってるわよ！<PARA>さきに　けんきゅうじょへ<LINE>いってらっしゃい！',
    (0x27, 0x4185): 'あら　{14}！<LINE>また　でかけるの？<PARA>きを　つけて<LINE>いってらっしゃい！',
    (0x29, 0x5A6E): 'もしもし…<PARA><……>　<PLAYER>？<LINE>オーキドはかせから　きいたわ<CONT>ジョウトに　ついたのね！<PARA>'
                    'おかねとかって　どうするの？<LINE>おかあさん　ちょきんしてあげようか？',
}
REPLACE = {(0x5D, 0x6039): [('ワカバタウンまで', 'マサラタウンまで')],
           (0x18, 0x697E): [('3ねんほど　まえ', 'つい　この　まえ')]}


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    banks = sorted({b for b, a in TEXTS} | {ELM_TICKET[0]})
    for b in banks:
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    log = []
    for (b, a), s in TEXTS.items():
        o = fo(b, a); old = copy_text(rom, o); new = T(s)
        if len(new) <= len(old):
            rom[o:o + len(new)] = new; log.append('%02X:%04X in place' % (b, a)); continue
        na = sp.put(b, new); seg = rom[b * 0x4000:(b + 1) * 0x4000]; n = 0
        for k in range(len(seg) - 2):
            if seg[k] in (0x4C, 0x51, 0x52) and seg[k + 1] == a & 0xFF and seg[k + 2] == a >> 8:
                rom[b * 0x4000 + k + 1] = na & 0xFF; rom[b * 0x4000 + k + 2] = na >> 8; n += 1
        assert n >= 1, ('no reference', hex(b), hex(a))
        log.append('%02X:%04X -> %04X (%d references)' % (b, a, na, n))
    for (b, a), pairs in REPLACE.items():
        o = fo(b, a); old = copy_text(rom, o)
        for x, y in pairs:
            ex, ey = encode(x).rstrip(b'\x50'), encode(y).rstrip(b'\x50'); assert len(ex) == len(ey)
            i = old.index(ex); rom[o + i:o + i + len(ey)] = ey
    # Elm's ship ticket: the player already has one (Kanto)
    o = fo(*ELM_TICKET); assert rom[o:o + 3] == bytes([0x9D, S_S_TICKET, 1])
    st = sp.put(ELM_TICKET[0], bytes([0x20, S_S_TICKET, 1, 0x9D, S_S_TICKET, 1, 0x90]))
    rom[o:o + 3] = bytes([0x00, st & 0xFF, st >> 8])

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    print('\n'.join(log))


if __name__ == '__main__':
    main()
