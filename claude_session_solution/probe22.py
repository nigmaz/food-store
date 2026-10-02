import sys,os; sys.path.insert(0,"/mnt/c/Users/ha/Downloads/pwn")
from dumper import G
g=G("god2")
for pair in ((b"A1",b"B2"),(b"C3",b"D4"),(b"E5",b"F6"),(b"YY",b"Z9")):
    g.add(pair[0]); g.add(pair[1]); g.cook(b"Beef noodles")
for t in b"B2,A1,D4,C3,F6,E5,Z9,YY".split(b","): g.rm(t)
g.add(b"CC")
for nm in (b"AAA6",b"BBB6",b"CCC6",b"DDD6",b"EEE6"):
    g.make(nm)
g.dump("groom + 5 foods"); g.close()
