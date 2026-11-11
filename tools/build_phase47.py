#!/usr/bin/env python3
"""Phase 47: from the Kanto Hall of Fame to Johto.
 * After the credits the game goes on in Pallet Town (Crystal: New Bark Town) until the player has reached Johto.
 * Prof. Oak's ticket (the base mod's event): the player still holds the S.S. Anne's ticket, so Oak takes it and gives
   the ship ticket (it used to fail, and Oak repeated himself).  Oak: "...ワカバタウンへ いくのじゃ！".
 * The first voyage of the fast ship from Vermilion goes to New Bark Town (Crystal: Olivine City): the ship's
   announcement and arrival lines say New Bark Town, and the player lands on the shore of New Bark Town.
   Later voyages are Crystal's (Olivine City).
 * New Bark Town's "player's house" is the house of Crystal's hero, Hibiki: his mother (new lines, she lets the
   player's Pokémon rest), no Pokégear scene, the neighbour, the sign "ここは ヒビキ のいえ".
 * Mt. Silver: Hibiki takes Red's place (Crystal's hero's sprite and picture, his own lines, a Johto team at Red's
   levels).
usage: build_phase47.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode, decode
from evedit import MapEvents
import build_phase12 as P12
import build_phase13 as P13
import build_phase17 as P17

PB = 0x5B                          # handlers / texts
EV_ARRIVED = 0x34C                 # the base mod: the player has reached Johto
S_S_TICKET = 0x44
SPAWN_NEW_BARK, SPAWN_PALLET = 0x0E, 0x02
W_EVENTFLAGS, W_DEFAULTSPAWN = 0xDA65, 0xD001
CONTINUE_SPAWN = (0x01, 0x5DC0)    # ld a, SPAWN_NEW_BARK ; ld [wDefaultSpawnpoint], a (after the credits)
OAK_GIVE = (0x78, 0x5D4A)          # the base mod's Oak: verbosegiveitem S_S_TICKET
OAK_TEXT = (0x78, 0x5DC9)          # ...アサギシティへ いくのじゃ！
SHIP_TEXTS = {0x4748: 0x4848, 0x4770: 0x496C, 0x4E6F: 0x502C}     # bank 1A: writetext sites -> Olivine texts
SHIP_ARRIVE = 0x477F               # bank 1A: setevent (gangway) ; setmapscene OLIVINE_PORT ; warp OLIVINE_PORT, 7, 23
NB_LANDING = (17, 7)
SPRITE_HIBIKI = 0x01               # Crystal's hero (SPRITE_CHRIS)
EV_BEAT_E4, EV_GOT_ELM_MON, EV_HIBIKI_GONE = 0x44, 0x1A, 0x762
MUSIC_HEAL, SP_HEALPARTY, SP_RESTARTMUSIC = 0x0D, 27, 0x3D
RED_CLASS = 0x3F
HIBIKI_PIC = (0x22, 0x48B2)        # the original's ChrisPic
PICBANK, PICSBANKS, PICS_FIX_BASE = 0x74, 0x5126A, 0x12
PIC_TABLE = 0x48CF                 # phase 10's trainer picture table (bank 7C)
PAL_REF, T_PAL = 0x971D, 0xB08B    # phase 10's trainer palettes (bank 2) / the original's


def T(s): return encode('{00}' + s) + b'\x57'


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (PB, 0x01, 0x1A, 0x78, 0x27, 0x74):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    log = []
    nb, h1 = mapid('NewBarkTown'), mapid('PlayersHouse1F')

    # ================= after the credits: Pallet Town until Johto is reached
    o = fo(*CONTINUE_SPAWN); assert rom[o:o + 5] == bytes([0x3E, SPAWN_NEW_BARK, 0xEA, W_DEFAULTSPAWN & 0xFF, W_DEFAULTSPAWN >> 8])
    fb = W_EVENTFLAGS + (EV_ARRIVED >> 3)
    hook = bytes([0xFA, fb & 0xFF, fb >> 8, 0xCB, 0x47 | ((EV_ARRIVED & 7) << 3), 0x3E, SPAWN_NEW_BARK, 0x20, 0x02,
                  0x3E, SPAWN_PALLET, 0xEA, W_DEFAULTSPAWN & 0xFF, W_DEFAULTSPAWN >> 8, 0xC9])
    hk = sp.put(0x01, hook)
    rom[o:o + 5] = bytes([0xCD, hk & 0xFF, hk >> 8, 0x00, 0x00])
    log.append('after the credits: spawn hook 01:%04X' % hk)

    # ================= Oak's ticket (the base mod): take the S.S. Anne's ticket first; New Bark Town
    o = fo(*OAK_GIVE); assert rom[o:o + 3] == bytes([0x9D, S_S_TICKET, 1])
    st = sp.put(0x78, bytes([0x20, S_S_TICKET, 1, 0x9D, S_S_TICKET, 1, 0x90]))       # takeitem ; verbosegiveitem ; end
    rom[o:o + 3] = bytes([0x00, st & 0xFF, st >> 8])
    o = fo(*OAK_TEXT); old, new = encode('アサギシティへ').rstrip(b'\x50'), encode('ワカバタウンへ').rstrip(b'\x50')
    i = rom.find(old, o, o + 40); assert i > 0 and len(old) == len(new); rom[i:i + len(new)] = new

    # ================= the fast ship's first voyage: New Bark Town
    a = Asm(sp.here(PB)); a.bank = PB
    nb_texts = {0x4848: T('こうそくせん　アクアごうは<LINE>ワカバタウンに　むかいます<PARA>ワカバタウンに　つきましたら<LINE>'
                          'ほうそうで　おしらせします'),
                0x496C: T('こうそくせん　アクアごうは<LINE>ワカバタウンに　とうちゃくしました！'),
                0x502C: T('こうそくせん　アクアごうは<LINE>ワカバタウンに　とうちゃくしました！')}
    s1a = {}
    for site, t in SHIP_TEXTS.items():
        o = fo(0x1A, site); assert rom[o:o + 3] == bytes([0x4C, t & 0xFF, t >> 8]), hex(site)
        a.label('h%X' % t); a.checkevent(EV_ARRIVED); a.iftrue('o%X' % t); a.writetext('t%X' % t); a.end()
        a.label('o%X' % t); a.farwritetext(0x1A, t); a.end()
    o = fo(0x1A, SHIP_ARRIVE); old_arrive = bytes(rom[o:o + 13])
    assert old_arrive[0] == 0x33 and old_arrive[3] == 0x12 and old_arrive[7:12] == bytes([0x3C, 0x0F, 0x01, 0x07, 0x17]), old_arrive.hex()
    a.label('arr'); a.checkevent(EV_ARRIVED); a.iftrue('arr_o')
    a.setevent(EV_ARRIVED); a.db(0x3B, *nb)                                    # blackoutmod NEW_BARK_TOWN
    a.warp(*nb, *NB_LANDING); a.end()
    a.label('arr_o'); a.raw(old_arrive)
    for t, v in nb_texts.items(): a.label('t%X' % t); a.raw(v)
    # ================= New Bark Town: Hibiki's house (Crystal's hero), his mother
    hm = MapEvents(rom, 'PlayersHouse1F')
    hm.coords = []                                                             # no "meet Mom" scene (Pokégear)
    for i_, (ob, ref) in enumerate(hm.objs):
        if ob[0] == 0x0C: hm.objs[i_][1] = 'mom'
        elif ob[0] == 0x2E: hm.objs[i_][1] = 'neighbour'
    texts = {'m1': T('あら？　あなたが　カントーから　きた<LINE>サトシくん　ね！<PARA>ヒビキの　ははです<PARA>'
                     'ウツギはかせから<LINE>はなしは　きいているわ<PARA>けんきゅうじょは　この　まちの<LINE>ひだりうえよ<PARA>'
                     'はかせが　まってるわ！<LINE>いってらっしゃい！'),
             'm2': T('あら　サトシくん！<LINE>おかえりなさい<PARA>うちの　ヒビキも　サトシくんと<LINE>おなじ　ころに　たびに　でたのよ<PARA>'
                     'いまごろ　どこで　なにを<LINE>しているのかしら<……><PARA>つかれたでしょう？<LINE>すこし　やすんでいって！'),
             'm3': T('あら　サトシくん！<PARA>ヒビキったら　シロガネやまに<LINE>こもって　しゅぎょう　してるらしいの<PARA>'
                     'もし　あったら　たまには<LINE>かえって　きなさいって<CONT>つたえてね！<PARA>つかれたでしょう？<LINE>すこし　やすんでいって！'),
             'm4': T('あら　サトシくん！<LINE>ヒビキに　あったの？<PARA>そう<……>　げんきに　してたのね<PARA>'
                     'あのこったら　サトシくんと<LINE>しょうぶ　できて<CONT>きっと　うれしかったと　おもうわ<PARA>'
                     'つかれたでしょう？<LINE>すこし　やすんでいって！'),
             'mh': T('<PLAYER>の　<POKEMON>は<LINE>みんな　げんきに　なった！'),
             'mb': T('いってらっしゃい！<LINE>むりは　しないでね！'),
             'n_t': T('こんにちは　サトシくん！<PARA>わたしは　となりの　いえの　もの<LINE>ヒビキくんの　おかあさんと<CONT>'
                      'おしゃべり　しに　きているの'),
             'sign': T('ここは　ヒビキ　のいえ')}
    a.label('mom'); a.faceplayer(); a.opentext()
    a.checkevent(EV_BEAT_E4); a.iftrue('mom_e4')
    a.checkevent(EV_GOT_ELM_MON); a.iftrue('mom_2')
    a.writetext('m1'); a.waitbutton(); a.closetext(); a.end()
    a.label('mom_e4'); a.checkevent(EV_HIBIKI_GONE); a.iftrue('mom_4'); a.writetext('m3'); a.sjump('mom_h')
    a.label('mom_4'); a.writetext('m4'); a.sjump('mom_h')
    a.label('mom_2'); a.writetext('m2')
    a.label('mom_h'); a.waitbutton(); a.closetext()
    a.playmusic(MUSIC_HEAL); a.special(SP_HEALPARTY); a.pause(60); a.special(SP_RESTARTMUSIC)
    a.opentext(); a.writetext('mh'); a.waitbutton(); a.writetext('mb'); a.waitbutton(); a.closetext(); a.end()
    a.label('neighbour'); a.jumptextfaceplayer('n_t')
    for k_, v in texts.items(): a.label(k_); a.raw(v)
    # ================= Mt. Silver: Hibiki in Red's place (Red's script, Hibiki's lines)
    sv = MapEvents(rom, 'SilverCaveRoom3')
    ob, ref = sv.objs[0]; assert ob[0] == 0x06
    p = fo(ref[1], ref[2]); rs = bytes(rom[p:p + 64])
    assert rs[:5] == bytes([0x0F, 0x6A, 0x00, 0x6A, 0x47]) and rs[5] == 0x4C and rs[10] == 0x63 and rs[15:18] == bytes([0x5D, RED_CLASS, 1])
    ob[0] = SPRITE_HIBIKI
    hb_texts = {'hs': T('<……>　！<LINE>サトシさん　ですよね？<PARA>ぼくは　ヒビキ<LINE>ワカバタウンから　きました<PARA>'
                        'いつか　あなたと<LINE>たたかって　みたかったんだ！<PARA>さあ　しょうぶ　です！'),
                'hw': T('<……>　まいったなあ！<LINE>やっぱり　つよいや！'),
                'hl': T('ありがとう　サトシさん！<PARA>もっと　もっと　つよく　なって<LINE>また　あいに　いきます！<PARA>'
                        'かあさんに　よろしく！')}
    e_ = rs.index(0x90) + 1; body = bytearray(rs[:e_])
    a.label('hibiki'); a.raw(body[:5]); a.db(0x4C); a.dw('hs'); a.raw(body[8:10]); a.db(0x63); a.dw('hw'); a.dw('hw')
    k2 = body.index(0x4C, 15); a.raw(body[15:k2]); a.db(0x4C); a.dw('hl'); a.raw(body[k2 + 3:])
    for k_, v in hb_texts.items(): a.label(k_); a.raw(v)
    hm.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(PB, blob) == base
    hm.install(a)
    sv.objs[0][1] = ('far', PB, a.labels['hibiki'])
    a2 = Asm(sp.here(PB)); a2.bank = PB
    sv.write(a2, sp)
    b2 = a2.base; blob2 = a2.done(); assert sp.put(PB, blob2) == b2
    sv.install(a2)
    # the trainer: name, party (Red's levels), picture (Crystal's hero), colours
    grp = P13.read_groups7e(rom)
    assert decode(grp[RED_CLASS - 1][0][0]) == 'レッド@'
    mv = lambda lv, sp_, *ms: bytes([lv, sp_, *ms])
    party = b'\x01' + mv(81, 0xB8, 0x39, 0x3A, 0x26, 0xCD) + mv(73, 0xC4, 0xBD, 0x73, 0x81, 0x5E) + mv(75, 0x8F, 0x85, 0xAD, 0x9C, 0x22) + \
        mv(77, 0x9A, 0x73, 0x22, 0xEB, 0x4C) + mv(77, 0x9D, 0x35, 0x59, 0x81, 0x62) + mv(77, 0xA0, 0x39, 0xF2, 0xA3, 0x08) + b'\xff'
    grp[RED_CLASS - 1][0] = [encode('ヒビキ@'), party]
    log.append('trainer parties (bank 7E free %d)' % P13.write_groups7e(rom, grp))
    pic = orig[fo(*HIBIKI_PIC):fo(*HIBIKI_PIC) + 784]
    assert rom[PICSBANKS + 25] == PICBANK
    pp = sp.put(PICBANK, lz(pic)); te = fo(0x7C, PIC_TABLE) + 3 * (RED_CLASS - 1)
    rom[te:te + 3] = bytes([PICS_FIX_BASE + 25, pp & 0xFF, pp >> 8])
    pb = fo(2, r16(PAL_REF + 1)) + 4 * RED_CLASS
    rom[pb:pb + 4] = orig[T_PAL:T_PAL + 4]
    log.append('Mt. Silver: Hibiki (picture %X:%04X)' % (PICBANK, pp))
    log.append('handlers / texts / Hibiki\'s house: %X:%04X (%d bytes)' % (PB, base, len(blob)))
    for site, t in SHIP_TEXTS.items():
        stub = sp.put(0x1A, bytes([0x04, PB, a.labels['h%X' % t] & 0xFF, a.labels['h%X' % t] >> 8]))
        o = fo(0x1A, site); rom[o:o + 3] = bytes([0x00, stub & 0xFF, stub >> 8])                    # scall stub
    o = fo(0x1A, SHIP_ARRIVE); rom[o:o + 13] = bytes([0x04, PB, a.labels['arr'] & 0xFF, a.labels['arr'] >> 8]) + bytes([0x90] * 9)
    # the house sign in New Bark Town
    ne = MapEvents(rom, 'NewBarkTown')
    na = attrs(rom, hdr_index('NewBarkTown')); ev = parse_events(rom, na['scbank'], na['events'])
    k = [i_ for i_, (y, x, t_, r_) in enumerate(ne.bgs) if (x, y) == (11, 5)][0]
    o_ = ev['bgs'][k][0]; sg = sp.put(PB, bytes([0x52]) + bytes([0, 0]))
    sgt = sp.put(PB, texts['sign']); rom[fo(PB, sg) + 1] = sgt & 0xFF; rom[fo(PB, sg) + 2] = sgt >> 8
    st2 = sp.put(na['scbank'], bytes([0x04, PB, sg & 0xFF, sg >> 8]))
    w16(o_ + 3, st2)

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    print('\n'.join(log))


if __name__ == '__main__':
    main()
