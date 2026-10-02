import os,sys
from pwn import *
context.log_level="error"
DIR="/mnt/c/Users/ha/Downloads/pwn"
env={"LD_LIBRARY_PATH":DIR}
p=process([DIR+"/ld-2.24.so","--library-path",DIR,DIR+"/food_store_local"],env=env)
p.recvuntil(b"Your name: "); p.sendline(b"AAAABBBB")
p.recvuntil(b"Your choice: "); p.sendline(b"5")
data=p.recvuntil(b"What do you want to cook :",timeout=3)
sys.stdout.write("PROMPT_OK\n")
p.sendline(b"Pineapple cake")
import time;time.sleep(0.5)
rest=p.recvrepeat(1.5)
sys.stdout.write(rest.decode(errors="replace"))
p.wait(timeout=2)
sys.stdout.write("\nEXITCODE=%r POLL=%r\n"%(getattr(p,'returncode',None),p.poll()))
