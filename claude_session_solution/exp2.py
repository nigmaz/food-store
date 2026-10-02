import sys; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
import os
which=os.environ.get('SEQ','1')
g=G()
if which=='1':
    # 3 recipes, remove middle, remove first (no consolidation? B between A and C)
    g.add(b'A1'); g.add(b'B2'); g.add(b'C3')
    g.rm(b'B2')      # free B (unsorted)
    g.add(b'D4')     # reuse B
    g.dump('seq1: A,B,C; rm B; add D(reuse B)')
elif which=='2':
    # make a food barrier then recipe, free recipe, reuse
    g.add(b'A1'); g.make(b'f1'); g.add(b'B2'); g.make(b'f2')
    g.rm(b'A1')
    g.add(b'D4')
    g.dump('seq2: A,bar,B,bar; rm A; add D(reuse A)')
elif which=='3':
    g.add(b'A1'); g.add(b'B2'); g.add(b'C3')
    g.rm(b'A1'); g.rm(b'C3')   # free A and C (non adjacent, B between)
    g.add(b'D4')
    g.dump('seq3: A,B,C; rm A,C; add D')
g.close()
