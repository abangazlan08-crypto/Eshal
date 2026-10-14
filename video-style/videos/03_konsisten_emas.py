#!/usr/bin/env python3
"""Video 3: 3 kelebihan simpan emas secara konsisten (studio, Public Gold) in the Azlan & Eza style.

python3 build_v3.py --preview   -> storyboard stills only (no video render)
python3 build_v3.py             -> full render
"""
import json, math, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np
import build as B
from build import (W, H, FPS, OUTRO, RED, F_XB, F_B, Image, ImageDraw, ImageFilter, text_sprite, rounded,
                   with_shadow, place, pop, pill, check_icon, ease_out, back_out, font, paper_texture,
                   load_logos, outro_frame, write_sfx, composite, syllables)

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, '..', 'work', 'v3')   # raw footage + photos (not in git)
ASSETS = os.path.join(HERE, '03_assets')
RAW = os.environ.get('RAW', os.path.join(WORK, 'raw.mp4'))
IMG1 = os.path.join(WORK, 'img1.jpg')   # 10g bar engraved AZLAN
IMG2 = os.path.join(WORK, 'img2.jpg')   # 10g bar engraved KHADIZAH
OUT = os.environ.get('OUT', os.path.join(WORK, 'out'))
os.makedirs(OUT, exist_ok=True)
GOLD = (232, 190, 92)
GOLD_L = (255, 232, 160)

# Descript SRT cues (source time). Cue "Kita tak perlu" (30.28) and the "...ketepi-- Ya Allah" take
# (46.44-50.26) are repeats/false starts and are left out.
CUES = [
    (0.862, 3.002, "Ramai yang faham emas itu bagus."),
    (3.402, 7.042, "Tapi yang betul-betul nampak hasilnya hanyalah mereka yang konsisten."),
    (7.502, 11.742, "Bukan yang beli sekali dua, tapi yang simpan setiap bulan tanpa gagal."),
    (12.722, 15.482, "Inilah kelebihan menabung emas secara konsisten."),
    (16.201, 22.082, "Pertama, kita secara automatik mengamalkan dollar cost averaging."),
    (22.782, 28.042, "Beli masa harga tinggi, beli juga masa harga rendah dan purata kos kita jadi"),
    (28.082, 29.702, "lebih baik dalam jangka masa panjang."),
    (34.282, 37.682, "Kita tak perlu teka-teka bila masa yang sesuai nak beli."),
    (38.582, 43.942, "Kedua, konsistensi membina disiplin kewangan yang sukar"),
    (43.982, 45.762, "dibina dengan cara yang lain."),
    (51.182, 56.722, "Bila dah jadi rutin, kita tak rasa berat pun nak ketepikan jumlah itu setiap bulan."),
    (57.542, 63.802, "Ketiga, dan ini yang paling penting, masa adalah rakan terbaik simpanan emas."),
    (64.141, 68.301, "Semakin awal dan semakin konsisten kita mula, semakin besar manfaat"),
    (68.362, 70.442, "kenaikan harga emas yang kita nikmati."),
    (71.222, 76.182, "Bukan tentang berapa banyak kita simpan sekaligus, tapi tentang seberapa"),
    (76.242, 78.642, "konsisten kita lakukan setiap bulan."),
    (79.442, 81.422, "Nak bermula simpan emas hari ini?"),
    (81.922, 83.801, "Kami akan bantu sebaiknya."),
]
B.SYL.update({'dollar': 2, 'cost': 1, 'averaging': 4, 'teka-teka': 4, 'betul-betul': 4})
# keep ranges from speech-energy analysis (edl.json), with the two false starts trimmed out
SEGS = [(0.74, 11.81), (12.02, 15.61), (16.0, 22.09), (22.6, 24.54), (24.7, 29.85), (34.16, 37.76),
        (38.21, 39.11), (39.43, 45.81), (51.05, 56.77), (57.42, 60.22), (60.62, 70.5), (70.76, 78.67),
        (79.06, 83.82)]
ZOOM = [1.0, 1.06, 1.0, 1.06, 1.0, 1.06, 1.0, 1.06, 1.0, 1.06, 1.0, 1.06, 1.0]
GRADE = ("eq=brightness=-0.035:contrast=1.10:saturation=1.08:gamma=0.97,"
         "colorbalance=rs=0.03:bs=-0.04:rm=0.03:bm=-0.02:bh=0.02,"
         "curves=master='0/0 0.25/0.21 0.5/0.5 0.78/0.82 1/0.97'")
RELIGHT = "eq=brightness=0.055:gamma=1.10:saturation=1.03,colorbalance=rm=0.015:bm=-0.01"
MASK = os.path.join(ASSETS, 'facemask.png')


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
    return None


def out2src(t):
    offs, _ = offsets()
    for (a, b), o in zip(SEGS, offs):
        if o <= t < o + (b - a):
            return a + (t - o)
    return SEGS[-1][1]


def align_words():
    regs = json.load(open(os.path.join(ASSETS, 'edl.json')))['regs']
    out = []
    for s, e, text in CUES:
        toks = [t.strip('.,?') for t in text.split()]
        wts = [syllables(t) for t in toks]
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
    """Graded source frame for output time t (preview mode)."""
    offs, _ = offsets()
    k = max(i for i, o in enumerate(offs) if o <= t)
    src = out2src(t)
    p = os.path.join(OUT, 'still.png')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{src}', '-i', RAW, '-i', MASK,
                    '-filter_complex', graded_filter(ZOOM[k]), '-map', '[v]', '-frames:v', '1', p], check=True)
    return Image.open(p).convert('RGBA')


# ---------------------------------------------------------------- graphics
def x_icon(s=58):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, s - 1, s - 1], fill=(220, 38, 38, 255))
    k = s * 0.3
    d.line([(k, k), (s - k, s - k)], fill=(255, 255, 255, 255), width=max(4, s // 9))
    d.line([(s - k, k), (k, s - k)], fill=(255, 255, 255, 255), width=max(4, s // 9))
    return im


def photo_card(path, w=420, rot_crop=None):
    im = Image.open(path).convert('RGB')
    # crop to the bar itself (bar sits roughly in the middle of the photo)
    iw, ih = im.size
    im = im.crop((int(iw * .08), int(ih * .14), int(iw * .92), int(ih * .86)))
    h = int(w * im.height / im.width)
    im = im.resize((w, h), Image.LANCZOS).convert('RGBA')
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 28, fill=255)
    im.putalpha(m)
    frame = rounded((w + 24, h + 24), 36, (255, 255, 255, 255))
    frame.alpha_composite(im, (12, 12))
    return frame


def shine(card, p):
    """Diagonal gold glint sweeping across a card, p in 0..1."""
    if not 0 < p < 1:
        return card
    c = card.copy()
    w, h = c.size
    band = Image.new('L', (w, h), 0)
    x = int(-w * 0.4 + p * w * 1.8)
    ImageDraw.Draw(band).polygon([(x, 0), (x + 90, 0), (x + 90 - h // 2, h), (x - h // 2, h)], fill=150)
    band = band.filter(ImageFilter.GaussianBlur(18))
    band = Image.fromarray(np.minimum(np.asarray(band), np.asarray(c.getchannel('A'))))
    glint = Image.new('RGBA', (w, h), (255, 248, 220, 255))
    glint.putalpha(band)
    c.alpha_composite(glint)
    return c


def badge(num, label, sub=None):
    f1, f2 = font(F_XB, 92), font(F_XB, 58)
    lw = int(f2.getlength(label))
    w, h = 190 + lw + 70, 170
    im = rounded((w, h), 40, (16, 18, 34, 240))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([18, 18, 152, 152], 30, fill=GOLD + (255,))
    d.text((85, 88), num, font=f1, fill=(30, 22, 10, 255), anchor='mm')
    d.text((190, 85 if not sub else 64), label, font=f2, fill=(255, 255, 255, 255), anchor='lm')
    if sub:
        d.text((192, 122), sub, font=font(F_B, 34), fill=GOLD_L + (255,), anchor='lm')
    return with_shadow(im, 20, 10, 0.45)


def dca_card(p):
    """Price line with equal monthly buys at high and low prices and the average-cost line (no figures)."""
    cw, ch = 920, 980
    im = rounded((cw, ch), 48, (18, 20, 36, 255))
    d = ImageDraw.Draw(im)
    d.text((cw / 2, 90), 'DOLLAR COST AVERAGING', font=font(F_XB, 52), fill=(255, 255, 255, 255), anchor='mm')
    d.text((cw / 2, 150), 'beli setiap bulan, harga naik atau turun', font=font(F_B, 32), fill=(150, 154, 180, 255), anchor='mm')
    x0, x1, yc = 80, cw - 80, 520
    xs = np.linspace(x0, x1, 300)
    ys = yc - 150 * np.sin((xs - x0) / (x1 - x0) * math.pi * 2.6) * np.linspace(1, 0.75, 300) - (xs - x0) * 0.10
    pe = ease_out(min(1, p / 0.6))
    nshow = max(2, int(300 * pe))
    d.line(list(zip(xs[:nshow], ys[:nshow])), fill=(150, 160, 200, 255), width=7, joint='curve')
    buys = np.linspace(0, 299, 9).astype(int)
    for k, bi in enumerate(buys):
        if bi < nshow:
            d.ellipse([xs[bi] - 17, ys[bi] - 17, xs[bi] + 17, ys[bi] + 17], fill=GOLD + (255,), outline=(255, 255, 255, 255), width=5)
    hi, lo = int(np.argmin(ys)), int(np.argmax(ys))
    if nshow > hi:
        d.text((xs[hi], ys[hi] - 52), 'harga tinggi', font=font(F_B, 30), fill=(255, 255, 255, 255), anchor='mm')
    if nshow > lo:
        d.text((xs[lo], ys[lo] + 54), 'harga rendah', font=font(F_B, 30), fill=(255, 255, 255, 255), anchor='mm')
    if p > 0.65:
        k = ease_out((p - 0.65) / 0.25)
        avg = float(np.mean(ys[buys]))
        xe = x0 + (x1 - x0) * k
        for xx in range(int(x0), int(xe), 34):
            d.line([(xx, avg), (min(xx + 20, xe), avg)], fill=GOLD_L + (255,), width=6)
        if k > 0.9:
            d.rounded_rectangle([cw / 2 - 170, avg + 22, cw / 2 + 170, avg + 82], 30, fill=GOLD + (255,))
            d.text((cw / 2, avg + 52), 'purata kos', font=font(F_XB, 34), fill=(30, 22, 10, 255), anchor='mm')
    d.rounded_rectangle([cw / 2 - 300, ch - 140, cw / 2 + 300, ch - 60], 40, fill=(255, 255, 255, 255))
    d.text((cw / 2, ch - 100), 'lebih baik jangka masa panjang', font=font(F_B, 34), fill=(25, 25, 35, 255), anchor='mm')
    return with_shadow(im, 28, 16, 0.4)


MONTHS = ['Jan', 'Feb', 'Mac', 'Apr', 'Mei', 'Jun', 'Jul', 'Ogo', 'Sep', 'Okt', 'Nov', 'Dis']


def calendar_card(p):
    cw, ch = 940, 390
    im = rounded((cw, ch), 40, (16, 18, 34, 240))
    d = ImageDraw.Draw(im)
    d.text((44, 30), 'RUTIN SETIAP BULAN', font=font(F_XB, 44), fill=(255, 255, 255, 255))
    n = int(12 * min(1, max(0, p)) + 0.001)
    for i, mo in enumerate(MONTHS):
        r, c = divmod(i, 6)
        x, y = 44 + c * 145, 110 + r * 135
        on = i < n
        d.rounded_rectangle([x, y, x + 125, y + 115], 22, fill=(GOLD + (255,)) if on else (45, 48, 70, 255))
        d.text((x + 62, y + 36), mo, font=font(F_B, 30), fill=(30, 22, 10, 255) if on else (170, 172, 190, 255), anchor='mm')
        if on:
            d.line([(x + 40, y + 80), (x + 56, y + 94), (x + 86, y + 64)], fill=(30, 22, 10, 255), width=7)
    return with_shadow(im, 20, 10, 0.45)


def growth_card(p, photo):
    cw, ch = 920, 1000
    im = rounded((cw, ch), 48, (18, 20, 36, 255))
    d = ImageDraw.Draw(im)
    d.text((cw / 2, 88), 'MASA = RAKAN TERBAIK', font=font(F_XB, 56), fill=(255, 255, 255, 255), anchor='mm')
    d.text((cw / 2, 148), 'semakin awal & konsisten, semakin besar manfaat', font=font(F_B, 30), fill=(150, 154, 180, 255), anchor='mm')
    x0, x1, yb = 90, cw - 90, 880
    xs = np.linspace(0, 1, 200)
    ys = yb - 520 * (xs ** 2.2)
    pe = ease_out(min(1, p / 0.8))
    nshow = max(2, int(200 * pe))
    pts = list(zip(x0 + xs[:nshow] * (x1 - x0), ys[:nshow]))
    poly = pts + [(pts[-1][0], yb), (x0, yb)]
    fill = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(fill).polygon(poly, fill=GOLD + (70,))
    im.alpha_composite(fill)
    d.line(pts, fill=GOLD_L + (255,), width=9, joint='curve')
    d.line([(x0, yb), (x1, yb)], fill=(80, 84, 110, 255), width=4)
    d.text((x0, yb + 40), 'mula awal', font=font(F_B, 30), fill=(170, 172, 190, 255), anchor='lm')
    d.text((x1, yb + 40), 'masa', font=font(F_B, 30), fill=(170, 172, 190, 255), anchor='rm')
    if p > 0.25:
        k = back_out(min(1, (p - 0.25) / 0.25))
        ph = photo.resize((max(1, int(photo.width * 0.9 * k)), max(1, int(photo.height * 0.9 * k))), Image.BICUBIC)
        ph = ph.rotate(-6, resample=Image.BICUBIC, expand=True)
        im.alpha_composite(ph, (int(280 - ph.width / 2), int(500 - ph.height / 2)))
    return with_shadow(im, 28, 16, 0.4)


def main():
    preview = '--preview' in sys.argv
    if not preview and '--skip-base' not in sys.argv:
        render_base()
    words = align_words()
    json.dump(words, open(os.path.join(OUT, 'words.json'), 'w'), indent=1)
    offs, base_dur = offsets()
    total = base_dur + OUTRO
    seg_t = [(o, o + (b - a)) for (a, b), o in zip(SEGS, offs)]

    def wt(word, nth=1, end=False):
        k = 0
        for w in words:
            if w['w'].lower() == word.lower():
                k += 1
                if k == nth:
                    return w['oe'] if end else w['os']
        raise KeyError(word)

    def cue_t(i, end=False):
        return src2out(CUES[i][1] if end else CUES[i][0])

    cap_cache = {}

    def cap(word):
        if word not in cap_cache:
            disp = word.lower()
            sz = 104
            while font(F_XB, sz).getlength(disp) > 900:
                sz -= 4
            gold = word.lower() in ('konsisten', 'emas', 'setiap', 'bulan', 'disiplin', 'masa', 'automatik')
            cap_cache[word] = text_sprite(disp, sz, (255, 255, 255) if not gold else GOLD_L,
                                          (247, 228, 160) if not gold else GOLD, stroke=5, stroke_col=(25, 18, 20))
        return cap_cache[word]
    cap_win = []
    for i, w in enumerate(words):
        nxt = words[i + 1]['os'] if i + 1 < len(words) else w['oe'] + 0.3
        cap_win.append((w['os'], nxt if nxt - w['oe'] < 0.35 else w['oe'] + 0.15, w['w']))

    # ---- sprites
    h1 = text_sprite('RAMAI FAHAM', 120, (255, 255, 255), (232, 232, 240))
    h2 = text_sprite('EMAS ITU BAGUS', 116, GOLD_L, GOLD, stroke=5, stroke_col=(60, 40, 10))
    h3 = text_sprite('TAPI...', 150, (255, 255, 255), (232, 232, 240))
    h4 = text_sprite('KONSISTEN', 176, GOLD_L, GOLD, stroke=7, stroke_col=(60, 40, 10))
    p_once = pill('Beli sekali dua', icon=x_icon(60), size=56)
    p_month = pill('Simpan setiap bulan', icon=check_icon(60), size=56)
    card1, card2 = photo_card(IMG1, 360), photo_card(IMG2, 360)
    big1, big2 = photo_card(IMG1, 470), photo_card(IMG2, 470)
    t3 = text_sprite('3 KELEBIHAN', 130, GOLD_L, GOLD, stroke=6, stroke_col=(60, 40, 10))
    nums = [badge('1', '', None), badge('2', '', None), badge('3', '', None)]
    b1 = badge('1', 'Dollar Cost', 'Averaging')
    b2 = badge('2', 'Disiplin', 'kewangan')
    b3 = badge('3', 'Masa', 'rakan terbaik')
    hot = pill('Paling penting!', size=50, bg=(232, 190, 92, 255))
    p_teka = pill('Tak perlu teka bila nak beli', icon=x_icon(60), size=52)
    p_lump = pill('Simpan sekaligus', icon=x_icon(60), size=56)
    p_cons = pill('Konsisten setiap bulan', icon=check_icon(60), size=56)
    p_cta = pill('Nak mula simpan emas hari ini?', size=52)
    p_help = pill('Kami akan bantu sebaiknya', icon=check_icon(60), size=52, bg=(232, 190, 92, 255))
    logo_c, logo_w = load_logos()
    wm = logo_w.resize((150, int(150 * logo_w.height / logo_w.width)), Image.LANCZOS)
    paper = paper_texture(W, H)

    T = {
        'tapi': wt('Tapi'), 'konsisten': wt('konsisten'), 'bukan': wt('Bukan'), 'simpan': wt('simpan'),
        'inilah': cue_t(3), 'pertama': cue_t(4), 'dollar': wt('dollar'),
        'dca_in': cue_t(5) - 0.05, 'dca_out': seg_t[4][1],
        'teka': cue_t(7), 'kedua': cue_t(8), 'rutin': cue_t(10), 'ketiga': cue_t(11), 'penting': wt('penting'),
        'grow_in': cue_t(12) - 0.05, 'grow_out': cue_t(13, True) + 0.1,
        'bukan2': cue_t(14), 'konsisten2': cue_t(15), 'cta': cue_t(16), 'kami': cue_t(17),
    }

    def overlay(t):
        fr = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        if t >= base_dur:
            return outro_frame(t - base_dur, int(t * FPS), logo_w), False
        cut = None
        for a_, b_, kind in ((T['dca_in'], T['dca_out'], 'dca'), (T['grow_in'], T['grow_out'], 'grow')):
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
            card = dca_card(pr) if kind == 'dca' else growth_card(pr, card2)
            place(fr, card, W / 2, H * 0.43 + (1 - k_in) * 120, 1.12 - 0.12 * k_in, a)
        else:
            # HOOK: "RAMAI FAHAM / EMAS ITU BAGUS" -> "TAPI..." -> "KONSISTEN" slam
            s, a = pop(t, 0.03, T['tapi'] - 0.05, 0.28, 0.12)
            place(fr, h1, W / 2 - 40, 220, s, a, rot=3)
            s, a = pop(t, 0.18, T['tapi'] - 0.05, 0.28, 0.12)
            place(fr, h2, W / 2 + 40, 360, s, a, rot=3)
            s, a = pop(t, T['tapi'], T['konsisten'] - 0.05, 0.22, 0.1)
            place(fr, h3, W / 2, 300, s, a, rot=-3)
            hk_end = seg_t[0][0] + (CUES[2][0] - SEGS[0][0]) - 0.05
            s, a = pop(t, T['konsisten'] - 0.04, hk_end, 0.22, 0.15)
            if a:
                slam = 1 + 0.6 * max(0, 1 - (t - T['konsisten'] + 0.04) / 0.18)
                place(fr, shine(h4, (t - T['konsisten'] - 0.2) / 0.6), W / 2, 300, s * slam if s >= 1 else s, a)
            # sekali dua vs setiap bulan + AZLAN bar
            e2 = seg_t[0][1] - 0.05
            s, a = pop(t, T['bukan'], e2)
            place(fr, p_once, W / 2 - 170, 230, s, a)
            s, a = pop(t, T['simpan'] - 0.05, e2)
            place(fr, p_month, W / 2 - 110, 360, s, a)
            s, a = pop(t, T['simpan'] + 0.1, e2, 0.34)
            place(fr, shine(card1, (t - T['simpan'] - 0.5) / 0.7), W - 165, 600, s * 0.72, a, rot=-8)
            # 3 kelebihan
            e3 = seg_t[1][1] - 0.05
            s, a = pop(t, T['inilah'], e3)
            place(fr, t3, W / 2, 250, s, a, rot=-2)
            for i in range(3):
                s, a = pop(t, T['inilah'] + 0.6 + i * 0.35, e3)
                place(fr, nums[i], W / 2 - 230 + i * 230, 440, s * 0.85, a)
            # 01 DCA
            s, a = pop(t, T['pertama'], T['dca_in'])
            place(fr, b1, W / 2, 300, s, a)
            # tak perlu teka
            s, a = pop(t, T['teka'], seg_t[5][1] - 0.04)
            place(fr, p_teka, W / 2, 300, s, a)
            # 02 disiplin
            s, a = pop(t, T['kedua'], seg_t[7][1] - 0.04)
            place(fr, b2, W / 2, 300, s, a)
            # rutin calendar
            r0, r1 = T['rutin'], seg_t[8][1] - 0.04
            s, a = pop(t, r0, r1)
            if a:
                place(fr, calendar_card((t - r0 - 0.3) / max(0.1, r1 - r0 - 0.9)), W / 2, 360, s, a)
            # 03 masa
            s, a = pop(t, T['ketiga'], T['grow_in'])
            place(fr, b3, W / 2, 290, s, a)
            s, a = pop(t, T['penting'] - 0.1, T['grow_in'], 0.3)
            place(fr, hot, W / 2 + 200, 460, s, a, rot=-6)
            # sekaligus vs setiap bulan
            e11 = seg_t[11][1] - 0.04
            s, a = pop(t, T['bukan2'] + 0.4, e11)
            place(fr, p_lump, W / 2 - 120, 250, s, a)
            s, a = pop(t, T['konsisten2'] - 0.05, e11)
            place(fr, p_cons, W / 2 + 60, 390, s, a)
            # CTA with both bars
            e12 = seg_t[12][1] - 0.02
            s, a = pop(t, T['cta'], T['kami'] - 0.05)
            place(fr, p_cta, W / 2, 230, s, a)
            s, a = pop(t, T['cta'] + 0.3, e12, 0.34)
            place(fr, shine(big1, (t - T['cta'] - 0.8) / 0.7), W / 2 - 220, 520, s * 0.72, a, rot=-7)
            s, a = pop(t, T['cta'] + 0.5, e12, 0.34)
            place(fr, shine(big2, (t - T['cta'] - 1.0) / 0.7), W / 2 + 220, 540, s * 0.72, a, rot=6)
            s, a = pop(t, T['kami'] - 0.05, e12)
            place(fr, p_help, W / 2, 230, s, a)
            place(fr, wm, W - 110, H - 300, 1, 0.9)
        for a0, a1, w in cap_win:
            if a0 <= t < a1:
                k = (t - a0) / 0.09
                place(fr, cap(w), W / 2, H * 0.80, 0.82 + 0.18 * back_out(min(1, k)) if k < 1 else 1, 1)
                break
        for o in offs[1:]:
            if abs(t - o) < 0.05:
                fr.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(60 * (1 - abs(t - o) / 0.05)))))
        return fr, True

    if preview:
        shots = [
            ('Hook 1', 0.6), ('Hook 2: TAPI', T['tapi'] + 0.5), ('Hook 3: KONSISTEN', T['konsisten'] + 0.45),
            ('Sekali dua vs setiap bulan', T['simpan'] + 0.9), ('3 kelebihan', T['inilah'] + 1.8),
            ('01 DCA', T['dollar']), ('Cutaway DCA', T['dca_out'] - 0.4), ('Tak perlu teka', T['teka'] + 1.0),
            ('02 Disiplin', T['kedua'] + 1.5), ('Rutin setiap bulan', seg_t[8][1] - 0.8), ('03 Masa', T['penting'] + 0.4),
            ('Cutaway: masa + bar', T['grow_out'] - 0.5), ('Sekaligus vs konsisten', seg_t[11][1] - 0.5),
            ('CTA + 2 bar emas', T['kami'] + 0.6), ('Outro', base_dur + 1.6),
        ]
        tiles = []
        for label, t in shots:
            ov, has_base = overlay(t)
            fr = base_still(t) if has_base else Image.new('RGBA', (W, H), (0, 0, 0, 255))
            fr.alpha_composite(ov)
            tile = fr.convert('RGB').resize((360, 640), Image.LANCZOS)
            d = ImageDraw.Draw(tile)
            mm, ss = divmod(t, 60)
            lab = Image.new('RGB', (360, 44), (24, 24, 30))
            ImageDraw.Draw(lab).text((6, 22), f'{int(mm)}:{ss:04.1f}  {label}', font=font(F_B, 21), fill=(255, 255, 255), anchor='lm')
            t2 = Image.new('RGB', (360, 684));t2.paste(tile, (0, 0));t2.paste(lab, (0, 640))
            tiles.append(t2)
        cols = 5
        rows = math.ceil(len(tiles) / cols)
        sheet = Image.new('RGB', (cols * 360 + (cols + 1) * 12, rows * 684 + (rows + 1) * 12), (24, 24, 30))
        for i, tl in enumerate(tiles):
            sheet.paste(tl, (12 + (i % cols) * 372, 12 + (i // cols) * 696))
        sheet.save(os.path.join(OUT, 'preview_storyboard.jpg'), quality=90)
        print('preview', os.path.join(OUT, 'preview_storyboard.jpg'), 'base', round(base_dur, 2), 'total', round(total, 2))
        return

    fdir = os.path.join(OUT, 'frames')
    os.makedirs(fdir, exist_ok=True)
    nfr = int(round(total * FPS))
    for fi in range(nfr):
        ov, _ = overlay(fi / FPS)
        ov.save(os.path.join(fdir, f'f{fi:05d}.png'), compress_level=1)
    pops = [T[k] for k in ('tapi', 'bukan', 'simpan', 'inilah', 'pertama', 'teka', 'kedua', 'rutin', 'ketiga',
                           'penting', 'bukan2', 'konsisten2', 'cta', 'kami')]
    whooshes = [(T['konsisten'] - 0.2, 0.4, 0.24), (T['dca_in'] - 0.12, 0.35, 0.18), (T['dca_out'] - 0.15, 0.35, 0.18),
                (T['grow_in'] - 0.12, 0.35, 0.18), (T['grow_out'] - 0.15, 0.35, 0.18), (base_dur - 0.15, 0.5, 0.22)]
    write_sfx(total, pops, whooshes, os.path.join(OUT, 'sfx.wav'))
    final = os.path.join(OUT, '3Kelebihan_SimpanEmas_AzlanEza.mp4')
    composite(os.path.join(OUT, 'base.mov'), fdir, os.path.join(OUT, 'sfx.wav'), total, final)
    print('done', final)


if __name__ == '__main__':
    main()
