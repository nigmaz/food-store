cd /mnt/c/Users/ha/Downloads/pwn
gdb -q -batch \
  -ex 'set pagination off' \
  -ex 'run' \
  -ex 'echo \n==== SIGSEGV ====\n' \
  -ex 'info registers rip rdi rsi rax rbx' \
  -ex 'bt' \
  -ex 'x/4i $pc' \
  --args ./ld-2.24.so --library-path . ./food_store_god < in.txt 2>&1 | tail -40
