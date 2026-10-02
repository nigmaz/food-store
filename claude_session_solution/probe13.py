import sys,os; sys.path.insert(0,"/mnt/c/Users/ha/Downloads/pwn")
from dumper import G
EXTRA=int(sys.argv[1]) if len(sys.argv)>1 else 0
g=G("god2")
g.add(b"A1"); g.add(b"B2"); g.cook(b"Beef noodles"); g.add(b"YY"); g.add(b"Z9"); g.cook(b"Beef noodles")
for t in (b"B2",b"Z9",b"A1",b"YY"): g.rm(t)
g.add(b"CC")
for i in range(EXTRA):
    g.add(b"EX%d"%i); g.rm(b"EX%d"%i)   # add+free extra recipes -> more unsorted chunks
g.dump("EXTRA=%d"%EXTRA); g.close()
