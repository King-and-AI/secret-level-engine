# Secret Level Engine

Makes short landscape explainer videos (1920×1080, 30 fps, **under 60 seconds**) in a game-level style:

**hook → Level 1 (a relatable puzzle) → the picture → Level 2 (the bigger idea) → Boss level (the real-world use) → ending**

Every frame is drawn in code on an HTML canvas, the music and sound effects are composed in code, and an AI narrator (ElevenLabs) is optional. Because all on-screen text is typed from code strings, it never comes out garbled the way AI-generated video text can.

The included worked example, *How do thousands of satellites avoid crashing?*, builds silently in about 2 minutes and needs no account or key.

## Needs

- `python3` with `numpy`, `scipy`, `pillow`, `playwright` (`python3 -m playwright install chromium`; if that download is missing, `render.py` falls back to an installed Chrome at `CHROME_BIN`, default `/opt/google/chrome/chrome`)
- `ffmpeg` built with the `rubberband` filter (only the voiced path needs rubberband)
- The system font **Noto Color Emoji** (for emoji objects)
- Optional: an ElevenLabs API key for narration

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
5. **Voice (optional).** Put a restricted key in `engine/.env` (copy `.env.example`). `LINES=lines.json VDIR=voice_x SPEED=1.15 python3 tts.py`, then `FAST="L1 L4" ./prepare_voice.sh voice_x` (tempo 1.06, or 1.09 for long lines). Copy `timeline_example.py`, place each phrase with `place(time, line, first_word, last_word, occ=n)`, squeeze pauses to about 0.2–0.35 s and anchor every cue to a spoken word. Then `TEMPO_PER='{"L1":1.09,"L4":1.09}' ./make_voiced.sh out.mp4 voice_x timeline_x.py`. Characters sent and charged are logged in `voice_x/credit-log.csv`.
6. **Check the finished file.** `./frames_qa.sh out.mp4 qa` pulls one full-size frame per second plus contact grids. Some problems only show in the encoded file. Keep it under 60 s and about −14 LUFS.

## Files

| File | What it does |
|---|---|
| `engine/index.html` | Loads the fonts and `scene.js` in a hidden browser page. |
| `engine/scene.js` | Engine core (helpers, background, captions, banners, HUD and XP bar, wipes, scene switching) plus the topic part (labels, cue times, scenes `s0`–`s5`). |
| `engine/render.py` | `stills t1,t2,...` for checking, or `video out.mp4` for every frame at 30 fps. |
| `engine/audio.py` | Composes music and sound effects from the cue sheet; `--voice` mixes in the narration with the music ducked under it. |
| `engine/tts.py` | ElevenLabs narration with word timestamps, one request per line. Logs credits. |
| `engine/phrases.py` | Reads word timings from the ElevenLabs results. |
| `engine/timeline_example.py` | Worked example of turning word timings into the cue sheet and the voice track. |
| `engine/cues.py` | Shared cue loader for `audio.py`. |
| `engine/prepare_voice.sh` | MP3 → WAV plus a gentle tempo lift. |
| `engine/make_silent.sh`, `make_voiced.sh` | One-command builds. |
| `engine/loudnorm.sh`, `mux.sh` | Two-pass loudness to −14 LUFS; final join with standard colour range. |
| `engine/sheet.py`, `grid.py`, `frames_qa.sh` | Contact sheets and frame checks. |
| `engine/lines_example.json` | The example's narration lines. |
| `engine/fonts/` | Fredoka, Nunito, JetBrains Mono with their licences. |
| `docs/CUES.md` | The cue names and which sounds fire on them. |

## Safety

- **Never commit a key.** `.env` is in `.gitignore`. Use a restricted ElevenLabs key with a credit limit and delete it when done.
- Make original pictures, music and jokes; no found memes, images or music.
- Get written consent before using any real person's voice; for a student, also their parent or school.

## Licences

See `NOTICE.md`.
