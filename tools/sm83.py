"""Small SM83 (Game Boy CPU) disassembler for reading ROM code."""
R8 = ['b', 'c', 'd', 'e', 'h', 'l', '[hl]', 'a']
R16 = ['bc', 'de', 'hl', 'sp']
R16S = ['bc', 'de', 'hl', 'af']
CC = ['nz', 'z', 'nc', 'c']
ALU = ['add a,', 'adc a,', 'sub', 'sbc a,', 'and', 'xor', 'or', 'cp']
CB = ['rlc', 'rrc', 'rl', 'rr', 'sla', 'sra', 'swap', 'srl']


def one(rom, o, pc):
    """(text, length) of the instruction at file offset o (pc = its address)"""
    op = rom[o]; n8 = rom[o + 1] if o + 1 < len(rom) else 0
    n16 = n8 | (rom[o + 2] << 8 if o + 2 < len(rom) else 0)
    def rel(): return pc + 2 + (n8 - 256 if n8 > 127 else n8)
    x, y, z = op >> 6, (op >> 3) & 7, op & 7
    if op == 0x00: return 'nop', 1
    if op == 0x08: return 'ld [$%04X], sp' % n16, 3
    if op == 0x10: return 'stop', 2
    if op == 0x18: return 'jr $%04X' % rel(), 2
    if x == 0 and z == 0 and y >= 4: return 'jr %s, $%04X' % (CC[y - 4], rel()), 2
    if x == 0 and z == 1: return ('ld %s, $%04X' % (R16[y >> 1], n16), 3) if y % 2 == 0 else ('add hl, %s' % R16[y >> 1], 1)
    if x == 0 and z == 2:
        t = ['[bc]', '[de]', '[hl+]', '[hl-]'][y >> 1]
        return ('ld %s, a' % t, 1) if y % 2 == 0 else ('ld a, %s' % t, 1)
    if x == 0 and z == 3: return ('inc ' if y % 2 == 0 else 'dec ') + R16[y >> 1], 1
    if x == 0 and z == 4: return 'inc ' + R8[y], 1
    if x == 0 and z == 5: return 'dec ' + R8[y], 1
    if x == 0 and z == 6: return 'ld %s, $%02X' % (R8[y], n8), 2
    if x == 0 and z == 7: return ['rlca', 'rrca', 'rla', 'rra', 'daa', 'cpl', 'scf', 'ccf'][y], 1
    if op == 0x76: return 'halt', 1
    if x == 1: return 'ld %s, %s' % (R8[y], R8[z]), 1
    if x == 2: return '%s %s' % (ALU[y], R8[z]), 1
    if x == 3:
        if z == 0 and y < 4: return 'ret ' + CC[y], 1
        if op == 0xE0: return 'ldh [$FF%02X], a' % n8, 2
        if op == 0xE8: return 'add sp, %d' % (n8 - 256 if n8 > 127 else n8), 2
        if op == 0xF0: return 'ldh a, [$FF%02X]' % n8, 2
        if op == 0xF8: return 'ld hl, sp%+d' % (n8 - 256 if n8 > 127 else n8), 2
        if z == 1:
            if y % 2 == 0: return 'pop ' + R16S[y >> 1], 1
            return ['ret', 'reti', 'jp hl', 'ld sp, hl'][y >> 1], 1
        if z == 2 and y < 4: return 'jp %s, $%04X' % (CC[y], n16), 3
        if op == 0xE2: return 'ld [c], a', 1
        if op == 0xEA: return 'ld [$%04X], a' % n16, 3
        if op == 0xF2: return 'ld a, [c]', 1
        if op == 0xFA: return 'ld a, [$%04X]' % n16, 3
        if op == 0xC3: return 'jp $%04X' % n16, 3
        if op == 0xCB:
            c = n8; cx, cy, cz = c >> 6, (c >> 3) & 7, c & 7
            if cx == 0: return '%s %s' % (CB[cy], R8[cz]), 2
            return '%s %d, %s' % (['', 'bit', 'res', 'set'][cx], cy, R8[cz]), 2
        if op == 0xF3: return 'di', 1
        if op == 0xFB: return 'ei', 1
        if z == 4 and y < 4: return 'call %s, $%04X' % (CC[y], n16), 3
        if z == 5:
            if y % 2 == 0: return 'push ' + R16S[y >> 1], 1
            if op == 0xCD: return 'call $%04X' % n16, 3
        if z == 6: return '%s $%02X' % (ALU[y], n8), 2
        if z == 7: return 'rst $%02X' % (y * 8), 1
    return 'db $%02X' % op, 1


def dis(rom, bank, addr, n=40, stop_ret=False):
    o = addr if addr < 0x4000 else bank * 0x4000 + addr - 0x4000
    out = []
    for _ in range(n):
        t, l = one(rom, o, addr)
        out.append('%02X:%04X  %-9s %s' % (bank, addr, rom[o:o + l].hex(), t))
        o += l; addr += l
        if stop_ret and t in ('ret', 'reti') or t.startswith('jp $') and stop_ret: break
    return '\n'.join(out)
