import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
g=G()
# adjacency: A,B,C3 (recipes) then YY (recipe), each separated? We want A,B,C3 contiguous to merge 0x1b0.
g.add(b'A1'); g.add(b'B2'); g.add(b'C3'); g.make(b'bar'); g.add(b'YY'); g.make(b'bar2')
# free B2, C3 first (so A1->next chain and merges)
g.rm(b'C3')   # C3 freed
g.rm(b'B2')   # B2 freed, adjacent to C3 -> merge? B2 before C3 -> consolidate 0x120
g.rm(b'A1')   # A1 freed, adjacent to merged -> 0x1b0
g.dump('three freed -> big chunk; check sizes')
g.close()
