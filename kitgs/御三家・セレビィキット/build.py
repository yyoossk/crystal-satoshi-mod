# 御三家・セレビィを 組む：python3 build.py <できる ROM> [セレビィだけ…など ほかの asm]
#   base.gbc の 上に 書く。rgbds 1.0.4 の rgbasm・rgblink・rgbfix を PATH に 入れておく。
#   既定は src/legends_crystal.asm（セレビィ＋伝説の 鳥）・src/starters_crystal.asm（カントー御三家）・src/johto3_crystal.asm（ジョウト御三家 3びき）
import subprocess,sys,os,zlib
def run(*a):
    r=subprocess.run(a,capture_output=True,text=True)
    if r.returncode: print(r.stdout,r.stderr); sys.exit(1)
    if r.stderr.strip(): print(r.stderr)
out=sys.argv[1]
asms=sys.argv[2:] or ['src/legends_crystal.asm','src/starters_crystal.asm','src/johto3_crystal.asm']
os.makedirs('obj',exist_ok=True); objs=[]
for a in asms:
    o='obj/'+os.path.basename(a)+'.o'; run('rgbasm','-I',os.environ.get('POKECRYSTAL','pokecrystal/'),'-o',o,a); objs.append(o)
run('rgblink','-O','base.gbc','-n',out.replace('.gbc','.sym'),'-m',out.replace('.gbc','.map'),'-o',out,*objs)
run('rgbfix','-v',out)
print(out,'%08X'%zlib.crc32(open(out,'rb').read()))
