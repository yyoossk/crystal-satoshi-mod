"""tiny SM83 assembler for the few instructions the MOD's small routines need (labels, jr/jp/call)"""
class MA:
    def __init__(s, base): s.base = base; s.b = bytearray(); s.L = {}; s.fx = []
    def here(s): return s.base + len(s.b)
    def label(s, n): s.L[n] = s.here()
    def __call__(s, *v):
        for x in v:
            if isinstance(x, tuple):           # ('jr', label) / ('a16', label)
                k, n = x; s.fx.append((len(s.b), k, n)); s.b += b'\0' if k == 'jr' else b'\0\0'
            else: s.b.append(x)
    def done(s):
        for off, k, n in s.fx:
            a = s.L[n]
            if k == 'jr':
                d = a - (s.base + off + 1); assert -128 <= d < 128, n; s.b[off] = d & 0xFF
            else: s.b[off] = a & 0xFF; s.b[off + 1] = a >> 8
        return bytes(s.b)
