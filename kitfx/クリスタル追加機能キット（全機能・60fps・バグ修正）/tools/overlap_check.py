#!/usr/bin/env python3
# この キットの 追加機能と、ほかの パッチの 書きかえが ROM の 同じ 場所に ぶつかって いないか 調べる
#   python3 tools/overlap_check.py <元の クリスタル base.gbc> <ほかの パッチを 当てた ROM> <この キットで 組んだ ROM（元の base.gbc に）>
# 出力：両方が 元と ちがう バイトの はんい（ぶつかり）と、近く（16バイト いない）で 両方が かえて いる 所
import sys
a=open(sys.argv[1],'rb').read(); o=open(sys.argv[2],'rb').read(); k=open(sys.argv[3],'rb').read()
n=min(len(a),len(o),len(k))
def ranges(mask):
    r=[]; i=0
    while i<n:
        if mask(i):
            j=i
            while j+1<n and mask(j+1): j+=1
            r.append((i,j)); i=j+1
        else: i+=1
    return r
other=[i for i in range(n) if o[i]!=a[i]]; ours=[i for i in range(n) if k[i]!=a[i]]
so=set(other); sk=set(ours)
def fmt(i,j): b=i//0x4000; ad=i if b==0 else 0x4000+i%0x4000; return '$%02x:%04x〜%04x（%dバイト）'%(b,ad,ad+(j-i),j-i+1)
both=ranges(lambda i:i in so and i in sk)
print('ほかの パッチが かえた バイト：%d、この キットが かえた バイト：%d'%(len(other),len(ours)))
print('■ 両方が かえた 所（ぶつかり）：%d か所'%len(both))
for i,j in both: print('  ',fmt(i,j))
near=[]
ko=ranges(lambda i:i in sk)
for i,j in ko:
    if any((x in so) for x in range(max(0,i-16),min(n,j+17))) and not any(i<=x<=j and x in so for x in range(i,j+1)):
        near.append((i,j))
print('■ 近くで 両方が かえて いる 所（たしかめる）：%d か所'%len(near))
for i,j in near: print('  ',fmt(i,j))
