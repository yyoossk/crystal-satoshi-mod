"""find a US pokecrystal code location in the JP ROM: the US bytes from a label (+off), with 16-bit operands
wildcarded, matched in the JP/MOD ROM"""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import loadsym, fo, PC
US = open(PC + '/pokecrystal.gbc', 'rb').read()
S = loadsym()
IMM16 = {0x01, 0x11, 0x21, 0x31, 0xC2, 0xC3, 0xC4, 0xCA, 0xCC, 0xCD, 0xD2, 0xD4, 0xDA, 0xDC, 0xEA, 0xFA, 0x08}
IMM8 = {0x06, 0x0E, 0x16, 0x1E, 0x26, 0x2E, 0x36, 0x3E, 0x18, 0x20, 0x28, 0x30, 0x38, 0xC6, 0xCE, 0xD6, 0xDE, 0xE6,
        0xEE, 0xF6, 0xFE, 0xE0, 0xF0, 0xE8, 0xF8, 0xCB}
def us_off(label, off=0):
    b, a = S[label]; return fo(b, a) + off
def pattern(o, n, wild_far=True):
    """regex for US bytes [o, o+n): 16-bit operands -> any 2 bytes; rst $08 (farcall) args too"""
    out = b''; i = o
    while i < o + n:
        op = US[i]
        if op in IMM16: out += re.escape(bytes([op])) + b'..'; i += 3
        elif op in IMM8: out += re.escape(bytes([op, US[i + 1]])); i += 2
        else: out += re.escape(bytes([op])); i += 1
    return out
def find(rom, label, off=0, n=16, bank=None):
    o = us_off(label, off); p = pattern(o, n)
    hits = [m.start() for m in re.finditer(p, rom, re.S)]
    if bank is not None: hits = [h for h in hits if h // 0x4000 == bank]
    return hits
if __name__ == '__main__':
    rom = open(sys.argv[1], 'rb').read()
    for lab in sys.argv[2:]:
        l, _, off = lab.partition('+')
        print(lab, [hex(h) for h in find(rom, l, int(off or '0', 0))])
