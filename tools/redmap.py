"""JP Red (赤) map headers and text tables, same interface as pkmap (which reads the Pikachu full-color hack)"""
import redtexts as RT
R = RT.R
PTRS, BANKS = 0x1BCB, 0xC883          # MapHeaderPointers / MapHeaderBanks in JP Red
def fo(b, a): return a if a < 0x4000 else b * 0x4000 + a - 0x4000
def header(mapid):
    b = R[BANKS + mapid]; p = R[PTRS + 2 * mapid] | R[PTRS + 2 * mapid + 1] << 8; o = fo(b, p)
    h = dict(bank=b, off=o, tileset=R[o], h=R[o + 1], w=R[o + 2], blk=R[o + 3] | R[o + 4] << 8,
             texts=R[o + 5] | R[o + 6] << 8, script=R[o + 7] | R[o + 8] << 8, conn=R[o + 9])
    n = bin(h['conn'] & 0xF).count('1'); q = o + 10 + 11 * n
    h['objects'] = R[q] | R[q + 1] << 8
    return h
def text_ptr(mapid, tid):
    h = header(mapid); t = fo(h['bank'], h['texts']) + 2 * (tid - 1)
    return h['bank'], R[t] | R[t + 1] << 8
def text_body(bank, ptr):
    """(kind, body): body = text bytes from the {00} start, without the terminator; or ('asm', offset)"""
    o = fo(bank, ptr)
    if R[o] == 0x17: t = fo(R[o + 3], R[o + 1] | R[o + 2] << 8)
    elif R[o] == 0x00: t = o
    else: return ('asm', o)
    i = t
    while R[i] not in (0x57, 0x58, 0x50): i += 1
    return ('text', bytes(R[t:i]))
def asm_texts(mapid, tid, n=200):
    """text bodies referenced by `ld hl, text` inside a text_asm"""
    b, p = text_ptr(mapid, tid); k, o = text_body(b, p); assert k == 'asm'
    out = []
    for i in range(o, o + n):
        if R[i] == 0x21:
            pp = R[i + 1] | R[i + 2] << 8
            if 0x4000 <= pp < 0x8000:
                kk, bb = text_body(b, pp)
                if kk == 'text' and bb not in out: out.append(bb)
    return out


def asm_hl(mapid, tid, n=160, stop=True):
    """operands of every `ld hl, $4000-$7FFF` inside a text_asm, in code order (bank, ptr)"""
    b, p = text_ptr(mapid, tid); k, o = text_body(b, p); assert k == 'asm'
    out = []
    for i in range(o, o + n):
        if R[i] == 0x21:
            pp = R[i + 1] | R[i + 2] << 8
            if 0x4000 <= pp < 0x8000 and (b, pp) not in out: out.append((b, pp))
        if stop and R[i] == 0xC3 and R[i + 1:i + 3] == bytes([0x6A, 0x0F]): break      # jp TextScriptEnd
    return out


def crystal_text(bank, ptr):
    """a Gen I text script (text_start / text_far / sounds / text_waitbutton / text_end) as Crystal text bytes"""
    out = bytearray(); o = fo(bank, ptr)
    while True:
        c = R[o]
        if c == 0x00 or c == 0x17:
            if c == 0x17: t = fo(R[o + 3], R[o + 1] | R[o + 2] << 8); o += 4
            else: t = o; o = None
            out.append(0x00); t += 1
            while R[t] not in (0x50, 0x57, 0x58): out.append(R[t]); t += 1
            if R[t] != 0x50: out.append(R[t]); return bytes(out)
            out.append(0x50)
            if o is None: o = t + 1
        elif c in (0x0B, 0x11, 0x12, 0x13): out.append(0x0F); o += 1     # sounds -> Crystal sound_item
        elif c == 0x0D: out.append(0x0D); o += 1                         # text_waitbutton
        elif c == 0x50: out.append(0x50); return bytes(out)
        else: raise ValueError('gen1 text command %02X at %X' % (c, o))
