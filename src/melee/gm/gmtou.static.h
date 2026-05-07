#ifndef MELEE_GM_GMTOU_STATIC_H
#define MELEE_GM_GMTOU_STATIC_H

#include "baselib/forward.h"

#include "dolphin/types.h"
#include "gm/types.h"

#include "sc/forward.h"

typedef struct TmBoxArrays {
    void* box2;
    void* box3;
    void* box4;
} TmBoxArrays;

/// @todo :: this isnt exactly right
typedef struct TmAnimTimers {
    u32 x0;
    u16 x4;
    u16 x6[4];
    u8 xE;
    u8 xF;
    u8 x10[4];
    u8 pad_x14[0x18 - 0x14];
    u8 x18[4];
    u8 x1C;
    struct {
        u8 a;
        u8 b;
        u8 c;
        u8 x0;
        u8 x1;
        u8 x2;
    } x1D[4]; ///< per-player jobj/anim states
    u8 pad_x35[0x38 - 0x35];
    u8 x38[4];
    u8 pad_x3C[0x40 - 0x3C];
} TmAnimTimers;

typedef struct gm_8019ECAC_OnEnter_t {
    u32 x0;
    s32 x4;
    u8 pad_x8[0x14 - 0x8];
    u32 x14;
} gm_8019ECAC_OnEnter_t;

struct lbl_803DA0D0_t {
    /* 0x000 */ u8 icon_model_map[0x18];
    /* 0x018 */ u8 pad_0x18[0x1E - 0x18];
    /* 0x01E */ u8 rank_thresholds[32][6];
    /* 0x0DE */ u8 pad_0xDE[0xE0 - 0xDE];
    /* 0x0E0 */ f32 bounce_y[41];
    /* 0x184 */ char unk_0x184[0x190 - 0x184];
    /* 0x190 */ char scene_data_name[0x1A8 - 0x190];
    /* 0x1A8 */ char tmbox_dat[0x1B4 - 0x1A8];
    /* 0x1B4 */ char box2_array_name[0x1CC - 0x1B4];
    /* 0x1CC */ char box3_array_name[0x1E4 - 0x1CC];
    /* 0x1E4 */ char box4_array_name[0x1FC - 0x1E4];
    /* 0x1FC */ char sis_data_name[0x210 - 0x1FC];
}; /* size = 0x210 */

extern struct lbl_803DA0D0_t lbl_803DA0D0;

extern TmData gm_804771C4;
extern SceneDesc* lbl_804D6690;
extern SceneDesc* lbl_804D6694;

#endif
