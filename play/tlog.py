import bot
from jpchar import decode
seen=[]
def txt(s):
    t=s.tilemap(); lines=[]
    for r in (14,16):
        l=decode(t[r*20+1:r*20+19], stop_at_end=False).strip()
        if l: lines.append(l)
    j=' / '.join(lines)
    if j and (not seen or seen[-1]!=j):
        if seen and j.startswith(seen[-1]): seen[-1]=j
        else: print('  T', s.where()[0], seen[-1] if seen else '', flush=True)
        seen.append(j)
op=bot.Bot.press
def press(s,*a,**k):
    try: txt(s)
    except Exception: pass
    return op(s,*a,**k)
bot.Bot.press=press
