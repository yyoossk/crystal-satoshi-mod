#!/usr/bin/env python3
"""Phase 51: Crystal's Blue (グリーン) is Shigeru: the Viridian Gym leader after the Kanto Hall of Fame (his lines,
the trainer's name), the phone caller who speaks of "Oak's grandson, the former champion".  (The Green Badge keeps
its name.)
usage: build_phase51.py IN.gbc OUT.gbc OUT.ips
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import *
from jpchar import encode
from evedit import copy_text
import build_phase13 as P13
import build_phase17 as P17

BLUE = 0x40


def T(s): return encode('{00}' + s) + b'\x57'


TEXTS = {
    (0x77, 0x69D3): 'シゲル{72}よお　<PLAYER>！<PARA>サカキの　かわりに<LINE>オレが　この　トキワジムの<CONT>ジムリーダーに　なったのさ！<PARA>'
                    'チャンピオンの　ときは<LINE>おまえに　まけたけど<CONT>こんどは　そうは　いかないぜ！<PARA>いくぜ！　<PLAYER>！',
    (0x77, 0x6A83): 'シゲル{72}バカなっ！<PARA>オレが　また　おまえに<LINE>まける　なんてっ！！<PARA><……>　ちっ　しょうがねえ<LINE>'
                    'バッジは　もう<CONT>もってるんだったな',
    (0x77, 0x6ACC): '<PLAYER>は　シゲルに<LINE>みとめられた！',
}


def main():
    src_rom, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src_rom, 'rb').read())
    log = []
    for (b, a), s in TEXTS.items():
        o = fo(b, a); old = copy_text(rom, o); new = T(s)
        assert len(new) <= len(old), (hex(b), hex(a), len(old), len(new))
        rom[o:o + len(new)] = new
    ko, kn = encode('グりーン').rstrip(b'\x50'), encode('シゲル').rstrip(b'\x50')
    for b, a in ((0x77, 0x6AE3), (0x77, 0x6B38), (0x5D, 0x6A2B)):          # the name only (bytes kept)
        o = fo(b, a); old = copy_text(rom, o); i = old.index(ko)
        new = old[:i] + kn + old[i + len(ko):]
        if b == 0x5D: new = new.replace(encode('さんって').rstrip(b'\x50'), encode('くんって').rstrip(b'\x50'))
        rom[o:o + len(new)] = new
    grp = P13.read_groups7e(rom)
    n = 0
    for p in grp[BLUE - 1]:
        if p[0] == encode('グりーン@'): p[0] = encode('シゲル@'); n += 1
    assert n >= 1
    log.append('Blue -> Shigeru: %d texts, %d parties (bank 7E free %d)' % (len(TEXTS), n, P13.write_groups7e(rom, grp)))
    P17.fix_outdoor_sprites(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    open(outips, 'wb').write(ips(orig, bytes(rom)))
    print('\n'.join(log))


if __name__ == '__main__':
    main()
