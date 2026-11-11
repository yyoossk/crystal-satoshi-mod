#!/usr/bin/env python3
"""Phase 50: Kanto's gym leaders after the Johto Hall of Fame.
The player already holds every Kanto badge (Crystal hands them out after the Johto League), so after Johto's Elite
Four (EVENT_BEAT_ELITE_FOUR) each Kanto gym leader offers a rematch, with Crystal's own team for that leader
(Brock, Misty, Lt. Surge, Erika, Janine, Sabrina, Blaine, Blue at Viridian); "no", or before the Johto League,
gives the leader's usual line.
usage: build_phase50.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import build_phase10 as P10
import build_phase13 as P13
import build_phase17 as P17

PB = 0x66
EV_BEAT_E4 = 0x44
# (bank, site of "checkflag/checkevent X ; iftrue post", trainer class, opens the text box itself)
LEADERS = [
    ('タケシ', 0x76, 0x7A99, 0x11, False,
     'ジョウトの　りーグも<LINE>せいは　したそうだな！<PARA>おれも　あれから<LINE>きたえなおしたんだ<PARA>もういちど<LINE>しょうぶ　しないか？',
     'まいった！<LINE>やっぱり　つよいな！', 'また　いつでも<LINE>かかってこい！'),
    ('カスミ', 0x77, 0x5E30, 0x12, False,
     'ジョウトでも　チャンピオンに<LINE>なったんですって？<PARA>わたしも　つよく　なったわよ！<LINE>もういちど　しょうぶ　しない？',
     'もう！<LINE>また　まけちゃった！', 'つぎは　ぜったい<LINE>まけないんだから！'),
    ('マチス', 0x79, 0x5FA5, 0x13, False,
     'ヘイ！　ジョウトでも<LINE>チャンピオン　だって？<PARA>ミーの　でんきも<LINE>パワーアップ　したぜ！<PARA>もういちど<LINE>バトル　するかい？',
     'オー！　ユーは<LINE>ほんとに　つよいね！', 'また　いつでも<LINE>バトル　しようぜ！'),
    ('エリカ', 0x77, 0x76D5, 0x15, False,
     'ジョウトでも　ごかつやく<LINE>だそうですね<PARA>わたくしの　<POKEMON>も<LINE>たくましく　なりましたの<PARA>'
     'もういちど　しょうぶ<LINE>いたしませんか？',
     'まあ<……><LINE>やっぱり　おつよいですわ', 'また　いつでも<LINE>いらしてくださいね'),
    ('アンズ', 0x77, 0x58B5, 0x1A, True,
     'ジョウトの　りーグも<LINE>せいは　したって？<PARA>あたいも　まけてらんない！<LINE>もういちど　しょうぶ　してよ！',
     'くやしいー！<LINE>まだまだ　しゅぎょうが　たりない！', 'つぎは　まけないからね！'),
    ('ナツメ', 0x77, 0x6CA1, 0x23, False,
     'あなたが　また　くることは<LINE>わかっていたわ<PARA>もういちど<LINE>しょうぶ　しましょう',
     '<……>　やはり<LINE>あなたは　つよいわ', 'また　あいましょう'),
    ('カツラ', 0x64, 0x4A19, 0x2E, False,
     'ウォーッ！<LINE>ジョウトでも　チャンピオンか！<PARA>わしの　ほのおも<LINE>まだまだ　もえて　おるぞ！<PARA>'
     'もういちど<LINE>しょうぶ　するか？',
     'もえつきたわい！', 'また　いつでも<LINE>くるが　ええ！'),
    ('グリーン', 0x77, 0x6980, 0x40, False,
     'よう！<LINE>ジョウトの　りーグも<CONT>せいは　したらしいな！<PARA>もういちど<LINE>しょうぶ　しようぜ！',
     'くそっ！<LINE>また　まけたか！', 'つぎは　まけないぜ！'),
]


def T(s): return encode('{00}' + s) + b'\x57'


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    f, n = bank_free_tail(rom, PB); sp.set_area(PB, f + 1, PB * 0x4000 + 0x4000)
    log = []
    _, G0, _ = P10.parse_groups(orig)
    grp = P13.read_groups7e(rom)
    a = Asm(sp.here(PB)); a.bank = PB; texts = {}
    sites = []
    for k, (name, b, site, cls, opens, ask, lose, after) in enumerate(LEADERS):
        o = fo(b, site); op = rom[o]
        assert op in (0x34, 0x31) and rom[o + 3] == 0x09, (name, rom[o:o + 6].hex())
        post = r16(o + 4); cont = site + 6
        if cls == 0x40:
            idx = 1                                                      # (Crystal's Blue is already his party 1)
        else:
            grp[cls - 1].append(list(G0[cls - 1][0])); idx = len(grp[cls - 1])
        L = 'L%d' % k
        a.label(L); a.db(op, rom[o + 1], rom[o + 2]); a.iftrue(L + 'b'); a.farsjump(b, cont)
        a.label(L + 'b'); a.checkevent(EV_BEAT_E4); a.iffalse(L + 'p')
        if opens: a.faceplayer(); a.opentext()
        a.writetext(L + 'q'); a.yesorno(); a.iffalse(L + 'p'); a.closetext()
        a.winlosstext(L + 'l', 0); a.loadtrainer(cls, idx); a.startbattle(); a.reloadmapafterbattle()
        a.opentext(); a.writetext(L + 'a'); a.waitbutton(); a.closetext(); a.end()
        a.label(L + 'p'); a.farsjump(b, post)
        texts[L + 'q'] = T(ask); texts[L + 'l'] = T(lose); texts[L + 'a'] = T(after)
        sites.append((b, site, L))
    for k_, v in texts.items(): a.label(k_); a.raw(v)
    base = a.base; blob = a.done(); assert sp.put(PB, blob) == base
    for b, site, L in sites:
        o = fo(b, site); t = a.labels[L]
        rom[o:o + 6] = bytes([0x04, PB, t & 0xFF, t >> 8, 0x90, 0x90])
    log.append('Kanto gym leaders\' rematches: %X:%04X (%d bytes)' % (PB, base, len(blob)))
    log.append('trainer parties (bank 7E free %d)' % P13.write_groups7e(rom, grp))

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    print('\n'.join(log))


if __name__ == '__main__':
    main()
