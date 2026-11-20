#!/usr/bin/env python3
"""MBC5 version (2026-11-20 「MBC30からMBC5に変更版を作って」): the same game on an MBC5 cartridge header, for emulators
and flash carts without MBC30 (MBC3 with 4 MB ROM and 64 KB SRAM).
 * header: cartridge type $10 (MBC3+TIMER+RAM+BATTERY) -> $1B (MBC5+RAM+BATTERY); ROM 4 MB / SRAM 64 KB stay.
   The game writes its ROM bank to $2000 (MBC5's low 8 bits; nothing writes $3000-$3FFF) and its SRAM bank (0-7)
   to $4000, as MBC5 needs.
 * MBC5 has no real-time clock, and MBC3's clock registers ($08-$0C written to $4000) would select SRAM banks on
   MBC5 (and write the save).  So:
   - GetClock / SetClock (home) farcall a software clock (asm/mbc5_clock.asm): the clock is the game time
     (wGameTime, counted while playing, saved with the game) minus a base in SRAM bank 0 ($AC81-$AC85, unused bytes
     after sRTCStatusFlags).  SetClock (the clock reset, the 140-day wrap) moves the base.  The clock's day /
     hour / minute run while playing; it stops while the game is off (and with the game time at 999:59:59).
   - StopRTC / StartRTC: ret.  SaveRTC: keeps clearing sRTCStatusFlags, without the clock register.
     (LatchClock writes $6000-$7FFF: nothing on MBC5.)
usage: build_mbc5.py IN.gbc OUT.gbc OUT.ips
"""
import os, sys, re, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from build_phase52 import rgbds

CODE_BANK = 0x8F
ASM = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'asm', 'mbc5_clock.asm')


def expect(rom, o, hexs):
    b = bytes.fromhex(hexs.replace(' ', ''))
    assert rom[o:o + len(b)] == b, (hex(o), rom[o:o + len(b)].hex(' '), hexs)
    return b


def w16(v): return bytes([v & 0xFF, v >> 8])


def main():
    src, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src, 'rb').read())
    assert len(rom) == 0x400000 and rom[0x147] == 0x10 and rom[0x148] == 7 and rom[0x149] == 5
    # the software clock
    o = bank_free_tail(rom, CODE_BANK)[0] + 2
    caddr = 0x4000 + (o - CODE_BANK * 0x4000)
    with tempfile.TemporaryDirectory() as d:
        open(d + '/in.gbc', 'wb').write(rom)
        subprocess.run([rgbds('rgbasm'), '-D', 'CODE_BANK=$%X' % CODE_BANK, '-D', 'CODE_ADDR=$%X' % caddr,
                        '-o', d + '/a.o', ASM], check=True)
        subprocess.run([rgbds('rgblink'), '-O', d + '/in.gbc', '-o', d + '/out.gbc', '-n', d + '/out.sym', d + '/a.o'],
                       check=True)
        new = bytearray(open(d + '/out.gbc', 'rb').read())
        sym = {l.split()[1]: int(l.split()[0].split(':')[1], 16) for l in open(d + '/out.sym')
               if re.match(r'[0-9a-f]+:[0-9a-f]+ ', l)}
    assert len(new) == len(rom)
    diff = [i for i in range(len(rom)) if rom[i] != new[i]]
    assert diff and min(diff) >= o and max(diff) < (CODE_BANK + 1) * 0x4000, (hex(min(diff)), hex(max(diff)))
    rom[:] = new
    # GetClock (00:05B7) / SetClock (00:0691): farcall
    expect(rom, 0x5B7, '3e 0a ea 00 00 cd 9c 05 21 00 40 11 00 a0 36 08 1a e6 3f e0 91')
    expect(rom, 0x691, '3e 0a ea 00 00 cd 9c 05 21 00 40 11 00 a0 36 0c 1a cb 77 12 36 08')
    for at, name in ((0x5B7, 'SoftGetClock'), (0x691, 'SoftSetClock')):
        rom[at:at + 7] = bytes([0x3E, CODE_BANK, 0x21]) + w16(sym[name]) + bytes([0xCF, 0xC9])
    # StopRTC / StartRTC (05:4000 / 05:4019): ret ; SaveRTC (05:406A): no clock register
    expect(rom, 0x14000, '3e 0a ea 00 00 cd 9c 05 3e 0c ea 00 40 fa 00 a0 cb f7 ea 00 a0 cd ad 2f c9')
    expect(rom, 0x14019, '3e 0a ea 00 00 cd 9c 05 3e 0c ea 00 40 fa 00 a0 cb b7 ea 00 a0 cd ad 2f c9')
    rom[0x14000] = 0xC9; rom[0x14019] = 0xC9
    rom[0x14008:0x1400D] = bytes(5); rom[0x14021:0x14026] = bytes(5)   # (unreached) clock register select
    expect(rom, 0x1406A, '3e 0a ea 00 00 cd 9c 05 21 00 a0 3e 0c ea 00 40 cb be 3e 00 ea 00 40 af ea 80 ac cd ad 2f c9')
    rom[0x1406A + 11:0x1406A + 18] = bytes(7)
    # no other writes of the clock registers to $4000
    left = [m.start() for m in re.finditer(rb'\x3e[\x08-\x0c]\xea\x00\x40', rom)]
    assert not left, [hex(x) for x in left]
    # header
    rom[0x147] = 0x1B
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('MBC5: clock %02X:%04X / %04X' % (CODE_BANK, sym['SoftGetClock'], sym['SoftSetClock']))


if __name__ == '__main__':
    main()
