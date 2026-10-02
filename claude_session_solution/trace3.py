import os,sys
from pwn import *
context.log_level="error"
DIR="/mnt/c/Users/ha/Downloads/pwn"
env={"LD_LIBRARY_PATH":DIR,"LD_PRELOAD":DIR+"/hook.so"}
logf=open(DIR+"/htrace.log","w")
p=process([DIR+"/ld-2.24.so","--library-path",DIR,DIR+"/food_store_local"],env=env,stderr=logf)
def mark(s): logf.flush(); open(DIR+"/htrace.log","a").write("=== "+s+" ===\n")
def ch(c): p.recvuntil(b"Your choice: "); p.sendline(str(c).encode())
p.recvuntil(b"Your name: "); p.sendline(b"AAAABBBB")
p.recvuntil(b"Your choice: ")   # main menu shown => init_shop done
open(DIR+"/htrace.log","a").write("=== after init (name+shop) ===\n")
p.sendline(b"5"); p.sendlineafter(b"What do you want to cook :",b"Pineapple cake"); p.recvuntil(b"Done !")
open(DIR+"/htrace.log","a").write("=== cook1 done ===\n")
ch(5); p.sendlineafter(b"What do you want to cook :",b"Pineapple cake"); p.recvuntil(b"Done !")
open(DIR+"/htrace.log","a").write("=== cook2 done (level2) ===\n")
ch(1); p.sendlineafter(b"Your choice: ",b"1")
p.recvuntil(b"Magic : "); magic=p.recvline().strip()
open(DIR+"/htrace.log","a").write("=== MAGIC="+magic.decode()+" ===\n")
p.sendlineafter(b"Title :",b"RECIPE_X")
p.sendlineafter(b"Choose ingredient :",b"0")
p.sendlineafter(b"Add more ingredient ? (1/Yes,2/No) : ",b"2")
open(DIR+"/htrace.log","a").write("=== added recipe RECIPE_X ===\n")
p.sendlineafter(b"Your choice: ",b"4")
ch(1); p.sendlineafter(b"Your choice: ",b"2"); p.sendlineafter(b"Title :",b"RECIPE_X")
open(DIR+"/htrace.log","a").write("=== removed RECIPE_X ===\n")
p.sendlineafter(b"Your choice: ",b"4")
ch(6)  # Eat
p.recvuntil(b"What do you want to eat ? :"); p.sendline(b"0")
open(DIR+"/htrace.log","a").write("=== ate dish 0 ===\n")
ch(7)
import time;time.sleep(0.3)
try:p.recvall(timeout=2)
except:pass
logf.flush(); logf.close()
print("done")
