import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G('god2')
print("init ok")
g.add(b'A1'); print("add A1 ok")
g.cook(b'Beef noodles'); print("cook1 ok")
g.cook(b'Beef noodles'); print("cook2 ok")
g.cook(b'Beef noodles'); print("cook3 ok (free cooking?)")
g.close()
