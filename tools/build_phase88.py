#!/usr/bin/env python3
"""Phase 88: Kanto gyms after the Kanto Hall of Fame (three years later, Satoshi the former champion).
 * Viridian Gym: once Shigeru leads it (after the Kanto Hall of Fame), Red's trainers (Giovanni's people) are gone,
   as in Crystal's Viridian Gym; the guide speaks of Shigeru ("three years ago he fought you for the championship")
   instead of Red's "so the leader was Giovanni!".
 * Pewter Gym's guide after Brock's defeat: "keep it up, aim for the Pokémon champion!" -> "what a fine battle!"
   (fits both the Kanto story and the champion three years later).
usage: build_phase88.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import Space
from evedit import MapEvents, copy_text
from jpchar import encode
import portmaps as PM
import build_phase17 as P17

FIRST_FLAG = 532                   # 524-531: phase 87
PEWTER_GUIDE_WON = (0x2E, 0x7350)
GUIDE_SPRITE = 0x48


def T(s): return encode('{00}' + s) + b'\x57'


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom); log = []
    for b in (0x63, 0x5B):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1, b * 0x4000 + 0x4000)
    BANK = max((0x63, 0x5B), key=lambda b: sp.cur[b][1] - sp.cur[b][0])
    FL = PM.Flags(FIRST_FLAG); gone = FL.new()
    # ---- Viridian Gym
    me = MapEvents(rom, 'ViridianGym')
    tr = [i for i, (o, r) in enumerate(me.objs) if r[0] == 'keep']
    assert len(tr) == 8 and all(me.objs[i][0][11:13] == b'\xff\xff' for i in tr)
    for i in tr: me.objs[i][0][11] = gone & 0xFF; me.objs[i][0][12] = gone >> 8
    gi = [i for i, (o, r) in enumerate(me.objs) if o[0] == GUIDE_SPRITE]; assert len(gi) == 1; gi = gi[0]
    g_old = me.objs[gi][1]; assert g_old[0] == 'far'
    cbs = [k for k, (t, r) in enumerate(me.callbacks) if t == 2]; assert len(cbs) == 1
    cb_old = me.callbacks[cbs[0]][1]; assert cb_old[0] == 'far'
    a = Asm(sp.here(BANK)); a.bank = BANK
    a.label('cb'); a.checkevent(P17.EV_HOF); a.iffalse('cb_k'); a.setevent(gone); a.farsjump(cb_old[1], cb_old[2])
    a.label('cb_k'); a.clearevent(gone); a.farsjump(cb_old[1], cb_old[2])
    a.label('gd'); a.checkevent(P17.EV_HOF); a.iffalse('gd_k'); a.db(0x51); a.dw('gd_t')       # jumptextfaceplayer
    a.label('gd_k'); a.farsjump(g_old[1], g_old[2])
    a.label('gd_t'); a.raw(T('おーす！　<PLAYER>！<PARA>いまの　トキワ　ジムの　りーダーは<LINE>シゲル！<PARA>'
                             '3ねんまえ　おまえと<LINE>チャンピオンの　ざを　かけて<CONT>たたかった　おとこだ！<PARA>'
                             'てごわいぜ！<LINE>がんばれよ！'))
    me.callbacks[cbs[0]] = (2, 'cb'); me.objs[gi][1] = 'gd'
    me.write(a, sp)
    base = a.base; assert sp.put(BANK, a.done()) == base
    me.install(a)
    log.append('ViridianGym: Red\'s trainers gone after the HoF (flag %X), guide; events %02X:%04X' % (gone, BANK, base))
    # ---- Pewter Gym's guide
    o = fo(*PEWTER_GUIDE_WON); old = copy_text(rom, o); new = T('さすがだな！<LINE>みごとな　たたかい　だったぜ！')
    assert len(new) <= len(old); rom[o:o + len(new)] = new
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
