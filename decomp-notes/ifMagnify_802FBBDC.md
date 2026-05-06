---
function: ifMagnify_802FBBDC
tu: src/melee/if/ifmagnify.c
headline: permuter-territory + float-regalloc
tags: [permuter-territory, float-regalloc, stack-offset, frame-size]
---
## ifMagnify_802FBBDC (`src/melee/if/ifmagnify.c`) — permuter-territory + float-regalloc

- **Tags:** `permuter-territory`, `float-regalloc`, `stack-offset`, `frame-size`
- **Best fuzzy:** (unknown)
- **Diagnosis:** Structural source matches m2c output. Function is 504 instr; reached 74.76% match (365 mismatches). Includes/types correct (added cm/camera.h, ft/ftdrawcommon.h, ft/ftlib.h, gr/stage.h, pl/player.h, baselib/displayfunc.h, melee/gm/types.h). Header updated to void ifMagnify_802FBBDC(HSD_GObj*). Remaining diffs: (1) constant hoisting — target keeps 0.5/1.0/0.125/300.0 in callee-saved FPRs f30/f29/f27/f28 across the inner loop, base reloads sda21 inline each use; (2) stack-offset shift of ~32 bytes (target 0x170 frame, base 0x148); (3) reg-alloc shifts r22<->r23 fighter/state across loop body; (4) some scheduling around the bilinear color blend with fctiwz/fsubs/fmadds chain. Cleared bitfield is is_offscreen (mask 0x80, bitfield bit 7); skip-loop check is ignore_offscreen (mask 0x40, bit 6). Bilinear blend computes fa = 1.0 - tx, fb = 1.0 - ty (var_f0/var_f0_3), then xt = 1.0 - fa, yt = 1.0 - fb, then 4-corner GXColor lookup via ifMagnify_803F984C[cy*4+cx] byte-indexed into ifMagnify_803F9828 fn-pointer table. NOTE: decomp-permuter offline at log time; flagged for permuter when available.
- **Tried:** (1) Wrote full source from m2c sketch, 34% match. (2) Added missing includes for Stage/ftLib/Player/displayfunc — match jumped to 73%. (3) Inverted hud_enabled||IsHUDHidden||Camera_80030130 cond into 'do_render' temp matching the asm 0/1 idiom. (4) Substituted u32 ifMagnify_803F984C[16] with ((u8*)&array[idx])[j] indexing — small bump to 74.76%.
- **Likely fix:** Permuter run on stable structural source. Remaining diffs are register allocation (which constants get hoisted to callee-saved FPRs) plus instruction scheduling within the dense color-blend bilinear interpolation block; both are classic permuter strengths. Mismatch count too large for a manual hand-tune (365 >> 15).

