# Changes from the original engine (v1.0)

The pipeline is unchanged: canvas scenes driven by a named cue sheet → Playwright frame capture → ffmpeg H.264; music and sound effects composed in numpy from the same cues; optional ElevenLabs voice with word timestamps → phrase-by-phrase timeline → ducked mix. The worked example re-renders frame-for-frame the same as its first build (mean pixel difference about 1/255, which is encoding noise).

What changed, and why:
- **Example scenes** are now the satellite-safety video; the first video's scenes, script versions and voice clips are not included.
- **`scene.js`**: marked where the engine core ends and the topic part starts; HUD labels and XP floaters moved into a `LABELS` setting; the optional local skyline is now `VARIANT=city`; two food icons from the first video removed.
- **`tts.py`**: narration lines are read from a JSON file (`LINES=`) instead of being written into the code; logs characters sent and charged to `credit-log.csv`. The request itself (voice, model, settings, format, header) is unchanged.
- **`render.py`**: falls back to an installed Chrome when Playwright's own browser download is missing; prints page errors.
- **New helpers**: `make_silent.sh`, `make_voiced.sh`, `mux.sh` (standard TV colour range; an earlier build came out "full range", which some players show washed out), `loudnorm.sh` (two passes, to land on −14 LUFS instead of about −13), `frames_qa.sh`.
