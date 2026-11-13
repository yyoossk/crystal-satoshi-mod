#!/usr/bin/env python3
"""Phase 70: the start of the journey as in Red (with this MOD's Pokégear):
 * Music: a script's playmusic now also clears wMapMusic, so the next playmapmusic (or the next map) brings the map's
   music back.  Before, playmapmusic compared the map's music with wMapMusic (unchanged by playmusic) and did nothing:
   the rival's theme went on in Oak's lab after the parcel (and after Shigeru left), on Route 22, ...
   Hook: Script_playmusic ($25:$718D, xor a / ld [wMusicFade],a) -> call PlaymusicHook (bank $25 free tail).
 * Red's house 1F: coming downstairs the first time, the player walks to Mom (she sits by the table watching TV) and
   she turns to him before she talks and gives the Pokégear (before, she gave it from across the room).
 * Shigeru's house (Red): his sister sits at the table with the town map on it.  Before the Pokédex: "Shigeru is at
   Grandpa's lab"; after it she puts the town map into the Pokégear (ENGINE_MAP_CARD; the map on the table goes);
   afterwards "use the Pokégear's town map".  Next time the player comes in, she walks around the room (Red: "Pokémon
   are living things...").  After the Kanto Hall of Fame: Crystal's Daisy as before.
 * Pallet Town: coming in from Route 1 the name sign closed at once.  Any player event (here Oak's "Wait!" coord
   events on the north entry, which end at once after the starter) clears the sign's timer (PlayerEvents).  Those two
   coord events now belong to scene 0 of a scene byte that is 0 only before the starter: the event flags' byte of
   EV_GOT_STARTER (flags $340-$347: $342-$347 are the starter's, set together).
 * The map name sign in Kanto: the Gen I overworld tileset's palettes (from the Pikachu full-color hack) had red / blue
   in palette 7 (the text and sign palette; its tiles use it only for $60-$7f), so the sign was red with a blue frame.
   Palette 7 is now the one Crystal shows the sign with (white, light blue, dark blue, black).
usage: build_phase70.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import portmaps as PM
import redmap as RM
from evedit import MapEvents
import build_phase12 as P12
import build_phase17 as P17

FIRST_FLAG = 518                   # 514-517: phase 58
BANK = 0x62
ENGINE_MAP_CARD, ENGINE_POKEDEX = 0x01, 0x0B
SPR_DAISY, SPR_POKEDEX = 0x0F, 0x55
WALK_UP_DOWN = 0x04
SFX_KEY_ITEM = 0x0091
RED_BLUES_HOUSE = 0x27
D, U, L, R = 0x0C, 0x0D, 0x0E, 0x0F
TR = 0x03
SCRIPT_PLAYMUSIC = 0x7187          # bank $25
W_EVENT_FLAGS = 0xDA65
W_MAP_MUSIC, W_MUSIC_FADE = 0xC2C0, 0xC2A7


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    f, n = bank_free_tail(rom, BANK); sp.set_area(BANK, f + 1, BANK * 0x4000 + 0x4000)
    FL = PM.Flags(FIRST_FLAG)
    log = []

    # ================= playmusic clears wMapMusic
    o = fo(0x25, SCRIPT_PLAYMUSIC)
    assert rom[o:o + 13] == bytes([0x11, 0, 0, 0xCD, 0x24, 0x3B, 0xAF, 0xEA, W_MUSIC_FADE & 0xFF, W_MUSIC_FADE >> 8,
                                   0xCD, 0x24, 0x3C]) or rom[o + 6:o + 10] == bytes([0xAF, 0xEA, 0xA7, 0xC2]), rom[o:o + 13].hex()
    hf, hn = bank_free_tail(rom, 0x25); assert hn >= 10
    hook = 0x4000 + (hf + 1) % 0x4000
    hb = bytes([0xAF, 0xEA, W_MUSIC_FADE & 0xFF, W_MUSIC_FADE >> 8, 0xEA, W_MAP_MUSIC & 0xFF, W_MAP_MUSIC >> 8, 0xC9])
    rom[fo(0x25, hook):fo(0x25, hook) + len(hb)] = hb
    rom[o + 6:o + 10] = bytes([0xCD, hook & 0xFF, hook >> 8, 0x00])
    log.append('Script_playmusic hook 25:%04X' % hook)

    # ================= Red's house 1F: walk to Mom first
    me = MapEvents(rom, 'RedsHouse1F')
    assert me.scenes[0] == 0x7FB6 and me.sb == 0x1F
    so = fo(0x1F, 0x7FB6); assert rom[so:so + 4] == bytes([0x8C, 0xA8, 0x7F, 0x90])          # sdefer MeetMom / end
    assert me.objs[0][0][0] == 0x0E and (me.objs[0][0][2] - 4, me.objs[0][0][1] - 4) == (5, 3)
    a = Asm(sp.here(BANK)); a.bank = BANK
    a.label('mom_sc'); a.sdefer('mom_go'); a.end()
    a.label('mom_go'); a.applymovement(0, 'mom_mv'); a.turnobject(2, TR); a.farsjump(0x1F, 0x7FA8)
    a.label('mom_mv'); a.db(D, D, D, L, 0x47)          # stairs (7, 0) -> (6, 3), beside Mom at (5, 3)
    me.scenes[0] = 'mom_sc'
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    me.install(a)
    log.append('RedsHouse1F: events %X:%04X (%d bytes)' % (BANK, base, len(blob)))

    # ================= Shigeru's house: Red's Daisy and the town map (into the Pokégear)
    me = MapEvents(rom, 'BluesHouse')
    assert len(me.objs) == 1 and me.objs[0][0][0] == SPR_DAISY and (me.objs[0][0][2] - 4, me.objs[0][0][1] - 4) == (2, 3)
    old_daisy = me.objs[0][1]; assert old_daisy[0] == 'far'
    sit_hide, walk_hide, map_gone = FL.new(), FL.new(), FL.new()
    me.objs[0][0][3] = P12.FACE['RIGHT']; me.objs[0][0][11] = sit_hide & 0xFF; me.objs[0][0][12] = sit_hide >> 8
    me.objs[0][1] = 'dz_sit'
    me.add_object(SPR_DAISY, 6, 4, WALK_UP_DOWN, 'dz_walk', flag=walk_hide, rng=0x10)
    mapobj = me.add_object(SPR_POKEDEX, 3, 3, P12.FACE['NONE'], 'dz_map', flag=map_gone) + 1
    texts = {
        'rival': '{00}こんにちは　<PLAYER>くん！<LINE>おとうとの　{39}なら<CONT>おじいちゃんの　けんきゅうじょよ<DONE>',
        'offer': '{00}オーキドの　おじいちゃん<LINE>おしごと　たのんだんだって？<CONT>たいへんねー<PARA>'
                 'ポケギア　かして！<LINE>タウンマップが　みられるように<CONT>して　あげる！<DONE>',
        'got': '{00}<PLAYER>の　ポケギアで<LINE>タウンマップが　みられる<CONT>ように　なった！<DONE>',
        'use': '{00}じぶんの　いる　ばしょや<LINE>まちの　なまえが　しりたいとき<CONT>ポケギアの　タウンマップ<CONT>みると　いいわよ<DONE>',
        'walk': '{00}にんげんと　おなじように<LINE><POKEMON>も　いきてるの！<CONT>たいりょくが　ないときは<CONT>やすませて　あげて！<DONE>',
        'map': '{00}カントー　ちほうの　ちずだ！<LINE><……>　もらえたら　うれしい？<DONE>',
    }
    for k_ in ('walk', 'map'):          # Red's own lines (JP Red)
        b_, p_ = RM.text_ptr(RED_BLUES_HOUSE, {'walk': 2, 'map': 3}[k_])
        assert RM.crystal_text(b_, p_) == encode(texts[k_]), k_
    a = Asm(sp.here(BANK)); a.bank = BANK
    a.label('dz_sit'); a.checkevent(P17.EV_HOF); a.iftrue('dz_old')
    a.faceplayer(); a.opentext(); a.checkflag(ENGINE_MAP_CARD); a.iftrue('dz_use')
    a.checkflag(ENGINE_POKEDEX); a.iftrue('dz_give')
    a.writetext('rival'); a.waitbutton(); a.closetext(); a.end()
    a.label('dz_give'); a.writetext('offer'); a.waitbutton()
    a.setflag(ENGINE_MAP_CARD); a.disappear(mapobj); a.setevent(map_gone)
    a.writetext('got'); a.playsound(SFX_KEY_ITEM); a.waitsfx(); a.waitbutton(); a.closetext(); a.end()
    a.label('dz_use'); a.writetext('use'); a.waitbutton(); a.closetext(); a.end()
    a.label('dz_old'); a.farsjump(old_daisy[1], old_daisy[2])
    a.label('dz_walk'); a.jumptextfaceplayer('walk')
    a.label('dz_map'); a.jumptext('map')
    # objects: walking after the map card (from the next visit; Red: after leaving the house), Crystal's after the HoF
    a.label('dz_cb'); a.checkevent(P17.EV_HOF); a.iftrue('dz_cbh')
    a.checkflag(ENGINE_MAP_CARD); a.iffalse('dz_cbs')
    a.setevent(sit_hide); a.clearevent(walk_hide); a.setevent(map_gone); a.endcallback()
    a.label('dz_cbh'); a.setevent(map_gone)
    a.label('dz_cbs'); a.clearevent(sit_hide); a.setevent(walk_hide); a.endcallback()
    me.callbacks.append((2, 'dz_cb'))
    for k_, v in texts.items():
        a.label(k_); a.raw(encode(v))
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    me.install(a)
    log.append('BluesHouse: events %X:%04X (%d bytes); flags %X-%X' % (BANK, base, len(blob), sit_hide, map_gone))

    # ================= Pallet Town: Oak's "Wait!" coord events only before the starter (scene byte)
    import build_phase21 as P21
    import build_phase28 as P28
    a_ = attrs(rom, hdr_index('PalletTown')); ev = parse_events(rom, a_['scbank'], a_['events'])
    stops = [(o_, c) for o_, c in ev['coords'] if c[1] == 1 and c[2] in (10, 11)]
    assert len(stops) == 2 and all(c[0] == 0xFF for o_, c in stops), stops
    for o_, c in stops: rom[o_] = 0
    sb = W_EVENT_FLAGS + (P17.EV_GOT_STARTER >> 3); assert P17.EV_GOT_STARTER >> 3 == 0x347 >> 3
    def r16(o): return rom[o] | rom[o + 1] << 8
    sr = P21.SCENES_REF
    tb = fo(rom[sr], r16(sr + 3)); n_ = 0
    while rom[tb + 4 * n_] != 0xFF: n_ += 1
    pal = mapid('PalletTown')
    assert all(bytes(rom[tb + 4 * i:tb + 4 * i + 2]) != bytes(pal) for i in range(n_))
    tab = bytes(rom[tb:tb + 4 * n_]) + bytes([*pal, sb & 0xFF, sb >> 8])
    assert rom[sr] == 0x61 and rom[sr - 1] == 0x3E and rom[sr + 2] == 0x21
    # bank $61 is full: the table moves to this phase's bank (GetMapSceneID: ld a, BANK / rst Bankswitch / ld hl, table)
    at = sp.put(BANK, tab + b'\xff'); rom[sr] = BANK; rom[sr + 3] = at & 0xFF; rom[sr + 4] = at >> 8
    rom[tb:tb + 4 * n_ + 1] = b'\xff' * (4 * n_ + 1)
    log.append('PalletTown: scene byte %04X (coord events at %s)' % (sb, [hex(o_) for o_, c in stops]))

    # ================= Kanto's sign: palette 7 as in Crystal
    old7, new7 = bytes.fromhex('ff7f1f21eb7e630c'), bytes.fromhex('ff7f6872a5400000')
    assert rom.count(new7) == 1                                                # Crystal's (bank $12)
    hits = []; i = rom.find(old7)
    while i >= 0:
        assert rom[i - 56:i - 48] == bytes.fromhex('fb6fb556ad35e71c'); hits.append(i); rom[i:i + 8] = new7; i = rom.find(old7)
    assert len(hits) == 2, hits
    log.append('palette 7 of the Gen I overworld tileset at %s' % [hex(h) for h in hits])

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
