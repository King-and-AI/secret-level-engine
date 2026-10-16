import re, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
def load():
    s = open(os.path.join(HERE, 'scene.js')).read()
    block = s[s.index('const CUE_DEFAULT = {'):s.index('};', s.index('const CUE_DEFAULT = {'))]
    d = {k: float(v) for k, v in re.findall(r'(\w+):\s*([0-9.]+)', block)}
    p = os.path.join(HERE, os.environ.get('CUES', 'cues.json'))
    if os.path.exists(p):
        d.update(json.load(open(p)))
    return d
if __name__ == '__main__':
    print(load())
