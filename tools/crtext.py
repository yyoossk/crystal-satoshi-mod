"""Crystal text-command parser (length and readable dump) for copying texts between ROMs."""
from jpchar import decode
def parse(rom, o):
    """returns (end offset exclusive, list of (kind, data))"""
    out = []
    while True:
        c = rom[o]
        if c == 0x00:
            e = o + 1
            while rom[e] not in (0x50, 0x57, 0x58): e += 1
            out.append(('text', decode(bytes(rom[o + 1:e])), rom[e]))
            if rom[e] in (0x57, 0x58): return e + 1, out
            o = e + 1
        elif c == 0x01: out.append(('ram', rom[o + 1] | rom[o + 2] << 8)); o += 3
        elif c == 0x02: out.append(('bcd', bytes(rom[o + 1:o + 4]).hex())); o += 4
        elif c == 0x09: out.append(('dec', bytes(rom[o + 1:o + 4]).hex())); o += 4
        elif c == 0x16: out.append(('far', rom[o + 3], rom[o + 1] | rom[o + 2] << 8)); o += 4
        elif c in (0x05, 0x06, 0x07, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x12, 0x13, 0x0A, 0x14, 0x15):
            out.append(('cmd', c)); o += 1 if c not in (0x14,) else 2
        elif c == 0x50: out.append(('end',)); return o + 1, out
        elif c == 0x08: out.append(('asm',)); return o + 1, out
        else: out.append(('??', c)); return o + 1, out
