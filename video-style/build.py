#!/usr/bin/env python3
"""Branded talking-head short: Azlan & Eza / PGLS Norway."""
import json, math, os, re, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

ROOT = os.path.dirname(os.path.abspath(__file__))
# Inputs/outputs are overridable so raw footage never has to live in the repo.
FONTS = os.path.join(ROOT, 'assets', 'fonts')
RAW = os.environ.get('RAW', os.path.join(ROOT, 'work', 'raw.mp4'))
LOGO = os.environ.get('LOGO', os.path.join(ROOT, 'assets', 'logo.png'))
OUT = os.environ.get('OUT', os.path.join(ROOT, 'work', 'out'))
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
OUTRO = 3.5
F_XB = os.path.join(FONTS, 'Poppins-ExtraBold.ttf')
F_B = os.path.join(FONTS, 'Poppins-Bold.ttf')

# TikTok safe zones on 1080x1920 (approx.): keep text and key graphics out of the top tab bar (y<150), the bottom
# caption/username/sound block (y>1460) and the right action rail (x>940, 760<y<1520).
TT_TOP, TT_BOTTOM, TT_RIGHT, TT_RAIL_Y = 150, 1460, 940, (760, 1520)
TT_CAPTION_Y = 1390          # one-word captions sit just above the bottom UI block
TT_CENTER_X = 1080 / 2 - 50  # full-screen cards shift left of the action rail
RED = (176, 30, 48)
KHAKI = (214, 210, 154)
NAVY = (14, 16, 32)
CYAN = (37, 244, 238)
PINK = (254, 44, 85)

# ---------------------------------------------------------------- edit decision
# source-time keep ranges (fillers "Aa" x3, "Okey" and dead air removed)
SEGS = [(0.50, 1.62), (2.68, 3.66), (3.90, 6.64), (7.62, 12.80),
        (13.82, 17.45), (17.73, 19.58), (19.90, 22.34)]
ZOOM = [1.0, 1.07, 1.0, 1.07, 1.0, 1.07, 1.0]

# phrase groups: text + speech sub-regions (source time) from energy analysis,
# anchored to Descript's verified word/silence times
GROUPS = [
    ("Assalamualaikum", [(0.65, 1.51)]),
    ("Azie dengan Capik", [(2.70, 3.31), (3.45, 3.56)]),
    ("Kita tetap dalam masih berada di Munich. Alright.",
     [(3.98, 5.21), (5.29, 6.00), (6.30, 6.56)]),
    ("jadi insyaAllah tahun depan untuk PGLS Norway kita sama-sama akan ke sana.",
     [(7.63, 8.37), (8.52, 8.93), (9.02, 9.27), (9.40, 9.94), (10.04, 11.05),
      (11.27, 11.96), (12.05, 12.17), (12.28, 12.68)]),
    ("so fokus saja pulas business talk dengan betul, buat persiapan betul dengan sabar.",
     [(13.89, 13.96), (14.08, 14.48), (14.60, 15.49), (15.62, 16.03), (16.11, 17.33)]),
    ("InsyaAllah kejayaan hanyalah persoalan masa.", [(17.83, 18.57), (18.70, 19.48)]),
    ("Berjumpa di Norway dengan double tiket.",
     [(20.00, 20.20), (20.28, 20.94), (21.17, 21.46), (21.61, 22.05), (22.15, 22.24)]),
]
SYL = {'PGLS': 4, 'Alright': 2, 'business': 2, 'talk': 1, 'double': 2, 'so': 1,
       'Norway': 2, 'Munich': 2}


def syllables(w):
    if w in SYL:
        return SYL[w]
    return max(1, len(re.findall(r'[aeiouAEIOU]+', w)))


def align_words():
    words = []
    for text, regs in GROUPS:
        toks = [t.strip('.,') for t in text.split()]
        wts = [syllables(t) for t in toks]
        total_sp = sum(b - a for a, b in regs)
        cum = np.cumsum([0] + wts) / sum(wts) * total_sp

        def sp2t(x):  # speech-time -> source time
            for a, b in regs:
                if x <= (b - a) + 1e-9:
                    return a + x
                x -= (b - a)
            return regs[-1][1]
        for i, t in enumerate(toks):
            words.append({'w': t, 's': sp2t(cum[i] + 1e-4), 'e': sp2t(cum[i + 1])})
    return words


def seg_offsets():
    offs, t = [], 0.0
    for a, b in SEGS:
        offs.append(t)
        t += b - a
    return offs, t


def src2out(x):
    offs, _ = seg_offsets()
    for (a, b), o in zip(SEGS, offs):
        if a - 0.05 <= x <= b + 0.05:
            return o + min(max(x, a), b) - a
    return None


# ---------------------------------------------------------------- base video
def render_base():
    cx_full, cy_face = 1150 + 1215 / 2, 0.48 * 2160
    parts = []
    for i, ((a, b), z) in enumerate(zip(SEGS, ZOOM)):
        d = b - a
        cw, ch = 1215 / z, 2160 / z
        x = min(max(cx_full - cw / 2, 0), 3840 - cw)
        y = min(max(cy_face - ch / 2, 0), 2160 - ch)
        p = os.path.join(OUT, f'seg{i}.mp4')
        vf = (f"crop={cw:.0f}:{ch:.0f}:{x:.0f}:{y:.0f},scale={W}:{H}:flags=lanczos,"
              f"setsar=1,fps={FPS},eq=contrast=1.05:saturation=1.12:gamma=1.02")
        af = (f"aresample=48000,afade=t=in:d=0.03,afade=t=out:st={d-0.03:.3f}:d=0.03")
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a}', '-t', f'{d}', '-i', RAW,
                        '-map', '0:v:0', '-map', '0:a:0', '-vf', vf, '-af', af,
                        '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', '-pix_fmt', 'yuv420p',
                        '-c:a', 'pcm_s16le', '-ac', '2', p], check=True)
        parts.append(p)
    lst = os.path.join(OUT, 'list.txt')
    open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst,
                    '-c', 'copy', os.path.join(OUT, 'base.mov')], check=True)


# ---------------------------------------------------------------- drawing helpers
def ease_out(t):
    t = min(max(t, 0), 1)
    return 1 - (1 - t) ** 3


def back_out(t, s=1.9):
    t = min(max(t, 0), 1) - 1
    return t * t * ((s + 1) * t + s) + 1


def font(path, size):
    return ImageFont.truetype(path, size)


def text_sprite(txt, size, fill_top, fill_bot=None, stroke=0, stroke_col=(0, 0, 0),
                shadow=True, path=F_XB, tracking=0):
    f = font(path, size)
    bb = f.getbbox(txt, stroke_width=stroke)
    pad = int(size * 0.35)
    tw, th = bb[2] - bb[0] + pad * 2, bb[3] - bb[1] + pad * 2
    mask = Image.new('L', (tw, th), 0)
    ImageDraw.Draw(mask).text((pad - bb[0], pad - bb[1]), txt, font=f, fill=255)
    smask = Image.new('L', (tw, th), 0)
    if stroke:
        ImageDraw.Draw(smask).text((pad - bb[0], pad - bb[1]), txt, font=f, fill=255,
                                   stroke_width=stroke, stroke_fill=255)
    fill_bot = fill_bot or fill_top
    grad = np.zeros((th, tw, 4), np.uint8)
    ys = np.clip((np.arange(th) - pad) / max(1, th - 2 * pad), 0, 1)[:, None]
    for c in range(3):
        grad[..., c] = (fill_top[c] * (1 - ys) + fill_bot[c] * ys).astype(np.uint8)
    grad[..., 3] = 255
    fill = Image.fromarray(grad)
    out = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    if shadow:
        sh = (smask if stroke else mask).filter(ImageFilter.GaussianBlur(size * 0.09))
        sh = sh.point(lambda v: int(v * 0.75))
        shimg = Image.new('RGBA', (tw, th), (0, 0, 0, 255))
        shimg.putalpha(sh)
        out.alpha_composite(shimg, (0, int(size * 0.05)))
    if stroke:
        st = Image.new('RGBA', (tw, th), stroke_col + (255,))
        st.putalpha(smask)
        out.alpha_composite(st)
    fill.putalpha(mask)
    out.alpha_composite(fill)
    return out


def rounded(size, r, fill, outline=None, width=0):
    im = Image.new('RGBA', size, (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], r, fill=fill,
                                         outline=outline, width=width)
    return im


def with_shadow(im, blur=22, off=10, alpha=0.45):
    pad = blur * 2
    out = Image.new('RGBA', (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    a = im.getchannel('A').point(lambda v: int(v * alpha))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 255))
    sh.putalpha(a)
    out.alpha_composite(sh, (pad, pad + off))
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(im, (pad, pad))
    return out


def place(frame, spr, cx, cy, scale=1.0, alpha=1.0, rot=0):
    if scale <= 0.01 or alpha <= 0.01:
        return
    s = spr
    if rot:
        s = s.rotate(rot, resample=Image.BICUBIC, expand=True)
    if abs(scale - 1) > 1e-3:
        s = s.resize((max(1, int(s.width * scale)), max(1, int(s.height * scale))), Image.BICUBIC)
    if alpha < 1:
        s = s.copy()
        s.putalpha(s.getchannel('A').point(lambda v: int(v * alpha)))
    frame.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2))) if (
        0 <= int(cx - s.width / 2) and 0 <= int(cy - s.height / 2) and
        int(cx - s.width / 2) + s.width <= W and int(cy - s.height / 2) + s.height <= H) else \
        paste_clip(frame, s, int(cx - s.width / 2), int(cy - s.height / 2))


def paste_clip(frame, s, x, y):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + s.width), min(H, y + s.height)
    if x1 <= x0 or y1 <= y0:
        return
    frame.alpha_composite(s.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))


def pop(t, t0, t1, dur_in=0.28, dur_out=0.18):
    """scale, alpha for an element visible t0..t1 with bounce in / shrink out."""
    if t < t0 or t > t1:
        return 0, 0
    if t < t0 + dur_in:
        k = (t - t0) / dur_in
        return back_out(k), min(1, k * 2.5)
    if t > t1 - dur_out:
        k = (t1 - t) / dur_out
        return 0.6 + 0.4 * k, k
    return 1, 1


# ---------------------------------------------------------------- assets
def paper_texture(w, h, seed=3):
    rng = np.random.default_rng(seed)
    base = np.zeros((h, w), np.float32)
    for sc, amp in ((6, 1.0), (14, 0.55), (40, 0.3)):
        n = rng.random((h // sc + 2, w // sc + 2)).astype(np.float32)
        im = Image.fromarray((n * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        base += np.asarray(im, np.float32) / 255 * amp
    # crease lines
    cr = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(cr)
    for _ in range(26):
        x0, y0 = rng.integers(-200, w + 200, 2)
        ang = rng.random() * math.pi
        L = rng.integers(300, 1400)
        d.line([x0, y0, x0 + math.cos(ang) * L, y0 + math.sin(ang) * L], fill=int(rng.integers(40, 120)),
               width=int(rng.integers(2, 5)))
    cr = np.asarray(cr.filter(ImageFilter.GaussianBlur(3)), np.float32) / 255
    emb = np.gradient(base, axis=1) * 9 + np.gradient(base, axis=0) * 6
    v = 236 + emb * 26 - cr * 22 + (base - base.mean()) * 10
    v = np.clip(v, 190, 252)
    rgb = np.stack([v, v + 1, v + 4], -1).clip(0, 255).astype(np.uint8)
    return Image.fromarray(rgb).convert('RGBA')


def load_logos():
    lg = Image.open(LOGO).convert('RGBA')
    bb = lg.getbbox()
    lg = lg.crop(bb)
    a = np.asarray(lg).copy()
    lum = a[..., :3].astype(int).mean(-1)
    dark = (lum < 70) & (a[..., 3] > 0)
    white = a.copy()
    white[dark, :3] = 255
    return lg, Image.fromarray(white)


def pill(text, icon=None, size=46, fg=(20, 20, 30), bg=(255, 255, 255, 245), padx=34, pady=18,
         icon_w=0):
    f = font(F_B, size)
    bb = f.getbbox(text)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    iw = icon.width + 18 if icon is not None else 0
    w, h = tw + padx * 2 + iw, th + pady * 2 + 8
    im = rounded((w, h), h // 2, bg)
    if icon is not None:
        im.alpha_composite(icon, (padx, (h - icon.height) // 2))
    ImageDraw.Draw(im).text((padx + iw - bb[0], (h - th) // 2 - bb[1]), text, font=f, fill=fg)
    return with_shadow(im, 16, 8, 0.35)


def pin_icon(s=52):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([s * .18, 0, s * .82, s * .64], fill=RED + (255,))
    d.polygon([(s * .22, s * .42), (s * .78, s * .42), (s * .5, s * .98)], fill=RED + (255,))
    d.ellipse([s * .37, s * .17, s * .63, s * .43], fill=(255, 255, 255, 255))
    return im


def de_flag(w=60, h=40):
    im = Image.new('RGBA', (w, h))
    d = ImageDraw.Draw(im)
    for i, c in enumerate([(0, 0, 0), (221, 0, 0), (255, 206, 0)]):
        d.rectangle([0, i * h / 3, w, (i + 1) * h / 3], fill=c + (255,))
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 7, fill=255)
    im.putalpha(m)
    return im


def my_flag(w=60, h=40):
    im = Image.new('RGBA', (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    sh = h / 14
    for i in range(0, 14, 2):
        d.rectangle([0, i * sh, w, (i + 1) * sh], fill=(204, 0, 1, 255))
    cw, ch = w * 0.5, sh * 8
    d.rectangle([0, 0, cw, ch], fill=(1, 0, 102, 255))
    r = ch * 0.36
    cx, cy = cw * 0.38, ch / 2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 204, 0, 255))
    r2 = r * 0.82
    d.ellipse([cx - r2 + r * 0.32, cy - r2, cx + r2 + r * 0.32, cy + r2], fill=(1, 0, 102, 255))
    sx, sy, R = cw * 0.74, cy, ch * 0.24
    pts = []
    for k in range(28):
        rr = R if k % 2 == 0 else R * 0.45
        a = -math.pi / 2 + k * math.pi / 14
        pts.append((sx + rr * math.cos(a), sy + rr * math.sin(a)))
    d.polygon(pts, fill=(255, 204, 0, 255))
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 7, fill=255)
    im.putalpha(m)
    return im


def no_flag(w=60, h=44):
    im = Image.new('RGBA', (w, h), (186, 12, 47, 255))
    d = ImageDraw.Draw(im)
    u = h / 16
    d.rectangle([w * 6 / 22, 0, w * 10 / 22, h], fill=(255, 255, 255, 255))
    d.rectangle([0, 6 * u, w, 10 * u], fill=(255, 255, 255, 255))
    d.rectangle([w * 7 / 22, 0, w * 9 / 22, h], fill=(0, 32, 91, 255))
    d.rectangle([0, 7 * u, w, 9 * u], fill=(0, 32, 91, 255))
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 7, fill=255)
    im.putalpha(m)
    return im


def check_icon(s=46, col=(34, 197, 94)):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, s - 1, s - 1], fill=col + (255,))
    d.line([(s * .27, s * .52), (s * .44, s * .69), (s * .74, s * .33)], fill=(255, 255, 255, 255),
           width=max(3, s // 9), joint='curve')
    return im


def cal_icon(s=50):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, s * .1, s - 1, s - 1], 9, fill=(255, 255, 255, 255), outline=(40, 40, 50, 255), width=3)
    d.rounded_rectangle([0, s * .1, s - 1, s * .38], 9, fill=RED + (255,))
    d.rectangle([0, s * .28, s - 1, s * .38], fill=RED + (255,))
    for gx in (.25, .5, .75):
        for gy in (.55, .8):
            d.ellipse([s * gx - 3, s * gy - 3, s * gx + 3, s * gy + 3], fill=(60, 60, 70, 255))
    return im


def ticket(w=560, h=230, sub='PGLS • NORWAY'):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 26, fill=(255, 255, 255, 255))
    stub = int(w * 0.70)
    d.rounded_rectangle([stub, 0, w - 1, h - 1], 26, fill=RED + (255,))
    d.rectangle([stub, 0, stub + 30, h - 1], fill=RED + (255,))
    for cy in (0, h):  # notches
        d.ellipse([stub - 20, cy - 20, stub + 20, cy + 20], fill=(0, 0, 0, 0))
    for y in range(22, h - 22, 22):
        d.line([stub, y, stub, y + 10], fill=(200, 200, 205, 255), width=3)
    f1, f2, f3 = font(F_B, 26), font(F_XB, 54), font(F_B, 30)
    d.text((34, 26), 'BOARDING PASS', font=f1, fill=(130, 130, 140, 255))
    d.text((34, 70), 'MYS', font=f2, fill=(25, 25, 35, 255))
    d.line([(180, 102), (232, 102)], fill=RED + (255,), width=9)
    d.polygon([(228, 88), (250, 102), (228, 116)], fill=RED + (255,))
    d.text((262, 70), 'NOR', font=f2, fill=(25, 25, 35, 255))
    d.text((34, 160), sub, font=f3, fill=(70, 70, 80, 255))
    fl = no_flag(80, 58)
    im.alpha_composite(fl, (stub + (w - stub - 80) // 2, 40))
    d.text((stub + (w - stub) / 2, 160), 'x1', font=font(F_XB, 40), fill=(255, 255, 255, 255), anchor='mm')
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 26, fill=255)
    for cy in (0, h):
        ImageDraw.Draw(m).ellipse([stub - 20, cy - 20, stub + 20, cy + 20], fill=0)
    im.putalpha(ImageChops.multiply(im.getchannel('A'), m))
    return with_shadow(im, 20, 12, 0.4)


# ---------------------------------------------------------------- shared outro / sfx / composite
_NAVY = None


def outro_frame(to, fi, logo_w, name='Azlan & Eza'):
    """Dark branded outro: glitch logo bounce-in + search-bar pill, fade to black."""
    global _NAVY
    if _NAVY is None:
        _NAVY = Image.new('RGBA', (W, H), NAVY + (255,))
    fr = _NAVY.copy()
    sc = back_out(min(1, to / 0.45)) * 0.66
    if (to < 0.5) and (fi % 3 != 0):
        for col, dx in ((CYAN, -14), (PINK, 14)):
            g = Image.new('RGBA', logo_w.size, col + (255,))
            g.putalpha(logo_w.getchannel('A').point(lambda v: int(v * 0.6)))
            place(fr, g, W / 2 + dx * (1 - to / 0.5), H * 0.40, sc, 1)
    place(fr, logo_w, W / 2, H * 0.40, sc, min(1, to / 0.2))
    k = ease_out((to - 0.5) / 0.4)
    if k > 0:
        pw, ph = 720, 104
        p_im = Image.new('RGBA', (pw + 24, ph + 24), (0, 0, 0, 0))
        pdr = ImageDraw.Draw(p_im)
        pdr.rounded_rectangle([0, 6, pw, ph + 6], 22, fill=CYAN + (255,))
        pdr.rounded_rectangle([12, 6, pw + 12, ph + 6], 22, fill=PINK + (255,))
        pdr.rounded_rectangle([6, 6, pw + 6, ph + 6], 22, fill=(255, 255, 255, 255))
        pdr.ellipse([46, 32, 86, 72], outline=(40, 40, 50, 255), width=6)
        pdr.line([80, 66, 100, 86], fill=(40, 40, 50, 255), width=7)
        pdr.text((128, 56), name, font=font(F_B, 50), fill=(25, 25, 35, 255), anchor='lm')
        pdr.rounded_rectangle([pw - 150, 18, pw - 10, ph - 6], 16, fill=RED + (255,))
        pdr.text((pw - 80, 56), 'Follow', font=font(F_B, 34), fill=(255, 255, 255, 255), anchor='mm')
        place(fr, p_im, W / 2, H * 0.62 + (1 - k) * 80, 1, k)
    if to > OUTRO - 0.5:
        fr.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * (to - (OUTRO - 0.5)) / 0.5))))
    return fr


def write_sfx(total, pops, whooshes, path, sr=48000):
    """pops: start times; whooshes: (start, dur, vol) tuples."""
    n = int(total * sr)
    sfx = np.zeros(n, np.float32)
    rng = np.random.default_rng(1)

    def add(i0, seg):
        if 0 <= i0 < n:
            sfx[i0:i0 + len(seg)] += seg[:n - i0]
    for t0, dur, vol in whooshes:
        m = int(dur * sr)
        out = np.convolve(rng.standard_normal(m).astype(np.float32), np.ones(24) / 24, 'same')
        add(int(t0 * sr), out * np.sin(np.linspace(0, math.pi, m)) ** 2 * vol)
    for t0 in pops:
        m = int(0.09 * sr)
        tt = np.arange(m) / sr
        add(int(t0 * sr), np.sin(2 * math.pi * (880 + 600 * tt / 0.09) * tt) * np.exp(-tt * 40) * 0.12)
    st = np.stack([sfx, sfx], -1)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes())


def audio_mix_graph(voice, sfx, total, music=None, music_ss=0.0, music_db=-14.0, out='a', outro_at=None,
                    music_tempo=1.0):
    """Voice + SFX, plus an optional music bed that ducks under the voice (sidechain) and rises on the outro."""
    g = (f"{voice}apad=whole_dur={total},asplit=2[vx][vkey];"
         f"[vx]{sfx}amix=inputs=2:normalize=0:duration=first[vs];")
    if music:
        lead = (f"atrim=start={music_ss},asetpts=PTS-STARTPTS" if music_ss >= 0   # negative = start the music later
                else f"adelay={int(-music_ss * 1000)}:all=1")
        if music_tempo != 1.0:   # stretch a slightly-too-short track
            lead += f",atempo={music_tempo}"
        g += (f"{music}{lead},aresample=48000,volume={music_db}dB,"
              f"apad=whole_dur={total},atrim=end={total},afade=t=in:d=0.8"
              + (f",volume='1+1.8*min(max((t-{outro_at})/0.6\\,0)\\,1)':eval=frame" if outro_at else '') + "[mu];"
              f"[mu][vkey]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=400:makeup=1[md];"
              f"[vs][md]amix=inputs=2:normalize=0:duration=first,")
    else:
        g += "[vkey]anullsink;[vs]"
    g += f"afade=t=in:d=0.2,afade=t=out:st={total-0.8}:d=0.8,loudnorm=I=-14:TP=-1.5:LRA=11[{out}]"
    return g


def composite(base, fdir, sfx, total, final, music=None, music_ss=0.0, music_db=-14.0, music_tempo=1.0):
    """Base video (+ cloned last frame under the outro) + RGBA overlay frames + sfx (+ music bed) -> final mp4."""
    fc = (f"[0:v]tpad=stop_mode=clone:stop_duration={OUTRO}[bv];"
          f"[bv][1:v]overlay=0:0:format=auto,fade=t=in:d=0.3,format=yuv420p[v];"
          + audio_mix_graph('[0:a]', '[2:a]', total, '[3:a]' if music else None, music_ss, music_db,
                            outro_at=total - OUTRO, music_tempo=music_tempo))
    cmd = ['ffmpeg', '-v', 'error', '-y', '-i', base, '-framerate', str(FPS), '-i', os.path.join(fdir, 'f%05d.png'),
           '-i', sfx]
    if music:
        cmd += ['-i', music]
    subprocess.run(cmd + ['-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-t', f'{total}', '-r', str(FPS),
                          '-c:v', 'libx264', '-crf', '19', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-movflags', '+faststart', final],
                   check=True)


# ---------------------------------------------------------------- main overlay render
def main():
    if '--skip-base' not in sys.argv:
        render_base()
    words = align_words()
    for w in words:
        w['os'], w['oe'] = src2out(w['s']), src2out(w['e'])
    words = [w for w in words if w['os'] is not None]
    json.dump(words, open(os.path.join(OUT, 'words.json'), 'w'), indent=1)
    offs, base_dur = seg_offsets()
    total = base_dur + OUTRO
    nfr = int(round(total * FPS))

    def wt(word, nth=1):
        k = 0
        for w in words:
            if w['w'].lower() == word.lower():
                k += 1
                if k == nth:
                    return w['os']
        raise KeyError(word)

    seg_t = [(o, o + (b - a)) for (a, b), o in zip(SEGS, offs)]

    # caption sprites (one word at a time)
    cap_cache = {}

    def cap(word):
        if word not in cap_cache:
            disp = word if word.isupper() else word.lower()
            sz = 104
            while font(F_XB, sz).getlength(disp) > 900:
                sz -= 4
            cap_cache[word] = text_sprite(disp, sz, (255, 255, 255), (247, 228, 160), stroke=5,
                                          stroke_col=(25, 18, 20))
        return cap_cache[word]
    cap_win = []
    for i, w in enumerate(words):
        nxt = words[i + 1]['os'] if i + 1 < len(words) else w['oe'] + 0.3
        end = nxt if nxt - w['oe'] < 0.35 else w['oe'] + 0.15
        # don't let captions cross segment ends
        cap_win.append((w['os'], end, w['w']))

    # title
    t_l1 = text_sprite('PGLS', 190, (255, 120, 135), RED, stroke=6, stroke_col=(255, 255, 255))
    t_l2 = text_sprite('NORWAY', 172, (255, 255, 255), (232, 232, 240), stroke=0)
    # location pill
    loc = pill('Munich', icon=pin_icon(66), size=60)
    flag_de = with_shadow(de_flag(100, 66), 10, 5, 0.35)
    # year chip
    year = pill('Tahun depan', icon=cal_icon(64), size=58)
    # checklist pills
    chk = {k: pill(k, icon=check_icon(58), size=56) for k in ('Fokus', 'Business talk', 'Persiapan', 'Sabar')}
    # tickets
    tk1, tk2 = ticket(), ticket()
    x2 = text_sprite('x2', 150, (255, 235, 150), (240, 190, 60), stroke=6, stroke_col=RED)
    logo_c, logo_w = load_logos()
    wm = logo_w.resize((150, int(150 * logo_w.height / logo_w.width)), Image.LANCZOS)
    paper = paper_texture(W, H)

    # progress card
    def progress_card(p):
        cw, ch = 900, 210
        im = rounded((cw, ch), 34, (16, 18, 34, 235))
        d = ImageDraw.Draw(im)
        d.text((44, 36), 'KEJAYAAN', font=font(F_XB, 46), fill=(255, 255, 255, 255))
        d.text((cw - 44, 36), f'{int(p * 100)}%', font=font(F_XB, 46), fill=(247, 228, 160, 255), anchor='ra')
        d.rounded_rectangle([44, 128, cw - 44, 166], 19, fill=(55, 58, 80, 255))
        x1 = 44 + (cw - 88) * p
        if x1 > 64:
            bar = Image.new('RGBA', (int(x1 - 44), 38))
            g = np.linspace(0, 1, bar.width)[None, :, None]
            arr = (np.array(RED)[None, None, :] * (1 - g) + np.array((247, 210, 120))[None, None, :] * g)
            arr = np.repeat(arr, 38, 0).astype(np.uint8)
            bar = Image.fromarray(arr).convert('RGBA')
            m = Image.new('L', bar.size, 0)
            ImageDraw.Draw(m).rounded_rectangle([0, 0, bar.width - 1, 37], 19, fill=255)
            bar.putalpha(m)
            im.alpha_composite(bar, (44, 128))
        d.text((44, 176), 'hanyalah persoalan masa ⏳'.replace(' ⏳', ''), font=font(F_B, 26),
               fill=(170, 172, 190, 255))
        return with_shadow(im, 18, 10, 0.45)

    # cutaway (route card)
    cut_in = wt('untuk') - 0.05
    cut_out = min(seg_t[3][1], wt('sana') + 0.35)

    def route_card(p):
        cw, ch = 900, 1060
        im = rounded((cw, ch), 48, (18, 20, 36, 255))
        d = ImageDraw.Draw(im)
        d.text((cw / 2, 92), 'NEXT STOP', font=font(F_B, 34), fill=(150, 154, 180, 255), anchor='mm')
        d.text((cw / 2, 170), 'PGLS NORWAY', font=font(F_XB, 82), fill=(255, 255, 255, 255), anchor='mm')
        A, C, B = (170, 720), (300, 330), (720, 420)

        def bz(t):
            return ((1 - t) ** 2 * A[0] + 2 * (1 - t) * t * C[0] + t * t * B[0],
                    (1 - t) ** 2 * A[1] + 2 * (1 - t) * t * C[1] + t * t * B[1])
        n = 60
        pe = ease_out(p)
        for i in range(n):
            t0, t1 = i / n, (i + 0.55) / n
            if t0 > pe:
                break
            d.line([bz(t0), bz(min(t1, pe))], fill=(247, 228, 160, 255), width=8)
        for pt, lab, fl, sub in ((A, 'MALAYSIA', None, ''), (B, 'NORWAY', no_flag(70, 50), 'tahun depan')):
            d.ellipse([pt[0] - 22, pt[1] - 22, pt[0] + 22, pt[1] + 22], fill=RED + (255,), outline=(255, 255, 255, 255), width=6)
        im.alpha_composite(my_flag(70, 46), (A[0] - 35, A[1] + 40))
        d.text((A[0] + 50, A[1] + 62), 'MALAYSIA', font=font(F_XB, 44), fill=(255, 255, 255, 255), anchor='lm')
        if pe > 0.85:
            k = (pe - 0.85) / 0.15
            im.alpha_composite(no_flag(70, 50), (B[0] - 35, B[1] - 110))
            d.text((B[0], B[1] + 60), 'NORWAY', font=font(F_XB, 44), fill=(255, 255, 255, int(255 * k)), anchor='mm')
        # plane
        px, py = bz(pe)
        qx, qy = bz(min(1, pe + 0.01))
        ang = math.degrees(math.atan2(qy - py, qx - px))
        pl = Image.new('RGBA', (90, 90), (0, 0, 0, 0))
        pd = ImageDraw.Draw(pl)
        pd.polygon([(88, 45), (10, 36), (10, 54)], fill=(255, 255, 255, 255))
        pd.polygon([(55, 45), (30, 6), (20, 6), (35, 45)], fill=(255, 255, 255, 255))
        pd.polygon([(55, 45), (30, 84), (20, 84), (35, 45)], fill=(255, 255, 255, 255))
        pd.polygon([(16, 45), (4, 26), (0, 26), (8, 45)], fill=(255, 255, 255, 255))
        pd.polygon([(16, 45), (4, 64), (0, 64), (8, 45)], fill=(255, 255, 255, 255))
        pl = pl.rotate(-ang, resample=Image.BICUBIC, expand=True)
        im.alpha_composite(pl, (int(px - pl.width / 2), int(py - pl.height / 2)))
        # sama-sama chip
        d.rounded_rectangle([cw / 2 - 260, ch - 150, cw / 2 + 260, ch - 66], 42, fill=(255, 255, 255, 255))
        d.text((cw / 2, ch - 108), 'kita sama-sama ke sana', font=font(F_B, 36), fill=(25, 25, 35, 255), anchor='mm')
        return with_shadow(im, 28, 16, 0.4)

    fdir = os.path.join(OUT, 'frames')
    os.makedirs(fdir, exist_ok=True)
    t_fokus, t_bt, t_pers, t_sabar = wt('fokus'), wt('business'), wt('persiapan'), wt('sabar')
    t_double = wt('double')
    t_tahun = wt('tahun')

    for fi in range(nfr):
        t = fi / FPS
        fr = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        main_part = t < base_dur

        # ---- cutaway (full screen)
        in_cut = cut_in <= t <= cut_out
        if in_cut:
            k_in = ease_out((t - cut_in) / 0.22)
            k_out = ease_out((cut_out - t) / 0.18)
            a = min(k_in, k_out)
            bgp = paper.copy()
            bgp.putalpha(int(255 * a))
            fr.alpha_composite(bgp)
            card = route_card((t - cut_in - 0.2) / max(0.1, (cut_out - cut_in - 0.7)))
            place(fr, card, W / 2, H * 0.43 + (1 - k_in) * 120, scale=1.12 - 0.12 * k_in, alpha=a)

        if main_part and not in_cut:
            # ---- title (segments A+B)
            s1, a1 = pop(t, 0.12, seg_t[1][1] - 0.05, 0.32)
            s2, a2 = pop(t, 0.30, seg_t[1][1] - 0.05, 0.32)
            place(fr, t_l1, W / 2 - 150, 190, s1, a1, rot=4)
            place(fr, t_l2, W / 2 + 90, 320, s2, a2, rot=4)
            # ---- location (segment C)
            s, a = pop(t, seg_t[2][0] + 0.05, seg_t[2][1] - 0.05)
            if a:
                k = ease_out((t - seg_t[2][0]) / 0.35)
                place(fr, loc, 60 + loc.width / 2 - (1 - k) * 500, 240, 1, a)
                place(fr, flag_de, 60 + loc.width + 50 - (1 - k) * 500, 240, s, a)
            # ---- tahun depan chip (segment D, before cutaway)
            s, a = pop(t, t_tahun - 0.1, cut_in)
            place(fr, year, W / 2, 230, s, a)
            # ---- checklist (segment E)
            e_end = seg_t[4][1] - 0.05
            for lab, t0, cx, cy in (('Fokus', t_fokus, 260, 180), ('Business talk', t_bt, 720, 180),
                                    ('Persiapan', t_pers, 330, 330), ('Sabar', t_sabar, 770, 330)):
                s, a = pop(t, t0 - 0.05, e_end)
                place(fr, chk[lab], cx, cy, s, a)
            # ---- progress (segment F)
            f0, f1 = seg_t[5]
            s, a = pop(t, f0 + 0.03, f1 - 0.03)
            if a:
                p = ease_out((t - f0 - 0.15) / (f1 - f0 - 0.45))
                place(fr, progress_card(max(0, p)), W / 2, 250, s, a)
            # ---- tickets (segment G)
            g0, g1 = seg_t[6]
            s, a = pop(t, t_double - 0.1, g1 - 0.02, 0.34)
            s2, a2 = pop(t, t_double + 0.08, g1 - 0.02, 0.34)
            place(fr, tk1, W / 2 - 140, 330, s * 0.92, a, rot=7)
            place(fr, tk2, W / 2 + 130, 360, s2 * 0.92, a2, rot=-5)
            s3, a3 = pop(t, t_double + 0.25, g1 - 0.02, 0.3)
            place(fr, x2, W - 130, 520, s3, a3, rot=-10)
            # ---- watermark logo
            place(fr, wm, W - 110, H - 330, 1, 0.9)

        if main_part:
            # ---- captions: one word at a time
            for a0, a1, w in cap_win:
                if a0 <= t < a1:
                    k = (t - a0) / 0.09
                    sc = 0.82 + 0.18 * back_out(min(1, k)) if k < 1 else 1
                    place(fr, cap(w), W / 2, H * 0.875, sc, 1)
                    break
            # whip flash at segment cuts
            for o in offs[1:]:
                if abs(t - o) < 0.05:
                    fl = Image.new('RGBA', (W, H), (255, 255, 255, int(70 * (1 - abs(t - o) / 0.05))))
                    fr.alpha_composite(fl)

        # ---- outro
        if t >= base_dur:
            fr = outro_frame(t - base_dur, fi, logo_w)
        fr.save(os.path.join(fdir, f'f{fi:05d}.png'), compress_level=1)
        if fi % 60 == 0:
            print('frame', fi, '/', nfr, flush=True)

    pops = (0.12, 0.30, seg_t[2][0], t_tahun - 0.1, t_fokus, t_bt, t_pers, t_sabar, seg_t[5][0],
            t_double, t_double + 0.08)
    whooshes = ((cut_in - 0.12, 0.35, 0.18), (cut_out - 0.15, 0.35, 0.18), (base_dur - 0.15, 0.5, 0.22))
    write_sfx(total, pops, whooshes, os.path.join(OUT, 'sfx.wav'))
    final = os.path.join(OUT, 'PGLS_Norway_AzlanEza.mp4')
    composite(os.path.join(OUT, 'base.mov'), fdir, os.path.join(OUT, 'sfx.wav'), total, final)
    print('done', final)


if __name__ == '__main__':
    main()
