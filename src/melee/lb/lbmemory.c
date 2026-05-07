#include "lbmemory.h"

#include <platform.h>

#include <baselib/debug.h>
#include <baselib/devcom.h>

#include <dolphin/os.h>
#include <dolphin/os/OSAlarm.h>

typedef struct DefragJob {
    OSAlarm x0_alarm;
    void* x28_src;
    void* x2C_dest;
    u32 x30_size;
    u32 x34_progress;
    void* x38_args;
    HSD_DevComCallback x3C_callback;
} DefragJob;

typedef struct FreeNode {
    void* x0;
    void* x4;
    void* x8;
} FreeNode;

struct Allocator {
    void* x0_arenaLo;
    void* x4_arenaHi;
    u8 x8[0x62C - 0x8];
    Handle* x62C_free_mem;
    s32 x630_num_allocs;
    s32 x634_max_num_allocs;
    Handle x638_handles[6];
    Handle* x698_free_heap;
    Handle* x69C;
    DefragJob x6A0_job;
    u32 x6E0;
    void* x6E4;
    void* x6E8;
    u8 x6EC[0x6F0 - 0x6EC];
};

/* 015184 */ void fn_80015184(OSAlarm* alarm, OSContext* context);
/* 015320 */ static void lbMemory_80015320(int, Handle*, void*, bool cancelflag);

/// lbMemory_804318B0
static struct Allocator g_alloc;
STATIC_ASSERT(sizeof(g_alloc) == 0x6F0);

/// might need to change to take lvalue instead of pointer if codegen is bad
#define PUSH_HANDLE(list, handle)                                             \
    do {                                                                      \
        handle->x0_next = *list;                                              \
        *list = handle;                                                       \
    } while (0)
#define POP_HANDLE(list, handle)                                              \
    do {                                                                      \
        handle = *list;                                                       \
        *list = handle->x0_next;                                              \
    } while (0)

/// pops handle from freelist and sets the popped regions's bounds
static inline Handle* new_handle(void* arenaLo, void* arenaHi)
{
    Handle* h;
    if (g_alloc.x698_free_heap == NULL) {
        __assert(__FILE__, 0x7BU, "_p(free_heap)");
    }
    // assert_arena_in_bounds(arenaLo, arenaHi);

    if (((u32) arenaLo < 0x80000000U) && ((u32) arenaHi < 0x80000000U)) {
        int ok = 0;
        if (((u32) arenaLo >= (u32) g_alloc.x0_arenaLo) &&
            ((u32) arenaHi <= (u32) g_alloc.x4_arenaHi))
        {
            ok = 1;
        }
        if (ok == 0) {
            __assert(__FILE__, 0x80U,
                     "(u32)arenaLo >= (u32)_p(a_arenaLo) && (u32)arenaHi <= "
                     "(u32)_p(a_arenaHi)");
        }
    }

    POP_HANDLE(&g_alloc.x698_free_heap, h);
    h->x0_next = NULL;
    h->x4_lo = arenaLo;
    h->x8_hi = arenaHi;
    h->xC_prev = NULL;
    return h;
}

Handle* lbMemory_80014E24(void* arenaLo, void* arenaHi)
{
    return new_handle(arenaLo, arenaHi);
}

/// moves a list of handles into x62C
/// then pushes the head to free_heap
/// why does it start at handle->xC_prev?
void lbMemory_80014EEC(Handle* handle)
{
    Handle* iter;
    Handle* tmp_next;
    if (handle == NULL) {
        __assert(__FILE__, 0x95U, "handle");
    }
    for (iter = handle->xC_prev; iter != NULL;) {
        tmp_next = iter->x0_next;
        PUSH_HANDLE(&g_alloc.x62C_free_mem, iter);
        iter = tmp_next;
        g_alloc.x630_num_allocs -= 1;
    }
    PUSH_HANDLE(&g_alloc.x698_free_heap, handle);
}

u32 lbMemory_80014F7C(Handle* h)
{
    u32 r0;
    u32 r4 = (u32) h->x4_lo;
    // this is weird.. i'm missing something
    // &h->xC_prev should be a Handle**,
    // and h->x0_prev looks the same as *h
    Handle* iter = (Handle*) &h->xC_prev;
    u32 sum = 0;

loop:
    iter = iter->x0_next;
    r0 = (u32) ((iter != NULL) ? iter->x4_lo : h->x8_hi);
    sum += r0 - r4;
    if (iter != NULL) {
        r4 = (u32) iter->x4_lo + (u32) iter->x8_hi;
        goto loop;
    }
    return sum;
}

/// malloc
Handle* lbMemory_80014FC8(Handle* arg0, u32 size)
{
    void* lo;
    Handle* memp_candidate;
    void* end;
    u32 least_leftover;
    u32 aligned_size;
    u32 leftover;
    u32 available_space;
    void* start;
    Handle* iter;

    least_leftover = 0x40000000U;
    if (g_alloc.x62C_free_mem == NULL) {
        __assert(__FILE__, 0xCCU, "_p(free_mem)");
    }
    start = arg0->x4_lo;
    // 32 byte alignment
    aligned_size = ((size + 0x1F) & 0xFFFFFFE0);
    iter = (Handle*) &arg0->xC_prev;
    memp_candidate = NULL;

    while (1) {
        // iter = var_r5->x0_next;
        // we look at iter each iteration,
        // until the last iteration, we check arg0
        end = (iter->x0_next != NULL) ? iter->x0_next->x4_lo : arg0->x8_hi;
        available_space = (u32) end - (u32) start;
        if (available_space >= aligned_size) {
            leftover = available_space - aligned_size;
            if (leftover <= least_leftover) {
                least_leftover = leftover;
                lo = start;
                memp_candidate = iter;
            }
        }
        if (iter->x0_next == NULL) {
            break;
        } else {
            iter = iter->x0_next;
            start = (void*) ((u32) iter->x4_lo + (u32) iter->x8_hi);
        }
    }
    if (memp_candidate == NULL) {
        // oom
        __assert(__FILE__, 0xE9U, "memp_kouho");
    }
    {
        Handle* result;
        POP_HANDLE(&g_alloc.x62C_free_mem, result);

        result->x8_hi = (void*) aligned_size;
        result->x4_lo = lo;
        result->x0_next = memp_candidate->x0_next;
        memp_candidate->x0_next = result;

        g_alloc.x630_num_allocs += 1;
        if (g_alloc.x630_num_allocs > g_alloc.x634_max_num_allocs) {
            g_alloc.x634_max_num_allocs = g_alloc.x630_num_allocs;
        }
        return result;
    }
}

void lbMemory_800150F0(Handle* h, void* arg1)
{
    Handle* handle = h->xC_prev;
    Handle* r6 = (Handle*) &h->xC_prev;

    while (handle != NULL) {
        if (handle->x4_lo == arg1) {
            r6->x0_next = handle->x0_next;
            PUSH_HANDLE(&g_alloc.x62C_free_mem, handle);
            g_alloc.x630_num_allocs -= 1;
            return;
        }
        r6 = handle;
        handle = handle->x0_next;
    }
    OSReport("[LbMem] Error: lbMemFreeToHeap %x.\n", arg1);
    __assert("lbmemory.c", 283, "0");
}

static void lbMemory_80015320(int unused, Handle* h, void* args, bool cancelflag)
{
    u32 src;
    u32 dest;
    u32 size;
    DefragJob* job;
    bool enabled;

    dest = (u32) g_alloc.x6E4;
    if (cancelflag) {
        __assert(__FILE__, 0x188, "!cancelflag");
    }
    if (h != NULL) {
        src = (u32) h->x4_lo;
        if (src != dest) {
            h->x4_lo = (void*) dest;
            g_alloc.x6E4 = (void*) ((u32) h->x4_lo + (u32) h->x8_hi);
            if ((u32) h->x4_lo < 0x80000000) {
                HSD_DevComRequest(0, src, dest,
                                  ((u32) h->x8_hi + 0x1F) & ~0x1F, 0x1B, 1,
                                  (HSD_DevComCallback) lbMemory_80015320,
                                  h->x0_next);
            } else {
                size = ((u32) h->x8_hi + 0x1F) & ~0x1F;
                args = h->x0_next;
                job = &g_alloc.x6A0_job;
                enabled = OSDisableInterrupts();
                if (job->x30_size != 0) {
                    __assert(__FILE__, 0x14F, "!p->size");
                }
                job->x28_src = (void*) src;
                job->x2C_dest = (void*) dest;
                job->x30_size = size;
                job->x34_progress = 0;
                job->x38_args = args;
                job->x3C_callback = (HSD_DevComCallback) lbMemory_80015320;
                OSRestoreInterrupts(enabled);
                OSCreateAlarm(&job->x0_alarm);
                OSSetAlarm(&job->x0_alarm, OSMillisecondsToTicks(3),
                           fn_80015184);
            }
        } else {
            g_alloc.x6E4 = (void*) (src + (u32) h->x8_hi);
            lbMemory_80015320(0, h->x0_next, NULL, 0);
        }
    } else {
        ((void (*)(u32)) g_alloc.x6E8)(g_alloc.x6E0);
    }
}

void fn_80015184(OSAlarm* alarm, OSContext* context)
{
    DefragJob* job = &g_alloc.x6A0_job;
    u32 progress;
    u32 chunk;

    if (job->x30_size == 0) {
        __assert(__FILE__, 0x127, "p->size");
    }
    progress = job->x34_progress;
    chunk = job->x30_size - progress;
    if (chunk > 0x19000) {
        chunk = 0x19000;
    }
    memcpy((void*) ((u32) job->x2C_dest + progress),
           (void*) ((u32) job->x28_src + progress), chunk);
    job->x34_progress += chunk;
    if (job->x34_progress == job->x30_size) {
        job->x30_size = 0;
        job->x3C_callback(0, (int) job->x38_args, NULL, 0);
    } else {
        OSCreateAlarm(&job->x0_alarm);
        OSSetAlarm(&job->x0_alarm, OSMillisecondsToTicks(3), fn_80015184);
    }
}

u32 lbMemory_8001529C(Handle* h, void* arg1, u32 arg2)
{
    void* lo;
    Handle* iter;
    void** r7;

    g_alloc.x6E8 = arg1;
    g_alloc.x6E0 = arg2;
    g_alloc.x6E4 = h->x4_lo;

    r7 = &g_alloc.x6E4;

    for (iter = h->xC_prev; iter != NULL; iter = iter->x0_next) {
        lo = iter->x4_lo;
        if (lo != *r7) {
            lbMemory_80015320(0, iter, 0, 0);
            return 1;
        }
        *r7 = (void*) ((u32) lo + (u32) iter->x8_hi);
    }
    return 0;
}

/// getArenaBounds
void lbMemory_800154BC(uintptr_t* arenaLo, uintptr_t* arenaHi)
{
    *arenaLo = (uintptr_t) g_alloc.x0_arenaLo;
    *arenaHi = (uintptr_t) g_alloc.x4_arenaHi;
}

/// same as lbMemory_80014E24, but sets to x69C to the popped handle
Handle* lbMemory_800154D4(void* arenaLo, void* arenaHi)
{
    g_alloc.x69C = new_handle(arenaLo, arenaHi);
    return g_alloc.x69C;
}

void lbMemory_800155A4(void)
{
    Handle* handle = g_alloc.x69C;
    Handle* iter;

    Handle** r5;

    HSD_ASSERT(149, handle);
    r5 = &g_alloc.x62C_free_mem;
    for (iter = handle->xC_prev; iter != NULL;) {
        Handle* tmp_next = iter->x0_next;
        PUSH_HANDLE(r5, iter);
        iter = tmp_next;
        g_alloc.x630_num_allocs -= 1;
    }
    PUSH_HANDLE(&g_alloc.x698_free_heap, handle);
    g_alloc.x69C = NULL;
}

void lbMemory_8001564C(void)
{
    FreeNode* nodes = (FreeNode*)&g_alloc;
    u32 sp14;
    s32 i;
    FreeNode* p;

    g_alloc.x0_arenaLo = (void*)ARAlloc(0x20U);
    ARFree(&sp14);
    g_alloc.x4_arenaHi =
        (ARGetSize() <= 0x01000000U) ? (void*)ARGetSize() : (void*)0x01000000U;

    g_alloc.x62C_free_mem = (Handle*)&nodes[0].x8;

    i = 0;
    p = nodes;
    do {
        p[0].x8 = &nodes[i + 1].x8;
        p[1].x8 = &nodes[i + 2].x8;
        p[2].x8 = &nodes[i + 3].x8;
        p[3].x8 = &nodes[i + 4].x8;
        p[4].x8 = &nodes[i + 5].x8;
        p[5].x8 = &nodes[i + 6].x8;
        p[6].x8 = &nodes[i + 7].x8;
        p[7].x8 = &nodes[i + 8].x8;
        p[8].x8 = &nodes[i + 9].x8;
        p[9].x8 = &nodes[i + 10].x8;
        p[10].x8 = &nodes[i + 11].x8;
        p[11].x8 = &nodes[i + 12].x8;
        p[12].x8 = &nodes[i + 13].x8;
        p[13].x8 = &nodes[i + 14].x8;
        p[14].x8 = &nodes[i + 15].x8;
        p[15].x8 = &nodes[i + 16].x8;
        p += 16;
        i += 16;
    } while (i < 0x80);

    for (; i < 0x82; i++, p++) {
        p->x8 = &nodes[i + 1].x8;
    }
    nodes[i].x8 = NULL;

    g_alloc.x634_max_num_allocs = 0;
    g_alloc.x630_num_allocs = 0;
    g_alloc.x698_free_heap = &g_alloc.x638_handles[0];
    g_alloc.x638_handles[0].x0_next = &g_alloc.x638_handles[1];
    g_alloc.x638_handles[1].x0_next = &g_alloc.x638_handles[2];
    g_alloc.x638_handles[2].x0_next = &g_alloc.x638_handles[3];
    g_alloc.x638_handles[3].x0_next = &g_alloc.x638_handles[4];
    g_alloc.x638_handles[4].x0_next = &g_alloc.x638_handles[5];
    g_alloc.x638_handles[5].x0_next = NULL;
    g_alloc.x69C = NULL;

    g_alloc.x69C = lbMemory_80014E24(g_alloc.x0_arenaLo, g_alloc.x4_arenaHi);
    g_alloc.x6A0_job.x30_size = 0;
}
