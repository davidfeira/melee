#include "ifmagnify.h"

#include "cm/camera.h"
#include "ft/ftlib.h"
#include "gr/ground.h"
#include "if/ifall.h"
#include "if/if_2FC93.h"
#include "lb/lb_00B0.h"
#include "lb/lb_00F9.h"
#include "lb/lbarchive.h"
#include "pl/player.h"

#include <baselib/cobj.h>
#include <baselib/gobj.h>
#include <baselib/gobjgxlink.h>
#include <baselib/gobjobject.h>
#include <baselib/gobjplink.h>
#include <baselib/jobj.h>
#include <baselib/tobj.h>
#include <melee/gm/gm_1601.h>
#include <melee/gm/gm_16AE.h>
#include <melee/gm/types.h>
#include <trigf.h>

/* 3F97E8 */ extern HSD_CameraDescPerspective ifMagnify_803F97E8;
/* 4DDB08 */ extern f32 ifMagnify_804DDB08;
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

/// #ifMagnify_802FB73C

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

/// #ifMagnify_802FBBDC

void ifMagnify_802FC3BC(void) {}

/// #ifMagnify_802FC3C0

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
