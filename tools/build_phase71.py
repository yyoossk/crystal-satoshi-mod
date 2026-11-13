#!/usr/bin/env python3
"""Phase 71: the player looks like Red (the Red full-color hack, akafc):
 * Field: the player's sprite (Crystal's sprite 1, Chris) uses Red's sprite (Crystal already has it: sprite 6, SPRITE_RED,
   the same data as Red's).  The naming screen's player icon (GetPlayerIcon, ld de, ChrisSpriteGFX) too.
 * Bike: the Red full-color hack's bike sprite (its sprite table's 2nd entry; Crystal-style, Red's colours).
 * Battle: the player's back pic is the Red full-color hack's (6x6, Gen I compressed in akafc; here column-major LZ as
   Crystal's ChrisBackpic).  Both loaders (battle core, GetChrisBackpic) point to it.
 * Player front pic (the name screen of the opening, the Hall of Fame): the Red full-color hack's Red (Gen I pic
   04:5791 in akafc, 7x7) in place of Crystal's ChrisPic (uncompressed, column-major, $22:$48B2).
 * The player's pic colours (Crystal's PlayerPalette, the 1st entry of the trainer palettes; phase 10 moved the
   table to $02:$77E3): the Red full-color hack's Red (skin $465C, red $20F6).
   Trainer card: Crystal's ChrisCardPic ($22:$436E, 5x7, column-major) becomes the middle 5 columns of that pic.
usage: build_phase71.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
import build_phase10 as P10

AKAFC = SC + '/akafc/akafc.gbc'
SPRITE_TABLE = (0x05, 0x4727)          # Crystal's OverworldSprites: dw gfx, db length, db bank, db type, db palette
GET_PLAYER_ICON = 0x88335              # $22:$4335 ld de, ChrisSpriteGFX / ld b, BANK
BACKPIC_SITES = (0x3FC38, 0x88839)     # ld b, $60 / ld hl, ChrisBackpic ; ld hl, ChrisBackpic / ld b, $60
AKA_BACKPIC = (0x22, 0x4F31)           # akafc: LoadPlayerBackPic's ld de, $4f31 / ld a, $22
AKA_SPRITES = 0x17B0C
AKA_FRONTPIC = (0x04, 0x5791)          # akafc: ld de, $5791 / ld a, $04 (Red's front pic)
CHRIS_PIC = 0x888B2                    # $22:$48B2, 7x7 uncompressed (KrisPic follows at $4BC2)
PLAYER_PAL = 0xB7E3                    # $02:$77E3 PlayerPalette (middle two colours)
RED_PAL = bytes.fromhex('5c46f620')                  # akafc: SpriteSheetPointerTable (dw gfx, db size, db bank)
BANK = 0x71


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    aka = open(AKAFC, 'rb').read()
    sp = Space(rom)
    f, n = bank_free_tail(rom, BANK); sp.set_area(BANK, f + 1 if f > BANK * 0x4000 else f, BANK * 0x4000 + 0x4000)
    log = []
    t = fo(*SPRITE_TABLE)
    chris, bike, red = rom[t:t + 6], rom[t + 6:t + 12], rom[t + 30:t + 36]
    assert chris == bytes.fromhex('0040c0300100') and bike == bytes.fromhex('8041c0300100') and red == bytes.fromhex('c046c0300100')
    # field: Red's sprite
    rom[t:t + 2] = red[:2]; rom[t + 3] = red[3]
    # naming screen icon
    o = GET_PLAYER_ICON; assert rom[o:o + 5] == bytes([0x11, 0x00, 0x40, 0x06, 0x30])
    rom[o + 1:o + 3] = red[:2]; rom[o + 4] = red[3]
    # bike: akafc's
    ab = aka[AKA_SPRITES + 4:AKA_SPRITES + 8]; assert ab[2] == 0xC0
    src = ab[3] * 0x4000 + (ab[0] | ab[1] << 8) - 0x4000
    gfx = aka[src:src + 0x180]
    a_ = sp.put(BANK, gfx); rom[t + 6] = a_ & 0xFF; rom[t + 7] = a_ >> 8; rom[t + 9] = BANK
    log.append('bike sprite from akafc %X -> %X:%04X' % (src, BANK, a_))
    # back pic: akafc's (Gen I pic, 6x6) -> column-major 2bpp -> LZ
    with tempfile.TemporaryDirectory() as d:
        po = AKA_BACKPIC[0] * 0x4000 + AKA_BACKPIC[1] - 0x4000
        assert aka.find(bytes([0x11, AKA_BACKPIC[1] & 0xFF, AKA_BACKPIC[1] >> 8, 0x3E, AKA_BACKPIC[0]])) > 0
        open(d + '/a.pic', 'wb').write(aka[po:po + 1500])
        subprocess.run([P10.PKMN, '-u', d + '/a.pic', d + '/a.2bpp'], check=True)
        raw = open(d + '/a.2bpp', 'rb').read(); assert len(raw) == 36 * 16, len(raw)
        col = b''.join(raw[(y * 6 + x) * 16:(y * 6 + x) * 16 + 16] for x in range(6) for y in range(6))
        open(d + '/c.2bpp', 'wb').write(col)
        subprocess.run([P10.LZ, d + '/c.2bpp', d + '/c.lz'], check=True, stdout=subprocess.DEVNULL)
        lzd = open(d + '/c.lz', 'rb').read()
    ap = sp.put(BANK, lzd)
    s0, s1 = BACKPIC_SITES
    assert rom[s0:s0 + 5] == bytes([0x06, 0x60, 0x21, 0xFC, 0x76]), rom[s0:s0 + 5].hex()
    assert rom[s1:s1 + 5] == bytes([0x21, 0xFC, 0x76, 0x06, 0x60]), rom[s1:s1 + 5].hex()
    rom[s0 + 1] = BANK; rom[s0 + 3] = ap & 0xFF; rom[s0 + 4] = ap >> 8
    rom[s1 + 1] = ap & 0xFF; rom[s1 + 2] = ap >> 8; rom[s1 + 4] = BANK
    log.append('back pic %X:%04X (%d bytes)' % (BANK, ap, len(lzd)))
    # front pic
    for site in (0x8886B - 13, 0x88899 - 13):
        assert rom[site:site + 3] == bytes([0x11, 0xB2, 0x48]), rom[site:site + 3].hex()
    with tempfile.TemporaryDirectory() as d:
        po = AKA_FRONTPIC[0] * 0x4000 + AKA_FRONTPIC[1] - 0x4000
        open(d + '/a.pic', 'wb').write(aka[po:po + 1500])
        subprocess.run([P10.PKMN, '-u', d + '/a.pic', d + '/a.2bpp'], check=True)
        raw = open(d + '/a.2bpp', 'rb').read(); assert len(raw) == 49 * 16, len(raw)
    col = b''.join(raw[(y * 7 + x) * 16:(y * 7 + x) * 16 + 16] for x in range(7) for y in range(7))
    rom[CHRIS_PIC:CHRIS_PIC + len(col)] = col
    card = 0x8836E; assert rom[0x88347:0x8834A] == bytes([0x21, 0x6E, 0x43]) and rom[0x88351:0x88354] == bytes([0x21, 0x9E, 0x45])
    cc = b''.join(raw[(y * 7 + x) * 16:(y * 7 + x) * 16 + 16] for x in range(1, 6) for y in range(7))
    rom[card:card + len(cc)] = cc
    # colours
    assert rom[PLAYER_PAL:PLAYER_PAL + 4] == bytes.fromhex('59323615')
    rom[PLAYER_PAL:PLAYER_PAL + 4] = RED_PAL
    log.append('front pic, player palette')

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
