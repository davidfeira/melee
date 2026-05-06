#include "grzebesroute.h"

#include <platform.h>

#include "cm/camera.h"
#include "ft/ftlib.h"
#include "gr/grdisplay.h"
#include "gr/ground.h"
#include "gr/grzakogenerator.h"
#include "gr/inlines.h"
#include "lb/lb_00F9.h"
#include "mp/mplib.h"

#include <baselib/gobj.h>
#include <baselib/gobjgxlink.h>
#include <baselib/gobjproc.h>
#include <baselib/lobj.h>
#include <baselib/random.h>

StageCallbacks grZe_Route_803E5DB0[] = {
    { grZebesRoute_8020B348, grZebesRoute_8020B374, grZebesRoute_8020B37C,
      grZebesRoute_8020B380, 0 },
    { grZebesRoute_8020B3C0, grZebesRoute_8020B424, grZebesRoute_8020B42C,
      grZebesRoute_8020B4D4, 0xC0000000 },
    { grZebesRoute_8020B384, grZebesRoute_8020B3B0, grZebesRoute_8020B3B8,
      grZebesRoute_8020B3BC, 0 },
    { NULL, NULL, NULL, NULL, 0 },
};

static struct {
    int x0;
    int x4;
}* grZe_Route_804D6A60;

extern Vec3 grZe_Route_803B83A0;

void grZebesRoute_8020B160(bool arg) {}

/// #grZebesRoute_8020B164
void grZebesRoute_8020B164(void)
{
    grZe_Route_804D6A60 = Ground_801C49F8();
    stage_info.unk8C.b4 = 0;
    stage_info.unk8C.b5 = 1;
    grZebesRoute_8020B260(0);
    grZebesRoute_8020B260(1);
    grZebesRoute_8020B260(2);
    Ground_801C39C0();
    Ground_801C3BB4();
}

void grZebesRoute_8020B1D4(void)
{
    grZebesRoute_8020B548();
}

void grZebesRoute_8020B1F4(void)
{
    int val;
    grZakoGenerator_801CAE04(NULL);
    val = grZe_Route_804D6A60->x4;
    if (val != 0) {
        val = HSD_Randi(grZe_Route_804D6A60->x4);
    } else {
        val = 0;
    }
    if (val == 0) {
        grZakoGenerator_801CAEB0(Ground_801C5840(), Ground_801C5940());
    }
}

bool grZebesRoute_8020B258(void)
{
    return false;
}

HSD_GObj* grZebesRoute_8020B260(int gobj_id)
{
    HSD_GObj* gobj;
    StageCallbacks* callbacks = &grZe_Route_803E5DB0[gobj_id];

    gobj = Ground_GetStageGObj(gobj_id);

    if (gobj != NULL) {
        Ground* gp = gobj->user_data;
        gp->x8_callback = NULL;
        gp->xC_callback = NULL;
        GObj_SetupGXLink(gobj, grDisplay_801C5DB0, 3, 0);
        if (callbacks->callback3 != NULL) {
            gp->x1C_callback = callbacks->callback3;
        }
        if (callbacks->callback0 != NULL) {
            callbacks->callback0(gobj);
        }
        if (callbacks->callback2 != NULL) {
            HSD_GObj_SetupProc(gobj, callbacks->callback2, 4);
        }
    } else {
        OSReport("%s:%d: couldn t get gobj(id=%d)\n", __FILE__, 197, gobj_id);
    }

    return gobj;
}

void grZebesRoute_8020B348(Ground_GObj* gobj)
{
    Ground* gp = GET_GROUND(gobj);
    grAnime_801C8138(gobj, gp->map_id, 0);
}

bool grZebesRoute_8020B374(Ground_GObj* arg)
{
    return false;
}

void grZebesRoute_8020B37C(Ground_GObj* arg) {}

void grZebesRoute_8020B380(Ground_GObj* arg) {}

void grZebesRoute_8020B384(Ground_GObj* gobj)
{
    Ground* gp = GET_GROUND(gobj);
    grAnime_801C8138(gobj, gp->map_id, 0);
}

bool grZebesRoute_8020B3B0(Ground_GObj* arg)
{
    return false;
}

void grZebesRoute_8020B3B8(Ground_GObj* arg) {}

void grZebesRoute_8020B3BC(Ground_GObj* arg) {}

void grZebesRoute_8020B3C0(Ground_GObj* gobj)
{
    Ground* gp = GET_GROUND(gobj);
    grAnime_801C8138(gobj, gp->map_id, 0);
    gp->x8_callback = NULL;
    gp->xC_callback = NULL;
    mpJointSetCb1(1, gp, (mpLib_Callback) fn_8020B4D8);
    gp->gv.zebes2.xC4 = (s16) grZe_Route_804D6A60->x0;
}

bool grZebesRoute_8020B424(Ground_GObj* arg)
{
    return false;
}

void grZebesRoute_8020B42C(Ground_GObj* gobj)
{
    Ground* gp = GET_GROUND(gobj);
    Vec3 pos = grZe_Route_803B83A0;
    HSD_GObj* fighter;
    s32 timer;

    fighter = Ground_801C57A4();
    if (fighter != NULL) {
        ftLib_80086644(fighter, &pos);
        if (pos.y < -50.0f) {
            pos.y = -50.0f;
        }
        pos.x = 0.0f;
        Ground_801C38BC(pos.x, pos.y);
    }

    timer = *(s16*) &gp->gv.zebes2.xC4;
    if (timer > 0) {
        gp->gv.zebes2.xC4 = timer - 1;
    } else {
        Camera_80030E44(1, NULL);
    }

    lb_800115F4();
}

void grZebesRoute_8020B4D4(Ground_GObj* arg) {}

void fn_8020B4D8(Ground* gp, s32 arg1, CollData* coll, s32 arg3,
                 mpLib_GroundEnum kind, f32 arg5)
{
    PAD_STACK(16);
    if ((s32) coll->x34_flags.b1234 == 1) {
        if (Ground_801C57A4() == coll->x0_gobj) {
            if (kind == 1) {
                stage_info.flags |= 0x10;
            }
        }
    }
}

void grZebesRoute_8020B548(void)
{
    Vec3 pos0;
    Vec3 pos1;
    Vec3 pos2;
    Vec3 pos3;
    Vec3 lpos;
    GXColor color0;
    GXColor color1;
    GXColor color2;
    HSD_LObj* lobj;
    s32 i;
    f32 scale;
    HSD_GObj* gobj;
    Vec3* base;

    gobj = HSD_GObjGXLinkHead[4];
    HSD_ASSERT(361, gobj);
    lobj = (HSD_LObj*) gobj->hsd_obj;
    scale = Ground_801C0498();
    base = &grZe_Route_803B83A0;
    for (i = 0, lobj = HSD_LObjGetNext(lobj); i < 3 && lobj != NULL;
         i++, lobj = HSD_LObjGetNext(lobj))
    {
        if (!HSD_LObjGetPosition(lobj, &lpos)) {
            HSD_ASSERT(372, 0);
        }
        switch (lobj->flags & 3) {
        case 3:
            pos0 = base[1];
            pos1 = base[2];
            color0.r = 0xFF;
            color0.g = 0xCC;
            color0.b = 0xFF;
            color0.a = 0xFF;
            HSD_LObjSetColor(lobj, color0);
            pos0.x *= scale;
            pos0.y *= scale;
            pos0.z *= scale;
            HSD_LObjSetPosition(lobj, &pos0);
            pos1.x *= scale;
            pos1.y *= scale;
            pos1.z *= scale;
            HSD_LObjSetInterest(lobj, &pos1);
            HSD_LObjSetSpot(lobj, 45.0f, 3);
            HSD_LObjSetDistAttn(lobj, 600.0f * scale, 0.99f, 3);
            break;
        case 2:
            if (lpos.y > 500.0f) {
                pos2 = base[3];
                color1.r = 0xFD;
                color1.g = 0xFD;
                color1.b = 0xBF;
                color1.a = 0xFF;
                HSD_LObjSetColor(lobj, color1);
                pos2.x *= scale;
                pos2.y *= scale;
                pos2.z *= scale;
                HSD_LObjSetPosition(lobj, &pos2);
                HSD_LObjSetDistAttn(lobj, 1000.0f * scale, 0.03f, 3);
            } else if (lpos.y < 500.0f) {
                pos3 = base[4];
                color2.r = 0x00;
                color2.g = 0x00;
                color2.b = 0xF7;
                color2.a = 0xFF;
                HSD_LObjSetColor(lobj, color2);
                pos3.x *= scale;
                pos3.y *= scale;
                pos3.z *= scale;
                HSD_LObjSetPosition(lobj, &pos3);
                HSD_LObjSetDistAttn(lobj, 400.0f * scale, 0.03f, 3);
            }
            break;
        }
    }
}

DynamicsDesc* grZebesRoute_8020B854(enum_t arg)
{
    return false;
}

bool grZebesRoute_8020B85C(Vec3* arg, int arg0, HSD_JObj* jobj)
{
    return true;
}
