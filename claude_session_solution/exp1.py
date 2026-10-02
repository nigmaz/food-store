import sys; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G()
g.add(b'AAAA'); g.add(b'BBBB')
g.rm(b'BBBB'); g.rm(b'AAAA')
g.add(b'CCCC')
g.dump('A,B added; B,A removed(consolidate); C added')
g.close()
