from t64a import *
import os
r = open(os.environ.get("FROM", SC + "/build/p64.gbc"), "rb").read()
fc = r[0xD1F3:0xD1F9]
def vals(b, k, rod, n=24):
    asm = bytes([0x21, 0x00, 0xC7])   # hl = buffer (wram0 C700)
    asm += bytes([0x3E, k[0], 0xEA, 0x7B, 0xDC, 0x3E, k[1], 0xEA, 0x7C, 0xDC])
    asm += bytes([0x0E, n])
    loop = bytes([0xC5, 0xE5, 0x16, 0x01, 0x1E, rod]) + fc + bytes([0xE1, 0x72, 0x23, 0x73, 0x23, 0xC1, 0x0D])
    asm += loop + bytes([0x20, (-(len(loop) + 2)) & 0xFF])
    asm += bytes([0x3E, 24, 0xEA, 0x7B, 0xDC, 0x3E, 4, 0xEA, 0x7C, 0xDC, 0xC9])
    for i, v in enumerate(asm): b.g.cmd('rpoke %x %d' % (SOFF + 0x40 + i, v))
    b.script([0x0E, SB, (SA + 0x40) & 0xFF, (SA + 0x40) >> 8], 120)
    return b.peek(0xC700, 2*n)
if __name__=='__main__':
    b = Bot(state='p64nb.st', out=OUT+'/fish5')
    for k in ((17,1),(26,88),(10,1)):
        for rod in (0,1,2): print(k, rod, vals(b,k,rod), flush=True)
