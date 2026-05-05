---
function: roll2upvec
tu: src/sysdolphin/baselib/cobj.c
headline: permuter-false-positive + tu-wide-data
tags: [permuter-false-positive, tu-wide-data, cross-tu-globals, stack-offset]
---
## roll2upvec (`src/sysdolphin/baselib/cobj.c`) — permuter-false-positive + tu-wide-data

- **Tags:** `permuter-false-positive`, `tu-wide-data`, `cross-tu-globals`, `stack-offset`
- **Best fuzzy:** 99.9535%
- **Diagnosis:** At 99.95%/99.66% with 18 instruction diffs. 14 of 18 are sdata2 float reloc-symbol mismatches: target uses named globals (HSD_CObj_804DE478/494/B0/B8/C0 @sda21) for 0.0001f, FLT_MIN, 1.0/0.0001/3.0 doubles; base generates anonymous pool labels (@243, @322, @588, @589, @590). Also @192 vs @181 — pool numbering offset of 11 slots, indicating target TU has 11 more sdata2 entries (~88 bytes) than current build. Source already inlines HSD_CObjGetEyeVector via mwcc (matches target structure exactly). Remaining 4 real diffs: inlined eyepos/interest locals at sp24/sp30 (current) vs sp28/sp34 (target), plus tmp scalars at sp1c/sp20 vs sp20/sp24 — uniform +4 byte shift, indicates one extra 4-byte padding slot before the inlined-call stack region in target. Frame size 0xa8 in both.
- **Tried:** Variant 1: manually inlined HSD_CObjGetEyeVector body (with eyepos/interest as outer locals + goto fallback). Result: frame ballooned to 0xc8, match dropped to 81% — mwcc's auto-inlining produces a tighter layout. Reverted.
- **Likely fix:** Reloc-symbol diffs will resolve when the rest of cobj.c TU functions match (tu-wide pool ordering). Stack-offset diffs may resolve simultaneously or need a tiny declaration-order tweak. Do NOT dispatch permuter — false-positive class. Wait for other cobj.c functions (especially upvec2roll which is currently inlined into target) to be addressed.
