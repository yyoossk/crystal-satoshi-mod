#!/usr/bin/env python3
"""Phase 67: scripts in ROM banks $80 and up (this MOD is 4MB: the kit's banks were moved to $80-$9B) can call
subscripts. Crystal's script engine keeps bit 7 of the bank in the call stack as a marker for map callbacks
(CallCallback ORs $80 into the caller's bank; ExitScriptSubroutine ANDs $7F when it returns), so a script in bank
$80+ came back to the wrong bank ($99 -> $19) after showemote / scall / farscall / callstd / verbosegiveitem etc.
(talking to the follower ran garbage after its emote: the screen faded and the player walked by itself).
Nothing reads the marker, so CallCallback no longer sets it and ExitScriptSubroutine keeps all 8 bits.
  $25:$74F4  or $80  -> or $00
  $25:$7B8B  and $7F -> and $FF
usage: build_phase67.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    a = fo(0x25, 0x74F1); assert rom[a:a + 8] == bytes([0xFA, 0x2A, 0xD4, 0xF6, 0x80, 0xEA, 0x2A, 0xD4]) == orig[a:a + 8]   # CallCallback
    rom[a + 4] = 0x00
    a = fo(0x25, 0x7B88); assert rom[a:a + 7] == bytes([0x2A, 0x47, 0xE6, 0x7F, 0xEA, 0x2A, 0xD4]) == orig[a:a + 7]         # ExitScriptSubroutine
    rom[a + 3] = 0xFF
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)


if __name__ == '__main__':
    main()
