from jpchar import decode
R = open(__import__('lib').SC + '/aka/Pocket Monsters - Aka (Japan) (SGB Enhanced).gb', 'rb').read()
def raw(o):
    """text body (from the {00} start) up to, not including, the terminator"""
    e = o
    while R[e] not in (0x50, 0x57, 0x58): e += 1
    return bytes(R[o:e])
def dump(lo, hi):
    o = lo
    while o < hi:
        if R[o] == 0 and R[o + 1] not in (0, 0x50) and R[o+1] >= 0x50:
            b = raw(o); t = decode(b)
            if t[4:30].replace('{72}', '').count('{') == 0 and len(b) > 4:
                print(hex(o), hex(R[o + len(b)]), t[:200]); o += len(b); continue
        o += 1
if __name__ == '__main__':
    import sys; dump(int(sys.argv[1], 16), int(sys.argv[2], 16))
