"""ElevenLabs narration with word timestamps, one request per line (L0..L5).
Usage: LINES=lines.json VOICE=voice.json VDIR=voice python3 tts.py [L0 L1 ...] [--force]
The key comes from the ELEVENLABS_API_KEY secret/environment variable (or ELEVEN_KEY, or engine/.env).
It is never printed or saved. Lines that already have a clip are skipped, so re-runs cost nothing."""
import json, os, base64, subprocess, sys, urllib.request, urllib.error, csv, time

HERE = os.path.dirname(os.path.abspath(__file__))
NO_KEY = ("The voiced option needs your own ElevenLabs API key.\n"
          "Save it as a secret named ELEVENLABS_API_KEY (or put ELEVENLABS_API_KEY=... in engine/.env), then run this again.\n"
          "A ~60 s video uses roughly 1,000 credits. No key? Use the silent option: ./make_silent.sh out.mp4")

def find_key():
    k = os.environ.get('ELEVENLABS_API_KEY') or os.environ.get('ELEVEN_KEY')
    p = os.path.join(HERE, '.env')
    if not k and os.path.exists(p):
        for l in open(p):
            if l.split('=', 1)[0].strip() in ('ELEVENLABS_API_KEY', 'ELEVEN_KEY') and '=' in l:
                v = l.split('=', 1)[1].strip()
                if v and not v.startswith('paste-'): k = v
    return k

VDIR = os.environ.get('VDIR', 'voice')
LINES = json.load(open(os.path.join(HERE, os.environ.get('LINES', 'lines.json'))))
S = json.load(open(os.path.join(HERE, os.environ.get('VOICE', 'voice_example.json'))))
ORDER = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5']

def gen(key, apikey, force=False):
    out = os.path.join(HERE, VDIR, key)
    if os.path.exists(out + '.json') and not force:
        return
    os.makedirs(os.path.join(HERE, VDIR), exist_ok=True)
    i = ORDER.index(key)
    body = {
        'text': LINES[key], 'model_id': S['model_id'],
        'voice_settings': {'stability': S['stability'], 'similarity_boost': S['similarity_boost'], 'style': S['style'],
                           'use_speaker_boost': S['use_speaker_boost'], 'speed': float(os.environ.get('SPEED', S['speed']))},
    }
    if i > 0: body['previous_text'] = LINES[ORDER[i - 1]][-200:]
    if i < len(ORDER) - 1: body['next_text'] = LINES[ORDER[i + 1]][:200]
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{S['voice_id']}/with-timestamps?output_format={S['output_format']}",
        data=json.dumps(body).encode(), headers={'xi-api-key': apikey, 'Content-Type': 'application/json', 'User-Agent': 'curl/8.5.0'})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            charged = r.headers.get('character-cost') or ''
            d = json.load(r)
    except urllib.error.HTTPError as e:
        msg = {401: 'ElevenLabs rejected the key (401). Check that ELEVENLABS_API_KEY is right and allowed to use text-to-speech.',
               402: 'ElevenLabs says the account is out of credits or the plan does not allow this (402).',
               429: 'ElevenLabs is rate-limiting or the credit limit was reached (429). Wait, or raise the key\'s credit limit.'}
        raise SystemExit(msg.get(e.code, f'ElevenLabs request failed (HTTP {e.code}).') + '\nNothing else was charged. You can still make the silent version: ./make_silent.sh out.mp4')
    open(out + '.mp3', 'wb').write(base64.b64decode(d['audio_base64']))
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', out + '.mp3', '-ar', '44100', '-ac', '1', out + '.wav'], check=True)
    json.dump({'alignment': d.get('alignment'), 'normalized': d.get('normalized_alignment'), 'text': LINES[key]}, open(out + '.json', 'w'))
    log = os.path.join(HERE, VDIR, 'credit-log.csv'); new = not os.path.exists(log)
    with open(log, 'a', newline='') as f:
        w = csv.writer(f)
        if new: w.writerow(['time', 'line', 'chars_sent', 'chars_charged'])
        w.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), key, len(LINES[key]), charged])
    print('generated', key, len(LINES[key]), 'chars sent, charged:', charged or 'not reported', flush=True)

if __name__ == '__main__':
    keys = [k for k in sys.argv[1:] if k != '--force'] or ORDER
    force = '--force' in sys.argv
    todo = [k for k in keys if force or not os.path.exists(os.path.join(HERE, VDIR, k + '.json'))]
    if not todo:
        print('all voice clips already exist in', VDIR, '(no credits used)'); sys.exit(0)
    apikey = find_key()
    if not apikey:
        print(NO_KEY, file=sys.stderr); sys.exit(3)
    print('sending', sum(len(LINES[k]) for k in todo), 'characters for', ' '.join(todo), flush=True)
    for k in todo:
        gen(k, apikey, force)
