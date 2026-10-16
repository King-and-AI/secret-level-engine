import asyncio, sys, json, base64, subprocess, os, time
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))

async def main():
    mode = sys.argv[1]  # 'stills' or 'video'
    cf = os.path.join(HERE, os.environ.get('CUES', 'cues.json'))
    cues = json.load(open(cf)) if os.path.exists(cf) else {}
    async with async_playwright() as p:
        # Uses Playwright's own Chromium; if that download is missing, falls back to an installed Chrome (CHROME_BIN).
        exe = os.environ.get('CHROME_BIN', '/opt/google/chrome/chrome')
        launch = dict(args=['--allow-file-access-from-files', '--disable-web-security', '--no-sandbox', '--disable-gpu'])
        try:
            b = await p.chromium.launch(**launch)
        except Exception:
            if not os.path.exists(exe): raise
            b = await p.chromium.launch(executable_path=exe, **launch)
        pg = await b.new_page(viewport={'width': 1920, 'height': 1080})
        pg.on('pageerror', lambda e: print('PAGEERROR', e, flush=True))
        await pg.add_init_script(f'window.CUE_OVERRIDE = {json.dumps(cues)}; window.VARIANT = {json.dumps(os.environ.get("VARIANT", "base"))};')
        await pg.goto('file://' + os.path.join(HERE, 'index.html'))
        ok = await pg.evaluate('fontsReady()')
        print('fonts', ok, flush=True)
        if mode == 'stills':
            times = [float(x) for x in sys.argv[2].split(',')]
            os.makedirs(os.path.join(HERE, 'stills'), exist_ok=True)
            for t in times:
                data = await pg.evaluate(f'(render({t}), document.getElementById("c").toDataURL("image/png"))')
                open(os.path.join(HERE, 'stills', f't{t:06.2f}.png'), 'wb').write(base64.b64decode(data.split(',')[1]))
            print('done stills')
        else:
            fps = 30
            end = await pg.evaluate('window.CUE.END')
            n = int(round(end * fps))
            out = sys.argv[2]
            ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(fps), '-c:v', 'mjpeg', '-i', '-',
                                   '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', str(fps), out], stdin=subprocess.PIPE)
            t0 = time.time()
            for i in range(n):
                t = i / fps
                data = await pg.evaluate(f'(render({t}), document.getElementById("c").toDataURL("image/jpeg", 0.96))')
                ff.stdin.write(base64.b64decode(data.split(',')[1]))
                if i % 150 == 0:
                    print(f'frame {i}/{n} {time.time()-t0:.1f}s', flush=True)
            ff.stdin.close(); ff.wait()
            print('video done', n, 'frames', f'{time.time()-t0:.1f}s')
        await b.close()

asyncio.run(main())
