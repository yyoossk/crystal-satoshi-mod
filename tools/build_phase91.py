#!/usr/bin/env python3
"""Phase 91: Shigeru's battles and blacking out, as in Red.
 * Blacking out before using any Pokémon Center: Red sends the player to Pallet Town, in front of his house (the town's
   fly spot; Red's wLastBlackoutMap starts as PALLET_TOWN).  Crystal sent him to his room (SPAWN_HOME, which also is
   the new game's start): GetWhiteoutSpawn's fallback is SPAWN_PALLET instead.
 * Losing to Shigeru: Red shows a line only in the "Rival1" battles (Oak's lab, Route 22's first, Cerulean City):
   Rival1WinText 「<RIVAL>：やりー！ おれって てんさい？」 (HandlePlayerBlackOut); the lab already used it.  Route 22's
   first battle and Cerulean City used other texts -> Rival1WinText.  The other battles (Route 22's second, ...) show
   nothing in Red: Route 22's second loses its lose text (S.S. Anne, Pokémon Tower, Silph Co., the champion already
   had none).
usage: build_phase91.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import build_phase17 as P17

SPAWN_TABLE = 0x15346              # SpawnPoints (JP): 0 = SPAWN_HOME, 2 = SPAWN_PALLET
WHITEOUT_FALLBACK = 0x123E8        # GetWhiteoutSpawn: ld a,c / jr c,.yes / xor a / .yes ld [wDefaultSpawnpoint],a / ret


def find_all(rom, t):
    out = []; i = rom.find(t)
    while i >= 0: out.append(i); i = rom.find(t, i + 1)
    return out


def text_at(rom, o):
    e = rom.index(0x57, o); return bytes(rom[o:e + 1])


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read()); log = []
    # ---- blackout spawn: GetWhiteoutSpawn (04:63D8) falls back to SPAWN_HOME (the room; also the new game's start)
    # when the last spawn map is no spawn point -> SPAWN_PALLET (Pallet Town 5, 6, in front of the house)
    o = WHITEOUT_FALLBACK
    assert rom[o:o + 8] == bytes.fromhex('79 38 01 af ea 01 d0 c9')
    assert rom[SPAWN_TABLE + 8:SPAWN_TABLE + 12] == bytes([0x0D, 0x02, 5, 6])
    f, n = bank_free_tail(rom, 4); f += 4; assert n >= 16
    rom[f:f + 9] = bytes.fromhex('79 38 02 3e 02 ea 01 d0 c9')   # ld a,c / jr c,+2 / ld a,SPAWN_PALLET / ld [wDefaultSpawnpoint],a / ret
    a_ = 0x4000 + f % 0x4000
    rom[o:o + 3] = bytes([0xC3, a_ & 0xFF, a_ >> 8])
    log.append('whiteout fallback -> SPAWN_PALLET (04:%04X)' % a_)
    # ---- texts (the copies the current scripts use: Route 22 = phase 31's bank 72, Cerulean = bank 62)
    def locate(o, bank):
        hits = [i - 5 for i in find_all(rom, P17.T(o)[5:20]) if i // 0x4000 == bank]
        assert len(hits) == 1, (hex(o), hits); return hits[0]
    lab_lose = locate(0x1D304, 0x62)
    win1 = text_at(rom, lab_lose)                       # 「<RIVAL>：やりー！ おれって てんさい？」
    for o, bank in ((0x5176D, 0x72), (0x19DC5, 0x62)):
        p = locate(o, bank); old = text_at(rom, p)
        assert len(win1) <= len(old), (hex(o), len(win1), len(old))
        rom[p:p + len(win1)] = win1
        log.append('lose text %05X (%02X:%04X) -> Rival1WinText' % (o, bank, 0x4000 + p % 0x4000))
    # Route 22's second battle: winlosstext win, lose -> win, 0
    p = locate(0x518D7, 0x72); ptr = 0x4000 + p % 0x4000
    seg = rom[0x72 * 0x4000:0x73 * 0x4000]
    hits = [i for i in range(len(seg) - 5) if seg[i] == 0x63 and seg[i + 3] == ptr & 0xFF and seg[i + 4] == ptr >> 8]
    assert len(hits) == 2, hits                          # two coord events (y 4 / 5)
    for i in hits:
        rom[0x72 * 0x4000 + i + 3] = 0; rom[0x72 * 0x4000 + i + 4] = 0
    log.append('Route 22 second battle: no lose text (%d)' % len(hits))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
