"""Read Gen I (Pikachu full-color hack) map headers, text tables and texts."""
import sys, os
SC = os.environ.get('MODROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F=open(SC+'/pkfc/pkfc.gbc','rb').read()
PTRS=0xFC1F2; BANKS=0xFC3E4
def fo(b,a): return a if a<0x4000 else b*0x4000+a-0x4000
def header(mapid):
    b=F[BANKS+mapid]; p=F[PTRS+2*mapid]|F[PTRS+2*mapid+1]<<8; o=fo(b,p)
    h=dict(bank=b,off=o,tileset=F[o],h=F[o+1],w=F[o+2],blk=F[o+3]|F[o+4]<<8,texts=F[o+5]|F[o+6]<<8,script=F[o+7]|F[o+8]<<8,conn=F[o+9])
    n=bin(h['conn']&0xF).count('1'); q=o+10+11*n
    h['objects']=F[q]|F[q+1]<<8
    return h
def text_ptr(mapid, tid):
    h=header(mapid); t=fo(h['bank'],h['texts'])+2*(tid-1)
    return h['bank'], F[t]|F[t+1]<<8
def text_body(bank, ptr):
    """return (kind, body) where body is text bytes (starting at 0x00 cmd) without terminator"""
    o=fo(bank,ptr)
    if F[o]==0x17:
        fp=F[o+1]|F[o+2]<<8; fb=F[o+3]; t=fo(fb,fp)
    elif F[o]==0x00: t=o
    else: return ('asm',o)
    i=t
    while F[i] not in (0x57,0x58,0x50): i+=1
    return ('text',F[t:i])
