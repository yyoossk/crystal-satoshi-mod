#!/usr/bin/env python3
"""Phase 83: the Johto story is three years after the Kanto one (as in the originals: Gold / Silver / Crystal take
place three years after Red / Green / Blue / Pikachu), and the lines fit a player who is Kanto's champion (Satoshi):
 * Prof. Oak's ticket after the Kanto Hall of Fame: "it has already been three years since you won the League".
   Phase 49's "Team Rocket was disbanded the other day" goes back to "three years ago".
 * Lake of Rage: Lance introduced himself as a stranger -> he knows Satoshi from the Pokémon League.
 * Clair (after her defeat): "you could never challenge the League" -> "even a League champion, I cannot accept you yet".
 * Route 27: "your first step into Kanto" -> "your home Kanto is just ahead".
 * Blackthorn Gym trainer: "Lance said to meet you again? No way!" -> "as expected of the champion".
 * Vermilion Pokémon Fan Club (Kanto: Gen I only): the woman's Bayleef -> Oddish (the overworld sprite is Oddish's).
 * The rival in Victory Road: "challenging the League now? You're weaker than me" -> "the champion is coming back
   to the League? Don't get cocky".
 * Johto League (the same Indigo Plateau): Will became one of the Elite Four after Satoshi became champion; Koga
   ("long time no see") and Bruno ("I'll pay you back for my defeat") know him; Lance kept the champion's seat since
   Satoshi left the League and gives it back; the Hall of Fame: "the League champion has come back".
   The Elite Four rooms run a copy of these texts in bank 7B: identical copies are changed too.
usage: build_phase83.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
from evedit import copy_text


PAIRS = {'の　': '{25}', 'は　': '{24}', 'に　': '{1D}', 'を　': '{1F}', 'が　': '{4A}'}   # the game's two-character codes


def T(s):
    for k, v in PAIRS.items(): s = s.replace(k, v)
    return encode('{00}' + s) + b'\x57'


TEXTS = {
    (0x1F, 0x58CD): '<PLAYER>じゃないか！<LINE>きみも　うわさを　ききつけて<CONT>やってきたのかい？<PARA>'
                    '<POKEMON>りーグで　たたかって<LINE>いらいだな<PARA>'
                    'おれも　ここの　うわさを　ききつけ<LINE>しんそうを　しらべていたんだが<……><PARA>'
                    '{14}！<LINE>きみの　じつりょくは<CONT>よく　しっている<PARA>'
                    'よかったら　おれと　いっしょに<LINE>しらべて　くれないか？',
    (0x1E, 0x4F57): 'わたしは　みとめないわ<PARA>まけて　いうのも　なんだけど<LINE>'
                    'りーグの　チャンピオン　でも<CONT>いまの　あなたは　みとめられない<PARA><……>　そうだわ！<PARA>'
                    'この　<POKEMON>ジムの　うらに<LINE>りゅうのあな　とよばれる<CONT>ばしょが　あるの<PARA>'
                    'ちゅうおうに　ほこらが　あるから<LINE>そこへ　いきなさい<PARA>もし　そこで　あなたが<LINE>'
                    'あまい　かんがえを　かえられたなら<PARA>ジムバッジを　わたすに　ふさわしい<LINE>{5D}として　みとめてあげるわ！',
    (0x26, 0x50A8): 'きみは　いま！<PARA>ふるさとの　カントーちほうは<LINE>もう　すぐ　そこだ！<PARA>'
                    'なんだったら　タウンマップで<LINE>かくにんして　ごらん！',
    (0x1E, 0x5191): 'えっ！　ワタルさまに<LINE>また　あおうって　いわれたのかい？<CONT>さすが　チャンピオン　だね！',
    (0x1D, 0x5D56): 'みて　みて！<LINE>わたしの　ナゾノクサ！<PARA>あたまの　はっぱが<LINE>すっごく　キュート！',
    (0x1D, 0x5D96): 'ナゾノクサ{72}くさー！',
    (0x1F, 0x6FCD): 'まてよ<PARA><……>　チャンピオン　さまが<LINE>また　りーグに　もどるのか？<PARA><……>　いい　きに　なるなよ<LINE>'
                    'いままでの　オレと　おもうなよ！<PARA>さいこう　さいきょうの<LINE><POKEMON>を　てにいれた！<CONT>'
                    'オレには　だれも　かてないぜ！<PARA><PLAYER>！<LINE>オレと　しょうぶ　しろ！',
    (0x78, 0x5D5C): 'オーキド{72}おお　<PLAYER>！<LINE>りーグを　せいは　してから<CONT>もう　3ねんか<……><PARA>'
                    'じつは　ジョウトの<LINE>ワカバタウンに　いる<CONT>ウツギはかせから<CONT>れんらくが　あってな<PARA>'
                    'おまえに　ぜひ<LINE>あいたい　そうじゃ！<PARA>そこで<……>　これを　やろう！',
}
TEXTS_E4 = {
    (0x1D, 0x689D): 'きみが　うわさの　チャンピオンか！<PARA>ボクの　なまえは　イツキ<PARA>'
                    'きみが　チャンピオンに　なったあと<LINE>してんのうの　ひとりに　なったんだ<PARA>'
                    'ボクは　もっと　つよくなる！<LINE>ここで　まけるわけには　いかない！',
    (0x1D, 0x6FA2): 'ワタル{72}まっていたよ！<PARA>{14}！<PARA>きみが　りーグを　さってから<LINE>'
                    'チャンピオンの　ざは<CONT>おれが　あずかっていた<PARA>ただ　どちらが　つよいか<LINE>たたかって　きめるだけ！<PARA>'
                    'ドラゴンつかいの　ワタル<LINE>いざ　まいる！',
    (0x1D, 0x7025): '<……>　おわった<PARA>やはり　きみには　かなわないな<PARA>チャンピオンの　ざは<LINE>きみに　かえすよ',
    (0x1D, 0x72B6): 'ワタル{72}<……>　この　へやに<LINE>はいるのも　ひさしぶり　だな<PARA>ここは　りーグ　チャンピオンの<LINE>'
                    'えいこうを　たたえるため<CONT>はげしい　たたかいを　かちぬいた<CONT><POKEMON>たちを　えいえんに<CONT>'
                    'きろくする　ばしょ　なんだ！<PARA>いま　ここに<LINE><POKEMON>への　やさしさと　しんらい<PARA>'
                    'じぶんへの　つよさと　きびしさ<PARA>だいじなものを　もった<LINE>りーグ　チャンピオンが　もどった！<PARA>'
                    'さあ　{14}！<LINE>きみと　きみの　パートナーを<CONT>きろく　しよう！',
    (0x1D, 0x6A06): '<……>　ファ　ファ　ファ！<PARA>ひさしぶり　よのう　<PLAYER>！<LINE>いまは　してんのうの　キョウ　よ！<PARA>'
                    'せっしゃの　たたかいかた<LINE>ひとすじなわ　では　いかんぞ！<PARA>まどわし　ねむらせ<LINE>どくを　くらわせる<……><PARA>'
                    '<……>　ファ　ファ　ファ！<PARA>'
                    'ちから　だけでは　およばない　<LINE><POKEMON>の　おくぶかさ<CONT>たっぷりと　あじわうが　よい！',
    (0x1D, 0x6BA1): 'また　あったな　<PLAYER>！<PARA>おれは　じぶんたちが　もっている<LINE>かのうせいを　しんじて<CONT>'
                    'あれから　さらに　きたえてきた<PARA>まえに　まけた　かりは<LINE>きょう　ここで　かえさせて　もらう！<PARA>'
                    'ウー！　ハーッ！',
}
REPLACE = {(0x18, 0x697E): [('つい　この　まえ', '3ねんほど　まえ')]}   # phase 49's change back: three years later
FAN_CLUB_CRY = (0x1D, 0x5A46)       # cry BAYLEEF -> ODDISH
ODDISH, BAYLEEF = 43, 153


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    allt = dict(TEXTS); allt.update(TEXTS_E4)
    for b in sorted({b for b, a in allt}):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    log = []
    for (b, a), s in allt.items():
        o = fo(b, a); old = copy_text(rom, o); new = T(s)
        c = rom.find(old)   # identical copies (the Elite Four rooms run a copy of bank 1D in 7B)
        while c >= 0:
            if c != o and len(new) <= len(old):
                rom[c:c + len(new)] = new; log.append('  copy at %02X:%04X' % (c // 0x4000, c % 0x4000 + 0x4000))
            c = rom.find(old, c + 1)
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
