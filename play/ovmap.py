import re,sys
def sections(mapf):
    secs=[]; bank=None
    for l in open(mapf,encoding='utf-8'):
        m=re.match(r'ROM[0X] bank #(\d+):',l)
        if m: bank=int(m.group(1)); continue
        m=re.match(r'\s+SECTION: \$(\w+)-\$(\w+) \(\$\w+ bytes\) \["(.*)"\]',l)
        if m: secs.append((bank,int(m.group(1),16),int(m.group(2),16),m.group(3)))
    return secs
if __name__=='__main__':
  secs=sections(sys.argv[1])
  for l in open(sys.argv[2],encoding='utf-8'):
      m=re.search(r'\$(\w\w):(\w+)〜(\w+)',l)
      if not m: continue
      b=int(m.group(1),16); a=int(m.group(2),16); e=int(m.group(3),16)
      hit=[s[3] for s in secs if s[0]==b and s[1]<=e and a<=s[2]]
      print(l.strip(), '=>', hit)
