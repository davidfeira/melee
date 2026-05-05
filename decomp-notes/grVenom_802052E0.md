---
function: grVenom_802052E0
tu: src/melee/gr/grvenom.c
tags: [stack-offset, float-literal, permuter-false-positive]
---
## grVenom_802052E0 (`src/melee/gr/grvenom.c`)

- **Tags:** `stack-offset`, `float-literal`, `permuter-false-positive`
- **Best fuzzy:** 99.92% — confirmed unreachable from function-level mutations.
- **Permuter status:** found 125+ score-0 outputs (cluster, ~24k iterations). Tried 3 ports (declaration reorder, math rewrite `data_idx*12 → 6*(data_idx*2)`, double-promote `0.0F→0.0`). All compiled to byte-different output; fuzzy stayed 99.92% across attempts.
- **Why permuter helps less than expected:** the 99.92% ceiling comes from `0.0F` being emitted as `@275@sda21` instead of using extern `grVe_804DB740`. That's a literal-pool layout decision driven by what other floats this TU already references. Function-level rewrites can't move it.
- **NOT a gr/ TU-data-pattern function** — it has no OSReport call.
- **Tried fix that improved strict (NOT fuzzy):** caching `0.0F` extern in a local: `f32 zero = grVe_804DB740;`. Eliminated symbol-relocation diff for the float literal.
- **Blocker:** Vec3 stack offset shifted 4 bytes (target sp+0x24, ours sp+0x28). Frame 0x48 in both; extra unused locals get DCE'd. PAD_STACK shifted it the wrong direction.
- **Likely fix:** permuter — pure stack-offset register-allocation noise.
