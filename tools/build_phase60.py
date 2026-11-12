#!/usr/bin/env python3
"""Phase 60: Johto has only Gen II Pokémon (Kanto only Gen I), and every Gen II Pokémon can be had in Johto except
the ones that come from Kanto's Pokémon (Crobat, Bellossom, Politoed, Slowking, Kingdra, Steelix, Scizor, Blissey,
Porygon2, Espeon, Umbreon and the babies Pichu, Cleffa, Igglybuff, Smoochum, Elekid, Magby: evolve / hatch them from
Pokémon brought from Kanto), the two starters Prof. Elm does not give and Celebi (both decided later).
 * Every Gen I Pokémon in Johto's wild data (grass and caves by time of day, surfing, the fishing groups and their
   time groups, the swarms, headbutt trees, Rock Smash, the Bug-Catching Contest; also Routes 26, 27, 28 and Tohjo
   Falls) is replaced by a Gen II Pokémon of the same kind at the same level (MAP below): e.g. Rattata -> Sentret,
   Pidgey -> Hoothoot, Spearow -> Murkrow, Zubat -> Gligar, Geodude -> Slugma, Bellsprout / Magnemite -> Mareep,
   Growlithe / Ponyta -> Houndour, Drowzee / Doduo -> Girafarig, Tentacool -> Chinchou, Magikarp -> Remoraid.
 * Gifts / events: Bill's Eevee -> Sneasel, the Dragon's Den elder's Dratini -> Larvitar, Kenya's Spearow -> Murkrow,
   the Union Cave Lapras (Fridays) -> Mantine, the Rocket hideout's Electrodes -> Forretress, the Goldenrod Game
   Corner's Abra / Cubone -> Natu / Phanpy, Johto's in-game trades with Gen II Pokémon on both sides.
   The Lake of Rage's red Gyarados stays.
 * Kanto: Crystal's Pewter Pokémon Center trade gave Xatu: it gives Kadabra.
usage: build_phase60.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
import portmaps as PM

N = PM.MON
MAP = {
    'CATERPIE': 'LEDYBA', 'METAPOD': 'LEDYBA', 'BUTTERFREE': 'LEDIAN', 'WEEDLE': 'SPINARAK', 'KAKUNA': 'SPINARAK',
    'BEEDRILL': 'ARIADOS', 'PIDGEY': 'HOOTHOOT', 'PIDGEOTTO': 'NOCTOWL', 'PIDGEOT': 'NOCTOWL',
    'RATTATA': 'SENTRET', 'RATICATE': 'FURRET', 'SPEAROW': 'MURKROW', 'FEAROW': 'MURKROW',
    'EKANS': 'DUNSPARCE', 'ARBOK': 'DUNSPARCE', 'SANDSHREW': 'PHANPY', 'SANDSLASH': 'DONPHAN',
    'NIDORAN_F': 'SNUBBULL', 'NIDORINA': 'GRANBULL', 'NIDORAN_M': 'TEDDIURSA', 'NIDORINO': 'URSARING',
    'JIGGLYPUFF': 'SNUBBULL', 'WIGGLYTUFF': 'GRANBULL', 'ZUBAT': 'GLIGAR', 'GOLBAT': 'GLIGAR',
    'ODDISH': 'SUNKERN', 'GLOOM': 'SUNFLORA', 'VILEPLUME': 'SUNFLORA', 'PARAS': 'PINECO', 'PARASECT': 'FORRETRESS',
    'VENONAT': 'YANMA', 'VENOMOTH': 'YANMA', 'DIGLETT': 'PHANPY', 'DUGTRIO': 'DONPHAN', 'MEOWTH': 'AIPOM',
    'PERSIAN': 'AIPOM', 'PSYDUCK': 'MARILL', 'GOLDUCK': 'AZUMARILL', 'MANKEY': 'TEDDIURSA', 'PRIMEAPE': 'URSARING',
    'GROWLITHE': 'HOUNDOUR', 'ARCANINE': 'HOUNDOOM', 'POLIWAG': 'WOOPER', 'POLIWHIRL': 'QUAGSIRE',
    'POLIWRATH': 'QUAGSIRE', 'ABRA': 'NATU', 'KADABRA': 'XATU', 'MACHOP': 'TEDDIURSA', 'MACHOKE': 'URSARING',
    'BELLSPROUT': 'MAREEP', 'WEEPINBELL': 'FLAAFFY', 'TENTACOOL': 'CHINCHOU', 'TENTACRUEL': 'LANTURN',
    'GEODUDE': 'SLUGMA', 'GRAVELER': 'MAGCARGO', 'PONYTA': 'HOUNDOUR', 'RAPIDASH': 'HOUNDOOM',
    'SLOWPOKE': 'WOOPER', 'SLOWBRO': 'QUAGSIRE', 'MAGNEMITE': 'MAREEP', 'MAGNETON': 'FLAAFFY',
    'FARFETCH_D': 'NATU', 'DODUO': 'GIRAFARIG', 'DODRIO': 'GIRAFARIG', 'SEEL': 'DELIBIRD', 'DEWGONG': 'PILOSWINE',
    'SHELLDER': 'CORSOLA', 'CLOYSTER': 'CORSOLA', 'GASTLY': 'MISDREAVUS', 'HAUNTER': 'MISDREAVUS', 'ONIX': 'SHUCKLE',
    'DROWZEE': 'GIRAFARIG', 'HYPNO': 'GIRAFARIG', 'KRABBY': 'CORSOLA', 'KINGLER': 'CORSOLA',
    'VOLTORB': 'PINECO', 'ELECTRODE': 'FORRETRESS', 'EXEGGCUTE': 'HOPPIP', 'EXEGGUTOR': 'JUMPLUFF',
    'CUBONE': 'PHANPY', 'MAROWAK': 'DONPHAN', 'LICKITUNG': 'STANTLER', 'KOFFING': 'HOUNDOUR', 'WEEZING': 'HOUNDOOM',
    'RHYHORN': 'PHANPY', 'RHYDON': 'DONPHAN', 'CHANSEY': 'MILTANK', 'TANGELA': 'SUNKERN', 'HORSEA': 'REMORAID',
    'SEADRA': 'OCTILLERY', 'GOLDEEN': 'QWILFISH', 'SEAKING': 'QWILFISH', 'STARYU': 'CORSOLA', 'STARMIE': 'CORSOLA',
    'SCYTHER': 'HERACROSS', 'PINSIR': 'HERACROSS', 'JYNX': 'SNEASEL', 'ELECTABUZZ': 'FLAAFFY', 'MAGMAR': 'MAGCARGO',
    'TAUROS': 'MILTANK', 'MAGIKARP': 'REMORAID', 'GYARADOS': 'OCTILLERY', 'LAPRAS': 'MANTINE', 'DITTO': 'SMEARGLE',
    'EEVEE': 'SNEASEL', 'DRATINI': 'MANTINE', 'DRAGONAIR': 'MANTINE', 'DRAGONITE': 'MANTINE', 'GRIMER': 'SLUGMA',
    'MUK': 'MAGCARGO', 'VULPIX': 'HOUNDOUR', 'NINETALES': 'HOUNDOOM', 'PIKACHU': 'MAREEP', 'RAICHU': 'AMPHAROS',
    'CLEFAIRY': 'SNUBBULL', 'CLEFABLE': 'GRANBULL', 'KANGASKHAN': 'URSARING', 'AERODACTYL': 'SKARMORY'}
M = {N[k]: N[v] for k, v in MAP.items()}
for k, v in MAP.items(): assert N[k] <= 151 < N[v], k


def sp(s):
    if 0 < s <= 151:
        assert s in M, ('no Gen II for', s)
        return M[s]
    return s


BA = 0x0A
JOHTO_GRASS, SWARM_GRASS, JOHTO_WATER = 0x660C, 0x7DDE, 0x7E3F
KANTO_GRASS, KANTO_WATER = 0x7140, 0x7D05
JOHTO_SIDE = [(3, 83), (24, 1), (24, 2), (19, 1)]       # Tohjo Falls, Routes 26, 27, 28 (in Crystal's Kanto tables)
FISH_BANK, FISH_GROUPS, N_FISH, TIME_FISH, TIME_FISH_END = 0x24, 0x69FB, 13, 0x6BE2, 0x6C3A
TREEMONS, TREEMONS_END = 0xB82DA, 0xB83C5
CONTEST = 0x97D49
TRADES = (0x3F, 0x7A53); JOHTO_TRADES = [0, 1, 2, 3]; PEWTER_TRADE = 4
GIFTS = [(0x54BA9, 'EEVEE', 'SNEASEL'), (0x714F1, 'DRATINI', 'LARVITAR'), (0x62D39, 'SPEAROW', 'MURKROW')]
STATICS = [(0x59A5A, 'LAPRAS', 'MANTINE')] + [(o, 'ELECTRODE', 'FORRETRESS') for o in (0x64CE9, 0x64D14, 0x64D3F)]
PRIZES = [(0x562A0, 0x56340, 'ABRA', 'NATU', 'ケーシィ', 'ネイティ'), (0x562A0, 0x56360, 'CUBONE', 'PHANPY', 'カラカラ', 'ゴマゾウ')]
TEXTS = [(0x15, 'イーブイ', 'ニューラ'), (0x1C, 'ミニりュウ', 'ヨーギラス'), (0x19, 'マルマイン', 'フォレトス')]
BILL_AFTER_AT = 0x54CD9          # 「マサキ：イーブイには　あたらしい　しんかの　かのうせい…」 (the line after the gift)
BILL_AFTER = '{00}マサキ{72}ニューラは　よるに<LINE>げんきに　なるらしいで'


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    def r16(o): return rom[o] | rom[o + 1] << 8
    log = []; n = [0]
    def put(o):
        v = sp(rom[o])
        if v != rom[o]: rom[o] = v; n[0] += 1

    # ---- grass / caves (47-byte entries) and surfing (9)
    def grass(off, only=None):
        o = fo(BA, off); k = 0
        while rom[o] != 0xFF:
            if only is None or (rom[o], rom[o + 1]) in only:
                for i in range(21): put(o + 6 + 2 * i)
                k += 1
            o += 47
        return k
    def water(off, only=None):
        o = fo(BA, off); k = 0
        while rom[o] != 0xFF:
            if only is None or (rom[o], rom[o + 1]) in only:
                for i in range(3): put(o + 4 + 2 * i)
                k += 1
            o += 9
        return k
    log.append('grass: Johto %d, swarms %d, Johto side %d; water: Johto %d, Johto side %d' % (
        grass(JOHTO_GRASS), grass(SWARM_GRASS), grass(KANTO_GRASS, JOHTO_SIDE), water(JOHTO_WATER), water(KANTO_WATER, JOHTO_SIDE)))
    # ---- fishing (Crystal's groups: Johto and the Johto side; Kanto's maps use phase 57's own fishing)
    tabs = set()
    for g in range(N_FISH):
        r = fo(FISH_BANK, FISH_GROUPS) + 7 * g
        for k in range(3): tabs.add(r16(r + 1 + 2 * k))
    for t in sorted(tabs):
        o = fo(FISH_BANK, t)
        while True:
            if rom[o + 1]: put(o + 1)                                 # species 0: a time group (level = index)
            if rom[o] == 0xFF: break
            o += 3
    for o in range(fo(FISH_BANK, TIME_FISH), fo(FISH_BANK, TIME_FISH_END), 2): put(o)
    assert rom[fo(FISH_BANK, TIME_FISH_END):fo(FISH_BANK, TIME_FISH_END) + 3] == bytes([0x21, 0xC0, 0xCF])
    # ---- headbutt / Rock Smash
    o = TREEMONS
    while o < TREEMONS_END:
        if rom[o] == 0xFF: o += 1; continue
        put(o + 1); o += 3
    assert rom[TREEMONS_END - 1] == 0xFF
    # ---- Bug-Catching Contest
    o = CONTEST
    while True:
        put(o + 1)
        if rom[o] == 0xFF: break
        o += 4
    log.append('wild species replaced: %d' % n[0])
    # ---- gifts / events
    for o, a, b in GIFTS:
        assert rom[o] == 0x2D and rom[o + 1] == N[a]; rom[o + 1] = N[b]
    for o, a, b in STATICS:
        assert rom[o] == 0x5C and rom[o + 1] == N[a]; rom[o + 1] = N[b]
    for bank, a, b in TEXTS:
        ka, kb = encode(a).rstrip(b'\x50'), encode(b).rstrip(b'\x50'); assert len(ka) == len(kb)
        s0 = bank * 0x4000; blob = rom[s0:s0 + 0x4000]; k = 0; i = blob.find(ka)
        while i >= 0: rom[s0 + i:s0 + i + len(ka)] = kb; k += 1; i = blob.find(ka, i + 1)
        assert k, a; log.append('text %s -> %s (%d)' % (a, b, k))
    i = rom.rfind(b'\x00', BILL_AFTER_AT - 40, BILL_AFTER_AT); e = rom.find(b'\x57', BILL_AFTER_AT)
    kb = encode(BILL_AFTER).rstrip(b'\x50') + b'\x57'; assert len(kb) <= e + 1 - i
    rom[i:e + 1] = kb + bytes(e + 1 - i - len(kb))
    for scr, menu, a, b, na, nb in PRIZES:
        k = 0
        for o in range(fo(0x15, 0x6280) if False else scr, scr + 0xA0):
            if rom[o] == 0x40 and rom[o + 1] == N[a] and rom[o + 2] == 0: rom[o + 1] = N[b]; k += 1
            if rom[o] == 0x2D and rom[o + 1] == N[a]: rom[o + 1] = N[b]; k += 1
        ka, kb = encode(na).rstrip(b'\x50'), encode(nb).rstrip(b'\x50')
        i = rom.find(ka, menu - 0x20, menu + 0x20); assert i > 0 and len(ka) == len(kb); rom[i:i + len(ka)] = kb
        assert k == 2, (a, k)
    # ---- trades
    t0 = fo(*TRADES)
    for i in JOHTO_TRADES:
        for j in (1, 2): rom[t0 + 16 * i + j] = sp(rom[t0 + 16 * i + j])
    assert rom[t0 + 16 * PEWTER_TRADE + 2] == N['XATU']; rom[t0 + 16 * PEWTER_TRADE + 2] = N['KADABRA']
    log.append('gifts, events, prizes, trades: done')
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    print('\n'.join(log))


if __name__ == '__main__':
    main()
