#include "mnstagesw.h"

#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/gobjgxlink.h>
#include <sysdolphin/baselib/gobjobject.h>
#include <sysdolphin/baselib/gobjplink.h>
#include <sysdolphin/baselib/gobjproc.h>
#include <sysdolphin/baselib/gobjuserdata.h>
#include <sysdolphin/baselib/jobj.h>
#include <sysdolphin/baselib/memory.h>
#include <sysdolphin/baselib/sislib.h>
#include <melee/gm/gm_1601.h>
#include <melee/gm/gm_1A3F.h>
#include <melee/gm/gmmain_lib.h>
#include <melee/lb/lb_00B0.h>
#include <melee/lb/lb_00F9.h>
#include <melee/lb/lbaudio_ax.h>
#include <melee/lb/lbcardgame.h>
#include <melee/mn/mnmain.h>
#include <melee/mn/mnruleplus.h>
#include <melee/sc/types.h>

#define NUM_STAGES 29

/// Extended user-data layout for the stage switch GObj.
/// Allocated at 0xB4 bytes via HSD_MemAlloc.
typedef struct {
    u8 cur_menu;        ///< 0x00: snapshot of mn_804A04F0.cur_menu
    u8 stage_idx;       ///< 0x01: current hovered stage index
    u8 confirmed[29];   ///< 0x02..0x1E: per-stage confirmed flags
    u8 state;           ///< 0x1F: animation state machine
    HSD_JObj* jobjs[6]; ///< 0x20..0x37: six JObj references
    u32 unk38[2];       ///< 0x38..0x3F: unknown padding
    HSD_Text* texts[29];///< 0x40..0xB3: text object array
} MnStageSw_Data;

/// Stage switch positioning data (15 floats)
static float mnStageSw_803ED488[15] = {
    0.0f, 199.0f, 0.0f, 0.0f, 9.0f,
    -0.1f, 0.0f, 0.0f, -0.1f, 0.0f,
    0.0f, -0.1f, 0.0f, 0.0f, -0.1f,
};

/// Confirmation toggle anim frames (off, on)
static f32 mnStageSw_804D4BB8[2] = { 0.0f, 1.0f };

/// Stage switch toggle indices - maps menu position to internal stage ID
static u8 mnStageSw_803ED4C4[NUM_STAGES] = {
    0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09,
    0x0B, 0x0A, 0x18, 0x1A, 0x1C, 0x0C, 0x0D, 0x0E, 0x0F, 0x10,
    0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x19, 0x1B,
};

/// Stage switch icon indices
static u8 mnStageSw_stageIcons[NUM_STAGES] = {
    0x08, 0x09, 0x11, 0x0A, 0x0C, 0x06, 0x0B, 0x07, 0x0E, 0x0D,
    0x1D, 0x17, 0x0F, 0x10, 0x12, 0x13, 0x14, 0x15, 0x1A, 0x1B,
    0x1C, 0x16, 0x18, 0x1F, 0x20, 0x21, 0x22, 0x23, 0x24,
};

static HSD_GObj* mnStageSw_804D6BF0;
static s8 mnStageSw_804D6BF4;

/* 23593C */ static void mnStageSw_8023593C(HSD_GObj* gobj);
/* 2359C8 */ static void mnStageSw_802359C8(HSD_GObj* gobj);
/* 235C58 */ static s32 mnStageSw_80235C58(u8 arg0);
/* 235DC8 */ static void mnStageSw_80235DC8(u8* user_data, s32 buttons);
/* 235F80 */ static void fn_80235F80(HSD_GObj* gobj);
/* 236178 */ static void mnStageSw_80236178(HSD_GObj* gobj, u8 idx);
/* 2364A0 */ static HSD_JObj* mnStageSw_802364A0(HSD_GObj* gobj, u8 idx);
/* 236548 */ static void mnStageSw_80236548(HSD_GObj* gobj, u8 arg1, u8 arg2);
/* 236998 */ static void fn_80236998(HSD_GObj* gobj);
/* 236CBC */ static HSD_GObj* mnStageSw_80236CBC(s8 arg0);

/// Sync stage toggle states from user data to unlock system.
/// For each stage, if it's unlocked, set its enable state from user_data[i+2].
/// Stack padding required to match original frame size.
/// Pragma prevents inlining - function is called from fn_80235F80, not
/// inlined.
#pragma dont_inline on
static void mnStageSw_8023593C(HSD_GObj* gobj)
{
    u8* arr = mnStageSw_803ED4C4;
    u8* ptr = arr;
    s32 i = 0;
    u8* user_data = gobj->user_data;
    u8* p;
    u8 pad[8];
    (void) pad;

    do {
        p = arr + (u8) i;
        if (gm_80164430(gm_801641CC(*p)) != 0) {
            gm_801641E4(*ptr, user_data[i + 2]);
        }
        i++;
        ptr++;
    } while (i < NUM_STAGES);
}
#pragma dont_inline reset

/// Initialize HSD_Text objects for stage labels on the stage switch screen.
/// Creates text objects for each stage column using JObj translation data
/// to position them, and sets the icon index based on unlock status.
static void mnStageSw_802359C8(HSD_GObj* gobj)
{
    extern u8 mn_804D6BB5;
    s32* ptr;
    HSD_Text* text;
    f32 base_y;
    f32 ref_y;
    f32 spacing;
    u8* icon_ptr;
    u8* icon_ptr2;
    s32 i;

    base_y = -1.6f + HSD_JObjGetTranslationY((HSD_JObj*) gobj->user_data);
    ref_y = HSD_JObjGetTranslationY((HSD_JObj*) gobj->user_data);
    spacing = HSD_JObjGetTranslationY((HSD_JObj*) gobj->user_data_remove_func) - ref_y;

    ptr = (s32*) gobj;
    icon_ptr = mnStageSw_803ED4C4;
    i = 0;
    do {
        text = HSD_SisLib_803A5ACC(0, (s32) mn_804D6BB5,
                                   1.0f + HSD_JObjGetTranslationX((HSD_JObj*) gobj->user_data),
                                   -((spacing * (f32) i) + base_y),
                                   17.5f, 160.0f, 300.0f);
        ptr[0x10] = (s32) text;
        text->font_size.x = 0.0521f;
        text->font_size.y = 0.0521f;
        text->default_alignment = 2;
        text->default_fitting = 1;
        if (gm_80164430(gm_801641CC(mnStageSw_803ED4C4[(u8) i])) != 0) {
            HSD_SisLib_803A6368(text, (s32) mnStageSw_stageIcons[*icon_ptr]);
        } else {
            HSD_SisLib_803A6368(text, 0x25);
        }
        i++;
        ptr++;
        icon_ptr++;
    } while (i < 0xF);

    ptr = (s32*) gobj + 0xF;
    icon_ptr2 = &mnStageSw_803ED4C4[15];
    i = 0xF;
    do {
        text = HSD_SisLib_803A5ACC(0, (s32) mn_804D6BB5,
                                   1.0f + HSD_JObjGetTranslationX((HSD_JObj*) gobj->x34_unk),
                                   -((spacing * (f32) (i - 0xF)) + base_y),
                                   17.5f, 160.0f, 300.0f);
        ptr[0x10] = (s32) text;
        text->font_size.x = 0.0521f;
        text->font_size.y = 0.0521f;
        text->default_alignment = 2;
        text->default_fitting = 1;
        if (gm_80164430(gm_801641CC(mnStageSw_803ED4C4[(u8) i])) != 0) {
            HSD_SisLib_803A6368(text, (s32) mnStageSw_stageIcons[*icon_ptr2]);
        } else {
            HSD_SisLib_803A6368(text, 0x25);
        }
        i++;
        ptr++;
        icon_ptr2++;
    } while ((s32) i < 0x1D);
}

/// Find the nearest unlocked stage to arg0 within its block.
/// Block is [0, 14] if arg0 < 15, else [15, 28].
/// Returns -1 if no stage in the block is unlocked.
/// Otherwise returns arg0 if unlocked, else searches outward by distance.
static s32 mnStageSw_80235C58(u8 arg0)
{
    s32 i;
    u8 block_start;
    u8 block_end;
    s32 j;
    s32 lo;
    s32 hi;
    s32 none_unlocked;
    s32 down;
    s32 up;

    if (arg0 < 15) {
        block_start = 0;
        block_end = 14;
    } else {
        block_start = 15;
        block_end = 28;
    }

    if (arg0 < 15) {
        j = 0;
        hi = 14;
    } else {
        j = 15;
        hi = 28;
    }
    lo = j;
    (void) lo;

    while ((s32) j <= (s32) hi) {
        if (gm_80164430(gm_801641CC(mnStageSw_803ED4C4[(u8) j])) != 0) {
            none_unlocked = 0;
            goto check_self;
        }
        j++;
    }
    none_unlocked = 1;

check_self:
    if (none_unlocked != 0) {
        return -1;
    }

    if ((u8) arg0 < 29 &&
        gm_80164430(gm_801641CC(mnStageSw_803ED4C4[(u8) arg0])) != 0)
    {
        return (u8) arg0;
    }

    up = (u8) arg0 + 1;
    i = 1;
    while (true) {
        down = (u8) arg0 - i;
        if ((s32) (u8) block_start <= down &&
            gm_80164430(gm_801641CC(mnStageSw_803ED4C4[(u8) down])) != 0)
        {
            return down;
        }
        if (up <= (s32) (u8) block_end &&
            gm_80164430(gm_801641CC(mnStageSw_803ED4C4[(u8) ((u8) arg0 + i)])) != 0)
        {
            return (u8) arg0 + i;
        }
        up++;
        i++;
    }
}

/// Handle d-pad input on the stage switch screen.
static void mnStageSw_80235DC8(u8* user_data, s32 buttons)
{
    u8 hov = (u8) mn_804A04F0.hovered_selection;
    u8* arr;
    s32 ret;
    s32 lo;
    s32 hi;

    if (buttons & 1) {
        arr = mnStageSw_803ED4C4;
        lo = 0xE;
        hi = 0x1C;
        do {
            switch ((s32) hov) {
            case 0xF:
                mn_804A04F0.hovered_selection = (u16) hi;
                break;
            case 0:
                mn_804A04F0.hovered_selection = (u16) lo;
                break;
            default:
                mn_804A04F0.hovered_selection = (u16) (hov - 1);
                break;
            }
            hov = (u8) mn_804A04F0.hovered_selection;
        } while (gm_80164430(gm_801641CC(arr[hov])) == 0);
        mn_804A04F0.confirmed_selection = user_data[hov + 2];
    } else if (buttons & 2) {
        arr = mnStageSw_803ED4C4;
        lo = 0;
        hi = 0xF;
        do {
            switch ((s32) hov) {
            case 0xE:
                mn_804A04F0.hovered_selection = (u16) lo;
                break;
            case 0x1C:
                mn_804A04F0.hovered_selection = (u16) hi;
                break;
            default:
                mn_804A04F0.hovered_selection = (u16) (hov + 1);
                break;
            }
            hov = (u8) mn_804A04F0.hovered_selection;
        } while (gm_80164430(gm_801641CC(arr[hov])) == 0);
        mn_804A04F0.confirmed_selection = user_data[hov + 2];
    } else if (buttons & 4) {
        if (hov >= 0xF && hov < 0x1D) {
            ret = mnStageSw_80235C58(hov - 0xF);
            if (ret != -1) {
                mn_804A04F0.hovered_selection = (u8) ret;
                mn_804A04F0.confirmed_selection = user_data[(u8) ret + 2];
            }
        }
    } else if (buttons & 8) {
        if (hov < 0xF) {
            ret = mnStageSw_80235C58(hov + 0xF);
            if (ret != -1) {
                mn_804A04F0.hovered_selection = (u8) ret;
                mn_804A04F0.confirmed_selection = user_data[(u8) ret + 2];
            }
        }
    }
}

static void fn_80235F80(HSD_GObj* gobj)
{
    u8* user_data = mnStageSw_804D6BF0->user_data;
    u32 buttons;
    s32 count;
    s32 ctr;
    s32 idx;
    s32 cond;
    u8 pad[40];
    (void) pad;

    buttons = mn_804A04F0.buttons = mn_80229624(4);
    count = 0;

    if (buttons & 0x20) {
        lbAudioAx_80024030(0);
        mn_804A04F0.entering_menu = 0;
        mnStageSw_8023593C(mnStageSw_804D6BF0);
        lb_8001CE00();
        mn_804D6BC8.cooldown = 5;
        mn_802339FC();
        HSD_GObjPLink_80390228(gobj);
        return;
    }
    if (mnStageSw_804D6BF4 == 0) {
        if (buttons & 0x200) {
            if (mn_804A04F0.hovered_selection < 0x1D) {
                if (mn_804A04F0.confirmed_selection != 0) {
                    u8* ud2 = mnStageSw_804D6BF0->user_data;
                    ctr = 0x1D;
                    idx = 0;
                    do {
                        if (ud2[idx + 2] != 0) {
                            count++;
                        }
                        idx++;
                        ctr--;
                    } while (ctr != 0);
                    if (count > 1) {
                        cond = 0;
                    } else {
                        cond = 1;
                    }
                    if (cond != 0) {
                        lbAudioAx_80024030(3);
                    } else {
                        lbAudioAx_80024030(2);
                        mn_804A04F0.confirmed_selection = 0;
                    }
                } else {
                    lbAudioAx_80024030(2);
                    mn_804A04F0.confirmed_selection = 1;
                }
                {
                    u8* arr2 = mnStageSw_803ED4C4;
                    u8* ptr = arr2;
                    s32 j = 0;
                    u8* ud3 = mnStageSw_804D6BF0->user_data;
                    u8* p;
                    do {
                        p = arr2 + (u8) j;
                        if (gm_80164430(gm_801641CC(*p)) != 0) {
                            gm_801641E4(*ptr, ud3[j + 2]);
                        }
                        j++;
                        ptr++;
                    } while (j < NUM_STAGES);
                }
                return;
            }
        } else if (buttons & 0x100) {
            lbAudioAx_80024030(1);
            if ((s32) gm_801A4310() == 1) {
                mnStageSw_8023593C(mnStageSw_804D6BF0);
                lb_8001CE00();
                mn_80229860(2);
                return;
            }
            mnStageSw_8023593C(mnStageSw_804D6BF0);
            lb_8001CE00();
            mn_8022F4CC();
            return;
        }
        if (buttons & 0xF) {
            lbAudioAx_80024030(2);
            mnStageSw_80235DC8(user_data, buttons);
        }
    }
}

/// Position stage icon JObj based on index
/// Uses stored reference JObjs to calculate X/Y position
static void mnStageSw_80236178(HSD_GObj* gobj, u8 idx)
{
    HSD_JObj* jobj;
    HSD_JObj* ref_jobj;
    f32 delta;

    jobj = GET_JOBJ(gobj);
    HSD_JObjClearFlagsAll(jobj, JOBJ_HIDDEN);

    delta = HSD_JObjGetTranslationY((HSD_JObj*) gobj->user_data_remove_func) -
            HSD_JObjGetTranslationY((HSD_JObj*) gobj->user_data);

    if ((u8) idx < 15) {
        ref_jobj = (HSD_JObj*) gobj->user_data;
        HSD_JObjSetTranslateX(jobj, HSD_JObjGetTranslationX(ref_jobj));
        HSD_JObjSetTranslateY(
            jobj, delta * (f32) (u8) idx +
                      HSD_JObjGetTranslationY((HSD_JObj*) gobj->user_data));
    } else {
        ref_jobj = (HSD_JObj*) gobj->x34_unk;
        HSD_JObjSetTranslateX(jobj, HSD_JObjGetTranslationX(ref_jobj));
        HSD_JObjSetTranslateY(
            jobj, delta * (f32) ((u8) idx - 15) +
                      HSD_JObjGetTranslationY((HSD_JObj*) gobj->user_data));
    }
}

/// Get JObj for stage icon at given index
/// Navigates JObj tree stored in gobj->user_data (idx < 15) or gobj->x34_unk
/// (idx >= 15)
#pragma dont_inline on
static HSD_JObj* mnStageSw_802364A0(HSD_GObj* gobj, u8 idx)
{
    HSD_JObj* jobj;
    u8 i;

    if (idx >= 15) {
        jobj = HSD_JObjGetChild(gobj->x34_unk);
        for (i = 15; i < idx; i++) {
            jobj = HSD_JObjGetNext(jobj);
        }
        return jobj;
    }
    jobj = HSD_JObjGetChild(gobj->user_data);
    for (i = 0; i < idx; i++) {
        jobj = HSD_JObjGetNext(jobj);
    }
    return jobj;
}
#pragma dont_inline reset

/// Update stage switch menu state on selection changes
/// arg1: selection changed (refresh icons + highlight position + start anim)
/// arg2: confirmation toggled (request stage on/off anim)
static void mnStageSw_80236548(HSD_GObj* gobj, u8 arg1, u8 arg2)
{
    HSD_GObj* inner = (HSD_GObj*) gobj->user_data;
    HSD_JObj* sp44;
    HSD_JObj* sp3C;
    HSD_JObj* highlight;
    f32 frame;
    f32 delta;
    u8 hov;
    u16 idx;

    if (arg1 != 0) {
        lb_80011E24(mnStageSw_802364A0(inner, ((u8*) inner)[1]), &sp44, 3,
                    -1);
        HSD_JObjSetFlagsAll(sp44, JOBJ_HIDDEN);
        frame = mn_8022F298(sp44);

        hov = (u8) mn_804A04F0.hovered_selection;
        lb_80011E24(mnStageSw_802364A0(inner, hov), &sp44, 3, -1);
        HSD_JObjClearFlagsAll(sp44, JOBJ_HIDDEN);
        HSD_JObjReqAnimAll(sp44, frame);
        HSD_JObjAnimAll(sp44);

        highlight = (HSD_JObj*) inner->hsd_obj;
        HSD_JObjClearFlagsAll(highlight, JOBJ_HIDDEN);

        delta = HSD_JObjGetTranslationY(
                    (HSD_JObj*) inner->user_data_remove_func) -
                HSD_JObjGetTranslationY((HSD_JObj*) inner->user_data);

        if (hov < 15) {
            HSD_JObjSetTranslateX(
                highlight,
                HSD_JObjGetTranslationX((HSD_JObj*) inner->user_data));
            HSD_JObjSetTranslateY(
                highlight,
                delta * (f32) hov +
                    HSD_JObjGetTranslationY((HSD_JObj*) inner->user_data));
        } else {
            HSD_JObjSetTranslateX(
                highlight,
                HSD_JObjGetTranslationX((HSD_JObj*) inner->x34_unk));
            HSD_JObjSetTranslateY(
                highlight,
                delta * (f32) (hov - 15) +
                    HSD_JObjGetTranslationY((HSD_JObj*) inner->user_data));
        }
    }

    if (arg2 != 0) {
        u8 confirmed = mn_804A04F0.confirmed_selection;
        lb_80011E24(mnStageSw_802364A0(
                        inner, (u8) mn_804A04F0.hovered_selection),
                    &sp3C, 2, -1);
        HSD_JObjReqAnimAll(sp3C, mnStageSw_804D4BB8[confirmed]);
        HSD_JObjAnimAll(sp3C);
    }

    if (arg1 != 0) {
        idx = mn_804A04F0.hovered_selection;
    } else {
        idx = (u16) ((u8*) inner)[1];
    }
    lb_80011E24(mnStageSw_802364A0(inner, (u8) idx), &sp44, 3, -1);
    mn_8022ED6C(sp44, (AnimLoopSettings*) mnStageSw_803ED488);
}

/// Update stage switch transition animation and state machine.
/// Drives enter/exit animations, text cleanup, and hover/confirm tracking.
static void fn_80236998(HSD_GObj* gobj)
{
    HSD_GObj* inner;
    f32* anim;
    s32 var_r29;
    s32 var_r28;
    s32 var_r27;
    HSD_JObj* jobj;
    u8 state;

    var_r29 = 0;
    var_r28 = 0;
    var_r27 = 0;
    inner = (HSD_GObj*) gobj->user_data;
    state = ((MnStageSw_Data*) inner)->state;
    if (state == 0 || state == 1 || state == 3) {
        if (((MnStageSw_Data*) inner)->cur_menu != (u8) mn_804A04F0.cur_menu) {
            if ((u8) mn_804A04F0.entering_menu != 0) {
                ((MnStageSw_Data*) inner)->state = 4;
            } else {
                ((MnStageSw_Data*) inner)->state = 2;
            }
            state = ((MnStageSw_Data*) inner)->state;
            switch ((s32) state) {
            case 1:
                anim = &mnStageSw_803ED488[3];
                break;
            case 2:
                anim = &mnStageSw_803ED488[9];
                break;
            case 3:
                anim = &mnStageSw_803ED488[6];
                break;
            case 4:
                anim = &mnStageSw_803ED488[12];
                break;
            }
            jobj = ((MnStageSw_Data*) inner)->jobjs[1];
            HSD_JObjReqAnim(jobj, anim[0]);
            HSD_JObjAnim(jobj);
            state = ((MnStageSw_Data*) inner)->state;
            if (state == 0 || state == 1 || state == 3) {
                var_r29 = 1;
                var_r28 = 1;
                var_r27 = 1;
            }
        }
    }

    state = ((MnStageSw_Data*) inner)->state;
    if (state != 0) {
        jobj = ((MnStageSw_Data*) inner)->jobjs[1];
        switch ((s32) state) {
        case 1:
            anim = &mnStageSw_803ED488[3];
            break;
        case 2:
            anim = &mnStageSw_803ED488[9];
            break;
        case 3:
            anim = &mnStageSw_803ED488[6];
            break;
        case 4:
            anim = &mnStageSw_803ED488[12];
            break;
        }
        if (mn_8022F298(jobj) >= anim[1]) {
            state = ((MnStageSw_Data*) inner)->state;
            switch ((s32) state) {
            case 3:
            case 1: {
                s32 i = 0;
                ((MnStageSw_Data*) inner)->state = (u8) i;
                mnStageSw_802359C8(inner);
                gobj = (HSD_GObj*) gobj->user_data;
                HSD_JObjClearFlagsAll(
                    (HSD_JObj*) gobj->user_data, 0x10);
                HSD_JObjClearFlagsAll(
                    (HSD_JObj*) gobj->x34_unk, 0x10);
                do {
                    HSD_JObj* sp10;
                    HSD_JObj* j;
                    j = mnStageSw_802364A0(gobj, (u8) i);
                    if ((s32) i !=
                        (s32) ((MnStageSw_Data*) gobj)->stage_idx)
                    {
                        lb_80011E24(j, &sp10, 3, -1);
                        HSD_JObjSetFlagsAll(sp10, 0x10);
                    }
                    i++;
                } while (i < 0x1D);
                mnStageSw_80236178(
                    gobj, ((MnStageSw_Data*) gobj)->stage_idx);
                mnStageSw_804D6BF4 = 0;
                return;
            }
            case 4: {
                s32 i = 0;
                s32* p = (s32*) inner + i;
                do {
                    HSD_SisLib_803A5CC4((HSD_Text*) p[0x10]);
                    i++;
                    p++;
                } while (i < 0x1D);
                HSD_GObjPLink_80390228(gobj);
                return;
            }
            }
        } else {
            HSD_JObjAnim(jobj);
        }
    }

    state = ((MnStageSw_Data*) inner)->state;
    if (state == 0 || state == 1 || state == 3) {
        if (((MnStageSw_Data*) inner)->stage_idx !=
            (u8) mn_804A04F0.hovered_selection)
        {
            var_r28 = 1;
        }
        if (((MnStageSw_Data*) inner)
                ->confirmed[(u8) mn_804A04F0.hovered_selection] !=
            (u8) mn_804A04F0.confirmed_selection)
        {
            var_r27 = 1;
        }
    }
    mnStageSw_80236548(gobj, (u8) var_r28, (u8) var_r27);
    if (var_r29 != 0) {
        ((MnStageSw_Data*) inner)->cur_menu =
            (u8) mn_804A04F0.cur_menu;
    }
    if (var_r28 != 0) {
        ((MnStageSw_Data*) inner)->stage_idx =
            (u8) mn_804A04F0.hovered_selection;
    }
    if (var_r27 != 0) {
        ((MnStageSw_Data*) inner)
            ->confirmed[(u8) mn_804A04F0.hovered_selection] =
            (u8) mn_804A04F0.confirmed_selection;
    }
}

/// #mnStageSw_80236CBC

void mnStageSw_80237410(void)
{
    HSD_GObj* gobj;
    HSD_GObjProc* proc;

    mn_804A04F0.prev_menu = mn_804A04F0.cur_menu;
    mn_804A04F0.cur_menu = 0x11;
    mn_804A04F0.hovered_selection = mnStageSw_80235C58(0);
    mnStageSw_804D6BF4 = 1;
    gobj = mnStageSw_80236CBC(1);
    HSD_GObj_80390CD4(gobj);
    gobj = GObj_Create(0, 1, 0x80);
    proc = HSD_GObj_SetupProc(gobj, fn_80235F80, 0);
    proc->flags_3 = HSD_GObj_804D783C;
}
