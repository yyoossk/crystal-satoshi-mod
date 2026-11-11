#!/usr/bin/env python3
"""Phase 48: Johto after Kanto.
 * Mr. Pokémon's house: Prof. Oak knows the player (he already has the Pokédex): new lines; "the Pokédex now records
   Johto's Pokémon too" instead of "got the Pokédex".
 * The Pokémon League: Kanto's Elite Four / champion (Red's, the base mod) until the player has Johto's eighth badge
   (the Rising Badge), also after the Kanto Hall of Fame (a rematch, as in Red); with it, Crystal's Elite Four and Lance.
   (Before, Crystal's were there right after the Kanto Hall of Fame, without any Johto badge.)
 * Jessie and James (ムサシとコジロウ, the Pikachu version's) in Johto's Team Rocket scenes: in the Slowpoke Well, the
   Mahogany hideout and the Radio Tower, with Johto teams (Wobbuffet at the Radio Tower); they leave when beaten or
   when the Rockets are gone.
usage: build_phase48.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
from evedit import MapEvents
import portmaps as PM
import build_phase13 as P13
import build_phase17 as P17
import build_phase28 as P28

FIRST_FLAG = 498                   # 482-497: phase 46
PB = 0x5B
EB = 0x65                          # relocated map events (Johto maps with trainers)
EV_HOF, EV_KANTO_MODE = 0x34A, 0x349
ENGINE_RISINGBADGE = 0x22
ROOMS = ['WillsRoom', 'KogasRoom', 'BrunosRoom', 'KarensRoom', 'LancesRoom']
OAK_SITES = {0x79E8: 'o1', 0x79ED: 'o2', 0x79F7: 'o3'}      # bank 1E: writetext in Mr. Pokémon's house (Oak)
JJ, SPR_JAMES, SPR_JESSIE = 72, 0x35, 0x36
EKANS, ARBOK, MEOWTH, KOFFING, WEEZING, WOBBUFFET = 0x17, 0x18, 0x34, 0x6D, 0x6E, 0xCA
# map, Rockets' flag (set when they are gone), Jessie (x, y, facing), James, party
JJ_SCENES = [('SlowpokeWellB1F', 0x6FC, (15, 12, 'RIGHT'), (14, 12, 'RIGHT'), [(14, EKANS), (14, KOFFING), (15, MEOWTH)]),
             ('TeamRocketBaseB1F', 0x6DA, (26, 2, 'RIGHT'), (26, 3, 'RIGHT'), [(26, ARBOK), (26, WEEZING), (27, MEOWTH)]),
             ('RadioTower2F', 0x6CE, (13, 1, 'RIGHT'), (13, 2, 'RIGHT'), [(30, ARBOK), (30, WEEZING), (31, WOBBUFFET)])]
FACE = {'DOWN': 6, 'UP': 7, 'LEFT': 8, 'RIGHT': 9}


def T(s): return encode('{00}' + s) + b'\x57'


JJ_TEXTS = [
    ('ムサシ{72}ちょっと　まったー！<PARA>コジロウ{72}ジョウトの　ヤドンの　シッポは<LINE>ロケットだんが　いただくぜ！<PARA>'
     'ムサシ{72}じゃまする　やつは<LINE>ここで　やっつけて　やるわ！',
     'ムサシ{72}ジョウトまで　きたのに<LINE>また　まけるなんて<……><PARA>コジロウ{72}おぼえてろよー！'),
    ('ムサシ{72}また　あんたね！<PARA>コジロウ{72}この　ひみつの　アジトは<LINE>ぜったいに　とおさないぜ！',
     'ムサシ{72}くやしいー！<PARA>コジロウ{72}なんで　いつも<LINE>こうなるんだ<……>'),
    ('ムサシ{72}ラジオとうは<LINE>ロケットだんが　いただいたわ！<PARA>コジロウ{72}サカキさまへの<LINE>だいじな　ほうそうの<CONT>'
     'じゃまは　させないぜ！<PARA>ムサシ{72}いけっ　ソーナンス！',
     'ムサシ{72}やっぱり　だめだったわ<……><PARA>コジロウ{72}こうなったら<LINE>にげるが　かちだ！'),
]
JJ_LOSE = 'ムサシ・コジロウ{72}<LINE>やなかんじー！'


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (PB, 0x1E, EB):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)

    # ================= Mr. Pokémon's house: Oak's lines
    a = Asm(sp.here(PB)); a.bank = PB
    texts = {
        'o1': T('オーキド{72}おお　<PLAYER>！<LINE>ちゃんと　ジョウトに　ついたな！<PARA>わしも　ふるい　ともだちの<LINE>'
                '<POKEMON>じいさんを　たずねて<CONT>きておったのじゃ<PARA>ほほうっ！<LINE>めずらしい　<POKEMON>を　もってるな！<PARA>'
                'ウツギくんの　おつかいか！<PARA>そうじゃ！<LINE><PLAYER>の　ずかんに<CONT>ジョウトの　<POKEMON>も<CONT>'
                'きろく　できるように　してやろう！'),
        'o2': T('<PLAYER>の　ずかんが<LINE>ジョウトの　ずかんに　なった！'),
        'o3': T('ジョウトには　カントーでは<LINE>みられない　<POKEMON>が<CONT>たくさん　いるのじゃ！<PARA>'
                'ずかんを　どんどん<LINE>うめていって　くれ！<PARA>おっと！<LINE>ながいを　した　ようじゃ！<PARA>'
                'これから　コガネシティへ　いって<LINE>いつもの　ラジオばんぐみの<CONT>しゅうろくを　せねば　ならんのだ！<PARA>'
                'それじゃ　<PLAYER>！<LINE>よろしく　たのんだぞ！')}
    for k_, v in texts.items(): a.label(k_); a.raw(v)
    # ================= the League: Kanto's (until the Rising Badge) / Crystal's
    K = FL.new()
    a.label('lcb'); a.checkevent(EV_HOF); a.iffalse('lcb_k'); a.checkflag(ENGINE_RISINGBADGE); a.iftrue('lcb_j')
    a.label('lcb_k'); a.setevent(EV_KANTO_MODE); a.clearevent(K); a.endcallback()
    a.label('lcb_j'); a.clearevent(EV_KANTO_MODE); a.setevent(K); a.endcallback()
    # ================= Jessie and James
    jl = []
    for i, (n, rf, jes, jam, party) in enumerate(JJ_SCENES):
        f = FL.new(); jl.append(f)
        intro, after = JJ_TEXTS[i]
        texts2 = {'ji%d' % i: T(intro), 'ja%d' % i: T(after), 'jw%d' % i: T(JJ_LOSE)}
        a.label('jj%d' % i); a.faceplayer(); a.opentext(); a.writetext('ji%d' % i); a.waitbutton(); a.closetext()
        a.winlosstext('jw%d' % i, 0); a.loadtrainer(JJ, 5 + i); a.startbattle(); a.reloadmapafterbattle()
        a.opentext(); a.writetext('ja%d' % i); a.waitbutton(); a.closetext()
        a.db(0x6D, 0xFE); a.db(0x6D, 0xFD); a.setevent(f); a.end()          # disappear (patched ids below)
        a.label('jcb%d' % i); a.checkevent(rf); a.iffalse('jcbe%d' % i); a.setevent(f)
        a.label('jcbe%d' % i); a.endcallback()
        for k_, v in texts2.items(): a.label(k_); a.raw(v)
    base = a.base; blob = bytearray(a.done()); assert sp.put(PB, bytes(blob)) == base
    L = dict(a.labels)
    log.append('texts / scripts %X:%04X (%d bytes)' % (PB, base, len(blob)))

    # Oak's writetexts -> stubs in bank 1E (farwritetext)
    for site, k_ in OAK_SITES.items():
        o = fo(0x1E, site); assert rom[o] == 0x4C, hex(site)
        st = sp.put(0x1E, bytes([0x4B, PB, L[k_] & 0xFF, L[k_] >> 8, 0x90]))
        rom[o:o + 3] = bytes([0x00, st & 0xFF, st >> 8])

    # League rooms: Kanto's people hidden by K instead of the Kanto Hall of Fame flag; the objects callback
    for n in ROOMS:
        me = MapEvents(rom, n); k_ = 0
        for ob, ref in me.objs:
            if (ob[11] | ob[12] << 8) == EV_HOF: ob[11] = K & 0xFF; ob[12] = K >> 8; k_ += 1
        assert k_ == 1, n
        assert not [t for t, r in me.callbacks if t == 2], n
        me.callbacks.append((2, ('far', PB, L['lcb'])))
        b = Asm(sp.here(PB)); b.bank = PB; me.write(b, sp); bb = b.base; bl = b.done(); assert sp.put(PB, bl) == bb; me.install(b)
    log.append('League rooms: Kanto\'s Elite Four until the Rising Badge')

    # Jessie and James: objects + callback in the three maps
    for i, (n, rf, jes, jam, party) in enumerate(JJ_SCENES):
        me = MapEvents(rom, n)
        lab = ('far', PB, L['jj%d' % i])
        ij = me.add_object(SPR_JESSIE, jes[0], jes[1], FACE[jes[2]], lab, flag=jl[i], pal_type=0x80) + 1
        im = me.add_object(SPR_JAMES, jam[0], jam[1], FACE[jam[2]], lab, flag=jl[i]) + 1
        p = fo(PB, L['jj%d' % i]); q = bytes(rom[p:p + 64]).index(bytes([0x6D, 0xFE, 0x6D, 0xFD]))
        rom[p + q + 1] = ij; rom[p + q + 3] = im
        b = Asm(sp.here(EB)); b.bank = EB
        old_cb = [r_ for t_, r_ in me.callbacks if t_ == 2]
        if old_cb:                                          # Crystal runs one callback of a type: chain them
            b.label('wcb'); b.checkevent(rf); b.iffalse('wcb2'); b.setevent(jl[i])
            b.label('wcb2'); b.farsjump(old_cb[0][1], old_cb[0][2])
            me.callbacks = [(t_, r_) for t_, r_ in me.callbacks if t_ != 2] + [(2, 'wcb')]
        else:
            me.callbacks.append((2, ('far', PB, L['jcb%d' % i])))
        me.write(b, sp); bb = b.base; bl = b.done(); assert sp.put(EB, bl) == bb; me.install(b)
    grp = P13.read_groups7e(rom)
    assert len(grp[JJ - 1]) == 4
    for i, (n, rf, jes, jam, party) in enumerate(JJ_SCENES):
        grp[JJ - 1].append([encode('ムサシとコジロウ@'), b'\x00' + b''.join(bytes([lv, s]) for lv, s in party) + b'\xff'])
    log.append('Jessie & James: 3 scenes (bank 7E free %d)' % P13.write_groups7e(rom, grp))

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    assert FL.i < 8 * (P28.SCENE_AREAS - 0xDA01)
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
