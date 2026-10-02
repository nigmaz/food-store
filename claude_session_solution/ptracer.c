#include <sys/prctl.h>
#ifndef PR_SET_PTRACER
#define PR_SET_PTRACER 0x59616d61
#endif
__attribute__((constructor)) static void a(){ prctl(PR_SET_PTRACER, -1, 0,0,0); }
