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
 * Mt. Moon 1F's item ball (Red: TM12 Water Gun) gives TM12 as the other Red TMs give the TM of the same number
   (phase 15 gave TM11, the same as Misty's).
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
    t_hide = FL.new()
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
