#!/usr/bin/env python3
"""Phase 17: Shigeru's remaining Red battles and Giovanni in the Viridian Gym (texts from JP Red).
 * Oak's lab: Shigeru waits by the table, takes the starter strong against yours, battles you on the way out
   (can be lost, party healed afterwards) and walks out.
 * Route 22 (in front of the League gate): 1st battle after the Pokédex until the Boulder Badge,
   2nd battle after the Earth Badge.
 * Cerulean City, north bridge: battle on the way to Route 24.
 * Viridian Gym: Giovanni (party 3) before the Kanto Hall of Fame, Earth Badge + TM27, then he leaves;
   Crystal's Blue stays there afterwards.
usage: build_phase17.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import portmaps as PM
import build_phase11 as P11
import build_phase12 as P12
import build_phase13 as P13
import build_phase15 as P15
import redtexts as RT
from evedit import MapEvents

FIRST_FLAG = 59                    # extended flags used up to here by phase 16
BLUE, GIOVANNI = 64, 71
SPR_BLUE, SPR_GIOVANNI = 0x07, 0x3F
EV_GOT_STARTER, EV_FIRE, EV_WATER, EV_GRASS = 0x342, 0x343, 0x344, 0x345
BALL_FLAG = {'fire': 0x346, 'water': 0x347, 'grass': 0x348}      # Charmander / Squirtle / Bulbasaur balls
EV_HOF = 0x34A
ENGINE_POKEDEX, ENGINE_BOULDER, ENGINE_EARTH = 0x0B, 0x23, 0x2A
HEAL_PARTY = 27
MUS_RIVAL, MUS_RIVAL_AFTER = 0x1F, 0x20
VAR_BATTLETYPE, BATTLETYPE_CANLOSE = 3, 1
STRBUF = 0xD071                    # getmonname buffer 0
D, U, L, R = 0x0C, 0x0D, 0x0E, 0x0F            # step movements
TD, TU, TL, TR = 0x00, 0x01, 0x02, 0x03        # turn head
MEND = 0x47
STARTERS = ('fire', 'water', 'grass')
SPECIES = {'fire': 0x04, 'water': 0x07, 'grass': 0x01}
RIVAL_TAKES = {'fire': 'water', 'water': 'grass', 'grass': 'fire'}


def riv(b): return bytes(b).replace(b'\x53', encode('シゲル'))
def T(o): return riv(RT.raw(o))
def after(o):
    """the text that follows the one at o (after its terminator)"""
    return T(o + len(RT.raw(o)) + 1)


OUTDOOR_SPRITES_PTR = (0x05, 0x44A9)


def fix_outdoor_sprites(rom, log):
    u = US.get(); G = u.groups(); tab = fo(*OUTDOOR_SPRITES_PTR)
    for gi in range(len(G) - 1):
        lp = fo(5, rom[tab + 2 * gi] | rom[tab + 2 * gi + 1] << 8)
        lst = list(rom[lp:lp + 23]); used = set()
        for k in range((G[gi + 1] - G[gi]) // 9):
            hdr = G[gi] + 9 * k
            if rom[hdr + 2] not in (1, 2): continue
            a = attrs(rom, hdr); ev = parse_events(rom, a['scbank'], a['events'])
            used |= {o[0] for _, o in ev['objs']}
        miss = sorted(x for x in used - set(lst) if x < 0x67)
        if not miss: continue
        cand = [i for i, x in enumerate(lst) if x in (0x11, 0x1B)] + [i for i in range(12, 23) if lst[i] not in used]
        assert len(cand) >= len(miss), (gi + 1, miss)
        for x, i in zip(miss, cand):
            log.append('outdoor sprites group %d: %02X -> %02X' % (gi + 1, lst[i], x)); lst[i] = x
        rom[lp:lp + 23] = bytes(lst)


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    for b in (0x62, 0x78):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1, b * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)

    # ================= trainer parties (bank 7E)
    groups = P13.read_groups7e(rom)
    def pb(mons): return b'\x00' + b''.join(bytes([lv, PM.MON[P15.P10.MON_ALIAS.get(s, s)]]) for lv, s in mons) + b'\xff'
    r1 = P11.red_parties('Rival1Data'); r2 = P11.red_parties('Rival2Data')
    pid = {}
    for key, src in (('lab', r1[0:3]), ('r22a', r1[3:6]), ('cer', r1[6:9]), ('r22b', r2[9:12])):
        for st, party in zip(STARTERS, src):
            groups[BLUE - 1].append([encode('シゲル@'), pb(party)]); pid[(key, st)] = len(groups[BLUE - 1])
    groups[GIOVANNI - 1].append([encode('サカキ@'), pb(P11.red_parties('GiovanniData')[2])])
    gio_party = len(groups[GIOVANNI - 1])
    log.append('trainer parties added (bank 7E free %d)' % P13.write_groups7e(rom, groups))

    # ================= Shigeru's items before the Hall of Fame (Red: Rival1 none, Rival2 potions, champion full restores)
    # GetTrainerAttributes (bank 7E copy) ends with  ld a,[hl] / ld [wEnemyTrainerBaseReward],a / ret  -> jp hook
    gta = fo(0x7E, 0x55A4)
    assert rom[gta] == 0x21 and rom[gta + 0x11:gta + 0x16] == bytes([0x7E, 0xEA, 0x48, 0xC6, 0xC9])
    POTION = P15.item_id('POTION'); r1ids = {pid[k] for k in pid if k[0] in ('lab', 'r22a', 'cer')}
    table = b''
    for i, (nm, party) in enumerate(groups[BLUE - 1]):
        if nm != encode('シゲル@'): continue
        lv = max(party[1::2][:-1]) if party[0] == 0 else 0
        if i + 1 in r1ids: table += bytes([i + 1, 0, 0])
        elif lv < 55: table += bytes([i + 1, POTION, POTION])
    W_EV = 0xDA65 + (EV_HOF >> 3)
    h = Asm(P13.HOOK7E)
    h.db(0x7E, 0xEA, 0x48, 0xC6)                                  # ld a,[hl] / ld [wEnemyTrainerBaseReward],a
    h.db(0xFA, 0x64, 0xD2, 0xFE, BLUE, 0xC0)                      # ld a,[wTrainerClass] / cp BLUE / ret nz
    h.db(0xFA, W_EV & 0xFF, W_EV >> 8, 0xCB, 0x47 | ((EV_HOF & 7) << 3), 0xC0)   # Hall of Fame -> Crystal's items
    h.db(0xFA, 0x62, 0xD2, 0x47, 0x21); h.dw('tab')               # ld a,[wOtherTrainerID] / ld b,a / ld hl,tab
    h.label('lp'); h.db(0x2A, 0xFE, 0xFF, 0xC8, 0xB8, 0x28, 0x04, 0x23, 0x23, 0x18, 0xF5)
    h.db(0x2A, 0xEA, 0x46, 0xC6, 0x7E, 0xEA, 0x47, 0xC6, 0xC9)    # items 1 / 2
    h.label('tab'); h.raw(table + b'\xff')
    hb = h.done(); assert P13.HOOK7E + len(hb) <= 0x8000, len(hb)
    o = fo(0x7E, P13.HOOK7E); assert not any(rom[o:o + len(hb)]); rom[o:o + len(hb)] = hb
    rom[gta + 0x11:gta + 0x16] = bytes([0xC3, P13.HOOK7E & 0xFF, P13.HOOK7E >> 8, 0x00, 0x00])
    log.append('Shigeru item hook at 7E:%04X (%d entries)' % (P13.HOOK7E, len(table) // 3))

    def rival_battle(a, key, win, lose, canlose=False, obj=None, pkey=None):
        """winlosstext + loadtrainer by starter + startbattle (labels key+...; parties of pkey)"""
        pkey = pkey or key
        a.winlosstext(win, lose)
        if obj: a.setlasttalked(obj)
        a.checkevent(EV_FIRE); a.iftrue(key + '_f')
        a.checkevent(EV_WATER); a.iftrue(key + '_w')
        a.loadtrainer(BLUE, pid[(pkey, 'grass')]); a.sjump(key + '_go')
        a.label(key + '_f'); a.loadtrainer(BLUE, pid[(pkey, 'fire')]); a.sjump(key + '_go')
        a.label(key + '_w'); a.loadtrainer(BLUE, pid[(pkey, 'water')])
        a.label(key + '_go')
        if canlose:
            a.loadvar(VAR_BATTLETYPE, BATTLETYPE_CANLOSE); a.startbattle(); a.dontrestartmapmusic(); a.reloadmap()
        else:
            a.startbattle(); a.dontrestartmapmusic(); a.reloadmapafterbattle()

    def by_starter(a, key):
        """jump to key+'_fire' / '_water' / '_grass'"""
        a.checkevent(EV_FIRE); a.iftrue(key + '_fire')
        a.checkevent(EV_WATER); a.iftrue(key + '_water')
        a.sjump(key + '_grass')

    def put_map(me, a, texts, movs):
        for k, v in texts.items():
            a.label(k); a.raw(P12.text(v))
        for k, v in movs.items():
            a.label(k); a.raw(bytes(v) + bytes([MEND]))
        me.write(a, sp)
        base = a.base; blob = a.done(); assert sp.put(0x62, blob) == base
        me.install(a)
        log.append('%s: events moved to %X:%04X (%d bytes)' % (me.name, 0x62, base, len(blob)))

    # ================================================================ Oak's lab
    me = MapEvents(rom, 'OaksLab')
    a = Asm(sp.here(0x62)); a.bank = 0x62
    lab_picked, lab_done = FL.new(), FL.new()
    r22hide, cer_hide = FL.new(), FL.new()           # rivals elsewhere stay hidden from the lab battle on
    RIVAL_POS = {'fire': (7, 5), 'water': (9, 4), 'grass': (6, 5)}
    rv = me.add_object(SPR_BLUE, 9, 4, P12.FACE['LEFT'], 'lr_talk', flag=lab_done) + 1
    texts = {'lr_go': T(0x1CB4F), 'lr_strong': T(0x1CB81), 'lr_this': T(0x1D272),
             'lr_intro': T(0x1D2AE), 'lr_win': T(0x1D2E4), 'lr_lose': T(0x1D304), 'lr_after': T(0x1D321)}
    # "シゲルは　オーキドから<LINE>[mon]を　もらった！"
    got = RT.raw(0x1D28A); texts['lr_got'] = riv(got) + b'\x50\x01' + bytes([STRBUF & 0xFF, STRBUF >> 8]) + RT.raw(0x1D299)
    movs = {}
    a.label('lr_talk'); a.faceplayer(); a.opentext(); a.checkevent(EV_GOT_STARTER); a.iftrue('lr_t2')
    a.writetext('lr_go'); a.waitbutton(); a.closetext(); a.end()
    a.label('lr_t2'); a.writetext('lr_strong'); a.waitbutton(); a.closetext(); a.end()
    # after the player got a starter: Shigeru takes his
    for st in STARTERS:
        tk = RIVAL_TAKES[st]; ball_obj = {'fire': 3, 'water': 4, 'grass': 5}[tk]
        a.label('lp_' + st)
        a.waitbutton(); a.closetext()
        a.checkevent(EV_HOF); a.iftrue('lp_end')
        if st == 'grass':                       # the player stands in the way: step up to the empty spot
            a.applymovement(0, 'mv_pup'); movs['mv_pup'] = [U]
        if st == 'water':
            a.turnobject(rv, TL)
        else:
            a.applymovement(rv, 'mv_pick_' + st)
            x, y = RIVAL_POS[st]; movs['mv_pick_' + st] = [D] + [L] * (9 - x) + [TU]
        a.opentext(); a.writetext('lr_this'); a.waitbutton()
        a.disappear(ball_obj); a.setevent(BALL_FLAG[tk])
        a.getmonname(SPECIES[tk]); a.writetext('lr_got'); a.playsound(0x0002); a.waitsfx(); a.waitbutton(); a.closetext()
        a.setevent(lab_picked); a.end()
    a.label('lp_end'); a.end()
    # map reload: put him back where he stands after his pick
    a.label('lr_cb'); a.checkevent(lab_picked); a.iffalse('lr_cbe'); a.checkevent(lab_done); a.iftrue('lr_cbe')
    by_starter(a, 'lr_cbp')
    for st in STARTERS:
        a.label('lr_cbp_' + st); x, y = RIVAL_POS[st]; a.moveobject(rv, x, y); a.endcallback()
    a.label('lr_cbe'); a.endcallback()
    me.callbacks.append((2, 'lr_cb'))
    # the battle on the way out (gap between the bookshelves, x = 4 / 5)
    for xp in (4, 5):
        L_ = 'lb%d' % xp
        me.coords.append((0xFF, 7, xp, L_))
        a.label(L_); a.checkevent(lab_picked); a.iffalse('lb_end'); a.checkevent(lab_done); a.iftrue('lb_end')
        a.playmusic(MUS_RIVAL); a.turnobject(0, TU)
        a.opentext(); a.writetext('lr_intro'); a.waitbutton(); a.closetext()
        by_starter(a, L_ + 'm')
        for st in STARTERS:
            a.label(L_ + 'm_' + st); x, y = RIVAL_POS[st]
            m = ([D] if y == 4 else []) + [L] * (x - xp) + [D]
            movs['mv_%s_%s' % (L_, st)] = m
            a.applymovement(rv, 'mv_%s_%s' % (L_, st)); a.sjump(L_ + 'b')
        a.label(L_ + 'b'); a.turnobject(0, TU)
        rival_battle(a, 'lab%d' % xp, 'lr_win', 'lr_lose', canlose=True, obj=rv, pkey='lab')
        a.special(HEAL_PARTY); a.playmusic(MUS_RIVAL_AFTER)
        a.opentext(); a.writetext('lr_after'); a.waitbutton(); a.closetext()
        movs['mv_out%d' % xp] = ([R] if xp == 4 else [L]) + [D] * 5
        a.applymovement(rv, 'mv_out%d' % xp); a.disappear(rv); a.setevent(lab_done)
        a.setevent(r22hide); a.setevent(cer_hide); a.playmapmusic(); a.end()
    a.label('lb_end'); a.end()
    put_map(me, a, texts, movs)
    # hook the three starter balls: after "…を てにいれた！" continue with Shigeru's pick
    for site, st in ((0x4032, 'fire'), (0x406F, 'water'), (0x40AC, 'grass')):
        o = fo(0x78, site); assert rom[o] == 0x2D and rom[o + 5] == 0x4C and rom[o + 8:o + 11] == b'\x53\x49\x90'
        txt = rom[o + 6] | rom[o + 7] << 8
        b = Asm(sp.here(0x62)); b.farwritetext(0x78, txt); b.farsjump(0x62, a.labels['lp_' + st])
        p = sp.put(0x62, b.done())
        rom[o + 5:o + 11] = bytes([0x04, 0x62, p & 0xFF, p >> 8, 0x90, 0x90])

    # ================================================================ Route 22 (gate front, x 14, y 9)
    me = MapEvents(rom, 'Route22')
    a = Asm(sp.here(0x62)); a.bank = 0x62
    r22a, r22b = FL.new(), FL.new()
    rv = me.add_object(SPR_BLUE, 13, 6, P12.FACE['DOWN'], 'r22_talk', flag=r22hide) + 1
    texts = {'r1i': T(0x51682), 'r1a': after(0x51682), 'r1w': T(0x5175A), 'r1l': T(0x5176D),
             'r2i': T(0x517B8), 'r2a': T(0x51842), 'r2w': T(0x518B6), 'r2l': T(0x518D7)}
    movs = {'mv_in': [R, D, D], 'mv_away': [U, U, L, U]}
    a.label('r22_talk'); a.end()
    me.coords.append((0xFF, 9, 14, 'r22'))
    a.label('r22'); a.checkevent(EV_HOF); a.iftrue('r22_end')
    a.checkflag(ENGINE_EARTH); a.iftrue('r22_2')
    a.checkevent(r22a); a.iftrue('r22_end'); a.checkflag(ENGINE_BOULDER); a.iftrue('r22_end')
    a.checkflag(ENGINE_POKEDEX); a.iffalse('r22_end')
    for k, key, fl in (('1', 'r22a', r22a), ('2', 'r22b', r22b)):
        if k == '2':
            a.label('r22_2'); a.checkevent(r22b); a.iftrue('r22_end')
        a.playmusic(MUS_RIVAL); a.appear(rv); a.applymovement(rv, 'mv_in'); a.turnobject(0, TU)
        a.opentext(); a.writetext('r%si' % k); a.waitbutton(); a.closetext()
        rival_battle(a, key, 'r%sw' % k, 'r%sl' % k, obj=rv)
        a.disappear(rv); a.moveobject(rv, 14, 8); a.appear(rv); a.turnobject(rv, TD)    # redraw after the battle
        a.playmusic(MUS_RIVAL_AFTER); a.opentext(); a.writetext('r%sa' % k); a.waitbutton(); a.closetext()
        a.applymovement(rv, 'mv_away'); a.disappear(rv); a.setevent(fl); a.playmapmusic(); a.end()
    a.label('r22_end'); a.end()
    put_map(me, a, texts, movs)

    # ================================================================ Cerulean City (north bridge, x 20/21, y 4)
    me = MapEvents(rom, 'CeruleanCity')
    a = Asm(sp.here(0x62)); a.bank = 0x62
    cer_done = FL.new()
    rv = me.add_object(SPR_BLUE, 20, 0, P12.FACE['DOWN'], 'cer_talk', flag=cer_hide) + 1
    texts = {'ci': T(0x19D3D), 'cw': T(0x19DA4), 'cl': T(0x19DC5), 'ca': T(0x19DDC)}
    movs = {'mv_cin': [D, D, D], 'mv_cout': [U, U, U]}
    a.label('cer_talk'); a.end()
    a.label('cer_cb'); a.checkevent(EV_HOF); a.iffalse('cer_cbe'); a.setevent(cer_done)
    a.label('cer_cbe'); a.endcallback()
    me.callbacks.append((2, 'cer_cb'))
    for xp in (20, 21):
        L_ = 'cer%d' % xp
        me.coords.append((0xFF, 4, xp, L_))
        a.label(L_); a.checkevent(cer_done); a.iftrue('cer_end')
        a.playmusic(MUS_RIVAL); a.moveobject(rv, xp, 0); a.appear(rv); a.applymovement(rv, 'mv_cin'); a.turnobject(0, TU)
        a.opentext(); a.writetext('ci'); a.waitbutton(); a.closetext()
        rival_battle(a, 'cerb%d' % xp, 'cw', 'cl', obj=rv, pkey='cer')
        a.disappear(rv); a.moveobject(rv, xp, 3); a.appear(rv); a.turnobject(rv, TD)
        a.playmusic(MUS_RIVAL_AFTER); a.opentext(); a.writetext('ca'); a.waitbutton(); a.closetext()
        a.applymovement(rv, 'mv_cout'); a.disappear(rv); a.setevent(cer_done); a.playmapmusic(); a.end()
    a.label('cer_end'); a.end()
    put_map(me, a, texts, movs)

    # ================================================================ Viridian Gym: Giovanni before the Hall of Fame
    # (the gym has trainers, so its events stay in bank 77; the new scripts go to bank 62)
    me = MapEvents(rom, 'ViridianGym')
    f, n = bank_free_tail(rom, me.sb); sp.set_area(me.sb, f + 1, me.sb * 0x4000 + 0x4000)
    gio_gone, blue_hide = FL.new(), FL.new()
    lo = me.objs[0][0]; lx, ly = lo[2] - 4, lo[1] - 4
    assert lo[0] == SPR_BLUE
    lo[11] = blue_hide & 0xFF; lo[12] = blue_hide >> 8
    tm27 = P12.tm_item(27)
    gv = len(me.objs) + 2                      # object id of Giovanni (appended below)
    texts = {'gi': T(0x742FC), 'gw': T(0x74388),
             'gb': encode('{00}<PLAYER>は　サカキから<LINE>グりーンバッジを　もらった！'),
             'ginfo': T(0x74438), 'gtm': b'\x00' + T(0x744C7)[2:], 'gfull': T(0x74525), 'gbye': T(0x743C7)}
    a = Asm(sp.here(0x62))
    a.label('gio'); a.faceplayer(); a.opentext(); a.writetext('gi'); a.waitbutton(); a.closetext()
    a.winlosstext('gw', 0); a.loadtrainer(GIOVANNI, gio_party); a.startbattle(); a.reloadmapafterbattle()
    a.opentext(); a.writetext('gb'); a.playsound(0x009C); a.waitsfx(); a.setflag(ENGINE_EARTH)
    a.writetext('ginfo'); a.promptbutton(); a.verbosegiveitem(tm27, 1); a.iffalse('g_full')
    a.writetext('gtm'); a.waitbutton(); a.sjump('g_bye')
    a.label('g_full'); a.writetext('gfull'); a.waitbutton()
    a.label('g_bye'); a.writetext('gbye'); a.waitbutton(); a.closetext()
    a.disappear(gv); a.setevent(gio_gone); a.end()
    a.label('vg_cb'); a.checkevent(EV_HOF); a.iftrue('vg_post')
    a.setevent(blue_hide); a.endcallback()
    a.label('vg_post'); a.clearevent(blue_hide); a.setevent(gio_gone); a.endcallback()
    for k, v in texts.items():
        a.label(k); a.raw(P12.text(v))
    base = a.base; assert sp.put(0x62, a.done()) == base
    assert me.add_object(SPR_GIOVANNI, lx, ly, P12.FACE['DOWN'], ('far', 0x62, a.labels['gio']), flag=gio_gone) + 1 == gv
    me.callbacks.append((2, ('far', 0x62, a.labels['vg_cb'])))
    e = Asm(sp.here(me.sb)); e.bank = me.sb
    me.write(e, sp); eb = e.base; blob = e.done(); assert sp.put(me.sb, blob) == eb; me.install(e)
    log.append('ViridianGym: Giovanni + new events at %X:%04X (%d bytes)' % (me.sb, eb, len(blob)))

    # ================= outdoor sprite lists: every NPC sprite on an outdoor map must be in its group's list
    # (otherwise it is drawn with another sprite's graphics).  Unused entries (Will / Karen first) are replaced.
    fix_outdoor_sprites(rom, log)

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
