import json
import os
TEMPO = float(os.environ.get('TEMPO', '1.06'))
import json as _j
TEMPO_PER = _j.loads(os.environ.get('TEMPO_PER', '{}'))
VDIR = os.environ.get('VDIR', 'voice')
def words(k):
    d=json.load(open(f'{VDIR}/{k}.json'))['alignment']
    ch=d['characters']; st=d['character_start_times_seconds']; en=d['character_end_times_seconds']
    out=[]; cur=''; cs=None; pe=None
    for c,a,b in zip(ch,st,en):
        if c.isspace():
            if cur: out.append([cur,cs,pe]); cur=''
        else:
            if not cur: cs=a
            cur+=c; pe=b
    if cur: out.append([cur,cs,pe])
    tp = TEMPO_PER.get(k, TEMPO)
    out = [[w0, a / tp, b / tp] for w0, a, b in out]
    return [w for w in out if not (w[0].startswith('<') or w[0].startswith('time=') or w[0]=='/>')]
def phrases(k, gap=0.28):
    ws=words(k); ph=[]; 
    for w in ws:
        if ph and w[1]-ph[-1]['end'] < gap: ph[-1]['words'].append(w); ph[-1]['end']=w[2]
        else: ph.append({'start':w[1],'end':w[2],'words':[w]})
    for p in ph: p['text']=' '.join(w[0] for w in p['words'])
    return ph
if __name__=='__main__':
    tot=0
    for k in ['L0','L1','L2','L3','L4','L5']:
        ph=phrases(k); s=sum(p['end']-p['start'] for p in ph); tot+=s
        print(k, round(s,2), len(ph)); 
        for p in ph: print('   ', round(p['start'],2), round(p['end'],2), p['text'])
    print('speech only total', round(tot,2))
