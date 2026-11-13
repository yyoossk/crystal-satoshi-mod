#!/usr/bin/env python3
"""Phase 73: Kanto's Pokémon Centers keep Crystal's rooms but have Red's people and lines (the playthrough check found
Crystal's lines there, about Crystal's time: "the Viridian Gym Leader went away", "Cinnabar's Gym is gone"...).
 * Viridian, Pewter, Cerulean, Vermilion, Lavender, Celadon, Saffron, Fuchsia, Cinnabar and the Rock Tunnel one
   (Route10Pokecenter1F): Crystal's people (but the nurse, the Pokémon-sprite / special people) are replaced by Red's
   (Red's sprite, movement, line).  Red's centers are 14 wide, Crystal's 10: Red's x 0-5 stay, x >= 6 move 4 left; when
   that tile is not free, the nearest free floor tile.
usage: build_phase73.py IN.gbc OUT.gbc OUT.ips
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
CENTERS = [('ViridianPokecenter1F', 'ViridianPokecenter', 0x29), ('PewterPokecenter1F', 'PewterPokecenter', 0x3A),
           ('CeruleanPokecenter1F', 'CeruleanPokecenter', 0x40), ('VermilionPokecenter1F', 'VermilionPokecenter', 0x59),
           ('LavenderPokecenter1F', 'LavenderPokecenter', 0x8D), ('CeladonPokecenter1F', 'CeladonPokecenter', 0x85),
           ('SaffronPokecenter1F', 'SaffronPokecenter', 0xB6), ('FuchsiaPokecenter1F', 'FuchsiaPokecenter', 0x9A),
           ('CinnabarPokecenter1F', 'CinnabarPokecenter', 0xAB), ('Route10Pokecenter1F', 'RockTunnelPokecenter', 0x51)]
NURSE = 0x37
KEEP = {0xFC}                       # a variable sprite (Fuchsia's Janine impersonator): kept
EUSINE = ('CeladonPokecenter1F', 0x2B)   # Crystal's Eusine (Johto story, after the Ho-Oh): kept (0x4B is the pharmacist: Red's people)
FLOOR = {0x00}


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    for B_ in BANKS:
        f, n = bank_free_tail(rom, B_); sp.set_area(B_, f + 1, B_ * 0x4000 + 0x4000)
    SPR = P29.SPR
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
        keep = [o for o in me.objs if o[0][0] == NURSE or o[0][0] in KEEP or o[0][0] >= 0x80 or (cname, o[0][0]) == EUSINE]
        assert keep and keep[0][0][0] == NURSE, cname
        taken = {(o[0][2] - 4, o[0][1] - 4) for o in keep} | {(w_[1], w_[0]) for w_ in me.warps}
        for x_, y_ in list(taken): taken |= {(x_, y_ + 1)} if (x_, y_) in {(w_[1], w_[0]) for w_ in me.warps} else set()
        objs, warps, bgs = P25.red_objects(rname)
        texts = {}
        new = []
        for i, o in enumerate(objs):
            tid = i + 1
            if o['sprite'] in ('SPRITE_NURSE', 'SPRITE_LINK_RECEPTIONIST'): continue
            if o['sprite'] == 'SPRITE_FAIRY' and any(k[0][0] >= 0x80 for k in keep): continue      # Pewter: Crystal's Jigglypuff
            x, y = (o['x'], o['y']) if o['x'] <= 5 else (o['x'] - 4, o['y'])
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

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
