#!/usr/bin/env python3
"""Phase 83: story lines that do not fit a player who is already Kanto's champion (Satoshi):
 * Lake of Rage: Lance introduced himself as a stranger -> he knows Satoshi from the Kanto League.
 * "Team Rocket was disbanded three years ago" -> "the other day" (Satoshi beat Giovanni in Kanto just before):
   the Rocket hideout, Kurt, the Slowpoke Well, the Radio Tower and a Goldenrod man.
 * Clair (after her defeat): "you could never challenge the League" -> winning in Kanto does not make Johto's League easy.
 * Route 27: "your first step into Kanto" -> "your home Kanto is just ahead".
 * Blackthorn Gym trainer: "Lance said to meet you again? No way!" -> "as expected of Kanto's champion".
 * Vermilion Pokémon Fan Club (Kanto: Gen I only): the woman's Bayleef -> Oddish (the overworld sprite is Oddish's).
 * Johto League: Koga (Satoshi beat him at the Fuchsia Gym) and Bruno (beaten at the Kanto League) know Satoshi.
usage: build_phase83.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
from evedit import copy_text


def T(s): return encode('{00}' + s) + b'\x57'


TEXTS = {
    (0x1F, 0x58CD): '<PLAYER>じゃないか！<LINE>きみも　うわさを　ききつけて<CONT>やってきたのかい？<PARA>'
                    'カントーの　りーグで　たたかって<LINE>いらいだな<PARA>'
                    'おれも　ここの　うわさを　ききつけ<LINE>しんそうを　しらべていたんだが<……><PARA>'
                    '{14}！<LINE>きみの　じつりょくは<CONT>よく　しっている<PARA>'
                    'よかったら　おれと　いっしょに<LINE>しらべて　くれないか？',
    (0x1E, 0x4F57): 'わたしは　みとめないわ<PARA>まけて　いうのも　なんだけど<LINE>'
                    'カントーで　かてたって<CONT>ジョウトは　むり　よ<PARA><……>　そうだわ！<PARA>'
                    'この　<POKEMON>ジムの　うらに<LINE>りゅうのあな　とよばれる<CONT>ばしょが　あるの<PARA>'
                    'ちゅうおうに　ほこらが　あるから<LINE>そこへ　いきなさい<PARA>もし　そこで　あなたが<LINE>'
                    'あまい　かんがえを　かえられたなら<PARA>ジムバッジを　わたすに　ふさわしい<LINE>{5D}として　みとめてあげるわ！',
    (0x26, 0x50A8): 'きみは　いま！<PARA>ふるさとの　カントーちほうは<LINE>もう　すぐ　そこだ！<PARA>'
                    'なんだったら　タウンマップで<LINE>かくにんして　ごらん！',
    (0x1E, 0x5191): 'えっ！　ワタルさまに<LINE>また　あおうって　いわれたのかい？<CONT>さすが　チャンピオン　だね！',
    (0x1D, 0x5D56): 'みて　みて！<LINE>わたしの　ナゾノクサ！<PARA>あたまの　はっぱが<LINE>すっごく　キュート！',
    (0x1D, 0x5D96): 'ナゾノクサ{72}くさー！',
    (0x1A, 0x6E30): 'ゲームコーナー{25}ちかには<LINE>{5E}{25}アジトが<……><PARA>おっと！<LINE>'
                    'それ{24}このあいだ<CONT>つぶれたんだった！',
}
TEXTS_E4 = {
    (0x1D, 0x6A06): '<……>　ファ　ファ　ファ！<PARA>ひさしぶり　よのう　<PLAYER>！<LINE>いまは　してんのうの　キョウ　よ！<PARA>'
                    'せっしゃの　たたかいかた<LINE>ひとすじなわ　では　いかんぞ！<PARA>まどわし　ねむらせ<LINE>どくを　くらわせる<……><PARA>'
                    '<……>　ファ　ファ　ファ！<PARA>'
                    'ちから　だけでは　およばない　<LINE><POKEMON>の　おくぶかさ<CONT>たっぷりと　あじわうが　よい！',
    (0x1D, 0x6BA1): 'また　あったな　<PLAYER>！<PARA>おれは　じぶんたちが　もっている<LINE>かのうせいを　しんじて<CONT>'
                    'あれから　さらに　きたえてきた<PARA>カントーで　まけた　かりは<LINE>ここで　かえさせて　もらうぞ！<PARA>'
                    'ウー！　ハーッ！',
}
REPLACE = {(0x19, 0x58C5): [('3ねんまえ', 'このあいだ')],
           (0x1C, 0x74D5): [('3ねんまえに', 'このあいだに')],        # Kurt
           (0x16, 0x5EC5): [('3ねんまえ', 'このあいだ')],        # Slowpoke Well grunt
           (0x17, 0x6A5B): [('3ねんまえ', 'このあいだ')],            # Radio Tower grunt
           (0x65, 0x76EC): [('3ねんまえ', 'このあいだ')]}            # its copy
FAN_CLUB_CRY = (0x1D, 0x5A46)       # cry BAYLEEF -> ODDISH
ODDISH, BAYLEEF = 43, 153


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    allt = dict(TEXTS); allt.update(TEXTS_E4)
    allt.update({(0x7B, a): t for (b, a), t in TEXTS_E4.items()})   # the Elite Four rooms run a copy of bank 1D in 7B
    for b in sorted({b for b, a in allt}):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    log = []
    for (b, a), s in allt.items():
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
            ex, ey = encode(x).rstrip(b'\x50'), encode(y).rstrip(b'\x50'); assert len(ex) == len(ey), (x, y)
            i = old.index(ex); rom[o + i:o + i + len(ey)] = ey
        log.append('%02X:%04X replaced' % (b, a))
    o = fo(*FAN_CLUB_CRY); assert rom[o:o + 3] == bytes([0x83, BAYLEEF, 0]); rom[o + 1] = ODDISH
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
