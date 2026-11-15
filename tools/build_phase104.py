#!/usr/bin/env python3
"""Phase 104: Kanto fixes (Route 24 / 25 trainers, Cerulean Mart, Bill).
 * Kanto trainers stayed hidden after they were beaten (on the next visit of the map): their object's visibility
   flag was the trainer's own "beaten" flag (Routes 3-25 / 4, Viridian Forest, Victory Road, the Fighting Dojo, ...).
   As in Red they stay: the visibility flag of every trainer object whose flag equals its trainer's beaten flag is
   now -1 (always shown).
 * Cerulean Mart: Red's man walking up and down (Red's (3,4)) stood on the spot in front of the clerk (Crystal's room:
   the clerk is at (1,3), the counter at (2,3), the player talks from (3,3)).  He is now where Red has him relative to
   the clerk: (4,2), walking up and down beside the counter.
 * Bill's house (Red's, before the Hall of Fame), as in the Pikachu version (pokeyellow scripts/BillsHouse.asm and
   engine/events/hidden_events/bills_house_pc.asm):
     - Bill (as a Pokémon) walks into the Cell Separator (up x3; around the player when the player stands above him)
       before he vanishes;
     - the PC: tink / shrink / tink / jingle with the Pikachu version's pauses, then Bill comes out of the machine at
       (1,2) and walks down / right x3 / down to (4,4), the player walks right x3 to him, and he talks (S.S. Ticket).
usage: build_phase104.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
sys.path.insert(0, os.path.join(SC, 'play'))
from mapdb import DB

BILL = (26, 51); BB = 0x61
BMON_END = 0x5456                  # disappear mon / setevent s1 / end
PC_END = 0x5474                    # playsound SFX_ENTER_DOOR / waitsfx / appear hum / setevent s2 / end
BHUM = 0x547E                      # Bill's S.S. Ticket script (faceplayer / opentext / ...)
MART = (7, 7)
SFX_GLASS_TING, SFX_WARP_TO, SFX_ITEM = 0xBC, 0x13, 0x01
KANTO_GROUPS = None


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read()); log = []
    db = DB(src_rom)
    # ---- trainers: visibility flag == beaten flag -> -1
    n = 0
    for k, m in sorted(db.maps.items()):
        a = attrs(rom, m['hdr']); b = a['scbank']
        for p, o in m['ev']['objs']:
            if rom[p + 7] & 0x0F != 2: continue                      # OBJECTTYPE_TRAINER
            sc = rom[p + 9] | rom[p + 10] << 8; fl = rom[p + 11] | rom[p + 12] << 8
            if sc < 0x4000 or fl == 0xFFFF: continue
            bf = rom[fo(b, sc)] | rom[fo(b, sc) + 1] << 8
            if fl == bf:
                rom[p + 11] = rom[p + 12] = 0xFF; n += 1
    assert 150 < n < 220, n
    log.append('trainers kept after their battle: %d objects' % n)
    # ---- Cerulean Mart: Red's man (3,4) -> (4,2)
    hit = [p for p, o in db.maps[MART]['ev']['objs'] if rom[p] == 0x23 and (rom[p + 2] - 4, rom[p + 1] - 4) == (3, 4)]
    assert len(hit) == 1
    rom[hit[0] + 1] = 2 + 4; rom[hit[0] + 2] = 4 + 4
    log.append('Cerulean Mart: man (3,4) -> (4,2)')
    # ---- Bill
    o1 = fo(BB, BMON_END); o2 = fo(BB, PC_END)
    assert rom[o1:o1 + 6] == bytes.fromhex('6d 02 33 35 08 90'), rom[o1:o1 + 6].hex()
    assert rom[o2:o2 + 10] == bytes.fromhex('84 1f 00 85 6e 03 33 36 08 90'), rom[o2:o2 + 10].hex()
    assert rom[fo(BB, BHUM):fo(BB, BHUM) + 2] == bytes([0x6A, 0x47])
    f, nfree = bank_free_tail(rom, BB); f += 4
    base = 0x4000 + f % 0x4000
    a = Asm(base)
    # Bill (Pokémon) walks into the machine
    a.label('mon')
    a.db(0x1C, 0x09); a.ifequal(0, 'around')                     # readvar VAR_FACING / ifequal DOWN
    a.applymovement(2, 'up3'); a.sjump('gone')
    a.label('around'); a.applymovement(2, 'round')
    a.label('gone'); a.disappear(2); a.setevent(0x835); a.end()
    a.label('up3'); a.db(0x0D, 0x0D, 0x0D, 0x47)
    a.label('round'); a.db(0x0F, 0x0D, 0x0D, 0x0E, 0x0D, 0x47)
    # the Cell Separator
    a.label('pc')
    a.pause(16); a.playsound(SFX_GLASS_TING); a.waitsfx()           # pause n = 2n frames (Yellow: 32 / 80 / 48 / 32 / 8)
    a.pause(40); a.playsound(SFX_WARP_TO); a.waitsfx()
    a.pause(24); a.playsound(SFX_GLASS_TING); a.waitsfx()
    a.pause(16); a.playsound(SFX_ITEM); a.waitsfx()
    a.moveobject(3, 1, 2); a.appear(3); a.setevent(0x836); a.pause(4)
    a.applymovement(3, 'out')
    a.applymovement(0, 'right3')
    a.turnobject(3, 0); a.turnobject(0, 1)                         # Bill faces down, the player up
    a.sjump(BHUM)
    a.label('out'); a.db(0x0C, 0x0F, 0x0F, 0x0F, 0x0C, 0x47)
    a.label('right3'); a.db(0x0F, 0x0F, 0x0F, 0x47)
    code = a.done()
    assert len(code) + 16 < nfree, (len(code), nfree)
    rom[f:f + len(code)] = code
    L = a.labels
    rom[o1:o1 + 6] = bytes([0x03, L['mon'] & 0xFF, L['mon'] >> 8, 0x90, 0x90, 0x90])       # sjump
    rom[o2:o2 + 10] = bytes([0x03, L['pc'] & 0xFF, L['pc'] >> 8]) + b'\x90' * 7
    log.append("Bill's house: %02X:%04X (walk into the machine), %02X:%04X (PC, Bill comes out)" % (BB, L['mon'], BB, L['pc']))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2_ = orig + bytes(len(rom) - len(orig))
    p = ips(o2_, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
