# Secret Level Engine

Makes short landscape explainer videos (1920×1080, 30 fps, **under 60 seconds**) in a game-level style:

**hook → Level 1 (a relatable puzzle) → the picture → Level 2 (the bigger idea) → Boss level (the real-world use) → ending**

Every frame is drawn in code on an HTML canvas and the music and sound effects are composed in code. Because all on-screen text is typed from code strings, it never comes out garbled the way AI-generated video text can.

## Two ways to make a video: Silent / With voiceover

| | **Option 1: Silent** | **Option 2: With voiceover** |
|---|---|---|
| What you get | Music, sound effects and captions that tell the whole story | The same, plus an AI narrator; music dips under the voice and every animation is timed to the spoken words |
| What you need | Nothing extra | Your own **ElevenLabs API key**, saved as a secret (environment variable) named `ELEVENLABS_API_KEY`, or in `engine/.env` |
| Cost | Free | About **1,000 ElevenLabs credits per ~60 s video** (1 credit per character; the worked example's narration is 1,015 characters). Re-builds reuse the saved clips and cost nothing |
| One command | `./make_silent.sh out.mp4` | `./make_voiced.sh out.mp4 lines.json timeline.py voice.json voice_dir` |
| Try the worked example | `./make_silent.sh example.mp4` (about 2 min, about 58.2 s long) | `./make_voiced.sh example-voiced.mp4 lines_example.json timeline_example.py voice_example.json voice_example` (about 1,000 credits the first time; about 58.7 s long) |

No key? The voiced command stops before doing anything and prints a plain message saying so; use the silent option instead. Tip: always make the silent cut first and check it, then pay for the voice.

The worked example is *How do thousands of satellites avoid crashing?* Its narration text is in `engine/lines_example.json` and its voice settings in `engine/voice_example.json` (ElevenLabs premade voice "Liam", speed 1.15, then a small tempo lift, mixed to −14 LUFS). No audio files are included: the voiced example makes its own clips with your key.

## Needs

- `python3` with `numpy`, `scipy`, `pillow`, `playwright` (`python3 -m playwright install chromium`; if that download is missing, `render.py` falls back to an installed Chrome at `CHROME_BIN`, default `/opt/google/chrome/chrome`)
- `ffmpeg` built with the `rubberband` filter (only the voiced path needs rubberband)
- The system font **Noto Color Emoji** (for emoji objects)
- Voiced option only: an ElevenLabs API key (see above)

## Quick start (check the setup)

```bash
cd engine
./make_silent.sh example.mp4      # about 2 minutes; prints length, loudness and size
```

## Make a new video

1. **Storyboard and script.** Six parts, under 60 s: hook (~6 s), Level 1 (~12 s), the picture (~5 s), Level 2 (~10 s), Boss (~16 s), ending (~6 s). Write the six lines `L0`–`L5` (one per part) in a `lines.json` like `lines_example.json`, even for a silent video: the captions are taken from them.
2. **Scenes.** In `engine/scene.js`, keep everything above the line *END OF ENGINE CORE*. Replace `LABELS`, the times in `CUE_DEFAULT` and the six scene functions `s0`–`s5`. Reuse the helpers: `txt`, `rich`, `pop`, `fout`, `caption`, `banner`, `card`, `arrowR`, `drawCheck`, `drawChip`, `rr`, `mw`. Read every time from `K()` (the cue sheet); never hard-code times. Keep the cue **names**: see `docs/CUES.md`.
3. **Check stills.** `python3 render.py stills 3.2,9.5,14,...` then `python3 sheet.py sheet.png stills/*.png` and look at the sheet. Fix overlaps and text outside its box before rendering the video.
4. **Silent video (free).** `./make_silent.sh out.mp4`. Review it before paying for any voice.
5. **Voice (Option 2 only).** Copy `voice_example.json` to `voice.json` (change the voice there if you like) and `timeline_example.py` to `timeline_x.py`. In the timeline, place each spoken phrase with `place(time, line, first_word, last_word, occ=n)`, keep pauses about 0.2–0.35 s and anchor every cue to a spoken word. Then `./make_voiced.sh out.mp4 lines.json timeline_x.py voice.json voice_x`. It makes the clips (once), lifts the tempo, builds the cue sheet, runs `check_voice.py` (every phrase inside its own scene, no overlaps, under 60 s) and builds the video. If a line overruns, add it to `"fast_lines"` in `voice.json` or tighten the timeline and run again (no new credits). Characters sent and charged are logged in `voice_x/credit-log.csv`. Optional: `python3 check_words.py voice_track.wav lines.json cues.json` (needs `openai-whisper`) transcribes the narration and compares it with the lines.
6. **Check the finished file.** `./frames_qa.sh out.mp4 qa` pulls one full-size frame per second plus contact grids. Some problems only show in the encoded file. Keep it under 60 s and about −14 LUFS.

## Files

| File | What it does |
|---|---|
| `engine/index.html` | Loads the fonts and `scene.js` in a hidden browser page. |
| `engine/scene.js` | Engine core (helpers, background, captions, banners, HUD and XP bar, wipes, scene switching) plus the topic part (labels, cue times, scenes `s0`–`s5`). |
| `engine/render.py` | `stills t1,t2,...` for checking, or `video out.mp4` for every frame at 30 fps. |
| `engine/audio.py` | Composes music and sound effects from the cue sheet; `--voice` mixes in the narration with the music ducked under it. |
| `engine/tts.py` | ElevenLabs narration with word timestamps, one request per line. Skips lines that already have a clip; stops with a plain message if there is no key; logs credits. |
| `engine/voice_example.json` | Voice settings for the worked example (voice, model, stability, speed, tempo, loudness). |
| `engine/check_voice.py`, `check_words.py` | Voiced timing check; optional transcript check. |
| `engine/phrases.py` | Reads word timings from the ElevenLabs results. |
| `engine/timeline_example.py` | Worked example of turning word timings into the cue sheet and the voice track. |
| `engine/cues.py` | Shared cue loader for `audio.py`. |
| `engine/prepare_voice.sh` | MP3 → WAV plus a gentle tempo lift. |
| `engine/make_silent.sh` | Option 1, silent: one-command build. |
| `engine/make_voiced.sh` | Option 2, with voiceover: one-command build. |
| `engine/loudnorm.sh`, `mux.sh` | Two-pass loudness to −14 LUFS; final join with standard colour range. |
| `engine/sheet.py`, `grid.py`, `frames_qa.sh` | Contact sheets and frame checks. |
| `engine/lines_example.json` | The example's narration lines. |
| `engine/fonts/` | Fredoka, Nunito, JetBrains Mono with their licences. |
| `docs/CUES.md` | The cue names and which sounds fire on them. |

## Safety

- **Never commit a key.** Prefer a secret/environment variable `ELEVENLABS_API_KEY`; if you use `engine/.env`, it is in `.gitignore`. Use a restricted ElevenLabs key with a credit limit and delete it when done.
- Make original pictures, music and jokes; no found memes, images or music.
- Get written consent before using any real person's voice; for a student, also their parent or school.

## Licences

See `NOTICE.md`.
