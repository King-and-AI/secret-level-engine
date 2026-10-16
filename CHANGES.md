# Changes from the original engine (v1.0)

The pipeline is unchanged: canvas scenes driven by a named cue sheet → Playwright frame capture → ffmpeg H.264; music and sound effects composed in numpy from the same cues; optional ElevenLabs voice with word timestamps → phrase-by-phrase timeline → ducked mix. The worked example re-renders frame-for-frame the same as its first build (mean pixel difference about 1/255, which is encoding noise).

What changed, and why:
- **Example scenes** are now the satellite-safety video; the first video's scenes, script versions and voice clips are not included.
- **`scene.js`**: marked where the engine core ends and the topic part starts; HUD labels and XP floaters moved into a `LABELS` setting; the optional local skyline is now `VARIANT=city`; two food icons from the first video removed.
- **`tts.py`**: narration lines are read from a JSON file (`LINES=`) instead of being written into the code; logs characters sent and charged to `credit-log.csv`. The request itself (voice, model, settings, format, header) is unchanged.
- **`render.py`**: falls back to an installed Chrome when Playwright's own browser download is missing; prints page errors.
- **New helpers**: `make_silent.sh`, `make_voiced.sh`, `mux.sh` (standard TV colour range; an earlier build came out "full range", which some players show washed out), `loudnorm.sh` (two passes, to land on −14 LUFS instead of about −13), `frames_qa.sh`.

## Two options (still v1.0, before first release)

- **Two clearly named ways to build:** Option 1 silent (`make_silent.sh`, free) and Option 2 with voiceover (`make_voiced.sh`, your own ElevenLabs key). The README opens with both.
- **`make_voiced.sh`** is now one command: `out.mp4 lines.json timeline.py voice.json voice_dir`. It makes the clips, applies the tempo lift, builds the cue sheet, checks the timing and builds the video. If there is no key it stops at once with a plain message (exit code 3) and points to the silent option.
- **`voice_example.json`**: the worked example's voice settings in one file (voice "Liam", model, stability 0.38, similarity 0.8, style 0.45, speaker boost, speed 1.15, tempo 1.06 or 1.09 for long lines, −14 LUFS). `tts.py` and `make_voiced.sh` read it; the request sent to ElevenLabs is unchanged.
- **`tts.py`**: finds the key in the `ELEVENLABS_API_KEY` environment variable (or `engine/.env`); never prints it; skips lines that already have a clip, so re-builds cost nothing; plain messages for a wrong key, no credits left, or rate limits.
- **`check_voice.py`** (new): every spoken phrase must sit inside its own scene, with no overlaps, and the video under 60 s. The timeline writes `placed.json` for it. **`check_words.py`** (new, optional): Whisper transcript compared with the lines.
- **`make_silent.sh`**: removes a `cues.json` left by a voiced build, so the silent cut always uses the times in `scene.js`.
- Checked: the voiced worked example rebuilt with the new command to 58.67 s, −14.3 LUFS, the same as its first build.
