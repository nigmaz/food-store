from pwn import *
import os,sys
context.arch='amd64'
context.log_level='error'
DIR='/mnt/c/Users/ha/Downloads/pwn'
BIN=DIR+'/food_store_local'
LD=DIR+'/ld-2.24.so'
env={'LD_LIBRARY_PATH':DIR}
if os.environ.get('TRACE'): env['LD_PRELOAD']=DIR+'/hook.so'

def start():
    return process([LD,'--library-path',DIR,BIN], env=env)

def name(p,n): p.sendlineafter(b'Your name: ',n)
def menu(p,c): p.sendlineafter(b'Your choice: ',str(c).encode())
# recipe submenu uses "Your choice: " too
def cook(p,title):
    menu(p,5)
    p.sendlineafter(b'What do you want to cook :',title)
def recipe_show(p):
    menu(p,1); p.sendlineafter(b'Your choice: ',b'3')
    # then returns to recipe menu; send 4 to return
def add_recipe(p,title,ings):
    menu(p,1); p.sendlineafter(b'Your choice: ',b'1')
    # Magic printed, then Title:
    p.recvuntil(b'Magic : '); magic=p.recvline().strip()
    p.sendlineafter(b'Title :',title)
    first=True
    for ing in ings:
        p.sendlineafter(b'Choose ingredient :',str(ing).encode())
        p.sendlineafter(b'Add more ingredient ? (1/Yes,2/No) : ',b'1')
    # finish: send 2 (No) — but loop asks after each add. We answered 1 each time; send one more cycle with 2
    # Actually simpler: after last ing, answer 2. Rework below.
    return magic

if __name__=='__main__':
    p=start()
    name(p,b'AAAABBBB')
    # cook twice to reach level 2
    cook(p,b'Pineapple cake'); 
    print(p.recvuntil(b'Your choice: ',timeout=2))
    p.close()
