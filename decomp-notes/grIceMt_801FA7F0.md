---
function: grIceMt_801FA7F0
tu: src/melee/gr/gricemt.c
headline: stack-offset + frame-size
tags: [stack-offset, frame-size]
---
## grIceMt_801FA7F0 (`src/melee/gr/gricemt.c`) — stack-offset + frame-size

- **Tags:** `stack-offset`, `frame-size`
- **Best fuzzy:** 99.8%
- **Diagnosis:** 99.8%/5 mismatches all in stwu/stw-r31/epilogue. Frame size delta: target wants 0x28, base produces 0x30 (8 bytes too large). Function body decompiled correctly: if(Ground_801C57A4()==arg2->x0_gobj) { gobj=Ground_801C2BA4(10); if(gobj && gobj->user_data) ((UnkFlagStruct*)&gp2->gv.icemt.xD8)->b4=1; }. Bit set is rlwimi r0,r3,3,28,28 (sets 0x08, ie b4 of UnkFlagStruct treated as bitfield from MSB). Sig: void(Ground* gp, s32 arg1, CollData* arg2, s32 arg3, mpLib_GroundEnum arg4, float arg8). Same class as mpJointListAdd, lb_8001BE30, ftCo_CapturePulledHi_Phys (8-byte excess). All 25 instructions and opcodes match perfectly, only stack frame size differs.
- **Tried:** (1) nested-if structure (current, 99.8%); (2) chained && in single if (99.4%, regressed - cmplw r3,r0 vs r0,r3 swap); (3) flat early-return guards (99.8%, same).
- **Likely fix:** Frame-size noise from mwcc spill slot reservation. Permuter unlikely to find since deletion of the frame slot would change all stwu/lwz offsets. Possibly an unused local that survives DCE, or related to mpLib_GroundEnum arg4 being unused (mwcc may reserve slot for unused enum arg). Try declaring an explicit (void)arg4 reference, or restructuring to use arg4. Worth checking if siblings fn_801F9338/9448/9558 (which call this) have the same enum-arg pattern.
