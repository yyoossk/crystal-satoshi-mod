import collmap
from collections import deque
WALK = {0x00, 0x18, 0x14, 0x10, 0x70, 0x71, 0x7A}
def moves(G, x, y):
    H, W = len(G), len(G[0])
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        nx, ny = x+dx, y+dy
        if not (0 <= nx < W and 0 <= ny < H): continue
        c = G[ny][nx]
        if c in WALK: yield (nx, ny)
        elif c == 0xA3 and dy == 1 and 0 <= ny+1 < H and G[ny+1][nx] in WALK: yield (nx, ny+1)
        elif c == 0xA0 and dx == 1 and G[ny][nx+1] in WALK: yield (nx+1, ny)
        elif c == 0xA1 and dx == -1 and G[ny][nx-1] in WALK: yield (nx-1, ny)
def reach(G, starts, block=()):
    seen = set(starts); q = deque(starts)
    while q:
        p = q.popleft()
        for n in moves(G, *p):
            if n not in seen and n not in block: seen.add(n); q.append(n)
    return seen
