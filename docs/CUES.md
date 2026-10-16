# The cue sheet (the timing contract)

Every animation and every sound effect is keyed to a **named time in seconds** (a "cue"). The picture (`scene.js`) and the sound (`audio.py`) read the same cue sheet, so they always line up.

- Silent video: the times are the `CUE_DEFAULT` list at the top of `scene.js`. Edit them by hand.
- Voiced video: a timeline script (copy `timeline_example.py`) works the times out from the narrator's word timings and writes `cues.json`, which overrides `CUE_DEFAULT`.

**Keep these names for every new video.** `audio.py` composes the music sections and places the sound effects on them. Give each name a new meaning in your own scenes, but keep the order and roughly the spacing.

| Cue | Scene | Sound that fires there (from `audio.py`) | Typical use |
|---|---|---|---|
| `h_title` | Hook | pop | title appears |
| `h_zzz` | Hook | three falling "boops" | sleepy / doubtful beat |
| `h_quote` | Hook | typing ticks | the student's question appears |
| `h_attr` | Hook | – | a small tag under the quote |
| `h_skel` | Hook | fast clock ticks | the gag ("still waiting…") |
| `h_glitch` | Hook | record scratch; intro music tape-stops here | gag punchline |
| `h_twist` | Hook | impact | "Plot twist:" |
| `h_twist2` | Hook | pop, then snare build-up and riser into B1 | the twist sentence |
| `B1` | wipe → Level 1 | whoosh, impact + level jingle; upbeat music starts | Level 1 banner |
| `l1_sign`, `l1_row1`, `l1_row2`, `l1_label` | Level 1 | ding; pop runs | items arrive |
| `l1_eq1`, `l1_eq2` | Level 1 | pops | working steps |
| `l1_step1`, `l1_step2`, `l1_step3` | Level 1 | blips | more steps |
| `l1_cap1`, `l1_cap2`, `l1_cap3` | Level 1 | – | captions |
| `l1_tags`, `l1_tags2` | Level 1 | coins, ding | the answer |
| `l1_xp` | Level 1 | XP jingle | XP bar fills, catchphrase floater |
| `B2` | wipe → The picture | whoosh; lighter music with arpeggio | |
| `g_title`, `g_axes` | Picture | pop, small whoosh | |
| `g_line1`, `g_line2` | Picture | zips | two things drawn |
| `g_cap` | Picture | – | caption |
| `g_dot` | Picture | bright ding | the key moment |
| `g_icons` | Picture | pops | |
| `B3` | wipe → Level 2 | whoosh, impact + level jingle; music with lead | Level 2 banner |
| `l2_title`, `l2_ones`, `l2_labels` | Level 2 | pop, blips, pop run | |
| `l2_morph` | Level 2 | whoosh + rising blips | something transforms |
| `l2_unk` | Level 2 | double pop | new term / new item |
| `l2_cap1`, `l2_cap2` | Level 2 | – | captions |
| `l2_chip` | Level 2 | boing | |
| `l2_power`, `l2_xp` | Level 2 | small impact + jingle, XP jingle | catchphrase, XP |
| `B4` | wipe → Boss | whoosh, impact + siren; minor-key driving music | Boss banner, red tint |
| `b_title`, `b_food` | Boss | pop, blips | |
| `b_grow` → `b_billions` | Boss | riser from b_grow to b_billions (kick drops out for the last second) | build-up |
| `b_billions` | Boss | big impact + cymbal | the explosion / big reveal |
| `b_grow_end`, `b_cap1`, `b_partB` | Boss | – | |
| `b_card1`, `b_card2` | Boss | pops | cards |
| `b_pulse` | Boss | blip pulses | |
| `b_out` | Boss | typing ticks | |
| `b_cap2` | Boss | – | caption |
| `b_xp` | Boss | big XP jingle | |
| `B5` | wipe → Ending | whoosh; outro chords | |
| `o_chip1`, `o_chip2`, `o_chip3` | Ending | rising pops | the chain of three chips |
| `o_yah` | Ending | boop | "YOU ARE HERE" / small line |
| `o_big` | Ending | impact | the closing line |
| `o_confirm` | Ending | stamp thump | stamp slams down |
| `o_done` | Ending | final chord, crash, jingle | "LEVEL COMPLETE", confetti |
| `o_fade` | Ending | sound fades from here to END | picture HOLDS (no fade to black) |
| `END` | – | – | video length; keep under 60 |

Scene order is fixed by `sceneList()` in `scene.js`: hook `s0` until `B1`, then `s1`, `s2`, `s3`, `s4`, `s5`.
