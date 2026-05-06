#include "mninfo.h"

#include "placeholder.h"

#include "gm/gmmain_lib.h"
#include "if/ifprize.h"
#include "lb/lb_00F9.h"
#include "lb/lblanguage.h"
#include "mn/inlines.h"
#include "mn/mnmain.h"

#include <sysdolphin/baselib/debug.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/gobjplink.h>
#include <sysdolphin/baselib/gobjproc.h>
#include <sysdolphin/baselib/gobjuserdata.h>
#include <sysdolphin/baselib/jobj.h>
#include <sysdolphin/baselib/memory.h>
#include <sysdolphin/baselib/sislib.h>

#pragma push
#pragma dont_inline on
s32 mnInfo_80251A08(s32 arg0)
{
    switch (arg0) { /* irregular */
    case 0x3E:
        return 0;
    case 0x34:
        if (lbLang_IsSettingUS() != 0) {
            return 0;
        }
        return gmMainLib_8015D94C(arg0);
    case 0x35:
        if (lbLang_IsSettingJP() != 0) {
            return 0;
        }
        return gmMainLib_8015D94C(arg0);
    default:
        return gmMainLib_8015D94C(arg0);
    }
}
#pragma pop

#pragma push
#pragma dont_inline on
s32 mnInfo_80251AA4(void)
{
    s32 i;
    s32 var_r30 = 0;

    for (i = 0; i < 0x42; i++) {
        if (mnInfo_80251A08(i) != 0) {
            var_r30++;
        }
    }
    return var_r30;
}
#pragma pop

/// #mnInfo_80251AFC

/// #mnInfo_80251D58

#pragma push
#pragma dont_inline on
void mnInfo_80251F04(HSD_GObj* gobj, u32 idx, u32 arg2)
{
    MnInfoData* data;
    HSD_Text* text;
    s16 sp16;

    data = gobj->user_data;
    if (data->right_column[idx] != NULL) {
        HSD_SisLib_803A5CC4(data->right_column[idx]);
    }
    text = HSD_SisLib_803A5ACC(0, 0, -5.0f, (3.45f * idx) + -5.9f, 17.0f,
                               514.2857f, 142.85715f);
    data->right_column[idx] = text;
    text->font_size.x = 0.035f;
    text->font_size.y = 0.035f;
    text->default_fitting = 1;
    un_802FE3F8((s32) arg2, 0x4BD, &sp16, NULL);
    HSD_SisLib_803A6368(text, (s32) (u16) sp16);
}
#pragma pop

extern void* mnInfo_804A0958[4];
extern HSD_GObj* mnInfo_804D6C78;
extern u8 mnInfo_804A0968[0x48];

void fn_80251FE4(HSD_GObj* unused)
{
    MnInfoData* data;
    HSD_GObj* gobj;
    s32 i;
    s32 count;
    u8* p;
    u8 v;
    long long x;

    data = mnInfo_804D6C78->user_data;
    if (mn_804D6BC8.cooldown != 0) {
        Menu_DecrementAnimTimer();
        return;
    }
    x = mn_804A04F0.buttons = mn_80229624(4);
    if (x & MenuInput_Back) {
        sfxBack();
        mn_804A04F0.entering_menu = 0;
        mn_80229894(5, 4, 3);
        return;
    }
    if (x & MenuInput_Up) {
        if (data->scroll_idx != 0) {
            MnInfoData* dw;
            MnInfoData* dr;
            data->scroll_idx -= 1;
            sfxMove();
            dw = mnInfo_804D6C78->user_data;
            dr = dw;
            for (i = 0; i < 4; i++) {
                if (dw->left_column[0] != NULL) {
                    HSD_SisLib_803A5CC4(dr->left_column[0]);
                    dw->left_column[0] = NULL;
                }
                if (dw->right_column[0] != NULL) {
                    HSD_SisLib_803A5CC4(dr->right_column[0]);
                    dw->right_column[0] = NULL;
                }
                dw = (MnInfoData*) ((u8*) dw + 4);
                dr = (MnInfoData*) ((u8*) dr + 4);
            }
            gobj = mnInfo_804D6C78;
            p = &mnInfo_804A0968[data->scroll_idx];
            for (i = 0; i < 4; i++) {
                if (mnInfo_80251A08(*p) != 0) {
                    v = *p;
                    mnInfo_80251D58(gobj, i, v, *gmMainLib_8015D804(v));
                    mnInfo_80251F04(gobj, i, v);
                }
                p++;
            }
        }
    } else if (x & MenuInput_Down) {
        count = 0;
        for (i = 0; i < 0x42; i++) {
            if (mnInfo_80251A08(i) != 0) {
                count++;
            }
        }
        if ((s32) (data->scroll_idx + 4) < count) {
            MnInfoData* dw;
            MnInfoData* dr;
            sfxMove();
            data->scroll_idx += 1;
            dw = mnInfo_804D6C78->user_data;
            dr = dw;
            for (i = 0; i < 4; i++) {
                if (dw->left_column[0] != NULL) {
                    HSD_SisLib_803A5CC4(dr->left_column[0]);
                    dw->left_column[0] = NULL;
                }
                if (dw->right_column[0] != NULL) {
                    HSD_SisLib_803A5CC4(dr->right_column[0]);
                    dw->right_column[0] = NULL;
                }
                dw = (MnInfoData*) ((u8*) dw + 4);
                dr = (MnInfoData*) ((u8*) dr + 4);
            }
            gobj = mnInfo_804D6C78;
            p = &mnInfo_804A0968[data->scroll_idx];
            for (i = 0; i < 4; i++) {
                if (mnInfo_80251A08(*p) != 0) {
                    v = *p;
                    mnInfo_80251D58(gobj, i, v, *gmMainLib_8015D804(v));
                    mnInfo_80251F04(gobj, i, v);
                }
                p++;
            }
        }
    }
}

static AnimLoopSettings mnInfo_803EFC08[0x12] = {
    { 0.0f, 199.0f, 0.0f },
    { 1.8e-42f, 1.802e-42f, 1.803e-42f },
    { 1.805e-42f, 2.1092525e-16f, 1.379729e31f },
    { 0.0f, 2.109659e-16f, 1.4748028e31f },
    { 0.0f, 225.43028f, 5.083402e31f },
    { 5.085142e31f, 7.153577e22f, 2.817505e20f },
    { 6.162976e-33f, 4.6115556e27f, 2.8237532e23f },
    { 0.0f, 3.0854143e32f, 1.6456562e19f },
    { 1.4757395e20f, 2.405757e8f, 2.6912729e20f },
    { 7.3738955e28f, 1.5307577e19f, 1.6892836e19f },
    { 1.8878586e28f, 2.405757e8f, 2.6912729e20f },
    { 7.3738955e28f, 1.5307577e19f, 1.6244036e19f },
    { 4.5346362e27f, 1.8878586e28f, 2.405757e8f },
    { 2.6912729e20f, 7.3738955e28f, 1.5307577e19f },
    { 1.710508e19f, 2.7487011e20f, 1.6892836e19f },
    { 1.8878586e28f, 2.405757e8f, 2.6912729e20f },
    { 7.3738955e28f, 1.5307577e19f, 1.7539375e19f },
    { 2.8395941e29f, 1.7935375e25f, 7.2243537e28f },
};

#pragma push
#pragma dont_inline on
void mnInfo_802522B8(HSD_GObj* gobj)
{
    s32 count;
    s32 i;
    MnInfoData* data;
    HSD_JObj* jobj;
    HSD_JObj* child;
    PAD_STACK(12);

    jobj = gobj->hsd_obj;
    data = gobj->user_data;
    lb_80011E24(jobj, &child, 2, -1);
    if (data->scroll_idx != 0) {
        HSD_JObjClearFlagsAll(child, JOBJ_HIDDEN);
    } else {
        HSD_JObjSetFlagsAll(child, JOBJ_HIDDEN);
    }
    lb_80011E24(jobj, &child, 1, -1);

    count = 0;
    for (i = 0; i < 0x42; i++) {
        if (mnInfo_80251A08(i) != 0) {
            count++;
        }
    }

    if ((data->scroll_idx + 4) < count) {
        HSD_JObjClearFlagsAll(child, JOBJ_HIDDEN);
    } else {
        HSD_JObjSetFlagsAll(child, JOBJ_HIDDEN);
    }
    mn_8022ED6C(jobj, mnInfo_803EFC08);
}
#pragma pop

void fn_802523B8(HSD_GObj* gobj)
{
    HSD_GObjPLink_80390228(gobj);
}

void fn_802523D8(HSD_GObj* gobj)
{
    MnInfoData* data;
    HSD_JObj* child;
    HSD_GObjProc* proc;
    HSD_JObj* jobj;
    s32 i;

    data = gobj->user_data;
    if (mn_804A04F0.cur_menu != 0x1D) {
        MnInfoData* dw;
        MnInfoData* dr;
        HSD_GObjProc_8038FE24(HSD_GObj_804D7838);
        proc = HSD_GObj_SetupProc(gobj, fn_802523B8, 0);
        proc->flags_3 = HSD_GObj_804D783C;
        dw = gobj->user_data;
        dr = dw;
        for (i = 0; i < 4; i++) {
            if (dw->left_column[0] != NULL) {
                HSD_SisLib_803A5CC4(dr->left_column[0]);
                dw->left_column[0] = NULL;
            }
            if (dw->right_column[0] != NULL) {
                HSD_SisLib_803A5CC4(dr->right_column[0]);
                dw->right_column[0] = NULL;
            }
            dw = (MnInfoData*) ((u8*) dw + 4);
            dr = (MnInfoData*) ((u8*) dr + 4);
        }
        HSD_SisLib_803A5CC4(data->description);
    } else {
        jobj = gobj->hsd_obj;
        lb_80011E24(jobj, &child, 2, -1);
        if (data->scroll_idx != 0) {
            HSD_JObjClearFlagsAll(child, JOBJ_HIDDEN);
        } else {
            HSD_JObjSetFlagsAll(child, JOBJ_HIDDEN);
        }
        lb_80011E24(jobj, &child, 1, -1);
        if ((s32) (data->scroll_idx + 4) < mnInfo_80251AA4()) {
            HSD_JObjClearFlagsAll(child, JOBJ_HIDDEN);
        } else {
            HSD_JObjSetFlagsAll(child, JOBJ_HIDDEN);
        }
        mn_8022ED6C(jobj, mnInfo_803EFC08);
    }
}

void fn_80252548(HSD_GObj* gobj)
{
    MnInfoData* data;
    HSD_GObjProc* proc;
    HSD_JObj* jobj;
    s32 i;

    data = gobj->user_data;
    if (mn_804A04F0.cur_menu != 0x1D) {
        MnInfoData* dw;
        MnInfoData* dr;
        HSD_GObjProc_8038FE24(HSD_GObj_804D7838);
        proc = HSD_GObj_SetupProc(gobj, fn_802523B8, 0);
        proc->flags_3 = HSD_GObj_804D783C;
        dw = gobj->user_data;
        dr = dw;
        for (i = 0; i < 4; i++) {
            if (dw->left_column[0] != NULL) {
                HSD_SisLib_803A5CC4(dr->left_column[0]);
                dw->left_column[0] = NULL;
            }
            if (dw->right_column[0] != NULL) {
                HSD_SisLib_803A5CC4(dr->right_column[0]);
                dw->right_column[0] = NULL;
            }
            dw = (MnInfoData*) ((u8*) dw + 4);
            dr = (MnInfoData*) ((u8*) dr + 4);
        }
        HSD_SisLib_803A5CC4(data->description);
    } else {
        u8* p;
        if (data->anim_timer != 0) {
            data->anim_timer--;
            return;
        }
        p = mnInfo_804A0968;
        for (i = 0; i < 4; i++) {
            if (mnInfo_80251A08(*p) != 0) {
                u8 v = *p;
                mnInfo_80251D58(gobj, i, v, *gmMainLib_8015D804(v));
                mnInfo_80251F04(gobj, i, v);
            }
            p++;
        }
        jobj = HSD_JObjLoadJoint(mnInfo_804A0958[0]);
        HSD_GObjObject_80390A70(gobj, HSD_GObj_804D7849, jobj);
        GObj_SetupGXLink(gobj, HSD_GObj_JObjCallback, 4, 0x80);
        HSD_JObjAddAnimAll(jobj, mnInfo_804A0958[1], mnInfo_804A0958[2],
                           mnInfo_804A0958[3]);
        HSD_JObjReqAnimAll(jobj, 0.0f);
        mnInfo_802522B8(gobj);
        HSD_GObjProc_8038FE24(HSD_GObj_804D7838);
        proc = HSD_GObj_SetupProc(gobj, fn_802523D8, 0);
        proc->flags_3 = HSD_GObj_804D783C;
    }
}

void mnInfo_80252720(MnInfoData* data)
{
    data->scroll_idx = 0;
    data->anim_timer = 10;
    data->description = NULL;
    data->left_column[0] = NULL;
    data->right_column[0] = NULL;
    data->left_column[1] = NULL;
    data->right_column[1] = NULL;
    data->left_column[2] = NULL;
    data->right_column[2] = NULL;
    data->left_column[3] = NULL;
    data->right_column[3] = NULL;
}

void mnInfo_80252758(void)
{
    HSD_GObj* gobj;
    MnInfoData* data;
    HSD_GObjProc* proc;
    HSD_Text* text;

    mn_804D6BC8.cooldown = 5;
    mn_804A04F0.prev_menu = mn_804A04F0.cur_menu;
    mn_804A04F0.cur_menu = 0x1D;
    mn_804A04F0.hovered_selection = 0;

    lbArchive_LoadSections(
        mn_804D6BB8, &mnInfo_804A0958[0], "MenMainConCo_Top_joint",
        &mnInfo_804A0958[1], "MenMainConCo_Top_animjoint",
        &mnInfo_804A0958[2], "MenMainConCo_Top_matanim_joint",
        &mnInfo_804A0958[3], "MenMainConCo_Top_shapeanim_joint", 0);

    mnInfo_80251AFC();

    gobj = GObj_Create(6, 7, 0x80);
    mnInfo_804D6C78 = gobj;

    data = HSD_MemAlloc(sizeof(MnInfoData));
    HSD_ASSERTREPORT(0x267, data, "Can't get user_data.\n");
    mnInfo_80252720(data);
    GObj_InitUserData(gobj, 0, HSD_Free, data);

    proc = HSD_GObj_SetupProc(gobj, (HSD_GObjEvent) fn_80252548, 0);
    proc->flags_3 = HSD_GObj_804D783C;

    data = gobj->user_data;
    if (data->description != NULL) {
        HSD_SisLib_803A5CC4(data->description);
    }
    text = HSD_SisLib_803A5ACC(0, 1, -9.5f, 9.1f, 17.0f, 364.68332f, 38.38772f);
    data->description = text;
    text->font_size.x = 0.0521f;
    text->font_size.y = 0.0521f;
    HSD_SisLib_803A6368(text, 0xA3);

    proc = HSD_GObj_SetupProc(GObj_Create(0, 1, 0x80),
                              (HSD_GObjEvent) fn_80251FE4, 0);
    proc->flags_3 = HSD_GObj_804D783C;
}
