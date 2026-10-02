import sys,os; sys.path.insert(0,"/mnt/c/Users/ha/Downloads/pwn")
from dumper import G
NFILL=int(sys.argv[1]) if len(sys.argv)>1 else 0
g=G("god2")
g.add(b"UNIQ777"); g.add(b"A1"); g.add(b"B2"); g.cook(b"Beef noodles"); g.add(b"YY"); g.add(b"Z9"); g.cook(b"Beef noodles")
for t in (b"B2",b"Z9",b"A1",b"YY"): g.rm(t)
g.add(b"CC")
g.cook(b"Beef noodles"); g.cook(b"Beef noodles"); g.cook(b"Beef noodles")  # D3=BN @YY (price0)
for i in range(NFILL):
    g.cook(b"Beef noodles")   # fill YY remainder
g.sell(b"2"); g.sell(b"3")    # seed + sell D3  (D3 freed, at CC->next)
g.dump("D3=BN, NFILL=%d"%NFILL); g.close()
