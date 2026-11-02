#!/usr/bin/env python3
"""Video 11: '10 gram emas dalam setahun' - full motion-graphic / 3D video on the user's own voiceover.
No camera footage. Light "Apple ad" look from the user's reference: white studio, bold black type, glass prompt
bars, dashed gradient pills, floating spheres, 3D gold bars/coins (fx3d) as products, push-ins and whips.
Font: Jost (closest free match to CapCut's Posterama, which is a licensed Monotype font).

python3 build_v11.py --preview         -> storyboard stills (with TikTok safe-zone guides)
python3 build_v11.py --audio-preview   -> cut voice + sfx + music
python3 build_v11.py --demo            -> short low-res motion demo
python3 build_v11.py                   -> full render
"""
import json, math, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_VS = os.path.join(HERE, '..')
WORK = os.path.join(HERE, '..', 'work', 'v11')   # voiceover, renders (not in git)
ASSETS = os.path.join(HERE, '11_assets')
sys.path.insert(0, REPO_VS)
import numpy as np
import build as B
import fx3d
from build import (W, H, FPS, OUTRO, RED, Image, ImageDraw, ImageFilter, rounded, with_shadow, place, pop,
                   check_icon, ease_out, back_out, font, load_logos, outro_frame, write_sfx, composite, syllables)

VO = os.environ.get('VO', os.path.join(WORK, 'vo.m4a'))
OUT = os.environ.get('OUT', os.path.join(WORK, 'out'))
FONTS = os.path.join(REPO_VS, 'assets', 'fonts')
J_XB, J_B, J_SB, J_M = (os.path.join(FONTS, f'Jost-{n}.ttf') for n in ('ExtraBold', 'Bold', 'SemiBold', 'Medium'))
GOLD, GOLD_L, GOLD_D = (232, 180, 70), (247, 228, 160), (150, 100, 25)
NAVY_BG, NAVY_C = (14, 16, 32), (22, 25, 46, 245)
WHITE = (255, 255, 255)
# Music: "Cautious Search" (Descript stock, approved on videos 5 and 9), crossfaded copy from video 9.
MUSIC = os.path.join(WORK, '..', 'v9', 'music.m4a')
MUSIC_SS, MUSIC_DB, MUSIC_TEMPO = 0.0, -17.0, 1.0
os.makedirs(OUT, exist_ok=True)

# Descript SRT cues of the voiceover, numbered as in transcript.srt. Retakes dropped: 9, 10 ("Bila dah nampak
# angka..." x2), 13 ("...ring-"), first half of 22 ("dapat lag-"), "Teknik yang keempat, tara-" in 28, and the
# first "Mulakan bulan ini dan," in 32. Cue starts below already skip those false starts.
CUES = {
    1: (4.146, 8.186, "Ramai yang nak mula menabung emas, tapi tak tahu nak mula dari mana."),
    2: (8.726, 12.846, "Jadi hari ni saya kongsikan teknik mudah untuk miliki 10~3"),
    3: (12.905, 14.686, "gram emas dalam masa setahun."),
    4: (15.166, 16.766, "Mulakan dengan kiraan."),
    5: (17.106, 19.566, "Harga emas hari ini RM548~10 segram."),
    6: (19.966, 24.406, "Maknanya 10~3 gram bernilai lebih kurang RM5,480~12."),
    7: (24.906, 33.846, "Bahagi dengan 12~4 bulan, kita cuma perlu ketepikan sekitar RM457~10 sebulan, "
                        "atau lebih kurang RM15~6 sehari."),
    11: (44.506, 48.806, "Bila dah nampak angka sebenar, target tu tak lagi nampak menakutkan."),
    12: (49.466, 52.446, "Teknik yang pertama adalah simpan dulu, baru berbelanja."),
    14: (57.906, 62.346, "Bila gaji masuk, terus ketepikan RM457~12 untuk emas."),
    15: (62.726, 67.906, "Jangan tunggu lebihan di hujung bulan, sebab selalunya memang tak ada lebihan yang tinggal."),
    17: (68.346, 72.106, "Jadikan ia bil wajib, sama macam bil elektrik dan air."),
    18: (74.506, 77.545, "Cara yang kedua, beli setiap bulan, tak kira harga."),
    19: (77.846, 80.066, "Harga emas naik turun, itu perkara biasa."),
    20: (80.506, 85.366, "Tapi bila kita beli konsisten setiap bulan, kita amalkan Dollar-Cost~3 Averaging~4."),
    21: (85.765, 87.586, "Bila harga tinggi, dapat gram yang sedikit."),
    22: (90.300, 92.406, "Bila harga turun, dapat lebih banyak gram."),
    23: (92.786, 98.786, "Purata kos kita jadi lebih seimbang dalam jangka panjang, tanpa perlu teka masa yang sesuai."),
    25: (100.206, 103.906, "Teknik yang ketiga pula adalah tambah bila ada rezeki lebih."),
    26: (104.426, 109.506, "Dapat bonus, komisen atau pendapatan sampingan? Tambah terus ke simpanan emas."),
    27: (109.806, 114.286, "Dengan cara ini, 10~3 gram boleh dicapai lebih cepat dari setahun."),
    28: (118.550, 121.246, "Teknik yang terakhir, tetapkan reminder."),
    29: (121.806, 126.726, "Set peringatan setiap kali gaji masuk, supaya pembelian emas tak terlepas."),
    30: (127.186, 129.826, "Konsistensi lebih penting dari jumlah."),
    31: (130.326, 133.466, "Ingat, 10~3 gram bermula dengan 1~2 gram yang pertama."),
    32: (136.100, 142.366, "Mulakan bulan ni, dan setahun lagi kita akan bersyukur dengan keputusan kita hari ini."),
    34: (144.226, 146.700, "Yang nak bermula, boleh hubungi kami."),
}
BREATH = {3: 0.45, 11: 0.45, 17: 0.45, 24: 0.45, 23: 0.45, 27: 0.45, 30: 0.3, 32: 0.4}   # longer pause at scene ends
B.SYL.update({'Dollar-Cost': 3, 'Averaging': 4, 'reminder': 3, 'segram': 2, 'komisen': 3, 'bonus': 2,
              'Konsistensi': 4, 'target': 2})


def build_segs():
    regs = json.load(open(os.path.join(ASSETS, 'edl_all.json')))['regs']
    keep = []
    for n, (s, e, _) in CUES.items():
        tail = BREATH.get(n, 0.0)
        for a, b in regs:
            a2, b2 = max(a - 0.08, s - 0.12), min(b + 0.10, e + 0.12)
            if b2 - a2 > 0.12:
                keep.append([a2, b2])
        if tail:
            last = max((k for k in keep if k[1] <= e + 0.13), key=lambda k: k[1])
            last[1] += tail
    segs = []
    for a, b in sorted(keep):
        if segs and a - segs[-1][1] < 0.18:
            segs[-1][1] = max(segs[-1][1], b)
        else:
            segs.append([a, b])
    return [(round(a * FPS) / FPS, round(b * FPS) / FPS) for a, b in segs]


SEGS = build_segs()


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


def align_words():
    regs = json.load(open(os.path.join(ASSETS, 'edl_all.json')))['regs']
    out = []
    for n, (s, e, text) in sorted(CUES.items()):
        toks, wts, ends = [], [], []
        for raw in text.split():
            punct = raw[-1] in '.,?!'
            if '~' in raw:
                d, k = raw.split('~')
                toks.append(d), wts.append(int(k.rstrip('.,?!')))
            else:
                toks.append(raw.rstrip('.,?!')), wts.append(syllables(raw.strip('.,?!')))
            ends.append(punct)
        rr = []
        for a, b in regs:
            a2, b2 = max(a, s - 0.05), min(b, e + 0.05)
            for sa, sb in SEGS:
                c0, c1 = max(a2, sa), min(b2, sb)
                if c1 - c0 > 0.03:
                    rr.append((c0, c1))
        rr = sorted(rr) or [(s, e)]
        tot = sum(b - a for a, b in rr)
        cum = np.cumsum([0] + wts) / sum(wts) * tot

        def sp2t(x):
            for a, b in rr:
                if x <= (b - a) + 1e-9:
                    return a + x
                x -= (b - a)
            return rr[-1][1]
        for i, t in enumerate(toks):
            out.append({'w': t, 'cue': n, 'end': ends[i] or i == len(toks) - 1,
                        's': sp2t(cum[i] + 1e-4), 'e': sp2t(cum[i + 1])})
    for w in out:
        w['os'], w['oe'] = src2out(w['s']), src2out(w['e'])
    return [w for w in out if w['os'] is not None]


def render_voice_and_base(base_dur):
    """Cut voice (frame-exact segments, 30 ms fades) + a plain black video of the same length."""
    n = len(SEGS)
    chain = ''.join(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.03,"
                    f"afade=t=out:st={b-a-0.03:.3f}:d=0.03[s{i}];" for i, (a, b) in enumerate(SEGS))
    chain += ''.join(f'[s{i}]' for i in range(n)) + f'concat=n={n}:v=0:a=1,highpass=f=70,' \
             'acompressor=threshold=0.1:ratio=3:attack=10:release=150:makeup=1.5[voice]'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', VO, '-f', 'lavfi', '-i',
                    f'color=c=black:s={W}x{H}:r={FPS}:d={base_dur:.3f}', '-filter_complex', chain,
                    '-map', '1:v', '-map', '[voice]', '-t', f'{base_dur:.3f}', '-c:v', 'libx264', '-preset', 'ultrafast',
                    '-c:a', 'pcm_s16le', '-ac', '2', os.path.join(OUT, 'base.mov')], check=True)


# ---------------------------------------------------------------- light "Apple ad" look (user's reference clip)
# White studio, bold black type, glass prompt bars, dashed pastel-gradient pills whose icon flips (x -> +),
# floating pastel / knit / felt spheres and clear bubbles, products (gold) with small label cards,
# fast camera push-ins and whip transitions.
INK, GREY, LGREY = (18, 18, 22), (112, 114, 124), (165, 168, 178)
BLUE_BTN = (0, 113, 227)
SPH = {'blue': (88, 132, 238), 'green': (70, 186, 104), 'grey': (196, 197, 202), 'pink': (240, 150, 190),
       'gold': (236, 190, 90)}


def jf(path, size):
    return font(path, size)


def fitw(spr, maxw=840):
    return spr if spr.width <= maxw else spr.resize((maxw, int(spr.height * maxw / spr.width)), Image.LANCZOS)


def headline(txt, size=120, col=INK, path=J_XB):
    f = jf(path, size)
    bb = f.getbbox(txt)
    pad = int(size * 0.18)
    im = Image.new('RGBA', (bb[2] - bb[0] + pad * 2, bb[3] - bb[1] + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - bb[0], pad - bb[1]), txt, font=f, fill=col + (255,))
    return fitw(im, 860)


def glyph_icon(kind, s=56, bg=INK, fg=WHITE):
    """Round icon: x, +, check, bell, arrow, mic."""
    S = s * 3
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, S - 1, S - 1], fill=bg + (255,))
    w = max(6, S // 11)
    c = fg + (255,)
    if kind == 'x':
        k = S * 0.32
        d.line([(k, k), (S - k, S - k)], fill=c, width=w)
        d.line([(S - k, k), (k, S - k)], fill=c, width=w)
    elif kind == '+':
        k = S * 0.28
        d.line([(k, S / 2), (S - k, S / 2)], fill=c, width=w)
        d.line([(S / 2, k), (S / 2, S - k)], fill=c, width=w)
    elif kind == 'check':
        d.line([(S * .28, S * .52), (S * .44, S * .68), (S * .74, S * .34)], fill=c, width=w, joint='curve')
    elif kind == 'bell':
        d.pieslice([S * .28, S * .2, S * .72, S * .7], 180, 360, fill=c)
        d.rectangle([S * .28, S * .45, S * .72, S * .66], fill=c)
        d.polygon([(S * .22, S * .72), (S * .78, S * .72), (S * .72, S * .62), (S * .28, S * .62)], fill=c)
        d.ellipse([S * .43, S * .72, S * .57, S * .84], fill=c)
    elif kind == 'arrow':
        d.polygon([(S * .3, S * .48), (S * .7, S * .48), (S * .5, S * .76)], fill=c)
        d.rectangle([S * .44, S * .24, S * .56, S * .5], fill=c)
    elif kind == 'mic':
        d.rounded_rectangle([S * .4, S * .2, S * .6, S * .58], S * .1, fill=c)
        d.arc([S * .3, S * .3, S * .7, S * .66], 0, 180, fill=c, width=w // 2)
        d.line([(S / 2, S * .66), (S / 2, S * .78)], fill=c, width=w // 2)
    return im.resize((s, s), Image.LANCZOS)


_grad = None


def dash_pill(text, icon='+', size=48, flip=0.0):
    """White pill with a dashed pastel-gradient border; the icon rotates from x to + as flip goes 0 -> 1."""
    global _grad
    f = jf(J_M, size)
    bb = f.getbbox(text)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    h = th + 56
    iw = h - 26
    w = tw + iw + 90
    S = 2
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([3 * S, 3 * S, (w - 3) * S, (h - 3) * S], (h // 2) * S, fill=(255, 255, 255, 250))
    # dashed border, coloured by a horizontal pink -> orange -> blue gradient
    mask = Image.new('L', im.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([3 * S, 3 * S, (w - 3) * S, (h - 3) * S], (h // 2) * S, outline=255, width=4 * S)
    xs = np.arange(im.width)[None, :]
    dash = ((xs // (14 * S)) % 2 == 0) | ((np.arange(im.height)[:, None] // (14 * S)) % 2 == 0) * 0
    m = np.asarray(mask) * (((xs + np.arange(im.height)[:, None]) // (13 * S)) % 2 == 0)
    gx = np.linspace(0, 1, im.width)
    cols = np.array([(255, 120, 180), (255, 170, 80), (110, 150, 255)], float)
    g = np.where(gx < 0.5, 0, 1)
    k = np.where(gx < 0.5, gx / 0.5, (gx - 0.5) / 0.5)[:, None]
    rgb = cols[g] * (1 - k) + cols[np.minimum(g + 1, 2)] * k
    border = np.zeros((im.height, im.width, 4), np.uint8)
    border[..., :3] = rgb[None, :, :].astype(np.uint8)
    border[..., 3] = m.astype(np.uint8)
    im.alpha_composite(Image.fromarray(border))
    im = im.resize((w, h), Image.LANCZOS)
    kind = icon
    if icon == '+':
        kind = 'x' if flip < 0.5 else '+'
    ic = glyph_icon(kind, iw, bg=(240, 240, 244), fg=INK)
    if icon == '+':
        ic = ic.rotate(-90 * min(1, flip * 2) if flip < 0.5 else 90 * (1 - min(1, (flip - 0.5) * 2)),
                       resample=Image.BICUBIC)
    im.alpha_composite(ic, (14, (h - iw) // 2))
    ImageDraw.Draw(im).text((iw + 40 - bb[0], (h - th) // 2 - bb[1]), text, font=f, fill=INK + (255,))
    return fitw(with_shadow(im, 14, 6, 0.14), 880)


def glass_pill(text, icon='mic', size=44, typed=1.0, sub=None):
    """Frosted prompt bar that types its text."""
    f = jf(J_M, size)
    full = f.getbbox(text)
    tw = full[2] - full[0]
    h = size + 64 + (52 if sub else 0)
    w = min(860, tw + 170)
    im = rounded((w, h), 40 if sub else h // 2, (255, 255, 255, 225))
    d = ImageDraw.Draw(im)
    n = int(round(len(text) * min(1, typed)))
    y0 = (size + 64) / 2
    d.text((40, y0), text[:n], font=f, fill=INK + (255,), anchor='lm')
    if typed < 1 and int(typed * 20) % 2 == 0:
        cx = 40 + f.getlength(text[:n]) + 6
        d.line([(cx, y0 - size * 0.45), (cx, y0 + size * 0.45)], fill=BLUE_BTN + (255,), width=4)
    ic = glyph_icon(icon, size + 18, bg=(238, 238, 243), fg=INK)
    im.alpha_composite(ic, (w - size - 50, int(y0 - (size + 18) / 2)))
    if sub:
        d.rounded_rectangle([34, y0 + 30, 34 + jf(J_M, 30).getlength(sub) + 70, y0 + 82], 26,
                            fill=(255, 230, 240, 255))
        d.text((70, y0 + 56), sub, font=jf(J_M, 30), fill=(220, 90, 140, 255), anchor='lm')
    return fitw(with_shadow(im, 22, 10, 0.16), 880)


def label_card(title, sub, btn=None):
    """Small product label (title, grey sub, blue pill) like the reference's 'MacBook Pro 14"' tags."""
    ft, fs = jf(J_B, 40), jf(J_M, 28)
    w = int(max(ft.getlength(title), fs.getlength(sub)) + 70)
    h = 150 if btn else 110
    im = rounded((w, h), 26, (255, 255, 255, 240))
    d = ImageDraw.Draw(im)
    d.text((w / 2, 42), title, font=ft, fill=INK + (255,), anchor='mm')
    d.text((w / 2, 82), sub, font=fs, fill=GREY + (255,), anchor='mm')
    if btn:
        bw = jf(J_B, 24).getlength(btn) + 40
        d.rounded_rectangle([w / 2 - bw / 2, 104, w / 2 + bw / 2, 138], 17, fill=BLUE_BTN + (255,))
        d.text((w / 2, 121), btn, font=jf(J_B, 24), fill=WHITE + (255,), anchor='mm')
    return with_shadow(im, 18, 8, 0.16)


def make_background():
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(-1, 1, W)[None, :]
    r = np.sqrt((x * 0.9) ** 2 + ((y - 0.42) * 1.5) ** 2)
    v = 250 - 34 * np.clip(r, 0, 1.2) ** 1.6
    g = np.stack([v - 3, v - 2, v + 1], -1)
    return Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert('RGBA')


_sph = {}


def sphere(kind, d, blur=0):
    """Shaded sphere sprite: pastel matte, knit/felt textured, or a clear bubble."""
    key = (kind, int(d), int(blur))
    if key in _sph:
        return _sph[key]
    S = int(d * 2)
    yy, xx = np.mgrid[0:S, 0:S]
    nx, ny = (xx - S / 2) / (S / 2), (yy - S / 2) / (S / 2)
    rr = nx ** 2 + ny ** 2
    inside = rr <= 1
    nz = np.sqrt(np.clip(1 - rr, 0, 1))
    L = np.array([-0.45, -0.6, 0.66])
    L = L / np.linalg.norm(L)
    lam = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    hv = L + np.array([0, 0, 1.0])
    hv /= np.linalg.norm(hv)
    spec = np.clip(nx * hv[0] + ny * hv[1] + nz * hv[2], 0, 1) ** 40
    out = np.zeros((S, S, 4), float)
    if kind == 'bubble':
        rim = (1 - nz) ** 2.5
        out[..., :3] = 255
        a = 0.06 + 0.55 * rim + 0.9 * spec
        tint = np.stack([200 + 40 * nx, 220 + 20 * ny, 255 + 0 * nx], -1)
        out[..., :3] = tint * (1 - spec[..., None]) + 255 * spec[..., None]
        out[..., 3] = np.clip(a, 0, 1) * 255 * inside
    else:
        base = np.array(SPH[kind if kind in SPH else 'grey'], float)
        shade = 0.42 + 0.62 * lam
        if kind in ('grey', 'green'):          # knit / felt texture
            rng_ = np.random.default_rng(3 if kind == 'grey' else 5)
            n = rng_.normal(0, 1, (S // 3 + 1, S // 3 + 1))
            n = np.kron(n, np.ones((3, 3)))[:S, :S]
            if kind == 'grey':
                n = n + 0.8 * np.sin((xx + yy * 0.3) * 0.9)
            shade = shade * (1 + 0.07 * n)
            sp = 0.15
        else:
            sp = 0.55
        rgb = base[None, None, :] * shade[..., None] + 255 * sp * spec[..., None]
        out[..., :3] = np.clip(rgb, 0, 255)
        out[..., 3] = 255 * inside
    # anti-aliased edge
    edge = np.clip((1 - np.sqrt(rr)) * S / 2, 0, 1)
    out[..., 3] *= edge
    im = Image.fromarray(out.astype(np.uint8)).resize((int(d), int(d)), Image.LANCZOS)
    if blur:
        pad = blur * 3
        big = Image.new('RGBA', (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
        big.alpha_composite(im, (pad, pad))
        im = big.filter(ImageFilter.GaussianBlur(blur))
    _sph[key] = im
    return im


# Floating props per scene: (kind, x, y, diameter, depth). depth > 1 = nearer (moves more, blurred when big).
FLOAT = {
    'hook': [('blue', 1010, 230, 200, 1.2), ('bubble', 70, 1000, 110, 1.0), ('grey', 60, 1330, 260, 1.3),
             ('bubble', 1010, 1110, 90, 0.9), ('green', 1010, 1380, 180, 1.4)],
    'title': [('blue', 60, 200, 220, 1.3), ('green', 1020, 700, 180, 1.1), ('grey', 1000, 1330, 280, 1.4),
              ('bubble', 80, 820, 100, 1.0), ('bubble', 1010, 260, 80, 0.9)],
    'kira': [('blue', 1020, 200, 220, 1.2), ('grey', 50, 1330, 260, 1.4), ('bubble', 1010, 1120, 100, 1.0),
             ('bubble', 60, 760, 80, 0.9)],
    't1': [('green', 50, 230, 200, 1.2), ('blue', 1030, 1330, 260, 1.4), ('bubble', 1020, 700, 90, 1.0),
           ('grey', 50, 1380, 160, 1.1)],
    't2': [('blue', 1030, 220, 200, 1.2), ('grey', 50, 1360, 230, 1.3), ('bubble', 50, 760, 80, 1.0),
           ('green', 1030, 1400, 150, 1.4)],
    't3': [('grey', 1030, 230, 210, 1.2), ('green', 50, 1340, 250, 1.4), ('bubble', 1010, 1120, 90, 1.0),
           ('blue', 50, 760, 130, 1.1)],
    't4': [('pink', 1030, 230, 190, 1.2), ('blue', 50, 1340, 250, 1.4), ('bubble', 50, 760, 90, 1.0),
           ('grey', 1030, 1400, 150, 1.1)],
    'end': [('blue', 50, 230, 220, 1.3), ('green', 1030, 760, 170, 1.1), ('grey', 1010, 1350, 280, 1.4),
            ('bubble', 70, 1150, 110, 1.0), ('bubble', 1010, 240, 80, 0.9)],
}


def draw_floaters(fr, scene, lt):
    """Props drift slowly; on scene entry they rush in from the camera (scale + offset), giving a fly-in."""
    k = ease_out(min(1, lt / 0.55))
    for i, (kind, x, y, d, z) in enumerate(FLOAT[scene]):
        dx = 18 * z * math.sin(lt * 0.7 + i)
        dy = 22 * z * math.sin(lt * 0.55 + i * 1.7) - lt * 6 * z
        sc = (1 + (1 - k) * 0.9 * z)
        ox, oy = (x - W / 2) * (sc - 1), (y - H / 2) * (sc - 1)
        blur = 6 if z >= 1.35 else 0
        spr = sphere(kind, d * (1 + 0.04 * math.sin(lt + i)), blur)
        place(fr, spr, x + dx + ox, y + dy + oy, sc, min(1, 0.25 + k))


_cache = {}


def bar3d(angle, size=520, rx=22.0, label='999.9'):
    key = ('bar', int(round(angle)) % 360, size, int(rx), label)
    if key not in _cache:
        tk = ('tex', label)
        if tk not in _cache:
            _cache[tk] = fx3d.bar_texture(label=label, font_path=J_XB)
        spr = fx3d.render_bar(int(round(angle)) % 360, rx=rx, size=size, texture=_cache[tk])
        _cache[key] = with_shadow(spr, 26, 22, 0.22)
    return _cache[key]


def coin3d(angle, size=300, label='1g', rx=-8.0):
    key = ('coin', int(round(angle)) % 360, size, label, int(rx))
    if key not in _cache:
        _cache[key] = with_shadow(fx3d.render_coin(int(round(angle)) % 360, rx=rx, size=size, label=label,
                                                   font_path=J_XB), 18, 14, 0.2)
    return _cache[key]


def tile(ch, s=110, rot=0.0):
    """White rounded letter tile with a little thickness (the flying 'hey Siri' letters)."""
    key = ('tile', ch, s)
    if key not in _cache:
        im = Image.new('RGBA', (s + 14, s + 22), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([7, 16, s + 7, s + 16], s // 5, fill=(214, 216, 224, 255))
        d.rounded_rectangle([7, 4, s + 7, s + 4], s // 5, fill=(255, 255, 255, 255))
        if ch == '*':
            d.ellipse([7 + s * .25, 4 + s * .25, 7 + s * .75, 4 + s * .75], fill=GOLD + (255,))
            d.text((7 + s / 2, 4 + s / 2), 'g', font=jf(J_XB, int(s * 0.32)), fill=(110, 70, 10, 255), anchor='mm')
        else:
            d.text((7 + s / 2, 4 + s / 2), ch, font=jf(J_XB, int(s * 0.62)), fill=INK + (255,), anchor='mm')
        _cache[key] = with_shadow(im, 12, 8, 0.18)
    return _cache[key]


# ---------------------------------------------------------------- real photos (user): gold bar + cash, backgrounds removed
GOLD_PNG = os.path.join(ASSETS, 'goldbar_cut.png')
CASH_PNG = os.path.join(ASSETS, 'money_cut.png')
_photo = {}


def photo(path, h=None, w=None):
    key = (path, h, w)
    if key not in _photo:
        im = Image.open(path).convert('RGBA')
        sc = (h / im.height) if h else (w / im.width)
        _photo[key] = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    return _photo[key]


def sheen(spr, p):
    """Diagonal light sweep across a product, p in 0..1."""
    if not 0 < p < 1:
        return spr
    w, h = spr.size
    band = Image.new('L', (w, h), 0)
    x = int(-w * 0.6 + p * w * 2.2)
    ImageDraw.Draw(band).polygon([(x, 0), (x + w * 0.25, 0), (x + w * 0.25 - h * 0.35, h), (x - h * 0.35, h)], fill=120)
    band = band.filter(ImageFilter.GaussianBlur(w * 0.06))
    band = Image.fromarray(np.minimum(np.asarray(band), np.asarray(spr.getchannel('A'))))
    out = spr.copy()
    glint = Image.new('RGBA', (w, h), (255, 250, 225, 255))
    glint.putalpha(band)
    out.alpha_composite(glint)
    return out


def ground_shadow(w):
    w = float(max(16, int(w) // 8 * 8))
    key = ('gsh', int(w))
    if key not in _photo:
        im = Image.new('RGBA', (int(w * 1.6), int(w * 0.5)), (0, 0, 0, 0))
        ImageDraw.Draw(im).ellipse([w * 0.3, w * 0.12, w * 1.3, w * 0.36], fill=(20, 20, 30, 90))
        _photo[key] = im.filter(ImageFilter.GaussianBlur(w * 0.07))
    return _photo[key]


def product(fr, path, cx, cy, t, h=None, w=None, scale=1.0, alpha=1.0, phase=0.0, sway=1.0, shine_every=3.2):
    """Real photo cut-out floating in 3D: smooth sub-degree sway, soft ground shadow, periodic light sweep."""
    if scale <= 0.01 or alpha <= 0.01:
        return
    base = photo(path, h=h, w=w)
    sp = sheen(base, ((t + phase) % shine_every) / 1.1) if shine_every else base
    spr = fx3d.warp3d(sp, rx=5 * sway * math.sin(t * 0.8 + phase), ry=12 * sway * math.sin(t * 0.6 + phase), shade=False)
    bob = 10 * sway * math.sin(t * 1.1 + phase)
    place(fr, ground_shadow(base.width * scale), cx, cy + base.height * scale * 0.52, 1, alpha * 0.9)
    place(fr, spr, cx, cy + bob, scale, alpha)


def count(t, t0, dur, v0, v1):
    k = ease_out(min(1, max(0, (t - t0) / dur)))
    return v0 + (v1 - v0) * k


def card(w, h):
    return rounded((w, h), 40, (255, 255, 255, 242))


def bills_card(t, t0):
    cw, ch = 820, 450
    im = card(cw, ch)
    d = ImageDraw.Draw(im)
    d.text((44, 62), 'Bil wajib bulanan', font=jf(J_XB, 44), fill=INK + (255,), anchor='lm')
    rows = [('Bil elektrik', False), ('Bil air', False), ('Emas  RM457', True)]
    for i, (lab, gold) in enumerate(rows):
        k = ease_out(min(1, max(0, (t - t0 - 0.25 - i * 0.45) / 0.3)))
        if k <= 0:
            continue
        y = 165 + i * 100
        if gold:
            d.rounded_rectangle([24, y - 42, cw - 24, y + 42], 26, fill=(255, 244, 214, int(255 * k)))
        d.text((60, y), lab, font=jf(J_B, 44), fill=((130, 86, 10) if gold else INK) + (int(255 * k),), anchor='lm')
        ic = glyph_icon('check', 54, bg=(52, 199, 89), fg=WHITE)
        ic.putalpha(ic.getchannel('A').point(lambda v: int(v * k)))
        im.alpha_composite(ic, (cw - 104, int(y - 27)))
    return with_shadow(im, 26, 12, 0.16)


def dca_chart(p):
    cw, ch = 900, 800
    im = card(cw, ch)
    d = ImageDraw.Draw(im)
    d.text((cw / 2, 70), 'Dollar-Cost Averaging', font=jf(J_XB, 52), fill=INK + (255,), anchor='mm')
    d.text((cw / 2, 122), 'beli setiap bulan, harga naik atau turun', font=jf(J_M, 31), fill=GREY + (255,), anchor='mm')
    x0, x1, yc = 90, cw - 90, 330
    xs = np.linspace(x0, x1, 300)
    ys = yc - 110 * np.sin((xs - x0) / (x1 - x0) * math.pi * 2.6) * np.linspace(1, 0.8, 300) - (xs - x0) * 0.06
    pe = ease_out(min(1, p / 0.55))
    nshow = max(2, int(300 * pe))
    d.line(list(zip(xs[:nshow], ys[:nshow])), fill=(60, 64, 80, 255), width=6, joint='curve')
    buys = np.linspace(10, 289, 8).astype(int)
    base = 680
    for bi in buys:
        if bi >= nshow:
            continue
        grams = 9000 / (yc + 160 - ys[bi])
        kk = ease_out(min(1, (nshow - bi) / 30))
        hh = (grams - 25) * 5.2 * kk
        d.line([(xs[bi], ys[bi] + 16), (xs[bi], base - hh - 6)], fill=(222, 223, 230, 255), width=2)
        d.rounded_rectangle([xs[bi] - 26, base - hh, xs[bi] + 26, base], 12, fill=GOLD + (255,))
        d.ellipse([xs[bi] - 14, ys[bi] - 14, xs[bi] + 14, ys[bi] + 14], fill=WHITE + (255,), outline=INK + (255,), width=5)
    d.line([(x0 - 20, base), (x1 + 20, base)], fill=(210, 212, 220, 255), width=3)
    d.text((x0 - 10, base + 40), 'gram dibeli', font=jf(J_M, 30), fill=GREY + (255,), anchor='lm')
    hi, lo = int(np.argmin(ys)), int(np.argmax(ys))
    if nshow > hi:
        d.text((xs[hi], ys[hi] - 42), 'harga tinggi', font=jf(J_B, 30), fill=INK + (255,), anchor='mm')
    if nshow > lo:
        d.text((xs[lo] + 105, ys[lo] + 4), 'harga turun', font=jf(J_B, 30), fill=INK + (255,), anchor='mm')
    return with_shadow(im, 30, 14, 0.16)


def progress_card(t, t0):
    cw, ch = 860, 360
    im = card(cw, ch)
    d = ImageDraw.Draw(im)
    d.text((44, 60), 'Target 10 gram', font=jf(J_XB, 44), fill=INK + (255,), anchor='lm')
    for i, (lab, speed, col) in enumerate((('simpanan bulanan', 0.55, (170, 176, 196)), ('+ bonus & komisen', 1.0, GOLD))):
        y = 145 + i * 115
        d.text((44, y), lab, font=jf(J_M, 34), fill=GREY + (255,), anchor='lm')
        d.rounded_rectangle([44, y + 30, cw - 44, y + 62], 16, fill=(236, 237, 242, 255))
        k = ease_out(min(1, max(0, (t - t0) / 2.4))) * speed
        d.rounded_rectangle([44, y + 30, 44 + (cw - 88) * k, y + 62], 16, fill=col + (255,))
        if k > 0.98:
            d.text((cw - 50, y), '10 g', font=jf(J_XB, 36), fill=(150, 100, 20, 255), anchor='rm')
    return with_shadow(im, 26, 12, 0.16)


def phone_notif():
    cw, ch = 800, 190
    im = rounded((cw, ch), 44, (255, 255, 255, 236))
    d = ImageDraw.Draw(im)
    im.alpha_composite(glyph_icon('bell', 110, bg=(255, 204, 0), fg=WHITE), (36, 40))
    d.text((172, 70), 'Gaji dah masuk!', font=jf(J_XB, 46), fill=INK + (255,), anchor='lm')
    d.text((172, 128), 'Masa untuk beli emas bulan ni', font=jf(J_M, 34), fill=GREY + (255,), anchor='lm')
    d.text((cw - 36, 46), 'sekarang', font=jf(J_M, 26), fill=LGREY + (255,), anchor='rm')
    return with_shadow(im, 26, 12, 0.18)


def calendar_card(t, t0):
    cw, ch = 860, 320
    im = card(cw, ch)
    d = ImageDraw.Draw(im)
    months = ['Jan', 'Feb', 'Mac', 'Apr', 'Mei', 'Jun', 'Jul', 'Ogo', 'Sep', 'Okt', 'Nov', 'Dis']
    for i, m in enumerate(months):
        cx, cy = 90 + (i % 6) * 136, 88 + (i // 6) * 146
        k = ease_out(min(1, max(0, (t - t0 - i * 0.12) / 0.25)))
        d.rounded_rectangle([cx - 56, cy - 50, cx + 56, cy + 50], 22, fill=(243, 243, 247, 255))
        d.text((cx, cy - 18), m, font=jf(J_B, 30), fill=GREY + (255,), anchor='mm')
        if k > 0:
            r = 21 * back_out(k)
            d.ellipse([cx - r, cy + 22 - r, cx + r, cy + 22 + r], fill=GOLD + (255,))
            d.text((cx, cy + 22), 'g', font=jf(J_XB, int(28 * k) + 1), fill=(90, 60, 10, 255), anchor='mm')
    return with_shadow(im, 26, 12, 0.16)


# ---------------------------------------------------------------- subtitles (small phrase captions)
def caption_chunks(words):
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if w['end'] or len(cur) >= 4:
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    out = []
    for i, c in enumerate(chunks):
        nxt = chunks[i + 1][0]['os'] if i + 1 < len(chunks) else c[-1]['oe'] + 0.4
        end = nxt if nxt - c[-1]['oe'] < 0.5 else c[-1]['oe'] + 0.25
        out.append((c[0]['os'], end, c))
    return out


SUB_SIZE = 46
_subc = {}


def subtitle(chunk, active):
    key = (id(chunk), active)
    if key not in _subc:
        f = jf(J_SB, SUB_SIZE)
        txts = [w['w'] for w in chunk]
        sp = f.getlength(' ')
        ws = [f.getlength(x) for x in txts]
        tw = sum(ws) + sp * (len(txts) - 1)
        h = SUB_SIZE + 34
        im = rounded((int(tw + 56), h), h // 2, (18, 18, 22, 190))
        d = ImageDraw.Draw(im)
        x = 28
        for i, (tx, wd) in enumerate(zip(txts, ws)):
            d.text((x, h / 2), tx, font=f, fill=(GOLD_L if i == active else WHITE) + (255,), anchor='lm')
            x += wd + sp
        _subc[key] = fitw(im, 860)
    return _subc[key]


def light_outro(to, logo_c):
    fr = make_background()
    sc = back_out(min(1, to / 0.45)) * 0.62
    place(fr, logo_c, W / 2, H * 0.40, sc, min(1, to / 0.2))
    k = ease_out((to - 0.5) / 0.4)
    if k > 0:
        p = dash_pill('Azlan & Eza', icon='+', size=52, flip=min(1, max(0, (to - 0.9) / 0.4)))
        place(fr, p, W / 2, H * 0.58 + (1 - k) * 80, 1, k)
    if to > OUTRO - 0.5:
        fr.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(255 * (to - (OUTRO - 0.5)) / 0.5))))
    return fr


def camera(img, s, dx=0.0, whip=0.0):
    """Push-in scale about the frame centre, plus an optional horizontal whip (offset + motion blur)."""
    if abs(s - 1) > 1e-3:
        nw, nh = int(W * s), int(H * s)
        img = img.resize((nw, nh), Image.BICUBIC).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    if whip > 0.01:
        a = np.asarray(img).astype(np.float32)
        n = 7
        acc = np.zeros_like(a)
        step = int(18 + 70 * whip)
        for i in range(n):
            acc += np.roll(a, int(dx) + (i - n // 2) * step // n * 3, axis=1)
        img = Image.fromarray((acc / n).astype(np.uint8))
    return img


def main():
    words = align_words()
    offs, base_dur = offsets()
    total = base_dur + OUTRO
    json.dump(words, open(os.path.join(OUT, 'words.json'), 'w'), indent=1)

    def ct(n, end=False):
        return src2out(CUES[n][1] if end else CUES[n][0])

    def wt(word, nth=1, cue=None):
        k = 0
        for w in words:
            if w['w'].lower().strip(',') == word.lower() and (cue is None or w['cue'] == cue):
                k += 1
                if k == nth:
                    return w['os']
        raise KeyError(word)

    T = {'teknik': wt('teknik', cue=2), 'gram10': wt('gram', cue=3), 'setahun': wt('setahun', cue=3),
         'kiraan': ct(4), 'rm548': wt('RM548'), 'rm5480': wt('RM5,480'), 'rm457': wt('RM457'), 'rm15': wt('RM15'),
         'angka': ct(11), 'takut': wt('menakutkan'),
         't1': ct(12), 'gaji': ct(14), 'lebihan': ct(15), 'bil': ct(17),
         't2': ct(18), 'naik': ct(19), 'dca': wt('Dollar-Cost'), 'tinggi': ct(21), 'turun': ct(22), 'purata': ct(23),
         't3': ct(25), 'bonus': wt('bonus'), 'komisen': wt('komisen'), 'sampingan': wt('sampingan'),
         'tambah2': wt('Tambah', cue=26), 'cepat': ct(27),
         't4': ct(28), 'set': ct(29), 'konsisten': ct(30),
         'ingat': ct(31), 'satu': wt('1'), 'mulakan': ct(32), 'syukur': wt('bersyukur'), 'cta': ct(34)}
    SCENES = [('hook', 0.0, T['teknik'] - 0.1), ('title', T['teknik'] - 0.1, T['kiraan'] - 0.1),
              ('kira', T['kiraan'] - 0.1, T['t1'] - 0.1), ('t1', T['t1'] - 0.1, T['t2'] - 0.1),
              ('t2', T['t2'] - 0.1, T['t3'] - 0.1), ('t3', T['t3'] - 0.1, T['t4'] - 0.1),
              ('t4', T['t4'] - 0.1, T['ingat'] - 0.1), ('end', T['ingat'] - 0.1, base_dur)]

    logo_c, logo_w = load_logos()
    wm = logo_c.resize((120, int(120 * logo_c.height / logo_c.width)), Image.LANCZOS)
    bg = make_background()
    chunks = caption_chunks(words)
    CX = B.TT_CENTER_X
    H_mula = headline('Nak mula', 150)
    H_dari = headline('dari mana?', 150)
    H_10 = headline('10 gram emas', 132)
    H_rm548 = headline('RM548', 150)
    H_rm457 = headline('RM457', 210)
    H_target = headline('Target,', 130)
    tech = {1: (headline('Simpan dulu,', 124), 'baru berbelanja'),
            2: (headline('Beli setiap bulan,', 104), 'tak kira harga'),
            3: (headline('Tambah', 140), 'bila ada rezeki lebih'),
            4: (headline('Tetapkan', 140), 'reminder')}
    H_konsisten = headline('Konsistensi', 128)
    H_ingat = headline('10 gram', 150)
    H_mulakan = headline('Mulakan', 150)
    H_bulan = headline('bulan ni.', 150)
    H_cta = headline('Yang nak bermula?', 96)
    sub_lbl = {n: headline(f'Teknik {n}', 46, col=GREY, path=J_B) for n in range(1, 5)}

    pops = [T[k] for k in ('gram10', 'rm548', 'rm5480', 'rm457', 'rm15', 'takut', 'gaji', 'lebihan', 'bil',
                           'naik', 'tinggi', 'turun', 'purata', 'bonus', 'komisen', 'sampingan', 'cepat', 'set',
                           'satu', 'cta')]
    whooshes = [(0.0, 0.4, 0.2)] + [(a - 0.12, 0.35, 0.24) for _, a, _ in SCENES[1:]] + [(base_dur - 0.15, 0.5, 0.22)]

    if '--audio-preview' in sys.argv:
        render_voice_and_base(base_dur)
        write_sfx(total, pops, whooshes, os.path.join(OUT, 'sfx.wav'))
        fc = B.audio_mix_graph('[0:a]', '[1:a]', total, '[2:a]', MUSIC_SS, MUSIC_DB, outro_at=base_dur,
                               music_tempo=MUSIC_TEMPO)
        outp = os.path.join(WORK, 'PREVIEW_audio_music.m4a')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(OUT, 'base.mov'), '-i', os.path.join(OUT, 'sfx.wav'),
                        '-i', MUSIC, '-filter_complex', fc, '-map', '[a]', '-t', f'{total}', '-c:a', 'aac', '-b:a', '128k',
                        outp], check=True)
        print('audio preview', outp, 'total', round(total, 2))
        return

    def show(fr, spr, cx, cy, t, t0, t1, rot=0):
        s, a = pop(t, t0, t1)
        place(fr, spr, cx, cy, s, a, rot=rot)

    def rise(fr, spr, cx, cy, t, t0, t1, dist=60):
        """Apple-style text entrance: slide up + fade, quick fade out."""
        if t < t0 or t > t1:
            return
        k = ease_out(min(1, (t - t0) / 0.35))
        a = min(k, max(0, (t1 - t) / 0.15))
        place(fr, spr, cx, cy + (1 - k) * dist, 1, a)

    def scene_of(t):
        for name, a, b in SCENES:
            if a <= t < b:
                return name, a, b
        return SCENES[-1]

    def content(fr, scene, t, a, b):
        lt = t - a
        if scene == 'hook':
            # letter tiles burst out below the headline ("hey Siri" letters), drawn first so the text sits on top
            letters = 'EMAS*1G*RM'
            if lt > 0.9:
                for i, ch in enumerate(letters):
                    ang = math.pi * (0.08 + 0.84 * i / (len(letters) - 1))     # lower half-fan
                    k = ease_out(min(1, (lt - 0.9 - i * 0.04) / 0.7))
                    if k <= 0:
                        continue
                    r = 80 + 300 * k + 20 * math.sin(lt + i)
                    x = CX + math.cos(ang) * r * 1.25
                    y = 860 + math.sin(ang) * r * 0.9 + (i % 2) * 50 - lt * 6
                    spr = fx3d.warp3d(tile(ch, 96 + (i % 3) * 16), rx=25 * math.sin(lt * 2 + i), ry=35 * math.cos(lt * 1.6 + i))
                    place(fr, spr, x, y, 0.8 + 0.2 * k, min(1, k * 1.5))
            g = glass_pill('nak mula menabung emas...', typed=min(1, lt / 1.4))
            rise(fr, g, CX, 300, t, 0.0, b)
            rise(fr, H_mula, CX, 520, t, 0.5, b)
            rise(fr, H_dari, CX, 680, t, 0.75, b)
        elif scene == 'title':
            for i in range(10):
                t0 = a + 0.25 + 0.1 * i
                if t >= t0:
                    k = ease_out(min(1, (t - t0) / 0.35))
                    place(fr, coin3d(8 + i * 3, size=250, label='1g', rx=-62), CX - 230, 1230 - i * 36 - (1 - k) * 260, 1, k)
            if t >= T['gram10'] - 0.3:
                k = ease_out(min(1, (t - T['gram10'] + 0.3) / 0.5))
                product(fr, GOLD_PNG, CX + 160, 960, t, h=520, scale=0.75 + 0.25 * k, alpha=k)
                rise(fr, label_card('Public Gold', 'Emas 999.9', 'Simpan'), CX + 160, 1270, t, T['gram10'] + 0.4, b)
            rise(fr, H_10, CX, 380, t, a + 0.05, b)
            show(fr, dash_pill('dalam masa setahun', '+', 50, flip=min(1, max(0, (t - T['setahun']) / 0.35))),
                 CX, 560, t, T['setahun'] - 0.6, b)
        elif scene == 'kira':
            rise(fr, glass_pill('mulakan dengan kiraan', icon='mic', typed=min(1, lt / 0.9)), CX, 270, t, a, b)
            rise(fr, H_rm548, CX, 520, t, T['rm548'] - 0.1, T['rm457'] - 0.2)
            rise(fr, headline('harga emas / gram', 46, col=GREY, path=J_B), CX, 640, t, T['rm548'], T['rm457'] - 0.2)
            if T['rm5480'] - 0.1 <= t < T['rm457'] - 0.2:
                v = count(t, T['rm5480'] - 0.1, 0.7, 548, 5480)
                rise(fr, headline(f'x 10 gram = RM{v:,.0f}', 70), CX, 820, t, T['rm5480'] - 0.1, T['rm457'] - 0.2)
            if t >= T['rm457'] - 0.2:
                rise(fr, headline('RM5,480  ÷  12 bulan', 62, col=GREY, path=J_B), CX, 470, t, T['rm457'] - 0.2, b)
                v = count(t, T['rm457'] - 0.2, 0.7, 0, 457)
                rise(fr, headline(f'RM{v:,.0f}', 210), CX, 660, t, T['rm457'] - 0.2, b)
                show(fr, dash_pill('sebulan', '+', 52, flip=min(1, max(0, (t - T['rm457'] - 0.6) / 0.35))),
                     CX, 840, t, T['rm457'] + 0.2, b)
                show(fr, glass_pill('lebih kurang RM15 sehari', icon='check'), CX, 990, t, T['rm15'] - 0.1, b)
            if t >= T['takut'] - 0.6:
                fl = min(1, max(0, (t - T['takut'] - 0.2) / 0.35))
                show(fr, dash_pill('menakutkan' if fl < 0.5 else 'tak lagi menakutkan', '+', 46, flip=fl),
                     CX, 1130, t, T['takut'] - 0.6, b)
            if t >= T['rm457']:
                k = ease_out(min(1, (t - T['rm457']) / 0.5))
                product(fr, CASH_PNG, CX + 300, 1270, t, w=220, scale=k, alpha=k, shine_every=0)
        elif scene in ('t1', 't2', 't3', 't4'):
            n = int(scene[1])
            hl, pl = tech[n]
            first = {'t1': T['gaji'], 't2': T['naik'], 't3': T['bonus'], 't4': T['set']}[scene] - 0.15
            # title phase: big centred headline, then it moves up and shrinks for the details
            k_up = ease_out(min(1, max(0, (t - first) / 0.45)))
            ty = 640 - 330 * k_up
            sc = 1 - 0.30 * k_up
            rise(fr, sub_lbl[n], CX, ty - 150 * sc - 20 * (1 - k_up), t, a + 0.05, b)
            if t >= a + 0.1:
                kk = ease_out(min(1, (t - a - 0.1) / 0.35))
                place(fr, hl, CX, ty + (1 - kk) * 60, sc, min(kk, max(0, (b - t) / 0.15)))
            fl = min(1, max(0, (t - a - 0.9) / 0.35))
            pill_ = dash_pill(pl, 'bell' if n == 4 else '+', 56 if n != 2 else 52, flip=fl)
            s_, a_ = pop(t, a + 0.5, b)
            place(fr, pill_, CX, ty + 160 * sc, s_ * sc, a_)
            if t < first:
                k = ease_out(min(1, max(0, (t - a - 0.4) / 0.5)))
                product(fr, GOLD_PNG, CX, 1060, t, h=470, scale=0.85 + 0.15 * k, alpha=min(k, max(0, (first - t) / 0.2)), phase=n)
            if scene == 't1':
                if T['gaji'] - 0.1 <= t < T['bil'] - 0.1:
                    e2 = T['bil'] - 0.1
                    rise(fr, glass_pill('Gaji dah masuk', icon='check'), CX, 520, t, T['gaji'] - 0.1, e2)
                    # salary cash arrives, then part of it slides across into the gold bar
                    kc = ease_out(min(1, max(0, (t - T['gaji']) / 0.5)))
                    fly = ease_out(min(1, max(0, (t - T['gaji'] - 1.3) / 0.7)))
                    product(fr, CASH_PNG, CX - 190 + 40 * fly, 830, t, w=420, scale=kc * (1 - 0.25 * fly), alpha=min(kc, (e2 - t) / 0.2),
                            shine_every=0)
                    if t > T['gaji'] + 1.0:
                        k = ease_out(min(1, (t - T['gaji'] - 1.0) / 0.5))
                        product(fr, GOLD_PNG, CX + 200, 800, t, h=440, scale=0.8 + 0.2 * k, alpha=min(k, (e2 - t) / 0.2))
                        rise(fr, label_card('Terus ketepikan', 'RM457 untuk emas', 'Simpan dulu'), CX + 200, 1060, t, T['gaji'] + 1.4, e2)
                    show(fr, dash_pill('Jangan tunggu lebihan hujung bulan', 'x', 40, flip=0), CX, 1180, t, T['lebihan'], e2)
                if t >= T['bil'] - 0.1:
                    kk = min(1, (t - T['bil'] + 0.1) / 0.4)
                    ang = 70 * (1 - ease_out(kk))
                    place(fr, fx3d.warp3d(bills_card(t, T['bil']), rx=ang, shade=False), CX, 820, 1, min(1, kk * 2, max(0, (b - t) / 0.15)))
            elif scene == 't2':
                show(fr, glass_pill('harga naik turun = biasa', icon='check'), CX, 560, t, T['naik'], T['dca'] - 0.2)
                if t >= T['dca'] - 0.2:
                    p = (t - T['dca']) / max(1.0, T['purata'] - T['dca'])
                    kk = min(1, (t - T['dca'] + 0.2) / 0.4)
                    place(fr, fx3d.warp3d(dca_chart(p), rx=70 * (1 - ease_out(kk)), shade=False), CX, 940, 0.86,
                          min(1, kk * 2, max(0, (b - t) / 0.15)))
                    show(fr, glass_pill('harga tinggi = gram sedikit', icon='x'), CX, 520, t, T['tinggi'], T['turun'] - 0.1)
                    show(fr, glass_pill('harga turun = lebih banyak gram', icon='check'), CX, 520, t, T['turun'], T['purata'] - 0.1)
                    show(fr, dash_pill('purata kos lebih seimbang', '+', 44, flip=min(1, max(0, (t - T['purata'] - 0.4) / 0.35))),
                         CX, 520, t, T['purata'], b)
            elif scene == 't3':
                bar_y = 930
                if t >= T['bonus'] - 0.4:
                    k = ease_out(min(1, (t - T['bonus'] + 0.4) / 0.5))
                    product(fr, GOLD_PNG, CX + 170, bar_y, t, h=470, scale=0.8 + 0.2 * k, alpha=min(k, max(0, (b - t) / 0.15)))
                    # extra income (cash) joins the gold on "tambah terus"
                    fly = ease_out(min(1, max(0, (t - T['tambah2']) / 0.7)))
                    product(fr, CASH_PNG, CX - 170 + 300 * fly, 1010 - 80 * fly, t, w=400, scale=k * (1 - 0.7 * fly),
                            alpha=min(k, 1 - fly), shine_every=0)
                for i, key in enumerate(('bonus', 'komisen', 'sampingan')):
                    t0, t1 = T[key] - 0.1, T['tambah2'] + 0.6
                    if t0 <= t < t1:
                        px, py = CX + (-210, 210, 0)[i], (590, 590, 690)[i]
                        if t > T['tambah2']:
                            k = ease_out((t - T['tambah2']) / 0.6)
                            px, py = px + (CX + 170 - px) * k, py + (bar_y - py) * k
                            s, al = 1 - 0.6 * k, 1 - k
                        else:
                            s, al = pop(t, t0, t1)
                        place(fr, glass_pill(('Bonus', 'Komisen', 'Pendapatan sampingan')[i], icon='+', size=44), px, py, s, al)
                if t >= T['cepat'] - 0.1:
                    kk = min(1, (t - T['cepat'] + 0.1) / 0.4)
                    place(fr, fx3d.warp3d(progress_card(t, T['cepat']), rx=60 * (1 - ease_out(kk)), shade=False), CX, 1180, 1,
                          min(1, kk * 2, max(0, (b - t) / 0.15)))
            elif scene == 't4':
                if T['set'] - 0.1 <= t < T['konsisten'] - 0.1:
                    e2 = T['konsisten'] - 0.1
                    k = ease_out(min(1, (t - T['set'] + 0.1) / 0.45))
                    shake = 6 * math.sin(t * 40) * max(0, 1 - (t - T['set'] - 0.4) / 0.5) if t > T['set'] + 0.4 else 0
                    place(fr, phone_notif(), CX + shake, 560 - (1 - k) * 200, 1, min(k, (e2 - t) / 0.15))
                    place(fr, calendar_card(t, T['set'] + 0.6), CX, 900, 1, min(1, max(0, (t - T['set'] - 0.4) / 0.3), (e2 - t) / 0.15))
                if t >= T['konsisten'] - 0.1:
                    rise(fr, H_konsisten, CX, 700, t, T['konsisten'] - 0.1, b)
                    show(fr, dash_pill('lebih penting dari jumlah', '+', 50, flip=min(1, max(0, (t - T['konsisten'] - 0.9) / 0.35))),
                         CX, 870, t, T['konsisten'] + 0.5, b)
        elif scene == 'end':
            e1 = T['mulakan'] - 0.1
            rise(fr, H_ingat, CX, 380, t, a + 0.05, e1)
            show(fr, dash_pill('bermula dengan 1 gram', '+', 52, flip=min(1, max(0, (t - T['satu'] - 0.2) / 0.35))), CX, 540, t, a + 0.5, e1)
            if t < e1:
                place(fr, coin3d(40 * math.sin(t * 1.8), size=380, label='1g', rx=-10), CX, 900, 1, min(1, (t - a) / 0.3, (e1 - t) / 0.15))
                if t >= T['satu'] + 0.4:
                    for i in range(9):
                        t0 = T['satu'] + 0.4 + i * 0.09
                        if t >= t0:
                            k = ease_out(min(1, (t - t0) / 0.35))
                            an = i * 2 * math.pi / 9
                            place(fr, coin3d(30 * math.sin(t * 2 + i), size=170, label='1g', rx=-10),
                                  CX + math.cos(an) * 330 * k, 900 + math.sin(an) * 300 * k, 1, min(k, (e1 - t) / 0.15))
            c0 = T['cta'] - 0.1
            rise(fr, H_mulakan, CX, 380, t, e1, c0)
            rise(fr, H_bulan, CX, 540, t, e1 + 0.2, c0)
            show(fr, glass_pill('setahun lagi kita akan bersyukur', icon='check', size=42), CX, 700, t, T['syukur'] - 0.6, c0)
            if t >= e1:
                k = ease_out(min(1, (t - e1) / 0.5))
                product(fr, GOLD_PNG, CX, 1030, t, h=500, scale=0.8 + 0.2 * k, alpha=k)
            rise(fr, H_cta, CX, 400, t, c0, base_dur)
            show(fr, dash_pill('Hubungi kami', 'arrow', 60), CX, 570, t, T['cta'] + 0.4, base_dur)

    def frame(t):
        if t >= base_dur:
            return light_outro(t - base_dur, logo_c)
        scene, a, b = scene_of(t)
        fr = bg.copy()
        lt = t - a
        content(fr, scene, t, a, b)
        # camera: push-in on scene entry, slow drift-in, whip blur across the cut
        s = 1.0 + 0.035 * min(1, lt / max(1.0, b - a))
        if lt < 0.3:
            s += 0.10 * (1 - ease_out(lt / 0.3))
        whip, dx = 0.0, 0.0
        if lt < 0.12 and a > 0:
            whip, dx = 1 - lt / 0.12, -80 * (1 - lt / 0.12)
        elif b - t < 0.12 and b < base_dur:
            whip, dx = 1 - (b - t) / 0.12, 80 * (1 - (b - t) / 0.12)
        fr = camera(fr, s, dx, whip)
        place(fr, wm, 95, 1010, 0.8, 0.6)
        for a0, a1, c in chunks:
            if a0 <= t < a1:
                act = max([i for i, w in enumerate(c) if w['os'] <= t] or [0])
                place(fr, subtitle(c, act), W / 2 - 40, B.TT_CAPTION_Y, 1, min(1, (t - a0) / 0.08))
                break
        return fr

    def guides(img, sx):
        g = Image.new('RGBA', img.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        for z in ((0, 0, 1080, B.TT_TOP), (0, B.TT_BOTTOM, 1080, 1920), (B.TT_RIGHT, B.TT_RAIL_Y[0], 1080, B.TT_RAIL_Y[1])):
            gd.rectangle([v * sx for v in z], fill=(255, 0, 60, 40), outline=(255, 0, 60, 200), width=2)
        img.alpha_composite(g)

    if '--demo' in sys.argv:
        t0, t1 = 0.0, T['bil'] + 1.5
        ddir = os.path.join(OUT, 'demo')
        os.makedirs(ddir, exist_ok=True)
        for f in os.listdir(ddir):
            os.remove(os.path.join(ddir, f))
        n = int((t1 - t0) * FPS)
        for i in range(n):
            frame(t0 + i / FPS).convert('RGB').resize((720, 1280), Image.LANCZOS).save(os.path.join(ddir, f'd{i:04d}.jpg'), quality=95)
        render_voice_and_base(base_dur)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(ddir, 'd%04d.jpg'),
                        '-ss', f'{t0}', '-t', f'{t1 - t0}', '-i', os.path.join(OUT, 'base.mov'), '-map', '0:v', '-map', '1:a',
                        '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest',
                        '-movflags', '+faststart', os.path.join(WORK, 'PREVIEW_motion_demo.mp4')], check=True)
        print('demo ok', round(t1 - t0, 1))
        return

    if '--preview' in sys.argv:
        shots = [('Hook', 2.2), ('10 gram emas', T['setahun'] + 0.6), ('Kiraan RM548', T['rm5480'] + 0.8),
                 ('RM457 sebulan', T['rm15'] + 0.9), ('Tak menakutkan', T['takut'] + 0.7), ('Teknik 1', T['t1'] + 1.4),
                 ('Gaji -> RM457', T['lebihan'] + 1.0), ('Bil wajib', T['bil'] + 2.2), ('Teknik 2', T['t2'] + 1.4),
                 ('DCA', T['turun'] + 1.0), ('Purata kos', T['purata'] + 2.0), ('Teknik 3', T['komisen'] + 0.5),
                 ('Bonus -> emas', T['tambah2'] + 0.3), ('Lebih cepat', T['cepat'] + 2.6), ('Teknik 4', T['set'] + 1.6),
                 ('Konsistensi', T['konsisten'] + 1.4), ('1 gram -> 10', T['satu'] + 0.9), ('Mulakan bulan ni', T['syukur'] + 0.3),
                 ('CTA', base_dur - 0.4), ('Outro', base_dur + 1.6)]
        tiles_ = []
        sx = 360 / 1080
        for label, tt in shots:
            tl = frame(tt).resize((360, 640), Image.LANCZOS)
            guides(tl, sx)
            mm, ss = divmod(tt, 60)
            t2_ = Image.new('RGB', (360, 684), (24, 24, 30))
            t2_.paste(tl.convert('RGB'), (0, 0))
            ImageDraw.Draw(t2_).text((6, 662), f'{int(mm)}:{ss:04.1f}  {label}', font=jf(J_SB, 22), fill=WHITE, anchor='lm')
            tiles_.append(t2_)
        cols = 10
        rows = math.ceil(len(tiles_) / cols)
        sheet = Image.new('RGB', (cols * 372 + 12, rows * 696 + 12), (24, 24, 30))
        for i, tl in enumerate(tiles_):
            sheet.paste(tl, (12 + (i % cols) * 372, 12 + (i // cols) * 696))
        sheet.save(os.path.join(WORK, 'PREVIEW_storyboard.jpg'), quality=86)
        print('preview ok; segments', len(SEGS), 'base', round(base_dur, 2), 'total', round(total, 2))
        return

    render_voice_and_base(base_dur)
    fdir = os.path.join(OUT, 'frames')
    os.makedirs(fdir, exist_ok=True)
    for fi in range(int(round(total * FPS))):
        frame(fi / FPS).save(os.path.join(fdir, f'f{fi:05d}.png'), compress_level=1)
    write_sfx(total, pops, whooshes, os.path.join(OUT, 'sfx.wav'))
    final = os.path.join(OUT, '10GramEmasSetahun_AzlanEza.mp4')
    composite(os.path.join(OUT, 'base.mov'), fdir, os.path.join(OUT, 'sfx.wav'), total, final,
              music=MUSIC, music_ss=MUSIC_SS, music_db=MUSIC_DB, music_tempo=MUSIC_TEMPO)
    print('done', final)


if __name__ == '__main__':
    main()
