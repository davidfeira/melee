---
function: mnInfo_80251AFC
tu: src/melee/mn/mninfo.c
headline: mwcc-loop-opt + frame-size
tags: [mwcc-loop-opt, frame-size, permuter-queued]
---
## mnInfo_80251AFC (`src/melee/mn/mninfo.c`) — mwcc-loop-opt + frame-size

- **Tags:** `mwcc-loop-opt`, `frame-size`, `permuter-queued`
- **Best fuzzy:** (unknown)
- **Diagnosis:** At 72.78% (107 mismatches). Structural shape correct: init loop fills mnInfo_804A0958[0x10..0x52] with 0..0x41, then two nested-loop sort passes calling mnInfo_80251A08 / gmMainLib_8015D804 that bubble-swap entries. Target frame is 0x30 (stmw r26 at 0x18 saving 6 regs r26-r31); mine is 0x28 (stmw r26 at 0x10). Init-loop unroll factor differs: target unrolls the inner store fully (32 stb per ctr-iter, single addi r9,r9,0x20 at end, ctr=2); mwcc on my source unrolls only 8 stb chunks and recomputes r9 = r31 + r10 mid-loop, and has an early bge guard (cmpwi r10,0x42; bge) before mtctr.
- **Tried:** (1) flat for-loop with index 'p[i] = (u8)i' over 0..0x42 — gets 8x unroll with mid-loop pointer recompute. (2) explicit nested loop: outer ctr=2 do-while with inner for(k=0..0x20) — REGRESSED to 53.29% (mwcc kept the outer loop variable in a register, didn't recognize constant trip). Reverted to (1).
- **Likely fix:** The 0x30 vs 0x28 frame size delta strongly suggests target source has an additional 8-byte local (perhaps unused, or a struct-by-value temp) keeping r26 saved alongside r27-r31. Worth trying a redundant local. The unroll-factor difference likely needs the init loop expressed as 'for (i=0; i<0x42; i+=0x20)' with explicit unrolled inner block, OR with two pointer chasers (ptr to 32-byte chunk, byte ptr inside) so mwcc recognizes the chunked structure. Permuter has good chance once frame size matches; structure is solid otherwise.

