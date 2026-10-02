#!/usr/bin/env python3
import sys
from pwn import *

elf = ELF("./food_store_patched")
ld = ELF("./ld-2.24.so")
libc = ELF("./libc.so.6")
ROP_LOAD = ROP("./libc.so.6")
context.update(binary=elf, log_level="DEBUG")
flag_path = b"/home/food_store/flag\x00"

if args.LOCAL:
    p = elf.process()
elif args.GDB:
    # context.terminal = ["tmux", "splitw", "-f", "-h"]
    p = gdb.debug(
        [elf.path],
        gdbscript="""
            # ===== MAIN MENU (main @ 0x31C5) =====
            breakrva 0x324C
            breakrva 0x3258
            breakrva 0x3264
            breakrva 0x3270
            breakrva 0x327C
            breakrva 0x3288
            breakrva 0x328F

            # ===== RECIPE submenu (fn_recipe_1CA9 @ 0x1CA9) =====
            breakrva 0x1D0D
            breakrva 0x1D32
            breakrva 0x1D3E

            # ===== SHOP submenu (fn_shop_30E3 @ 0x30E3) =====
            breakrva 0x312E
            breakrva 0x313A
            breakrva 0x3151
        """
        # =========================================================
        # MAIN MENU  (main @ 0x31C5 — jump table switch 8 cases)
        # 1. Recipe              | breakrva 0x324C  (call fn_recipe_1CA9)
        # 2. Assignment          | breakrva 0x3258  (call fn_assignment_2B62)
        # 3. Chef's information  | breakrva 0x3264  (call fn_chef_info_1D5A)
        # 4. Shop                | breakrva 0x3270  (call fn_shop_30E3)
        # 5. Cook                | breakrva 0x327C  (call fn_cook_2259)
        # 6. Eat                 | breakrva 0x3288  (call fn_eat_2A12)
        # 7. Exit                | breakrva 0x328F  (case 7; fclose@0x32A5, _exit@0x32AF)
        #     - đọc lựa chọn menu chính | breakrva 0x320E (call fn_read_number_1134)
        # ---------------------------------------------------------
        # RECIPE submenu  (fn_recipe_1CA9 @ 0x1CA9)
        # 1. Add new recipe      | breakrva 0x1D0D  (call fn_add_new_recipe_17DC)   [gate level>1]
        # 2. Remove recipe       | breakrva 0x1D32  (call fn_remove_recipe_1B90)    [gate level>2]
        # 3. Show recipe         | breakrva 0x1D3E  (call fn_show_recipe_1A9B)
        # 4. Return              | breakrva 0x1CE7  (cmp rax,4 ; jz loc_1D57)
        #     - đọc lựa chọn submenu | breakrva 0x1CC0 (call fn_read_number_1134)
        # ---------------------------------------------------------
        # SHOP submenu  (fn_shop_30E3 @ 0x30E3)
        # 1. Buy                 | breakrva 0x312E  (call fn_buy_2F40)
        # 2. Sell                | breakrva 0x313A  (call fn_sell_2744)
        # 3. Make                | breakrva 0x3151  (call fn_make_2895)             [gate level>3]
        # 4. Return              | breakrva 0x3121  (cmp rax,4 ; jz loc_3169)
        #     - đọc lựa chọn submenu | breakrva 0x30FA (call fn_read_number_1134)
        # =========================================================
    )
else:
    p = remote("chall.pwnable.tw", "10406")


# Prompt chung của 3 menu (main / recipe / shop) đều là "Your choice: "
CHOICE = b"Your choice: "

# =============================================================================
# Khởi tạo
# =============================================================================
def set_name(name):
    """fn_player_init_profile_316C: đọc tối đa 7 byte. Level=1, Power=20, Money=100."""
    p.sendlineafter(b"Your name: ", name)
    return

# =============================================================================
# MENU CHÍNH (main @ 0x31C5)
#   1. Recipe   2. Assignment   3. Chef's info   4. Shop   5. Cook   6. Eat   7. Exit
# =============================================================================
def recipe_menu():
    """Vào submenu Recipe (main choice 1). Sau đó dùng add_recipe/remove_recipe/show_recipe"""
    p.sendlineafter(CHOICE, b"1")
    return

def assignment(accept=True):
    """NPC đòi 1 món ngẫu nhiên. Trả về tên món NPC muốn (bytes).
    Nếu accept=True và bạn đang có CookedFood trùng tên -> +80 exp, +434 money, free node."""
    p.sendlineafter(CHOICE, b"2")
    # "NPC: I want to eat <title> \nCan you prepare it for me ? \n"
    line = p.recvuntil(b"Can you prepare", drop=True)
    want = line.split(b"I want to eat ", 1)[1].strip() if b"I want to eat " in line else b""
    p.sendlineafter(b"(1/Yes,0/No) :", b"1" if accept else b"0")
    return want

p.interactive()

# # ===== Unlink write-what-where (không kiểm tra) =====
# # sell_2744:
# breakrva 0x2800   # *(prev+0x28) = next   (GHI #1)
# breakrva 0x280C   # *(next+0x30) = prev   (GHI #2)
# breakrva 0x281C   # realloc(node, 0)  -> free
# # eat_2A12:
# breakrva 0x2ACD   # *(prev+0x28) = next
# breakrva 0x2AD9   # *(next+0x30) = prev
# breakrva 0x2AE9   # free
# # assignment_2B62:
# breakrva 0x2D19   # *(prev+0x28) = next
# breakrva 0x2D25   # *(next+0x30) = prev
# breakrva 0x2D67   # free
# # ===== Magic leak (add_recipe) =====
# breakrva 0x1927   # call __printf_chk  -> RDX = chuỗi hex (addr_chunk XOR key)
