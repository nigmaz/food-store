# Food Store harness. Convention: every action sends its menu number to the
# currently-pending "Your choice: " prompt, reads only its own output, and
# leaves the NEXT "Your choice: " prompt pending (unconsumed).
from pwn import *
import os
context.arch='amd64'
context.log_level=os.environ.get('LOG','error')
DIR='/mnt/c/Users/ha/Downloads/pwn'
STAR=b'*'*41

class FS:
    def __init__(self, mode='dbg'):
        self.mode=mode
        env={'LD_LIBRARY_PATH':DIR}
        if mode=='remote':
            self.p=remote('chall.pwnable.tw',10406)
        else:
            binname={'dbg':'food_store_dbg','local':'food_store_local','god':'food_store_god','god2':'food_store_god2'}[mode]
            self.p=process([DIR+'/ld-2.24.so','--library-path',DIR,DIR+'/'+binname],env=env)
        self.p.timeout=6
    def ru(self,x,**k): return self.p.recvuntil(x,**k)
    def sl(self,x): self.p.sendline(x if isinstance(x,bytes) else str(x).encode())
    def _c(self,c): self.ru(b'Your choice: '); self.sl(c)   # answer main/sub prompt
    def name(self,n): self.ru(b'Your name: '); self.sl(n)
    # --- main menu actions (each leaves next 'Your choice: ' pending) ---
    def cook(self, title):
        self._c(5); self.ru(b'What do you want to cook :'); self.sl(title)
        return self.ru(b'Done !')
    def chef(self):
        self._c(3); self.ru(STAR); d=self.ru(STAR)   # header, then footer
        import re
        g=lambda k: (int(re.search(k+rb' : (\d+)',d).group(1)) if re.search(k+rb' : (\d+)',d) else None)
        return dict(level=g(b'Level'),power=g(b'Power'),money=g(b'Money'),raw=d)
    def eat(self, idx):
        self._c(6); self.ru(b'What do you want to eat ? :'); self.sl(idx)
        return self.ru(b'\n')
    def assignment(self, yes=True):
        self._c(2); self.ru(b'Your choice (1/Yes,0/No) :'); self.sl(b'1' if yes else b'0')
        return self.ru(b'\n')
    # --- recipe submenu (enter, do one op, return to main) ---
    def add_recipe(self, title, ings, read_magic=True):
        self._c(1); self.ru(b'Your choice: '); self.sl(b'1')
        magic=None
        if read_magic: self.ru(b'Magic : '); magic=self.p.recvline().strip()
        self.ru(b'Title :'); self.sl(title)
        for i,ing in enumerate(ings):
            self.ru(b'Choose ingredient :'); self.sl(ing)
            self.ru(b'Add more ingredient ? (1/Yes,2/No) : ')
            self.sl(b'1' if i<len(ings)-1 else b'2')
        self.ru(b'Your choice: '); self.sl(b'4')
        return magic
    def remove_recipe(self, title):
        self._c(1); self.ru(b'Your choice: '); self.sl(b'2')
        self.ru(b'Title :'); self.sl(title)
        self.ru(b'Your choice: '); self.sl(b'4')
    def show_recipe(self):
        self._c(1); self.ru(b'Your choice: '); self.sl(b'3')
        d=self.ru(b'Your choice: ')   # recipe submenu prompt after listing
        self.sl(b'4')
        return d
    # --- shop submenu ---
    def buy(self, idx, qty):
        self._c(4); self.ru(b'Your choice: '); self.sl(b'1')
        self.ru(b'What do you want to buy ? :'); self.sl(idx)
        r=self.ru(b'Quantity :'); self.sl(qty)
        d=self.ru(b'Your choice: '); self.sl(b'4'); return d
    def sell(self, idx):
        self._c(4); self.ru(b'Your choice: '); self.sl(b'2')
        self.ru(b'What do you want to sell ? :'); self.sl(idx)
        d=self.ru(b'Your choice: '); self.sl(b'4'); return d
    def make(self, nm):
        self._c(4); self.ru(b'Your choice: '); self.sl(b'3')
        self.ru(b'Ingredient :'); self.sl(nm)
        d=self.ru(b'Your choice: '); self.sl(b'4'); return d
    def close(self): self.p.close()
