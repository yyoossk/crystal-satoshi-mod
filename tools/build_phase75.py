#!/usr/bin/env python3
"""Phase 75: Kanto's Marts (the playthrough check found Crystal's people in Cerulean's Mart: "there are many trainers on
the way to Cerulean Cape"...): like phase 73's Pokémon Centers, Crystal's rooms stay, the clerk stays, the other people
are Red's (sprite, movement, line), at Red's place or the nearest free floor tile.
 * Pewter, Cerulean, Vermilion, Lavender, Saffron, Fuchsia (Viridian's and Cinnabar's are Red's rooms already).
 * "appear" on a person who is already on the screen made a second copy of him (Crystal's CopyObjectStruct does not
   check; the map's own loaders do): Cerulean's guard stood doubled after the backyard Rocket.  CopyObjectStruct
   (02:40E7) now returns when the person already has an object struct.
 * Vermilion's passage to the dock: Crystal's teacher ("the fast ship sails on Wednesdays and Sundays") stands there
   only after the Hall of Fame (the S.S. Aqua's time); before it, as in Red, no one (objects callback, flag 521).
 * Vermilion Gym: Red's trash-can locks (Crystal's room has no door and only trash).  The opening in front of Lt. Surge
   (block 2,2) is closed by a wall block until the 2nd lock opens; the 15 cans work as Red's GymTrashScript (the 1st
   switch in a random even can, chosen when entering (NEWMAP callback: not again after a battle); the 2nd in a random neighbour; a wrong can resets the locks and
   moves the 1st switch); Red's lines.  Flags 522 (1st lock), 523 (2nd lock); the two can numbers in the byte of flags
   0xA10-0xA17 ($DA43).
 * Celadon's Pokémon Center: Crystal's Eusine (kept by phase 73) stands there only after the Kanto Hall of Fame (the
   Johto story) and until the Ho-Oh, as in Crystal (flag 524; objects callback).
 * Rocket Hideout B1F: the door to the elevator room opens right after its guard (Red: "the door opened in the
   commotion") — the tiles callback ran before the trainer flag was set, so it stayed shut until the map was entered
   again; the guard's after-battle script now opens it (changeblock, door sound, refresh).
 * Mt. Moon 1F's item ball (Red: TM12 Water Gun) gives TM12 as the other Red TMs give the TM of the same number
   (phase 15 gave TM11, the same as Misty's).
Flags used: 521-524 (0xA09-0xA0C) and the byte of 528-535 (0xA10-0xA17); the next phase starts at 536.
usage: build_phase75.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
import redmap as RM
from evedit import MapEvents
import build_phase25 as P25
import build_phase29 as P29

BANKS = (0x78, 0x7A, 0x71, 0x62)
CENTERS = [('PewterMart', 'PewterMart', 0x38), ('CeruleanMart', 'CeruleanMart', 0x43),
           ('VermilionMart', 'VermilionMart', 0x5B), ('LavenderMart', 'LavenderMart', 0x96),
           ('SaffronMart', 'SaffronMart', 0xB4), ('FuchsiaMart', 'FuchsiaMart', 0x98)]
NURSE = 0x39                        # the clerk
KEEP = {0x4B, 0xFC}                 # Crystal's Eusine (Celadon), a variable sprite (Fuchsia): kept
FLOOR = {0x00}


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    for B_ in BANKS:
        f, n = bank_free_tail(rom, B_); sp.set_area(B_, f + 1, B_ * 0x4000 + 0x4000)
    SPR = dict(P29.SPR); SPR.setdefault('SPRITE_BALDING_GUY', 0x2D)
    log = []

    def hl(mapid_, tid):
        return [RM.crystal_text(b, p) for b, p in RM.asm_hl(mapid_, tid, n=160, stop=False) if RM.R[RM.fo(b, p)] in (0x00, 0x17)]
    def rt(mapid_, tid):
        b, p = RM.text_ptr(mapid_, tid); k, v = RM.text_body(b, p)
        if k == 'text': return RM.crystal_text(b, p)
        return hl(mapid_, tid)[0]

    for cname, rname, rid in CENTERS:
        me = MapEvents(rom, cname)
        a_ = attrs(rom, hdr_index(cname))
        # collision grid (for free tiles)
        import portmaps as PM
        TS = PM.Tilesets(rom, sp); co = TS.coll_off(rom[hdr_index(cname) + 1])
        w, h = a_['w'], a_['h']; bo = fo(a_['blkbank'], a_['blk'])
        G = [[0] * (2 * w) for _ in range(2 * h)]
        for by in range(h):
            for bx in range(w):
                bl = rom[bo + by * w + bx]
                for q in range(4): G[2 * by + q // 2][2 * bx + q % 2] = rom[co + 4 * bl + q]
        keep = [o for o in me.objs if o[0][0] == NURSE or o[0][0] in KEEP or o[0][0] >= 0x80]
        assert keep and keep[0][0][0] == NURSE, cname
        taken = {(o[0][2] - 4, o[0][1] - 4) for o in keep} | {(w_[1], w_[0]) for w_ in me.warps}
        for x_, y_ in list(taken): taken |= {(x_, y_ + 1)} if (x_, y_) in {(w_[1], w_[0]) for w_ in me.warps} else set()
        objs, warps, bgs = P25.red_objects(rname)
        texts = {}
        new = []
        for i, o in enumerate(objs):
            tid = i + 1
            if o['sprite'] == 'SPRITE_CLERK': continue
            x, y = o['x'], o['y']
            cand = sorted(((abs(xx - x) + abs(yy - y), xx, yy) for yy in range(2, 2 * h - 1) for xx in range(2 * w)
                           if G[yy][xx] in FLOOR and (xx, yy) not in taken))
            _, x, y = cand[0]; taken.add((x, y))
            mv, rng = P25.face((0, 0, 0, o['move'], o['face']))
            lab = 'n%d' % tid
            new.append([bytearray([SPR[o['sprite']], y + 4, x + 4, mv, rng, 0xFF, 0xFF, 0, 0, 0, 0, 0xFF, 0xFF]), lab])
            texts[lab + 't'] = rt(rid, tid)
        me.objs = keep + new
        for BANK in BANKS:
            a = Asm(sp.here(BANK)); a.bank = BANK
            for k_ in texts:
                lab = k_[:-1]; a.label(lab); a.jumptextfaceplayer(k_)
            for k_, v in texts.items():
                a.label(k_); a.raw(v)
            import copy
            me2 = copy.copy(me); me2.objs = [list(o) for o in me.objs]
            me2.write(a, sp)
            base = a.base; blob = a.done()
            if sp.cur[BANK][0] + len(blob) <= sp.cur[BANK][1]: break
        assert sp.put(BANK, blob) == base
        me2.install(a)
        log.append('%s: %d of Red\'s people %s, kept %s (%X:%04X)' % (cname, len(new),
                   [(o[0][2] - 4, o[0][1] - 4) for o in new], [hex(o[0][0]) for o in keep], BANK, base))

    # ================= Mt. Moon 1F: TM12 (Red's TM12 Water Gun), not TM11
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'play'))
    from mapdb import DB
    db = DB(src_rom); m = db.maps[(26, 37)]
    import build_phase12 as P12
    balls = [o for o in db.objs((26, 37)) if o[0] == 0x54]
    hit = [fo(m['scbank'], o[9] | o[10] << 8) for o in balls if rom[fo(m['scbank'], o[9] | o[10] << 8)] == P12.tm_item(11)]
    assert len(hit) == 1
    rom[hit[0]] = P12.tm_item(12)
    log.append('MtMoon1F: TM11 -> TM12 at %X' % hit[0])

    # ================= Vermilion's passage: the S.S. Aqua teacher only after the HoF
    import portmaps as PM
    import build_phase17 as P17
    FL = PM.Flags(521)
    me = MapEvents(rom, 'VermilionPortPassage')
    assert len(me.objs) == 1 and me.objs[0][0][0] == 0x29 and (me.objs[0][0][2] - 4, me.objs[0][0][1] - 4) == (17, 1)
    t_hide = FL.new(); assert t_hide == 0xA09
    FL.new(); FL.new()                  # 0xA0A / 0xA0B: Vermilion Gym's locks (below)
    me.objs[0][0][11] = t_hide & 0xFF; me.objs[0][0][12] = t_hide >> 8
    BANK = [B_ for B_ in BANKS if sp.cur[B_][1] - sp.cur[B_][0] > 300][0]
    a = Asm(sp.here(BANK)); a.bank = BANK
    a.label('pp_cb'); a.checkevent(P17.EV_HOF); a.iftrue('pp_hof'); a.setevent(t_hide); a.endcallback()
    a.label('pp_hof'); a.clearevent(t_hide); a.endcallback()
    me.callbacks.append((2, 'pp_cb'))
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    me.install(a)
    log.append('VermilionPortPassage: teacher after the HoF (flag %X), events %X:%04X' % (t_hide, BANK, base))

    # ================= Celadon's Pokémon Center: Eusine after the HoF
    me = MapEvents(rom, 'CeladonPokecenter1F')
    eu = [o for o in me.objs if o[0][0] == 0x2B]; assert len(eu) == 1 and (eu[0][0][11] | eu[0][0][12] << 8) == 0x7B7
    EU_HIDE = FL.new(); assert EU_HIDE == 0xA0C
    eu[0][0][11] = EU_HIDE & 0xFF; eu[0][0][12] = EU_HIDE >> 8
    assert not [t for t, r_ in me.callbacks if t == 2]
    BANK = [B_ for B_ in BANKS if sp.cur[B_][1] - sp.cur[B_][0] > 300][0]
    a = Asm(sp.here(BANK)); a.bank = BANK
    a.label('eu_cb'); a.checkevent(P17.EV_HOF); a.iffalse('eu_h'); a.checkevent(0x7B7); a.iftrue('eu_h')
    a.clearevent(EU_HIDE); a.endcallback()
    a.label('eu_h'); a.setevent(EU_HIDE); a.endcallback()
    me.callbacks.append((2, 'eu_cb'))
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    me.install(a)
    log.append('CeladonPokecenter1F: Eusine after the HoF (flag %X), events %X:%04X' % (EU_HIDE, BANK, base))

    # ================= Vermilion Gym: Red's trash cans
    from mini_asm import MA
    import redtexts as RT
    EV1, EV2 = 0xA0A, 0xA0B
    BYTE = 0xDA43; HL_FLAGS = 0xDA42                 # EV1 = bit 2, EV2 = bit 3 of $DA42
    RANDOM, SCRIPTVAR = 0x2F5E, 0xC2DD
    SFX_PUSH_BUTTON, SFX_ENTER_DOOR = 0x11, 0x1F
    SFX_ENTER_DOOR_ = SFX_ENTER_DOOR
    G_WALL, G_FLOOR = 0x20, 0x01
    me = MapEvents(rom, 'VermilionGym')
    ga = attrs(rom, hdr_index('VermilionGym')); gbo = fo(ga['blkbank'], ga['blk'])
    assert rom[gbo + 2 * ga['w'] + 2] == G_FLOOR and rom[gbo + 2 * ga['w'] + 0] == G_WALL
    cans = sorted([(x, y) for y, x, t, r in me.bgs if 7 <= y <= 11])
    assert cans == [(x, y) for x in (1, 3, 5, 7, 9) for y in (7, 9, 11)]
    TABLE = [(2, 1, 3, 0, 0), (3, 0, 2, 4, 0), (2, 1, 5, 0, 0), (3, 0, 4, 6, 0), (4, 1, 3, 5, 7), (3, 2, 4, 8, 0),
             (3, 3, 7, 9, 0), (4, 4, 6, 8, 10), (3, 5, 7, 11, 0), (3, 6, 10, 12, 0), (4, 7, 9, 11, 13),
             (3, 8, 10, 14, 0), (2, 9, 13, 0, 0), (3, 10, 12, 14, 0), (2, 11, 13, 0, 0)]      # Red's GymTrashCans
    BANK = 0x63; f_, n_ = bank_free_tail(rom, BANK); sp.set_area(BANK, f_ + 1, BANK * 0x4000 + 0x4000)
    m = MA(sp.here(BANK))
    m.label('trash')
    m(0xFA, SCRIPTVAR & 0xFF, SCRIPTVAR >> 8, 0x4F)                       # ld a,[wScriptVar] / ld c,a
    m(0x21, HL_FLAGS & 0xFF, HL_FLAGS >> 8)                                 # ld hl,flags
    m(0xCB, 0x5E, 0x20, ('jr', 't_trash'))                                  # bit 3,[hl] / jr nz,trash
    m(0xCB, 0x56, 0x20, ('jr', 't_second'))                                 # bit 2,[hl] / jr nz,second
    m(0xFA, BYTE & 0xFF, BYTE >> 8, 0xE6, 0x0F, 0xB9, 0x20, ('jr', 't_trash'))
    m(0xCB, 0xD6)                                                           # set 2,[hl]
    m(0x21, ('a16', 'table'), 0x79, 0x87, 0x87, 0x81, 0x5F, 0x16, 0x00, 0x19)  # hl = table + c*5
    m(0x2A, 0x47)                                                           # ld a,[hli] / ld b,a (count)
    m.label('t_rnd'); m(0xCD, RANDOM & 0xFF, RANDOM >> 8, 0xE6, 0x03, 0xB8, 0x30, ('jr', 't_rnd'))
    m(0x5F, 0x16, 0x00, 0x19, 0x7E)                                         # a = [hl + r]
    m(0xCB, 0x37, 0x47, 0xFA, BYTE & 0xFF, BYTE >> 8, 0xE6, 0x0F, 0xB0, 0xEA, BYTE & 0xFF, BYTE >> 8)
    m(0x3E, 1, 0x18, ('jr', 't_ret'))
    m.label('t_second')
    m(0xFA, BYTE & 0xFF, BYTE >> 8, 0xCB, 0x37, 0xE6, 0x0F, 0xB9, 0x28, ('jr', 't_open'))
    m(0xCB, 0x96)                                                           # res 2,[hl]
    m(0xCD, ('a16', 'init_rnd'), 0x3E, 2, 0x18, ('jr', 't_ret'))
    m.label('t_open'); m(0xCB, 0xDE, 0x3E, 3, 0x18, ('jr', 't_ret'))
    m.label('t_trash'); m(0xAF)
    m.label('t_ret'); m(0xEA, SCRIPTVAR & 0xFF, SCRIPTVAR >> 8, 0xC9)
    m.label('init')                                                         # entering: the 1st switch (Red: random & $e)
    m(0x21, HL_FLAGS & 0xFF, HL_FLAGS >> 8, 0xCB, 0x56, 0xC0)
    m.label('init_rnd')
    m(0xCD, RANDOM & 0xFF, RANDOM >> 8, 0xE6, 0x0E, 0x47, 0xFA, BYTE & 0xFF, BYTE >> 8, 0xE6, 0xF0, 0xB0,
      0xEA, BYTE & 0xFF, BYTE >> 8, 0xC9)
    m.label('table')
    for row in TABLE: m(*row)
    code = m.done(); assert sp.put(BANK, code) == m.base
    a = Asm(sp.here(BANK)); a.bank = BANK
    for i, (x, y) in enumerate(cans):
        idx = ((x - 1) // 2) * 3 + (y - 7) // 2; assert idx == i
        a.label('can%d' % i); a.db(0x15, idx); a.sjump('can')
    a.label('can'); a.callasm(BANK, m.L['trash'])
    a.ifequal(1, 'c1'); a.ifequal(2, 'c2'); a.ifequal(3, 'c3'); a.jumptext('t_trash')
    a.label('c1'); a.opentext(); a.writetext('t_1'); a.playsound(SFX_PUSH_BUTTON); a.waitsfx(); a.waitbutton(); a.closetext(); a.end()
    a.label('c2'); a.jumptext('t_fail')
    a.label('c3'); a.opentext(); a.writetext('t_3'); a.waitbutton(); a.closetext()
    a.changeblock(4, 4, G_FLOOR); a.playsound(SFX_ENTER_DOOR); a.refreshmap(); a.waitsfx(); a.end()
    a.label('g_cb'); a.checkevent(EV2); a.iftrue('g_cbo'); a.changeblock(4, 4, G_WALL)
    a.label('g_cbo'); a.endcallback()
    a.label('g_new'); a.callasm(BANK, m.L['init']); a.endcallback()      # entering (not after a battle)
    for lab, adr in (('t_trash', 0x5FDCF), ('t_1', 0x5FEAF), ('t_3', 0x5FF4D), ('t_fail', 0x5FF8D)):
        a.label(lab); a.raw(RT.raw(adr) + b'\x57')
    me.bgs = [(y, x, t, ('can%d' % cans.index((x, y))) if (x, y) in cans else r_) for y, x, t, r_ in me.bgs]
    me.callbacks += [(5, 'g_new'), (1, 'g_cb')]
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    me.install(a)
    log.append('VermilionGym: trash cans (flags %X %X, $%04X), code %X:%04X, events %X:%04X' % (EV1, EV2, BYTE, BANK, m.base, BANK, base))

    # ================= Rocket Hideout B1F: the door opens right after its guard
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'play'))
    from mapdb import DB as _DB
    db_ = _DB(src_rom); m_ = db_.maps[(26, 21)]
    gd = [o for o in db_.objs((26, 21)) if (o[2] - 4, o[1] - 4) == (28, 18)]; assert len(gd) == 1
    hb_ = fo(m_['scbank'], gd[0][9] | gd[0][10] << 8); assert rom[hb_:hb_ + 2] == bytes([0xEA, 0x05])
    x_old = rom[hb_ + 10] | rom[hb_ + 11] << 8
    a2 = attrs(rom, m_['hdr']); bo2 = fo(a2['blkbank'], a2['blk']); blk_open = rom[bo2 + 8 * a2['w'] + 12]
    f_, n_ = bank_free_tail(rom, m_['scbank']); sp.set_area(m_['scbank'], f_ + 1, m_['scbank'] * 0x4000 + 0x4000)
    a = Asm(sp.here(m_['scbank'])); a.bank = m_['scbank']
    a.changeblock(24, 16, blk_open); a.playsound(SFX_ENTER_DOOR_); a.refreshmap(); a.sjump(x_old)
    base = a.base; blob = a.done(); assert sp.put(m_['scbank'], blob) == base
    rom[hb_ + 10] = base & 0xFF; rom[hb_ + 11] = base >> 8
    log.append('RocketHideoutB1F: the door opens after its guard (block %02X, %X:%04X)' % (blk_open, m_['scbank'], base))

    # ================= appear: no second copy
    CO = 0x80E7; assert rom[CO] == 0xCD and rom[CO + 3:CO + 5] == bytes([0xA7, 0xC0])
    f, n = bank_free_tail(rom, 2); hk = f + 1; assert n >= 12
    a_ = 0x4000 + hk - 0x8000
    rom[hk:hk + 10] = bytes([0x0A, 0xFE, 0xFF, 0xC0]) + rom[CO:CO + 3] + bytes([0xC3, 0xEA, 0x40])   # ld a,[bc] / cp -1 / ret nz / call CheckObjectMask / jp $40EA
    rom[CO:CO + 3] = bytes([0xC3, a_ & 0xFF, a_ >> 8])
    log.append('CopyObjectStruct: no second copy (02:%04X)' % a_)

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
