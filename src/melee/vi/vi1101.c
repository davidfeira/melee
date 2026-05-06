#include "vi1101.h"

#include "vi.h"

#include "ef/efasync.h"
#include "ef/eflib.h"
#include "gm/gm_1601.h"
#include "gm/gm_1A45.h"
#include "lb/lb_00F9.h"
#include "lb/lbarchive.h"
#include "lb/lbaudio_ax.h"
#include "lb/lbshadow.h"
#include "sc/types.h"
#include "vi/types.h"

#include <baselib/aobj.h>
#include <baselib/cobj.h>
#include <baselib/gobj.h>
#include <baselib/gobjgxlink.h>
#include <baselib/gobjobject.h>
#include <baselib/gobjproc.h>
#include <baselib/jobj.h>

static SceneDesc* un_804D6FC0;
static SceneDesc* un_804D6FC4;
static HSD_Archive* un_804D6FC8;
static HSD_Archive* un_804D6FCC;

/// #un_8031F294

void fn_8031F548(HSD_GObj* gobj)
{
    HSD_JObjAnimAll(GET_JOBJ(gobj));
}

static void fn_8031F56C(HSD_GObj* gobj)
{
    HSD_CObj* cobj;
    char pad[8];

    lbShadow_8000F38C(0);
    cobj = gobj->hsd_obj;
    if (HSD_CObjSetCurrent(cobj) != 0) {
        u8* colors = (u8*) &un_804D5B08;
        HSD_SetEraseColor(colors[0], colors[1], colors[2], colors[3]);
        cobj = gobj->hsd_obj;
        HSD_CObjEraseScreen(cobj, 1, 0, 1);
        vi_8031CA04(gobj);
        gobj->gxlink_prios = 0x281;
        HSD_GObj_80390ED0(gobj, 7);
        HSD_CObjEndCurrent();
    }
}

void fn_8031F600(HSD_GObj* gobj)
{
    HSD_CObj* cobj = GET_COBJ(gobj);

    HSD_CObjAnim(cobj);

    if (170.0f == cobj->aobj->curr_frame) {
        if (gm_80164840(7) != 0) {
            vi_8031C9B4(0xD, 0);
            lbAudioAx_800237A8(0x209, 0x7F, 0x40);
        }
    }

    if (190.0f == cobj->aobj->curr_frame) {
        vi_8031C9B4(0xD, 0);
        lbAudioAx_800237A8(0x209, 0x7F, 0x40);
    }

    if (241.0f == cobj->aobj->curr_frame) {
        if (gm_80164840(7) != 0) {
            lbAudioAx_800237A8(0x20A, 0x7F, 0x40);
        }
    }

    if (271.0f == cobj->aobj->curr_frame) {
        lbAudioAx_800237A8(0x20A, 0x7F, 0x40);
    }

    if (cobj->aobj->curr_frame == cobj->aobj->end_frame) {
        lb_800145F4();
        gm_801A4B60();
    }
}

void un_8031F714_OnEnter(void* arg)
{
    int i;
    HSD_CObj* cobj;
    HSD_GObj* cam_gobj;
    HSD_GObj* light_gobj;
    HSD_GObj* model_gobj;
    HSD_JObj* jobj;
    SceneDesc* scene;
    ViCharaDesc* desc = (ViCharaDesc*) arg;
    u8 char_index;

    lbAudioAx_800236DC();
    efLib_Init();
    efAsync_LoadSync(0);
    lbAudioAx_80023F28(0x55);
    lbAudioAx_80024E50(1);
    char_index = desc->p1_char_index;
    un_804D6FCC = lbArchive_LoadSymbols("Vi1101.dat", &un_804D6FC0,
                                        "visual1101Scene", &un_804D6FC4,
                                        "visual1101Cam2Scene", 0);
    un_804D6FC8 = lbArchive_LoadSymbols(viGetCharAnimByIndex(char_index), 0);

    light_gobj = GObj_Create(0xB, 3, 0);
    HSD_GObjObject_80390A70(light_gobj, HSD_GObj_804D784A,
                            lb_80011AC4(un_804D6FC0->lights));
    GObj_SetupGXLink(light_gobj, HSD_GObj_LObjCallback, 0, 0);

    if (gm_80164840(7) != 0) {
        scene = un_804D6FC0;
    } else {
        scene = un_804D6FC4;
    }

    cam_gobj = GObj_Create(0x13, 0x14, 0);
    cobj = lb_80013B14((HSD_CameraDescPerspective*) scene->cameras->desc);
    HSD_GObjObject_80390A70(cam_gobj, HSD_GObj_804D784B, cobj);
    GObj_SetupGXLinkMax(cam_gobj, (GObj_RenderFunc) fn_8031F56C, 5);
    HSD_CObjAddAnim(cobj, scene->cameras->anims[0]);
    HSD_CObjReqAnim(cobj, 0.0f);
    HSD_CObjAnim(cobj);
    HSD_GObj_SetupProc(cam_gobj, fn_8031F600, 0);

    for (i = 0; un_804D6FC0->models[i] != NULL; i++) {
        model_gobj = GObj_Create(0xE, 0xF, 0);
        jobj = HSD_JObjLoadJoint(un_804D6FC0->models[i]->joint);
        HSD_GObjObject_80390A70(model_gobj, HSD_GObj_804D7849, jobj);
        GObj_SetupGXLink(model_gobj, HSD_GObj_JObjCallback, 9, 0);
        gm_8016895C(jobj, un_804D6FC0->models[i], 0);
        HSD_JObjReqAnimAll(jobj, 0.0f);
        HSD_JObjAnimAll(jobj);
        HSD_GObj_SetupProc(model_gobj, fn_8031F548, 0x17);
    }

    un_8031F294(desc->p1_char_index, desc->p1_costume_index);
    lbAudioAx_80024E50(0);
}

void un_8031F960_OnFrame(void)
{
    vi_8031CAAC();
}
