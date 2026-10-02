# Food Store (pwnable.tw :10406) — tiến độ

## Môi trường test (WSL)
- libc = glibc 2.24-9ubuntu2.2 (khớp byte đề bài), loader `.libc24/x/.../ld-2.24.so` -> copy `ld-2.24.so`.
- Chạy: `./ld-2.24.so --library-path . ./food_store` (bản thật) hoặc `food_store_local` (flag->"flag"), `food_store_dbg` (alarm off), `food_store_god` (level5/power/money cao để nghiên cứu heap).
- gdb attach qua `ptracer.so` (PR_SET_PTRACER). Dumper: `dumper.py` + `gdb_dump.py`.

## Bảo vệ
Full RELRO, NX, PIE, canary. Seccomp: open/read/write/writev/close/mmap/munmap/exit (KHÔNG execve). Flag mở sẵn fd 3.

## Cấu trúc
- recipe = malloc(0x88): title[0x18]@0, 13 ingredient-ptr @0x18..0x78, next@0x80 (TRÙNG prev_size chunk kế).
- food = 0x28 {name[0x20], price@0x20(u32), qty@0x24(u32)}. mảng foods_ptr 10 slot.
- dish = 0x38 {name[0x18], price@0x18, energy@0x20(u64), next@0x28, prev@0x30} - list đôi vòng @0x205060.
- recipe list head @0x2050d0. secret 8 byte @0x2050d8. Magic = recipe_ptr ^ secret.

## BUG
`add_recipe` không khởi tạo recipe->next (chỉ clear 0x18..0x78). next@0x80 trùng prev_size chunk kế.
Khi free: set_foot ghi next=0x90. Khi consolidate+split: next = dữ liệu cũ tại offset đó.

## LEAK LIBC (SẠCH, không crash) — ĐÃ XÁC THỰC
Groom (cần level>=3 để remove): 
  add A, add B, cook(sep1), add YY, add Z, cook(sep2)  # cook = dish separator, không tốn food slot
  rm B, rm Z, rm A, rm YY
  add CC
=> CC->next = &YY (YY = chunk 0x120 merge-forward => YY->next=0 => show dừng sạch).
show recipe: title của fake node YY = YY+0 = main_arena.
=> libc_base = leak - 0x3c1c68 (ra page-aligned => đúng). Script: leakverify.py.

## PRIMITIVE khác đã xác nhận
- Type-confusion FREE: đặt một food vào chunk YY (= CC->next) -> remove_recipe(food_name) khớp fake node
  -> free food đó (vào fastbin) trong khi foods_ptr vẫn giữ (UAF). Process sống.

## CÒN LẠI (chưa xong) - giai đoạn GHI
Cần: heap leak + arbitrary write -> __free_hook = gadget/stack-pivot -> ROP open/read/write (ORW).
Khó vì:
- 10 food-slot (init 5), poison next=0x90, đặt chunk chính xác rất nhạy bin.
- Double-free food (fastbin dup 0x30) bị chặn: re-match title sau free cần next=&self (cần heap addr).
- Dish double-free (free as recipe + as dish) SẠCH nhưng dish name = recipe title (scanf, không null) => khó ghi gadget có null byte. Food dup (Make name = read, có null) mới ghi được nhưng vướng ở trên.
- Heap leak qua dangling-ingredient: freed food fd=0 khi sole trong fastbin => chưa lộ heap.

Hướng tiếp: dish fastbin dup để set fastbin fd (qua dish name) -> cấp phát 0x40 tại target libc; hoặc tìm cách lộ heap để mở double-free food.

## UPDATE: BOTH LEAKS CLEAN (process alive)
### LIBC leak (confirmed): libc_base = leak - 0x3c1c68  (page-aligned => correct)
groom: addUNIQ, addA,addB,cook,addYY,addZ,cook ; rm B,Z,A,YY ; addCC => CC->next=&YY(0x120 merge, ->next=0)
show recipe -> fake node title = main_arena.

### DISH fastbin[0x40] DOUBLE-FREE (confirmed): free dish-as-recipe (type-confusion) + free-as-dish(sell)
with a dish E freed between => fastbin[0x40]=[D3,E,D3...] cycle.

### HEAP leak (confirmed, clean): 
- free dish E (sell) -> fastbin[0x40]=[E]
- free dish D3 via type-confusion (remove matching the dish name, D3 is CC->next fake node @YY) -> fastbin[0x40]=[D3,E], D3.fd=&E, D3 STILL in dish list (remove-as-recipe doesn't unlink dish list)
- show-dishes (sell invalid idx) -> D3 "Name : %s" = D3.fd = &E = HEAP pointer. No crash.
- key placement: UNIQ777 must be the 3rd cook (lands at YY 0x120 after D1,D2 drain the 0x90 remainder).

### Runtime: NO 0x30/0x40 fake chunk anywhere in libc (COUNT 0). Only 0x70/0x50/0x80 fakes (from libc ptr bytes). 
So fastbin-dup must target HEAP (now have heap leak) not libc hooks directly.

### TODO write stage: with heap+libc, craft heap fake chunk -> fastbin dup overlap -> corrupt a recipe->next = arbitrary fake node -> arb read(stack via environ)/arb free/unlink-write -> __free_hook or stack ROP -> ORW(open/read/write fd3 flag).

## OBSTACLE (write stage): recipe-list corruption after type-confusion free
- Freeing a removable fake node (dish/food) via remove_recipe sets CC->next = node+0x80 (garbage/libc for 0x30/0x40 nodes).
- => recipe list broken => cook / add_recipe / show_recipe / remove / assignment all CRASH (they traverse recipes).
- cook is the ONLY 0x40 allocator, so the dish fastbin[0x40] dup becomes UNUSABLE after the leak.
- Post-corruption only Make/Buy/Eat/Sell/chef work (no recipe traversal). None allocate 0x40.
- The clean 0x120 fake node keeps CC->next=0 (YY+0x80=0) but its title=libc => can't remove() it (unmatchable).

## STATE: have clean libc+heap leak (process alive). Have dish 0x40 double-free primitive.
## MISSING: a usable arbitrary write that (a) doesn't brick the recipe list, or (b) repairs CC->next,
##          and reaches a code-exec target despite: no 0x30/0x40 libc fake-size; seccomp blocks execve/system.
## Candidate: food-dangling-ingredient heap leak with a 0x120 fake node (CC->next stays 0) to keep list usable;
##            then food double-free (heap known) -> fastbin[0x30] -> but still need a 0x30 target (none in libc).
##            OR unsorted-bin-attack via dish-dup overlap writing a freed recipe bk (needs cook => blocked by corruption).

## MAJOR BREAKTHROUGH + remaining obstacle
### USABLE dish fastbin[0x40] dup (recipe list stays intact):
- Keep the fake-node dish D3 with D3+0x80==0: drain the 0x90 remainder with 2 dishes (E,D1) FIRST,
  then cook UNIQ777 as the 3rd cook so it lands at YY(0x120) with a CLEAN 0xe0 leftover => D3+0x80=0.
- Sequence: add UNIQ777; (clean libc groom to CC->next=&YY); cook E; cook D1; cook UNIQ777(@YY);
  rm UNIQ777(recipe); rm UNIQ777(D3 => CC->next = D3+0x80 = 0, CLEAN); sell E; sell D3(dbl free).
- Result: CC->next=0 (list PC->BN->CC intact) AND fastbin[0x40]=[D3,E,D3,E...] cycle.
- CONFIRMED: cook after this works (no crash) and the cooked dish NAME (=recipe title) OVERWRITES the fastbin fd.
  => arbitrary 0x40 allocation: cook a recipe whose title = p64(fake_chunk) to set fd, then cook to alloc there.

### Arbitrary read plan (via overlapping a live recipe R slot0):
- R with title[0x10]='A' => *(R+0x10)=0x41 fake 0x40 size => alloc a dish at R+0x18=slot0.
- cook a 0-INGREDIENT recipe (dish price=0, so show R won't crash on slot3=price) whose title=p64(environ)
  => R.slot0 = environ => show_recipe R prints %s at environ => STACK leak.

### OBSTACLE: poison when adding exploit recipes AFTER the dup
- After the dup there is a freed 0x90 (the UNIQ777 recipe). Any new recipe reuses it => ->next=0x90 poison
  => subsequent append/traversal crashes. Pair-trick fails (append traverses through the poisoned node).
- Need: add all exploit recipes (with runtime-address titles) without leaving/ reusing a lone freed 0x90,
  OR consolidate the freed recipe so a reuse gets ->next=0 (like the CC consolidate+split).
- Plus: controlled-title recipes need scanf-safe address bytes (no 0x00/0x20/0x09-0x0d).

### STATUS: core primitives cracked (libc+heap leak, usable 0x40 dup, arbitrary alloc).
### Remaining = long intricate assembly (poison mgmt + scanf-safe titles + overlap read + ROP build + stack pivot).

## SESSION 2 — PRECISE DIAGNOSIS OF THE FINAL BLOCKER (all verified on god2)
### Confirmed working + process ALIVE:
- LIBC leak: groom -> CC->next=&YY(0x120 unsorted) -> show_recipes prints YY title = main_arena; libc_base=leak-0x3c1c68 (page aligned). ALIVE.
- HEAP leak: seed sell(2); rm(UNIQ777)x2  => fastbin[0x40]=[D3,seed], D3.fd=&seed, D3 STILL in dish list (type-confusion free keeps it). show_dishes prints D3 Name=&seed = heap. ALIVE.
  heap_base = heap_leak & ~0xfff ; R = heap_base+0x980 ; R+8 fake chunk (title[0x10]=0x41 => *(R+0x10)=0x41 fake 0x40 size).
- Fastbin[0x40] double-free CYCLE (D3<->X): seed sell(2); rm,rm; sell(0); sell(2)  => clean cycle 0x930<->0x8f0, recipe list clean, dish list healthy, cook works.
- Exploit recipes R + SLOT(=p64(environ)) added BEFORE the frees stay CLEAN (->next valid).

### THE BLOCKER (now fully understood):
- cook() FIRST calls show_recipe() internally (disasm: call at binary+0x229c -> 0x1a9b) which traverses the ENTIRE recipe list (follows ->next @ node+0x80 until 0) printing each title+ingredients.
- show_recipe ALSO iterates 13 ingredient slots node+0x18+i*8 for EVERY node (skips null slots, printf %s on non-null). So a freed dish fake-node with garbage trailing slots -> strlen crash; a node with ->next=0x90 -> printf(%s,0x90) -> strlen(0x90) SIGSEGV.
- => the recipe list must be 100% clean (every ->next 0-or-valid) for ANY cook to run.
- FD (the one recipe that MUST be added after the heap leak, title=p64(R+8) to drive the arb 0x40 alloc) reuses the lone freed 0x90 (the cook-recipe freed by rm#1). add_recipe memsets only 0x80 bytes, so FD->next (=FD+0x80 = next chunk prev_size) retains 0x90 => poison => every subsequent cook crashes.
- Magic secret is read from /dev/urandom (open+read at init 0x10d2), NOT rand/time => no predictable PHASE-A heap leak via Magic. So the rm-based leak (which makes the 0x90) is the only ALIVE heap leak found (show_recipes on a freed dish fake-node crashes on its trailing ingredient slots; show_dishes is the only slot-free printer and needs the dish in the DISH list, which only the type-confusion rm preserves -> rm frees a 0x90 recipe to match D3).

### WHY FD can't be clean (proved):
- FD->next must be 0 (or a valid node). FD->next = leftover at FD+0x80. Only TOP memory is fresh-zero there.
- malloc(0x88) returns the exact-fit lone 0x90 before ever using top. Consolidating the 0x90 (merge w/ neighbor/CC) still leaves FD->next = old recipe +0x80 leftover = 0x90. No food-free primitive exists (sell/eat both unlink dishes; shop sell = dishes only) to consolidate differently.
- So FD MUST allocate from TOP => the cook-recipe (freed for the rm-match) must be TOP-ADJACENT when freed (so free merges into top, no lone 0x90).
- But the cook-recipe must exist before the 3rd cook (to cook D3@YY) and be BEFORE D3 in the list (so rm#1 matches it first), forcing it to a LOW address; and adding a 0x90 recipe between CC and the cooks gets absorbed by the YY 0x120 region (breaks D3@YY placement). => tension.

### CONCRETE NEXT STEP (clear, not yet built): SEPARATE fake nodes.
- Make D3's fake node DISH-SIZED (<0x90) so a late-added cook-recipe X cannot fit in it and goes to TOP (top-adjacent). Then rm(X) merges into top (NO lone 0x90), rm(D3) frees a 0x40, and FD adds from TOP clean.
- Needs TWO fake nodes: one 0x120 unsorted for the LIBC leak (main_arena title), one dish-sized for D3/dup. i.e. consume the 0x120 YY after the libc leak, then build a fresh small CC2->next fake node for D3.
- After FD clean: cook(FD)x3 + cook(SLOT) => R.slot0=environ; then arb READ via show_recipes on R (ensure R.slot1..12 null/safe: dish price/energy=0, next/prev heap -> printf %s ok). Leak *environ = stack. Then arb WRITE -> ROP/ORW for flag (fd 3).
- Harness: exploit1.py has the full I/O (libc+heap leak parse, cycle, cooks, read). dumper.py/probe*.py for state dumps. Seed=sell(2), cycle=sell(0),sell(2), R=base+0x980.

## SESSION 2 (cont) — two decisive findings that narrow the finish
### (1) show_recipe ingredient loop = 13 slots node+0x18+i*8, printf("%s", slot) on each non-null slot (reads string AT the slot value).
- Dumped D3(freed dish)'s slots: slot0=price area (0x5555_0000_0030 bad), slot1=energy, slot4=chunk-size(0x91/0xe1 bad), slot5/6 = whatever is after D3 (R's title 'RRRR'=0x5252.. bad, OR main_arena = readable).
- => a freed DISH can NEVER be shown via show_recipes without crash: its own price/energy/chunk-size bytes are small non-null = bad pointers for %s. Only a big freed RECIPE-region node (nulls + main_arena) is %s-safe (that's why the libc-leak node works). CONFIRMED dead end for show_recipes heap leak.
- GOOD: show_recipes on R AFTER the arb-write IS safe IF cook4's dish has price=0,energy=0: R slots = [environ, 0,0, price0, energy0, next(heap), prev(heap), 0..] all readable => stack leak works, process alive. So the READ side is fine once FD works.

### (2) The rm for the heap leak ALWAYS frees a 0x90 recipe (=> FD poison), and it is unavoidable with the dish-fake-node:
- Heap leak needs a freed dish shown in the DISH list (show_dishes, the only %s-safe printer). Only the type-confusion rm keeps a freed dish in the dish list; sell/eat unlink it.
- rm matches by title; D3's name == its cook-recipe's title; the cook-recipe is ALWAYS earlier in the list than D3 (it must exist before the 3rd cook, and cooking D3 into YY requires YY free => no 0x90-recipe can sit between CC and the cook or it eats the 0x120 YY). So rm hits the cook-recipe (0x90) first => lone 0x90 => FD (next recipe add) reuses it => FD->next=0x90 => cook's internal show_recipe crashes. DEAD END for this path.
- A 0x40-sized CC->next fake node WOULD fix it (0x90 cook-recipe X goes to top, D3=0x40 lands in YY, X ends up AFTER D3 so rm(Xtitle) hits D3 first = frees 0x40, no 0x90). But making CC->next point at a <0x90 chunk needs a groom re-engineering not yet found (the consolidate+split only produced a 0x120 node).

### => FINISH likely needs a DIFFERENT core primitive, not the dish-fake-node dup. Prime candidate: the recipe->next @ user+0x80 == next-chunk prev_size bug + type-confusion free to drive BACKWARD CONSOLIDATION with a controlled prev_size => overlapping chunks => directly corrupt a live recipe's ->next / ingredient ptr => arb R/W, bypassing the fastbin-dup+FD entirely. (Or a reference writeup to shortcut.)
- Everything else is READY: libc_base, heap_base, environ, R(base+0x980, title[0x10]=0x41), SLOT=p64(environ), the arb-READ output path (show_recipes on R, price0 dish), ORW target (fd 3, seccomp blocks execve).

## SESSION 2 (cont) — prev_size / uninitialized-next direction
### No buffer-overflow primitive:
- All string/number input uses __read_chk (fortified, size-checked) or scanf "%23s" (bounded). Integer read 0x1134 = __read_chk(0, buf, 0x17, 0x18). No off-by-one / overflow => classic House of Einherjar (needs to clear a chunk prev_inuse via overflow) is NOT directly available.
- The ONLY memory-corruption bug is recipe->next (@user+0x80) being UNINITIALIZED by add_recipe (memset covers only 0x80 bytes). recipe->next == the next chunk's prev_size field.
### What recipe->next gives:
- On FREE of recipe A: set_foot writes A's size (0x90) into P(next)->prev_size == A->next  => the "0x90 poison".
- On ALLOC-from-split: A->next = stale data at that offset = whatever bin fd/bk or old content was there (this is how CC->next ends up = &YY, a heap chunk pointer => a FAKE LIST NODE).
### Fake-node primitive (the real lever):
- CC->next = &YY where YY is a freed/binned chunk. show_recipes reads YY+0 as the "title" (=%s of the 8 bytes there). YY+0 = chunk fd = main_arena (sole in bin) => LIBC leak (works, alive). YY+0x18 (an "ingredient" slot) = a HEAP pointer (leftover) but it is printed as %s-at-that-address (food name), NOT as the pointer value, so it is NOT a direct heap-address leak.
- To get a HEAP-ADDRESS leak this way, need CC->next target's +0 (fd) to be a HEAP ptr = the target must have an in-bin successor (2+ chunks in its bin). Current groom leaves it sole (fd=main_arena+0x168, i.e., a small/large bin head). Adding more freed recipes AFTER CC hits the 0x90-poison (can't). Need a groom that leaves 2 chunks in one bin, created BEFORE CC. NOT yet built.
- Weaponization path (not finished): make a recipe's ->next point at a chunk whose content I CONTROL (reallocate YY as a dish/food and write YY+0/+0x18), turning it into a controlled fake recipe node => arb read (show title), arb free (rm), and chain ->next for deeper R/W. Intricate multi-step grooming; the stale-leftover value is a BIN pointer (hard to force to an arbitrary libc addr like environ), so steering it to exactly a chosen target is the open problem.

### HONEST STATE: Two leaks + fastbin cycle + arb-0x40-alloc mechanism are solid. Every onward path (dish-dup FD, show_recipes-dish leak, Einherjar, controlled CC->next) is blocked by a specific, documented constraint (0x90 poison / dish-slot %s crash / no overflow / bin-pointer leftover not arbitrary). Finishing almost certainly needs a reference writeup or a technique insight not yet found via experimentation.

## SESSION 2 — DEEP RE of ALL handlers (decisive structural facts)
### No overflow / OOB anywhere:
- Inputs: numbers via __read_chk(0, buf, 0x17, 0x18)+atoll (0x1134); strings via a read wrapper + strncpy(0x1f for food, 0x18 for title) — all FORTIFIED/bounded. Only one sprintf (Magic, fixed format). No strcpy/memcpy/gets.
- foods_ptr = a 0x50 chunk (10 ptr slots). make/buy loop i=0..9 (bounded); full => "no space". No OOB array write.
- Ingredient index in add_recipe/show bounds-checked (unsigned cmp vs count @0x20506c). Negative => huge unsigned => rejected.
### CRITICAL: foods have FIXED names.
- init (0x1e95) creates foods with hard-coded names (Egg, Pineapple, Flouir, Suger, Beef, Apple, Salt, Pork, Scallion) + fixed price/qty.
- make (shop opt 3) and buy (opt 1) pick an ingredient BY INDEX (read-int), not by name => NO user-controlled food name.
- => the ONLY attacker-controlled bytes written into heap chunks are RECIPE TITLE and DISH NAME (= recipe title via cook): 0x17 bytes at chunk+0, scanf "%23s" so NO null and NO whitespace (0x09-0x0d,0x20). Recipe INGREDIENT slots are always real food pointers (foods_ptr[idx]); recipe ->next is uninitialized/stale; dish price/energy/next/prev are numbers/heap-list ptrs. None are arbitrary attacker pointers.
### Consequences for the finish (why it is hard):
- A fake recipe node's "title" (%s of node+0) prints CONTROLLED bytes (not a leak); a leak requires node+0 == a stale pointer (freed-chunk fd) => libc leak works; heap leak needs node+0 == heap (2-chunk bin) [feasible, not built]; a STACK leak would need a slot/field == &environ or *environ, which cannot be set (foods only, titles have no nulls) => stack leak appears infeasible with current primitives.
- ORW w/o execve => __free_hook = setcontext/stack-pivot + a fake ucontext (needs many controlled qwords incl nulls) OR a ROP chain, but controlled heap data is title-only (no null). This no-null, numbers-only constraint makes ucontext/ROP crafting very hard. 
- The fastbin arb-0x40-alloc (if FD-clean were solved) writes a DISH there, whose body = name(title, no null) + numbers — again constrained.
### BOTTOM LINE: the single bug (uninit recipe->next) + title-only, no-null controlled data is a tight box. A working exploit exists (500pt chall) but needs the specific intended chain.

## SESSION 2 — *** CLEAN libc+heap LEAK IN ONE GROOM (no 0x90, process ALIVE) ***
### The groom (god2; 4 recipe groups each becomes a 0x120 via pairwise free+merge, barriers=cook):
  add A1,B2; cook BN; add C3,D4; cook BN; add E5,F6; cook BN; add YY,Z9; cook BN
  rm order: B2,A1,D4,C3,F6,E5,Z9,YY   (pairwise-reverse within each group)
  add CC
=> recipe chain: PC -> BN -> CC -> NODE1 -> NODE2 -> NODE3 -> 0, where NODE1/2/3 are the leftover 0x120 smallbin chunks (CC consumed one of the four).
=> show_recipes (menu 1 then 3) prints each node's title = %s of node+0 (the chunk fd):
   titles = [ 'Pineapple cake', 'Beef noodles', 'CC', <main_arena>, <heap>, '' ]
   ts[3] = main_arena pointer  => libc_base = u64(ts[3][:6]) - 0x3c1c68   (page-aligned, VERIFIED)
   ts[4] = heap pointer        => heap_base = u64(ts[4][:6]) & ~0xfff     (leak = heap_base + 0x8a0)
   PROCESS STAYS ALIVE (0x120 nodes have safe %s slots; chain ends with ->next=0). NO rm, NO 0x90.
### Why it works: with 4 merged 0x120 groups, add CC leaves 3 in smallbin[0x120] linked; CC->next lands on the bin-TAIL-ish node whose fd=main_arena (libc), and that node's ->next walks to a bin-HEAD/mid node whose fd=heap (heap leak). Order controls which node has fd=libc vs fd=heap.
### THIS UNBLOCKS THE EXPLOIT: after the clean leak (no 0x90 anywhere), add R(title[0x10]=0x41)+SLOT(p64(environ))+FD(p64(R+8)) from TOP => all clean (->next=0). Then build the dish fastbin[0x40] double-free cycle; the type-confusion rm there frees only 0x40 dishes (no 0x90 recipe freed if matched right) OR even if a 0x90 is freed later it is never re-added into the list. cook(FD) works (list clean). Script: /tmp/hleak2.py (leaks both, alive). Groom harness: probe16.py.
### TODO next: lock heap offsets (R lands at heap_base+? after appends), rebuild dish-dup cycle on THIS groom, then arb 0x40 alloc -> R.slot0=environ -> stack leak -> ROP/ORW(fd3).

## SESSION 2 — RUNNABLE DELIVERABLE + final arb-write wall
### exploit_leaks.py (god2): WORKS. One groom -> libc_base (page-aligned) + heap_base + system/__free_hook/environ, process ALIVE. This is the solid, reproducible leak stage. cook() still works after it (dishes are 0x40, don't touch the 0x120 fake nodes).
### Why arb-write is still walled (all avenues tested this session):
- Need ONE recipe titled p64(R+8) (to drive fastbin[0x40] fd) OR R with title[0x10]=0x41 (fake 0x40 size). Adding ANY recipe (malloc 0x90) after the leak reuses a freed 0x90 (->next=0x90) or splits a 0x120 fake node (->next=stale ptr / breaks the chain). First post-leak add => poisoned/garbage ->next; the 2nd add's append walks through it => crash. So you can add at most 1 poisoned recipe and then cannot cook (cook calls show_recipe which walks the WHOLE list -> hits the bad ->next -> crash). Confirmed.
- Cannot add a recipe from TOP (clean ->next=0) because the groom leaves 0x90/0x120 free chunks that malloc(0x90) consumes first; and those 0x120 are the in-list fake nodes (can't clear them without breaking the chain / without a write primitive).
- Cooking only makes 0x40 dishes whose name == an EXISTING recipe title (PC/BN/CC or the leak nodes' leftover titles). The leak nodes' titles are 0x120-chunk addresses => cooking one sets fastbin fd to a 0x120 chunk => size check 0x120!=0x40 => "malloc(): memory corruption (fast)" abort. No way to point the fastbin at a crafted 0x40 fake size without FD.
- Unsorted-bin attack needs a controlled freed-chunk bk (user+0x8). Writing a freed chunk's bk needs a UAF write or title overlap; free() overwrites bk with main_arena, and there is no primitive to rewrite a freed chunk's bk. No controlled bk => no unsorted attack.
- No overflow/off-by-one (fortified reads) => no House of Einherjar.
### CONCLUSION: the clean libc+heap leak is solved and runnable.

## SESSION 2 — *** BREAKTHROUGH 2: FOOD arb-write to libc () ***
### I WAS WRONG that food names are fixed. `make` (shop opt 3) reads an "Ingredient :" NAME and CREATES a food with that user-controlled name (strncpy 0x1f bytes, no mid-null). VERIFIED: make(b"ZZZWXYQ9") => foods[5] name="ZZZWXYQ9".
### Food = 0x28 req -> 0x30 chunk -> fastbin[0x30]. There IS a fake 0x30 size in libc at these spots (val 0x3b/0x3c, fastbin_index==1==0x30 bin):
  - libc+0x3c1ad2 (val 0x3b) => food-user @ libc+0x3c1ada  == __memalign_hook-0x6; so a food here overwrites __memalign_hook(+0x6), __realloc_hook(+0xe), __malloc_hook(+0x16) with the CONTROLLED food NAME.  <-- classic hook overwrite
  - libc+0x3c18b2 (val 0x3b) => food-user @ libc+0x3c18ba  overlaps _IO_2_1_stdin_(+0x6)
  - libc+0x3c25c2 (val 0x3c) => food-user @ libc+0x3c25ca  near _IO_2_1_stdout_-0x36 (food 0x20 ends before stdout+0)
### => PLAN: (1) clean libc leak; (2) FOOD fastbin[0x30] double-free (type-confusion rm on a food placed at CC->next fake node; now have heap leak to satisfy re-match) ; (3) make with name=p64(libc+0x3c1ad2) to set fastbin[0x30] fd; (4) make (cycle) to alloc a food @ libc+0x3c1ada and write a CONTROLLED name over __realloc_hook (hit first by realloc(0,size) which the program uses for all allocs) = gadget/stack-pivot; (5) trigger realloc -> RIP -> ORW (read fd3, write fd1). Program allocates via realloc(0,size) so __realloc_hook fires. Food name is no-null (strncpy stops at null) so hook value must be null-free (libc addr 0x7f.. ok, high2=0 via strncpy pad).
### TODO: build food double-free (fastbin[0x30]) + verify fd control via make-name; pick ORW gadget for __realloc_hook(rdi=0,rsi=size,rdx=caller) or pivot; "" likely = final ORW writes flag to stdout, or FSOP on a FILE via same food primitive.

## SESSION 2 — *** ARBITRARY READ COMPLETE (3 leaks, process alive): exploit2.py ***
### THE FD-POISON WALL IS BROKEN. Key insight: after the dd6 dish-dup, MAKE 2 FOODS (0x30) consume the lingering free chunks, so subsequent recipe adds come clean (->next valid). Verified: dd6 dup + 2 foods + add R,FD,SLOT => ALL CLEAN, and the fastbin[0x40] cycle stays intact (foods/recipes are 0x30/0x90, not 0x40).
### Full working flow (exploit2.py, god2):
  1. dd6 groom (add UNIQ777; A1,B2;cook;YY,Z9;cook; rm B2,Z9,A1,YY; add CC) -> CC->next=&YY. LIBC leak = u64(last show_recipes title)-0x3c1c68 (ts[-1]=YY=main_arena+0x168). page-aligned.
  2. cook BN(E=#2),BN(D1=#3),UNIQ777(D3=#4@YY). sell(2)=free E. rm UNIQ777 x2 = free recipe + free D3 (D3 stays listed, D3.fd=&E). show_dishes -> D3 name = &E = HEAP leak. heap_base = leak & ~0xfff.
  3. CYCLE: sell(0) (free a 0x40 groom dish = intervening; the price-0 drains are 0x50 so DON'T use them as intervening) ; sell(2) (free D3 again) -> fastbin[0x40] cycle [D3,x,D3].
  4. make 2 foods (ff0,ff1) -> clean recipe adds enabled.
  5. add R (b"R"*16+b"A"; R+0x10=0x41 fake 0x40 size), add FD (p64(R+8)[:6]; sets fastbin fd), add SLOT (p64(environ)[:6]). R lands at heap_base+0x980. All clean.
  6. cook FD; cook FD; cook FD; cook SLOT  -> arb 0x40 alloc at R+8 (user R+0x18=R.slot0); R.slot0 = environ.
  7. show_recipes -> R ingredient[0] = printf("%s",environ) = STACK leak (the dish from SLOT has price0/energy0 so R.slot1.. are null/heap = safe). process ALIVE.
### SCANF-SAFE: FD/SLOT titles are 6 bytes, must avoid 0x00/0x09-0x0d/0x20 (retry on remote ASLR). R title has no null.
### I now have: libc_base, heap_base, stack leak, an ARBITRARY READ (set R.slot0=X via the same cook cycle -> show_recipes -> *X), and a fastbin[0x40] arb-ALLOC (write a 0x40 dish, name=recipe title no-null, at any addr with a 0x40 fake size at +8).
### TODO (final): arb-WRITE -> ORW. Options: (a) scan stack (arb-read) for saved retaddr + a 0x40-ish fake size, arb-alloc a dish to drop a stack-pivot/ROP; (b) bootstrap fastbin[0x30] (food) from the 0x40 alloc or a food double-free -> write __realloc_hook (0x30 fake @ libc+0x3c1ad2) = gadget; program allocs via realloc(0,size) so __realloc_hook fires. ORW = read(3,buf,n)+write(1,buf,n); flag fd=3 preopened.

## SESSION 2 — FINAL WRITE/ORW CONSTRAINT MAP (the remaining blocker)
### Facts found:
- PIE base = libc_base + 0x3c7000 LOCALLY (ld-2.24 loader maps the binary right after libc; the stack "saved RIPs" are at libc+0x3c7xxx = program .text). So BSS globals (recipe/dish/foods heads, secret) are derivable locally without a separate PIE leak. (Remote layout differs -> needs check.)
- Fastbin write target survey (what has a usable fake size for our alloc sizes 0x30 food / 0x40 dish):
  - 0x40 (dish) fake size: ONLY re_max_failures@libc+0x3c11e1 (useless). NONE near hooks/FILE/arena. So the 0x40 arb-alloc is HEAP-ONLY (plus crafted 0x41 in heap content).
  - 0x30 (food) fake size: libc+0x3c1ad2 -> food user @ __memalign_hook-6 (overwrites __realloc_hook/__malloc_hook); libc+0x3c18b2 -> stdin; libc+0x3c25c2 -> food ends at 0x3c25ea, does NOT reach _IO_2_1_stdout_(0x3c2600) or stderr vtable.
  - NO 0x30 or 0x40 fake size anywhere near __free_hook(0x3c3788). So __free_hook (the clean setcontext ORW: free(ptr)->setcontext(rdi=ptr)) is UNREACHABLE by fastbin alloc.
  - No 0x40 fake size on the stack near the saved return addresses -> stack-ROP write blocked too.
### => The ONLY reachable code-ptr write is __realloc_hook/__malloc_hook (via a food 0x30 fastbin). But the program calls realloc(0,size)/malloc(size): hook is invoked as hook(rdi=0_or_size, rsi=size, rdx=caller) -- rdi is NOT a controlled pointer, so setcontext(rdi) doesn't work and there is no clean single-gadget stack-pivot to a heap ROP chain. THIS is the open problem.
### Also: food fastbin[0x30] DOUBLE-FREE itself is intricate (needs F->next=&F self-loop; F+0x80 is misaligned to food boundaries so needs the dish 0x40 arb-alloc to write it; the dish-dup that gives the 0x40 alloc sets CC->next=0, which conflicts with placing a food fake node at CC->next). Heap leak for the self-loop addr can come from a food fake node whose name[0x18:]=p64(main_arena+0x60) -> show_recipes prints %s of *top = a heap ptr.
### STATE: arb-read (3 leaks) + 0x40 heap-write are solid and runnable (exploit2.py).

## SESSION 2 — *** ORW MECHANISM SOLVED (realloc(node,0) -> setcontext(rdi=node)) ***
### KEY: rm (remove_recipe) and eat free via realloc(node, 0). In glibc 2.24, realloc(ptr,0) with __realloc_hook set calls __realloc_hook(ptr=node, 0, caller) => rdi = node (a CONTROLLED chunk)! So:
  1. food fastbin[0x30] double-free -> fd = libc+0x3c1ad2 -> make a food @ libc+0x3c1ada with name = <0xe bytes pad> + p64(setcontext_gadget)[:6]  => writes __realloc_hook = setcontext (food+0xe), __malloc_hook = 0 (food+0x16, via strncpy null-pad), __memalign_hook = pad(harmless).
     setcontext gadget (2.24) = setcontext+0x35 area: `mov rsp,[rdi+0xa0]; ... ; mov rcx,[rdi+0xa8]; push rcx; ret`. setcontext=libc+0x48010.
  2. rm (or eat) a chunk C that I control => realloc(C,0) => __realloc_hook(C) => setcontext(C): rsp=[C+0xa0], rip=[C+0xa8]. Put a ROP stack ptr at C+0xa0 and a `ret` at C+0xa8 => pivot to a heap ROP chain.
  3. ROP (heap, via dish/food names, libc gadgets): read(3, buf, 0x100); write(1, buf, 0x100). flag fd=3 preopened. (open already done by the service.)
### CAVEAT ON TRIGGER: after writing __realloc_hook, the NEXT realloc fires it. rm's first alloc-op is realloc(node,0) (rdi=node) -> good. Avoid any add/cook (realloc(0,size): rdi=0 -> setcontext(0) crash) between the hook-write and the rm trigger. Set __malloc_hook=0 so printf/puts internal mallocs (if any) are safe.
### REMAINING BUILD (large but conceptually complete): food fastbin[0x30] double-free (self-loop F->next=&F via the dish 0x40 arb-alloc, since F+0x80 is misaligned to food boundaries; the dish-dup gives the 0x40 alloc but sets CC->next=0 so the food fake node must be re-established) + craft C's fake ucontext (C+0xa0/+0xa8) + place the ROP chain (multiple 0x40 writes, libc gadgets no-null via strncpy pad). Many slow iterations but each piece is understood.
