#!/usr/bin/env python3
"""Phase 58: Bulbasaur, Charmander and Squirtle given as in the Pikachu version / the Pikachu full-color hack, so all
151 can be had (the MOD's Oak gives one of the three, as in Red).
 * Cerulean City: Melanie's house (Pikachu version) where Red's trade house was (same room): Melanie gives Bulbasaur
   (Lv 10; the Pikachu version's condition, Pikachu's friendship, does not exist here), her Bulbasaur, Oddish and
   Sandshrew.  Red's trade there (Poliwhirl for Jynx) goes with the house, as in the Pikachu version.
 * Route 24: the trainer (Damian) above the bridge gives Charmander (Lv 10).
 * Vermilion City: Officer Jenny gives Squirtle (Lv 10) after the Thunder Badge.
 * Texts from the Pikachu full-color hack; Officer Jenny's and Sandshrew's walking pictures from it (new sprites).
usage: build_phase58.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import pkmap
import portmaps as PM
import build_phase10 as P10
import build_phase14 as P14
import build_phase57 as P57
from evedit import MapEvents

PB = 0x47
FIRST_FLAG = 514                   # 512-513: phase 57
BULBASAUR, CHARMANDER, SQUIRTLE, ODDISH_MON, SANDSHREW_MON = 1, 4, 7, 43, 27
SPR_GIRL, SPR_COOLTRAINER_M = 0x28, 0x23
SPR_BULBASAUR, SPR_ODDISH = 0x93, 0x85                 # Crystal's Pokémon sprites
SPRITE_JENNY, SPRITE_SANDSHREW = 0x77, 0x78            # new (after phase 56's Jessie / James)
PKFC_JENNY, PKFC_SANDSHREW = 0xFE691, 0xFE991          # PKFC OfficerJennySprite (24 tiles) / SandshrewSprite (12)
PAL_OW_BLUE, PAL_OW_BROWN = 1, 3
MOVE_POKEMON, STAND = 0x16, {'DOWN': 6, 'UP': 7, 'LEFT': 8, 'RIGHT': 9}
PAL_NPC_BLUE, PAL_NPC_GREEN = 0x90, 0xA0
THUNDER_BADGE = 0x25               # engine flag (phase 55: Vermilion Gym)
MELANIE_HOUSE = (26, 73)           # phase 25: Red's Cerulean trade house
Y_MELANIE, Y_ROUTE24, Y_VERMILION = 0x3F, 0x23, 0x05   # pokeyellow map ids (PKFC)


def pk_texts(bank, o, n=0x120):
    """texts loaded by `ld hl, text` in Gen I code at o"""
    out = []; F = pkmap.F
    for i in range(o, o + n):
        if F[i] == 0x21:
            p = F[i + 1] | F[i + 2] << 8
            if 0x4000 <= p < 0x8000:
                k, v = pkmap.text_body(bank, p)
                if k == 'text' and len(v) > 3 and bytes(v) not in out: out.append(bytes(v))
    return out


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (PB,):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 16, b * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    pk = open(P10.PKFC, 'rb').read()

    # ================= sprites (phase 56's way: the second sprite table, two more entries)
    stubs = []
    for off, d in P14.OW_READERS:
        assert rom[off] == 0xCD; s_ = fo(0x05, r16(off + 1))
        assert rom[s_:s_ + 2] == bytes([0xFE, 0x67]) and rom[s_ + 8] == 0x21
        stubs.append((s_, d))
    virt = r16(stubs[0][0] + 9) - stubs[0][1]
    n2 = len(P14.NEW_SPRITES) + 3 + 2                         # + phase 56's Jessie / James
    assert SPRITE_JENNY == 0x67 + n2
    t2 = virt + 0x66 * 6
    end = fo(0x05, t2) + 6 * n2; add = b''                  # the table ends where the bank's free tail starts
    for off, nt_, typ, pal in ((PKFC_JENNY, 24, 1, PAL_OW_BLUE), (PKFC_SANDSHREW, 12, 2, PAL_OW_BROWN)):
        ga = sp.put(PB, pk[off:off + nt_ * 16])
        add += bytes([ga & 0xFF, ga >> 8, 0xC0, PB, typ, pal])
    assert not any(rom[end:end + len(add) + 8]); rom[end:end + len(add)] = add

    # ================= texts (PKFC)
    F = pkmap.F
    b_, p_ = pkmap.text_ptr(Y_MELANIE, 1); mel = pk_texts(b_, fo(b_, p_))
    assert len(mel) == 5 and 'フシギダネ' in __import__('jpchar').decode(mel[0])
    mon_t = [bytes(pkmap.text_body(*pkmap.text_ptr(Y_MELANIE, t))[1]) for t in (2, 3, 4)]
    assert all(t.count(0x72) == 1 for t in mon_t)
    mon_t = [t.replace(b'\x72', b'\x70') + b'\x71' for t in mon_t]      # Gen I's ':' -> Crystal's 「 」
    b_, p_ = pkmap.text_ptr(Y_ROUTE24, 9); dam = pk_texts(b_, fo(b_, p_))
    assert len(dam) == 4 and 'ヒトカゲ' in __import__('jpchar').decode(dam[0])
    b_, p_ = pkmap.text_ptr(Y_VERMILION, 7); o_ = fo(b_, p_)
    i_ = F.index(bytes([0x06]), o_); jb = F[i_ + 1]; assert F[i_ + 2] == 0x21
    jen = pk_texts(jb, fo(jb, F[i_ + 3] | F[i_ + 4] << 8), 0x90)
    assert len(jen) == 5 and 'ゼニガメ' in __import__('jpchar').decode(jen[0])
    texts = {}
    def T(lab, body): texts[lab] = bytes(body) + b'\x57'; return lab

    a = Asm(sp.here(PB)); a.bank = PB
    def give(mon, got, fail, after):
        """givepoke mon Lv 10; wScriptVar = given (party or box)"""
        a.givepoke(mon, 10); a.callasm(PB, 'given'); a.iffalse(fail)
        after()
    a.label('given'); a.raw(bytes([0xFA, 0xDD, 0xC2, 0xFE, 0x02, 0x3E, 0x00, 0x28, 0x01, 0x3C, 0xEA, 0xDD, 0xC2, 0xC9]))
    a.label('quit'); a.closetext(); a.end()

    # ---- Melanie (Cerulean)
    got_b, bulba_gone = FL.new(), FL.new()
    a.label('mel'); a.faceplayer(); a.opentext(); a.checkevent(got_b); a.iftrue('mel_g')
    a.writetext(T('mel1', mel[0])); a.waitbutton(); a.writetext(T('mel2', mel[1])); a.yesorno(); a.iffalse('mel_r')
    def mel_after():
        a.writetext(T('mel3', mel[2])); a.waitbutton(); a.closetext(); a.disappear(3); a.setevent(bulba_gone)
        a.setevent(got_b); a.end()
    give(BULBASAUR, got_b, 'quit', mel_after)
    a.label('mel_r'); a.writetext(T('mel5', mel[3])); a.waitbutton(); a.closetext(); a.end()
    a.label('mel_g'); a.writetext(T('mel4', mel[4])); a.waitbutton(); a.closetext(); a.end()
    for lab, mon, t in (('m_bul', BULBASAUR, mon_t[0]), ('m_odd', ODDISH_MON, mon_t[1]), ('m_san', SANDSHREW_MON, mon_t[2])):
        a.label(lab); a.opentext(); a.writetext(T(lab + 't', t)); a.cry(mon); a.waitsfx(); a.waitbutton(); a.closetext(); a.end()
    # the house's events (Red's trade house: its warps stay)
    hh = P57.US.get().groups()[25] + 9 * (MELANIE_HOUSE[1] - 1)
    at = fo(rom[hh], r16(hh + 3))
    old = parse_events(rom, rom[at + 6], r16(at + 9))
    a.label('mapscripts'); a.db(0, 0)
    a.label('events'); a.db(0, 0); a.db(len(old['warps']))
    for _, w in old['warps']: a.raw(bytes(w))
    a.db(0, 0)
    objs = [(SPR_GIRL, 3, 1, STAND['DOWN'], 0, 'mel', 0xFFFF), (SPR_BULBASAUR, 4, 1, MOVE_POKEMON, PAL_NPC_GREEN, 'm_bul', bulba_gone),
            (SPR_ODDISH, 1, 4, MOVE_POKEMON, PAL_NPC_BLUE, 'm_odd', 0xFFFF),
            (SPRITE_SANDSHREW, 5, 3, STAND['LEFT'], 0, 'm_san', 0xFFFF)]
    a.db(len(objs))
    for spr, x, y, mv, pal, lab, fl in objs:
        a.db(spr, y + 4, x + 4, mv, 0, 0xFF, 0xFF, pal, 0); a.dw(lab); a.dw(fl)
    # ---- Damian (Route 24)
    got_c = FL.new()
    a.label('dam'); a.faceplayer(); a.opentext(); a.checkevent(got_c); a.iftrue('dam_g')
    a.writetext(T('dam1', dam[0])); a.yesorno(); a.iffalse('dam_r')
    def dam_after():
        a.writetext(T('dam2', dam[1])); a.waitbutton(); a.closetext(); a.setevent(got_c); a.end()
    give(CHARMANDER, got_c, 'quit', dam_after)
    a.label('dam_r'); a.writetext(T('dam3', dam[2])); a.waitbutton(); a.closetext(); a.end()
    a.label('dam_g'); a.writetext(T('dam4', dam[3])); a.waitbutton(); a.closetext(); a.end()
    # ---- Officer Jenny (Vermilion)
    got_s = FL.new()
    a.label('jen'); a.faceplayer(); a.opentext(); a.checkevent(got_s); a.iftrue('jen_g')
    a.checkflag(THUNDER_BADGE); a.iftrue('jen_b')
    a.writetext(T('jen1', jen[0])); a.waitbutton(); a.closetext(); a.end()
    a.label('jen_b'); a.writetext(T('jen2', jen[1])); a.yesorno(); a.iffalse('jen_r')
    def jen_after():
        a.writetext(T('jen3', jen[2])); a.waitbutton(); a.closetext(); a.setevent(got_s); a.end()
    give(SQUIRTLE, got_s, 'quit', jen_after)
    a.label('jen_r'); a.writetext(T('jen4', jen[3])); a.waitbutton(); a.closetext(); a.end()
    a.label('jen_g'); a.writetext(T('jen5', jen[4])); a.waitbutton(); a.closetext(); a.end()
    for k, v in texts.items(): a.label(k); a.raw(v)
    base = a.base; blob = a.done(); assert sp.put(PB, blob) == base
    rom[at + 6] = PB; w16(at + 7, a.labels['mapscripts']); w16(at + 9, a.labels['events'])
    log.append('Melanie\'s house (26:%d), scripts %02X:%04X (%d bytes)' % (MELANIE_HOUSE[1], PB, base, len(blob)))

    # ================= Route 24 / Vermilion City: the new people
    for name, spr, x, y, face, lab in (('Route24', SPR_COOLTRAINER_M, 6, 5, 'DOWN', 'dam'),
                                       ('VermilionCity', SPRITE_JENNY, 19, 15, 'DOWN', 'jen')):
        me = MapEvents(rom, name)
        assert all((o[2] - 4, o[1] - 4) != (x, y) for o, _ in me.objs)
        e = Asm(sp.here(PB)); e.bank = PB
        me.add_object(spr, x, y, STAND[face], ('far', PB, a.labels[lab]))
        me.write(e, sp); eb = e.base; blob = e.done(); assert sp.put(PB, blob) == eb; me.install(e)
        log.append('%s: %d objects, events %02X:%04X' % (name, len(me.objs), PB, eb))
    log.append('flags %X-%X' % (FIRST_FLAG + 0x800, FL.i + 0x800 - 1))

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    print('\n'.join(log))


if __name__ == '__main__':
    main()
