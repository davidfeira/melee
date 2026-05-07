#include "hsd_3B34.h"

#include "hsd_3A94.h"

/// hsd_803B5C2C
static int lbl_804D6398 = 3;

void hsd_803B5C2C(int mode)
{
    lbl_804D6398 = mode;
    if ((mode < 1) || (mode > 10)) {
        lbl_804D6398 = 3;
    }
}

extern u8* hsd_804D79B8;
extern s32 hsd_804D79BC;
extern s32 hsd_804D79C0;
extern s32 hsd_804D79C4;
extern u8 hsd_804D79C8;

extern u8 lbl_80431090[0x5A8];
extern u16 lbl_80431678[0xC];
extern u8 lbl_80431690[0xC];
extern u16 lbl_8043169C[0xC];
extern u8 lbl_804316B4[0xC];

s32 hsd_803B5C4C(s32 arg0)
{
    s32 var_r30;
    s32 var_r29;

    var_r30 = 0;
    var_r29 = arg0;
    do {
        if (hsd_804D79C4 == 0) {
            hsd_804D79C4 = 8;
            if (hsd_804D79B8 >= (u8*) (hsd_804D79BC + hsd_804D79C0)) {
                longjmp((__jmp_buf*) hsd_804D2E70, 1);
            }
            hsd_804D79C8 = *hsd_804D79B8++;
            if (hsd_804D79C8 == 0xFF) {
                if (*hsd_804D79B8 != 0) {
                    longjmp((__jmp_buf*) hsd_804D2E70, 1);
                } else {
                    if (hsd_804D79B8 >= (u8*) (hsd_804D79BC + hsd_804D79C0)) {
                        longjmp((__jmp_buf*) hsd_804D2E70, 1);
                    }
                    hsd_804D79B8++;
                }
            }
        }
        var_r30 <<= 1;
        if (hsd_804D79C8 & (1 << (hsd_804D79C4 - 1))) {
            var_r30 |= 1;
        }
        hsd_804D79C4--;
    } while (--var_r29 != 0);
    return var_r30;
}

u8 hsd_803B5D70(s32 arg0, s32 arg1)
{
    u8* base = lbl_80431090;
    u16* var_r6;
    u8* var_r3;
    u8* var_r27;
    u16* var_r28;
    u8* var_r29;
    s32 var_r31;
    s32 var_r30;
    s32 var_r26;
    u16* var_r4;

    var_r31 = 0;
    var_r30 = 0;
    if (arg0 == 0) {
        var_r6 = (arg1 == 0) ? lbl_80431678 : lbl_8043169C;
        var_r3 = (arg1 == 0) ? lbl_80431690 : lbl_804316B4;
        var_r27 = base + 0x80;
    } else {
        var_r6 = (u16*) (base + ((arg1 == 0) ? 0x8C : 0x3BC));
        var_r3 = base + ((arg1 == 0) ? 0x1D0 : 0x318);
        var_r27 = base + ((arg1 == 0) ? 0x274 : 0x500);
    }
    var_r28 = var_r6;
    var_r29 = var_r3;
    var_r26 = 1;
    do {
        var_r30 = (var_r30 << 1) | hsd_803B5C4C(1);
        var_r4 = var_r28;
        while (var_r26 == (s32) *var_r29) {
            if (var_r30 == (s32) *var_r4) {
                return var_r27[var_r31];
            }
            var_r4++;
            var_r28++;
            var_r31++;
            var_r29++;
        }
        var_r26++;
    } while (var_r26 <= 0x10);
    return 0;
}

extern u8 lbl_80431638[0x40];

void hsd_803B5EA0(s32 arg0)
{
    s32 var_r29;
    s32 var_r3;
    s32 len;
    u32 ctr;
    u8* var_r6;
    s32 bits;
    s32 sym;
    u8* base;

    base = hsd_804D2E70;

    sym = hsd_803B5D70(0, arg0);
    if (sym > 0) {
        var_r3 = hsd_803B5C4C(sym);
        if (!(var_r3 & (1 << (sym - 1)))) {
            var_r3 -= (1 << sym) - 1;
        }
    } else {
        var_r3 = 0;
    }
    *(s32*)(base + arg0 * 4 + 0x818) += var_r3;
    var_r29 = 1;
    *(s32*)(base + 0x718) = *(s32*)(base + arg0 * 4 + 0x818);

    while (var_r29 < 0x40) {
        bits = hsd_803B5D70(1, arg0);
        if (bits == 0) {
            var_r6 = lbl_80431638 + var_r29;
            len = 0x40 - var_r29;
            if (var_r29 < 0x40) {
                ctr = (u32)len >> 3;
                if (ctr != 0) {
                    do {
                        *(s32*)(base + var_r6[0] * 4 + 0x718) = 0;
                        *(s32*)(base + var_r6[1] * 4 + 0x718) = 0;
                        *(s32*)(base + var_r6[2] * 4 + 0x718) = 0;
                        *(s32*)(base + var_r6[3] * 4 + 0x718) = 0;
                        *(s32*)(base + var_r6[4] * 4 + 0x718) = 0;
                        *(s32*)(base + var_r6[5] * 4 + 0x718) = 0;
                        *(s32*)(base + var_r6[6] * 4 + 0x718) = 0;
                        *(s32*)(base + var_r6[7] * 4 + 0x718) = 0;
                        var_r6 += 8;
                        ctr--;
                    } while (ctr != 0);
                    len &= 7;
                    if (len == 0) {
                        goto exit_loop;
                    }
                }
                do {
                    *(s32*)(base + *var_r6++ * 4 + 0x718) = 0;
                    len--;
                } while (len != 0);
            }
            goto exit_loop;
        } else {
            u32 count = (u32)hsd_803B5C4C(bits) - 1;
            ctr = count >> 3;
            if (ctr != 0) {
                do {
                    *(s32*)(base + lbl_80431638[var_r29] * 4 + 0x718) = 0; var_r29++;
                    *(s32*)(base + lbl_80431638[var_r29] * 4 + 0x718) = 0; var_r29++;
                    *(s32*)(base + lbl_80431638[var_r29] * 4 + 0x718) = 0; var_r29++;
                    *(s32*)(base + lbl_80431638[var_r29] * 4 + 0x718) = 0; var_r29++;
                    *(s32*)(base + lbl_80431638[var_r29] * 4 + 0x718) = 0; var_r29++;
                    *(s32*)(base + lbl_80431638[var_r29] * 4 + 0x718) = 0; var_r29++;
                    *(s32*)(base + lbl_80431638[var_r29] * 4 + 0x718) = 0; var_r29++;
                    *(s32*)(base + lbl_80431638[var_r29] * 4 + 0x718) = 0; var_r29++;
                    ctr--;
                } while (ctr != 0);
                count &= 7;
                if (count == 0) {
                    goto done_zeros;
                }
            }
            do {
                *(s32*)(base + lbl_80431638[var_r29] * 4 + 0x718) = 0; var_r29++;
                count--;
            } while (count != 0);
done_zeros:
            sym = hsd_803B5D70(1, arg0);
            var_r3 = hsd_803B5C4C(sym);
            if (!(var_r3 & (1 << (sym - 1)))) {
                var_r3 -= (1 << sym) - 1;
            }
            *(s32*)(base + lbl_80431638[var_r29] * 4 + 0x718) = var_r3;
            var_r29++;
        }
    }
exit_loop:;
}
