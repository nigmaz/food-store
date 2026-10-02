import sys,os,subprocess; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
from pwn import ELF
L=ELF('/mnt/c/Users/ha/Downloads/pwn/libc-4e5dfd832191073e18a09728f68666b6465eeacd.so')
# build reverse symbol map (offset->name) for interesting pointers
syms={L.symbols[n]:n for n in L.symbols}
g=G('god2'); g.add(b'A1'); g.sync(); pid=g.p.pid
libc=None
for line in open('/proc/%d/maps'%pid):
    if 'libc.so.6' in line and libc is None: libc=int(line.split('-')[0],16)
body=r'''import gdb,struct
inf=gdb.inferiors()[0]; L=_L_
def rd(a,n): return inf.read_memory(a,n).tobytes()
res=[]
for o in range(0x3c0000,0x3c7000):
    v=struct.unpack("<Q",rd(L+o,8))[0]; sz=v&~0xf
    if sz in (0x30,0x40):
        res.append((o,sz,o+0x10))
for o,sz,u in res: print("FAKE off=%#x size=%#x user=%#x"%(o,sz,u))
print("COUNT",len(res))
'''.replace('_L_',hex(libc))
open('/tmp/rd2.py','w').write(body)
out=subprocess.run(['gdb','-q','-nx','-batch','-p',str(pid),'-ex','set pagination off','-ex','set debuginfod enabled off','-ex','source /tmp/rd2.py','-ex','detach','-ex','quit'],capture_output=True,text=True)
# annotate users near symbols
lines=out.stdout.splitlines()
for ln in lines:
    if ln.startswith('FAKE'):
        u=int(ln.split('user=')[1],16)
        near=[ (syms[s],s-u) for s in syms if abs(s-u)<=0x30 ]
        if near: print(ln, "NEAR", near)
print([l for l in lines if l.startswith('COUNT')])
g.close()
