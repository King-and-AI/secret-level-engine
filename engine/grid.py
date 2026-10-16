"""Contact grids: python3 grid.py 'dir/f*.png' out_prefix [per_grid]  (2 columns, each frame at 960x540)."""
import sys, glob
from PIL import Image, ImageDraw
fs = sorted(glob.glob(sys.argv[1])); n = int(sys.argv[3]) if len(sys.argv) > 3 else 6
for j in range(0, len(fs), n):
    batch = fs[j:j + n]; rows = (len(batch) + 1) // 2
    im = Image.new('RGB', (1920, 540 * rows))
    for i, f in enumerate(batch):
        a = Image.open(f).convert('RGB').resize((960, 540)); ImageDraw.Draw(a).text((5, 5), f.split('/')[-1], fill='white'); im.paste(a, ((i % 2) * 960, (i // 2) * 540))
    im.save(f'{sys.argv[2]}{j // n:02d}.png')
