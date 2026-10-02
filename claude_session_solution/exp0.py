import sys; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G()
print("init done")
g.add(b'AAAA'); print("added A")
g.dump('after A')
g.close()
