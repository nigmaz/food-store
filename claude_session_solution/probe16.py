import sys,os; sys.path.insert(0,"/mnt/c/Users/ha/Downloads/pwn")
from dumper import G
order=sys.argv[1] if len(sys.argv)>1 else "B2,A1,D4,C3,F6,E5,Z9,YY"
g=G("god2")
g.add(b"A1"); g.add(b"B2"); g.cook(b"Beef noodles")
g.add(b"C3"); g.add(b"D4"); g.cook(b"Beef noodles")
g.add(b"E5"); g.add(b"F6"); g.cook(b"Beef noodles")
g.add(b"YY"); g.add(b"Z9"); g.cook(b"Beef noodles")
for t in order.split(","): g.rm(t.encode())
g.add(b"CC")
g.dump("order=%s"%order); g.close()
