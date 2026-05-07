#include "ifmagnify.h"

#include "cm/camera.h"
#include "ft/ftdrawcommon.h"
#include "ft/ftlib.h"
#include "gr/ground.h"
#include "gr/stage.h"
#include "if/ifall.h"
#include "if/if_2FC93.h"
#include "lb/lb_00B0.h"
#include "lb/lb_00F9.h"
#include "lb/lbarchive.h"
#include "pl/inlines.h"
#include "pl/player.h"

#include <baselib/cobj.h>
#include <baselib/dobj.h>
#include <baselib/gobj.h>
#include <baselib/gobjgxlink.h>
#include <baselib/gobjobject.h>
#include <baselib/gobjplink.h>
#include <baselib/gobjuserdata.h>
#include <baselib/jobj.h>
#include <baselib/memory.h>
#include <baselib/mobj.h>
#include <baselib/displayfunc.h>
#include <baselib/tobj.h>
#include <melee/gm/gm_1601.h>
#include <melee/gm/gm_16AE.h>
#include <melee/gm/types.h>
#include <trigf.h>

/* 3F97E8 */ extern HSD_CameraDescPerspective ifMagnify_803F97E8;
/* 4DDB08 */ extern f32 ifMagnify_804DDB08;
/* 4DDB28 */ extern f32 ifMagnify_804DDB28;
/* 4DDB2C */ extern f32 ifMagnify_804DDB2C;
/* 4DDB30 */ extern f32 ifMagnify_804DDB30;
/* 4DDB34 */ extern f32 ifMagnify_804DDB34;
/* 4DDB38 */ extern f32 ifMagnify_804DDB38;
/* 4DDB3C */ extern f32 ifMagnify_804DDB3C;
/* 4DDB40 */ extern f32 ifMagnify_804DDB40;
/* 4DDB44 */ extern f32 ifMagnify_804DDB44;
/* 4DDB48 */ extern f32 ifMagnify_804DDB48;
/* 4DDB4C */ extern f32 ifMagnify_804DDB4C;
/* 4DDB50 */ static const double ifMagnify_804DDB50 = 4503601774854144.0;
/* 4DDB60 */ extern int ifMagnify_804DDB60;

__declspec(section ".sdata") char ifMagnify_804D57E8[] = "lupe";

ifMagnify ifMagnify_804A1DE0;

s32 ifMagnify_802FB6E8(s32 slot)
{
    if (ifMagnify_802FC998(slot) != 0) {
        return ifMagnify_804A1DE0.player[slot].state.unk;
    }
    return 0;
}

void ifMagnify_802FB73C(void* player, Vec2* in, Vec2* out)
{
    typedef struct {
        HSD_GObj* gobj;
        HSD_TObj* tobj;
        HSD_ImageDesc* idesc;
        struct {
            u8 is_offscreen : 1;
            u8 ignore_offscreen : 1;
            u8 unk : 6;
        } state;
    } PlayerEntry;
    PlayerEntry* p = (PlayerEntry*) player;

    f32 x = in->x;
    f32 y = in->y;
    f32 ratio;
    f32 tmp;

    if (ifMagnify_804DDB08 == x) {
        if (y > ifMagnify_804DDB08) {
            out->y = ifMagnify_804DDB28;
        } else {
            out->y = ifMagnify_804DDB2C;
        }
        out->x = ifMagnify_804DDB08;
    } else {
        ratio = y / x;
        if ((ratio > ifMagnify_804DDB30) || (ratio < ifMagnify_804DDB34)) {
            if (y > ifMagnify_804DDB08) {
                out->y = ifMagnify_804DDB28;
            } else {
                out->y = ifMagnify_804DDB2C;
            }
            tmp = (out->y * x) / y;
            if (tmp < ifMagnify_804DDB38) {
                out->x = ifMagnify_804DDB38;
            } else if (tmp > ifMagnify_804DDB3C) {
                out->x = ifMagnify_804DDB3C;
            } else {
                out->x = tmp;
            }
        } else {
            if (x > ifMagnify_804DDB08) {
                out->x = ifMagnify_804DDB3C;
            } else {
                out->x = ifMagnify_804DDB38;
            }
            tmp = (out->x * y) / x;
            if (tmp < ifMagnify_804DDB2C) {
                out->y = ifMagnify_804DDB2C;
            } else if (tmp > ifMagnify_804DDB28) {
                out->y = ifMagnify_804DDB28;
            } else {
                out->y = tmp;
            }
        }
    }

    if (out->x == ifMagnify_804DDB38) {
        p->state.unk = 2;
        return;
    }
    if (out->x == ifMagnify_804DDB3C) {
        p->state.unk = 4;
        return;
    }
    if (out->y == ifMagnify_804DDB28) {
        p->state.unk = 1;
        return;
    }
    p->state.unk = 3;
}

void ifMagnify_802FB8C0(HSD_GObj* arg0, s32 arg1)
{
    typedef struct {
        HSD_GObj* gobj;
        HSD_JObj* tobj;
        HSD_ImageDesc* idesc;
        struct {
            u8 is_offscreen : 1;
            u8 ignore_offscreen : 1;
            u8 unk : 6;
        } state;
    } PlayerEntry;

    S32Vec2 sp40;
    Vec2 sp38;
    f32 sp34;
    f32 sp30;
    Vec3 sp24;
    GXColor sp20;
    GXColor sp1C;
    s32 do_render;
    s32 slot;
    PlayerEntry* entry;
    s32 var_r29;
    HSD_GObj* fighter;
    u8 pkind;
    u8 team_mode;
    u32 state_val;
    u8 kind;
    PAD_STACK(24);

    if (arg1 != 0) {
        return;
    }

    entry = (PlayerEntry*) arg0->user_data;
    slot = ((u8*) entry - ((u8*) ifMagnify_804A1DE0.player + 0)) / 0x10;
    var_r29 = 0;

    if (gm_8016AE38()->hud_enabled == 0 || ifAll_IsHUDHidden() != 0 ||
        Camera_80030130() != 0) {
        do_render = 0;
    } else {
        do_render = 1;
    }

    if (do_render != 0 && entry->state.is_offscreen) {
        fighter = Player_GetEntity(slot);
        if (fighter != NULL) {
            ftLib_80086A58(fighter, &sp40);
            sp30 = (f32) sp40.x - ifMagnify_804DDB40;
            sp34 = -((f32) sp40.y - ifMagnify_804DDB44);
            HSD_JObjSetRotationZ(entry->tobj, atan2f(sp34, sp30));
            ifMagnify_802FB73C(entry, (Vec2*) &sp30, &sp38);
            sp24.x = ifMagnify_804DDB48 * sp38.x;
            sp24.y = ifMagnify_804DDB4C * sp38.y;
            sp24.z = ifMagnify_804DDB08;
            HSD_JObjSetTranslate((HSD_JObj*) entry->gobj->hsd_obj, &sp24);
            HSD_GObj_JObjCallback(arg0, arg1);
            state_val = entry->state.unk & 0x3F;
            if (state_val == 4 || state_val == 2) {
                pkind = Player_GetPlayerSlotType(slot);
                team_mode = gm_8016B168();
                sp20 = gm_80160968(gm_80160854((u8) slot, Player_GetTeam(slot),
                                              team_mode, pkind));
                sp1C = sp20;
                if (state_val == 2) {
                    kind = 1;
                } else {
                    kind = 2;
                }
                un_802FD928((u8) slot, kind, &sp1C);
                var_r29 = 1;
            }
        }
    }

    if (var_r29 == 0) {
        un_802FD9D8((u8) slot);
    }
}

extern f32 ifMagnify_804DDB0C;
extern f32 ifMagnify_804DDB10;
extern f32 ifMagnify_804DDB14;
extern f32 ifMagnify_804DDB18;
extern f32 ifMagnify_804DDB58;
extern f32 ifMagnify_804DDB5C;

extern GXColor* (*ifMagnify_803F9828[9])(void);
extern u32 ifMagnify_803F984C[16];

void ifMagnify_802FBBDC(HSD_GObj* gobj)
{
    s32 i;
    s32 j;
    f32 sp_left;
    f32 sp_right;
    f32 sp_top;
    f32 sp_bottom;
    f32 sp_ortho_top;
    f32 sp_ortho_bottom;
    f32 sp_ortho_left;
    f32 sp_ortho_right;
    Vec3 sp_pos;
    HSD_CObj* cobj;
    HSD_GObj* fighter;
    GXColor colors[4];
    f32 yt;
    f32 xt;
    f32 fb;
    f32 fa;
    f32 scale;
    Vec2 sp_pp;
#define px sp_pp.x
#define py sp_pp.y
    f32 cx_lookup;
    f32 cy_lookup;
    f32 fx0;
    f32 fx1;
    f32 fx2;
    f32 fx3;
    ifMagnify* mg;
    s32 in_view;

    ifMagnify_804A1DE0.player[0].state.is_offscreen = 0;
    ifMagnify_804A1DE0.player[1].state.is_offscreen = 0;
    ifMagnify_804A1DE0.player[2].state.is_offscreen = 0;
    ifMagnify_804A1DE0.player[3].state.is_offscreen = 0;
    ifMagnify_804A1DE0.player[4].state.is_offscreen = 0;
    ifMagnify_804A1DE0.player[5].state.is_offscreen = 0;

    {
        s32 do_render;
        if (gm_8016AE38()->hud_enabled == 0 || ifAll_IsHUDHidden() != 0 ||
            Camera_80030130() != 0) {
            do_render = 0;
        } else {
            do_render = 1;
        }
        if (do_render == 0) {
            return;
        }
    }

    cobj = gobj->hsd_obj;
    HSD_CObjGetOrtho(cobj, &sp_ortho_top, &sp_ortho_bottom, &sp_ortho_left,
                     &sp_ortho_right);
    if (HSD_CObjSetCurrent(cobj) != 0) {
        HSD_GObj_80390ED0(gobj, 7);
        HSD_CObjEndCurrent();
    }

    for (i = 0, mg = &ifMagnify_804A1DE0; i < 6;
         i++, mg = (ifMagnify*) ((u8*) mg + 0x10)) {
        fighter = Player_GetEntity(i);
        if (mg->player[0].state.ignore_offscreen) {
            continue;
        }
        if (fighter == NULL) {
            continue;
        }
        if (ftLib_80086B64(fighter) == 0) {
            continue;
        }
        if (ftLib_80086ED0(fighter) == 0) {
            continue;
        }
        scale = ftLib_80086B80(fighter) * ifMagnify_804DDB58;
        HSD_CObjSetOrtho(cobj, sp_ortho_top * scale, sp_ortho_bottom * scale,
                         sp_ortho_left * scale, sp_ortho_right * scale);
        ftLib_80086B90(fighter, &sp_pos);
        HSD_CObjSetInterest(cobj, &sp_pos);
        sp_pos.z = ifMagnify_804DDB5C;
        HSD_CObjSetEyePosition(cobj, &sp_pos);
        if (HSD_CObjSetCurrent(cobj) == 0) {
            continue;
        }
        Player_80036978(i, (s32) &sp_pp);
        in_view = 1;
        if (!(px < Stage_GetCamBoundsLeftOffset()) &&
            !(px > Stage_GetCamBoundsRightOffset())) {
            in_view = 0;
        }
        if (in_view != 0) {
            fa = ifMagnify_804DDB08;
        } else {
            f32 bucket;
            if (px < Stage_GetCamBoundsLeftOffset()) {
                bucket = ifMagnify_804DDB08;
            } else if (px > Stage_GetCamBoundsRightOffset()) {
                bucket = ifMagnify_804DDB0C;
            } else if (px <
                       ifMagnify_804DDB10 *
                           (Stage_GetCamBoundsLeftOffset() +
                            Stage_GetCamBoundsRightOffset())) {
                bucket = ifMagnify_804DDB14;
            } else {
                bucket = ifMagnify_804DDB18;
            }
            if ((s32) bucket - 1 == 0) {
                f32 l1 = Stage_GetCamBoundsLeftOffset();
                f32 r1 = Stage_GetCamBoundsRightOffset();
                f32 mid = ifMagnify_804DDB10 *
                              (Stage_GetCamBoundsLeftOffset() + r1) -
                          l1;
                fa = ifMagnify_804DDB14 -
                     (px - Stage_GetCamBoundsLeftOffset()) / mid;
            } else {
                f32 r1 = Stage_GetCamBoundsRightOffset();
                f32 r2 = Stage_GetCamBoundsRightOffset();
                f32 mid = -(ifMagnify_804DDB10 *
                                (Stage_GetCamBoundsLeftOffset() + r2) -
                            r1);
                f32 r3 = Stage_GetCamBoundsRightOffset();
                fa = ifMagnify_804DDB14 -
                     -(ifMagnify_804DDB10 *
                           (Stage_GetCamBoundsLeftOffset() + r3) -
                       px) /
                         mid;
            }
        }
        xt = ifMagnify_804DDB14 - fa;

        in_view = 1;
        if (!(py > Stage_GetCamBoundsTopOffset()) &&
            !(py < Stage_GetCamBoundsBottomOffset())) {
            in_view = 0;
        }
        if (in_view != 0) {
            fb = ifMagnify_804DDB08;
        } else {
            f32 bucket;
            if (py > Stage_GetCamBoundsTopOffset()) {
                bucket = ifMagnify_804DDB08;
            } else if (py < Stage_GetCamBoundsBottomOffset()) {
                bucket = ifMagnify_804DDB0C;
            } else if (py >
                       ifMagnify_804DDB10 *
                           (Stage_GetCamBoundsTopOffset() +
                            Stage_GetCamBoundsBottomOffset())) {
                bucket = ifMagnify_804DDB14;
            } else {
                bucket = ifMagnify_804DDB18;
            }
            if ((s32) bucket - 1 == 0) {
                f32 t1 = Stage_GetCamBoundsTopOffset();
                f32 b1 = Stage_GetCamBoundsBottomOffset();
                f32 mid = -(ifMagnify_804DDB10 *
                                (Stage_GetCamBoundsTopOffset() + b1) -
                            t1);
                fb = ifMagnify_804DDB14 -
                     (Stage_GetCamBoundsTopOffset() - py) / mid;
            } else {
                f32 b1 = Stage_GetCamBoundsBottomOffset();
                f32 b2 = Stage_GetCamBoundsBottomOffset();
                f32 mid = ifMagnify_804DDB10 *
                              (Stage_GetCamBoundsTopOffset() + b2) -
                          b1;
                f32 b3 = Stage_GetCamBoundsBottomOffset();
                fb = ifMagnify_804DDB14 -
                     (ifMagnify_804DDB10 *
                          (Stage_GetCamBoundsTopOffset() + b3) -
                      py) /
                         mid;
            }
        }
        yt = ifMagnify_804DDB14 - fb;

        for (j = 0; j < 4; j++) {
            if (py > Stage_GetCamBoundsTopOffset()) {
                cy_lookup = ifMagnify_804DDB08;
            } else if (py < Stage_GetCamBoundsBottomOffset()) {
                cy_lookup = ifMagnify_804DDB0C;
            } else if (py >
                       ifMagnify_804DDB10 *
                           (Stage_GetCamBoundsTopOffset() +
                            Stage_GetCamBoundsBottomOffset())) {
                cy_lookup = ifMagnify_804DDB14;
            } else {
                cy_lookup = ifMagnify_804DDB18;
            }
            if (px < Stage_GetCamBoundsLeftOffset()) {
                cx_lookup = ifMagnify_804DDB08;
            } else if (px > Stage_GetCamBoundsRightOffset()) {
                cx_lookup = ifMagnify_804DDB0C;
            } else if (px <
                       ifMagnify_804DDB10 *
                           (Stage_GetCamBoundsLeftOffset() +
                            Stage_GetCamBoundsRightOffset())) {
                cx_lookup = ifMagnify_804DDB14;
            } else {
                cx_lookup = ifMagnify_804DDB18;
            }
            {
                u8 byte = ((u8*) &ifMagnify_803F984C[(s32) cy_lookup * 4 +
                                                     (s32) cx_lookup])[j];
                colors[j] = *ifMagnify_803F9828[byte]();
            }
        }

        fx0 = xt * (ifMagnify_804DDB14 - yt);
        fx1 = (ifMagnify_804DDB14 - xt) * (ifMagnify_804DDB14 - yt);
        fx2 = (ifMagnify_804DDB14 - xt) * yt;
        fx3 = xt * yt;

        HSD_SetEraseColor(
            (u8) (s32) ((f32) colors[3].r * fx3 +
                        ((f32) colors[2].r * fx2 +
                         ((f32) colors[0].r * fx1 +
                          (f32) colors[1].r * fx0))),
            (u8) (s32) ((f32) colors[3].g * fx3 +
                        ((f32) colors[2].g * fx2 +
                         ((f32) colors[0].g * fx1 +
                          (f32) colors[1].g * fx0))),
            (u8) (s32) ((f32) colors[3].b * fx3 +
                        ((f32) colors[2].b * fx2 +
                         ((f32) colors[0].b * fx1 +
                          (f32) colors[1].b * fx0))),
            (u8) (s32) ((f32) colors[3].a * fx3 +
                        ((f32) colors[2].a * fx2 +
                         ((f32) colors[0].a * fx1 +
                          (f32) colors[1].a * fx0))));
        HSD_CObjEraseScreen(cobj, 1, 0, 1);
        HSD_GObj_804D7814 = fighter;
        ftDrawCommon_80080C28(fighter, 0);
        ftDrawCommon_80080C28(fighter, 1);
        ftDrawCommon_80080C28(fighter, 2);
        HSD_GObj_804D7814 = NULL;
        lb_800122C8(mg->player[0].idesc, 0, 0, 1);
        HSD_CObjEndCurrent();
        mg->player[0].state.is_offscreen = 1;
    }

    HSD_CObjSetOrtho(cobj, sp_ortho_top, sp_ortho_bottom, sp_ortho_left,
                     sp_ortho_right);
}

void ifMagnify_802FC3BC(void) {}

void ifMagnify_802FC3C0(s32 slot)
{
    HSD_JObj* jobj_root;
    HSD_JObj* sp10;
    GXColor spC;
    HSD_GObj* gobj;
    HSD_MObj* mobj;
    void* entry;
    HSD_ImageDesc* idesc;

    entry = (u8*) &ifMagnify_804A1DE0 + slot * 0x10 + 0x14;
    if (*(HSD_GObj**) entry != NULL) {
        HSD_GObjPLink_80390228(*(HSD_GObj**) entry);
    }
    gobj = GObj_Create(HSD_GOBJ_CLASS_UI, 15, 0);
    GObj_InitUserData(gobj, HSD_GOBJ_CLASS_UI,
                      (void (*)(void*)) ifMagnify_802FC3BC, entry);
    jobj_root = HSD_JObjLoadJoint(**(HSD_Joint***) ifMagnify_804A1DE0.joint);
    HSD_GObjObject_80390A70(gobj, HSD_GObj_804D7849, jobj_root);
    GObj_SetupGXLink(gobj, (GObj_RenderFunc) ifMagnify_802FB8C0, 11, 0);

    lb_80011E24(jobj_root, &sp10, 2, -1);
    if (slot == 0) {
        *(HSD_ImageDesc**) ((u8*) entry + 8) =
            sp10->u.dobj->next->mobj->tobj->imagedesc;
    } else {
        HSD_ImageDesc* src = ifMagnify_804A1DE0.player[0].idesc;
        HSD_ImageDesc* dst =
            (HSD_ImageDesc*) ((u8*) &ifMagnify_804A1DE0 + slot * 0x18 + 0x5C);
        *dst = *src;
        idesc = (HSD_ImageDesc*) ((u8*) &ifMagnify_804A1DE0 +
                                  (slot - 1) * 0x18 + 0x74);
        *(HSD_ImageDesc**) ((u8*) entry + 8) = idesc;
        idesc = *(HSD_ImageDesc**) ((u8*) entry + 8);
        idesc->image_ptr = HSD_MemAlloc(
            (GXGetTexBufferSize(idesc->width, idesc->height, idesc->format, 0,
                                0) +
             0x1F) &
            ~0x1F);
        sp10->u.dobj->next->mobj->tobj->imagedesc =
            *(HSD_ImageDesc**) ((u8*) entry + 8);
    }

    lb_80011E24(jobj_root, (HSD_JObj**) ((u8*) entry + 4), 1, -1);
    spC = gm_80160968(gm_80160854(slot, Player_GetTeam(slot), gm_8016B168(),
                                  Player_GetPlayerSlotType(slot)));

    mobj = (*(HSD_JObj**) ((u8*) entry + 4))->u.dobj->mobj;
    mobj->mat->diffuse.r = spC.r;
    mobj->mat->diffuse.g = spC.g;
    mobj->mat->diffuse.b = spC.b;
    mobj = sp10->u.dobj->mobj;
    mobj->mat->diffuse.r = spC.r;
    mobj->mat->diffuse.g = spC.g;
    mobj->mat->diffuse.b = spC.b;

    *(HSD_GObj**) entry = gobj;
    *(u8*) ((u8*) entry + 0xC) &= ~0x80;
    *(u8*) ((u8*) entry + 0xC) &= ~0x40;
}

void ifMagnify_802FC618(void)
{
    u8* player0 = (u8*) &ifMagnify_804A1DE0 + 0x14;
    HSD_GObj* gobj;
    HSD_CObj* cobj;
    HSD_ImageDesc* idesc;
    f32 half_height;
    f32 half_width;
    int pad;
    HSD_RectS16 viewport;

    gobj = GObj_Create(14, 15, 0);
    cobj = lb_80013B14(&ifMagnify_803F97E8);
    HSD_GObjObject_80390A70(gobj, HSD_GObj_804D784B, cobj);
    GObj_SetupGXLinkMax(gobj, (GObj_RenderFunc) ifMagnify_802FBBDC, 0);
    gobj->gxlink_prios = 0x10;

    idesc = *(HSD_ImageDesc**) (player0 + 8);
    half_height = ifMagnify_804DDB4C * idesc->height;
    half_width = ifMagnify_804DDB4C * idesc->width;
    HSD_CObjSetOrtho(cobj, half_height, -half_height, -half_width, half_width);

    viewport.xmin = 0;
    viewport.xmax = (*(HSD_ImageDesc**) (player0 + 8))->width;
    viewport.ymin = 0;
    viewport.ymax = (*(HSD_ImageDesc**) (player0 + 8))->height;
    HSD_CObjSetViewport(cobj, &viewport);
    HSD_CObjSetScissorx4(cobj, (u16) viewport.xmin, (u16) viewport.xmax,
                         (u16) viewport.ymin, (u16) viewport.ymax);
}

void ifMagnify_802FC750(void)
{
    ifMagnify* base = &ifMagnify_804A1DE0;
    s32 i;
    u8* ptr;
    s32 offset;
    HSD_GObj** gobj_ptr;

    ptr = (u8*) base;
    offset = 0;
    for (i = 0; i < 6; ptr += 0x10, offset += 0x10, i++) {
        if (*(HSD_GObj**) (ptr + 0x14) != NULL) {
            gobj_ptr = (HSD_GObj**) ((u8*) base + offset + 0x14);
            HSD_GObjPLink_80390228(*gobj_ptr);
            *gobj_ptr = NULL;
        }
    }
}

void ifMagnify_802FC7C0(ifMagnify* magnify)
{
    volatile int default_val = ifMagnify_804DDB60;
    GXColor* result;

    result = Ground_801C0604();
    if (result != NULL) {
        magnify->x4 = *(int*) result;
    } else {
        magnify->x4 = default_val;
    }

    result = Ground_801C0618();
    if (result != NULL) {
        magnify->x8 = *(int*) result;
    } else {
        magnify->x8 = default_val;
    }

    result = Ground_801C062C();
    if (result != NULL) {
        magnify->xC = *(int*) result;
    } else {
        magnify->xC = default_val;
    }

    result = Ground_801C0640();
    if (result != NULL) {
        magnify->x10 = *(int*) result;
    } else {
        magnify->x10 = default_val;
    }
}

void ifMagnify_802FC870(void)
{
    s32 i;

    memzero(&ifMagnify_804A1DE0, 0x74);
    ifMagnify_802FC7C0(&ifMagnify_804A1DE0);
    lbArchive_LoadSections(*ifAll_802F3690(), (void**) &ifMagnify_804A1DE0,
                           ifMagnify_804D57E8, 0);

    for (i = 0; i < 6; i++) {
        ifMagnify_802FC3C0(i);
    }
    ifMagnify_802FC618();
}

void ifMagnify_802FC8E8(void)
{
    ifMagnify_804A1DE0.player[0].state.ignore_offscreen = 1;
    ifMagnify_804A1DE0.player[1].state.ignore_offscreen = 1;
    ifMagnify_804A1DE0.player[2].state.ignore_offscreen = 1;
    ifMagnify_804A1DE0.player[3].state.ignore_offscreen = 1;
    ifMagnify_804A1DE0.player[4].state.ignore_offscreen = 1;
    ifMagnify_804A1DE0.player[5].state.ignore_offscreen = 1;
}

void ifMagnify_802FC940(void)
{
    ifMagnify_804A1DE0.player[0].state.ignore_offscreen = 0;
    ifMagnify_804A1DE0.player[1].state.ignore_offscreen = 0;
    ifMagnify_804A1DE0.player[2].state.ignore_offscreen = 0;
    ifMagnify_804A1DE0.player[3].state.ignore_offscreen = 0;
    ifMagnify_804A1DE0.player[4].state.ignore_offscreen = 0;
    ifMagnify_804A1DE0.player[5].state.ignore_offscreen = 0;
}

bool ifMagnify_802FC998(s32 ply_slot)
{
    return ifMagnify_804A1DE0.player[ply_slot].state.is_offscreen;
}
