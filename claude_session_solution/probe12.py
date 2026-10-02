import sys,os; sys.path.insert(0,"/mnt/c/Users/ha/Downloads/pwn")
from dumper import G
g=G("god2")
g.add(b"A1"); g.add(b"B2"); g.cook(b"Beef noodles"); g.add(b"YY"); g.add(b"Z9"); g.cook(b"Beef noodles")
for t in (b"B2",b"Z9",b"A1",b"YY"): g.rm(t)
g.add(b"CC")
g.add(b"R"*16+b"A"); g.add(b"SLOTXX")   # do these eat YY?
g.dump("after CC,R,SLOT"); g.close()
