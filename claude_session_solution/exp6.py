import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G()
g.add(b'AA'); g.add(b'BB'); g.make(b'b1'); g.add(b'YY'); g.make(b'b2')
g.rm(b'BB'); g.rm(b'AA'); g.add(b'CC')   # CC->next=&YY ; remainder(0x90) in unsorted
# consume unsorted remainder with Makes (foods 0x30) so YY becomes sole unsorted
g.make(b'm1'); g.make(b'm2'); g.make(b'm3'); g.make(b'm4')
g.rm(b'YY')
g.dump('after makes + rm YY')
g.close()
