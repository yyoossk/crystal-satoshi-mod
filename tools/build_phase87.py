#!/usr/bin/env python3
"""Phase 87: the Kanto gym leaders' rematch lines three years later.
 After the Johto Hall of Fame each Kanto gym leader offers a rematch with Crystal's team (phase 50).  Their lines now
 fit the story (three years after the Kanto League): the leaders Satoshi beat (Brock, Misty, Lt. Surge, Erika,
 Sabrina, Blaine, Shigeru at Viridian) greet him after three years; Janine, Koga's daughter who now leads the Fuchsia
 Gym, has never met him and introduces herself.
 * Blaine: after the Kanto Hall of Fame he is in Crystal's Seafoam Gym, which had no rematch (phase 50 hooked Red's
   Cinnabar Gym): the same rematch there.
usage: build_phase87.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import Space
import build_phase50 as P50

PB = P50.PB
SEAFOAM_SITE, SEAFOAM_POST = (0x27, 0x7D4C), (0x27, 0x7D7A)   # Blaine: checkflag VOLCANOBADGE ; iftrue post
NEW = {
    'タケシ': ('おお　<PLAYER>！<LINE>ひさしぶりだな！<PARA>3ねんぶりか<……><LINE>ジョウトの　りーグも<CONT>せいは　したそうだな！<PARA>'
             'おれも　あれから<LINE>きたえなおしたんだ<PARA>もういちど<LINE>しょうぶ　しないか？', None, None),
    'カスミ': ('<PLAYER>！<LINE>3ねんぶりね！<PARA>ジョウトでも　チャンピオンに<LINE>なったんですって？<PARA>'
             'わたしも　つよく　なったわよ！<LINE>もういちど　しょうぶ　しない？', None, None),
    'マチス': ('ヘイ！　<PLAYER>！<LINE>ひさしぶり　だな！<PARA>ジョウトでも<LINE>チャンピオン　だって？<PARA>'
             'ミーの　でんきも<LINE>パワーアップ　したぜ！<PARA>もういちど<LINE>バトル　するかい？', None, None),
    'エリカ': ('まあ　<PLAYER>さん<LINE>おひさしぶりですわ<PARA>ジョウトでも　ごかつやく<LINE>だそうですね<PARA>'
             'わたくしの　<POKEMON>も<LINE>たくましく　なりましたの<PARA>もういちど　しょうぶ<LINE>いたしませんか？', None, None),
    'アンズ': ('あたいは　アンズ！<LINE>セキチクジムの　りーダーよ！<PARA>ちちうえの　キョウは<LINE>いま　してんのう　なの<PARA>'
             'あたいの　しのびの　わざ<LINE>うけて　みる？', None, 'あんた　つよいね！<LINE>つぎは　まけないからね！'),
    'ナツメ': ('<PLAYER><……><LINE>3ねんぶり　ね<PARA>あなたが　また　くることは<LINE>わかっていたわ<PARA>'
             'もういちど<LINE>しょうぶ　しましょう', None, None),
    'カツラ': ('ウォーッ！　<PLAYER>か！<LINE>3ねんぶり　じゃのう！<PARA>しまの　かざんが　ふんかして<LINE>'
             'ジムは　ここに　うつったんじゃ<PARA>ジョウトでも　チャンピオンか！<LINE>わしの　ほのおも<CONT>'
             'まだまだ　もえて　おるぞ！<PARA>もういちど<LINE>しょうぶ　するか？', None, None),
    'グリーン': ('よう　<PLAYER>！<LINE>3ねんぶり　だな！<PARA>ジョウトの　りーグも<LINE>せいは　したらしいな！<PARA>'
              'あのときの　かりを<LINE>かえさせて　もらうぜ！<PARA>もういちど<LINE>しょうぶ　しようぜ！', None, None),
}


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    f, n = bank_free_tail(rom, PB); sp.set_area(PB, f + 1, PB * 0x4000 + 0x4000)
    B0 = PB * 0x4000; log = []
    for name, b, site, cls, opens, ask, lose, after in P50.LEADERS:
        for old_s, new_s, kind in ((ask, NEW[name][0], 'ask'), (after, NEW[name][2], 'after')):
            if new_s is None: continue
            old = P50.T(old_s); new = P50.T(new_s)
            seg = bytes(rom[B0:B0 + 0x4000]); i = seg.find(old); assert i >= 0 and seg.count(old) == 1, (name, kind)
            a = 0x4000 + i
            if len(new) <= len(old):
                rom[B0 + i:B0 + i + len(new)] = new; log.append('%s %s in place' % (name, kind)); continue
            na = sp.put(PB, new); k = 0
            for j in range(0x4000 - 2):
                if seg[j] == 0x4C and seg[j + 1] == a & 0xFF and seg[j + 2] == a >> 8:
                    rom[B0 + j + 1] = na & 0xFF; rom[B0 + j + 2] = na >> 8; k += 1
            assert k == 1, (name, kind, k)
            log.append('%s %s -> %02X:%04X' % (name, kind, PB, na))
    # Blaine after the Kanto Hall of Fame stands in Crystal's Seafoam Gym (phase 50 hooked Red's Cinnabar Gym only):
    # the same rematch there (phase 50's party and lines for him)
    o = fo(*SEAFOAM_SITE); assert rom[o:o + 6] == bytes([0x34, 0x29, 0x00, 0x09, SEAFOAM_POST[1] & 0xFF, SEAFOAM_POST[1] >> 8])
    seg = bytes(rom[B0:B0 + 0x4000]); i = seg.find(bytes([0x5D, 0x2E])); assert i > 0 and seg[i + 3:i + 5] == bytes([0x5E, 0x5F])
    idx = seg[i + 2]
    wl = seg[i - 4:i]; assert seg[i - 5] == 0x63                       # winlosstext win, 0
    j = seg.rfind(bytes([0x4C]), 0, i - 5); ask = seg[j + 1:j + 3]; assert seg[j + 3] == 0x4E   # writetext ask ; yesorno
    aft = seg[i + 7:i + 9]; assert seg[i + 6] == 0x4C
    a = Asm(sp.here(PB)); a.bank = PB
    a.label('sf'); a.db(0x34, 0x29, 0x00); a.iftrue('sfb'); a.farsjump(SEAFOAM_SITE[0], SEAFOAM_SITE[1] + 6)
    a.label('sfb'); a.checkevent(P50.EV_BEAT_E4); a.iffalse('sfp')
    a.db(0x4C); a.raw(ask); a.yesorno(); a.iffalse('sfp'); a.closetext()
    a.db(0x63); a.raw(wl); a.loadtrainer(0x2E, idx); a.startbattle(); a.reloadmapafterbattle()
    a.opentext(); a.db(0x4C); a.raw(aft); a.waitbutton(); a.closetext(); a.end()
    a.label('sfp'); a.farsjump(*SEAFOAM_POST)
    base = a.base; assert sp.put(PB, a.done()) == base
    rom[o:o + 6] = bytes([0x04, PB, base & 0xFF, base >> 8, 0x90, 0x90])
    log.append('Seafoam Gym: Blaine\'s rematch %02X:%04X' % (PB, base))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
