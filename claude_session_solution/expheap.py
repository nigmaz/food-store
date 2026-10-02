import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G()
seq=os.environ.get('SEQ','free1')
if seq=='free1':
    g.add(b'A1'); g.add(b'B2')
    g.rm(b'A1')   # free one recipe (B between? no, A then B; A has bar? no). A freed, B after A in mem+list
g.dump(seq)
g.close()
