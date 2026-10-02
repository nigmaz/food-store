import gdb
inf=gdb.inferiors()[0]
def rq(a):
    try: return int.from_bytes(inf.read_memory(a,8).tobytes(),'little')
    except: return None
LIBC=L_; BASE=B_
def tag(v):
    if v is None: return '?'
    if LIBC<=v<LIBC+0x400000: return 'LIBC+%#x'%(v-LIBC)
    if v>0x5000000000 and (v>>44)!=0: return 'PTR'
    return ''
fp=rq(F_); print("libc=%#x base=%#x foods_ptr=%#x secret=%#x"%(LIBC,BASE,fp or 0,rq(S_)))
print("-- recipes head=%#x --"%rq(H_))
n=rq(H_); seen=set()
for i in range(16):
    if not n or n in seen: print("  end/loop %#x"%(n or 0)); break
    seen.add(n)
    d=inf.read_memory(n,0x88).tobytes() if (n>0x1000) else None
    if d is None: print("  node %#x bad"%n); break
    try: d=inf.read_memory(n,0x88).tobytes()
    except: print("  node %#x UNREADABLE"%n); break
    nx=int.from_bytes(d[0x80:0x88],'little')
    print("  R %#x title=%r next=%#x %s"%(n,d[:12],nx,tag(nx)))
    n=nx
start=(fp & ~0xfff) if fp else 0
end=(fp+0x1800) if fp else start
print("-- heap --")
a=start; cnt=0
while a<end and cnt<90:
    sz=rq(a+8)
    if sz is None: break
    r=sz&~0xf; pv=sz&1
    if r<0x20 or r>0x1000: a+=0x10; continue
    fd=rq(a+0x10)
    t=tag(fd)
    mark=' <== LIBC' if 'LIBC' in t else ''
    print("  @%#x sz=%#x pv=%d fd=%#x %s%s"%(a,r,pv,fd,t,mark))
    a+=r; cnt+=1
MA = LIBC + 0x3c1b00
print("-- fastbins (main_arena %#x) --"%MA)
for i in range(7):
    v=rq(MA+0x10+i*8)
    if v:
        chain=[]; n=v; seen=0
        while n and seen<8:
            chain.append(hex(n)); n=rq(n+0x10); seen+=1
        print("  fast[sz=%#x]: "%(0x30+i*0x10) + " -> ".join(chain))
print("-- top=%#x --"%rq(MA+0x60))
# CC->next target + its fd/bk (heap-leak check)
__n=rq(H_); __cc=None
for _ in range(12):
    if not __n: break
    try: __t3=inf.read_memory(__n,3).tobytes()
    except: break
    if __t3==b"CC\x00": __cc=__n; break
    __n=rq(__n+0x80)
if __cc:
    __tg=rq(__cc+0x80)
    print("== CC %#x -> next target %#x =="%(__cc,__tg))
    for o in (0,8,0x10,0x18):
        v=rq(__tg+o); tag=""
        if v and LIBC<=v<LIBC+0x400000: tag="LIBC+%#x"%(v-LIBC)
        elif v and 0x5000000000<v<0x600000000000: tag="HEAP"
        print("   +%#x = %#x %s"%(o,v or 0,tag))
# smallbin/unsorted 0x120 chain
print("== 0x120 chunks fd-chain ==")
for __a in range(0,0x1800,0x10):
    __p=(F_ & ~0xfff)+__a
    __s=rq(__p+8)
    if __s and (__s&~0xf)==0x120:
        __fd=rq(__p+0x10); __bk=rq(__p+0x18)
        def __t(v):
            if v and LIBC<=v<LIBC+0x400000: return "LIBC+%#x"%(v-LIBC)
            if v and 0x5000000000<v<0x600000000000: return "HEAP"
            return ""
        print("  0x120 @%#x fd=%#x %s bk=%#x %s"%(__p,__fd or 0,__t(__fd),__bk or 0,__t(__bk)))
# dump foods_ptr array + food names
print("== foods ==")
__fp=rq(F_)
for i in range(10):
    __f=rq(__fp+i*8)
    if __f:
        try: __nm=inf.read_memory(__f,0x18).tobytes()
        except: __nm=b"?"
        print("  foods[%d] @%#x name=%r"%(i,__f,__nm[:16]))
print("== fastbins (0x30=idx0? check) ==")
MA2=LIBC+0x3c1b00
for i in range(4):
    v=rq(MA2+0x10+i*8)
    if v: print("  fast idx%d (sz %#x): %#x"%(i,0x20+i*0x10,v))
