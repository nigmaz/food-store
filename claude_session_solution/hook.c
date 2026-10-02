#define _GNU_SOURCE
#include <stddef.h>
#include <unistd.h>
#include <sys/syscall.h>
extern void* __libc_malloc(size_t);
extern void  __libc_free(void*);
extern void* __libc_realloc(void*,size_t);
static void w(const char*s,int n){ syscall(SYS_write,2,s,n); }
static void hex(unsigned long v){ char b[19]="0x"; const char*d="0123456789abcdef";
  int i; for(i=0;i<16;i++) b[2+i]=d[(v>>((15-i)*4))&0xf]; w(b,18); }
static void dec(unsigned long v){ char b[24]; int i=24; if(!v){w("0",1);return;}
  while(v){b[--i]="0123456789"[v%10];v/=10;} w(b+i,24-i); }
void* malloc(size_t n){ void*p=__libc_malloc(n);
  w("[H] malloc(",11); hex(n); w(") = ",4); hex((unsigned long)p); w("\n",1); return p; }
void free(void*p){ w("[H] free(",9); hex((unsigned long)p); w(")\n",2); __libc_free(p); }
void* realloc(void*p,size_t n){ void*q=__libc_realloc(p,n);
  w("[H] realloc(",12); hex((unsigned long)p); w(",",1); hex(n); w(") = ",4); hex((unsigned long)q); w("\n",1); return q; }
