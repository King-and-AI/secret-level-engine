import sys, glob
from PIL import Image, ImageDraw
files = sys.argv[2:]
cols = 2; w, h = 960, 540
rows = (len(files)+cols-1)//cols
sheet = Image.new('RGB', (cols*w, rows*h), 'black')
d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(f).convert('RGB').resize((w, h), Image.LANCZOS)
    sheet.paste(im, ((i%cols)*w, (i//cols)*h))
    d.text(((i%cols)*w+8, (i//cols)*h+8), f.split('/')[-1], fill='yellow')
sheet.save(sys.argv[1])
