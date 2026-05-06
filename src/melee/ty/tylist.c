#include "tylist.h"

#include "gm/gmmain_lib.h"
#include "if/textlib.h"
#include "lb/lb_00B0.h"
#include "lb/lbarchive.h"
#include "lb/lblanguage.h"
#include "ty/toy.h"
#include "ty/types.h"

#include <m2c_macros.h>
#include <baselib/archive.h>
#include <baselib/cobj.h>
#include <baselib/controller.h>
#include <baselib/displayfunc.h>
#include <baselib/dobj.h>
#include <baselib/fog.h>
#include <baselib/gobj.h>
#include <baselib/gobjgxlink.h>
#include <baselib/gobjobject.h>
#include <baselib/gobjplink.h>
#include <baselib/gobjproc.h>
#include <baselib/mobj.h>
#include <baselib/sislib.h>
#include <baselib/tobj.h>
#include <baselib/video.h>

typedef struct {
    u8 pad[0x28];
    HSD_CObj* cobj;
} TyListData;

typedef struct {
    u8 pad[0x4E8];
    u8* digits;
} SisFontData;

typedef struct {
    HSD_GObj* gobj;
    u8 pad[0x4C];
    void* data;
} TyArchiveData;

void un_803124BC(void)
{
    u16* table1;
    s16* list;
    u16* table2;
    s32 i;

    table1 = gmMainLib_8015CC78();
    table2 = gmMainLib_8015CC84();

    if (un_804D6ED0 == NULL) {
        char* archiveName;
        if (lbLang_IsSavedLanguageJP()) {
            archiveName = "TyDatai.dat";
        } else {
            archiveName = "TyDatai.usd";
        }
        un_804D6ED0 = lbArchive_LoadSymbols(
            archiveName, &un_804D6EC4, "tyInitModelTbl", &un_804D6EC0,
            "tyInitModelDTbl", &un_804D6EBC, "tyModelSortTbl", &un_804D6EB8,
            "tyExpDifferentTbl", &un_804D6EB4, "tyNoGetUsTbl", &un_804D6EB0,
            "tyDisplayModelTbl", &un_804D6EAC, "tyDisplayModelUsTbl", NULL);
    }

    i = 0;
loop: {
    s32 skip;
    s16 val;

    list = un_804D6EB4;
    if (lbLang_IsSettingUS()) {
        while ((val = *list) != -1) {
            if (val == i) {
                skip = 0;
                goto check;
            }
            list++;
        }
    }
    skip = 1;
check:
    if (skip != 0 && (s32) un_803060BC(i, 6) == 2) {
        *table1 |= 0x4000;
    }
}
    i++;
    table1++;
    if (i < 0x125) {
        goto loop;
    }

    *table2 |= 4;
    un_804A284C[3] |= 4;
}

void un_8031263C(void)
{
    s32 i;
    u16* table1;
    u16* table2;

    ((TyModeState*) un_804A284C)->x4 = 0;
    table1 = gmMainLib_8015CC78();
    table2 = gmMainLib_8015CC84();

    if (un_804D6ED0 == NULL) {
        char* archiveName;
        if (lbLang_IsSavedLanguageJP()) {
            archiveName = "TyDatai.dat";
        } else {
            archiveName = "TyDatai.usd";
        }
        un_804D6ED0 = lbArchive_LoadSymbols(
            archiveName, &un_804D6EC4, "tyInitModelTbl", &un_804D6EC0,
            "tyInitModelDTbl", &un_804D6EBC, "tyModelSortTbl", &un_804D6EB8,
            "tyExpDifferentTbl", &un_804D6EB4, "tyNoGetUsTbl", &un_804D6EB0,
            "tyDisplayModelTbl", &un_804D6EAC, "tyDisplayModelUsTbl", NULL);
    }

    i = 0;
    do {
        if (un_80304CC8(i) != 0) {
            if ((s32) un_803060BC(i, 6) == 2) {
                *table1 |= 0x4000;
            }
        }
        i++;
        table1++;
    } while (i < 0x125);

    *table2 |= 4;
    un_804A284C[3] |= 4;

    if (un_804D6ECC == NULL) {
        un_804D6ECC = lbArchive_LoadSymbols(str_TyDataf_dat, &un_804D6EA8,
                                            str_tyModelFileTbl, &un_804D6EA4,
                                            str_tyModelFileUsTbl, NULL);
    }

    un_8031234C(0);
}
void un_803127D4(void)
{
    un_804D6ED0 = NULL;
    un_804D6EC4 = NULL;
    un_804D6EC0 = NULL;
    un_804D6EBC = NULL;
    un_804D6EB8 = NULL;
    un_804D6EB4 = NULL;
    un_804D6EB0 = NULL;
    un_804D6EAC = NULL;
    un_804D6ECC = NULL;
    un_804D6EA8 = NULL;
    un_804D6EA4 = NULL;
    un_804D6EC8 = NULL;
    memzero(&un_804A2AA8, sizeof(ToyAnimState));
}

/// Formats a number into a string buffer using digit glyphs from the font.
char* un_80312834(char* buf, u32 num)
{
    u8* lookup = ((SisFontData*) HSD_SisLib_804D1124[0])->digits;
    u32 idx;
    u32 original = num;

    if (num >= 100) {
        idx = (num / 100) * 2;
        *buf++ = lookup[idx];
        *buf++ = lookup[idx + 1];
        num = num % 100;
    }

    if (num >= 10) {
        idx = (num / 10) * 2;
        *buf++ = lookup[idx];
        *buf++ = lookup[idx + 1];
        num = num % 10;
    } else if (original >= 100) {
        *buf++ = lookup[0];
        *buf++ = lookup[1];
    }

    idx = num * 2;
    *buf++ = lookup[idx];
    *buf++ = lookup[idx + 1];
    *buf = 0;
    return buf;
}

extern f32 un_804DDE28;
extern f32 un_804DDE2C;
extern f32 un_804DDE30;
extern f32 un_804DDE34;
extern f32 un_804DDE38;
extern f32 un_804DDE3C;
extern f32 un_804DDE40;
extern GXColor lb_804D3760;
extern GXColor lb_804D3764;

typedef struct TyListRow {
    /* 0x00 */ u8 pad_0[0xC];
    /* 0x0C */ HSD_JObj* jobj;
    /* 0x10 */ u8 pad_10[0x18 - 0x10];
    /* 0x18 */ HSD_Text* text0;
    /* 0x1C */ HSD_Text* text1;
    /* 0x20 */ HSD_Text* text2;
    /* 0x24 */ s8 x24;
    /* 0x25 */ u8 pad_25;
    /* 0x26 */ s16 idx;
    /* 0x28 */ s32 x28;
    /* 0x2C */ u8 pad_2C[0x30 - 0x2C];
    /* 0x30 */ f32 x30;
} TyListRow;

void un_80312904(void* arg0, s8 arg1)
{
    TyListState* state = (TyListState*) un_804A2AC0;
    TyListRow* row = (TyListRow*) arg0;
    HSD_JObj* jobj;
    HSD_JObj* jobj2;
    HSD_JObj* jobj3;
    f32 f30;
    f32 f29;
    f32 f31;
    s32 skip;
    u8* digits;
    PAD_STACK(0x78);

    if (row->idx == -1) {
        return;
    }

    if (un_GetTrophyTotal() < 0xB) {
        s8 v = row->x24;
        if (v == -1 || v == (s8) state->entryCount - 2) {
            skip = 0;
        } else {
            skip = 1;
        }
    } else {
        skip = 1;
    }

    if (skip == 0) {
        return;
    }

    jobj = row->jobj;
    if (jobj == NULL) {
        __assert("jobj.h", 0x3E1, "jobj");
    }
    f30 = jobj->translate.x - un_804DDE28;
    jobj2 = state->gobj->hsd_obj;
    if (jobj2 == NULL) {
        __assert("jobj.h", 0x3EE, "jobj");
    }
    f29 = (-row->x30 - jobj2->translate.y) - un_804DDE2C;
    jobj3 = state->gobj->hsd_obj;
    if (jobj3 == NULL) {
        __assert("jobj.h", 0x3FB, "jobj");
    }
    f31 = jobj3->translate.z;

    if (arg1 != 0x63) {
        if ((s8) row->x24 == arg1) {
            row->text0->text_color = lb_804D3764;
            row->text1->text_color = lb_804D3764;
            row->text2->text_color = lb_804D3764;
        } else {
            row->text0->text_color = lb_804D3760;
            row->text1->text_color = lb_804D3760;
            row->text2->text_color = lb_804D3760;
        }
    }

    row->text0->pos_x = f30;
    row->text0->pos_y = f29;
    row->text0->pos_z = f31;
    row->text0->font_size.x = un_804DDE30;
    row->text0->font_size.y = un_804DDE34;
    row->text0->default_kerning = 1;
    {
        extern s32 un_803082F8(s16);
        HSD_SisLib_803A6368(row->text0, un_803082F8(row->idx));
    }

    row->text1->pos_x = un_804DDE38 + f30;
    row->text1->pos_y = f29;
    row->text1->pos_z = f31;
    row->text1->font_size.x = un_804DDE30;
    row->text1->font_size.y = un_804DDE34;
    HSD_SisLib_803A6368(row->text1, 0x13B);

    digits = ((u8**) ((char*) HSD_SisLib_804D1124[0] + 0x4B8))[row->x28];
    un_80312834((char*) digits, un_803048C0(un_80308354(row->idx)));

    row->text2->default_alignment = 2;
    row->text2->default_kerning = 1;
    row->text2->pos_x = un_804DDE3C + f30;
    row->text2->pos_y = f29;
    row->text2->pos_z = f31;
    row->text2->font_size.x = un_804DDE40;
    row->text2->font_size.y = un_804DDE34;
    HSD_SisLib_803A6368(row->text2, row->x28 + 0x12E);
}

/// #un_80312BAC

void un_80312E88(TyListArg* arg, float delta)
{
    TyListArg* ptr;
    HSD_JObj* jobj;
    char* data;
    s32 i;
    PAD_STACK(8);

    arg->x30 = arg->x30 + delta;

    if (un_804DDE4C == delta) {
        arg->x30 = arg->x2C;
    } else if (delta < un_804DDE48) {
        if (arg->x30 < arg->x2C) {
            arg->x30 = arg->x2C;
        }
    } else {
        if (arg->x30 > arg->x2C) {
            arg->x30 = arg->x2C;
        }
    }

    ptr = arg;
    data = un_804A2AC0;
    i = 0;
loop:
    if ((jobj = ptr->xC) == NULL) {
        goto next;
    }
    if (i == 2) {
        goto next;
    }
    {
        float pos = arg->x30;
        if (jobj == NULL) {
            __assert(&un_804D5A78, 0x3B3, &un_804D5A80);
        }
        jobj->translate.y = pos;
    }

    if ((jobj->flags & 0x02000000) == 0) {
        if (jobj == NULL) {
            goto skip_dirty;
        }
        if (jobj == NULL) {
            __assert(&un_804D5A78, 0x234, &un_804D5A80);
        }
        {
            u32 flags = jobj->flags;
            s32 skip = 0;
            if ((flags & 0x800000) == 0 && (flags & 0x40)) {
                skip = 1;
            }
            if (skip == 0) {
                HSD_JObjSetMtxDirtySub(jobj);
            }
        }
    }
skip_dirty:

    if (arg->idx == un_GetTrophyTotal() - 1) {
        float pos;
        jobj = ((TyListState*) data)->jobj;
        pos = arg->x30;
        if (jobj == NULL) {
            __assert(&un_804D5A78, 0x3B3, &un_804D5A80);
        }
        jobj->translate.y = pos;

        if ((jobj->flags & 0x02000000) == 0) {
            if (jobj == NULL) {
                goto next;
            }
            if (jobj == NULL) {
                __assert(&un_804D5A78, 0x234, &un_804D5A80);
            }
            {
                u32 flags = jobj->flags;
                s32 skip = 0;
                if ((flags & 0x800000) == 0 && (flags & 0x40)) {
                    skip = 1;
                }
                if (skip == 0) {
                    HSD_JObjSetMtxDirtySub(jobj);
                }
            }
        }
    }

next:
    i = i + 1;
    ptr = (TyListArg*) ((s8*) ptr + 4);
    if (i < 3) {
        goto loop;
    }

    un_80312904(arg, 0x63);
    un_80313464(arg);
}
/// #un_8031305C

void un_80313358(TyListState* state, s8 arg2, s8 arg3, s8 arg4)
{
    int i;

    if (arg2 != -1) {
        state->x29E = arg2;
        state->x2A1 = arg4;
    }

    state->x29F = arg3;
    state->x2A4 = state->x2A8 / (float) arg3;

    if (state->x2A1 == 0) {
        for (i = 0; i < state->entryCount; i++) {
            TyListArg* entry = &state->entries[i];
            TyListArg* sub = entry->x0;
            entry->x2C = sub->x30;
            un_80312904(entry, state->entryCount + 1);
        }
    } else {
        for (i = 0; i < state->entryCount; i++) {
            TyListArg* entry = &state->entries[i];
            TyListArg* sub = entry->x4;
            entry->x2C = sub->x30;
            un_80312904(entry, state->entryCount + 1);
        }
    }
}

void un_80313464(TyListArg* arg)
{
    char* data = un_804A2AC0;
    s32 val;
    PAD_STACK(24);

    val = un_804D6EDC[arg->idx];

    un_803083D8(arg->x14, val);

    if (arg->x10 != NULL) {
        HSD_JObjUnref(arg->x10);
        arg->x10 = NULL;
    }

    if (un_80304924(val) != 0) {
        arg->x10 = un_80313508(((TyListState*) data)->gobj, un_803FE8D0,
                               un_804DDE60, arg->x30, un_804DDE48);
    }
}
HSD_JObj* un_80313508(void* parent, void* symbol, float x, float y, float z)
{
    HSD_JObj* jobj;
    TyArchiveData* archive;
    void* joint;
    PAD_STACK(8);

    archive = un_804D6ED8;
    joint = HSD_ArchiveGetPublicAddress(archive->data, symbol);

    if (joint == NULL) {
        OSPanic(un_803FE8F0, 0x337, un_803FE8FC);
        return NULL;
    }

    jobj = HSD_JObjLoadJoint(joint);

    if (x != un_804DDE48 || y != un_804DDE48 || z != un_804DDE48) {
        // Set X
        if (jobj == NULL) {
            __assert(&un_804D5A78, 0x3A4, &un_804D5A80);
        }
        jobj->translate.x = x;

        if ((jobj->flags & 0x02000000) == 0) {
            if (jobj == NULL) {
                goto skip_x;
            }
            if (jobj == NULL) {
                __assert(&un_804D5A78, 0x234, &un_804D5A80);
            }
            {
                u32 flags = jobj->flags;
                s32 skip = 0;
                if ((flags & 0x800000) == 0 && (flags & 0x40)) {
                    skip = 1;
                }
                if (skip == 0) {
                    HSD_JObjSetMtxDirtySub(jobj);
                }
            }
        }
    skip_x:

        // Set Y
        if (jobj == NULL) {
            __assert(&un_804D5A78, 0x3B3, &un_804D5A80);
        }
        jobj->translate.y = y;

        if ((jobj->flags & 0x02000000) == 0) {
            if (jobj == NULL) {
                goto skip_y;
            }
            if (jobj == NULL) {
                __assert(&un_804D5A78, 0x234, &un_804D5A80);
            }
            {
                u32 flags = jobj->flags;
                s32 skip = 0;
                if ((flags & 0x800000) == 0 && (flags & 0x40)) {
                    skip = 1;
                }
                if (skip == 0) {
                    HSD_JObjSetMtxDirtySub(jobj);
                }
            }
        }
    skip_y:

        // Set Z
        if (jobj == NULL) {
            __assert(&un_804D5A78, 0x3C2, &un_804D5A80);
        }
        jobj->translate.z = z;

        if ((jobj->flags & 0x02000000) == 0) {
            if (jobj == NULL) {
                goto skip_z;
            }
            if (jobj == NULL) {
                __assert(&un_804D5A78, 0x234, &un_804D5A80);
            }
            {
                u32 flags = jobj->flags;
                s32 skip = 0;
                if ((flags & 0x800000) == 0 && (flags & 0x40)) {
                    skip = 1;
                }
                if (skip == 0) {
                    HSD_JObjSetMtxDirtySub(jobj);
                }
            }
        }
    skip_z:;
    }

    if (parent != NULL) {
        HSD_JObj* parentJobj = ((HSD_GObj*) parent)->hsd_obj;
        HSD_JObj* child;
        HSD_JObjAddChild(parentJobj, jobj);
        child = parentJobj->child;
        while (child->next != NULL) {
            child = child->next;
        }
    } else {
        HSD_GObj* gobj;
        gobj = GObj_Create(6, 7, 0);
        HSD_GObjObject_80390A70(gobj, (u8) HSD_GObj_804D7849, jobj);
        GObj_SetupGXLink(gobj, HSD_GObj_JObjCallback, 0x39, 0);
    }

    return jobj;
}

/// #un_80313774

/// #fn_80313BD8

void fn_80313BD8(HSD_GObj* gobj);
extern s32 un_804D6EEC;
extern f32 un_804DDE44;
extern f32 un_804DDE68;
extern f32 un_804DDE88;
extern f32 un_804DDE8C;
extern char un_804D5A88[3];

typedef struct TyListArchive {
    /* 0x00 */ HSD_JObj** x0;
    /* 0x04 */ u8 pad_4[0x18 - 0x4];
    /* 0x18 */ HSD_JObj* jobjs[3];
} TyListArchive;

typedef struct TyListGobjEntry {
    /* 0x00 */ HSD_GObj* x0;
    /* 0x04 */ HSD_GObj* x4;
    /* 0x08 */ u8 pad_8[0x16 - 0x8];
    /* 0x16 */ s8 x16;
} TyListGobjEntry;

void fn_8031438C(HSD_GObj* arg0)
{
    TyListState* state = (TyListState*) un_804A2AC0;
    TyListGobjEntry* entry = (TyListGobjEntry*) &state->gobj_2AC;
    TyListArchive* archive = un_804D6ED8;
    s32 i;
    HSD_GObj* tmp;
    PAD_STACK(0x18);

    if (((s8*) state)[0x2C2] != 0) {
        if (entry->x16 > 1) {
            for (i = 0; i < 3; i++) {
                u8* base_p = (u8*) archive + i * 4;
                if (i == (s8) state->x29B) {
                    HSD_JObjReqAnim(*(HSD_JObj**) (base_p + 0x18),
                                    un_804DDE44);
                } else {
                    HSD_JObjReqAnim(*(HSD_JObj**) (base_p + 0x18),
                                    un_804DDE48);
                }
                HSD_AObjSetRate(
                    archive->jobjs[0]->u.dobj->mobj->tobj->aobj,
                    un_804DDE48);
            }
            HSD_JObjAnimAll((HSD_JObj*) archive->x0[10]);
        } else {
            tmp = entry->x4;
            if (tmp != NULL) {
                ((s32*) tmp)[9] = 0;
                ((s32*) tmp)[8] = 0x42100000;
            }
            state->x290 = HSD_SisLib_803A6754(3, un_804D6EEC);
            state->x290->pos_z = un_804DDE68;
            state->x290->font_size.x = un_804DDE40;
            state->x290->font_size.y = un_804DDE34;
            state->x290->default_kerning = 1;
            state->x290->default_alignment = 2;
            HSD_SisLib_803A6B98(state->x290, un_804DDE88, un_804DDE8C,
                                un_804D5A88, un_GetTrophyTotal());
        }
        entry->x16--;
        return;
    }

    HSD_GObjProc_8038FED4(arg0);
    HSD_GObj_SetupProc(entry->x0, fn_80313BD8, 0);
    HSD_GObj_80390CD4(entry->x0);
}

void fn_80314504(HSD_GObj* gobj)
{
    TyListData* data = (TyListData*) gobj;

    if ((s32) HSD_CObjSetCurrent(data->cobj) != 0) {
        HSD_SetEraseColor(0, 0, 0, 0xFF);
        HSD_CObjEraseScreen(data->cobj, 1, 0, 0);
        HSD_GObj_80390ED0(gobj, 7);
        HSD_FogSet(0);
        HSD_CObjEndCurrent();
    }
}

/// #un_8031457C

void un_803147C4(void)
{
    TyListState* state = (TyListState*) un_804A2AC0;
    char* strs = un_803FE880;
    TyArchiveData* archive;
    PAD_STACK(8);

    memzero(&state->gobj_2AC, 0x18);
    un_8031457C();
    memzero(&state->gobj_2C4, 0x14);

    archive = un_804D6ED8;

    if (archive->data == NULL) {
        OSReport(strs + 0x14C);
        OSPanic(strs + 0x70, 0x636, un_804D5A8C);
    }

    {
        HSD_JObj* jobj =
            HSD_ArchiveGetPublicAddress(archive->data, strs + 0x170);
        if (jobj != NULL) {
            state->gobj_2C4 = GObj_Create(2, 3, 0);
            HSD_GObjObject_80390A70(state->gobj_2C4, (u8) HSD_GObj_804D784A,
                                    un_80306EEC(jobj, 0));
            GObj_SetupGXLink(state->gobj_2C4, HSD_GObj_LObjCallback, 0x34, 0);
        }
    }

    un_80307470(0);
    if (un_GetTrophyTotal() != 0) {
        memzero(state, 0x2AC);
        un_80313774();
    }
    HSD_PadRenewStatus();
}

void un_803148E4(s32 arg0)
{
    TyListState* state = (TyListState*) un_804A2AC0;
    TyModeState* mode = (TyModeState*) un_804A284C;
    TyArchiveData* archive = un_804D6ED8;
    PAD_STACK(8);

    if (un_GetTrophyTotal() != 0) {
        if (arg0 != 0) {
            un_804A284C[0x12A] = state->selectedIdx;
            un_804A284C[0x12B] = un_804D6EDC[state->selectedIdx];
            mode->x1 = state->x29B;
            mode->x2 = state->x29C;
            mode->x3 = state->x2B8;
        } else {
            if (un_GetTrophyTotal() != 0) {
                s16 val = un_804D6EDC[state->selectedIdx];
                un_803067BC(0, 0);
                state->selectedIdx = un_803062BC(val);
            }
            un_804A284C[0x12A] = state->selectedIdx;
            un_804A284C[0x12B] = un_804D6EDC[state->selectedIdx];
            mode->x1 = 0;
            mode->x2 = 0;
            mode->x3 = 0;
        }

        if (un_80304924(un_804D6EDC[state->selectedIdx]) != 0) {
            un_80304988(un_804D6EDC[state->selectedIdx]);
        }
    }

    if (state->gobj != NULL) {
        if (arg0 != 0) {
            HSD_GObjPLink_80390228(state->gobj);
        }
        state->gobj = NULL;
    }

    if (arg0 != 0) {
        HSD_SisLib_803A5E70();
    }

    if (archive->gobj != NULL) {
        if (arg0 != 0) {
            HSD_GObjPLink_80390228(archive->gobj);
        }
        archive->gobj = NULL;
    }

    if (state->gobj_2C4 != NULL && arg0 != 0) {
        HSD_GObjPLink_80390228(state->gobj_2C4);
    }

    if (state->gobj_2AC != NULL) {
        HSD_GObjProc_8038FED4(state->gobj_2AC);
        if (arg0 != 0) {
            HSD_GObjPLink_80390228(state->gobj_2AC);
        }
    }

    if (state->gobj_2B0 != NULL && arg0 != 0) {
        HSD_GObjPLink_80390228(state->gobj_2B0);
    }
}
