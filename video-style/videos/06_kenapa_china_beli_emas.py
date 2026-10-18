#!/usr/bin/env python3
"""Video 6: 'Kenapa China masih beli emas walaupun harga jatuh?' (studio) in the Azlan & Eza style.

python3 build_v6.py --preview         -> storyboard stills (with TikTok safe-zone guides)
python3 build_v6.py --audio-preview   -> voice + sfx + music mix only
python3 build_v6.py                   -> full render
"""
import importlib.util, json, math, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_VS = os.path.join(HERE, '..')
WORK = os.path.join(HERE, '..', 'work', 'v6')   # raw footage, news screenshots, licensed music (not in git)
ASSETS = os.path.join(HERE, '06_assets')
sys.path.insert(0, REPO_VS)
import numpy as np
import build as B
from build import (W, H, FPS, OUTRO, RED, F_XB, F_B, Image, ImageDraw, ImageFilter, text_sprite, rounded,
                   with_shadow, place, pop, pill, check_icon, ease_out, back_out, font, paper_texture,
                   load_logos, outro_frame, write_sfx, composite, syllables)


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REPO_VS, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V3 = _load('v3', 'videos/03_konsisten_emas.py')
V5 = _load('v5', 'videos/05_jangan_simpan_dalam_bank.py')
x_icon, shine, badge, GOLD, GOLD_L = V3.x_icon, V3.shine, V3.badge, V3.GOLD, V3.GOLD_L
money_card, warn_icon, NAVY_C, ALERT = V5.money_card, V5.warn_icon, V5.NAVY_C, V5.ALERT

RAW = os.environ.get('RAW', os.path.join(WORK, 'raw.mp4'))
IMG1 = os.path.join(WORK, 'img1.jpg')   # screenshot: headline + gold-bar photo (has an ad in the middle: cropped out)
IMG2 = os.path.join(WORK, 'img2.jpg')   # screenshot: reserves value US$350.08b -> US$323.52b, gold -6% in Sept
CREDIT = 'Sumber: Reuters via The Edge Malaysia, 7 Okt 2026'
OUT = os.environ.get('OUT', os.path.join(WORK, 'out'))
MASK = os.path.join(HERE, '03_assets', 'facemask.png')   # same studio as videos 3 and 5
MUSIC = os.path.join(WORK, 'music.m4a')
# Descript stock (Audioblocks): "Technological Documentary (Loop)" x3 = 275s, -15.2 LUFS, seamless joins.
MUSIC_SS, MUSIC_DB, MUSIC_TEMPO = 0.0, -16.0, 1.0
os.makedirs(OUT, exist_ok=True)
GRADE, RELIGHT = V3.GRADE, V3.RELIGHT

# Descript SRT cues; "display~syllables" tokens show numbers compactly. All sentences kept (user rule: keep context).
CUES = [
    (0.234, 4.314, "Kenapa China masih membeli emas berpuluh-puluh tan walaupun"),
    (4.354, 5.774, "harga emas dunia sedang jatuh?"),
    (6.814, 9.814, "Adakah China tahu sesuatu yang kita tak tahu?"),
    (10.754, 16.834, "Menurut laporan Reuters bertarikh 7~1 Oktober 2026~6 bank pusat China"),
    (16.874, 22.294, "telah meningkatkan pembelian emas pada September, menjadikan pembelian"),
    (22.334, 26.994, "tersebut berterusan selama 23~5 bulan berturut-turut."),
    (28.134, 33.654, "Pegangan emas China meningkat daripada 76.73~9"),
    (33.714, 39.814, "juta kepada 77.47~9 juta Troy Ounce bersamaan"),
    (39.874, 45.114, "pertambahan kira-kira 23~5 tan emas dalam masa sebulan sahaja."),
    (46.918, 53.298, "Apa yang menarik, China terus membeli walaupun harga emas dunia telah jatuh"),
    (53.378, 56.478, "lebih 6%~4 sepanjang September."),
    (56.798, 63.578, "Malah, nilai rizab emas China turut menyusut daripada 350.08~9"),
    (63.698, 67.438, "bilion US Dollar kepada 323.52~10"),
    (67.498, 73.758, "bilion US Dollar, iaitu penurunan sekitar 26.56~10"),
    (74.618, 75.758, "bilion US Dollar."),
    (76.978, 84.898, "Pada 7~1 Oktober, harga emas spot pula dilaporkan sekitar 4,147.47~16"),
    (84.998, 86.498, "US Dollar se ounce."),
    (86.658, 91.418, "Persoalannya, kenapa China masih membeli emas walaupun nilainya sedang menurun?"),
    (91.838, 95.558, "Sebab China bukan sekadar melihat harga emas hari ini."),
    (95.777, 100.658, "China sedang melihat kedudukan kewangan negaranya untuk jangka masa panjang."),
    (101.658, 105.338, "Pertama, China mahu mengurangkan kebergantungan"),
    (105.378, 107.318, "kepada dolar Amerika Syarikat."),
    (108.118, 114.118, "Kedua, China mahu mempelbagaikan rizab negaranya supaya tidak terlalu"),
    (114.158, 116.158, "bergantung kepada satu jenis aset."),
    (117.058, 121.217, "Dan ketiga, emas fizikal yang dimiliki sendiri bukan"),
    (121.277, 123.798, "liabiliti mana-mana kerajaan."),
    (125.118, 130.318, "Sebab itulah emas mempunyai peranan penting dalam sistem kewangan dunia."),
    (131.338, 133.358, "Sekarang cuba kita fikir."),
    (133.578, 138.598, "Kalau sebuah negara yang mempunyai rizab kewangan begitu besar pun masih"),
    (138.618, 143.538, "melihat kepentingan menyimpan emas, bagaimana pula dengan kita yang sedang"),
    (143.618, 145.418, "membina simpanan untuk masa depan?"),
    (146.718, 150.938, "Ada satu pengajaran penting yang kita boleh ambil daripada tindakan"),
    (150.978, 153.518, "China dalam membina kekayaan."),
    (153.718, 160.378, "Jangan hanya fikir bagaimana untuk menambah nilai aset, tetapi fikir"),
    (160.438, 164.678, "juga bagaimana untuk melindungi kekayaan yang sudah kita bina."),
    (165.678, 171.958, "Bukan bermaksud semua duit perlu ditukarkan kepada emas, tetapi kita perlu"),
    (172.018, 174.737, "faham kepentingan mempelbagaikan simpanan."),
    (175.517, 179.318, "Sebab dalam pengurusan kewangan, bukan sekadar berapa banyak duit"),
    (179.358, 184.458, "yang kita ada, tetapi bagaimana kita mengurus dan melindungi kekayaan"),
    (184.498, 187.738, "tersebut untuk jangka masa panjang."),
    (187.978, 192.518, "Emas bukan segala-galanya, tetapi emas mempunyai peranan penting"),
    (192.578, 194.658, "dalam perancangan kewangan kita."),
]
B.SYL.update({'berpuluh-puluh': 6, 'berturut-turut': 6, 'kira-kira': 4, 'mana-mana': 4, 'segala-galanya': 6,
              'Troy': 1, 'Ounce': 1, 'US': 2, 'Dollar': 2, 'spot': 1, 'ounce': 1, 'Reuters': 2})


def build_segs():
    regs = json.load(open(os.path.join(ASSETS, 'edl_all.json')))['regs']
    keep = [[max(0, a - 0.08), b + 0.10] for a, b in regs if b > 0.15 and a < 194.9]
    segs = []
    for a, b in sorted(keep):
        if segs and a - segs[-1][1] < 0.18:
            segs[-1][1] = max(segs[-1][1], b)
        else:
            segs.append([a, b])
    zoom, z = [], 1.0
    for i, (a, b) in enumerate(segs):
        if i and a - segs[i - 1][1] >= 0.6:
            z = 1.06 if z == 1.0 else 1.0
        zoom.append(z)
    return [tuple(s) for s in segs], zoom


SEGS, ZOOM = build_segs()


def offsets():
    o, t = [], 0.0
    for a, b in SEGS:
        o.append(t)
        t += b - a
    return o, t


def src2out(x):
    offs, _ = offsets()
    for (a, b), o in zip(SEGS, offs):
        if a - 0.05 <= x <= b + 0.05:
            return o + min(max(x, a), b) - a
    for (a, b), o in zip(SEGS, offs):
        if x < a:
            return o
    return None


def out2src(t):
    offs, _ = offsets()
    for (a, b), o in zip(SEGS, offs):
        if o <= t < o + (b - a):
            return a + (t - o)
    return SEGS[-1][1]


def align_words():
    regs = json.load(open(os.path.join(ASSETS, 'edl_all.json')))['regs']
    out = []
    for s, e, text in CUES:
        toks, wts = [], []
        for raw in text.split():
            if '~' in raw:
                d, n = raw.split('~')
                toks.append(d.rstrip('.,?')), wts.append(int(n))
            else:
                t = raw.strip('.,?')
                toks.append(t), wts.append(syllables(t))
        rr = [(max(a, s - 0.05), min(b, e + 0.05)) for a, b in regs if b > s - 0.05 and a < e + 0.05]
        rr = [r for r in rr if r[1] - r[0] > 0.03] or [(s, e)]
        tot = sum(b - a for a, b in rr)
        cum = np.cumsum([0] + wts) / sum(wts) * tot

        def sp2t(x):
            for a, b in rr:
                if x <= (b - a) + 1e-9:
                    return a + x
                x -= (b - a)
            return rr[-1][1]
        for i, t in enumerate(toks):
            out.append({'w': t, 's': sp2t(cum[i] + 1e-4), 'e': sp2t(cum[i + 1])})
    for w in out:
        w['os'], w['oe'] = src2out(w['s']), src2out(w['e'])
    return [w for w in out if w['os'] is not None]


def vf_for(z):
    cw, ch = 1080 / z, 1920 / z
    x, y = (1080 - cw) / 2, min(max(0.40 * 1920 - ch / 2, 0), 1920 - ch)
    return f"crop={cw:.0f}:{ch:.0f}:{x:.0f}:{y:.0f},scale={W}:{H}:flags=lanczos,setsar=1"


def graded_filter(z):
    return (f"[0:v]{vf_for(z)},fps={FPS},{GRADE},split[a][b];[b]{RELIGHT}[bb];[1:v]format=gray[m];"
            f"[bb][m]alphamerge[lit];[a][lit]overlay=format=auto,vignette=PI/4.6,unsharp=5:5:0.35,format=yuv420p[v]")


def render_base():
    parts = []
    for i, ((a, b), z) in enumerate(zip(SEGS, ZOOM)):
        d = b - a
        p = os.path.join(OUT, f'seg{i}.mov')
        af = f"aresample=48000,afade=t=in:d=0.03,afade=t=out:st={d-0.03:.3f}:d=0.03"
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a}', '-t', f'{d}', '-i', RAW, '-loop', '1', '-i', MASK,
                        '-filter_complex', graded_filter(z) + f";[0:a]{af}[au]", '-map', '[v]', '-map', '[au]',
                        '-t', f'{d}', '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', '-c:a', 'pcm_s16le',
                        '-ac', '2', p], check=True)
        parts.append(p)
    lst = os.path.join(OUT, 'list.txt')
    open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy',
                    os.path.join(OUT, 'base.mov')], check=True)


def base_still(t):
    offs, _ = offsets()
    k = max(i for i, o in enumerate(offs) if o <= t)
    p = os.path.join(OUT, 'still.png')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{out2src(t)}', '-i', RAW, '-i', MASK,
                    '-filter_complex', graded_filter(ZOOM[k]), '-map', '[v]', '-frames:v', '1', p], check=True)
    return Image.open(p).convert('RGBA')


# ---------------------------------------------------------------- graphics
def fit_pill(text, icon=None, size=56, bg=None, maxw=840):
    """pill() that shrinks its font until it fits inside the TikTok safe width (left edge .. action rail)."""
    kw = {} if bg is None else {'bg': bg}
    while True:
        spr = pill(text, icon=icon, size=size, **kw)
        if spr.width - 64 <= maxw or size <= 30:
            return spr
        size -= 2


def cn_flag(w=96, h=64):
    im = Image.new('RGBA', (w, h), (222, 41, 16, 255))
    d = ImageDraw.Draw(im)

    def star(cx, cy, r, rot=0):
        pts = []
        for k in range(10):
            rr = r if k % 2 == 0 else r * 0.4
            a = -math.pi / 2 + rot + k * math.pi / 5
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.polygon(pts, fill=(255, 222, 0, 255))
    u = h / 20
    star(5 * u, 5 * u, 3 * u)
    for cx, cy in ((10, 2), (12, 4), (12, 7), (10, 9)):
        star(cx * u, cy * u, u, 0.4)
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 8, fill=255)
    im.putalpha(m)
    return im


def arrow_icon(s=60, up=True, col=(34, 197, 94)):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, s - 1, s - 1], fill=col + (255,))
    if up:
        d.polygon([(s / 2, s * .2), (s * .78, s * .55), (s * .22, s * .55)], fill=(255, 255, 255, 255))
        d.rectangle([s * .42, s * .5, s * .58, s * .8], fill=(255, 255, 255, 255))
    else:
        d.polygon([(s / 2, s * .8), (s * .78, s * .45), (s * .22, s * .45)], fill=(255, 255, 255, 255))
        d.rectangle([s * .42, s * .2, s * .58, s * .5], fill=(255, 255, 255, 255))
    return im


def news_card(p, head, gold):
    cw = 940
    pw = cw - 80
    hh = int(pw * head.height / head.width)
    gh = int(pw * 0.55)
    ch = 120 + hh + 24 + gh + 150
    im = rounded((cw, ch), 44, NAVY_C)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([40, 36, 260, 96], 30, fill=ALERT + (255,))
    d.text((150, 66), 'LAPORAN', font=font(F_XB, 32), fill=(255, 255, 255, 255), anchor='mm')
    k = ease_out(min(1, max(0, p) / 0.3))
    for img, y, hgt in ((head, 120, hh), (gold, 120 + hh + 24, gh)):
        z = 1.0 + 0.05 * max(0, p)
        src = img.resize((int(pw * z), int(pw * z * img.height / img.width)), Image.LANCZOS)
        top = (src.height - hgt) // 2
        src = src.crop(((src.width - pw) // 2, max(0, top), (src.width - pw) // 2 + pw, max(0, top) + hgt)).convert('RGBA')
        m = Image.new('L', src.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, src.width - 1, src.height - 1], 24, fill=int(255 * k))
        src.putalpha(m)
        im.alpha_composite(src, (40, y))
    y = 120 + hh + 24 + gh
    d.text((cw - 50, y + 14), CREDIT, font=font(F_B, 22), fill=(150, 154, 180, int(255 * k)), anchor='ra')
    kk = ease_out((p - 0.35) / 0.3)
    if kk > 0:
        d.text((cw / 2, y + 90 + (1 - kk) * 20), 'Bank pusat China tambah emas', font=font(F_XB, 46),
               fill=GOLD_L + (int(255 * kk),), anchor='mm')
    return with_shadow(im, 28, 16, 0.4)


def months_card(p):
    cw, ch = 900, 520
    im = rounded((cw, ch), 44, NAVY_C)
    d = ImageDraw.Draw(im)
    n = int(round(23 * ease_out(min(1, max(0, p) / 0.8))))
    d.text((cw / 2, 90), f'{n} BULAN', font=font(F_XB, 92), fill=GOLD_L + (255,), anchor='mm')
    d.text((cw / 2, 170), 'berturut-turut beli emas', font=font(F_B, 38), fill=(200, 202, 220, 255), anchor='mm')
    for i in range(23):
        r, c = divmod(i, 8)
        x, y = 90 + c * 100, 250 + r * 85
        on = i < n
        d.ellipse([x - 30, y - 30, x + 30, y + 30], fill=(GOLD + (255,)) if on else (45, 48, 70, 255))
        if on:
            d.line([(x - 13, y + 1), (x - 3, y + 11), (x + 14, y - 10)], fill=(30, 22, 10, 255), width=6)
    return with_shadow(im, 22, 12, 0.45)


def reserve_card(p, excerpt):
    """Cutaway: value of reserves US$350.08b -> US$323.52b (-26.56b) + the screenshot excerpt."""
    cw = 940
    pw = cw - 80
    eh = int(pw * excerpt.height / excerpt.width)
    ch = 110 + 2 * 170 + 120 + eh + 110
    im = rounded((cw, ch), 48, NAVY_C)
    d = ImageDraw.Draw(im)
    d.text((cw / 2, 70), 'NILAI RIZAB EMAS CHINA', font=font(F_XB, 52), fill=(255, 255, 255, 255), anchor='mm')
    rows = [('Ogos', 'USD 350.08 bilion', 1.0, (150, 160, 200)), ('September', 'USD 323.52 bilion', 323.52 / 350.08, (255, 130, 140))]
    for i, (lab, val, frac, col) in enumerate(rows):
        k = ease_out((p - i * 0.25) / 0.35)
        y = 130 + i * 170
        d.text((50, y), lab, font=font(F_B, 34), fill=(170, 172, 190, 255))
        d.text((cw - 50, y), val, font=font(F_XB, 40), fill=col + (255,), anchor='ra')
        d.rounded_rectangle([50, y + 62, cw - 50, y + 112], 25, fill=(45, 48, 70, 255))
        if k > 0.02:
            d.rounded_rectangle([50, y + 62, 50 + (cw - 100) * frac * k, y + 112], 25, fill=col + (255,))
    if p > 0.6:
        kk = back_out(min(1, (p - 0.6) / 0.2))
        tag = text_sprite('-USD 26.56 bilion', int(60 * max(0.05, kk)), (255, 160, 160), (240, 70, 80), stroke=4,
                          stroke_col=(40, 10, 10))
        im.alpha_composite(tag, (int(cw / 2 - tag.width / 2), int(500 - tag.height / 2)))
    y = 110 + 2 * 170 + 120
    ex = excerpt.resize((pw, eh), Image.LANCZOS).convert('RGBA')
    m = Image.new('L', ex.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, pw - 1, eh - 1], 20, fill=255)
    ex.putalpha(m)
    im.alpha_composite(ex, (40, y))
    d.text((cw - 50, y + eh + 16), CREDIT, font=font(F_B, 22), fill=(150, 154, 180, 255), anchor='ra')
    return with_shadow(im, 28, 16, 0.4)


def reasons_card(p, n_on):
    cw, ch = 900, 640
    im = rounded((cw, ch), 44, NAVY_C)
    d = ImageDraw.Draw(im)
    d.text((cw / 2, 70), 'KENAPA CHINA BELI EMAS?', font=font(F_XB, 48), fill=(255, 255, 255, 255), anchor='mm')
    items = [('Kurangkan bergantung', 'pada dolar AS'), ('Pelbagaikan rizab', 'bukan satu jenis aset'),
             ('Emas fizikal milik sendiri', 'bukan liabiliti mana-mana kerajaan')]
    for i, (a, b) in enumerate(items):
        if i >= n_on:
            continue
        y = 150 + i * 160
        d.rounded_rectangle([40, y, cw - 40, y + 135], 30, fill=(30, 33, 52, 255))
        d.rounded_rectangle([60, y + 20, 155, y + 115], 24, fill=GOLD + (255,))
        d.text((107, y + 68), str(i + 1), font=font(F_XB, 64), fill=(30, 22, 10, 255), anchor='mm')
        d.text((185, y + 48), a, font=font(F_XB, 42), fill=(255, 255, 255, 255), anchor='lm')
        d.text((185, y + 96), b, font=font(F_B, 32), fill=(170, 172, 190, 255), anchor='lm')
    return with_shadow(im, 22, 12, 0.45)


def main():
    preview = '--preview' in sys.argv
    if not preview and '--audio-preview' not in sys.argv and '--skip-base' not in sys.argv:
        render_base()
    words = align_words()
    json.dump(words, open(os.path.join(OUT, 'words.json'), 'w'), indent=1)
    offs, base_dur = offsets()
    total = base_dur + OUTRO

    def cue_t(i, end=False):
        return src2out(CUES[i][1] if end else CUES[i][0])

    def wt(word, nth=1):
        k = 0
        for w in words:
            if w['w'].lower() == word.lower():
                k += 1
                if k == nth:
                    return w['os']
        raise KeyError(word)

    gold_words = {'emas', 'fizikal', 'melindungi', 'mempelbagaikan', 'panjang', 'penting'}
    red_words = {'jatuh', 'menyusut', 'menurun', 'penurunan'}
    cap_cache = {}

    def cap(word):
        if word not in cap_cache:
            num = word[:1].isdigit()
            disp = word if num or word in ('China', 'Reuters', 'September', 'Oktober', 'US', 'Dollar', 'Troy', 'Ounce',
                                           'Amerika', 'Syarikat') else word.lower()
            sz = 104
            while font(F_XB, sz).getlength(disp) > 880:
                sz -= 4
            lw = word.lower()
            if lw in red_words:
                top, bot = (255, 150, 150), (240, 70, 80)
            elif lw in gold_words or num:
                top, bot = GOLD_L, GOLD
            else:
                top, bot = (255, 255, 255), (247, 228, 160)
            cap_cache[word] = text_sprite(disp, sz, top, bot, stroke=5, stroke_col=(25, 18, 20))
        return cap_cache[word]
    cap_win = []
    for i, w in enumerate(words):
        nxt = words[i + 1]['os'] if i + 1 < len(words) else w['oe'] + 0.3
        cap_win.append((w['os'], nxt if nxt - w['oe'] < 0.35 else w['oe'] + 0.15, w['w']))

    # sprites
    raw1 = Image.open(IMG1).convert('RGB')
    head = raw1.crop((0, 0, 1240, 420))
    gold_ph = raw1.crop((0, 930, 1290, 1710))
    excerpt = Image.open(IMG2).convert('RGB')
    h1 = text_sprite('KENAPA CHINA', 112, (255, 255, 255), (232, 232, 240))
    h2 = text_sprite('MASIH BELI EMAS', 104, GOLD_L, GOLD, stroke=5, stroke_col=(60, 40, 10))
    h3 = text_sprite('WALAUPUN HARGA JATUH?', 62, (255, 150, 150), (240, 70, 80), stroke=4, stroke_col=(255, 255, 255))
    flag = with_shadow(cn_flag(110, 74), 10, 5, 0.35)
    qmark = text_sprite('?', 300, GOLD_L, GOLD, stroke=8, stroke_col=(60, 40, 10))
    p_tahu = fit_pill('China tahu sesuatu?', size=60)
    c_oz = None
    p_tan = fit_pill('+ kira-kira 23 tan dalam sebulan', icon=arrow_icon(60), size=50, bg=(232, 190, 92, 255))
    p_drop = fit_pill('Harga emas jatuh lebih 6% (Sept)', icon=arrow_icon(60, False, (220, 38, 38)), size=48)
    p_spot = fit_pill('Harga spot 7 Okt: ~USD 4,147.47/oz', size=46)
    p_q2 = fit_pill('Kenapa masih beli?', size=60)
    p_today = fit_pill('Bukan harga hari ini', icon=x_icon(60), size=54)
    p_long = fit_pill('Kedudukan kewangan jangka panjang', icon=check_icon(60), size=46, bg=(232, 190, 92, 255))
    p_role = fit_pill('Emas: peranan penting dalam sistem kewangan dunia', size=38, bg=(232, 190, 92, 255))
    p_fikir = fit_pill('Sekarang cuba kita fikir...', size=56)
    p_negara = fit_pill('Negara sebesar China pun simpan emas', size=46)
    p_kita = fit_pill('Bagaimana dengan kita?', icon=warn_icon(60), size=56, bg=(232, 190, 92, 255))
    p_tambah = fit_pill('Tambah nilai aset', size=56)
    p_lindung = fit_pill('Lindungi kekayaan', icon=check_icon(60), size=56, bg=(232, 190, 92, 255))
    p_semua = fit_pill('Semua duit tukar ke emas', icon=x_icon(60), size=52)
    p_pelbagai = fit_pill('Pelbagaikan simpanan', icon=check_icon(60), size=56, bg=(232, 190, 92, 255))
    p_banyak = fit_pill('Bukan berapa banyak duit', icon=x_icon(60), size=52)
    p_urus = fit_pill('Cara urus & lindungi', icon=check_icon(60), size=56, bg=(232, 190, 92, 255))
    p_end1 = fit_pill('Emas bukan segala-galanya', size=54)
    p_end2 = fit_pill('Tapi peranan penting dalam perancangan', icon=check_icon(60), size=44, bg=(232, 190, 92, 255))
    logo_c, logo_w = load_logos()
    wm = logo_w.resize((150, int(150 * logo_w.height / logo_w.width)), Image.LANCZOS)
    paper = paper_texture(W, H)

    T = {'masih': wt('masih'), 'walaupun': wt('walaupun'), 'adakah': cue_t(2),
         'n_in': cue_t(3) - 0.05, 'n_out': cue_t(4, True) + 0.1,
         'm23': wt('23'), 'pegangan': cue_t(6), 'oz2': wt('77.47'), 'tan23': wt('23', 2),
         'menarik': cue_t(9), 'pct6': wt('6%'),
         'r_in': cue_t(11) - 0.05, 'r_out': cue_t(14, True) + 0.2,
         'spot': cue_t(15), 'persoalan': cue_t(17), 'sebab': cue_t(18), 'panjang1': cue_t(19),
         'q_in': cue_t(20) - 0.05, 'q_out': cue_t(25, True) + 0.2, 'kedua': cue_t(22), 'ketiga': cue_t(24),
         'peranan': cue_t(26), 'fikir': cue_t(27), 'negara': cue_t(28), 'kita': wt('bagaimana', 1),
         'ajar': cue_t(31), 'tambah': wt('menambah'), 'lindung': wt('melindungi'),
         'semua': cue_t(35), 'pelbagai': wt('mempelbagaikan', 2), 'banyak': cue_t(37), 'urus': wt('mengurus'),
         'end1': cue_t(40), 'end2': wt('tetapi', 4)}
    pops = [T[k] for k in ('masih', 'walaupun', 'adakah', 'm23', 'pegangan', 'tan23', 'pct6', 'spot', 'persoalan',
                           'sebab', 'panjang1', 'kedua', 'ketiga', 'peranan', 'fikir', 'kita', 'tambah', 'lindung',
                           'semua', 'pelbagai', 'banyak', 'urus', 'end1', 'end2')]
    whooshes = [(T['walaupun'] - 0.15, 0.4, 0.24)] + [(T[k + '_in'] - 0.12, 0.35, 0.18) for k in 'nrq'] + \
               [(T[k + '_out'] - 0.15, 0.35, 0.18) for k in 'nrq'] + [(base_dur - 0.15, 0.5, 0.22)]

    if '--audio-preview' in sys.argv:
        write_sfx(total, pops, whooshes, os.path.join(OUT, 'sfx.wav'))
        n = len(SEGS)
        chain = ''.join(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.03,"
                        f"afade=t=out:st={b-a-0.03:.3f}:d=0.03[s{i}];" for i, (a, b) in enumerate(SEGS))
        chain += ''.join(f'[s{i}]' for i in range(n)) + f'concat=n={n}:v=0:a=1[voice];'
        fc = chain + B.audio_mix_graph('[voice]', '[1:a]', total, '[2:a]', MUSIC_SS, MUSIC_DB, outro_at=base_dur,
                                       music_tempo=MUSIC_TEMPO)
        outp = os.path.join(OUT, 'PREVIEW_audio_music.m4a')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', RAW, '-i', os.path.join(OUT, 'sfx.wav'), '-i', MUSIC,
                        '-filter_complex', fc, '-map', '[a]', '-t', f'{total}', '-c:a', 'aac', '-b:a', '160k', outp],
                       check=True)
        print('audio preview', outp, 'total', round(total, 2))
        return

    def two(fr, t, a_spr, ta, b_spr, tb, end, ya=250, yb=390):
        s, a = pop(t, ta, end)
        place(fr, a_spr, B.TT_CENTER_X + 10, ya, s, a)
        s, a = pop(t, tb, end)
        place(fr, b_spr, B.TT_CENTER_X + 30, yb, s, a)

    def overlay(t):
        fr = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        if t >= base_dur:
            return outro_frame(t - base_dur, int(t * FPS), logo_w), False
        cut = None
        for a_, b_, kind in ((T['n_in'], T['n_out'], 'n'), (T['r_in'], T['r_out'], 'r'), (T['q_in'], T['q_out'], 'q')):
            if a_ <= t <= b_:
                cut = (a_, b_, kind)
        if cut:
            a_, b_, kind = cut
            k_in, k_out = ease_out((t - a_) / 0.22), ease_out((b_ - t) / 0.18)
            a = min(k_in, k_out)
            bgp = paper.copy()
            bgp.putalpha(int(255 * a))
            fr.alpha_composite(bgp)
            pr = (t - a_ - 0.15) / max(0.1, b_ - a_ - 0.7)
            if kind == 'n':
                card = news_card(pr, head, gold_ph)
            elif kind == 'r':
                card = reserve_card(pr, excerpt)
            else:
                n_on = 1 + (t >= T['kedua'] - 0.1) + (t >= T['ketiga'] - 0.1)
                card = reasons_card(pr, n_on)
            sc = min(0.9, (B.TT_BOTTOM - 260) / card.height)     # keep cards above the bottom UI block
            place(fr, card, B.TT_CENTER_X, 170 + card.height * sc / 2 + (1 - k_in) * 100, sc * (1.1 - 0.1 * k_in), a)
        else:
            # HOOK
            e0 = T['adakah'] - 0.05
            s, a = pop(t, 0.03, e0, 0.28, 0.12)
            place(fr, h1, B.TT_CENTER_X + 20, 240, s, a, rot=-3)
            s, a = pop(t, T['masih'] - 0.05, e0, 0.25, 0.12)
            place(fr, h2, B.TT_CENTER_X + 20, 365, s, a, rot=-3)
            s, a = pop(t, T['walaupun'] - 0.05, e0, 0.22, 0.12)
            if a:
                slam = 1 + 0.5 * max(0, 1 - (t - T['walaupun'] + 0.05) / 0.18)
                place(fr, h3, B.TT_CENTER_X + 20, 480, s * slam if s >= 1 else s, a, rot=-3)
            e1 = T['n_in']
            s, a = pop(t, T['adakah'], e1, 0.3)
            place(fr, qmark, B.TT_CENTER_X + 300, 470, s, a, rot=10 * math.sin(t * 5))
            place(fr, flag, B.TT_CENTER_X - 300, 420, s, a, rot=-6)
            place(fr, p_tahu, B.TT_CENTER_X, 260, s, a)
            # 23 bulan (after news cutaway, before pegangan)
            s, a = pop(t, T['n_out'], T['pegangan'] - 0.05)
            if a:
                place(fr, months_card((t - T['n_out']) / 1.2), B.TT_CENTER_X, 400, s * 0.9, a)
            # ounces + 23 tan
            e2 = T['menarik'] - 0.05
            s, a = pop(t, T['pegangan'] + 0.4, e2)
            if a:
                k = ease_out(min(1, max(0, t - T['oz2'] + 0.2) / 0.8))
                val = 76.73 + (77.47 - 76.73) * k
                place(fr, money_card(f'{val:.2f} juta oz', 'pegangan emas China (troy ounce)', GOLD_L, w=760),
                      B.TT_CENTER_X, 300, s, a)
            s, a = pop(t, T['tan23'] - 0.1, e2)
            place(fr, p_tan, B.TT_CENTER_X, 520, s, a)
            # -6%
            s, a = pop(t, T['pct6'] - 0.6, T['r_in'])
            place(fr, p_drop, B.TT_CENTER_X, 300, s, a)
            # spot price
            s, a = pop(t, T['spot'] + 1.0, T['persoalan'] - 0.05)
            place(fr, p_spot, B.TT_CENTER_X, 300, s, a)
            # persoalan / sebab / jangka panjang
            s, a = pop(t, T['persoalan'], T['sebab'] - 0.05, 0.3)
            place(fr, p_q2, B.TT_CENTER_X, 260, s, a)
            place(fr, qmark, B.TT_CENTER_X + 300, 440, s * 0.6, a, rot=10 * math.sin(t * 5))
            two(fr, t, p_today, T['sebab'] + 0.3, p_long, T['panjang1'] + 0.6, T['q_in'])
            # after reasons cutaway
            s, a = pop(t, T['peranan'] + 0.3, T['fikir'] - 0.05)
            place(fr, p_role, B.TT_CENTER_X, 300, s, a)
            s, a = pop(t, T['fikir'], T['negara'] - 0.05)
            place(fr, p_fikir, B.TT_CENTER_X, 300, s, a)
            two(fr, t, p_negara, T['negara'] + 0.4, p_kita, T['kita'] - 0.1, T['ajar'] - 0.05)
            two(fr, t, p_tambah, T['tambah'] - 0.1, p_lindung, T['lindung'] - 0.1, T['semua'] - 0.05)
            two(fr, t, p_semua, T['semua'] + 0.6, p_pelbagai, T['pelbagai'] - 0.1, T['banyak'] - 0.05)
            two(fr, t, p_banyak, T['banyak'] + 1.2, p_urus, T['urus'] - 0.1, T['end1'] - 0.05)
            two(fr, t, p_end1, T['end1'], p_end2, T['end2'] - 0.1, base_dur - 0.02)
            place(fr, wm, 95, 1010, 0.85, 0.85)
        for a0, a1, w in cap_win:
            if a0 <= t < a1:
                k = (t - a0) / 0.09
                place(fr, cap(w), W / 2, B.TT_CAPTION_Y, 0.82 + 0.18 * back_out(min(1, k)) if k < 1 else 1, 1)
                break
        for o, z0, z1 in zip(offs[1:], ZOOM[:-1], ZOOM[1:]):
            if z0 != z1 and abs(t - o) < 0.05:
                fr.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(60 * (1 - abs(t - o) / 0.05)))))
        return fr, True

    if preview:
        shots = [('Hook', T['walaupun'] + 0.6), ('China tahu sesuatu?', T['adakah'] + 1.2),
                 ('Cutaway: laporan Reuters', T['n_out'] - 0.5), ('23 bulan', T['pegangan'] - 0.3),
                 ('Pegangan + 23 tan', T['menarik'] - 0.4), ('Harga -6%', T['r_in'] - 0.3),
                 ('Cutaway: nilai rizab', T['r_out'] - 0.5), ('Harga spot', T['persoalan'] - 0.3),
                 ('Kenapa masih beli?', T['sebab'] - 0.3), ('Jangka panjang', T['q_in'] - 0.3),
                 ('Cutaway: 3 sebab', T['q_out'] - 0.5), ('Kita fikir', T['ajar'] - 0.4),
                 ('Tambah vs lindungi', T['semua'] - 0.4), ('Pelbagaikan', T['banyak'] - 0.4),
                 ('Urus & lindungi', T['end1'] - 0.4), ('Penutup', base_dur - 0.4), ('Outro', base_dur + 1.6)]
        tiles_ = []
        sx = 360 / 1080
        for label, t in shots:
            ov, has_base = overlay(t)
            fr = base_still(t) if has_base else Image.new('RGBA', (W, H), (0, 0, 0, 255))
            fr.alpha_composite(ov)
            tile = fr.resize((360, 640), Image.LANCZOS)
            g = Image.new('RGBA', tile.size, (0, 0, 0, 0))
            gd = ImageDraw.Draw(g)
            for z in ((0, 0, 1080, B.TT_TOP), (0, B.TT_BOTTOM, 1080, 1920), (B.TT_RIGHT, B.TT_RAIL_Y[0], 1080, B.TT_RAIL_Y[1])):
                gd.rectangle([v * sx for v in z], fill=(255, 0, 60, 60), outline=(255, 0, 60, 200), width=2)
            tile.alpha_composite(g)
            mm, ss = divmod(t, 60)
            t2 = Image.new('RGB', (360, 684), (24, 24, 30))
            t2.paste(tile.convert('RGB'), (0, 0))
            ImageDraw.Draw(t2).text((6, 662), f'{int(mm)}:{ss:04.1f}  {label}', font=font(F_B, 21), fill=(255, 255, 255), anchor='lm')
            tiles_.append(t2)
        cols = 9
        rows = math.ceil(len(tiles_) / cols)
        sheet = Image.new('RGB', (cols * 372 + 12, rows * 696 + 12), (24, 24, 30))
        for i, tl in enumerate(tiles_):
            sheet.paste(tl, (12 + (i % cols) * 372, 12 + (i // cols) * 696))
        sheet.save(os.path.join(OUT, 'preview_storyboard.jpg'), quality=88)
        print('preview ok; segments', len(SEGS), 'base', round(base_dur, 2), 'total', round(total, 2))
        return

    fdir = os.path.join(OUT, 'frames')
    os.makedirs(fdir, exist_ok=True)
    for fi in range(int(round(total * FPS))):
        ov, _ = overlay(fi / FPS)
        ov.save(os.path.join(fdir, f'f{fi:05d}.png'), compress_level=1)
    write_sfx(total, pops, whooshes, os.path.join(OUT, 'sfx.wav'))
    final = os.path.join(OUT, 'KenapaChinaBeliEmas_AzlanEza.mp4')
    composite(os.path.join(OUT, 'base.mov'), fdir, os.path.join(OUT, 'sfx.wav'), total, final,
              music=MUSIC if os.path.exists(MUSIC) else None, music_ss=MUSIC_SS, music_db=MUSIC_DB, music_tempo=MUSIC_TEMPO)
    print('done', final)


if __name__ == '__main__':
    main()
