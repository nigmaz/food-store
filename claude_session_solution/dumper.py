# usage: python3 dumper.py  (drives god binary to a state, then dumps)
import sys,os,subprocess; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
os.environ['LOG']='error'
from pwn import *
DIR='/mnt/c/Users/ha/Downloads/pwn'
env={'LD_LIBRARY_PATH':DIR,'LD_PRELOAD':DIR+'/ptracer.so'}

class G:
    def __init__(self, mode='god'):
        binname={'god':'food_store_god','god2':'food_store_god2','dbg':'food_store_dbg'}[mode]
        self.binname=binname
        self.p=process([DIR+'/ld-2.24.so','--library-path',DIR,DIR+'/'+binname],env=env)
        self.p.timeout=8
        self.ru(b'Your name: '); self.sl(b'AAAA')
    def ru(self,x,**k): return self.p.recvuntil(x,**k)
    def sl(self,x): self.p.sendline(x if isinstance(x,bytes) else str(x).encode())
    def add(self,title,ings=(b'0',)):
        self.ru(b'Your choice: '); self.sl(b'1'); self.ru(b'Your choice: '); self.sl(b'1')
        self.ru(b'Magic : '); m=self.p.recvline().strip()
        self.ru(b'Title :'); self.sl(title)
        for i,ing in enumerate(ings):
            self.ru(b'Choose ingredient :'); self.sl(ing)
            self.ru(b'Add more ingredient ? (1/Yes,2/No) : '); self.sl(b'1' if i<len(ings)-1 else b'2')
        self.ru(b'Your choice: '); self.sl(b'4'); return m
    def make(self,nm):
        self.ru(b'Your choice: '); self.sl(b'4'); self.ru(b'Your choice: '); self.sl(b'3')
        self.ru(b'Ingredient :'); self.sl(nm); self.ru(b'Your choice: '); self.sl(b'4')
    def cook(self, title):
        self.ru(b'Your choice: '); self.sl(b'5'); self.ru(b'What do you want to cook :'); self.sl(title); self.ru(b'Done !')
    def buy(self, idx, qty):
        self.ru(b'Your choice: '); self.sl(b'4'); self.ru(b'Your choice: '); self.sl(b'1')
        self.ru(b'What do you want to buy ? :'); self.sl(idx); self.ru(b'Quantity :'); self.sl(qty)
        self.ru(b'Your choice: '); self.sl(b'4')
    def rm(self,title):
        self.ru(b'Your choice: '); self.sl(b'1'); self.ru(b'Your choice: '); self.sl(b'2')
        self.ru(b'Title :'); self.sl(title); self.ru(b'Your choice: '); self.sl(b'4')
    def eat(self, idx):
        self.ru(b'Your choice: '); self.sl(b'6'); self.ru(b'What do you want to eat ? :'); self.sl(idx)
    def sell(self, idx):
        self.ru(b'Your choice: '); self.sl(b'4'); self.ru(b'Your choice: '); self.sl(b'2')
        self.ru(b'What do you want to sell ? :'); self.sl(idx); self.ru(b'Your choice: '); self.sl(b'4')
    def sync(self): self.ru(b'Your choice: ')
    def dump(self,label=''):
        self.sync(); pid=self.p.pid
        base=libc=None
        for line in open('/proc/%d/maps'%pid):
            p=line.split()
            path=p[-1] if len(p)>=6 else ''
            if path.endswith(self.binname) and base is None: base=int(line.split('-')[0],16)
            if 'libc.so.6' in path and libc is None: libc=int(line.split('-')[0],16)
        heads=base+0x2050d0; sec=base+0x2050d8; dishhead=base+0x205060; foodsp=base+0x2050c8
        body=open(DIR+'/gdb_dump.py').read()
        body=body.replace('H_',hex(heads)).replace('S_',hex(sec)).replace('D_',hex(dishhead)).replace('F_',hex(foodsp)).replace('L_',hex(libc)).replace('B_',hex(base))
        open('/tmp/d.py','w').write(body)
        out=subprocess.run(['gdb','-q','-nx','-batch','-p',str(pid),'-ex','set pagination off','-ex','set debuginfod enabled off','-ex','source /tmp/d.py','-ex','detach','-ex','quit'],capture_output=True,text=True)
        print('===== DUMP %s ====='%label); print(out.stdout)
        if out.returncode: print('ERR',out.stderr[-400:])
    def close(self): self.p.close()
