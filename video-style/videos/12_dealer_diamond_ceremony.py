#!/usr/bin/env python3
"""Video 12: one-day trip Kuching -> KL -> Diamond Recognition Ceremony (Public Gold) -> Kuching.
Handheld vlog footage, re-cut as a dealer-recruitment piece with urgency (user: "biar nampak professional,
masukkan unsur urgency supaya orang berminat nak jadi dealer Public Gold").

python3 videos/12_dealer_diamond_ceremony.py --preview         -> storyboard (safe zones drawn) + grade compare
python3 videos/12_dealer_diamond_ceremony.py --demo 0 20       -> 30 fps 720p motion demo of a time range
python3 videos/12_dealer_diamond_ceremony.py --words           -> word list for a spelling check
python3 videos/12_dealer_diamond_ceremony.py                   -> full render
"""
import importlib.util, json, math, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_VS = os.path.join(HERE, '..')
WORK = os.path.join(HERE, '..', '..', 'work', '12')   # raw footage + renders (not in git)
sys.path.insert(0, REPO_VS)
import numpy as np
import build as B
from build import (W, H, FPS, OUTRO, RED, F_XB, F_B, Image, ImageDraw, text_sprite, rounded, with_shadow, place,
                   pop, fit_pill, check_icon, pin_icon, ease_out, back_out, font, load_logos, outro_frame,
                   write_sfx, composite, syllables)


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REPO_VS, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V3 = _load('v3', 'videos/03_konsisten_emas.py')
V5 = _load('v5', 'videos/05_jangan_simpan_dalam_bank.py')
V6 = _load('v6', 'videos/06_kenapa_china_beli_emas.py')
shine, GOLD, GOLD_L = V3.shine, V3.GOLD, V3.GOLD_L
warn_icon, NAVY_C = V5.warn_icon, V5.NAVY_C
arrow_icon = V6.arrow_icon

RAW = os.environ.get('RAW', os.path.join(WORK, 'raw.mp4'))
OUT = os.environ.get('OUT', os.path.join(WORK, 'out'))
os.makedirs(OUT, exist_ok=True)
# Premium grade from video 3 (no face relight: the vlog shots change every few seconds).
GRADE = ("eq=brightness=-0.02:contrast=1.08:saturation=1.10:gamma=0.98,"
         "colorbalance=rs=0.02:bs=-0.03:rm=0.03:bm=-0.02:bh=0.02,"
         "curves=master='0/0 0.25/0.22 0.5/0.5 0.78/0.81 1/0.97'")
MENTOR_IMG = os.path.join(WORK, 'mentor.jpg')   # user photo: with our upline mentor (not in git)
MUSIC = os.environ.get('MUSIC', os.path.join(WORK, 'music.m4a'))
# 'Technological Documentary (Loop)' (approved on video 6), kept soft per user ("jangan terlalu kuat")
MUSIC_SS, MUSIC_DB, MUSIC_TEMPO = 0.0, -21.0, 1.0

# Descript SRT cues (source seconds). Spelling to be checked by the user where marked [?].
CUES = {
    1: (0.106, 0.826, "Kita nak buat apa?"),
    2: (1.146, 2.506, "Pergi KL."),
    3: (12.654, 14.734, "Okey dah sampai KL."),                       # [?] Descript: "Edward dah sampai KL"
    4: (19.426, 22.926, "Selalu kitorang melimpas dia selalu mesti ramai."),   # [?] melimpas
    5: (22.965, 24.026, "Tapi hari ni tak ramai."),
    6: (24.066, 27.665, "So kitorang nak try lah since breakfast dari pagi tadi lah."),
    7: (28.426, 29.105, "Dari terus tadi."),
    8: (29.305, 30.625, "So kitorang try."),
    9: (42.094, 43.094, "Little bit better than that."),
    10: (43.534, 45.354, "Get your clappers out."),
    11: (45.714, 47.014, "Kita warm up sedikit."),
    12: (47.434, 49.814, "Keluarkan clapper clapper anda."),
    14: (50.034, 52.614, "Welcome to Leadership and Achievers."),
    15: (57.038, 62.337, "Semulakan zaman ada pemimpin yang kita idamkan"),
    16: (68.214, 70.194, "Ya Allah, Ya Rahman Ya Rahim."),
    17: (70.934, 75.774, "Pada petang ini kami berhimpun di Diamond Recognition Ceremony."),
    18: (76.034, 79.434, "Triple Star Pearl, Dr Nor Shahirah."),
    19: (79.494, 82.274, "Triple Star Pearl for Nor Syafika."),
    20: (82.434, 87.994, "Triple Star Jade, Siti Zainakiah binti Zolambia."),
    21: (88.454, 94.654, "Untuk meraikan Four Star Ruby, Mr Steven Klonda Adaite."),
    22: (127.826, 132.766, "Alhamdulillah dah selesai Diamond Recognition Ceremony."),
    23: (133.526, 135.806, "So kami all dah on the way nak balik Kuching."),
    24: (144.046, 147.805, "Alhamdulillah, sekarang dah sampai Kuching."),
    25: (152.341, 155.762, "Such a long day sebab ni orang bangun pukul empat~2 pagi."),
    26: (156.142, 157.941, "Pergi matahari belum keluar."),
    27: (160.270, 161.110, "Tak boleh ikut."),                           # [?]
    28: (163.630, 164.269, "Hidup orang."),                             # [?]
    29: (165.750, 166.970, "Ini lah life busy bee oh."),
    30: (169.518, 170.818, "Sikitlah, setiap hari je betul."),          # [?]
    31: (172.118, 173.618, "And boleh je stay di KL."),
    32: (173.878, 174.898, "Kami je stay KL."),
    33: (174.938, 176.678, "Cuma bagi dua tek kenang Isya."),            # [?] unclear in Descript
    34: (178.018, 178.558, "Weekend kan?"),
    35: (178.598, 179.698, "Ni sok cuti dah."),
    36: (179.838, 180.378, "So sikitlah."),
    37: (181.198, 182.918, "Nak spend masa KL ke apa."),
    38: (182.958, 183.578, "Pulanglah."),
}
NO_CAPTION = {15, 18, 19, 20, 21}      # song lyric pill / rank cards instead of word captions
FLAG = {'okey', 'melimpas', 'tak', 'ikut', 'hidup', 'sikitlah', 'setiap', 'betul', 'tek', 'kenang', 'isya', 'bagi',
        'dua', 'cuma', 'sok', 'terus'}

# Edit list in output order: (src_in, src_out, kind, gain_db). Talk parts follow the cues (pauses cut);
# b-roll is trimmed to the strongest few seconds of each moment.
PLAN = [
    (120.30, 123.30, 'broll', -6),   # HOOK: confetti on the Diamond stage
    ('cue', 1, 2, 'talk', 0),        # "Kita nak buat apa? Pergi KL."
    (3.00, 5.40, 'broll', -12),      # wing (loud engine)
    (6.10, 8.30, 'broll', -12),      # couple on the plane
    ('cue', 3, 3, 'talk', 0),        # "...dah sampai KL"
    ('cue', 4, 8, 'talk', 0),        # breakfast talk
    (30.80, 33.70, 'broll', -4),     # entrance arch
    (35.40, 39.20, 'broll', -4),     # Eza in the hall
    ('cue', 9, 14, 'talk', 0),       # MC warm up
    ('cue', 15, 15, 'broll', -4),    # song
    ('cue', 16, 17, 'talk', 0),      # doa + Diamond Recognition Ceremony
    ('cue', 18, 21, 'talk', 0),      # achievers called up
    (95.50, 98.60, 'broll', -12),    # light show (loud)
    (100.20, 103.00, 'broll', -8),   # big screen
    (123.60, 127.60, 'broll', -6),   # celebration + award photo, under the upline-mentor photo card
    ('cue', 22, 23, 'talk', 0),      # selesai, on the way balik Kuching
    (136.40, 139.00, 'broll', -4),   # airport walk
    ('cue', 24, 24, 'talk', 0),      # sampai Kuching
    ('cue', 25, 38, 'talk', 0),      # long day / busy bee / pulanglah
    (184.10, 187.10, 'broll', -4),   # laugh + walk off
    (117.40, 122.60, 'broll', -14),  # CTA over the stage
]
CAPTIONS = False    # user (video 12): no subtitles
ZOOM_TALK = 1.07     # punch-in on every other talk segment


def build_segs():
    segs = []
    talk_i = 0
    for p in PLAN:
        if p[0] == 'cue':
            _, c0, c1, kind, g = p
            parts = []
            for n in sorted(CUES):
                if c0 <= n <= c1:
                    s, e, _ = CUES[n]
                    a, b = s - 0.12, e + 0.14
                    if parts and a - parts[-1][1] < 0.30:
                        parts[-1][1] = b
                    else:
                        parts.append([a, b])
            z = ZOOM_TALK if (kind == 'talk' and talk_i % 2) else 1.0
            talk_i += kind == 'talk'
            for a, b in parts:
                segs.append([a, b, kind, g, z])
        else:
            segs.append([p[0], p[1], p[2], p[3], 1.0])
    out = []
    for a, b, k, g, z in segs:
        a, b = round(max(0, a) * FPS) / FPS, round(b * FPS) / FPS
        out.append((a, b, k, g, z))
    return out


SEGS = build_segs()


def offsets():
    o, t = [], 0.0
    for s in SEGS:
        o.append(t)
        t += s[1] - s[0]
    return o, t


def src2out(x, after=0.0):
    offs, _ = offsets()
    for s, o in zip(SEGS, offs):
        if o + 1e-6 >= after and s[0] - 0.05 <= x <= s[1] + 0.05:
            return o + min(max(x, s[0]), s[1]) - s[0]
    return None


def out2src(t):
    offs, _ = offsets()
    for s, o in zip(SEGS, offs):
        if o <= t < o + (s[1] - s[0]):
            return s[0] + (t - o), s[4]
    return SEGS[-1][1], SEGS[-1][4]


def align_words():
    """Words spread inside each cue by syllable count, kept only where the cue survives the cut."""
    out = []
    for n, (s, e, text) in sorted(CUES.items()):
        if n in NO_CAPTION:
            continue
        toks, wts = [], []
        for raw in text.split():
            if '~' in raw:
                d, k = raw.split('~')
                toks.append(d.rstrip('.,?!')), wts.append(int(k.rstrip('.,?!')))
            else:
                t = raw.strip('.,?!')
                toks.append(t), wts.append(max(1, syllables(t)))
        cum = np.cumsum([0] + wts) / sum(wts) * (e - s)
        for i, t in enumerate(toks):
            out.append({'w': t, 'cue': n, 's': s + cum[i], 'e': s + cum[i + 1]})
    for w in out:
        w['os'] = src2out(w['s'], after=3.0)    # skip the hook copy of the stage shot
        w['oe'] = src2out(w['e'], after=3.0)
    return [w for w in out if w['os'] is not None and w['oe'] is not None]


VF = f"scale={W}:{H}:flags=lanczos,setsar=1"


def seg_vf(z):
    zf = '' if z == 1.0 else f",scale={int(W * z) // 2 * 2}:{int(H * z) // 2 * 2}:flags=lanczos,crop={W}:{H}"
    return f"[0:v]{VF}{zf},fps={FPS},{GRADE},unsharp=5:5:0.30,format=yuv420p"


def render_base():
    parts = []
    for i, (a, b, kind, g, z) in enumerate(SEGS):
        d = b - a
        p = os.path.join(OUT, f'seg{i:02d}.mov')
        n = int(round(d * FPS))
        af = (f"aresample=48000,volume={g}dB,apad,atrim=end_sample={int(round(n / FPS * 48000))},"
              f"afade=t=in:d=0.03,afade=t=out:st={d-0.03:.3f}:d=0.03")
        vf = seg_vf(z) + f",trim=end_frame={n},setpts=PTS-STARTPTS[v]"
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a}', '-t', f'{d + 0.3}', '-i', RAW,
                        '-filter_complex', vf + f";[0:a]{af}[au]", '-map', '[v]', '-map', '[au]',
                        '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', '-c:a', 'pcm_s16le',
                        '-ac', '2', '-video_track_timescale', '30000', p], check=True)
        parts.append(p)
    lst = os.path.join(OUT, 'list.txt')
    open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy',
                    os.path.join(OUT, 'base.mov')], check=True)


def base_still(t, graded=True):
    p = os.path.join(OUT, 'still.png')
    src, z = out2src(t)
    fc = (seg_vf(z) if graded else f"[0:v]{VF}") + "[v]"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{src}', '-i', RAW,
                    '-filter_complex', fc, '-map', '[v]', '-frames:v', '1', p], check=True)
    return Image.open(p).convert('RGBA')


# ---------------------------------------------------------------- graphics
def star_icon(s=60, col=GOLD):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    pts = []
    for i in range(10):
        r = s * (0.48 if i % 2 == 0 else 0.2)
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((s / 2 + r * math.cos(a), s / 2 + r * math.sin(a)))
    ImageDraw.Draw(im).polygon(pts, fill=col + (255,))
    return im


def plane_icon(s=60, col=(30, 110, 230)):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = col + (255,)
    d.polygon([(s * .08, s * .55), (s * .92, s * .3), (s * .98, s * .38), (s * .2, s * .68)], fill=c)
    d.polygon([(s * .45, s * .45), (s * .55, s * .1), (s * .66, s * .12), (s * .62, s * .42)], fill=c)
    d.polygon([(s * .4, s * .58), (s * .58, s * .9), (s * .68, s * .88), (s * .58, s * .52)], fill=c)
    return im.rotate(10, resample=Image.BICUBIC)


def clock_icon(s=58, col=RED, ang=0.0):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([3, 3, s - 3, s - 3], outline=col + (255,), width=6)
    c = s / 2
    d.line([c, c, c, c - s * 0.30], fill=col + (255,), width=5)
    d.line([c, c, c + s * 0.28 * math.sin(ang), c - s * 0.28 * math.cos(ang)], fill=col + (255,), width=4)
    return im


STOPS = ['KUCHING', 'KL', 'DIAMOND CEREMONY', 'KUCHING']


def tracker(active, p, w=820):
    """'Satu hari' journey tracker: four stops, the line fills up to the active stop (p = 0..1 to the next)."""
    h = 118
    im = rounded((w, h), 30, (16, 18, 34, 225))
    d = ImageDraw.Draw(im)
    xs = [70 + i * (w - 140) / 3 for i in range(4)]
    y = 44
    d.line([xs[0], y, xs[-1], y], fill=(80, 84, 110, 255), width=6)
    xe = xs[active] + (xs[min(3, active + 1)] - xs[active]) * p
    d.line([xs[0], y, xe, y], fill=GOLD + (255,), width=6)
    for i, x in enumerate(xs):
        on = i <= active
        r = 15 if i == active else 11
        d.ellipse([x - r, y - r, x + r, y + r], fill=(GOLD if on else (80, 84, 110)) + (255,),
                  outline=(255, 255, 255, 255) if i == active else None, width=4)
        f = font(F_XB if i == active else F_B, 25)
        d.text((x, y + 46), STOPS[i], font=f, fill=(255, 255, 255, 255) if on else (150, 152, 175, 255),
               anchor='mm')
    return with_shadow(im, 16, 8, 0.4)


def chip(text, col=RED, size=34):
    f = font(F_XB, size)
    tw = int(f.getlength(text))
    w, h = tw + 64, size + 34
    im = rounded((w, h), h // 2, col + (255,))
    ImageDraw.Draw(im).text((w / 2, h / 2), text, font=f, fill=(255, 255, 255, 255), anchor='mm')
    return with_shadow(im, 12, 6, 0.35)


def rank_card(rank, sub, w=800):
    im = rounded((w, 210), 40, (16, 18, 34, 240))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 18, 210], 9, fill=GOLD + (255,))
    d.text((60, 62), sub, font=font(F_B, 34), fill=(190, 192, 210, 255), anchor='lm')
    sz = 76
    while font(F_XB, sz).getlength(rank) > w - 200:
        sz -= 2
    d.text((58, 140), rank, font=font(F_XB, sz), fill=GOLD_L + (255,), anchor='lm')
    im.alpha_composite(star_icon(96), (w - 140, 58))
    return with_shadow(im, 20, 10, 0.45)


def slam_text(txt, size=104, maxw=780, red=False):
    if red:
        spr = text_sprite(txt, size, (255, 255, 255), (255, 255, 255), stroke=0)
        bg = rounded((spr.width + 10, spr.height - int(size * 0.3)), 24, RED + (255,))
        out = Image.new('RGBA', (bg.width, spr.height), (0, 0, 0, 0))
        out.alpha_composite(bg, (0, int(size * 0.15)))
        out.alpha_composite(spr, (5, 0))
        spr = with_shadow(out, 18, 8, 0.4)
    else:
        spr = text_sprite(txt, size, GOLD_L, GOLD, stroke=7, stroke_col=(40, 26, 8))
    if spr.width > maxw:
        spr = spr.resize((maxw, int(spr.height * maxw / spr.width)), Image.LANCZOS)
    return spr


def quote_pill(text, size=50):
    f = font(F_XB, size)
    tw = int(f.getlength(text))
    w, h = tw + 150, size + 70
    im = rounded((w, h), h // 2, (16, 18, 34, 238))
    d = ImageDraw.Draw(im)
    d.text((40, h / 2 + 8), '“', font=font(F_XB, size + 30), fill=GOLD + (255,), anchor='lm')
    d.text((100, h / 2), text, font=f, fill=GOLD_L + (255,), anchor='lm')
    spr = with_shadow(im, 18, 8, 0.4)
    if spr.width > 900:
        spr = spr.resize((900, int(spr.height * 900 / spr.width)), Image.LANCZOS)
    return spr


def route_pill(stops, size=40, bg=(16, 18, 34, 235), fg=(255, 255, 255, 255), icon=None):
    """Pill like 'KUCHING -> KL -> KUCHING' with drawn arrows (Poppins has no arrow glyph)."""
    f = font(F_XB, size)
    aw, gap = int(size * 0.9), int(size * 0.45)
    iw = icon.width + 18 if icon is not None else 0
    tw = sum(int(f.getlength(x)) for x in stops) + (len(stops) - 1) * (aw + 2 * gap)
    h = size + 40
    w = tw + 70 + iw
    im = rounded((w, h), h // 2, bg)
    d = ImageDraw.Draw(im)
    x = 35
    if icon is not None:
        im.alpha_composite(icon, (x, (h - icon.height) // 2))
        x += iw
    for i, st in enumerate(stops):
        d.text((x, h / 2), st, font=f, fill=fg, anchor='lm')
        x += int(f.getlength(st))
        if i < len(stops) - 1:
            x += gap
            y = h / 2
            lw = max(4, size // 9)
            d.line([x, y, x + aw - size * 0.3, y], fill=GOLD + (255,), width=lw)
            d.polygon([(x + aw, y), (x + aw - size * 0.38, y - size * 0.26), (x + aw - size * 0.38, y + size * 0.26)],
                      fill=GOLD + (255,))
            x += aw + gap
    return with_shadow(im, 16, 8, 0.35)


def quote_card(lines, size=52, w=860):
    lh = int(size * 1.3)
    h = 60 + lh * len(lines)
    im = rounded((w, h), 40, (16, 18, 34, 238))
    d = ImageDraw.Draw(im)
    d.text((34, 52), '\u201c', font=font(F_XB, size + 40), fill=GOLD + (255,), anchor='lm')
    for i, ln in enumerate(lines):
        d.text((w / 2 + 20, 30 + lh * (i + 0.5)), ln, font=font(F_XB, size), fill=GOLD_L + (255,), anchor='mm')
    return with_shadow(im, 18, 8, 0.4)


def mentor_card(w=720):
    im = Image.open(MENTOR_IMG).convert('RGB')
    iw, ih = im.size
    im = im.crop((0, int(ih * 0.075), iw, int(ih * 0.86)))      # drop the empty floor
    h = int(w * im.height / im.width)
    im = im.resize((w, h), Image.LANCZOS).convert('RGBA')
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 28, fill=255)
    im.putalpha(m)
    frame = rounded((w + 28, h + 28), 38, (255, 255, 255, 255))
    frame.alpha_composite(im, (14, 14))
    return frame


def mentor_name_card(w=760):
    im = rounded((w, 190), 40, (16, 18, 34, 240))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 18, 190], 9, fill=GOLD + (255,))
    d.text((52, 62), 'Dr Syafiq Roslan & isteri', font=font(F_XB, 52), fill=(255, 255, 255, 255), anchor='lm')
    d.text((54, 134), 'Upline mentor kami  \u2022  5 Star Diamond', font=font(F_B, 36), fill=GOLD_L + (255,),
           anchor='lm')
    return with_shadow(im, 20, 10, 0.45)


def write_word_list(words):
    lines = ['VIDEO 12 - Diamond Recognition Ceremony (vlog sehari)',
             'Tanda [?] = sila semak ejaan / bunyi. Masa = kedudukan dalam video siap.', '']
    cur = None
    for w in words:
        if w['cue'] != cur:
            cur = w['cue']
            mm, ss = divmod(w['os'], 60)
            lines += ['', f"[{int(mm)}:{ss:04.1f}]  {re.sub(r'~\d+', '', CUES[cur][2])}"]
        mark = '  [?]' if w['w'].lower() in FLAG else ''
        mm, ss = divmod(w['os'], 60)
        lines.append(f"    {int(mm)}:{ss:04.1f}  {w['w']}{mark}")
    p = os.path.join(WORK, 'SEMAK_EJAAN_video12.txt')
    open(p, 'w').write('\n'.join(lines) + '\n')
    return p


def main():
    preview = '--preview' in sys.argv
    words = align_words()
    offs, base_dur = offsets()
    total = base_dur + OUTRO
    if '--words' in sys.argv:
        print(write_word_list(words))
        return
    if not preview and '--skip-base' not in sys.argv and not os.path.exists(os.path.join(OUT, 'base.mov')) \
            or '--rebase' in sys.argv:
        render_base()

    def ct(n, end=False):
        s, e, _ = CUES[n]
        return src2out(e if end else s, after=3.0)

    def wt(word, nth=1):
        k = 0
        for w in words:
            if w['w'].lower() == word.lower():
                k += 1
                if k == nth:
                    return w['os']
        raise KeyError(word)

    gold_words = {'kl', 'kuching', 'diamond', 'recognition', 'ceremony', 'achievers', 'leadership', 'empat',
                  'pagi', 'busy', 'bee', 'alhamdulillah'}
    keep_case = {'KL', 'Kuching', 'Diamond', 'Recognition', 'Ceremony', 'Leadership', 'Achievers', 'Allah',
                 'Rahman', 'Rahim', 'Ya', 'Alhamdulillah', 'Isya'}
    cap_cache = {}

    def cap(word):
        if word not in cap_cache:
            disp = word if word in keep_case else word.lower()
            sz = 100
            while font(F_XB, sz).getlength(disp) > 860:
                sz -= 4
            top, bot = (GOLD_L, GOLD) if word.lower() in gold_words else ((255, 255, 255), (247, 228, 160))
            cap_cache[word] = text_sprite(disp, sz, top, bot, stroke=5, stroke_col=(25, 18, 20))
        return cap_cache[word]
    cap_win = []
    for i, w in enumerate(words):
        nxt = words[i + 1]['os'] if i + 1 < len(words) else w['oe'] + 0.3
        cap_win.append((w['os'], nxt if nxt - w['oe'] < 0.35 else w['oe'] + 0.15, w['w']))

    # cuts where the scene changes (b-roll in/out): faint flash + soft whoosh
    jumps = [o for s0, s1, o in zip(SEGS, SEGS[1:], offs[1:]) if abs(s1[0] - s0[1]) > 1.0]

    CX = B.TT_CENTER_X
    cta_t = offs[-1]
    hook_e = offs[1]
    # hook
    h1 = text_sprite('SEHARI', 150, RED, RED, stroke=9, stroke_col=(255, 255, 255))
    h2 = text_sprite('KE PENTAS DIAMOND', 92, (255, 255, 255), GOLD_L, stroke=7, stroke_col=(30, 22, 10))
    h_chip = route_pill(['KUCHING', 'KL', 'KUCHING'], 38)
    # story
    p_kl = route_pill(['Kuching', 'KL'], 52, bg=(255, 255, 255, 245), fg=(20, 20, 30, 255), icon=plane_icon(60))
    p_sampai = fit_pill('Sampai KL', icon=pin_icon(56), size=56)
    p_event = fit_pill('Diamond Recognition Ceremony', icon=star_icon(56, (255, 255, 255)), size=46, bg=(232, 190, 92, 255))
    p_lead = fit_pill('Leadership & Achievers', icon=star_icon(56), size=52)
    q_song = quote_card(['Semulakan zaman ada', 'pemimpin yang kita idamkan'], 50)
    s_diamond = slam_text('DIAMOND RECOGNITION', 96)
    p_selesai = fit_pill('Majlis selesai', icon=check_icon(56), size=54)
    p_balik = fit_pill('On the way balik Kuching', icon=plane_icon(60), size=50)
    p_kch = fit_pill('Sampai Kuching', icon=pin_icon(56), size=56)
    # CTA (urgency) - wording from the user
    c1 = text_sprite('ANDA MUNGKIN AKAN JADI', 60, (255, 255, 255), (255, 255, 255), stroke=6, stroke_col=(20, 16, 24))
    c2 = slam_text('DIAMOND', 170, maxw=760)
    c2b = slam_text('SETERUSNYA', 112, maxw=700)
    c3 = fit_pill('Berminat nak explore bisnes Public Gold?', icon=star_icon(60, (255, 255, 255)), size=46, bg=(232, 190, 92, 255))
    c4 = fit_pill('Isi form di bawah', icon=arrow_icon(64, False, (110, 12, 26)), size=60, bg=RED + (255,))
    m_card = mentor_card()
    m_pill = mentor_name_card()
    m_chip = chip('5 STAR DIAMOND', RED, 34)
    logo_c, logo_w = load_logos()
    wm = logo_w.resize((150, int(150 * logo_w.height / logo_w.width)), Image.LANCZOS)

    T = {'kl': ct(2), 'sampai': ct(3), 'bfast': wt('breakfast'), 'arch': offs[[i for i, s in enumerate(SEGS)
                                                                               if s[0] == 30.8][0]],
         'mc': ct(9), 'lead': wt('Leadership'), 'song': ct(15), 'doa': ct(16), 'diamond': wt('Diamond'),
         'r1': ct(18), 'r2': ct(20), 'r3': ct(21), 'r_end': ct(21, True),
         'selesai': ct(22), 'balik': ct(23), 'kch': ct(24), 'empat': wt('empat'), 'bee': ct(29),
         'end29': ct(29, True)}
    i_light = [i for i, s in enumerate(SEGS) if s[0] == 95.5][0]
    T['light'] = offs[i_light]
    T['light_e'] = offs[i_light + 2]
    i_m = [i for i, s_ in enumerate(SEGS) if s_[0] == 123.6][0]
    T['mentor'], T['mentor_e'] = offs[i_m], offs[i_m + 1]
    # tracker stops: 0 Kuching .. 3 Kuching (out times)
    trk = [(hook_e, T['sampai'], 0), (T['sampai'], T['arch'], 1), (T['arch'], T['balik'], 2),
           (T['balik'], T['kch'], 2.5), (T['kch'], cta_t, 3)]
    pops = [T[k] for k in ('kl', 'sampai', 'arch', 'lead', 'song', 'selesai',
                           'balik', 'kch', 'mentor')] + [cta_t + 1.2, cta_t + 2.0]
    whooshes = [(0.0, 0.4, 0.24), (hook_e - 0.15, 0.35, 0.2), (T['diamond'] - 0.15, 0.35, 0.2),
                (T['light'] - 0.1, 0.4, 0.24), (cta_t - 0.15, 0.45, 0.24)] + \
               [(j - 0.12, 0.3, 0.12) for j in jumps] + [(base_dur - 0.15, 0.5, 0.22)]

    t = 0.0

    def show(fr, spr, cx, cy, t0, t1, rot=0):
        s, a = pop(t, t0, t1)
        place(fr, spr, cx, cy, s, a, rot=rot)

    def slam(fr, spr, cx, cy, t0, t1, rot=-3):
        s, a = pop(t, t0, t1)
        k = 1 + 0.25 * max(0, 1 - (t - t0) / 0.16)
        place(fr, spr, cx, cy, s * k if s >= 1 else s, a, rot=rot)

    def overlay(tt):
        nonlocal t
        t = tt
        fr = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        if t >= base_dur:
            return outro_frame(t - base_dur, int(t * FPS), logo_w), False
        # HOOK over the confetti stage
        if t < hook_e:
            show(fr, h1, CX - 40, 300, 0.03, hook_e, rot=-4)
            show(fr, h2, CX + 10, 440, 0.25, hook_e, rot=-4)
            show(fr, h_chip, CX, 560, 0.7, hook_e)
        # journey tracker (top band)
        if hook_e <= t < cta_t and not (T['mentor'] <= t < T['mentor_e']):
            for a, b, st in trk:
                if a <= t < b:
                    act = int(st)
                    p = (st - act) if st != int(st) else min(1, (t - a) / max(0.1, b - a)) * 0.0
                    spr = tracker(act, p)
                    k = ease_out(min(1, (t - hook_e) / 0.35))
                    kout = ease_out(min(1, (cta_t - t) / 0.3))
                    place(fr, spr, CX, 225 - (1 - k) * 60, 1, min(k, kout))
                    break
        show(fr, p_kl, CX, 400, T['kl'], T['sampai'] - 0.1)
        show(fr, p_sampai, CX, 400, T['sampai'], ct(3, True) + 0.3)
        show(fr, p_event, CX, 400, T['arch'] + 0.2, T['mc'] - 0.1)
        show(fr, p_lead, CX, 400, T['lead'] - 0.1, ct(14, True) + 0.3)
        show(fr, q_song, CX, 420, T['song'] + 0.2, ct(15, True))
        slam(fr, s_diamond, CX, 420, T['diamond'] - 0.05, T['r1'] - 0.05)
        # upline mentor photo card (dim footage, slow push-in, gold shine)
        if T['mentor'] <= t < T['mentor_e']:
            tm = t - T['mentor']
            dm = T['mentor_e'] - T['mentor']
            fr.alpha_composite(Image.new('RGBA', (W, H), (8, 8, 16, int(140 * min(1, tm / 0.3, (dm - tm) / 0.2)))))
            s_, a_ = pop(t, T['mentor'] + 0.1, T['mentor_e'], dur_in=0.4)
            card = shine(m_card, (tm - 1.0) / 1.2)
            place(fr, card, CX, 700, s_ * (1 + 0.035 * tm / dm), a_, rot=-2)
            show(fr, m_chip, CX - 190, 310, T['mentor'] + 0.6, T['mentor_e'], rot=-4)
            show(fr, m_pill, CX, 1205, T['mentor'] + 0.9, T['mentor_e'])
        show(fr, p_selesai, CX, 400, T['selesai'] + 0.3, T['balik'] - 0.05)
        show(fr, p_balik, CX, 400, T['balik'], ct(23, True) + 0.3)
        show(fr, p_kch, CX, 400, T['kch'], ct(24, True) + 0.3)
        # CTA (urgency)
        if t >= cta_t:
            tc = t - cta_t
            dim = Image.new('RGBA', (W, H), (8, 8, 16, int(150 * ease_out(min(1, tc / 0.5)))))
            fr.alpha_composite(dim)
            show(fr, c1, CX, 555, cta_t + 0.25, base_dur)
            slam(fr, c2, CX, 700, cta_t + 0.6, base_dur)
            slam(fr, c2b, CX + 20, 830, cta_t + 0.85, base_dur)
            show(fr, c3, CX, 990, cta_t + 1.2, base_dur)
            bob = 14 * abs(math.sin(max(0, tc - 2.3) * 2 * math.pi / 0.9))     # arrow pill nudges down
            show(fr, c4, CX, 1150 + bob, cta_t + 2.0, base_dur)
        # captions
        for w0, w1, w in (cap_win if CAPTIONS else []):
            if w0 <= t < w1:
                k = min(1, (t - w0) / 0.12)
                place(fr, cap(w), CX, B.TT_CAPTION_Y, 0.85 + 0.15 * back_out(k), min(1, k * 2))
                break
        # watermark (left side, clear of the action rail)
        if hook_e <= t < cta_t and not (T['mentor'] <= t < T['mentor_e']):
            place(fr, wm, 95, 1010, 1, 0.9)
        for j in jumps:
            if j <= t < j + 0.14:
                fl = Image.new('RGBA', (W, H), (255, 255, 255, int(90 * (1 - (t - j) / 0.14))))
                fr = Image.alpha_composite(fl, fr)
        return fr, True

    if '--audio-preview' in sys.argv:
        write_sfx(total, pops, whooshes, os.path.join(OUT, 'sfx.wav'))
        fc = '[0:a]apad[v0];' + B.audio_mix_graph('[v0]', '[1:a]', total, '[2:a]', MUSIC_SS, MUSIC_DB,
                                                   outro_at=base_dur, music_tempo=MUSIC_TEMPO)
        outp = os.path.join(WORK, 'PREVIEW_audio_music.m4a')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(OUT, 'base.mov'),
                        '-i', os.path.join(OUT, 'sfx.wav'), '-i', MUSIC, '-filter_complex', fc, '-map', '[a]',
                        '-t', f'{total}', '-c:a', 'aac', '-b:a', '160k', outp], check=True)
        print('audio preview', outp)
        return

    if '--demo' in sys.argv:
        i = sys.argv.index('--demo')
        d0, d1 = float(sys.argv[i + 1]), float(sys.argv[i + 2])
        ddir = os.path.join(OUT, 'demo')
        os.makedirs(ddir, exist_ok=True)
        for f in os.listdir(ddir):
            os.remove(os.path.join(ddir, f))
        write_sfx(total, pops, whooshes, os.path.join(OUT, 'sfx.wav'))
        for k in range(int((d1 - d0) * FPS)):
            ov, _ = overlay(d0 + k / FPS)
            ov.resize((720, 1280), Image.LANCZOS).save(os.path.join(ddir, f'c{k:05d}.png'), compress_level=1)
        base = os.path.join(OUT, 'base.mov')
        dst = os.path.join(WORK, f'PREVIEW_demo_{int(d0)}_{int(d1)}.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{d0}', '-t', f'{d1 - d0}', '-i', base,
                        '-framerate', f'{FPS}', '-i', os.path.join(ddir, 'c%05d.png'),
                        '-ss', f'{d0}', '-t', f'{d1 - d0}', '-i', os.path.join(OUT, 'sfx.wav'),
                        '-filter_complex', '[0:v]tpad=stop_mode=clone:stop_duration=4,scale=720:1280[b];'
                        '[b][1:v]overlay=0:0:shortest=1,format=yuv420p[v];'
                        '[0:a][2:a]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14[a]',
                        '-map', '[v]', '-map', '[a]', '-t', f'{d1 - d0}', '-r', str(FPS),
                        '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-c:a', 'aac', '-b:a', '160k',
                        '-movflags', '+faststart', dst], check=True)
        print('demo', dst)
        return

    if preview:
        shots = [('Hook', 1.6), ('Pergi KL', T['kl'] + 0.4), ('Sampai KL', T['sampai'] + 0.6),
                 ('Breakfast', T['bfast'] + 0.6), ('Majlis', T['arch'] + 1.0), ('MC', T['lead'] + 0.4),
                 ('Lagu', T['song'] + 1.2), ('Diamond', T['diamond'] + 0.6), ('Pearl', T['r1'] + 1.0),
                 ('Jade', T['r2'] + 1.0), ('Ruby', T['r3'] + 1.5), ('Light show', T['light'] + 2.0), ('Mentor', T['mentor'] + 2.4),
                 ('Selesai', T['selesai'] + 1.0), ('Balik', T['balik'] + 0.6), ('Kuching', T['kch'] + 1.0),
                 ('4 pagi', T['empat'] + 0.5), ('Busy bee', T['bee'] + 0.6), ('CTA', base_dur - 0.6),
                 ('Outro', base_dur + 1.6)]
        tiles_ = []
        sx = 360 / 1080
        for label, tt in shots:
            ov, has_base = overlay(tt)
            fr = base_still(tt) if has_base else Image.new('RGBA', (W, H), (0, 0, 0, 255))
            fr.alpha_composite(ov)
            tile = fr.resize((360, 640), Image.LANCZOS)
            g = Image.new('RGBA', tile.size, (0, 0, 0, 0))
            gd = ImageDraw.Draw(g)
            for z in ((0, 0, 1080, B.TT_TOP), (0, B.TT_BOTTOM, 1080, 1920),
                      (B.TT_RIGHT, B.TT_RAIL_Y[0], 1080, B.TT_RAIL_Y[1])):
                gd.rectangle([v * sx for v in z], fill=(255, 0, 60, 60), outline=(255, 0, 60, 200), width=2)
            tile.alpha_composite(g)
            mm, ss = divmod(tt, 60)
            t2_ = Image.new('RGB', (360, 684), (24, 24, 30))
            t2_.paste(tile.convert('RGB'), (0, 0))
            ImageDraw.Draw(t2_).text((6, 662), f'{int(mm)}:{ss:04.1f}  {label}', font=font(F_B, 21),
                                     fill=(255, 255, 255), anchor='lm')
            tiles_.append(t2_)
        cols = 10
        rows = math.ceil(len(tiles_) / cols)
        sheet = Image.new('RGB', (cols * 372 + 12, rows * 696 + 12), (24, 24, 30))
        for i, tl in enumerate(tiles_):
            sheet.paste(tl, (12 + (i % cols) * 372, 12 + (i // cols) * 696))
        sheet.save(os.path.join(WORK, 'PREVIEW_storyboard.jpg'), quality=86)
        cmp_ = Image.new('RGB', (3 * 1100 + 20, 1000), (24, 24, 30))
        d = ImageDraw.Draw(cmp_)
        for i, tt in enumerate((T['bfast'], T['r2'], T['bee'])):
            for j, gr in enumerate((False, True)):
                im = base_still(tt, gr).resize((540, 960), Image.LANCZOS).convert('RGB')
                cmp_.paste(im, (20 + i * 1100 + j * 545, 36))
                d.text((20 + i * 1100 + j * 545, 18), 'Asal' if not gr else 'Grade', font=font(F_B, 26),
                       fill=(255, 255, 255) if not gr else GOLD_L, anchor='lm')
        cmp_.save(os.path.join(WORK, 'PREVIEW_colorgrade.jpg'), quality=86)
        print('preview ok; segments', len(SEGS), 'base', round(base_dur, 2), 'total', round(total, 2))
        return

    fdir = os.path.join(OUT, 'frames')
    os.makedirs(fdir, exist_ok=True)
    for fi in range(int(round(total * FPS))):
        ov, _ = overlay(fi / FPS)
        ov.save(os.path.join(fdir, f'f{fi:05d}.png'), compress_level=1)
    write_sfx(total, pops, whooshes, os.path.join(OUT, 'sfx.wav'))
    final = os.path.join(OUT, 'DealerDiamond_AzlanEza.mp4')
    composite(os.path.join(OUT, 'base.mov'), fdir, os.path.join(OUT, 'sfx.wav'), total, final,
              music=MUSIC if os.path.exists(MUSIC) else None, music_ss=MUSIC_SS, music_db=MUSIC_DB,
              music_tempo=MUSIC_TEMPO)
    print('done', final)


if __name__ == '__main__':
    main()
