"""Disassembler for JP Crystal map scripts (table from pokecrystal macros; JP op = US op, minus 1 for US >= 0x53)."""
import re, sys
from lib import *
SRC = open(PC + '/macros/scripts/events.asm', encoding='utf-8').read()
OPS = {}
for m in re.finditer(r'const (\w+)_command\s*;\s*\$([0-9a-f]+)\s*\nMACRO \w+\n(.*?)ENDM', SRC, re.S):
    name, us, body = m.group(1), int(m.group(2), 16), '\n' + m.group(3)
    args = []
    body = re.sub(r'\n\s*if [^\n]*\n(?:(?!\belse\b|\bendc\b).)*?\belse\b', '', body, flags=re.S)   # optional args: keep the full form
    body = re.sub(r'\n\s*if .*?endc', '', body, flags=re.S)
    for l in body.split('\n'):
        l = l.strip()
        k = l.split()[0] if l else ''
        if k in ('db', 'dw', 'dba', 'dn', 'dbw', 'dwb') and '_command' not in l:
            n = l.split(';')[0][len(k):].count(',') + 1
            args.append({'db': [1] * n, 'dw': [2] * n, 'dba': [3], 'dn': [1], 'dbw': [1, 2], 'dwb': [2, 1]}[k])
    if us == 0x52: continue
    jp = us if us < 0x52 else us - 1
    OPS[jp] = (name, [x for a in args for x in a])
ENDS = {'end', 'sjump', 'farsjump', 'endcallback', 'jumptext', 'jumptextfaceplayer', 'jumpstd', 'endall', 'return', 'memjump'}


def dis(rom, bank, addr, n=60, follow=False):
    out = []; o = fo(bank, addr)
    for _ in range(n):
        op = rom[o]
        if op not in OPS: out.append('%04X: ?? %02X' % (addr, op)); break
        name, sz = OPS[op]; p = o + 1; vals = []
        for s in sz:
            v = int.from_bytes(rom[p:p + s], 'little') if s != 3 else (rom[p], rom[p + 1] | rom[p + 2] << 8)
            vals.append(('%X:%04X' % v) if s == 3 else ('%04X' % v if s == 2 else '%02X' % v)); p += s
        out.append('%04X: %s %s' % (addr, name, ', '.join(vals)))
        addr += p - o; o = p
        if name in ENDS and not follow: break
    return out


if __name__ == '__main__':
    rom = open(sys.argv[1], 'rb').read()
    print('\n'.join(dis(rom, int(sys.argv[2], 16), int(sys.argv[3], 16), int(sys.argv[4]) if len(sys.argv) > 4 else 80, True)))
