import os
from pwn import *
context.log_level="error"
DIR="/mnt/c/Users/ha/Downloads/pwn"
env={"LD_LIBRARY_PATH":DIR,"LD_PRELOAD":DIR+"/hook.so"}
p=process([DIR+"/ld-2.24.so","--library-path",DIR,DIR+"/food_store_local"],env=env,stderr=process.PIPE)
def rl(u): return p.recvuntil(u)
rl(b"Your name: "); p.sendline(b"AAAABBBB")
rl(b"Your choice: "); p.sendline(b"3")   # chef info
rl(b"Your choice: "); p.sendline(b"7")   # exit
import time; time.sleep(0.3)
out=p.recvall(timeout=2)
sys.stdout.write(out.decode(errors="replace"))
