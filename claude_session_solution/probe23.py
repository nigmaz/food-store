import sys,os; sys.path.insert(0,"/mnt/c/Users/ha/Downloads/pwn")
from dumper import G
NF=int(sys.argv[1]) if len(sys.argv)>1 else 5
g=G("god2")
for pair in ((b"A1",b"B2"),(b"C3",b"D4"),(b"E5",b"F6"),(b"YY",b"Z9")):
    g.add(pair[0]); g.add(pair[1]); g.cook(b"Beef noodles")
for t in b"B2,A1,D4,C3,F6,E5,Z9,YY".split(b","): g.rm(t)
g.add(b"CC")
for i in range(NF): g.make(b"f%d_xxxxxx"%i)
g.add(b"MARKREC1")   # recipe add after foods - clean?
g.dump("after %d foods + MARKREC1"%NF); g.close()
