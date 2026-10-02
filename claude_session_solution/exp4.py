import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G()
# A,B adjacent; Y after B. A->next=&B, B->next=&Y
g.add(b'AA'); g.add(b'BB'); g.add(b'YY')
g.rm(b'BB')        # A->next = B->next = &Y ; B freed (A live, Y live -> no consolidate)
g.rm(b'AA')        # A freed, consolidates with B(free). A+0x80=&Y preserved. list ..BN->YY
g.add(b'CC')       # reuse merged, split. C+0x80 = A+0x80 = &Y ?
g.dump('exp4: expect CC->next = &YY')
g.close()
