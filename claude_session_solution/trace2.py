import os,sys
from pwn import *
context.log_level="error"
DIR="/mnt/c/Users/ha/Downloads/pwn"
env={"LD_LIBRARY_PATH":DIR,"LD_PRELOAD":DIR+"/hook.so"}
p=process([DIR+"/ld-2.24.so","--library-path",DIR,DIR+"/food_store_local"],env=env,stderr=2)
def ru(u): return p.recvuntil(u)
def ch(c): ru(b"Your choice: "); p.sendline(str(c).encode())
ru(b"Your name: "); p.sendline(b"AAAABBBB")
sys.stderr.write("\n--- cook #1 ---\n"); sys.stderr.flush()
ch(5); p.sendlineafter(b"What do you want to cook :",b"Pineapple cake"); ru(b"Done !")
sys.stderr.write("\n--- cook #2 (level up) ---\n"); sys.stderr.flush()
ch(5); p.sendlineafter(b"What do you want to cook :",b"Pineapple cake"); ru(b"Done !")
sys.stderr.write("\n--- add recipe ---\n"); sys.stderr.flush()
ch(1); p.sendlineafter(b"Your choice: ",b"1")
ru(b"Magic : "); magic=p.recvline().strip(); sys.stderr.write("MAGIC="+magic.decode()+"\n")
p.sendlineafter(b"Title :",b"MYRECIPE")
p.sendlineafter(b"Choose ingredient :",b"0")
p.sendlineafter(b"Add more ingredient ? (1/Yes,2/No) : ",b"2")
p.sendlineafter(b"Your choice: ",b"4")  # return to main
sys.stderr.write("\n--- remove recipe MYRECIPE ---\n"); sys.stderr.flush()
ch(1); p.sendlineafter(b"Your choice: ",b"2"); p.sendlineafter(b"Title :",b"MYRECIPE")
p.sendlineafter(b"Your choice: ",b"4")
ch(7)
import time; time.sleep(0.3)
try: p.recvall(timeout=2)
except: pass
