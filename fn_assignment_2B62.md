# `fn_assignment_2B62()` — giải thích logic theo từng dòng (mã giả)

> Chức năng **NPC đặt món — Assignment** (menu chính mục 2) của Food Store (pwnable.tw).

```c
int fn_assignment_2B62()
{
  unsigned int v1;                 // số recipe
  unsigned int i;                  // bộ đếm
  unsigned int v3;                 // chỉ số ngẫu nhiên
  struct Recipe *it;               // con trỏ duyệt / recipe được chọn
  struct Recipe *chosen;           //   (cùng ô với it)
  struct CookedFood *ptr_node;     // node đang xét
  struct CookedFood *prev_cooked_food;
  struct CookedFood *next_cooked_food;

  v1 = 0;
  if ( !g_recipeListHead_2050D0 )                               // (A)
    return puts("NPC: I am very hungry !");
  for ( it = g_recipeListHead_2050D0; it; it = it->next_recipe ) // (B)
    ++v1;
  v3 = rand() % v1;                                             // (C)
  chosen = g_recipeListHead_2050D0;
  for ( i = 0; i < v3; ++i )                                    // (D)
    chosen = chosen->next_recipe;
  _printf_chk(1LL, "NPC: I want to eat %s \n...", chosen->title);// (E)
  _printf_chk(1LL, "Your choice (1/Yes,0/No) :");
  if ( fn_read_number_1134() != 1 || !g_foodListHead_205060 )   // (F)
    return puts("NPC: So sad :(");
  ptr_node = g_foodListHead_205060;                            // (G)
  while ( strcmp(ptr_node->name, chosen->title) )              // (H)
  {
    ptr_node = ptr_node->next_cooked_food;
    ++i;
    if ( ptr_node == g_foodListHead_205060 )
      return fn_printf_msg_11C0("Can not find the food !", 0);
  }
  if ( g_playerXPBar_2050B0 + 80 <= 0x63 )                      // (I)
    g_playerXPBar_2050B0 += 80LL;
  else {
    ++g_playerLevel_2050A8;
    g_playerXPBar_2050B0 -= 20LL;
  }
  g_playerMoney_2050C0 += 434LL;                                // (J)
  prev_cooked_food = ptr_node->prev_cooked_food;               // (K) unlink
  next_cooked_food = ptr_node->next_cooked_food;
  prev_cooked_food->next_cooked_food = next_cooked_food;        //  *(prev+0x28)=next
  next_cooked_food->prev_cooked_food = prev_cooked_food;        //  *(next+0x30)=prev
  if ( ptr_node == g_foodListHead_205060 ) {                    // (L) cập nhật head
    if ( g_foodListHead_205060 == next_cooked_food )
      g_foodListHead_205060 = 0LL;
    else
      g_foodListHead_205060 = next_cooked_food;
  }
  realloc(ptr_node, 0LL);                                       // (M) free
  return puts("NPC: Thank you !");
}
```

---

## Khai báo biến
```c
unsigned int v1;   // số lượng recipe đang có
unsigned int i;    // biến đếm (dùng cho vòng lặp)
unsigned int v3;   // chỉ số recipe được chọn ngẫu nhiên
struct Recipe *it;       // con trỏ chạy để duyệt danh sách recipe
struct Recipe *chosen;   // recipe mà NPC "muốn ăn" (dùng chung ô nhớ với it)
struct CookedFood *ptr_node;          // node món đang xét trong danh sách vòng
struct CookedFood *prev_cooked_food;  // lưu tạm node phía trước (để unlink)
struct CookedFood *next_cooked_food;  // lưu tạm node phía sau (để unlink)
```

## (A) — Nếu chưa có công thức nào
```c
v1 = 0;
if ( !g_recipeListHead_2050D0 )
    return puts("NPC: I am very hungry !");
```
`g_recipeListHead` là đầu danh sách công thức (singly-linked). Nếu **NULL** (chưa tạo recipe nào) → in "NPC đói" và **thoát hàm ngay**. Dòng này cũng gián tiếp **chống chia cho 0** ở bước (C).

## (B) — Đếm số recipe
```c
for ( it = g_recipeListHead_2050D0; it; it = it->next_recipe )
    ++v1;
```
Duyệt toàn bộ danh sách recipe từ đầu đến hết (`it = it->next` cho tới khi `NULL`), mỗi node `++v1`. Kết thúc: `v1` = **tổng số công thức**.

## (C) — Chọn ngẫu nhiên 1 recipe
```c
v3 = rand() % v1;
chosen = g_recipeListHead_2050D0;
```
`v3` = một số ngẫu nhiên trong khoảng `[0, v1-1]` → chỉ số recipe NPC sẽ đòi. `chosen` bắt đầu từ đầu danh sách.
> `rand()` dùng seed `srand(time(0))` → về lý thuyết đoán trước được, nhưng không quan trọng cho logic game.

## (D) — Nhảy tới recipe thứ `v3`
```c
for ( i = 0; i < v3; ++i )
    chosen = chosen->next_recipe;
```
Đi `v3` bước từ đầu danh sách → `chosen` trỏ đúng recipe được chọn.

## (E) — NPC thông báo muốn ăn món gì
```c
_printf_chk(1LL, "NPC: I want to eat %s \n...", chosen->title);
_printf_chk(1LL, "Your choice (1/Yes,0/No) :");
```
In tên món (`chosen->title`) mà NPC muốn, rồi hỏi người chơi đồng ý giao không.
> Lưu ý: Hex-Rays *giấu* đối số `chosen->title` trong bản decompile gốc; thực tế assembly **có** truyền — đây **không** phải lỗi format-string.

## (F) — Kiểm tra trả lời & có món hay không
```c
if ( fn_read_number_1134() != 1 || !g_foodListHead_205060 )
    return puts("NPC: So sad :(");
```
Đọc lựa chọn. Thoát với "So sad" nếu **một trong hai**: người chơi **không** chọn 1 (Yes), **hoặc** danh sách món đã nấu (`g_foodListHead`) **rỗng**. (Toán tử `||` ngắn mạch: sai điều kiện đầu là thoát luôn.)

## (G)+(H) — Tìm món đã nấu trùng tên
```c
ptr_node = g_foodListHead_205060;
while ( strcmp(ptr_node->name, chosen->title) )
{
    ptr_node = ptr_node->next_cooked_food;
    ++i;
    if ( ptr_node == g_foodListHead_205060 )
        return fn_printf_msg_11C0("Can not find the food !", 0);
}
```
Bắt đầu từ đầu danh sách món đã nấu. Vòng `while` chạy **khi `strcmp != 0` (tức tên CHƯA khớp)**:
- Bước sang node kế tiếp (`->next`, danh sách **vòng tròn**).
- `++i` (chỉ là tăng biến thừa, không dùng lại — "code smell").
- Nếu đi hết một vòng và **quay về head** → nghĩa là không có món nào trùng → in "Can not find the food !" và thoát.

Khi `strcmp == 0` (khớp tên) → thoát vòng, `ptr_node` là món cần giao. Dùng `strcmp` (so chuỗi kết thúc `\0`), và cả `name` lẫn `title` đều null-terminate chuẩn → so khớp đúng.

## (I) — Thưởng kinh nghiệm / lên cấp
```c
if ( g_playerXPBar_2050B0 + 80 <= 0x63 )
    g_playerXPBar_2050B0 += 80LL;
else {
    ++g_playerLevel_2050A8;
    g_playerXPBar_2050B0 -= 20LL;
}
```
Nếu cộng 80 EXP mà vẫn `≤ 99 (0x63)` → cộng thẳng 80. Ngược lại (sẽ vượt ngưỡng) → **lên 1 level** và EXP `-= 20` (giữ lại phần dư). (Khác với `Cook`: Cook dùng +60 / -40.)

## (J) — Thưởng tiền
```c
g_playerMoney_2050C0 += 434LL;
```
Cộng 434 money.

## (K) — Gỡ node khỏi danh sách (UNLINK — điểm lỗi)
```c
prev_cooked_food = ptr_node->prev_cooked_food;   // prev
next_cooked_food = ptr_node->next_cooked_food;   // next
prev_cooked_food->next_cooked_food = next_cooked_food;  // *(prev+0x28) = next
next_cooked_food->prev_cooked_food = prev_cooked_food;  // *(next+0x30) = prev
```
Logic chuẩn của danh sách vòng-đôi: nối `prev` ↔ `next` để "tháo" `ptr_node` ra. **Không hề kiểm tra** `prev->next == ptr_node` hay `next->prev == ptr_node`. Nếu khống chế được `prev`/`next` của một node giả → đây là **write-what-where** (ghi `next` vào `prev+0x28`, ghi `prev` vào `next+0x30`).

## (L) — Cập nhật đầu danh sách nếu cần
```c
if ( ptr_node == g_foodListHead_205060 ) {
    if ( g_foodListHead_205060 == next_cooked_food )
        g_foodListHead_205060 = 0LL;   // node duy nhất → danh sách rỗng
    else
        g_foodListHead_205060 = next_cooked_food;  // dời head sang node kế
}
```
Chỉ xử lý khi node bị gỡ **chính là head**: nếu đó là node duy nhất (`head == next`) → head = NULL; nếu không → head trỏ sang `next`.

## (M) — Giải phóng & kết thúc
```c
realloc(ptr_node, 0LL);              // = free(ptr_node)
return puts("NPC: Thank you !");
```
`realloc(ptr, 0)` đóng vai trò `free`. Giải phóng node vừa gỡ, in "NPC: Thank you !".

---

## Tóm tắt luồng
Đếm recipe → chọn ngẫu nhiên 1 món NPC đòi → hỏi Yes/No → nếu Yes và đang có món nấu trùng tên thì **thưởng EXP + 434 money + gỡ (unlink) và free** node món đó; mọi trường hợp còn lại in thông báo tương ứng và thoát. Điểm đáng chú ý nhất về bảo mật là khối **(K)** — unlink không kiểm tra tính toàn vẹn (giống hệt `fn_sell_2744` và `fn_eat_2A12`).
