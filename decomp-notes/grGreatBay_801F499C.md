---
function: grGreatBay_801F499C
tu: src/melee/gr/grgreatbay.c
headline: frame-size + stack-offset
tags: [frame-size, stack-offset, permuter-false-positive]
---
## grGreatBay_801F499C (`src/melee/gr/grgreatbay.c`) — frame-size + stack-offset

- **Tags:** `frame-size`, `stack-offset`, `permuter-false-positive`
- **Best fuzzy:** 99.936%
- **Diagnosis:** Frame size delta: target wants 0x80, base produces 0x90 (16 bytes too big). All 36 stack-offset mismatches are uniform 0x10 shift relative to target. Layout: target has Vec3 pos2 at sp[0x18], Vec3 pos at sp[0x24], f64 scratch at 0x30/0x40 (two pairs of 16-byte stfd/lfd float-to-int conversion temps), saved regs at 0x54, f31 at 0x78. Base has same logical layout but shifted +0x10, with extra unidentified 16-byte slot at sp[0x18..0x27] before pos2. Plus 12 sda21 mismatches: target references named sdata2 floats grGb_804DB538/grGb_804DB548 (defined in source as 'const f32/double' at file scope, 0.0f and the float-to-int magic 4503601774854144), base emits anonymous @508@sda21/@517@sda21 - classic permuter-false-positive named-vs-anon pool. Plus 1 reloc-class @ instr 1992: addi r5,r26,0x174 (target uses named &grGb_803E3E60+0x174 reloc, base uses different reloc form, asm bytes printed identically).
- **Tried:** (1) Collapsed inner-scope pos2 into outer pos: frame matches at 0x80 (0 frame mismatches!) but case-2 access lands at 0x24 instead of target's 0x18 - target genuinely has TWO distinct Vec3 slots at 0x18 and 0x24. (2) Moved both Vec3 pos2 and pos to outer scope (pos2 first decl, then pos): frame still 0x90, 50 mismatches. (3) Outer pos, outer pos2 (pos first): same as baseline 52 mismatches. (4) Both Vec3 in inner case scopes (case 1 pos, case 2 pos2): same as baseline 52 mismatches. Scope changes do not shrink frame.
- **Likely fix:** Target has an extra non-DCE'd local that base lacks - same pattern as ftCo_CapturePulledHi_Phys / HSD_CObjGetViewingMtxPtr stuck notes. Sda21 mismatches are permuter-false-positive class (named globals defined but unused by source: const f32 grGb_804DB538=0.0f, etc. at file scope lines 125-128). Reloc-class addi r5,r26,0x174 is also permuter-false-positive. Real work is finding the missing local. Cannot use permuter (sda21+reloc would score as match but report.json fuzzy fails).
