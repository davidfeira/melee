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
