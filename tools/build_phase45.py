#!/usr/bin/env python3
"""Phase 45: the S.S. Anne leaves, and Shigeru walks away after the ship battle, as in Red / the Pikachu full-color hack.
When the player comes down the gangway onto the dock with HM01 (Cut), the music changes to Surfing, the ship sounds
its horn and sails off to the left, smoke drifting from its funnel (the lower part of the screen scrolls, Red's
raster effect, here through Crystal's LY overrides), then the player walks out of the dock.
(Phase 16's instant departure when walking up the dock is gone.)
usage: build_phase45.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from evedit import MapEvents
import build_phase17 as P17
import build_phase21 as P21
import build_phase28 as P28

BANK = 0x59
MUSIC_SURF, SFX_BOAT = 0x21, 0x1C
MUS_RIVAL, MUS_RIVAL_AFTER = 0x1F, 0x20
VAR_X, VAR_Y = 0x12, 0x13
WATER_TILE, WATER_ATTR = 0x14, 0x03          # the dock's water (tile, BG attribute)
SMOKE_TILE, SMOKE_VRAM = 0x3F, 0x83F0         # OBJ tile in VRAM bank 1 (free at the dock)
OAM = 0xC490                                  # shadow OAM entries 36-39
TILEMAP_R10, ATTRMAP_R10 = 0xC568, 0xCE95     # JP wTilemap / wAttrmap, screen row 10
SCRATCH = 0xD191                              # WRAM 5 (wMagnetTrain): smoke X, scroll, counters
DELAYFRAMES = 0x0468
H_LCDC, H_LYS, H_LYE, H_PAL = 0xC6, 0xC7, 0xC8, 0xE5
SMOKE = open(os.path.join(PY, 'gfx/overworld/smoke.2bpp'), 'rb').read()


class M:
    """machine code with labels (jr / jp / call / ld nn)"""
    def __init__(s, base): s.base = base; s.b = bytearray(); s.L = {}; s.fx = []
    def __call__(s, *v): s.b += bytes(v); return s
    def lab(s, n): s.L[n] = s.base + len(s.b); return s
    def jr(s, op, n): s.b.append(op); s.fx.append(('r', len(s.b), n)); s.b.append(0); return s
    def w(s, op, n):
        if op is not None: s.b.append(op)
        s.fx.append(('a', len(s.b), n)); s.b += b'\0\0'; return s
    def done(s):
        for k, o, n in s.fx:
            t = s.L[n]
            if k == 'a': s.b[o] = t & 0xFF; s.b[o + 1] = t >> 8
            else:
                d = t - (s.base + o + 1); assert -128 <= d < 128, n; s.b[o] = d & 0xFF
        return bytes(s.b)


def routines(base):
    m = M(base)
    sx, sd, se, sb = SCRATCH, SCRATCH + 1, SCRATCH + 2, SCRATCH + 3
    def lo(v): return v & 0xFF
    def hi(v): return v >> 8
    # ---- prep: the smoke tile, a white OBJ palette (7)
    m.lab('prep')
    m(0x3E, 1, 0xE0, 0x4F)                                           # VRAM bank 1
    m.w(0x21, 'smoke')(0x11, lo(SMOKE_VRAM), hi(SMOKE_VRAM), 0x0E, 16)
    m.lab('pl')(0xF3).lab('pw')(0xF0, 0x41, 0xE6, 0x02).jr(0x20, 'pw')(0x2A, 0x12, 0xFB, 0x13, 0x0D).jr(0x20, 'pl')
    m(0xAF, 0xE0, 0x4F)
    m(0xF0, 0x70, 0xF5, 0x3E, 0x05, 0xE0, 0x70)                      # WRAM 5
    m(0x21, 0xF8, 0xD0, 0x0E, 4).lab('pp')(0x36, 0xFF, 0x23, 0x36, 0x7F, 0x23, 0x0D).jr(0x20, 'pp')   # wOBPals2 #7
    m(0xF1, 0xE0, 0x70, 0x3E, 1, 0xE0, H_PAL, 0xC9)
    # ---- anim: Red's VermilionDockSSAnneLeavesScript loop
    m.lab('anim')
    m(0xF0, 0x70, 0xF5, 0x3E, 0x05, 0xE0, 0x70)
    m(0xAF, 0xE0, H_LYS, 0xE0, H_LYE)
    m(0x21, 0x00, 0xD1, 0x0E, 0x90, 0xAF).lab('f0')(0x22, 0x0D).jr(0x20, 'f0')        # LY overrides: SCX 0
    m(0x1E, 20).lab('pf')(0xD5).w(0xCD, 'wcol')(0xD1, 0x1C, 0x7B, 0xFE, 32).jr(0x20, 'pf')   # water in BG columns 20-31
    m(0x3E, 0x43, 0xE0, H_LCDC)                                      # overrides -> rSCX
    m(0x3E, 88, 0xEA, lo(sx), hi(sx), 0xAF, 0xEA, lo(sd), hi(sd), 0x3E, 8, 0xEA, lo(se), hi(se))
    m.lab('outer')
    m(0xFA, lo(sx), hi(sx), 0xD6, 16, 0xEA, lo(sx), hi(sx), 0x47, 0xC6, 8, 0x4F)      # smoke X -= 16 ; b = X, c = X + 8
    m(0x21, lo(OAM), hi(OAM))
    for y, xr in ((100, 0x70), (100, 0x71), (108, 0x70), (108, 0x71)):
        m(0x36, y, 0x23, xr, 0x23, 0x36, SMOKE_TILE, 0x23, 0x36, 0x0F, 0x23)          # Y, X, tile, VRAM 1 / palette 7
    m(0x3E, 16, 0xEA, lo(sb), hi(sb))
    m.lab('inner')
    m(0x21, lo(OAM + 1), hi(OAM + 1), 0x0E, 4).lab('dr')(0x34, 0x34, 0x23, 0x23, 0x23, 0x23, 0x0D).jr(0x20, 'dr')  # drift right
    m(0x0E, 8, 0xCD, lo(DELAYFRAMES), hi(DELAYFRAMES))
    m(0xFA, lo(sd), hi(sd), 0x3C, 0xEA, lo(sd), hi(sd), 0x47)
    m(0x21, 0x4F, 0xD1, 0x0E, 0x30).lab('ov')(0x70, 0x23, 0x0D).jr(0x20, 'ov')        # lines $50-$7F: SCX = d
    m(0x78, 0xE6, 0x07).jr(0x20, 'skip')(0x78, 0x0F, 0x0F, 0x0F, 0x3D, 0x5F).w(0xCD, 'wcol')   # a column scrolled out: water
    m.lab('skip')
    m(0xFA, lo(sb), hi(sb), 0x3D, 0xEA, lo(sb), hi(sb)).w(0xC2, 'inner')
    m(0xFA, lo(se), hi(se), 0x3D, 0xEA, lo(se), hi(se)).w(0xC2, 'outer')
    m(0xAF, 0xE0, H_LCDC)
    m(0x21, lo(OAM), hi(OAM), 0xAF, 0x0E, 16).lab('ho')(0x22, 0x0D).jr(0x20, 'ho')
    m(0x21, lo(TILEMAP_R10), hi(TILEMAP_R10), 0x0E, 120, 0x3E, WATER_TILE).lab('t1')(0x22, 0x0D).jr(0x20, 't1')
    m(0x21, lo(ATTRMAP_R10), hi(ATTRMAP_R10), 0x0E, 120, 0x3E, WATER_ATTR).lab('t2')(0x22, 0x0D).jr(0x20, 't2')
    m(0xF1, 0xE0, 0x70, 0xC9)
    # ---- wcol: e = BG column; rows 10-15 -> water (tile and attribute)
    m.lab('wcol')(0x21, 0x40, 0x99, 0x16, 0x00, 0x19, 0x06, 6)
    m.lab('wr')(0xAF, 0xE0, 0x4F, 0x0E, WATER_TILE).w(0xCD, 'vput')
    m(0x3E, 1, 0xE0, 0x4F, 0x0E, WATER_ATTR).w(0xCD, 'vput')
    m(0x7D, 0xC6, 0x20, 0x6F).jr(0x30, 'wn')(0x24).lab('wn')(0x05).jr(0x20, 'wr')
    m(0xAF, 0xE0, 0x4F, 0xC9)
    m.lab('vput')(0xF3).lab('vw')(0xF0, 0x41, 0xE6, 0x02).jr(0x20, 'vw')(0x71, 0xFB, 0xC9)
    m.lab('smoke')(*SMOKE)
    return m


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (BANK,):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    log = []

    # the dock (phase 16) and its flags
    pw = MapEvents(rom, 'VermilionPortPassage')
    dock = [(w[3], w[4]) for w in pw.warps if w[3] == G26][0]
    hh = GROUP26_END + 9 * (dock[1] - G26_COUNT - 1)
    da = attrs(rom, hh); sb_ = da['scbank']; dev = parse_events(rom, sb_, da['events'])
    c_ = dev['coords'][0][1]; o_ = fo(sb_, c_[4] | c_[5] << 8)
    assert rom[o_] == 0x31 and rom[o_ + 3] == 0x09 and rom[o_ + 6] == 0x31
    got_hm01 = r16(o_ + 1); gl = fo(sb_, r16(o_ + 4))
    assert rom[gl] == 0x31 and rom[gl + 3] == 0x09; ship_left = r16(gl + 1); gend = r16(gl + 4)
    rom[gl:gl + 3] = bytes([0x03, gend & 0xFF, gend >> 8])          # walking up the dock: nothing any more
    # where the dock's exit leads (the passage's warp)
    lw = [w for o, w in dev['warps'] if (w[3], w[4]) == mapid('VermilionPortPassage')][0]
    py_, px_ = pw.warps[lw[2] - 1][0], pw.warps[lw[2] - 1][1]
    log.append('dock %d:%d, flags HM01 %X ship left %X; exit -> passage (%d, %d)' % (*dock, got_hm01, ship_left, px_, py_))

    # routines + the departure script (bank BANK)
    base = sp.here(BANK)
    m = routines(base)
    code = m.done()
    a = Asm(base + len(code)); a.bank = BANK
    a.label('dep')
    a.setevent(ship_left)
    a.turnobject(0, 0)
    a.playmusic(MUSIC_SURF)
    a.callasm(BANK, m.L['prep'])
    a.pause(120)
    a.playsound(SFX_BOAT)
    a.callasm(BANK, m.L['anim'])
    for bx in range(5, 9):
        a.changeblock(2 * bx, 2, 0x01); a.changeblock(2 * bx, 4, 0x0D)
    a.playsound(SFX_BOAT); a.pause(120)
    a.applymovement(0, 'mv')
    a.warp(*mapid('VermilionPortPassage'), px_, py_)
    a.end()
    a.label('mv'); a.db(0x0D, 0x0D, 0x47)
    blob = code + a.done()
    assert sp.put(BANK, blob) == base
    log.append('departure: %X:%04X (%d bytes)' % (BANK, base, len(blob)))

    # the map scene table: the dock shares phase 28's always-0 scene byte
    sr = P21.SCENES_REF
    tb = fo(rom[sr], r16(sr + 3)); n_ = 0
    while rom[tb + 4 * n_] != 0xFF: n_ += 1
    tab = bytes(rom[tb:tb + 4 * n_])
    assert all(tab[4 * i:4 * i + 2] != bytes(dock) for i in range(n_))
    tab += bytes([*dock, P28.SCENE_AREAS & 0xFF, P28.SCENE_AREAS >> 8])
    assert rom[sr] == 0x61 and not any(rom[tb + 4 * n_ + 1:tb + len(tab) + 1])
    rom[tb:tb + len(tab) + 1] = tab + b'\xff'

    # the dock's scene script (map scripts in its script bank): the player has just come down the gangway
    so = fo(sb_, da['scripts']); assert rom[so] == 0
    ncb = rom[so + 1]; cbs = bytes(rom[so + 2:so + 2 + 3 * ncb])
    f, n = bank_free_tail(rom, sb_); sp.set_area(sb_, f + 1, sb_ * 0x4000 + 0x4000)
    s = Asm(sp.here(sb_)); s.bank = sb_
    s.label('ms'); s.db(1); s.dw('scn'); s.dw(0); s.db(ncb); s.raw(cbs)
    s.label('scn'); s.checkevent(got_hm01); s.iffalse('e'); s.checkevent(ship_left); s.iftrue('e')
    s.db(0x1C, VAR_X); s.ifnotequal(14, 'e'); s.db(0x1C, VAR_Y); s.ifnotequal(2, 'e')
    s.sdefer('go')
    s.label('e'); s.end()
    s.label('go'); s.farsjump(BANK, a.labels['dep'])
    sbase = s.base; sblob = s.done(); assert sp.put(sb_, sblob) == sbase
    w16(da['attr_off'] + 7, s.labels['ms'])

    # ================= S.S. Anne 2F: Shigeru (Red): his music, he faces the player, and after the battle walks away
    n2 = None
    for k in range(G26_COUNT + 1, 160):
        hk = GROUP26_END + 9 * (k - G26_COUNT - 1)
        try: a2 = attrs(rom, hk); e2 = parse_events(rom, a2['scbank'], a2['events'])
        except Exception: continue
        if len(e2['coords']) == 2 and [c[1][1:3] for c in e2['coords']] == [bytes([8, 36]), bytes([8, 37])]:
            n2 = k; break
    assert n2 is not None
    a2 = attrs(rom, GROUP26_END + 9 * (n2 - G26_COUNT - 1)); b2 = a2['scbank']; e2 = parse_events(rom, b2, a2['events'])
    olds = [fo(b2, c[1][4] | c[1][5] << 8) for c in e2['coords']]
    for p in olds: assert rom[p] == 0x31 and rom[p + 3] == 0x09 and rom[p + 6] == 0x6E and rom[p + 8] == 0x68 and rom[p + 12] == 0x03
    beat = r16(olds[0] + 1); rve = r16(olds[0] + 4); rv = rom[olds[0] + 7]; rvb = r16(olds[0] + 13)
    rms = [r16(p + 10) for p in olds]
    q = fo(b2, rvb); seg = bytes(rom[q:q + 0x60]); i5 = seg.index(bytes([0x5E, 0x5F])) + 2
    tail = seg[i5:i5 + 12]
    assert tail[0] == 0x47 and tail[1] == 0x4C and tail[4:6] == bytes([0x53, 0x49]) and tail[6:8] == bytes([0x6D, rv]) and tail[11] == 0x90
    rva = tail[2] | tail[3] << 8
    f, n = bank_free_tail(rom, b2); sp.set_area(b2, f + 1, b2 * 0x4000 + 0x4000)
    s = Asm(sp.here(b2)); s.bank = b2
    for (x, (rp, rm)) in zip((36, 37), zip(olds, rms)):
        s.label('n%d' % x); s.checkevent(beat); s.db(0x09); s.dw(rve)
        s.playmusic(MUS_RIVAL); s.appear(rv); s.applymovement(rv, rm)
        s.turnobject(rv, 0 if x == 36 else 3); s.turnobject(0, 1 if x == 36 else 2)
        s.sjump(rvb)
    s.label('after'); s.db(0x1C, VAR_X); s.ifequal(37, 'p37')
    s.disappear(rv); s.moveobject(rv, 36, 7); s.appear(rv); s.turnobject(rv, 0); s.sjump('talk')
    s.label('p37'); s.disappear(rv); s.moveobject(rv, 36, 8); s.appear(rv); s.turnobject(rv, 3)
    s.label('talk'); s.playmusic(MUS_RIVAL_AFTER); s.opentext(); s.writetext(rva); s.waitbutton(); s.closetext()
    s.db(0x1C, VAR_X); s.ifequal(37, 'w37')
    s.applymovement(rv, 'mvr'); s.sjump('gone')
    s.label('w37'); s.applymovement(rv, 'mv4')
    s.label('gone'); s.disappear(rv); s.setevent(beat); s.playmapmusic(); s.end()
    s.label('mvr'); s.db(0x0F, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x47)
    s.label('mv4'); s.db(0x0C, 0x0C, 0x0C, 0x0C, 0x47)
    sbase = s.base; sblob = s.done(); assert sp.put(b2, sblob) == sbase
    for (o, c), x in zip(e2['coords'], (36, 37)): w16(o + 4, s.labels['n%d' % x])
    rom[q + i5:q + i5 + 3] = bytes([0x03, s.labels['after'] & 0xFF, s.labels['after'] >> 8])
    log.append('S.S. Anne 2F (26:%d): Shigeru walks away' % n2)

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    print('\n'.join(log))


if __name__ == '__main__':
    main()
