"""ElevenLabs narration with word timestamps, one request per line (L0..L5).
Usage: LINES=lines.json VDIR=voice_x SPEED=1.15 python3 tts.py [L0 L1 ...] [--force]
The key is read from ELEVEN_KEY / ELEVENLABS_API_KEY or engine/.env. It is never printed or saved."""
import json, os, base64, subprocess, sys, urllib.request, csv, time

HERE = os.path.dirname(os.path.abspath(__file__))
def _key():
    k = os.environ.get('ELEVEN_KEY') or os.environ.get('ELEVENLABS_API_KEY')
    p = os.path.join(HERE, '.env')
    if not k and os.path.exists(p):
        k = next((l.split('=', 1)[1].strip() for l in open(p) if l.startswith('ELEVEN_KEY=')), None)
    if not k:
        raise SystemExit('No ElevenLabs key: put ELEVEN_KEY=... in engine/.env (never commit or share that file).')
    return k
VOICE = os.environ.get('VOICE_ID', 'TX3LPaxmHKxFdv7VOQHJ')  # "Liam", an ElevenLabs premade voice
VDIR = os.environ.get('VDIR', 'voice')
MODEL = 'eleven_multilingual_v2'
LINES = json.load(open(os.path.join(HERE, os.environ.get('LINES', 'lines.json'))))
ORDER = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5']

def gen(key, force=False):
    out = os.path.join(HERE, VDIR, key)
    if os.path.exists(out + '.json') and not force:
        return
    os.makedirs(os.path.join(HERE, VDIR), exist_ok=True)
    i = ORDER.index(key)
    body = {
        'text': LINES[key], 'model_id': MODEL,
        'voice_settings': {'stability': 0.38, 'similarity_boost': 0.8, 'style': 0.45, 'use_speaker_boost': True, 'speed': float(os.environ.get('SPEED', '1.08'))},
    }
    if i > 0: body['previous_text'] = LINES[ORDER[i - 1]].split('<')[0][-200:]
    if i < len(ORDER) - 1: body['next_text'] = LINES[ORDER[i + 1]].split('<')[0][:200]
    req = urllib.request.Request(
        f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128',
        data=json.dumps(body).encode(), headers={'xi-api-key': _key(), 'Content-Type': 'application/json', 'User-Agent': 'curl/8.5.0'})
    with urllib.request.urlopen(req, timeout=120) as r:
        charged = r.headers.get('character-cost') or r.headers.get('x-character-count') or ''
        d = json.load(r)
    open(out + '.mp3', 'wb').write(base64.b64decode(d['audio_base64']))
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', out + '.mp3', '-ar', '44100', '-ac', '1', out + '.wav'], check=True)
    json.dump({'alignment': d.get('alignment'), 'normalized': d.get('normalized_alignment'), 'text': LINES[key]}, open(out + '.json', 'w'))
    log = os.path.join(HERE, VDIR, 'credit-log.csv'); new = not os.path.exists(log)
    with open(log, 'a', newline='') as f:
        w = csv.writer(f)
        if new: w.writerow(['time', 'line', 'chars_sent', 'chars_charged'])
        w.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), key, len(LINES[key]), charged])
    print('generated', key, len(LINES[key]), 'chars sent, charged:', charged or 'not reported')

if __name__ == '__main__':
    keys = sys.argv[1:] or ORDER
    force = '--force' in keys
    for k in [k for k in keys if k != '--force']:
        gen(k, force)
