#!/usr/bin/env python3
"""Phase 18: Team Rocket in Saffron City (Red).
 * Rockets 1-7 in the streets until Giovanni leaves Silph Co. (11F).
 * The rocket in front of Silph Co. blocks the door until Jessie & James are beaten in the Pokémon Tower;
   then a sleeping rocket stands beside the door until Silph Co. is freed.
 Texts from JP Red.  (Red's extra citizens after the liberation are not added: Crystal's own townspeople stay.)
usage: build_phase18.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
import portmaps as PM
import build_phase12 as P12
import build_phase17 as P17
import redtexts as RT
from evedit import MapEvents

FIRST_FLAG = 68                    # extended flags used up to here by phase 17
SPR_ROCKET = 0x35
EV_SILPH_FREED = 0x606             # Giovanni left Silph Co. 11F (phase 14)
EV_TOWER_FREED = 0x5E1             # Jessie & James beaten on Pokémon Tower 7F (phase 11)
WALK_LR = (0x04, 0x10)             # SPRITEMOVEDATA_WALK_LEFT_RIGHT, radius 1


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    f, n = bank_free_tail(rom, 0x62); sp.set_area(0x62, f + 1, 0x62 * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)

    # Red's texts, in pokered order: Rocket1-7, scientist, workers, gentleman, Pidgeot, rocker, Rocket8, Rocket9
    o = 0x50C35; tx = []
    while len(tx) < 16:
        b = RT.raw(o); o += len(b) + 1
        if b[:1] == b'\x00': tx.append(b)
    rk = tx[0:7]; guard, sleeper = tx[13], tx[14]

    me = MapEvents(rom, 'SaffronCity')
    a = Asm(sp.here(0x62)); a.bank = 0x62
    # a map holds at most 14 object events (ids 2-15): Crystal has 8 here.  Rockets 2 and 3 borrow two of
    # Crystal's townspeople (variable sprites) until Silph Co. is freed, and the two rockets at the Silph Co.
    # door share one object.
    SHARE = {1: (7, 0x28, 0xFE), 2: (2, 0x23, 0xFD)}      # rocket index -> (Crystal object index, sprite, var)
    ROCKETS = [((7, 6), None), ((20, 8), WALK_LR), ((34, 4), None), ((13, 12), None),
               ((11, 25), WALK_LR), ((32, 13), WALK_LR), ((18, 30), WALK_LR)]
    texts = {}
    for i, ((x, y), mv) in enumerate(ROCKETS):
        L = 'rk%d' % i; texts[L + 't'] = rk[i]
        a.label(L); a.jumptextfaceplayer(L + 't')
        if i in SHARE:
            ci, spr, var = SHARE[i]; ob = me.objs[ci]; assert ob[0][0] == spr
            ob[0][0] = var; osc = ob[1]; ob[1] = 'sh%d' % i
            a.label('sh%d' % i); a.checkevent(EV_SILPH_FREED); a.iffalse(L); a.farsjump(osc[1], osc[2])
            continue
        if mv: me.add_object(SPR_ROCKET, x, y, mv[0], L, flag=EV_SILPH_FREED, rng=mv[1])
        else: me.add_object(SPR_ROCKET, x, y, P12.FACE['DOWN'], L, flag=EV_SILPH_FREED)
    door = me.add_object(SPR_ROCKET, 18, 22, P12.FACE['DOWN'], 'rkd', flag=EV_SILPH_FREED) + 1
    assert len(me.objs) <= 14 and door <= 15
    a.label('rkd'); a.checkevent(EV_TOWER_FREED); a.iftrue('rk9'); a.jumptextfaceplayer('rk8t'); texts['rk8t'] = guard
    a.label('rk9'); a.jumptext('rk9t'); texts['rk9t'] = sleeper
    a.label('sf_cb')
    a.checkevent(EV_SILPH_FREED); a.iftrue('sf_free')
    for i, (ci, spr, var) in SHARE.items():
        (x, y), _ = ROCKETS[i]; a.variablesprite(var - 0xF0, SPR_ROCKET); a.moveobject(ci + 2, x, y)
    a.checkevent(EV_TOWER_FREED); a.iffalse('sf_e'); a.moveobject(door, 19, 22); a.endcallback()
    a.label('sf_free')
    for i, (ci, spr, var) in SHARE.items(): a.variablesprite(var - 0xF0, spr)
    a.label('sf_e'); a.endcallback()
    me.callbacks.append((2, 'sf_cb'))
    # the sprite graphics are loaded before the objects: set the variable sprites there too
    a.label('sf_spr'); a.checkevent(EV_SILPH_FREED); a.iftrue('sf_spr_free')
    for i, (ci, spr, var) in SHARE.items(): a.variablesprite(var - 0xF0, SPR_ROCKET)
    a.endcallback()
    a.label('sf_spr_free')
    for i, (ci, spr, var) in SHARE.items(): a.variablesprite(var - 0xF0, spr)
    a.endcallback()
    me.callbacks.append((4, 'sf_spr'))
    for k, v in texts.items():
        a.label(k); a.raw(P12.text(v))
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(0x62, blob) == base
    me.install(a)
    log.append('SaffronCity: 9 rockets, events moved to 62:%04X (%d bytes)' % (base, len(blob)))
    P17.fix_outdoor_sprites(rom, log)

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
