import sys,os; sys.path.insert(0,"/mnt/c/Users/ha/Downloads/pwn")
from dumper import G
g=G("god2")
g.make(b"ZZZWXYQ9")   # try controlled food name
g.dump("after make ZZZWXYQ9"); g.close()
