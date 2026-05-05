---
function: grOnett_801E40E4
tu: src/melee/gr/gronett.c
headline: cross-tu-globals + mwcc-redundant-branch
tags: [cross-tu-globals, reloc-symbol-false-positive, paired-siblings]
---
## grOnett_801E40E4 (`src/melee/gr/gronett.c`) — cross-tu-globals + mwcc-redundant-branch

- **Tags:** `cross-tu-globals`, `reloc-symbol-false-positive`, `paired-siblings`
- **Best fuzzy:** 98.0392% (3 mismatches, 51 instr — Opus subagent, no commit)
- **Diagnosis:** 3 mismatches on 51-instr function. (1) Extra `b 0xa74` at offset 2532 — our build emits two consecutive `b .L_801E41A8` after the `cmpwi r0, 0; beq case0` switch dispatch; base only has one. The duplicate is unreachable dead code mwcc emits as a "fall-through" branch after the switch's default exit even though the prior `b` already exited. (2,3) `lfd f2, grOt_804DB2B0@sda21` vs `lfd f2, @331@sda21` at offsets 2552/2624 — same address (0x804DB2B0), reloc-symbol-name only. The 0x4330000080000000 magic constant for u32→double conversion. Symbols.txt registers `grOt_804DB2B0` as a global double, so mwcc names the sdata2 entry that way; base TU produced an anonymous `@331` literal pool entry at the same address.
- **Tried:** (1) Replace `return` with `break` in case 0 — no change. (2) Remove PAD_STACK(8) — much worse (frame regressed to 0x28, 11 mismatches). (3) Drop trailing `break` after `case 3` body — no change.
- **Likely fix:** Reloc-name half is paired-sibling cross-TU work (same pattern as `it_802B56E4`): would need to remove the `grOt_804DB2B0` global from symbols.txt OR change the TU layout so the literal pool emits the named symbol instead of `@331`. The extra-branch half is an mwcc-internal switch-dispatch quirk; permuter unlikely to fix structurally without affecting unrelated layout. Not a single-function subagent fix.

- **Stack offset mismatches** (4-16 bytes off): mwcc DSE removes unused locals, so naive padding doesn't help. PAD_STACK has subtle placement effects. Almost always permuter territory.
- **Float literal `@NNN@sda21` placeholders:** the target wants a named global. Declare `extern f32 <name>;` near the function, or define a `static const f32 <name> = <value>;` at the right place in the file.
- **Float `0.0F` / `1.0F` etc.:** sometimes these need to be assigned to a local (`f32 zero = some_extern;`) rather than inlined, to match the compiler's caching of the SDA pool offset.
- **OSReport literals:** all `gr*.c` files where the function calls OSReport need the format string + filename inlined into the TU's data section. See the closed gr/ examples (`940801c05`, `842c69cbb`, `e68a70432`, `3105e21c5`, `d91b9cbed`).
- **Struct-split:** sometimes a single `lbl_XXXX` struct in a header should be two adjacent structs (e.g. fn_80186080's `lbl_804735E8` → `lbl_804735E8` + `lbl_8047368C`). Look for `pad_NNN` fields that mark a struct boundary the original had.
- **Aliasing optimization (`-O4,p`):** mwcc merges stack slots it can prove are aliased. If the target keeps them separate, the C needs a shape that defeats aliasing analysis (often via cast or volatile).
