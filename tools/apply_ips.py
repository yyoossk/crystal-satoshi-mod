#!/usr/bin/env python3
"""usage: apply_ips.py IN.gbc PATCH.ips OUT.gbc"""
import sys
rom = bytearray(open(sys.argv[1], 'rb').read()); p = open(sys.argv[2], 'rb').read(); i = 5
assert p[:5] == b'PATCH'
while p[i:i + 3] != b'EOF':
    o = int.from_bytes(p[i:i + 3], 'big'); n = int.from_bytes(p[i + 3:i + 5], 'big'); i += 5
    if n == 0:
        r = int.from_bytes(p[i:i + 2], 'big'); data = bytes([p[i + 2]]) * r; i += 3
    else:
        data = p[i:i + n]; i += n
    if o + len(data) > len(rom): rom += bytes(o + len(data) - len(rom))
    rom[o:o + len(data)] = data
open(sys.argv[3], 'wb').write(rom)
