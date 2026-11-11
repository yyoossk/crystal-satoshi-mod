#!/usr/bin/env python3
"""Phase 47: from the Kanto Hall of Fame to Johto.
 * After the credits the game goes on in Pallet Town (Crystal: New Bark Town) until the player has reached Johto.
 * Prof. Oak's ticket (the base mod's event): the player still holds the S.S. Anne's ticket, so Oak takes it and gives
   the ship ticket (it used to fail, and Oak repeated himself).  Oak: "...ワカバタウンへ いくのじゃ！".
 * The first voyage of the fast ship from Vermilion goes to New Bark Town (Crystal: Olivine City): the ship's
   announcement and arrival lines say New Bark Town, and the player lands on the shore of New Bark Town.
   Later voyages are Crystal's (Olivine City).
 * New Bark Town's "player's house" is someone else's (an old lady's): no Mom, no Pokégear scene; the neighbour, the
   kitchen and the sign speak of the old lady.
usage: build_phase47.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
from evedit import MapEvents
import build_phase12 as P12
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
SPRITE_GRANNY = 0x30


def T(s): return encode('{00}' + s) + b'\x57'


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (PB, 0x01, 0x1A, 0x78, 0x27):
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
    # ================= New Bark Town: the old lady's house
    hm = MapEvents(rom, 'PlayersHouse1F')
    hm.coords = []                                                             # no "meet Mom" scene
    for i_, (ob, ref) in enumerate(hm.objs):
        if ob[0] == 0x0C: ob[0] = SPRITE_GRANNY; hm.objs[i_][1] = 'granny'
        elif ob[0] == 0x2E: hm.objs[i_][1] = 'neighbour'
    texts = {'g_t': T('あら　いらっしゃい！<LINE>カントーから　きたのかい？<PARA>ウツギはかせの　けんきゅうじょなら<LINE>'
                      'この　まちの　ひだりうえ　だよ'),
             'n_t': T('となりの　いえの　ものよ<PARA>ここの　おばあちゃんと<LINE>おしゃべり　しに　きているの'),
             'stove': T('おばあさんの　とくい　りょうり<LINE>グレンふう　かざんハンバーグ！'),
             'sink': T('ぴかぴかの　ながしだい！<LINE>おばあさんは　きれいずき'),
             'sign': T('ここは　おばあさん　のいえ')}
    a.label('granny'); a.jumptextfaceplayer('g_t')
    a.label('neighbour'); a.jumptextfaceplayer('n_t')
    a.label('stove_s'); a.jumptext('stove')
    a.label('sink_s'); a.jumptext('sink')
    a.label('sign_s'); a.jumptext('sign')
    hm.bgs = [(y, x, t_, 'stove_s' if k == 0 else 'sink_s' if k == 1 else r_) for k, (y, x, t_, r_) in enumerate(hm.bgs)]
    for k_, v in texts.items(): a.label(k_); a.raw(v)
    hm.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(PB, blob) == base
    hm.install(a)
    log.append('handlers / texts / the old lady\'s house: %X:%04X (%d bytes)' % (PB, base, len(blob)))
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
