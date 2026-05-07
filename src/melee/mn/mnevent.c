#include "mnevent.h"

#include "db/db.h"
#include "gm/gm_1601.h"
#include "gm/gm_1BA8.h"
#include "gm/gmmain_lib.h"
#include "lb/lb_00F9.h"
#include "lb/lbarchive.h"
#include "lb/lbaudio_ax.h"
#include "mn/inlines.h"
#include "mn/mnmain.h"
#include "mn/types.h"

#include <baselib/gobj.h>
#include <baselib/gobjgxlink.h>
#include <baselib/gobjobject.h>
#include <baselib/gobjplink.h>
#include <baselib/gobjproc.h>
#include <baselib/gobjuserdata.h>
#include <baselib/jobj.h>
#include <baselib/memory.h>
#include <baselib/sislib.h>

s32 mnEvent_8024CE74(void)
{
    int count = 0;
    int i;
    PAD_STACK(8);

    if (g_debugLevel > 2) {
        return 0x2A;
    }

    count = 0;
    for (i = 0; i < 0x33; i++) {
        if (gmMainLib_8015CEFC(i)) {
            count += 1;
        }
    }

    if (count <= 5) {
        return 1;
    }
    if (count <= 9) {
        return 6;
    }
    if (count <= 0xF) {
        return 0xB;
    }
    if (count <= 0x15) {
        return 0x10;
    }
    if (count <= 0x1A) {
        return 0x14;
    }
    if (count >= 0x32) {
        if (gm_80162EC8()) {
            return 0x2A;
        }
        return 0x29;
    }
    if (gm_80164840(0x14) && gm_80164840(7) && gm_80164840(0xF) &&
        gm_80164840(0x15))
    {
        if (gm_80164840(0xA) && gm_80164840(9) && gm_80164840(3) &&
            gm_80164840(0x18) && gm_80164840(0x19) && gm_80164840(0x16) &&
            gm_80164840(0x17))
        {
            return 0x29;
        }
        return 0x1E;
    }
    return 0x15;
}

static AnimLoopSettings mnEvent_803EF740 = { 0, 0, -0.1f };
static AnimLoopSettings mnEvent_803EF74C = { 0, 0, -0.1f };
static AnimLoopSettings mnEvent_803EF758 = { 0, 199.0f, 0 };

void mnEvent_8024D4E0(HSD_JObj* jobj, Vec3* translate)
{
    HSD_JObjSetTranslate(jobj, translate);
}

static GXColor mnEvent_804D5028 = { 0xCA, 0xBC, 0x9F, 0xFF };
static GXColor mnEvent_804D502C = { 0, 0, 0, 0xFF };
static char mnEvent_803EF7A0[] = { 0x81, 0x7C, 0x81, 0x7C, 0x3A,
                                   0x81, 0x7C, 0x81, 0x7C, 0x20,
                                   0x81, 0x7C, 0x81, 0x7C, 0 };
static char mnEvent_804D5044[] = { 0x81, 0x7C, 0, 0 };

void mnEvent_8024D5B0(HSD_GObj* gobj, s32 idx)
{
    int sp18;
    int sp14;
    int sp10;
    HSD_Text* text;
    u32 val;
    MnEventData* data = gobj->user_data;

    if (data->name_text != NULL) {
        HSD_SisLib_803A5CC4(data->name_text);
    }
    text = HSD_SisLib_803A6754(0, 1);
    data->name_text = text;
    text->pos_x = 3.8f;
    text->pos_y = 6.9f;
    text->pos_z = 17.0f;
    text->text_color = mnEvent_804D502C;
    text->default_alignment = 2;
    text->font_size.x = 0.03f;
    text->font_size.y = 0.03f;
    val = gmMainLib_8015CF5C((u8) gm_801BEBC0((u8) idx));
    if ((u8) gm_801BEB8C((u8) gm_801BEBC0((u8) idx)) != 0) {
        if (gmMainLib_8015CEFC((u8) gm_801BEBC0((u8) idx)) != 0) {
            mn_8022EA78((char*) &sp18, 2, ((val / 60) / 60) % 60);
            mn_8022EA78((char*) &sp14, 2, (val / 60) % 60);
            mn_8022EA78((char*) &sp10, 2,
                        (u32) (s32) ((99.0f * (f32) (val % 60)) / 59.0f));
            HSD_SisLib_803A6B98(text, 0.0f, 0.0f, "%s:%s %s", &sp18, &sp14,
                                &sp10);
        } else {
            text->pos_x = 4.25f;
            text->pos_y = 6.9f;
            text->pos_z = 17.0f;
            text->default_kerning = 1;
            HSD_SisLib_803A6B98(text, 0.0f, 0.0f, mnEvent_803EF7A0, &sp18,
                                &sp14, &sp10);
        }
    } else if (gmMainLib_8015CEFC((u8) gm_801BEBC0((u8) idx)) != 0) {
        HSD_SisLib_803A6B98(text, 0.0f, 0.0f, "%d", val);
    } else {
        text->default_kerning = 1;
        HSD_SisLib_803A6B98(text, 0.0f, 0.0f, mnEvent_804D5044);
    }
}

void fn_8024E1B4(HSD_GObj* gobj)
{
    int i;
    MnEventData* data = gobj->user_data;
    if (mn_8022EC18(gobj->hsd_obj, &mnEvent_803EF74C, 0x80) >=
        mnEvent_803EF74C.end_frame)
    {
        for (i = 0; i < 9; i++) {
            if (data->gobjs[i] != NULL) {
                HSD_GObjPLink_80390228(data->gobjs[i]);
                data->gobjs[i] = NULL;
            }
            if (data->texts[i] != NULL) {
                HSD_SisLib_803A5CC4(data->texts[i]);
                data->texts[i] = NULL;
            }
            if (data->icons[i] != NULL) {
                HSD_SisLib_803A5CC4(data->icons[i]);
                data->icons[i] = NULL;
            }
        }
        HSD_GObjPLink_80390228(gobj);
    }
}

void fn_8024E2A0(HSD_GObj* gobj)
{
    HSD_GObjProc* proc;
    HSD_JObj* jobj;
    HSD_JObj* tree;
    MnEventData* data = gobj->user_data;
    PAD_STACK(8);

    tree = gobj->hsd_obj;

    if (mn_804A04F0.cur_menu != 7) {
        HSD_GObjProc_8038FE24(HSD_GObj_804D7838);
        proc = HSD_GObj_SetupProc(gobj, fn_8024E1B4, 0);
        proc->flags_3 = HSD_GObj_804D783C;
        HSD_SisLib_803A5CC4(data->desc_text);
        HSD_SisLib_803A5CC4(data->name_text);
    } else {
        lb_80011E24(tree, &jobj, 1, -1);
        mn_8022ED6C(jobj, &mnEvent_803EF758);
    }
}

void fn_8024E34C(HSD_GObj* gobj)
{
    HSD_GObjProc* proc;
    HSD_JObj* tree = gobj->hsd_obj;
    MnEventData* data = gobj->user_data;
    PAD_STACK(16);

    if (mn_804A04F0.cur_menu != 7) {
        HSD_GObjProc_8038FE24(HSD_GObj_804D7838);
        proc = HSD_GObj_SetupProc(gobj, fn_8024E1B4, 0);
        proc->flags_3 = HSD_GObj_804D783C;
        HSD_SisLib_803A5CC4(data->desc_text);
        HSD_SisLib_803A5CC4(data->name_text);
    } else {
        float frame = mn_8022EC18(tree, &mnEvent_803EF740, 0x80);
        if (frame == mnEvent_803EF740.end_frame) {
            HSD_GObjProc_8038FE24(HSD_GObj_804D7838);
            proc = HSD_GObj_SetupProc(gobj, fn_8024E2A0, 0);
            proc->flags_3 = HSD_GObj_804D783C;
        }
    }
}

void mnEvent_8024D014(HSD_GObj* gobj)
{
    HSD_JObj* jobj;
    MnEventData* data = gobj->user_data;
    HSD_JObj* tree = gobj->hsd_obj;
    PAD_STACK(8);

    lb_80011E24(tree, &jobj, 3, -1);
    if (data->first_event == 0) {
        HSD_JObjSetFlagsAll(jobj, JOBJ_HIDDEN);
    } else {
        HSD_JObjClearFlagsAll(jobj, JOBJ_HIDDEN);
    }

    lb_80011E24(tree, &jobj, 2, -1);
    if (data->first_event == mnEvent_8024CE74()) {
        HSD_JObjSetFlagsAll(jobj, JOBJ_HIDDEN);
    } else {
        HSD_JObjClearFlagsAll(jobj, JOBJ_HIDDEN);
    }
}

void mnEvent_8024D0CC(HSD_GObj* gobj, s32 event)
{
    HSD_JObj* tree = gobj->hsd_obj;
    HSD_JObj* jobj;
    f32 frame;
    FORCE_PAD_STACK_4;

    if (event == 0x21) {
        frame = 25.0f;
    } else {
        frame = gm_80164024(event);
    }

    lb_80011E24(tree, &jobj, 4, -1);
    HSD_JObjReqAnimAll(jobj, frame);
    HSD_JObjAnimAll(jobj);
}

void mnEvent_8024D15C(s32 arg0, s32 arg1)
{
    HSD_JObj* jobj_c;
    HSD_JObj* jobj_d;
    Vec3 pos2;
    Vec3 pos;
    HSD_JObj* jobj_b;
    HSD_JObj* jobj_a;
    AnimLoopSettings* base = &mnEvent_803EF740;
    HSD_JObj* jobj = mnEvent_804D6C60->hsd_obj;
    MnEventData* data = mnEvent_804D6C60->user_data;
    s32 slot_off;
    HSD_GObj** gobj_slot;

    lb_80011E24(jobj, &jobj_a, 0xA, -1);
    lb_80011E24(jobj, &jobj_b, 0xC, -1);

    HSD_JObjGetTranslation2(jobj_a, &pos);
    pos.y -= (f32)arg0 * (HSD_JObjGetTranslationY(jobj_b) - HSD_JObjGetTranslationY(jobj_a));

    slot_off = arg0 * 4;
    gobj_slot = (HSD_GObj**)((char*)data + slot_off + 8);
    if (*gobj_slot != NULL) {
        HSD_GObjPLink_80390228(*gobj_slot);
        *gobj_slot = NULL;
    }

    if (gmMainLib_8015CEFC(arg1)) {
        HSD_JObj* jobj2 = mnEvent_804D6C60->hsd_obj;
        lb_80011E24(jobj2, &jobj_c, 0xA, -1);
        lb_80011E24(jobj2, &jobj_d, 0xC, -1);

        HSD_JObjGetTranslation2(jobj_c, &pos2);
        pos2.y += (f32)arg0 * (HSD_JObjGetTranslationY(jobj_d) - HSD_JObjGetTranslationY(jobj_c));

        {
            HSD_GObj* new_gobj = GObj_Create(6, 7, 0x80);
            HSD_JObj* new_jobj = HSD_JObjLoadJoint(mnEvent_804A0908);
            HSD_GObjObject_80390A70(new_gobj, HSD_GObj_804D7849, new_jobj);
            GObj_SetupGXLink(new_gobj, HSD_GObj_JObjCallback, 4, 0x80);
            mnEvent_8024D4E0(new_jobj, &pos2);
            *gobj_slot = new_gobj;
        }
    }

    {
        HSD_Text** text_slot = (HSD_Text**)((char*)data + slot_off + 0x2C);
        if (*text_slot != NULL) {
            HSD_SisLib_803A5CC4(*text_slot);
        }
        {
            HSD_Text* text = HSD_SisLib_803A6754(0, 1);
            *text_slot = text;
            text->font_size.x = 0.035f;
            text->font_size.y = 0.035f;
            text->pos_x = pos.x + *(f32*)((char*)base + 0x24);
            text->pos_y = pos.y + *(f32*)((char*)base + 0x28);
            text->pos_z = 17.0f;
            text->default_kerning = 1;
            text->text_color = mnEvent_804D5028;
            HSD_SisLib_803A6B98(text, 0.0f, 0.0f, (char*)base + 0x3C, arg1 + 1);
        }
    }

    {
        HSD_Text** icon_slot = (HSD_Text**)((char*)data + slot_off + 0x50);
        if (*icon_slot != NULL) {
            HSD_SisLib_803A5CC4(*icon_slot);
        }
        {
            HSD_Text* icon = HSD_SisLib_803A5ACC(0, 1,
                pos.x + *(f32*)((char*)base + 0x30),
                pos.y + *(f32*)((char*)base + 0x34),
                17.0f, 364.68332f, 38.38772f);
            *icon_slot = icon;
            icon->font_size.x = 0.035f;
            icon->font_size.y = 0.035f;
            HSD_SisLib_803A6368(icon, ((gm_801BEBA8((u8)arg1) * 2) & 0x1FE) + 0x154);
        }
    }
}

void mnEvent_8024D7E0(HSD_GObj* gobj, s32 idx)
{
    MnEventData* data = gobj->user_data;
    HSD_Text* text;
    s32 sis_idx;
    PAD_STACK(8);

    if (data->desc_text != NULL) {
        HSD_SisLib_803A5CC4(data->desc_text);
    }

    sis_idx = (idx * 2) + 0x155;
    text =
        HSD_SisLib_803A5ACC(0, 1, -9.5f, 8.0f, 17.0f, 364.68332f, 38.38772f);
    data->desc_text = text;
    text->font_size.x = 0.0521f;
    text->font_size.y = 0.0521f;
    HSD_SisLib_803A6368(text, sis_idx);
}

void mnEvent_8024E420(MnEventData* data, s32 event_idx)
{
    s32 max_events;
    int i;

    max_events = mnEvent_8024CE74();

    if (event_idx < max_events) {
        data->first_event = event_idx;
        data->page = 0;
    } else {
        data->first_event = max_events;
        data->page = event_idx - max_events;
    }

    data->desc_text = NULL;
    data->name_text = NULL;

    for (i = 0; i < 9; i++) {
        data->gobjs[i] = NULL;
        data->texts[i] = NULL;
        data->icons[i] = NULL;
    }
}

void fn_8024D864(HSD_GObj* gobj)
{
    MnEventData* data;
    HSD_GObj* target;
    u64 input;
    s32 i;
    PAD_STACK(8);

    if (mn_804D6BC8.cooldown != 0) {
        Menu_DecrementAnimTimer();
        return;
    }
    input = Menu_GetAllInputs();
    if ((input & 0x20) != 0) {
        sfxBack();
        mn_804A04F0.entering_menu = 0;
        mn_80229894(1, 1U, 3);
        return;
    }
    if (mnEvent_804D6C64 != 0) {
        mnEvent_804D6C64--;
        return;
    }
    if (mnEvent_804D6C60 == NULL) {
        mnEvent_8024E524(mnEvent_804D6C65);
    }
    data = mnEvent_804D6C60->user_data;
    if ((input & 0x10) != 0) {
        sfxForward();
        gm_801BEB74(data->first_event + data->page);
        gm_801677E8(mn_802295AC());
        mn_80229860(0x2B);
        return;
    }
    if ((input & 0x400) != 0) {
        HSD_JObj* jobj_x;
        s32 max_events = mnEvent_8024CE74();
        s32 first = data->first_event;
        u8 idx;
        if (first + 9 >= max_events && first == max_events) {
            return;
        }
        sfxMove();
        if (data->first_event + 9 < max_events) {
            data->first_event += 9;
        } else {
            data->first_event = max_events;
        }
        first = data->first_event;
        for (i = 0; i < 9; i++) {
            mnEvent_8024D15C(i, first + i);
        }
        idx = gm_801BEBA8(data->first_event + data->page);
        target = mnEvent_804D6C60;
        mnEvent_8024D0CC(target, (s8) gm_801BEBF8(idx));
        mnEvent_8024D7E0(target, idx);
        mnEvent_8024D5B0(target, idx);
        lb_80011E24(target->hsd_obj, &jobj_x, 9, -1);
        HSD_JObjReqAnimAll(jobj_x, gm_801BEB8C(gm_801BEBC0(idx)));
        HSD_JObjAnimAll(jobj_x);
        mnEvent_8024D014(target);
    } else if ((input & 0x800) != 0) {
        HSD_JObj* jobj_y;
        s32 first = data->first_event;
        u8 idx;
        if (first - 9 < 0 && first == 0) {
            return;
        }
        sfxMove();
        if (data->first_event - 9 >= 0) {
            data->first_event -= 9;
        } else {
            data->first_event = 0;
        }
        first = data->first_event;
        for (i = 0; i < 9; i++) {
            mnEvent_8024D15C(i, first + i);
        }
        idx = gm_801BEBA8(data->first_event + data->page);
        target = mnEvent_804D6C60;
        mnEvent_8024D0CC(target, (s8) gm_801BEBF8(idx));
        mnEvent_8024D7E0(target, idx);
        mnEvent_8024D5B0(target, idx);
        lb_80011E24(target->hsd_obj, &jobj_y, 9, -1);
        HSD_JObjReqAnimAll(jobj_y, gm_801BEB8C(gm_801BEBC0(idx)));
        HSD_JObjAnimAll(jobj_y);
        mnEvent_8024D014(target);
    } else if ((input & 0x1) != 0) {
        if (data->page != 0) {
            HSD_JObj* jobj_top;
            HSD_JObj* jobj_bot;
            HSD_JObj* jobj_cur;
            HSD_JObj* jobj_anim;
            HSD_JObj* tree;
            u8 page_val;
            u8 idx;
            f32 ay, by;
            sfxMove();
            data->page--;
            page_val = data->page;
            tree = mnEvent_804D6C60->hsd_obj;
            lb_80011E24(tree, &jobj_top, 0xA, -1);
            lb_80011E24(tree, &jobj_bot, 0xC, -1);
            ay = HSD_JObjGetTranslationY(jobj_top);
            by = HSD_JObjGetTranslationY(jobj_bot);
            lb_80011E24(tree, &jobj_cur, 0xB, -1);
            HSD_JObjSetTranslateY(jobj_cur, page_val * (by - ay));
            idx = gm_801BEBA8(data->first_event + data->page);
            target = mnEvent_804D6C60;
            mnEvent_8024D0CC(target, (s8) gm_801BEBF8(idx));
            mnEvent_8024D7E0(target, idx);
            mnEvent_8024D5B0(target, idx);
            lb_80011E24(target->hsd_obj, &jobj_anim, 9, -1);
            HSD_JObjReqAnimAll(jobj_anim, gm_801BEB8C(gm_801BEBC0(idx)));
            HSD_JObjAnimAll(jobj_anim);
            mnEvent_8024D014(target);
            return;
        }
        if (data->first_event != 0) {
            HSD_JObj* jobj_anim;
            s32 first;
            u8 idx;
            sfxMove();
            data->first_event--;
            first = data->first_event;
            for (i = 0; i < 9; i++) {
                mnEvent_8024D15C(i, first + i);
            }
            idx = gm_801BEBA8(data->first_event + data->page);
            target = mnEvent_804D6C60;
            mnEvent_8024D0CC(target, (s8) gm_801BEBF8(idx));
            mnEvent_8024D7E0(target, idx);
            mnEvent_8024D5B0(target, idx);
            lb_80011E24(target->hsd_obj, &jobj_anim, 9, -1);
            HSD_JObjReqAnimAll(jobj_anim, gm_801BEB8C(gm_801BEBC0(idx)));
            HSD_JObjAnimAll(jobj_anim);
            mnEvent_8024D014(target);
        }
    } else if ((input & 0x2) != 0) {
        if (data->page < 8) {
            HSD_JObj* jobj_top;
            HSD_JObj* jobj_bot;
            HSD_JObj* jobj_cur;
            HSD_JObj* jobj_anim;
            HSD_JObj* tree;
            u8 page_val;
            u8 idx;
            f32 ay, by;
            sfxMove();
            data->page++;
            page_val = data->page;
            tree = mnEvent_804D6C60->hsd_obj;
            lb_80011E24(tree, &jobj_top, 0xA, -1);
            lb_80011E24(tree, &jobj_bot, 0xC, -1);
            ay = HSD_JObjGetTranslationY(jobj_top);
            by = HSD_JObjGetTranslationY(jobj_bot);
            lb_80011E24(tree, &jobj_cur, 0xB, -1);
            HSD_JObjSetTranslateY(jobj_cur, page_val * (by - ay));
            idx = gm_801BEBA8(data->first_event + data->page);
            target = mnEvent_804D6C60;
            mnEvent_8024D0CC(target, (s8) gm_801BEBF8(idx));
            mnEvent_8024D7E0(target, idx);
            mnEvent_8024D5B0(target, idx);
            lb_80011E24(target->hsd_obj, &jobj_anim, 9, -1);
            HSD_JObjReqAnimAll(jobj_anim, gm_801BEB8C(gm_801BEBC0(idx)));
            HSD_JObjAnimAll(jobj_anim);
            mnEvent_8024D014(target);
            return;
        }
        if (data->first_event < mnEvent_8024CE74()) {
            HSD_JObj* jobj_anim;
            s32 first;
            u8 idx;
            sfxMove();
            data->first_event++;
            first = data->first_event;
            for (i = 0; i < 9; i++) {
                mnEvent_8024D15C(i, first + i);
            }
            idx = gm_801BEBA8(data->first_event + data->page);
            target = mnEvent_804D6C60;
            mnEvent_8024D0CC(target, (s8) gm_801BEBF8(idx));
            mnEvent_8024D7E0(target, idx);
            mnEvent_8024D5B0(target, idx);
            lb_80011E24(target->hsd_obj, &jobj_anim, 9, -1);
            HSD_JObjReqAnimAll(jobj_anim, gm_801BEB8C(gm_801BEBC0(idx)));
            HSD_JObjAnimAll(jobj_anim);
            mnEvent_8024D014(target);
        }
    }
}

void mnEvent_8024E524(s32 event_idx)
{
    HSD_JObj* sp1C;
    HSD_JObj* sp20;
    HSD_JObj* sp24;
    HSD_JObj* sp28;
    HSD_GObj* gobj;
    HSD_JObj* jobj;
    MnEventData* data;
    char* base = (char*) &mnEvent_803EF740;
    void** arr = mnEvent_804A08F8;
    HSD_GObj* target;
    u8 page;
    u8 idx;
    s32 first_event;
    s32 i;
    f32 ay, by;

    gobj = GObj_Create(6, 7, 0x80);
    mnEvent_804D6C60 = gobj;
    jobj = HSD_JObjLoadJoint(arr[0]);
    HSD_GObjObject_80390A70(gobj, HSD_GObj_804D7849, jobj);
    GObj_SetupGXLink(gobj, HSD_GObj_JObjCallback, 4, 0x80);
    HSD_JObjAddAnimAll(jobj, arr[1], arr[2], arr[3]);
    HSD_JObjReqAnimAll(jobj, 0.0f);
    HSD_JObjAnimAll(jobj);

    data = HSD_MemAlloc(0x7C);
    if (data == NULL) {
        OSReport(base + 0x70);
        __assert(base + 0x88, 0x39B, base + 0x94);
    }
    mnEvent_8024E420(data, event_idx);
    GObj_InitUserData(gobj, 0, HSD_Free, data);

    page = data->page;
    lb_80011E24(jobj, &sp20, 0xA, -1);
    lb_80011E24(jobj, &sp24, 0xC, -1);
    ay = HSD_JObjGetTranslationY(sp20);
    by = HSD_JObjGetTranslationY(sp24);
    lb_80011E24(jobj, &sp28, 0xB, -1);
    HSD_JObjSetTranslateY(sp28, page * (by - ay));

    HSD_GObj_SetupProc(gobj, fn_8024E34C, 0)->flags_3 = HSD_GObj_804D783C;
    first_event = data->first_event;
    for (i = 0; i < 9; i++) {
        mnEvent_8024D15C(i, first_event + i);
    }

    idx = gm_801BEBA8(data->first_event + data->page);
    target = mnEvent_804D6C60;
    mnEvent_8024D0CC(target, (s8) gm_801BEBF8(idx));
    mnEvent_8024D7E0(target, idx);
    mnEvent_8024D5B0(target, idx);
    lb_80011E24(target->hsd_obj, &sp1C, 9, -1);
    HSD_JObjReqAnimAll(sp1C, gm_801BEB8C(gm_801BEBC0(idx)));
    HSD_JObjAnimAll(sp1C);
    mnEvent_8024D014(target);
}

void mnEvent_8024E838(int event_idx, int first_time)
{
    HSD_GObjProc* proc;
    void** arr = mnEvent_804A08F8;
    char* base = (char*) &mnEvent_803EF740;

    mn_804D6BC8.cooldown = 5;
    mn_804A04F0.prev_menu = mn_804A04F0.cur_menu;
    mn_804A04F0.cur_menu = 7;
    mn_804A04F0.hovered_selection = 0;
    mnEvent_804D6C65 = event_idx;

    if (first_time) {
        mnEvent_804D6C64 = 0x14;
    } else {
        mnEvent_804D6C64 = 0;
    }

    mnEvent_804D6C60 = NULL;
    {
        HSD_Archive* archive = mn_804D6BB8;
        lbArchive_LoadSections(archive, arr, base + 0xA0, arr + 1, base + 0xB8,
                               arr + 2, base + 0xD4, arr + 3, base + 0xF4,
                               arr + 4, base + 0x118, 0);
    }

    if (first_time == 0) {
        mnEvent_8024E524(event_idx);
    }

    proc = HSD_GObj_SetupProc(GObj_Create(0, 1, 0x80), fn_8024D864, 0);
    proc->flags_3 = HSD_GObj_804D783C;
}
