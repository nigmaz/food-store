Có thể hiểu/dịch các struct này sang tiếng Việt như sau:

### 1. `Ingredient` — **Nguyên liệu**

```c
struct Ingredient // Kích thước: 0x28 = 40 bytes
{
    char name[32];       // Tên nguyên liệu
    uint32_t price;      // Giá nguyên liệu
    uint32_t quantity;   // Số lượng
};
```

| Offset | Trường     | Tiếng Việt      |            Kích thước |
| ------ | ---------- | --------------- | --------------------: |
| `0x00` | `name[32]` | Tên nguyên liệu |              32 bytes |
| `0x20` | `price`    | Giá             |               4 bytes |
| `0x24` | `quantity` | Số lượng        |               4 bytes |
|        | **Tổng**   |                 | **40 bytes (`0x28`)** |

### 2. `Recipe` — **Công thức món ăn**

```c
struct Recipe // Kích thước: 0x88 = 136 bytes
{
    char title[24];                  // Tên / tiêu đề công thức
    Ingredient *ingredients[13];     // Danh sách 13 con trỏ tới nguyên liệu
    struct Recipe *next_recipe;      // Công thức tiếp theo
};
```

| Offset | Trường            | Tiếng Việt                      |             Kích thước |
| ------ | ----------------- | ------------------------------- | ---------------------: |
| `0x00` | `title[24]`       | Tên công thức / tên món         |               24 bytes |
| `0x18` | `ingredients[13]` | Mảng 13 con trỏ nguyên liệu     |              104 bytes |
| `0x80` | `next_recipe`     | Con trỏ tới công thức tiếp theo |                8 bytes |
|        | **Tổng**          |                                 | **136 bytes (`0x88`)** |

`ingredients` là **mảng con trỏ**, không chứa trực tiếp 13 struct `Ingredient`:

```text
Recipe
 ├─ title
 ├─ ingredients[0] ──> Ingredient
 ├─ ingredients[1] ──> Ingredient
 ├─ ...
 ├─ ingredients[12] ─> Ingredient
 └─ next_recipe ─────> Recipe tiếp theo
```

### 3. `CookedFood` — **Món ăn đã nấu / thành phẩm**

```c
struct CookedFood // Kích thước: 0x38 = 56 bytes
{
    char name[24];                       // Tên món ăn
    uint32_t sell_price;                 // Giá bán
    uint32_t padding;                    // Phần đệm căn chỉnh
    uint64_t energy_value;               // Giá trị năng lượng
    struct CookedFood *next_cooked_food; // Món tiếp theo
    struct CookedFood *prev_cooked_food; // Món trước đó
};
```

| Offset | Trường             | Tiếng Việt                |            Kích thước |
| ------ | ------------------ | ------------------------- | --------------------: |
| `0x00` | `name[24]`         | Tên món ăn                |              24 bytes |
| `0x18` | `sell_price`       | Giá bán                   |               4 bytes |
| `0x1C` | `padding`          | Padding / vùng đệm        |               4 bytes |
| `0x20` | `energy_value`     | Giá trị năng lượng        |               8 bytes |
| `0x28` | `next_cooked_food` | Con trỏ tới món tiếp theo |               8 bytes |
| `0x30` | `prev_cooked_food` | Con trỏ tới món trước đó  |               8 bytes |
|        | **Tổng**           |                           | **56 bytes (`0x38`)** |

Nhìn về mặt cấu trúc dữ liệu thì `Recipe` là **linked list một chiều** thông qua `next_recipe`, còn `CookedFood` là **doubly linked list (danh sách liên kết kép)** vì có cả `next_cooked_food` và `prev_cooked_food`.
