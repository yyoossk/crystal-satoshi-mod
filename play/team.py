"""the League team the user asked for: six Pokémon at Lv 100 (max DVs and stat exp, PP Up x3), many types"""
import math
R = open('/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad/build/p114.gbc', 'rb').read()
BASE, NAMES, MOVES = 0x514BA, 0x5341A, 0x41C69
PARTY, PCOUNT = 0xDCA5, 0xDC9D
OTN, NICK = PARTY + 6 * 0x30, PARTY + 6 * 0x30 + 6 * 6
M = dict(PSYCHIC=94, ICE_BEAM=58, THUNDERBOLT=85, FLAMETHROWER=53, FIRE_BLAST=126, EARTHQUAKE=89, ROCK_SLIDE=157,
         CRUNCH=242, SURF=57, OUTRAGE=200, SHADOW_BALL=247, SLUDGE_BOMB=188, MEGAHORN=224, CROSS_CHOP=238)
TEAM = [(150, ['PSYCHIC', 'ICE_BEAM', 'THUNDERBOLT', 'FLAMETHROWER']),     # ミュウツー
        (248, ['ROCK_SLIDE', 'EARTHQUAKE', 'CRUNCH', 'FIRE_BLAST']),        # バンギラス
        (149, ['OUTRAGE', 'THUNDERBOLT', 'FIRE_BLAST', 'SURF']),            # カイリュー
        (94, ['SHADOW_BALL', 'SLUDGE_BOMB', 'THUNDERBOLT', 'PSYCHIC']),     # ゲンガー
        (131, ['SURF', 'ICE_BEAM', 'THUNDERBOLT', 'PSYCHIC']),              # ラプラス
        (214, ['MEGAHORN', 'CROSS_CHOP', 'EARTHQUAKE', 'ROCK_SLIDE'])]      # ヘラクロス
EXP100 = {0: 1000000, 1: 847000, 2: 1059860, 3: 1059860, 4: 800000, 5: 1250000}
def mon(sp, moves, otid, L=100):
    bs = R[BASE + 0x20 * (sp - 1):BASE + 0x20 * sp]; assert bs[0] == sp
    st = lambda base, hp=False: (((base + 15) * 2 + 64) * L) // 100 + (L + 10 if hp else 5)
    hp = st(bs[1], True); atk, df, spd, sat, sdf = (st(x) for x in (bs[2], bs[3], bs[4], bs[5], bs[6]))
    mv = [M[m] for m in moves]
    pp = []
    for m in mv:
        b_ = R[MOVES + 7 * (m - 1) + 5]; pp.append(min(63, b_ + 3 * max(1, b_ // 5)) | 0xC0)
    e = EXP100[bs[22]]
    d = bytearray(0x30)
    d[0] = sp; d[1] = 0; d[2:6] = bytes(mv); d[6:8] = otid; d[8:11] = e.to_bytes(3, 'big')
    for i in range(5): d[11 + 2 * i:13 + 2 * i] = b'\xff\xff'
    d[21:23] = b'\xff\xff'; d[23:27] = bytes(pp); d[27] = 255; d[31] = L
    for o, v in ((34, hp), (36, hp), (38, atk), (40, df), (42, spd), (44, sat), (46, sdf)): d[o:o + 2] = v.to_bytes(2, 'big')
    return bytes(d)
def install(b):
    b.bank1(); otid = bytes(b.peek(PARTY + 6, 2)); otname = bytes(b.peek(OTN, 6))
    b.g.poke(PCOUNT, 6)
    for i, (sp, moves) in enumerate(TEAM):
        b.g.poke(PCOUNT + 1 + i, sp)
        for j, v in enumerate(mon(sp, moves, otid)): b.g.poke(PARTY + 0x30 * i + j, v)
        for j, v in enumerate(otname): b.g.poke(OTN + 6 * i + j, v)
        nm = R[NAMES + 5 * (sp - 1):NAMES + 5 * sp] + b'\x50'
        for j, v in enumerate(nm): b.g.poke(NICK + 6 * i + j, v)
    b.g.poke(PCOUNT + 7, 0xFF)
