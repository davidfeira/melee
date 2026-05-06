#include "gr/grpura.h"

#include <platform.h>

#include "baselib/gobjgxlink.h"
#include "baselib/gobjproc.h"
#include "baselib/random.h"
#include "cm/camera.h"
#include "gr/grdisplay.h"
#include "gr/ground.h"
#include "gr/grzakogenerator.h"
#include "gr/inlines.h"
#include "gr/stage.h"
#include "gr/types.h"
#include "lb/lb_00B0.h"
#include "lb/lb_00F9.h"
#include "mp/mplib.h"

#include <dolphin/mtx.h>
#include <baselib/gobj.h>
#include <baselib/jobj.h>
#include <baselib/tobj.h>
#include <sysdolphin/baselib/dobj.h>

/* 213030 */ static void grPura_80213030(Ground_GObj* arg0);

StageCallbacks grPu_803E6800[] = {
    { grPura_80211EF0, grPura_80211F1C, grPura_80211F24, grPura_80211F28, 0 },
    { grPura_80212024, grPura_802120D8, grPura_802120E0, grPura_8021228C, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80211F68, grPura_80211FD0, grPura_80211FD8, grPura_80212020,
      0x40000000 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80212290, grPura_80212314, grPura_8021231C, grPura_802125EC, 0 },
    { grPura_80211F2C, grPura_80211F58, grPura_80211F60, grPura_80211F64,
      0x80000000 }
};

char grPu_803E6A30[] = "/GrPu.dat";

StageData grPu_803E6A3C = { 0x11,
                            grPu_803E6800,
                            grPu_803E6A30,
                            grPura_80211D00,
                            grPura_80211CFC,
                            grPura_80211DD8,
                            grPura_80211DDC,
                            grPura_80211E00,
                            grPura_802130C0,
                            grPura_802130C8,
                            1,
                            0,
                            0 };

GXColor grPu_803E6AA0[] = {
    { 0x00, 0x00, 0x00, 0xFF }, { 0x00, 0x00, 0x50, 0xFF },
    { 0x80, 0x80, 0x00, 0xFF }, { 0xFF, 0xFF, 0x00, 0xFF },
    { 0x3F, 0x80, 0x00, 0x00 }, { 0x00, 0x00, 0x00, 0x02 },
    { 0x00, 0x00, 0x00, 0x01 }, { 0x3F, 0x80, 0x00, 0x00 },
    { 0x00, 0x00, 0x00, 0x03 }, { 0x00, 0x00, 0x00, 0x02 },
    { 0x3F, 0x80, 0x00, 0x00 },
};

void* grPu_803E6E20;

struct HSD_ImageDesc grPu_803E7620 = { &grPu_803E6E20, 32, 32, 4, 0, 0, 0 };

void grPura_80211CFC(bool num) {}

/// #grPura_80211D00

const f32 grPu_804DBA58 = 0.8;
const f32 grPu_804DBA5C = 3600.0;
const f32 grPu_804DBA70 = 0.0;
const f32 grPu_804DBA74 = 2.0;
const f32 grPu_804DBA78 = 30.0;
const f32 grPu_804DBA7C = -30.0;

/* 4D6AA0 */ static HSD_GObj* grPu_804D6AA0;

void grPura_80211D00(void)
{
    Vec3 cam_offset;
    f32 fVar1;

    grPu_804D6AA0 = Ground_801C49F8();
    stage_info.unk8C.b4 = 0;
    stage_info.unk8C.b5 = 1;
    grPura_80211E08(0);
    grPura_80211E08(1);
    grPura_80211E08(4);
    // r3 = grIzumi_801CBCE8(3);
    // grAnime_801C8780(r3, 3, 0, 0.0f, 1.0f);
    Ground_801C39C0();
    Ground_801C3BB4();
    Stage_UnkSetVec3TCam_Offset(&cam_offset);
    fVar1 = Stage_GetCamBoundsTopOffset();
    Ground_801C3880(grPu_804DBA58 * (fVar1 - cam_offset.y));
    fVar1 = Stage_GetCamBoundsBottomOffset();
    Ground_801C3890(grPu_804DBA58 * (fVar1 - cam_offset.y));
    fVar1 = Stage_GetCamBoundsLeftOffset();
    Ground_801C38A0(grPu_804DBA58 * (fVar1 - cam_offset.x));
    fVar1 = Stage_GetCamBoundsRightOffset();
    Ground_801C38AC(grPu_804DBA58 * (fVar1 - cam_offset.x));
}

void grPura_80211DD8(void) {}

/// #grPura_80211DDC
void grPura_80211DDC(void)
{
    grZakoGenerator_801CAE04(NULL);
}

bool grPura_80211E00(void)
{
    return false;
}

#pragma dont_inline on
HSD_GObj* grPura_80211E08(int gobj_id)
{
    HSD_GObj* gobj;
    StageCallbacks* callbacks = &grPu_803E6800[gobj_id];

    gobj = Ground_GetStageGObj(gobj_id);

    if (gobj != NULL) {
        Ground_SetupStageCallbacks(gobj, callbacks);
    } else {
        OSReport("%s:%d: couldn t get gobj(id=%d)\n", "grpura.c", 0x108,
                 gobj_id);
    }

    return gobj;
}
#pragma dont_inline reset

/// #grPura_80211EF0
void grPura_80211EF0(Ground_GObj* arg0)
{
    Ground* gp = arg0->user_data;
    grAnime_801C8138(arg0, gp->map_id, 0);
}

bool grPura_80211F1C(Ground_GObj* arg0)
{
    return false;
}

void grPura_80211F24(Ground_GObj* arg0) {}

void grPura_80211F28(Ground_GObj* arg0) {}

/// #grPura_80211F2C
void grPura_80211F2C(Ground_GObj* arg0)
{
    Ground* gp = arg0->user_data;
    grAnime_801C8138(arg0, gp->map_id, 0);
}

bool grPura_80211F58(Ground_GObj* arg0)
{
    return false;
}

void grPura_80211F60(Ground_GObj* arg0) {}

void grPura_80211F64(Ground_GObj* arg0) {}

void grPura_80211F68(Ground_GObj* arg0)
{
    Ground_JObjInline1(arg0);
    grPura_80212CD4(arg0);
    grPura_802125F0(arg0);
    grPura_80212FC0(arg0);
}

bool grPura_80211FD0(Ground_GObj* arg0)
{
    return false;
}

void grPura_80211FD8(Ground_GObj* arg0)
{
    grPura_80212EF4(arg0);
    Ground_801C2FE0(arg0);
    grPura_80213030(arg0);
    mpLib_80055E24(0x18);
    lb_800115F4();
}

void grPura_80212020(Ground_GObj* arg0) {}

void grPura_80212024(Ground_GObj* arg0)
{
    unsigned int uVar1;
    Ground* gp = GET_GROUND(arg0);
    PAD_STACK(16);
    grAnime_801C8138(arg0, gp->map_id, 0);
    gp->x11_flags.b012 = 2;
    *(s16*) &gp->gv.pura.xC4 = HSD_Randi(4);
    do {
        uVar1 = HSD_Randi(4);
    } while (*(s16*) &gp->gv.pura.xC4 == (gp->gv.pura.xC6 = uVar1));
    Ground_801C205C(&grPu_803E6AA0[*(s16*) &gp->gv.pura.xC4]);
    Camera_SetBackgroundColor(grPu_803E6AA0[*(s16*) &gp->gv.pura.xC4].r,
                              grPu_803E6AA0[*(s16*) &gp->gv.pura.xC4].g,
                              grPu_803E6AA0[*(s16*) &gp->gv.pura.xC4].b);
    *(s16*) &gp->gv.pura.xC8 = 0;
}

bool grPura_802120D8(Ground_GObj* arg0)
{
    return false;
}

/// #grPura_802120E0

void grPura_8021228C(Ground_GObj* arg0) {}

/// #grPura_80212290
void grPura_80212290(Ground_GObj* arg0)
{
    Ground* gp = GET_GROUND(arg0);
    HSD_JObj* jobj = arg0->hsd_obj;
    PAD_STACK(8);
    arg0->render_cb = (GObj_RenderFunc) fn_802130D0;
    HSD_MObjSetToonTextureImage(&grPu_803E7620);
    lb_80011C18(jobj, 0x1000);
    grPura_80213250(jobj);
    HSD_MObjSetToonTextureImage(NULL);
    grAnime_801C8138(arg0, gp->map_id, 0);
}

bool grPura_80212314(Ground_GObj* arg0)
{
    return false;
}

/// #grPura_8021231C
void grPura_8021231C(Ground_GObj* arg0)
{
    Ground* gp = GET_GROUND(arg0);
    HSD_JObj* jobj = arg0->hsd_obj;
    Vec3 vec;
    Quaternion quat;
    HSD_JObjGetTranslation2(gp->gv.pura2.xC8, &vec);
    HSD_JObjSetTranslate(jobj, &vec);
    HSD_JObjGetRotation(gp->gv.pura2.xC8, &quat);
    HSD_JObjSetRotation(jobj, &quat);
    HSD_JObjGetScale(gp->gv.pura2.xC8, &vec);
    HSD_JObjSetScale(jobj, &vec);

    // HSD_JObjGetFlags(jobj);
    if ((HSD_JObjGetFlags(gp->gv.pura2.xC8) & 0x10) &&
        ((HSD_JObjGetFlags(jobj) & 0x10) == NULL))
    {
        HSD_JObjSetFlagsAll(jobj, 0x10);
    } else if (((HSD_JObjGetFlags(gp->gv.pura2.xC8) & 0x10) == NULL) &&
               (HSD_JObjGetFlags(jobj) & 0x10))
    {
        HSD_JObjClearFlagsAll(jobj, 0x10);
    }
}

void grPura_802125EC(Ground_GObj* arg0) {}

/// #grPura_802125F0
typedef struct grPura_AB0Entry {
    s32 idx;
    f32 mult;
    s32 check;
} grPura_AB0Entry;

void grPura_802125F0(HSD_GObj* arg0)
{
    int i;
    HSD_GObj* gobj;
    Ground* gp;
    HSD_JObj* dst;
    HSD_JObj* src;
    HSD_JObj* child;
    f32 sx;
    grPura_AB0Entry* entry =
        (grPura_AB0Entry*) ((char*) &grPu_803E6800[0] + 0x2B0);

    for (i = 0; i < 27; i++, entry++) {
        if (entry->check == -1) {
            continue;
        }
        gobj = grPura_80211E08(1);
        if (gobj == NULL) {
            __assert("grpura.c", 0x291, "gobj");
        }
        gp = GET_GROUND(gobj);
        if (gp == NULL) {
            __assert("grpura.c", 0x292, "gp");
        }

        *(s16*) &gp->gv.pura.xC4 = (s16) entry->idx;
        gp->gv.pura2.xC8 = Ground_801C3FA4(
            arg0, Ground_801C33C0(4, *(s16*) &gp->gv.pura.xC4));

        dst = gobj->hsd_obj;
        HSD_JObjSetTranslateX(dst, HSD_JObjGetTranslationX(gp->gv.pura2.xC8));
        HSD_JObjSetTranslateY(dst, HSD_JObjGetTranslationY(gp->gv.pura2.xC8));
        HSD_JObjSetTranslateZ(dst, HSD_JObjGetTranslationZ(gp->gv.pura2.xC8));

        if (HSD_JObjGetFlags(gp->gv.pura2.xC8) & 0x10) {
            HSD_JObjSetFlagsAll(dst, 0x10);
        }

        child = (gobj->hsd_obj != NULL) ? ((HSD_JObj*) gobj->hsd_obj)->child
                                        : NULL;
        HSD_JObjSetTranslateX(child, grPu_804DBA70);
        HSD_JObjSetTranslateY(child, grPu_804DBA70);
        HSD_JObjSetTranslateZ(child, grPu_804DBA70);

        src = gp->gv.pura2.xC8;
        sx = HSD_JObjGetScaleX(src);
        if (sx < grPu_804DBA74) {
            sx *= entry->mult;
        }
        HSD_JObjSetScaleX(src, sx);
        HSD_JObjSetScaleY(src, sx);
        HSD_JObjSetScaleZ(src, sx);

        dst = gobj->hsd_obj;
        HSD_JObjSetScaleX(dst, sx);
        HSD_JObjSetScaleY(dst, sx);
        HSD_JObjSetScaleZ(dst, sx);
    }
}

/// #grPura_80212CD4

/// #grPura_80212EF4
typedef struct grPura_unk128 {
    u8 _0[8];
    u32 x8;
    u8 _C[4];
    Vec3 x10;
} grPura_unk128;

void grPura_80212EF4(HSD_GObj* arg0)
{
    Ground* gp = GET_GROUND(arg0);
    HSD_JObj** jobjs = (HSD_JObj**) ((s8*) gp + 0xC4);
    grPura_unk128** structs = (grPura_unk128**) ((s8*) gp + 0x128);
    int i = 0;
    Vec3 vec;

    do {
        if (jobjs[i] != NULL && structs[i] != NULL) {
            lb_8000B1CC(jobjs[i], NULL, &vec);
            structs[i]->x10 = vec;
            if (HSD_JObjGetFlags(jobjs[i]) & 0x10) {
                structs[i]->x8 = 1;
            } else {
                structs[i]->x8 = 0;
            }
        }
        i++;
    } while (i < 25);
}

/// #grPura_80212FC0

void grPura_80213030(Ground_GObj* arg0)
{
    UNUSED unsigned char _[8];
    Point3d spC;
    u16* var_r31 = grPu_803E6C0C;
    u32 var_r30 = 0;

    do {
        if (M2C_FIELD(var_r31, HSD_JObj**, 8) != NULL) {
            lb_8000B1CC(M2C_FIELD(var_r31, HSD_JObj**, 8), NULL, &spC);
            mpVtxSetPos(M2C_FIELD(var_r31, s16*, 0), spC.x, spC.y);
        }
        var_r30 += 1;
        var_r31 += 6;
    } while (var_r30 < 0x2A);
    mpJointUpdateBounding(0);
    mpJointUpdateBounding(9);
    mpJointUpdateBounding(0x18);
    mpJointUpdateBounding(5);
}

DynamicsDesc* grPura_802130C0(enum_t arg0)
{
    return false;
}

bool grPura_802130C8(Vec3* a, int num, HSD_JObj* joint)
{
    return true;
}

void fn_802130D0(HSD_GObj* arg0, int arg1)
{
    PAD_STACK(8);
    HSD_MObjSetToonTextureImage(&grPu_803E7620);
    grDisplay_801C5DB0(arg0, arg1);
    HSD_MObjSetToonTextureImage(0);
}

void grPura_80213128(HSD_DObj* dobj)
{
    HSD_DObj* iter;
    HSD_DObj* next;
    HSD_DObj* next2;

    if ((next = dobj->next) != NULL) {
        if ((next2 = next->next) != NULL) {
            if (next2->next != NULL) {
                grPura_80213128(next2->next);
            }
            for (iter = next2; iter != NULL; iter = iter->next) {
                grPura_80213224(iter);
            }
            if (next2->mobj != NULL) {
                HSD_MObjCompileTev(next2->mobj);
            }
        }
        for (iter = next; iter != NULL; iter = iter->next) {
            if (iter != NULL) {
                HSD_MObjCompileTev(iter->mobj);
            }
        }
        if (next->mobj != NULL) {
            HSD_MObjCompileTev(next->mobj);
        }
    }
    for (iter = dobj; iter != NULL; iter = iter->next) {
        if (iter != NULL) {
            HSD_MObjCompileTev(iter->mobj);
        }
    }
    if (dobj->mobj != NULL) {
        HSD_MObjCompileTev(dobj->mobj);
    }
}

/// #grPura_80213224
void grPura_80213224(HSD_DObj* dobj)
{
    if (dobj != 0) {
        HSD_MObjCompileTev(dobj->mobj);
    }
}

/// #grPura_80213250
#pragma dont_inline on
void grPura_80213250(HSD_JObj* arg0)
{
    HSD_JObj* jobj;
    HSD_DObj* dobj;
    HSD_DObj* sub;
    HSD_DObj* iter;

    jobj = arg0->child;
    if (jobj != NULL) {
        if (jobj->child != NULL) {
            grPura_80213250(jobj->child);
        }
        if (jobj->next != NULL) {
            grPura_80213250(jobj->next);
        }
        if (union_type_dobj(jobj)) {
            dobj = jobj->u.dobj;
            if (dobj != NULL) {
                if (dobj->next != NULL) {
                    grPura_80213128(dobj->next);
                }
                for (iter = dobj; iter != NULL; iter = iter->next) {
                    grPura_80213224(iter);
                }
                if (dobj->mobj != NULL) {
                    HSD_MObjCompileTev(dobj->mobj);
                }
            }
        }
    }

    jobj = arg0->next;
    if (jobj != NULL) {
        if (jobj->child != NULL) {
            grPura_80213250(jobj->child);
        }
        if (jobj->next != NULL) {
            grPura_80213250(jobj->next);
        }
        if (union_type_dobj(jobj)) {
            dobj = jobj->u.dobj;
            if (dobj != NULL) {
                if (dobj->next != NULL) {
                    grPura_80213128(dobj->next);
                }
                for (iter = dobj; iter != NULL; iter = iter->next) {
                    grPura_80213224(iter);
                }
                if (dobj->mobj != NULL) {
                    HSD_MObjCompileTev(dobj->mobj);
                }
            }
        }
    }

    if (union_type_dobj(arg0)) {
        dobj = arg0->u.dobj;
        if (dobj != NULL) {
            sub = dobj->next;
            if (sub != NULL) {
                if (sub->next != NULL) {
                    grPura_80213128(sub->next);
                }
                for (iter = sub; iter != NULL; iter = iter->next) {
                    grPura_80213224(iter);
                }
                if (sub->mobj != NULL) {
                    HSD_MObjCompileTev(sub->mobj);
                }
            }
            for (iter = dobj; iter != NULL; iter = iter->next) {
                if (iter != NULL) {
                    HSD_MObjCompileTev(iter->mobj);
                }
            }
            if (dobj->mobj != NULL) {
                HSD_MObjCompileTev(dobj->mobj);
            }
        }
    }
}
#pragma dont_inline reset
