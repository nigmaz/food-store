import sys,os,subprocess; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G('god2')
g.add(b'A1')  # minimal op
g.sync(); pid=g.p.pid
libc=None
for line in open('/proc/%d/maps'%pid):
    if 'libc.so.6' in line and libc is None: libc=int(line.split('-')[0],16)
# read libc region 0x3c1a00..0x3c1c00 and 0x3c3700..0x3c3800 and main_arena 0x3c1b00
body=r'''import gdb
inf=gdb.inferiors()[0]
L=_L_
def rd(a,n): return inf.read_memory(a,n).tobytes()
import struct
def scan(name,start,end):
    print("== %s =="%name)
    for o in range(start,end):
        v=struct.unpack("<Q",rd(L+o,8))[0]
        sz=v & ~0xf
        if sz in (0x30,0x40,0x50,0x60,0x70,0x80):
            print("  fake@libc+%#x size=%#x user=libc+%#x"%(o,sz,o+0x10))
scan("hooks", 0x3c1a00, 0x3c1b60)
scan("free_hook", 0x3c3700, 0x3c3800)
scan("IO", 0x3c24c0, 0x3c2720)
print("malloc_hook region bytes libc+0x3c1ac0:", rd(L+0x3c1ac0,0x50).hex())
'''.replace('_L_',hex(libc))
open('/tmp/rd.py','w').write(body)
out=subprocess.run(['gdb','-q','-nx','-batch','-p',str(pid),'-ex','set pagination off','-ex','set debuginfod enabled off','-ex','source /tmp/rd.py','-ex','detach','-ex','quit'],capture_output=True,text=True)
print("libc=%#x"%libc)
print(out.stdout)
if out.returncode: print("ERR",out.stderr[-300:])
g.close()
