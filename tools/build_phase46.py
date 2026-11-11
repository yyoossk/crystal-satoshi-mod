#!/usr/bin/env python3
"""Phase 46: Rock Tunnel, Diglett's Cave and the Route 5 Day Care as in Red / the Pikachu full-color hack (new maps;
Crystal's are no longer reached):
 * Rock Tunnel 1F / B1F: Red's caves (Gen I cavern tileset), trainers, sign, wild Pokémon; dark until Flash (the
   tileset palette routine of phase 44 gives black palettes when the map is dark).
 * Diglett's Cave: Red's cave between the Route 2 and Route 11 entrances, Red's wild Pokémon.
 * The Day Care on Route 5: Red's house and gentleman (one Pokémon, Red's texts and rules: not with only one Pokémon,
   none knowing an HM move; ¥100 + ¥100 a level to take it back), on Crystal's day-care-man slot.
usage: build_phase46.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import portmaps as PM
import redmap as RM
import build_phase17 as P17
import build_phase21 as P21
import build_phase25 as P25
import build_phase27 as P27
import build_phase28 as P28
import build_phase41 as P41
import build_phase45 as P45
import routekit as RK

FIRST_FLAG = 482                   # 481: phase 44
FIRST_MAP = 147                    # 26:145-146 = phase 44
TBANK, BANK, CBANK = 0x69, 0x62, 0x74
CAVERN_TS, HOUSE_TS = 37, 44
SPR = dict(P41.SPR)
NEW = ['RockTunnel1F', 'RockTunnelB1F', 'DiglettsCave', 'Daycare']
RED_ID = {'RockTunnel1F': 0x52, 'RockTunnelB1F': 0xE8, 'DiglettsCave': 0xC5, 'Daycare': 0x48}
HDR = {'RockTunnel1F': 'RockTunnel1F', 'RockTunnelB1F': 'RockTunnelB1F', 'DiglettsCave': 'DiglettsCave',
       'Daycare': 'Route5CleanseTagHouse'}
# JP Crystal: RAM and routines (from DayCareMan, 05:6BB7)
W_SCRIPTVAR = 0xC2DD
W_PARTYCOUNT, W_CURSPECIES, W_CURMON = 0xDC9D, 0xD0C8, 0xD0C9
W_MON1ITEM, W_NICKS = 0xDCA6, 0xDDE9
W_SB1, W_SB2, W_MONEY = 0xD05B, 0xD066, 0xD841
W_DAYCAREMAN, W_BREED1NICK = 0xDE89, 0xDE8A
ADDNTIMES, GETNICKNAME, PLAYMONCRY, COPYBYTES = 0x30CA, 0x3872, 0x379E, 0x2FF2
FC_SELECTMON = (0x14, 0x401D); FC_FAINTED = (0x03, 0x67E0); FC_ISMAIL = (0x2E, 0x61FA)
FC_DEPOSIT = (0x03, 0x607F); FC_INITBREED = (0x05, 0x723B); FC_GROWTH = (0x03, 0x6946); FC_RETRIEVE = (0x03, 0x5F76)
FC_COMPAREMONEY = (0x05, 0x6425); FC_TAKEMONEY = (0x05, 0x6414)
DAYCARE_TEXTS = 0x6D88             # PrintDayCareText.TextTable (05): Crystal's own texts for eggs / mail / last healthy
DCT_CANT_BREED_EGG, DCT_REMOVE_MAIL, DCT_LAST_ALIVE = 6, 7, 8
SPECIAL_MONEY = 0x51               # PlaceMoneyTopRight
SFX_TRANSACTION = 0x22
HM_MOVES = [0x0F, 0x13, 0x39, 0x46, 0x94]          # Cut, Fly, Surf, Strength, Flash (Red)


def daycare_code(base):
    m = P45.M(base)
    lo = lambda v: v & 0xFF; hi = lambda v: v >> 8
    def farcall(b, a): m(0x3E, b, 0x21, lo(a), hi(a), 0xCF)
    def ret_a(): m(0xEA, lo(W_SCRIPTVAR), hi(W_SCRIPTVAR), 0xC9)
    m.lab('has')(0xFA, lo(W_DAYCAREMAN), hi(W_DAYCAREMAN), 0xE6, 1); ret_a()
    m.lab('one')(0xFA, lo(W_PARTYCOUNT), hi(W_PARTYCOUNT), 0xFE, 2, 0x3E, 0, 0x30, 1, 0x3C); ret_a()
    m.lab('full')(0xFA, lo(W_PARTYCOUNT), hi(W_PARTYCOUNT), 0xFE, 6, 0x3E, 0, 0x38, 1, 0x3C); ret_a()
    # sel: 0 ok (nickname in wStringBuffer1), 1 declined, 2 egg, 3 last healthy, 4 mail, 5 knows an HM move
    m.lab('sel')(0x06, 6); farcall(*FC_SELECTMON); m.jr(0x38, 'sd')
    m(0xFA, lo(W_CURSPECIES), hi(W_CURSPECIES), 0xFE, 0xFD).jr(0x28, 'se')
    farcall(*FC_FAINTED); m.jr(0x38, 'sf')
    m(0x21, lo(W_MON1ITEM), hi(W_MON1ITEM), 0x01, 0x30, 0x00, 0xFA, lo(W_CURMON), hi(W_CURMON), 0xCD, lo(ADDNTIMES), hi(ADDNTIMES), 0x56)
    farcall(*FC_ISMAIL); m.jr(0x38, 'sm')
    m(0x21, lo(W_MON1ITEM + 1), hi(W_MON1ITEM + 1), 0x01, 0x30, 0x00, 0xFA, lo(W_CURMON), hi(W_CURMON),
      0xCD, lo(ADDNTIMES), hi(ADDNTIMES), 0x0E, 4)
    m.lab('mv')(0x2A, 0xE5).w(0x21, 'hms')(0x06, len(HM_MOVES))
    m.lab('hm')(0xBE).jr(0x28, 'shm')(0x23, 0x05).jr(0x20, 'hm')(0xE1, 0x0D).jr(0x20, 'mv')
    m(0x21, lo(W_NICKS), hi(W_NICKS), 0xFA, lo(W_CURMON), hi(W_CURMON), 0xCD, lo(GETNICKNAME), hi(GETNICKNAME))
    m(0xAF); ret_a()
    m.lab('sd')(0x3E, 1); ret_a()
    m.lab('se')(0x3E, 2); ret_a()
    m.lab('sf')(0x3E, 3); ret_a()
    m.lab('sm')(0x3E, 4); ret_a()
    m.lab('shm')(0xE1, 0x3E, 5); ret_a()
    m.lab('hms')(*HM_MOVES)
    # dep: Crystal's DepositMonWithDayCareMan, the man's flags, breeding check
    m.lab('dep'); farcall(*FC_DEPOSIT)
    m(0x21, lo(W_DAYCAREMAN), hi(W_DAYCAREMAN), 0xCB, 0xC6, 0xCB, 0xFE); farcall(*FC_INITBREED); m(0xC9)
    m.lab('cry')(0xFA, lo(W_CURSPECIES), hi(W_CURSPECIES), 0xCD, lo(PLAYMONCRY), hi(PLAYMONCRY), 0xC9)
    # grow: levels grown (wStringBuffer2 + 1), nickname (wStringBuffer1), price 100 * (levels + 1) (wStringBuffer2 + 2..4)
    m.lab('grow'); farcall(*FC_GROWTH)
    m(0x78, 0xEA, lo(W_SB2), hi(W_SB2), 0x7A, 0xEA, lo(W_SB2 + 1), hi(W_SB2 + 1))
    m(0x21, lo(W_BREED1NICK), hi(W_BREED1NICK), 0x11, lo(W_SB1), hi(W_SB1), 0x01, 6, 0, 0xCD, lo(COPYBYTES), hi(COPYBYTES))
    m(0x21, 0, 0, 0x01, 100, 0, 0xFA, lo(W_SB2 + 1), hi(W_SB2 + 1), 0xCD, lo(ADDNTIMES), hi(ADDNTIMES), 0x11, 100, 0, 0x19)
    m(0xAF, 0xEA, lo(W_SB2 + 2), hi(W_SB2 + 2), 0x7C, 0xEA, lo(W_SB2 + 3), hi(W_SB2 + 3), 0x7D, 0xEA, lo(W_SB2 + 4), hi(W_SB2 + 4))
    m(0xFA, lo(W_SB2 + 1), hi(W_SB2 + 1), 0xA7).jr(0x28, 'g0')(0x3E, 1)
    m.lab('g0'); ret_a()
    m.lab('poor')(0x11, lo(W_MONEY), hi(W_MONEY), 0x01, lo(W_SB2 + 2), hi(W_SB2 + 2)); farcall(*FC_COMPAREMONEY)
    m(0x3E, 0, 0x30, 1, 0x3C); ret_a()
    m.lab('take')(0x01, lo(W_SB2 + 2), hi(W_SB2 + 2), 0x11, lo(W_MONEY), hi(W_MONEY)); farcall(*FC_TAKEMONEY); m(0xC9)
    m.lab('ret'); farcall(*FC_RETRIEVE)
    m(0x21, lo(W_DAYCAREMAN), hi(W_DAYCAREMAN), 0xCB, 0x86, 0xCB, 0xAE, 0xC9)
    return m


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    sp = Space(rom)
    def r16(o): return rom[o] | rom[o + 1] << 8
    def w16(o, v): rom[o] = v & 0xFF; rom[o + 1] = v >> 8
    for b in (TBANK, BANK, CBANK):
        f, n = bank_free_tail(rom, b); sp.set_area(b, f + 1 if f > b * 0x4000 else f, b * 0x4000 + 0x4000)
    log = []
    FL = PM.Flags(FIRST_FLAG)
    K = RK.Kit(rom, sp, TBANK, FL, log, FIRST_MAP - 1)
    nid = {n: (G26, FIRST_MAP + i) for i, n in enumerate(NEW)}
    r10, r5 = mapid('Route10North'), mapid('Route5')

    # ================= tilesets: Red's cavern (Crystal's tileset 37), Red's house (44)
    cav = Tileset('Cavern', 17, 'cavern.bst', SC + '/out/pk_cavern.pkl')
    hts = Tileset('House', 8, 'house.bst', SC + '/out/pk_house.pkl')
    nmp = {}
    for n in NEW:
        w_, h_ = RK.red_dims(n); nmp[n] = MapPort(n, hts if n == 'Daycare' else cav, w_, h_, n + '.blk')
    caves = {n: nmp[n] for n in NEW if n != 'Daycare'}
    K.ts_variants(CAVERN_TS, cav, caves,
                  {n: {(x, y): P25.warp_override(cav, nmp[n], x, y, True) for x, y, d, wi in P25.red_objects(n)[1]} for n in caves},
                  P21.PAIRS)
    K.ts_variants(HOUSE_TS, hts, {'Daycare': nmp['Daycare']},
                  {'Daycare': {(x, y): P25.warp_override(hts, nmp['Daycare'], x, y) for x, y, d, wi in P25.red_objects('Daycare')[1]}})
    K.bank = BANK
    K.add_parties(['RockTunnel1F', 'RockTunnelB1F'])
    K.alloc_headers(FIRST_MAP, len(NEW))

    # ================= the Day Care's routines
    cb = sp.here(CBANK); m = daycare_code(cb); code = m.done(); assert sp.put(CBANK, code) == cb
    L = {k: v for k, v in m.L.items()}

    # ================= events
    a = Asm(sp.here(BANK)); a.bank = BANK; texts = {}
    def W(x, y, wid, mp): return bytes([y, x, wid, *mp])
    # Rock Tunnel / Diglett's Cave
    entr = {}
    for n in ('DiglettsCaveRoute2', 'DiglettsCaveRoute11'):
        for k in range(G26_COUNT + 1, FIRST_MAP):
            h_ = GROUP26_END + 9 * (k - G26_COUNT - 1)
            if not rom[h_]: continue
            try: ev_ = parse_events(rom, attrs(rom, h_)['scbank'], attrs(rom, h_)['events'])
            except Exception: continue
            ws = [w for o, w in ev_['warps']]
            if len(ws) == 3 and (ws[2][3], ws[2][4]) == mapid('DiglettsCave') and (n not in entr) and \
                    (ws[0][3], ws[0][4]) == mapid('Route2' if n.endswith('2') else 'Route11'):
                entr[n] = (G26, k)
    assert len(entr) == 2, entr
    CONST = {'ROCK_TUNNEL_1F': nid['RockTunnel1F'], 'ROCK_TUNNEL_B1F': nid['RockTunnelB1F'],
             'DIGLETTS_CAVE_ROUTE_2': entr['DiglettsCaveRoute2'], 'DIGLETTS_CAVE_ROUTE_11': entr['DiglettsCaveRoute11']}
    for n in ('RockTunnel1F', 'RockTunnelB1F', 'DiglettsCave'):
        ob, bgs = K.red_events(a, texts, n, RED_ID[n], {'RockTunnel1F': 'rt1_', 'RockTunnelB1F': 'rtb_', 'DiglettsCave': 'dc_'}[n], {}, SPR)
        ws = [W(x, y, wi, r10 if d == 'LAST_MAP' else CONST[d]) for x, y, d, wi in P25.red_objects(n)[1]]
        K.emit(a, n, ws, [], bgs, ob, [])

    # the Day Care
    sub = {('ram', 0xCD68): b'\x01' + bytes([W_SB1 & 0xFF, W_SB1 >> 8]),
           ('ram', 0xD985): b'\x01' + bytes([W_SB1 & 0xFF, W_SB1 >> 8]),
           ('dec', 0xCD3E): bytes([0x09, (W_SB2 + 1) & 0xFF, (W_SB2 + 1) >> 8, 0x13]),
           ('bcd', 0xCD3F): bytes([0x09, (W_SB2 + 2) & 0xFF, (W_SB2 + 2) >> 8, 0x36])}
    def G(p): return P27.gen1_text(RM.fo(0x15, p), sub)
    texts.update({'dc_intro': G(0x7411), 'dc_which': G(0x742D), 'dc_will': G(0x7442), 'dc_later': G(0x7459),
                  'dc_grown': G(0x7472), 'dc_price': G(0x74BD), 'dc_got': G(0x74DD), 'dc_soon': G(0x74F8),
                  'dc_no': G(0x751F), 'dc_full': G(0x7534), 'dc_one': G(0x754E), 'dc_hm': G(0x7564),
                  'dc_here': G(0x7583), 'dc_poor': G(0x759B)})
    def ca(lab): a.callasm(CBANK, L[lab])
    def crystal_text(i): return r16(fo(5, DAYCARE_TEXTS) + 2 * i)
    a.label('dcm'); a.faceplayer(); a.opentext()
    ca('has'); a.iftrue('dcw')
    a.writetext('dc_intro'); a.yesorno(); a.iffalse('dcn')
    ca('one'); a.iftrue('dc1')
    a.writetext('dc_which'); ca('sel')
    a.ifequal(1, 'dcn'); a.ifequal(5, 'dch')
    for v, t in ((2, DCT_CANT_BREED_EGG), (3, DCT_LAST_ALIVE), (4, DCT_REMOVE_MAIL)):
        a.ifequal(v, 'dcx%d' % v)
    ca('dep'); a.writetext('dc_will'); ca('cry'); a.waitsfx(); a.writetext('dc_later'); a.waitbutton(); a.closetext(); a.end()
    for v, t in ((2, DCT_CANT_BREED_EGG), (3, DCT_LAST_ALIVE), (4, DCT_REMOVE_MAIL)):
        a.label('dcx%d' % v); a.farwritetext(5, crystal_text(t)); a.waitbutton(); a.closetext(); a.end()
    for lab, t in (('dcn', 'dc_no'), ('dc1', 'dc_one'), ('dch', 'dc_hm'), ('dcf', 'dc_full'), ('dcp', 'dc_poor')):
        a.label(lab); a.writetext(t); a.waitbutton(); a.closetext(); a.end()
    a.label('dcw'); ca('grow'); a.iftrue('dcg')
    a.writetext('dc_soon'); a.sjump('dck')
    a.label('dcg'); a.writetext('dc_grown')
    a.label('dck'); ca('full'); a.iftrue('dcf')
    a.writetext('dc_price'); a.special(SPECIAL_MONEY); a.yesorno(); a.iffalse('dcn')
    ca('poor'); a.iftrue('dcp')
    ca('take'); a.playsound(SFX_TRANSACTION); a.waitsfx(); a.special(SPECIAL_MONEY)
    a.writetext('dc_here'); ca('ret'); ca('cry'); a.waitsfx(); a.writetext('dc_got'); a.waitbutton(); a.closetext(); a.end()
    o = P25.red_objects('Daycare')[0][0]
    mv, rng = P25.face((0, 0, 0, o['move'], o['face']))
    dob = [[SPR[o['sprite']], o['y'] + 4, o['x'] + 4, mv, rng, 0xFF, 0xFF, 0, 0, 'dcm', 0xFFFF]]
    K.emit(a, 'Daycare', [W(x, y, wi, r5) for x, y, d, wi in P25.red_objects('Daycare')[1]], [], [], dob, [])
    K.put_texts(a, texts)
    base = a.base; blob = a.done(); assert sp.put(BANK, blob) == base
    log.append('events %X:%04X (%d bytes), Day Care routines %X:%04X (%d bytes)' % (BANK, base, len(blob), CBANK, cb, len(code)))
    for i, n in enumerate(NEW):
        K.make_map(FIRST_MAP + i, nmp[n], HOUSE_TS if n == 'Daycare' else CAVERN_TS, border_of(n), HDR[n],
                   3 if n == 'Daycare' else 4, a, n)

    # ================= the way in
    rt = [wi for x, y, d, wi in P25.red_objects('Route10')[1] if d == 'ROCK_TUNNEL_1F']; k_ = [0]
    def f10(i, w_):
        if (w_[3], w_[4]) == mapid('RockTunnel1F'): r_ = (rt[k_[0]], nid['RockTunnel1F']); k_[0] += 1; return r_
    assert K.fix_warps('Route10North', f10) == 2
    for n in ('DiglettsCaveRoute2', 'DiglettsCaveRoute11'):
        wi = [w for x, y, d, w in P25.red_objects(n)[1] if d == 'DIGLETTS_CAVE'][0]
        h_ = GROUP26_END + 9 * (entr[n][1] - G26_COUNT - 1)
        assert K.fix_warps(h_, lambda i, w_: (wi, nid['DiglettsCave']) if (w_[3], w_[4]) == mapid('DiglettsCave') else None) == 1
    dw = [wi for x, y, d, wi in P25.red_objects('Route5')[1] if d == 'DAYCARE'][0]
    assert K.fix_warps('Route5', lambda i, w_: (dw, nid['Daycare']) if (w_[3], w_[4]) == mapid('Route5CleanseTagHouse') else None) == 1

    # ================= wild Pokémon
    kg = P27.kanto_grass(rom)
    for n in ('RockTunnel1F', 'RockTunnelB1F', 'DiglettsCave'):          # Crystal's entries (maps no longer reached)
        p = kg
        while rom[p] != 0xFF and (rom[p], rom[p + 1]) != mapid(n): p += 47
        if rom[p] != 0xFF: rom[p:p + 2] = bytes(nid[n])
        K.red_wild(nid[n], n)

    # ================= Route 29 (Johto): its map attributes lay where phase 23 put group 26 headers -> the original's back
    h29 = hdr_index('Route29'); ao = attrs(orig, h29)['attr_off']; n29 = 12 + 12 * bin(orig[ao + 11] & 0xF).count('1')
    if bytes(rom[attrs(rom, h29)['attr_off']:][:n29]) != orig[ao:ao + n29]:
        p29 = sp.put(CBANK, orig[ao:ao + n29]); rom[h29] = CBANK; w16(h29 + 3, p29)
        log.append('Route 29: map attributes restored (%X:%04X)' % (CBANK, p29))

    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    assert FL.i < 8 * (P28.SCENE_AREAS - 0xDA01)
    log.append('extended flags used up to %d' % FL.i)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
