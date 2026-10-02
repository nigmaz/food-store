# Food Store (pwnable.tw) — View Source: chức năng & luồng thực thi

> **Mục đích**: tài liệu reverse-engineering phục vụ học tập / **BlueTeam** trên một binary CTF
> có sẵn ở local. Không nhắm vào hệ thống thực.
>
> **Nguồn & cách kiểm chứng**: hợp nhất `images/README.md`, `images/README.txt`, hai PDF
> (`…Dịch ngược mã C.pdf`, `…Giải challenge Food Store.pdf`), bản decompile
> `food_store_patched.c`, **và đối chiếu lại ở mức assembly** với IDB đang mở qua MCP
> (`food_store_patched.i64`, module `vuln`, imagebase `0x0`). Mọi offset/struct/luồng dưới đây
> đều đã kiểm chứng bằng disasm thực tế, không chỉ dựa vào pseudocode Hex-Rays.
>
> Xem thêm phần đính lỗi & đánh giá tính khai thác ở `images/README_new.md` và hướng khai
> thác ở `images/expl_writeup.md`.

---

## 1. Tổng quan

Binary là một **game quản lý quán ăn** text-based chạy theo vòng lặp menu. Người chơi có
kho nguyên liệu (pantry), công thức (recipe), món đã nấu (cooked food), cửa hàng (shop) và
nhiệm vụ NPC (assignment). Mục tiêu CTF: đọc `/home/food_store/flag` (được `fopen` sẵn khi
khởi động, trước khi bật seccomp).

| Thuộc tính | Giá trị |
|---|---|
| Kiến trúc | x86-64, PIE, dynamically linked |
| Bảo vệ | Full RELRO · Stack Canary · NX · FORTIFY (`*_chk`) · seccomp-BPF · `alarm(60)` |
| libc đi kèm | **glibc 2.24** (`Ubuntu GLIBC 2.24-9ubuntu2.2`), loader `ld-2.24.so` |
| Allocator | `realloc(0,n)` dùng như `malloc`; `realloc(p,0)` dùng như `free` |
| Heap (2.24) | **chưa có tcache**; chỉ fastbins (chunk ≤ `0x80`) + unsorted/small/large; còn `__malloc_hook`/`__free_hook` |

### Seccomp (giải mã trực tiếp từ bytes `0x36E0`, 25 lệnh BPF)
`ALLOW`: `read(0)`, `write(1)`, `open(2)`, `close(3)`, `mmap(9)`, `munmap(11)`, `writev(20)`,
`rt_sigreturn(15)`, `exit(60)`, `exit_group(231)`. Mặc định **`KILL`**.
→ **không có `execve`/`openat`/`mprotect`**. Vì `open(2)` được phép → hướng hợp lệ là **ORW**
(open→read→write). (Bộ lọc được nạp trong `fn_install_seccomp_filter_F00` ngay sau
`fn_game_init_FFC`, trước phần lớn cấp phát heap.)

---

## 2. Cấu trúc dữ liệu (offset đã xác nhận ở assembly)

### `Ingredient` — `realloc(0, 0x28)` → **chunk 0x30** (fastbin)
```c
typedef struct {
    char     name[0x20];   // +0x00   strncpy(..., 0x1F)  (xem ghi chú §6)
    uint32_t price;        // +0x20
    uint32_t quantity;     // +0x24
} Ingredient;
```

### `Recipe` — `realloc(0, 0x88)` → **chunk 0x90** (unsorted/small khi free)
```c
#define MAX_ING 13
typedef struct Recipe {
    char           title[0x18];     // +0x00   scanf("%23s")
    Ingredient    *ingredients[13]; // +0x18 .. +0x7F  (trỏ thẳng vào Ingredient trong pantry)
    struct Recipe *next;            // +0x80   (singly linked list)
} Recipe;
```

### `CookedFood` — `realloc(0, 0x38)` → **chunk 0x40** (fastbin) — **vòng-đôi**
Offset xác nhận trong `fn_cooked_food_list_print_25E1` (`[+0x18]`,`[+0x20]`,`[+0x28]`) và
`fn_sell_2744` (`[+0x30]`,`[+0x28]`):
```c
typedef struct CookedFood {
    char               name[0x18];  // +0x00   strncpy(recipe->title, 0x18)
    uint32_t           sell_price;  // +0x18   = total_cost * 1.217
    uint32_t           _pad;        // +0x1C
    uint64_t           energy;      // +0x20   = total_cost / 0x1C
    struct CookedFood *next;        // +0x28
    struct CookedFood *prev;        // +0x30
} CookedFood;                        // size 0x38
```

### Bảng slot pantry/shop — `realloc(0, 0x50)` → **chunk 0x60** (fastbin)
Không phải mảng struct mà là **1 khối chứa 10 con trỏ `Ingredient*`** (`*(QWORD*)&slots->name[8*i]`).
`g_pantrySlots` và `g_shopSlots` trong `.bss` chỉ giữ **1 con trỏ** tới khối heap này.

---

## 3. Bản đồ `.bss` đầy đủ (rất quan trọng cho khai thác)

```
0x205020  stdout   (FILE*)   ← COPY reloc, TRỎ tới _IO_2_1_stdout_ trong libc  ← leak libc nếu đọc được
0x205030  stdin    (FILE*)   ← TRỎ tới _IO_2_1_stdin_
0x205040  stderr   (FILE*)   ← TRỎ tới _IO_2_1_stderr_
0x205048  byte_205048        (cờ dùng trong sub_E90)
0x205050  g_tmpMsgBuf        char*  realloc(0,0x80) → chunk 0x90, ổn định suốt đời chương trình
0x205058  g_flagFile         FILE*  "/home/food_store/flag" (mở trước seccomp)
0x205060  g_foodListHead     CookedFood*  (vòng-đôi)          [IDA note: Shell_2744/eat/assignment - bug]
0x205068  g_shopRestockEpoch u32
0x20506C  g_pantryCount      u32
0x205070  g_shopCount        u32
0x205080  g_shopSlots        Ingredient**  (→ khối heap 10 con trỏ)
0x2050A0  g_playerName[8]    (đọc tối đa 7 byte)
0x2050A8  g_playerLevel      i32  (init = 1)
0x2050B0  g_playerXPBar      u64  (0..0x63)
0x2050B8  g_playerPower      u64  (init = 20)
0x2050C0  g_playerMoney      u64  (init = 100)
0x2050C8  g_pantrySlots      Ingredient**  (→ khối heap 10 con trỏ)
0x2050D0  g_recipeListHead   Recipe*       [IDA note: removeRecipe_1B90 - bug]
0x2050D8  g_heapMagicKey[8]  8 byte random /dev/urandom (cho chuỗi "Magic")
```

> **Điểm then chốt**: `stdout/stdin/stderr` nằm ngay đầu `.bss`, kề các global game. Giá trị tại
> `0x205020` là **con trỏ libc** (`&_IO_2_1_stdout_`) → nếu có arbitrary-read là leak libc ngay;
> nếu ghi đè được cấu trúc `_IO_2_1_stdout_` → FSOP (xem `expl_writeup.md`).

---

## 4. Ánh xạ hàm (địa chỉ IDA → tên → chức năng)

| Addr | Tên | Chức năng |
|------|-----|-----------|
| `0xFFC` | `fn_game_init_FFC` | setvbuf; `srand(time)`; `fopen(flag)`; cấp `g_tmpMsgBuf(0x80)`; đọc 8 byte `/dev/urandom`→`g_heapMagicKey`; `signal(SIGALRM)`; `alarm(60)` |
| `0xF00` | `fn_install_seccomp_filter_F00` | dựng BPF từ `g_dataSeccomp_36E0`, `prctl(NO_NEW_PRIVS)`, `prctl(SET_SECCOMP)` |
| `0x32BA` | `fn_patch_seccomp_labels_32BA` | vá nhãn jt/jf trong BPF trước khi nạp |
| `0x34B3` | `fn_get_or_add_label_index_34B3` | resolver nhãn BPF (≤256) |
| `0x35BB` | `fn_sock_filter_35BB` | dump BPF `{code,jt,jf,k}` (debug, không reachable từ menu) |
| `0x1134` | `fn_read_number_1134` | `_read_chk(0,buf,23,24)` rồi `atoll` → đọc 1 dòng số |
| `0x11FF` | `fn_read_string_11FF` | `_read_chk(0,buf,n,n)` rồi cắt `\n` cuối |
| `0x11C0` | `fn_printf_msg_11C0` | `printf("%s", s)`; nếu cờ ≠ 0 thì `exit(-1)` |
| `0x1276` | `fn_pantry_add_or_update_ingredient_1276` | thêm/cộng dồn nguyên liệu vào pantry |
| `0x141B` | `fn_shop_add_or_update_ingredient_141B` | thêm/cộng dồn nguyên liệu vào shop |
| `0x15C0` | `fn_pantry_list_ingredient_15C0` | in pantry (No/Ingredient/Quantity/Price) |
| `0x16A4` | `fn_recipe_print_menu_16A4` | menu Recipe |
| `0x1721` | `fn_recipe_attach_ingredient_1721` | gắn 1 `Ingredient*` vào `recipe->ingredients[]` (≤13) |
| `0x17DC` | `fn_add_new_recipe_17DC` | tạo recipe + in **"Magic"** (`addr(chunk) XOR key`) + chọn nguyên liệu |
| `0x1A9B` | `fn_show_recipe_1A9B` | in toàn bộ recipe (tuỳ cờ: kèm nguyên liệu) |
| `0x1B90` | `fn_remove_recipe_1B90` | xoá recipe theo title; `realloc(node,0)` |
| `0x1CA9` | `fn_recipe_1CA9` | vòng lặp menu Recipe (gate theo level) |
| `0x1D5A` | `fn_chef_info_1D5A` | in Name/Level/Power/Money |
| `0x1DF4` | `fn_main_menu_print_1DF4` | menu chính |
| `0x1E95` | `fn_init_default_player_pantry_and_recipes_1E95` | 5 nguyên liệu + 2 recipe mặc định |
| `0x2149` | `fn_shop_init_inventory_2149` | 9 nguyên liệu shop + lưu `g_shopRestockEpoch` |
| `0x2259` | `fn_cook_2259` | nấu: trừ power/quantity, +exp, tạo `CookedFood`, chèn vào vòng |
| `0x25E1` | `fn_cooked_food_list_print_25E1` | in danh sách món đã nấu (No/Name/Price/Energe) |
| `0x26C7` | `fn_menu_shop_26C7` | menu Shop |
| `0x2744` | `fn_sell_2744` | bán 1 món: +money, **unlink (không check)**, free |
| `0x2895` | `fn_make_2895` | tự chế nguyên liệu (level>3, tốn 100): đọc **31 byte tuỳ ý** |
| `0x2A12` | `fn_eat_2A12` | ăn 1 món: +power, **unlink (không check)**, free |
| `0x2B62` | `fn_assignment_2B62` | NPC đòi món ngẫu nhiên; nếu có món trùng tên → +exp/+money, **unlink**, free |
| `0x2DCA` | `fn_shop_list_and_autorestock_2DCA` | in shop + auto-restock theo thời gian |
| `0x2F40` | `fn_buy_2F40` | mua nguyên liệu về pantry |
| `0x30E3` | `fn_shop_30E3` | vòng lặp menu Shop |
| `0x316C` | `fn_player_init_profile_316C` | hỏi tên (7 byte); set level=1/power=20/money=100 |
| `0x31C5` | `main` | init + vòng lặp menu chính |

---

## 5. Luồng thực thi

### 5.1 Khởi động (`main` @ 0x31C5)
```
fn_game_init_FFC()                              // IO, srand, mở flag, g_tmpMsgBuf, magic key, alarm
fn_install_seccomp_filter_F00()                 // BẬT seccomp (từ đây không mở file mới ngoài open hợp lệ)
fn_init_default_player_pantry_and_recipes_1E95()// pantry: Egg,Pineapple,Flouir,Suger,Beef
                                                // recipe: "Pineapple cake", "Beef noodles"
fn_player_init_profile_316C()                   // tên 7 byte; level=1, xp=0, power=20, money=100
fn_shop_init_inventory_2149()                   // shop: Egg,Pineapple,Flouir,Suger,Apple,Beef,Salt,Pork,Scallion
loop: fn_main_menu_print_1DF4(); dispatch(read_number())
```

### 5.2 Dispatch menu chính
| Chọn | Hành động | Prompt/đọc |
|---|---|---|
| 1 | Recipe (submenu) | — |
| 2 | `fn_assignment_2B62` | `"...I want to eat %s..."`, `"Your choice (1/Yes,0/No) :"` |
| 3 | `fn_chef_info_1D5A` | in thông tin |
| 4 | Shop (submenu) | — |
| 5 | `fn_cook_2259` | `show_recipe(0)`, `"What do you want to cook :"` read_string(0x18) |
| 6 | `fn_eat_2A12` | list, `"What do you want to eat ? :"` read_number |
| 7 | Exit | `fclose(flag)`, `exit(0)` |

### 5.3 Submenu Recipe (`fn_recipe_1CA9`)
| Chọn | Hành động | Gate |
|---|---|---|
| 1 | `fn_add_new_recipe_17DC` | `level > 1` |
| 2 | `fn_remove_recipe_1B90` | `level > 2` |
| 3 | `fn_show_recipe_1A9B(1)` | — |
| 4 | Return | — |

**`fn_add_new_recipe_17DC`** (chi tiết, vì chứa "Magic"):
1. `new_rec = realloc(0, 0x88)`.
2. Lấy **8 byte giá trị con trỏ `new_rec`** (= địa chỉ chunk), XOR từng byte với `g_heapMagicKey[i]`,
   `sprintf("%02X")` → chuỗi hex.
3. Zero `ingredients[0..12]`.
4. In `"Magic : <hex>\n"`  → **in đúng chuỗi hex** (assembly `1913 mov rdx,rax` xác nhận có truyền đối số).
5. `"Title :"` → `scanf("%23s", new_rec)` → `getchar()`.
6. In pantry; vòng: `"Choose ingredient :"` read_number (idx, bound `< g_pantryCount`) → `attach`;
   `"Add more ingredient ? (1/Yes,2/No) : "` read_number.
7. Nối `new_rec` vào cuối SLL `g_recipeListHead`.

> ⇒ **Magic = `địa_chỉ_chunk_recipe XOR key8`** (đúng, nhưng muốn dùng phải khôi phục `key`).

### 5.4 Submenu Shop (`fn_shop_30E3`)
| Chọn | Hành động | Gate |
|---|---|---|
| 1 | `fn_buy_2F40` | — |
| 2 | `fn_sell_2744` | — |
| 3 | `fn_make_2895` | `level > 3` |
| 4 | Return | — |

- **Buy**: `shop_list_and_autorestock()` (in + `"What do you want to buy ? :"`) → read_number(idx 0..9)
  → `"Quantity :"` read_number(qty). Check tồn kho `stock ≥ qty`, check tiền `money ≥ qty*price`
  (cost tính **u32** — tràn lý thuyết nhưng bị chặn bởi tồn kho), rồi chuyển về pantry.
- **Sell**: list → `"What do you want to sell ? :"` read_number(idx) → +money → **unlink** → free.
- **Make**: tốn 100, `"Ingredient :"` → `read_string(0x1F)` vào chunk `0x28` đã `memset(0x20)`
  → **31 byte nội dung do người chơi hoàn toàn kiểm soát** (price = `rand()%500`, qty = 1).

### 5.5 Cook / Eat / Assignment — thao tác vòng-đôi `CookedFood`
- **Cook**: tìm recipe theo title; `power ≥ 10` (trừ 10); trừ quantity từng nguyên liệu (hết → báo lỗi + exit);
  `xp += 60` (cap 0x63, vượt → `++level`); tạo `CookedFood` (`sell_price`, `energy`, `name` từ title);
  chèn vào cuối vòng `g_foodListHead`.
- **Eat/Sell/Assignment**: duyệt vòng tới node cần, cập nhật power/money/exp, rồi **unlink KHÔNG kiểm tra**:
  ```
  prev = node->prev; next = node->next;
  prev->next = next;   // *(prev+0x28) = next
  next->prev = prev;   // *(next+0x30) = prev
  realloc(node, 0);    // free
  ```
  Head được cập nhật nếu node là head. **Không có `prev->next==node`/`next->prev==node`**.

### 5.6 Bảng gate theo level & cách lên level
| Tính năng | Yêu cầu |
|---|---|
| Add recipe | level > 1 |
| Remove recipe | level > 2 |
| Make ingredient | level > 3 |

Lên level: **Cook** `+60` exp, **Assignment** `+80` exp; khi vượt `0x63` thì `++level`. Grind
`Cook`→`Eat` (Eat hồi power từ `energy`) để đạt level 4 mở **Make**.

---

## 6. Ghi chú kỹ thuật (đã kiểm chứng)

- **`strncpy(name, src, 0x1F)` không null-terminate** ở `1276`/`141B` là có thật, nhưng **không
  reachable** với tên dài do người chơi kiểm soát (init/shop dùng tên hard-code ngắn; `Make`
  `memset(0x20)` trước khi đọc → `name[31]=0`). ⇒ không thành info-leak thực tế.
- **Mọi `__printf_chk` đều truyền đủ đối số** (kiểm chứng `0x15C0`, `0x25E1`, `0x17DC`): pseudocode
  Hex-Rays chỉ **ẩn** varargs của họ `_chk`. ⇒ **không có** "format/vararg leak".
- **Bug lõi = unlink không kiểm tra** (sell/eat/assignment) → write-what-where có ràng buộc.
  IDB đã đánh dấu `Shell_2744 - bug`, `eat_2A12 - bug`, `assignment_2B62 - bug`.
- **`g_tmpMsgBuf`** (chunk `0x90`, địa chỉ ổn định trong `.bss` tại `0x205050`): nơi lý tưởng đặt
  ROP chain sau khi có leak.
- **`Make`**: nguồn **31 byte nội dung heap do người chơi kiểm soát hoàn toàn** → nguyên liệu
  dùng để dựng dữ liệu/fake-chunk cho heap feng-shui.
- Chunk/bin (glibc 2.24): Ingredient `0x30`, slots `0x60`, CookedFood `0x40` → **fastbin**;
  Recipe & tmpMsgBuf `0x90` → **unsorted/small** (vì > `0x80`). **Không tcache.**
