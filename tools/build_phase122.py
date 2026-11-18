#!/usr/bin/env python3
"""Phase 122: the gym guides teach the leader's Red TM move (2026-11-19 request 「トレーナーやジムリーダーなどから
わざマシンをもらう場合で赤にないものだけは、ジムリーダーから勝ったら、入口にいる案内？の人から教えてもらえるようにして
／ジムリーダーからもらうわざマシンはそのまま／一回そのジムリーダーに勝って外にでようとしたら、呼び止められてその人が
近寄ってくる感じ／その場でもし覚えなくてもはなしかければ何度教えてもらえるようにして」).
 The Kanto leaders give Crystal's TM of Red's number (kept).  Where Red's TM move is not a Crystal TM, the gym guide
 at the entrance teaches Red's move after the leader is beaten:
   Brock: Bide (Red TM34) / Misty: BubbleBeam (TM11) / Lt. Surge: Thunderbolt (TM24) / Erika: Mega Drain (TM21) /
   Sabrina: Psywave (TM46) / Giovanni: Fissure (TM27).   (Koga's Toxic and Blaine's Fire Blast are Crystal TMs too.)
 * Leaving the gym the first time after the badge (the tiles in front of the doors): "<PLAYER>! wait!", the guide
   walks up to the player and offers the move (yes: the move tutor's party menu; no: "talk to me any time").
 * Afterwards talking to the guide offers it again, any number of times.  Before the badge: the guide's Red lines.
 * Celadon Gym has no guide in Red: a guide stands near the entrance only once Erika is beaten.
 * Who can learn: Red's TM/HM table for that TM (pokered base stats), through Crystal's move tutor (special MoveTutor
   with the move number in wScriptVar: GetMoveTutorMove passes numbers >= 4 through; the predef CanLearnTMHMMove goes
   to a wrapper that answers from these lists and leaves every other move to Crystal's routine).
usage: build_phase122.py IN.gbc OUT.gbc OUT.ips
"""
import os, sys, re, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'play'))
from lib import *
from portlib import Space
from evedit import MapEvents
from jpchar import encode

CODE_BANK, DATA_BANK = 0x20, 0x21
W_PUTATIVE_MOVE, W_CUR_PARTY_SPECIES = 0xD293, 0xD0C8
CAN_LEARN = (0x04, 0x55D3); PREDEF_CAN_LEARN = 0x8595
GET_TUTOR_MOVE = 0x491F7
SPECIAL_MOVE_TUTOR = 131
SPR_GUIDE = 0x48
FIRST_FLAG = 0xA16                       # phase 112 used 0xA15 (EXT_FLAGS index 533)
GYMS = [  # map, leader, badge engine flag, Red move constant, move name, Red TM number
    ('PewterGym', 'タケシ', 0x23, 'BIDE', 'がまん', 34),
    ('CeruleanGym', 'カスミ', 0x24, 'BUBBLEBEAM', 'バブルこうせん', 11),
    ('VermilionGym', 'マチス', 0x25, 'THUNDERBOLT', '10まんボルト', 24),
    ('CeladonGym', 'エリカ', 0x26, 'MEGA_DRAIN', 'メガドレイン', 21),
    ('SaffronGym', 'ナツメ', 0x28, 'PSYWAVE', 'サイコウェーブ', 46),
    ('ViridianGym', 'サカキ', 0x2A, 'FISSURE', 'じわれ', 27)]
CELADON_GUIDE_AT = (7, 15)
DV = {'D': (0, 1), 'U': (0, -1), 'L': (-1, 0), 'R': (1, 0)}
DIRN = {'D': 0, 'U': 1, 'L': 2, 'R': 3}
OPP = {'D': 'U', 'U': 'D', 'L': 'R', 'R': 'L'}


def move_ids():
    d = {}; i = 0
    for l in open(PC + '/constants/move_constants.asm'):
        s = l.strip()
        if s.startswith('const_def'): i = 0
        m = re.match(r'const (\w+)', s)
        if m: d[m.group(1)] = i; i += 1
    return d


def red_learners(move):
    PR = os.path.join(os.path.dirname(PC), 'pokered')
    dex = {}; i = 0
    for l in open(PR + '/constants/pokedex_constants.asm'):
        m = re.match(r'\s*const (DEX_\w+)', l)
        if m: i += 1; dex[m.group(1)] = i
    out = []
    for f in glob.glob(PR + '/data/pokemon/base_stats/*.asm'):
        t = open(f).read()
        d = re.search(r'db (DEX_\w+)', t).group(1)
        tm = re.search(r'tmhm (.*?)\n\s*; end', t, re.S)
        moves = {x.strip() for x in tm.group(1).replace('\\', ' ').split(',')} if tm else set()
        if move in moves: out.append(dex[d])
    return sorted(out)


def T(s): return b'\x00' + encode(s + '<DONE>')


def path(grid, walk, block, start, goals):
    """BFS: shortest list of directions from start to any goal tile"""
    from collections import deque
    q = deque([start]); prev = {start: None}
    while q:
        p = q.popleft()
        if p in goals:
            out = []
            while prev[p]: d, p = prev[p]; out.append(d)
            return out[::-1]
        for d, (dx, dy) in DV.items():
            n = (p[0] + dx, p[1] + dy)
            if n in prev or not (0 <= n[1] < len(grid) and 0 <= n[0] < len(grid[0])): continue
            if grid[n[1]][n[0]] not in walk or n in block: continue
            prev[n] = (d, p); q.append(n)
    return None


def main():
    src, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src, 'rb').read())
    log = []
    import bot
    from mapdb import DB
    db = DB(src)
    MV = move_ids()
    sp = Space(rom)
    for b in (CODE_BANK, DATA_BANK):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 16, b * 0x4000 + 0x4000)

    # ---- the tutor: GetMoveTutorMove passes move numbers >= 4 through (1-3: Crystal's three tutor moves)
    o = GET_TUTOR_MOVE
    old = bytes.fromhex('fa dd c2 fe 01 28 07 fe 02 28 06 3e 3a c9 3e 35 c9 3e 55 c9'.replace(' ', ''))
    assert rom[o:o + 20] == old, rom[o:o + 20].hex(' ')
    rom[o:o + 20] = bytes.fromhex('faddc2 fe04 d0 fe02 3e55 c8 3803 3e3a c9 3e35 c9 00'.replace(' ', ''))
    # ---- who can learn: the predef CanLearnTMHMMove -> a wrapper with Red's lists
    entries = []
    for gym, leader, badge, mv, mname, tm in GYMS: entries.append((MV[mv], red_learners(mv)))
    a = Asm(sp.here(CODE_BANK))
    w16 = lambda v: bytes([v & 0xFF, v >> 8])
    a.label('wrap'); a.raw(bytes([0xD5, 0xFA]) + w16(W_PUTATIVE_MOVE) + bytes([0x57, 0x21])); a.dw('mtab')
    a.label('l1'); a.raw(bytes([0x2A, 0xA7, 0xCA])); a.dw('orig'); a.raw(bytes([0xBA, 0xCA])); a.dw('found')
    a.raw(bytes([0x23, 0x23, 0xC3])); a.dw('l1')
    a.label('found'); a.raw(bytes([0x2A, 0x66, 0x6F, 0xFA]) + w16(W_CUR_PARTY_SPECIES) + bytes([0x57]))
    a.label('l2'); a.raw(bytes([0x2A, 0xFE, 0xFF, 0xCA])); a.dw('no'); a.raw(bytes([0xBA, 0xC2])); a.dw('l2')
    a.raw(bytes([0x0E, 0x01, 0xD1, 0xC9]))
    a.label('no'); a.raw(bytes([0x0E, 0x00, 0xD1, 0xC9]))
    a.label('orig'); a.raw(bytes([0xD1, 0x3E, CAN_LEARN[0], 0x21]) + w16(CAN_LEARN[1]) + bytes([0xCF, 0xC9]))
    a.label('mtab')
    for k, (m, lst) in enumerate(entries): a.db(m); a.dw('ls%d' % k)
    a.db(0)
    for k, (m, lst) in enumerate(entries): a.label('ls%d' % k); a.raw(bytes(lst) + b'\xff')
    base = a.base; blob = a.done(); assert sp.put(CODE_BANK, blob) == base
    assert rom[PREDEF_CAN_LEARN:PREDEF_CAN_LEARN + 3] == bytes([CAN_LEARN[1] & 0xFF, CAN_LEARN[1] >> 8, CAN_LEARN[0]])
    rom[PREDEF_CAN_LEARN:PREDEF_CAN_LEARN + 3] = w16(a.labels['wrap']) + bytes([CODE_BANK])
    log.append('tutor: GetMoveTutorMove passes >= 4; CanLearnTMHMMove -> %02X:%04X (%d bytes, lists %s)'
               % (CODE_BANK, a.labels['wrap'], len(blob), [len(l) for m, l in entries]))

    # ---- the gyms
    flag = FIRST_FLAG
    for gym, leader, badge, mv, mname, tm in GYMS:
        me = MapEvents(rom, gym)
        k = db.ids[gym] if hasattr(db, 'ids') else None
        m = [mm for kk, mm in db.maps.items() if mm['attr'] == me.a['attr_off']][0]
        grid = bot.grid_of(db.r, m['hdr'])
        called = flag; flag += 1
        a = Asm(sp.here(DATA_BANK)); a.bank = DATA_BANK
        gi = [i for i, (o, r) in enumerate(me.objs) if o[0] == SPR_GUIDE]
        if gym == 'CeladonGym':
            assert not gi
            hide = flag; flag += 1
            gid = me.add_object(SPR_GUIDE, *CELADON_GUIDE_AT, 0x06, 'guide', flag=hide, pal_type=0x90) + 1   # (object 1 is the follower)
            gpos = CELADON_GUIDE_AT; gref = None
            me.callbacks.append((2, 'cb_obj'))
            a.label('cb_obj'); a.checkflag(badge); a.iffalse('cb_hide'); a.clearevent(hide); a.endcallback()
            a.label('cb_hide'); a.setevent(hide); a.endcallback()
        else:
            assert len(gi) == 1, (gym, gi)
            o, gref = me.objs[gi[0]]; gid = gi[0] + 2                 # (object 1 is the follower: map objects from 2)
            gpos = (o[2] - 4, o[1] - 4); me.objs[gi[0]][1] = 'guide'
        block = {(ob[2] - 4, ob[1] - 4) for ob, r in me.objs} - {gpos}
        doors = [(w[1], w[0]) for w in me.warps][:2]                 # (x, y): the two door tiles
        texts = {'call': T('<PLAYER>！　ちょっと　まって！'),
                 'ask1': T(leader + 'に　かった　おいわいに<LINE>わざを　ひとつ　おしえて　あげよう！<PARA>'
                           + mname + 'を<LINE>おぼえさせるかい？'),
                 'ask2': T('<PLAYER>！<LINE>' + mname + 'を　おぼえさせるかい？'),
                 'ok': T('これで　' + mname + 'も<LINE>ばっちりだ！<PARA>また　いつでも<LINE>おしえて　あげるからな！'),
                 'no': T('そうか<……><PARA>おぼえさせたく　なったら<LINE>いつでも　はなしかけてくれ！')}
        # the teaching (scall): opentext is already open
        a.label('teach'); a.yesorno(); a.iffalse('t_no')
        a.db(0x15, MV[mv]); a.special(SPECIAL_MOVE_TUTOR)                 # setval move ; special MoveTutor
        a.ifequal(0, 't_ok')
        a.label('t_no'); a.writetext('no'); a.waitbutton(); a.closetext(); a.end()
        a.label('t_ok'); a.writetext('ok'); a.waitbutton(); a.closetext(); a.end()
        # talking to the guide
        a.label('guide'); a.checkflag(badge)
        if gref is not None: a.iffalse('g_red')
        a.faceplayer(); a.opentext(); a.setevent(called); a.writetext('ask2'); a.scall('teach'); a.end()
        if gref is not None:
            a.label('g_red')
            if gref[0] == 'far': a.farsjump(gref[1], gref[2])
            else: raise ValueError(gref)
        # leaving: the tiles in front of the doors
        for j, (dx_, dy_) in enumerate(doors):
            tx, ty = dx_, dy_ - 1
            assert grid[ty][tx] in bot.WALK, (gym, tx, ty)
            goals = {}
            for d, (ddx, ddy) in DV.items():
                g = (tx + ddx, ty + ddy)
                if d == 'D': continue
                if 0 <= g[1] < len(grid) and 0 <= g[0] < len(grid[0]) and grid[g[1]][g[0]] in bot.WALK and g not in block:
                    goals[g] = OPP[d]                                   # the guide stands at g and faces the player
            pth = path(grid, bot.WALK, block | {(tx, ty)}, gpos, set(goals))
            assert pth is not None, (gym, gpos, (tx, ty))
            end = gpos
            for d in pth: end = (end[0] + DV[d][0], end[1] + DV[d][1])
            gface = goals[end]; pface = OPP[gface]
            L = 'lv%d' % j
            me.coords.append((0xFF, ty, tx, L))
            a.label(L); a.checkflag(badge); a.iffalse(L + 'x'); a.checkevent(called); a.iftrue(L + 'x')
            if gym == 'CeladonGym': a.appear(gid)
            # (no showemote: in this MOD the emote's tiles overwrite the follower's until the player moves)
            a.opentext(); a.writetext('call'); a.waitbutton(); a.closetext()
            if pth: a.applymovement(gid, L + 'm')
            a.turnobject(gid, DIRN[gface]); a.turnobject(0, DIRN[pface])
            a.setevent(called)
            a.opentext(); a.writetext('ask1'); a.scall('teach')
            if pth: a.applymovement(gid, L + 'b')
            a.label(L + 'x'); a.end()
            a.label(L + 'm'); a.db(*[0x0C + DIRN[d] for d in pth]); a.db(0x47)
            a.label(L + 'b'); a.db(*[0x0C + DIRN[OPP[d]] for d in reversed(pth)]); a.db(0x47)
            log.append('  %s: (%d,%d) guide %s -> %s' % (gym, tx, ty, gpos, ''.join(pth) or '-'))
        for kk, v in texts.items(): a.label(kk); a.raw(v)
        me.write(a, sp)
        base = a.base; blob = a.done(); assert sp.put(DATA_BANK, blob) == base
        me.install(a)
        log.append('%s: %s %s (Red TM%02d), events %02X:%04X (%d bytes), flag %X' % (gym, leader, mname, tm, DATA_BANK, base, len(blob), called))

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
