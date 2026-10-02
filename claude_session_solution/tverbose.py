import sys; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from pwn import *
context.log_level='error'
DIR='/mnt/c/Users/ha/Downloads/pwn'
p=process([DIR+'/ld-2.24.so','--library-path',DIR,DIR+'/food_store_dbg'],env={'LD_LIBRARY_PATH':DIR})
def dump(u=b'Your choice: ',t=2):
    d=p.recvuntil(u,timeout=t); sys.stdout.write(d.decode(errors='replace')); sys.stdout.flush(); return d
p.recvuntil(b'Your name: '); p.sendline(b'AAAA')
dump()
p.sendline(b'4')          # shop
dump()
p.sendline(b'1')          # buy -> shows buy menu then "What do you want to buy ? :"
d=p.recvuntil(b'What do you want to buy ? :',timeout=2); sys.stdout.write(d.decode(errors='replace'))
p.sendline(b'1')          # pineapple
d=p.recvuntil(b'Quantity :',timeout=2); sys.stdout.write(d.decode(errors='replace'))
p.sendline(b'3')
dump()  # result + back to shop menu "Your choice:"
p.sendline(b'4')  # return
dump()
p.sendline(b'7'); 
sys.stdout.write(p.recvrepeat(1).decode(errors='replace'))
