import sys
from jpchar import encode, decode
from lib import JP_BASE
rom = open(sys.argv[1], 'rb').read()
for s in sys.argv[2:]:
    e = encode(s).rstrip(b'\x50')
    i = rom.find(e)
    while i >= 0:
        st = i
        while st > 0 and rom[st-1] not in (0x50, 0x57, 0x58) and i - st < 300: st -= 1
        en = rom.find(b'\x57', i); en2 = rom.find(b'\x50', i)
        en = min(x for x in (en, en2, i+400) if x >= 0)
        print('%02X:%04X' % (st // 0x4000, st % 0x4000 + (0x4000 if st >= 0x4000 else 0)), repr(s), decode(rom[st:en+1], False)[:600])
        i = rom.find(e, i + 1)
