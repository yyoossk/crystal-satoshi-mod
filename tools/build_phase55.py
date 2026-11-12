#!/usr/bin/env python3
"""Phase 55: the Kanto gyms as in Red (found by the start-to-finish playthrough).
 * Gym leaders before the Johto League (Brock, Misty, Lt. Surge, Erika, Sabrina): Red's lines (the challenge, the
   defeat, the badge's effect, the TM and its use, the line afterwards) instead of Crystal's post-game lines, which
   spoke of a challenger "from Johto"; each gives Red's TM (Crystal's TM with the same number, like the TMs found in
   Kanto; the TM's use is described for that move); with a full bag the TM is given when talked to again.
   After the Johto League: Crystal's lines and phase 50's rematches as before.
 * Fuchsia Gym: Koga (Red's leader, Pikachu version's party) until the Johto League, then Janine as in Crystal.
   Koga is shown with Crystal's Koga picture, called ジムリーダー, with the Kanto gym leader music.
 * Gym guides (Pewter, Cerulean, Vermilion, Fuchsia, Saffron, Viridian): Red's lines (Crystal's spoke of Johto, or of
   Misty being away); Viridian's guide stands in the gym as in Red.
 * Viridian Gym: Giovanni's TM27 is described as Crystal's TM27 (おんがえし).
 * After the Kanto Hall of Fame: Lavender Town's doors led nowhere (the warp table used after the Hall of Fame was
   read from a bank the town's events had left) and the Vermilion port passage's exits led to wrong places in Red's
   Vermilion City: the after-Hall-of-Fame warp tables are rebuilt from the current warps (Lavender's tower door ->
   Crystal's Radio Tower, the passage's dock door -> Crystal's port).
 * Ported maps (Red's ladders and stairs: Mt. Moon, Rock Tunnel, Seafoam Islands, Victory Road, Cerulean Cave,
   Silph Co., Pokémon Tower, ...): arriving on a ladder whose tile below is a wall no longer pushes the player one
   step down into the wall (stuck there); as in Red the player stands on the ladder (Crystal's ladder collision).
usage: build_phase55.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode, decode
import build_phase12 as P12
import build_phase13 as P13
import build_phase50 as P50
import portmaps as PM
import redtexts as RT
from evedit import MapEvents, copy_text

PB = 0x2E                          # scripts and texts (free from 6342; the test ROM's script area is 7F00-)
PB_END = 0x7F00
FIRST_FLAG = 503                   # 502: phase 52
EV_BEAT_E4 = 0x44                  # Johto Elite Four beaten
SFX_ITEM, SFX_GET_BADGE = 0x0001, 0x009C
KOGA, BROCK_CLS = 0x0F, 0x11
SPR_KOGA, SPR_JANINE, SPR_GUIDE = 0x21, 0x0A, 0x48
W_OTHER_CLASS, W_OTHER_ID = 0xD260, 0xD262
HOME_HOOKS = 0x3F80                # home bank: free 3F7F-3FFF
PARA = 0x51


def R(o):
    """a JP Red text body ({00} ... without its terminator)"""
    return bytes(RT.raw(o))


def nopara(b):
    return b[:1] + b[2:] if b[1] == PARA else b


def E(s):
    return encode('{00}' + s).rstrip(b'\x50')


def cut(b, s):
    k = encode(s).rstrip(b'\x50'); i = b.find(k); assert i > 0, s
    return b[:i]


def text(b): return bytes(b) + b'\x57'


# The TMs' moves are Crystal's (same number as Red's TM); Red's lines describe Red's move: rewritten for the move.
BROCK_TM = (cut(nopara(R(0x5C8B3)), '{5C}34には') +
            encode('{5C}34には<CONT>いばる　が　はいっている！<PARA>あいてを　おこらせて<LINE>こうげきりょくを　ぐーんと　あげるが<CONT>'
                   'こんらん　させて　しまう！<CONT>おもしろい　わざだ！').rstrip(b'\x50'))
MISTY_TM = E('{5C}11は　にほんばれを<LINE><POKEMON>に　おしえるの<PARA>ひざしが　つよく　なって<LINE>'
             'ほのおの　わざが<CONT>つよく　なるのよ！')
ERIKA_TM = E('{5C}21の　なかは<LINE>やつあたり　です<PARA><POKEMON>が　なついて　いない　ほど<LINE>'
             'いりょくが　あがる<CONT>ふしぎな　わざ　です')
SABRINA_TM = E('{5C}46は　どろぼう！<LINE>あいての　もちものを<CONT>うばいとる　わざよ！')
GIOVANNI_TM = E('{5C}27は　おんがえし　だ！<LINE><POKEMON>が　なついて　いるほど<CONT>いりょくが　あがる　わざだ！<PARA>'
                'おれが　むかし<……>　ここで<LINE><POKEMON>　ジムを　やってる　とき<CONT>つくった　ものだ<……>')

# map, leader sprite, leader name, badge name, pre, defeat (cut before), badge info, TM intro, TM, TM text,
# no room, after
LEADERS = [
    dict(map='PewterGym', spr=0x1A, name='タケシ', badge='グレーバッジ', pre=R(0x5C78F),
         defeat=cut(R(0x5C95D), '<PARA><PLAYER>は'), info=nopara(R(0x5C9B0)), intro=R(0x5C885), tm=34,
         tmtext=BROCK_TM, full=R(0x5C950), after=R(0x5C81E)),
    dict(map='CeruleanGym', spr=0x1D, name='カスミ', badge='ブルーバッジ', pre=R(0x5CF13),
         defeat=R(0x5D069), info=R(0x5CFB8), intro=None, tm=11, tmtext=MISTY_TM, full=R(0x5D05E), after=MISTY_TM),
    dict(map='VermilionGym', spr=0x1F, name='マチス', badge='オレンジバッジ', pre=R(0x5D7E8),
         defeat=R(0x5D98A), info=R(0x5D8C2), intro=None, tm=24, tmtext=nopara(R(0x5D93F)), full=R(0x5D96E),
         after=R(0x5D86B)),
    dict(map='CeladonGym', spr=0x20, name='エりカ', badge='レインボーバッジ', pre=R(0x49195),
         defeat=R(0x4922F), info=R(0x492AC), intro=None, tm=21, tmtext=ERIKA_TM, full=R(0x4936A), after=R(0x4926C)),
    dict(map='SaffronGym', spr=0x22, name='ナツメ', badge='ゴールドバッジ', pre=R(0x5E5A4),
         defeat=R(0x5E617), info=R(0x5E6BA), intro=None, tm=46, tmtext=SABRINA_TM, full=R(0x5E783),
         after=R(0x5E67A)),
]
KOGA_L = dict(map='FuchsiaGym', spr=SPR_JANINE, name='キョウ', badge='ピンクバッジ', pre=R(0x75998),
              defeat=R(0x75A0E), info=R(0x75A7B), intro=None, tm=6, tmtext=nopara(R(0x75AF2)), full=R(0x75B2C),
              after=R(0x75A32))
KOGA_PARTY = [(44, 'VENONAT'), (46, 'VENONAT'), (48, 'VENONAT'), (50, 'VENOMOTH')]       # Pikachu version

# guide texts: map -> (before the leader is beaten, after)
GUIDES = {'PewterGym': None, 'CeruleanGym': (0x5D17D, 0x5D202), 'VermilionGym': (0x5DB59, 0x5DC08),
          'FuchsiaGym': (0x75E1B, 0x75E92), 'SaffronGym': (0x5EAE7, 0x5EB59), 'ViridianGym': (0x747D5, 0x74856)}


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom); log = []
    def r16(o): return rom[o] | rom[o + 1] << 8
    f, n = bank_free_tail(rom, PB); sp.set_area(PB, f + 1, PB * 0x4000 + PB_END - 0x4000)
    FL = PM.Flags(FIRST_FLAG)
    a = Asm(sp.here(PB)); a.bank = PB; texts = {}
    def T(key, b): texts[key] = text(b); return key

    def trainer_flags(name):
        me = MapEvents(rom, name); out = []
        for o, ref in me.objs:
            if ref[0] == 'keep': out.append(r16(fo(me.sb, ref[1])))
        return out

    def obj_script(name, spr):
        me = MapEvents(rom, name)
        for o, ref in me.objs:
            if o[0] == spr:
                assert ref[0] == 'far'; return me, ref[1], ref[2]
        raise KeyError((name, spr))

    def leader_script(L, k, cls, idx, badge_flag, setevents, orig_jump, opens):
        """Red's leader: before the Johto League; orig_jump = (bank, addr) of the old behaviour"""
        P = 'L%d' % k; got_tm = FL.new()
        a.label(P)
        if opens: a.faceplayer(); a.opentext()
        a.checkevent(EV_BEAT_E4); a.iftrue(P + 'old')
        a.checkflag(badge_flag); a.iftrue(P + 'post')
        a.writetext(T(P + 'pre', L['pre'])); a.waitbutton(); a.closetext()
        a.winlosstext(T(P + 'def', L['defeat']), 0); a.loadtrainer(cls, idx); a.startbattle(); a.reloadmapafterbattle()
        for e in setevents: a.setevent(e)
        a.opentext()
        a.writetext(T(P + 'got', E('<PLAYER>は　%sから<LINE>%sを　もらった！' % (L['name'], L['badge']))))
        a.playsound(SFX_GET_BADGE); a.waitsfx(); a.setflag(badge_flag)
        a.writetext(T(P + 'info', L['info'])); a.promptbutton()
        if L['intro']: a.writetext(T(P + 'intro', L['intro'])); a.promptbutton()
        a.sjump(P + 'give')
        a.label(P + 'post'); a.checkevent(got_tm); a.iffalse(P + 'give')
        a.writetext(T(P + 'after', L['after'])); a.waitbutton(); a.closetext(); a.end()
        a.label(P + 'give'); a.db(0x1F, P12.tm_item(L['tm']), 1); a.iffalse(P + 'full')     # giveitem
        a.setevent(got_tm)
        a.writetext(T(P + 'gtm', E('<PLAYER>は　%sから<LINE>{5C}%02dを　もらった！' % (L['name'], L['tm']))))
        a.playsound(SFX_ITEM); a.waitsfx()
        a.writetext(T(P + 'tmt', L['tmtext'])); a.waitbutton(); a.closetext(); a.end()
        a.label(P + 'full'); a.writetext(T(P + 'fullt', L['full'])); a.waitbutton(); a.closetext(); a.end()
        a.label(P + 'old'); a.farsjump(*orig_jump)
        return P

    # ---------------------------------------------------------------- Brock .. Sabrina
    patches = []
    for k, L in enumerate(LEADERS):
        me, sb, sa = obj_script(L['map'], L['spr'])
        o = fo(sb, sa)
        # faceplayer / opentext / farsjump 66:hook (phase 50) / nop nop / writetext / waitbutton / closetext /
        # winlosstext / loadtrainer c,i / startbattle / reloadmapafterbattle / setevent... / opentext
        assert rom[o:o + 3] == bytes([0x6A, 0x47, 0x04]) and rom[o + 3] == P50.PB, (L['map'], rom[o:o + 8].hex())
        hook = (rom[o + 3], r16(o + 4))
        q = o + 8; assert rom[q] == 0x4C and rom[q + 3:q + 6] == bytes([0x53, 0x49, 0x63]), L['map']
        q += 10; assert rom[q] == 0x5D; cls, idx = rom[q + 1], rom[q + 2]
        q += 3; assert rom[q:q + 2] == bytes([0x5E, 0x5F]); q += 2
        sev = []
        while rom[q] == 0x33: sev.append(r16(q + 1)); q += 3
        sev += [t for t in trainer_flags(L['map']) if t not in sev]       # Red: the gym's trainers count as beaten
        # the badge flag: phase 50's hook starts with the original "checkflag ENGINE_xBADGE"
        h = fo(*hook); assert rom[h] == 0x34; badge = r16(h + 1)
        P = leader_script(L, k, cls, idx, badge, sev, hook, False)
        patches.append((o + 2, P))
        log.append('%s: %s (party %X/%d, badge flag %X, TM%02d, sets %s)' % (L['map'], L['name'], cls, idx, badge,
                                                                            L['tm'], ' '.join('%X' % e for e in sev)))

    # ---------------------------------------------------------------- Fuchsia: Koga until the Johto League
    grp = P13.read_groups7e(rom)
    grp[KOGA - 1].append([encode('キョウ@'),
                          b'\x00' + b''.join(bytes([lv, PM.MON[s]]) for lv, s in KOGA_PARTY) + b'\xff'])
    koga_id = len(grp[KOGA - 1])
    log.append('trainer parties (bank 7E free %d); Koga = class %X party %d' % (P13.write_groups7e(rom, grp), KOGA,
                                                                                 koga_id))
    me = MapEvents(rom, 'FuchsiaGym')
    jo = [i for i, (o, ref) in enumerate(me.objs) if o[0] == SPR_JANINE][0]
    jref = me.objs[jo][1]; jx, jy = me.objs[jo][0][2] - 4, me.objs[jo][0][1] - 4
    o = fo(jref[1], jref[2])
    # farsjump 66:hook / nop nop / applymovement / faceplayer / opentext / writetext / waitbutton / closetext /
    # winlosstext / loadtrainer / startbattle / reloadmapafterbattle / setevent...
    assert rom[o] == 0x04 and rom[o + 1] == P50.PB, rom[o:o + 8].hex()
    hook = (rom[o + 1], r16(o + 2)); h = fo(*hook); assert rom[h] == 0x34; soul = r16(h + 1)
    q = rom.index(bytes([0x5E, 0x5F]), o) + 2; sev = []
    while rom[q] == 0x33: sev.append(r16(q + 1)); q += 3
    sev += [t for t in trainer_flags('FuchsiaGym') if t not in sev]
    koga_hide, janine_hide = FL.new(), FL.new()
    me.objs[jo][0][11] = janine_hide & 0xFF; me.objs[jo][0][12] = janine_hide >> 8
    KP = leader_script(KOGA_L, 9, KOGA, koga_id, soul, sev, (jref[1], jref[2]), True)
    a.label('fg_cb'); a.checkevent(EV_BEAT_E4); a.iftrue('fg_johto')
    a.setevent(janine_hide); a.clearevent(koga_hide); a.endcallback()
    a.label('fg_johto'); a.clearevent(janine_hide); a.setevent(koga_hide); a.endcallback()
    log.append('FuchsiaGym: Koga (badge flag %X, sets %s)' % (soul, ' '.join('%X' % e for e in sev)))

    # ---------------------------------------------------------------- gym guides
    guide_patches = []
    for name, tx in GUIDES.items():
        me2 = me if name == 'FuchsiaGym' else MapEvents(rom, name)
        gi = [i for i, (o_, ref) in enumerate(me2.objs) if o_[0] == SPR_GUIDE][0]
        go, gref = me2.objs[gi]
        G = 'G_' + name
        beat = {'PewterGym': None}.get(name)
        a.label(G); a.faceplayer(); a.opentext()
        # "beaten": the badge of the gym
        if name == 'ViridianGym': badge = 0x2A
        elif name == 'FuchsiaGym': badge = soul
        else:
            L = [L_ for L_ in LEADERS if L_['map'] == name][0]
            badge = [int(x.split('badge flag ')[1].split(',')[0], 16) for x in log if x.startswith(name + ':')][0]
        a.checkflag(badge); a.iftrue(G + 'w')
        if name == 'PewterGym':
            a.writetext(T(G + 'q', R(0x5CACD))); a.yesorno(); a.iffalse(G + 'no')
            a.writetext(T(G + 'y', R(0x5CB28))); a.promptbutton(); a.sjump(G + 'adv')
            a.label(G + 'no'); a.writetext(T(G + 'n', R(0x5CB90))); a.promptbutton()
            a.label(G + 'adv'); a.writetext(T(G + 'a', R(0x5CB3B))); a.waitbutton(); a.closetext(); a.end()
            a.label(G + 'w'); a.writetext(T(G + 'b', R(0x5CBA7))); a.waitbutton(); a.closetext(); a.end()
        else:
            a.writetext(T(G + 'a', R(tx[0]))); a.waitbutton(); a.closetext(); a.end()
            a.label(G + 'w'); a.writetext(T(G + 'b', R(tx[1]))); a.waitbutton(); a.closetext(); a.end()
        if name == 'FuchsiaGym':
            me2.objs[gi][1] = ('far', PB, G)            # (the events are rewritten below)
        else:
            assert gref[0] == 'far'
            guide_patches.append((fo(gref[1], gref[2]), G))
            if name == 'ViridianGym':                   # Crystal: shown with Blue only; Red: always there
                ev = parse_events(rom, me2.sb, me2.a['events'])
                op = [p for p, ob in ev['objs'] if ob[0] == SPR_GUIDE][0]
                rom[op + 11] = 0xFF; rom[op + 12] = 0xFF
        log.append('%s: guide (Red)' % name)

    for k_, v in texts.items():
        a.label(k_); a.raw(v)
    base = a.base; blob = a.done(); assert sp.put(PB, blob) == base
    log.append('scripts and texts at %X:%04X-%04X' % (PB, base, base + len(blob)))
    for o, P in patches:
        t = a.labels[P]; rom[o:o + 4] = bytes([0x04, PB, t & 0xFF, t >> 8])
    for o, G in guide_patches:
        assert len(rom[o:o + 4]) == 4
        t = a.labels[G]; rom[o:o + 4] = bytes([0x04, PB, t & 0xFF, t >> 8])

    # Fuchsia's events (moved to a bank with room: Koga's object, the callback)
    me.callbacks.append((2, ('far', PB, a.labels['fg_cb'])))
    me.add_object(SPR_KOGA, jx, jy, 6, ('far', PB, a.labels[KP]), flag=koga_hide)
    for o_, ref in me.objs:
        if isinstance(ref, tuple) and ref[0] == 'far' and ref[1] == PB and isinstance(ref[2], str):
            pass
    me.objs = [[o_, ('far', PB, a.labels[ref[2]]) if (isinstance(ref, tuple) and ref[0] == 'far' and
                                                       isinstance(ref[2], str)) else ref] for o_, ref in me.objs]
    EB = 0x2C
    f, n = bank_free_tail(rom, EB); sp.set_area(EB, f + 1, EB * 0x4000 + 0x4000)
    e = Asm(sp.here(EB)); e.bank = EB
    me.write(e, sp); eb = e.base; blob = e.done(); assert sp.put(EB, blob) == eb; me.install(e)
    log.append('FuchsiaGym: events at %X:%04X (%d bytes)' % (EB, eb, len(blob)))

    # Koga: "ジムリーダー" (GetTrainerClassName 0E:554B) and the Kanto gym leader music (IsKantoGymLeader 0F:5116)
    h1 = HOME_HOOKS
    c1 = bytes([0x79, 0xFE, KOGA, 0x20, 0x0A,                       # ld a,c / cp KOGA / jr nz,.x
                0xFA, W_OTHER_ID & 0xFF, W_OTHER_ID >> 8, 0xFE, koga_id,   # ld a,[wOtherTrainerID] / cp id
                0x79, 0x20, 0x02, 0x3E, BROCK_CLS,                  # ld a,c / jr nz,.x / ld a,BROCK
                0x21, 0x9A, 0xD4, 0xFE, 0x09, 0xC9])                # .x ld hl,wRivalName / cp RIVAL1 / ret
    assert c1[3] == 0x20 and len(c1) == 21
    c1 = bytearray(c1); c1[4] = 15 - 5                                # jr nz -> .x (offset 15)
    for b_ in (0x0E, 0x7E):                    # GetTrainerClassName, GetOTName (bank 0E and its copy in 7E)
        for ad in (0x554B, 0x5577):
            o = fo(b_, ad); assert rom[o:o + 6] == bytes([0x21, 0x9A, 0xD4, 0x79, 0xFE, 0x09])
            rom[o:o + 6] = bytes([0xCD, h1 & 0xFF, h1 >> 8, 0x00, 0x00, 0x00])
    o2 = fo(0x0F, 0x5116); assert rom[o2:o2 + 5] == bytes([0x21, 0x4F, 0x7F, 0x18, 0x03])
    h2 = h1 + len(c1)
    c2 = bytes([0xFA, W_OTHER_CLASS & 0xFF, W_OTHER_CLASS >> 8, 0xFE, KOGA, 0x20, 0x09,
                0xFA, W_OTHER_ID & 0xFF, W_OTHER_ID >> 8, 0xFE, koga_id, 0x20, 0x02, 0x37, 0xC9,
                0x21, 0x4F, 0x7F, 0xC3, 0x1E, 0x51])
    rom[o2:o2 + 5] = bytes([0xC3, h2 & 0xFF, h2 >> 8, 0x00, 0x00])
    assert all(b == 0 for b in rom[h1:h2 + len(c2)]) and h2 + len(c2) <= 0x4000
    rom[h1:h1 + len(c1)] = c1; rom[h2:h2 + len(c2)] = c2
    log.append('Koga: class name / music hooks at 00:%04X-%04X' % (h1, h2 + len(c2)))

    # Giovanni's TM27 text (phase 17, bank 62): the move of Crystal's TM27
    old = text(b'\x00' + R(0x744C7)[2:]); i = rom.find(old, 0x62 * 0x4000, 0x63 * 0x4000); assert i > 0
    new = text(GIOVANNI_TM); assert len(new) <= len(old)
    rom[i:i + len(new)] = new
    log.append("Giovanni's TM27 text (62:%04X)" % (i % 0x4000 + 0x4000))

    # ---------------------------------------------------------------- ladders of the ported tilesets
    TS = PM.Tilesets(rom, sp)
    
    FORCED = (0x71, 0x79, 0x7A, 0x7B)          # Crystal walks the player down after arriving on these
    WALKABLE = {0x00, 0x18, 0x14, 0x10}
    fixed = set()
    u = US.get(); grp_ptr = [rom[0x94000 + 2 * i] | rom[0x94001 + 2 * i] << 8 for i in range(26)]
    for g in range(26):
        n_ = (grp_ptr[g + 1] - grp_ptr[g]) // 9 if g < 25 else 160
        for m in range(n_):
            hdr = fo(0x25, grp_ptr[g]) + 9 * m
            if not (0 < rom[hdr] < 0x80): continue
            ts = rom[hdr + 1]
            if ts < 33 or ts >= TS.count(): continue
            try: at = attrs(rom, hdr)
            except Exception: continue
            if not (0x4000 <= at['events'] < 0x8000) or not (0 < at['w'] <= 80 and 0 < at['h'] <= 80): continue
            co = TS.coll_off(ts); bo = fo(at['blkbank'], at['blk']); w, h = at['w'], at['h']
            def cell(x, y):
                if not (0 <= x < 2 * w and 0 <= y < 2 * h): return None, None
                b_ = rom[bo + (y // 2) * w + x // 2]; q = (y % 2) * 2 + x % 2
                return co + 4 * b_ + q, rom[co + 4 * b_ + q]
            try: ev = parse_events(rom, at['scbank'], at['events'])
            except Exception: continue
            for _, wv in ev['warps']:
                y, x = wv[0], wv[1]
                o, c = cell(x, y)
                if o is None or c not in FORCED: continue
                _, below = cell(x, y + 1)
                if below in WALKABLE: continue
                rom[o] = 0x72; fixed.add((g + 1, m + 1, x, y))
    log.append('ladders: %d warps of ported maps no longer step down into a wall' % len(fixed))

    # ---------------------------------------------------------------- after-HoF warp tables (phase 12 / 16 switches)
    def cur_warps(name):
        a_ = attrs(rom, hdr_index(name)); ev = parse_events(rom, a_['scbank'], a_['events'])
        return a_['scbank'], [bytearray(w) for _, w in ev['warps']]
    for name, old_ptr, fn_ld, override in (
            ('LavenderTown', 0x72DA, 0x5EA4, {1: ('LavRadioTower1F', 1)}),
            ('VermilionPortPassage', 0x7F79, 0x6326, {4: ('VermilionPort', 1)})):
        sb_, ws = cur_warps(name)
        o = fo(0x78, fn_ld); assert rom[o] == 0x21 and r16(o + 1) == old_ptr, name
        for i, (mn, idx) in override.items():
            ws[i][2] = idx; ws[i][3], ws[i][4] = mapid(mn)
        f, n = bank_free_tail(rom, sb_)
        if sb_ not in sp.cur: sp.set_area(sb_, f + 1, sb_ * 0x4000 + 0x4000)
        na = sp.put(sb_, b''.join(bytes(w) for w in ws))
        rom[o + 1] = na & 0xFF; rom[o + 2] = na >> 8
        log.append('%s: warps after the Hall of Fame rebuilt (%X:%04X)' % (name, sb_, na))

    log.append('extended flags used up to %d' % FL.i)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    print('\n'.join(log))


if __name__ == '__main__':
    main()
