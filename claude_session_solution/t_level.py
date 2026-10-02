import sys; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from fs import *
g=FS('dbg'); g.name(b'AAAA')
def pc(t): c=g.chef(); print(t,{k:c[k] for k in('level','power','money')})
pc('chef0')
for i in range(5):
    r=g.cook(b'Beef noodles'); print('cook',i,b'Done' in r); pc(' chef')
g.close()
