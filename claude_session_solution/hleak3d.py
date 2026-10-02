import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G('god2')
g.add(b'UNIQ777',(b'0',))
g.add(b'A1'); g.add(b'B2'); g.cook(b'Beef noodles'); g.add(b'YY'); g.add(b'Z9'); g.cook(b'Beef noodles')
for t in (b'B2',b'Z9',b'A1',b'YY'): g.rm(t)
g.add(b'CC')
g.cook(b'Beef noodles'); g.cook(b'Beef noodles'); g.cook(b'Beef noodles'); g.cook(b'UNIQ777')  # D1,D2,E,D3
g.sell(b'4')   # free E (index4)
g.dump('after sell E (before rm D3)')
g.close()
