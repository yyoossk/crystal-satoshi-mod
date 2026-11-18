"""walk into every warp of every map (post-game save): from a walkable tile next to it, step in; carpets: press their direction"""
import sys,os,json; R=sys.argv[1]; ONLY=sys.argv[2] if len(sys.argv)>2 else None; sys.argv=['x']; sys.path.insert(0,'play'); os.environ['PTROM']=R
import bot, pt as P, hon as Hn
from bot import grid_of, WALK
OUT='/tmp/wt/r_%s.jsonl'%R
done=set()
import glob
for F in glob.glob('/tmp/wt/r_%s*.jsonl'%R):
    for l in open(F): d=json.loads(l); done.add((tuple(d['k']),d['i']))
b=bot.Bot(state='play/pt_h_jrematch.st', out='/tmp/wtx'); b.fs=[]; b.seen=set(); b.tag='w'; print('start',b.where(),flush=True)
base='/tmp/wt/base_%s_%s.st'%(R,os.getpid()); b.g.save_state(base)
DV={'U':(0,-1),'D':(0,1),'L':(-1,0),'R':(1,0)}
CD={0x70:'D',0x76:'L',0x78:'U',0x7E:'R'}
keys=sorted(b.db.maps)
LST=json.load(open(os.environ['LIST'])) if os.environ.get('LIST') else None
if LST is not None: keys=sorted({tuple(x[0]) for x in LST})
SH=os.environ.get('SHARD')
if SH: a_,n_=map(int,SH.split('/')); keys=[k for j,k in enumerate(keys) if j%n_==a_]
if ONLY: keys=[tuple(json.loads(ONLY))] if ONLY.startswith('[') else keys
f=open(OUT,'a')
for k in keys:
    m=b.db.maps[k]
    try: G=grid_of(b.db.r,m['hdr'])
    except Exception: continue
    W=m['ev']['warps']
    for i,(o,w) in enumerate(W):
        if (k,i) in done: continue
        if LST is not None and [list(k),i] not in LST: continue
        wy,wx=w[0],w[1]
        if not(0<=wy<len(G) and 0<=wx<len(G[0])): continue
        c=G[wy][wx]; cd=CD.get(c)
        order=([cd] if cd else [])+[d for d in 'UDLR' if d!=cd]
        res='noapproach'; how=None
        for d in order:
            dx,dy=DV[d]; ax,ay=wx-dx,wy-dy
            if not(0<=ay<len(G) and 0<=ax<len(G[0])) or G[ay][ax] not in WALK: continue
            b.g.load_state(base); b.wait(2)
            b.warp(k,ax,ay,wait=120)
            if b.where()!=(k,ax,ay):
                if not Hn.warp_to(b,k,ax,ay) or b.where()[1:]!=(ax,ay): res='nowarp'; continue
            b.bank1(); b.g.poke(P.W_REPEL,250)
            b.g.down(d); b.wait(20); b.g.up(d); b.wait(70)
            if b.textbox(): P.ev(b,5)
            wh=b.where()
            if wh[0]!=k or abs(wh[1]-wx)+abs(wh[2]-wy)>2: res='ok'; how=d; break
            if b.where()[1:]==(wx,wy):
                dd=cd or d
                b.g.down(dd); b.wait(24); b.g.up(dd); b.wait(70)
                wh=b.where()
                if wh[0]!=k or abs(wh[1]-wx)+abs(wh[2]-wy)>2: res='ok'; how=d+'+'+dd; break
            res='fail'
            break
        rec={'k':list(k),'name':b.names.get(k),'i':i,'xy':[wx,wy],'coll':c,'res':res,'how':how}
        f.write(json.dumps(rec,ensure_ascii=False)+'\n'); f.flush()
print('done')
