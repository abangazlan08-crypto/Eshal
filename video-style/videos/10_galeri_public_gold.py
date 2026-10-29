#!/usr/bin/env python3
"""Video 10: walking tour of Galeri Public Gold (Menara Public Gold, KL), Bahasa Sarawak, Azlan & Eza style.
Handheld vertical phone footage. Fujifilm-style soft grade (low contrast, slightly brighter, NO vignette), no zoom.

python3 build_v10.py --preview         -> storyboard stills (with TikTok safe-zone guides) + grade comparison
python3 build_v10.py --audio-preview   -> voice + sfx + music mix only
python3 build_v10.py --words           -> word-by-word spelling list for the user to check
python3 build_v10.py                   -> full render
"""
import importlib.util, json, math, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_VS = os.path.join(HERE, '..')
WORK = os.path.join(HERE, '..', 'work', 'v10')   # raw footage, licensed music (not in git)
ASSETS = os.path.join(HERE, '10_assets')
sys.path.insert(0, REPO_VS)
import numpy as np
import build as B
from build import (W, H, FPS, OUTRO, RED, F_XB, F_B, Image, ImageDraw, text_sprite, rounded, with_shadow, place,
                   pop, fit_pill, check_icon, pin_icon, ease_out, back_out, font, load_logos, outro_frame, write_sfx,
                   composite, syllables)


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REPO_VS, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V3 = _load('v3', 'videos/03_konsisten_emas.py')
V5 = _load('v5', 'videos/05_jangan_simpan_dalam_bank.py')
V6 = _load('v6', 'videos/06_kenapa_china_beli_emas.py')
shine, badge, GOLD, GOLD_L = V3.shine, V3.badge, V3.GOLD, V3.GOLD_L
warn_icon, NAVY_C = V5.warn_icon, V5.NAVY_C
arrow_icon = V6.arrow_icon

RAW = os.environ.get('RAW', os.path.join(WORK, 'raw.mp4'))
OUT = os.environ.get('OUT', os.path.join(WORK, 'out'))
# Fujifilm-like tone (user: not too much contrast, a bit brighter, no vignette): lifted blacks, soft highlight
# roll-off, slightly muted saturation, teal-cyan shadows, warm mids.
GRADE = ("eq=brightness=0.03:contrast=0.94:saturation=0.90:gamma=1.03,"
         "curves=r='0/0.035 0.25/0.24 0.5/0.52 0.8/0.81 1/0.97':g='0/0.04 0.25/0.25 0.5/0.51 0.8/0.80 1/0.965':"
         "b='0/0.06 0.25/0.26 0.5/0.49 0.8/0.77 1/0.93',"
         "colorbalance=rs=-0.03:gs=0.005:bs=0.025:rm=0.015:gm=0.005:bm=-0.02:rh=0.01:bh=-0.015,hue=s=0.97")
# Music: video 4's approved acoustic track ("Positive Hopeful Acoustic Guitar Live Strum"), crossfaded to length.
MUSIC = os.path.join(WORK, 'music.m4a')
MUSIC_SS, MUSIC_DB, MUSIC_TEMPO = 0.0, -17.0, 1.0
CAPTIONS = False    # user (video 10): no subtitles for this video
os.makedirs(OUT, exist_ok=True)

# Descript SRT cues (numbered as in transcript.srt), spelled by sound (Bahasa Sarawak).
# Dropped (fillers / repeats / unfinished): 2 8 20 28 34 38 39 40 41 43 46 47 51 52 60 61 64 66 69 71 72 75 78.
CUES = {
    1: (2.514, 5.874, "Mun dia pikir-pikir balik nak, scammer pun bukan nunjuk nyampunoh."),
    3: (7.334, 12.414, "So, sebenarnya tok lah founder Public Gold ok?"),
    4: (12.814, 14.314, "Dato' Seri Louis Ng."),
    5: (14.613, 20.714, "Jadi kita boleh nampak, ok Public Gold sebenarnya dekat kami sebenarnya di Menara"),
    6: (20.774, 22.194, "Public Gold di Jalan Tuanku Abdul Razak."),
    7: (22.234, 25.014, "So kami di Galeri Public Gold."),
    9: (26.754, 31.954, "So, mun kita ingin nak nangga Public Gold tok macam ni, kita boleh pergi"),
    10: (32.014, 34.934, "ke tingkat empat Galeri Public Gold."),
    11: (35.014, 38.954, "So kita boleh tengoklah, ok history Public Gold ok."),
    12: (39.534, 43.734, "So Public Gold tok dah bertapak di Malaysia since 2008~4."),
    13: (44.214, 48.974, "Ok, so kita boleh tengoklah journey Public Gold memang ditunjukkan di situ."),
    14: (49.414, 55.074, "Haa jadi boleh nampak macam ni, growth Public Gold."),
    15: (56.314, 60.294, "Public Gold adalah syarikat jual beli emas yang terbesar, jual beli emas"),
    16: (60.314, 62.514, "dan perak yang terbesar di Malaysia."),
    17: (63.894, 68.574, "Dan yang bestnya kita boleh nampak perkembangan Public Gold dari zero."),
    18: (68.814, 76.014, "Haa so di situ ok, haa kita nampak si yang besar tok."),
    19: (76.814, 78.374, "Jom dekat-dekat rapat-rapat."),
    21: (81.074, 85.614, "So tok adalah Public Gold Refinery Factory."),
    22: (86.174, 87.034, "Maksudnya apa?"),
    23: (87.514, 93.874, "Kilang ok kilang penulenan emas yang ada di Batu Kawan, Penang."),
    24: (95.714, 102.334, "Dan untuk pengetahuan, gold refinery tok adalah yang pertama di Malaysia."),
    25: (103.054, 107.014, "Ok tengok betapa kukuhnya Public Gold."),
    26: (108.594, 109.694, "So kita boleh tengok."),
    27: (111.294, 111.594, "Jom!"),
    29: (123.926, 127.026, "So, tok adalah Public Gold Global Footprint."),
    30: (127.106, 127.625, "Haa nangga."),
    31: (128.145, 130.186, "Many region, one legacy."),
    32: (130.946, 134.406, "Ah so kita dapat nangga lah future Public Gold macam ni."),
    33: (137.026, 142.026, "So boleh lihat awards-awards yang Public Gold dapat."),
    35: (142.506, 143.526, "Haa so boleh nangga lah."),
    36: (144.206, 149.466, "Public Gold dah dapat National Record, The Malaysia Book of Record, The"),
    37: (149.666, 153.326, "Biggest Gold Bar pada 28~4 Mac 2026~6."),
    42: (164.642, 166.462, "Ok jom kita bawak ngembak lagi."),
    44: (172.002, 172.802, "So boleh nampak?"),
    45: (174.322, 177.402, "Yang berminat untuk travel VVIP~4 Trip."),
    48: (182.600, 184.281, "Tok adalah Leadership Seminar"),
    49: (184.341, 189.162, "yang maksudnya trip yang bakal dipergi oleh para-para achievers."),
    50: (189.602, 194.142, "Ok, para-para ni let say yang, yang capai a certain target lah."),
    53: (196.902, 201.762, "So yang bestnya salah satu kelebihan yang actually ada banyak sebenarnya"),
    54: (201.822, 203.082, "kelebihan bila jadi dealer."),
    55: (203.442, 207.642, "Ok salah satunya adalah kita boleh pergi ke VVIP~4 Trip yang"),
    56: (207.682, 210.482, "disponsor sepenuhnya oleh Public Gold."),
    57: (210.562, 211.922, "So boleh nampak galeri lagi."),
    58: (215.314, 216.994, "So, jom!"),
    59: (223.510, 226.800, "So tok antara insan-insan top-top"),
    62: (230.510, 231.490, "Jom kami mengembara kita."),
    63: (231.770, 235.370, "So, haa mesti kita mahu tahu nak siapa guru kami orang."),
    65: (235.890, 241.250, "So guru kami orang adalah Million Star Triple Diamond."),
    67: (242.390, 246.290, "Haa jadi mungkin kita mahu tahu, tok adalah guru kami."),
    68: (246.550, 248.890, "Haa guru kami orang ke guru kami dengan suami."),
    70: (250.190, 251.730, "Founder G100~3."),
    73: (257.089, 261.029, "Dan tok adalah gambar Mahaguru Emas Malaysia okey."),
    74: (262.950, 265.570, "Tuan Cikgu Hashim serta isteri."),
    76: (267.270, 271.390, "Dan mungkin kita jadi sekiranya kita berminat untuk menjadi dealer,"),
    77: (271.610, 273.130, "mungkin kita join lah team kami orang."),
}
# Repeated words / false starts cut from inside kept cues (source seconds).
CUTS = [(180.10, 182.60),     # "tok adalah Leadership Seminar ach, err," (retake follows)
        (204.56, 205.62),     # first "kita boleh," (said twice)
        (226.80, 227.45),     # trailing "err..."
        (261.30, 262.95)]     # "Err Cikgu Ha-, apa" before "Tuan Cikgu Hashim"
# Words to flag for the user's spelling check (unclear sound / names / Sarawak words).
FLAG = {'nyampunoh', 'ngembak', 'mengembara', 'nunjuk', 'si', 'hundred', 'g', 'triple', 'cikgu', 'hashim',
        'dipergi', 'kilang'}
B.SYL.update({'pikir-pikir': 4, 'nyampunoh': 3, 'Public': 2, 'Gold': 1, "Dato'": 2, 'Seri': 2, 'Louis': 2,
              'Ng': 1, 'Tuanku': 3, 'Abdul': 2, 'Razak': 2, 'history': 3, 'since': 1, 'journey': 2, 'growth': 1,
              'bestnya': 2, 'zero': 2, 'dekat-dekat': 4, 'rapat-rapat': 4, 'Refinery': 4, 'Factory': 3,
              'refinery': 4, 'gold': 1, 'Global': 2, 'Footprint': 2, 'Many': 2, 'region': 2, 'one': 1,
              'legacy': 3, 'future': 2, 'awards-awards': 4, 'National': 3, 'Record': 2, 'The': 1, 'Book': 1,
              'of': 1, 'Biggest': 2, 'Bar': 1, 'travel': 2, 'Trip': 1, 'trip': 1, 'Leadership': 3,
              'Seminar': 3, 'achievers': 3, 'para-para': 4, 'let': 1, 'say': 1, 'a': 1, 'certain': 2,
              'target': 2, 'actually': 4, 'dealer': 2, 'top-top': 2, 'insan-insan': 4, 'Million': 2,
              'Star': 1, 'Triple': 2, 'Diamond': 2, 'Founder': 2, 'founder': 2, 'G': 1, 'Hundred': 2,
              'join': 1, 'team': 1, 'okey': 2, 'ok': 2, 'So': 1, 'tengoklah': 3, 'Penang': 2})


def build_segs():
    regs = json.load(open(os.path.join(ASSETS, 'edl_all.json')))['regs']
    keep = []
    for s, e, _ in CUES.values():
        for a, b in regs:
            a2, b2 = max(a - 0.08, s - 0.12), min(b + 0.10, e + 0.12)
            if b2 - a2 > 0.12:
                keep.append([a2, b2])
    for c0, c1 in CUTS:
        nk = []
        for a, b in keep:
            if b <= c0 or a >= c1:
                nk.append([a, b])
            else:
                if a < c0 - 0.05:
                    nk.append([a, c0])
                if b > c1 + 0.05:
                    nk.append([c1, b])
        keep = nk
    segs = []
    for a, b in sorted(keep):
        if segs and a - segs[-1][1] < 0.18:
            segs[-1][1] = max(segs[-1][1], b)
        else:
            segs.append([a, b])
    # snap cut points to the frame grid so every segment has exactly as much video as audio
    # (otherwise each cut adds a fraction of a frame and the picture drifts behind the voice)
    segs = [(round(a * FPS) / FPS, round(b * FPS) / FPS) for a, b in segs]
    return [s for s in segs if s[1] > s[0]], [1.0] * len(segs)    # no zoom


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


def in_segs(x):
    return any(a <= x <= b for a, b in SEGS)


def align_words():
    regs = json.load(open(os.path.join(ASSETS, 'edl_all.json')))['regs']
    out = []
    for n, (s, e, text) in sorted(CUES.items()):
        toks, wts = [], []
        for raw in text.split():
            if '~' in raw:
                d, k = raw.split('~')
                toks.append(d.rstrip('.,?!')), wts.append(int(k.rstrip('.,?!')))
            else:
                t = raw.strip('.,?!')
                toks.append(t), wts.append(syllables(t))
        # speech inside this cue that survives the cut list
        rr = []
        for a, b in regs:
            a2, b2 = max(a, s - 0.05), min(b, e + 0.05)
            if b2 - a2 > 0.03:
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
            out.append({'w': t, 'cue': n, 's': sp2t(cum[i] + 1e-4), 'e': sp2t(cum[i + 1])})
    for w in out:
        w['os'], w['oe'] = src2out(w['s']), src2out(w['e'])
    return [w for w in out if w['os'] is not None]


VF = f"scale={W}:{H}:flags=lanczos,setsar=1"


def graded_filter():
    return f"[0:v]{VF},fps={FPS},{GRADE},unsharp=5:5:0.30,format=yuv420p[v]"


def render_base():
    parts = []
    for i, (a, b) in enumerate(SEGS):
        d = b - a
        p = os.path.join(OUT, f'seg{i}.mov')
        n = int(round(d * FPS))        # exact frame count; audio trimmed/padded to the same length
        af = (f"aresample=48000,apad,atrim=end_sample={int(round(n / FPS * 48000))},"
              f"afade=t=in:d=0.03,afade=t=out:st={d-0.03:.3f}:d=0.03")
        vf = graded_filter().replace('format=yuv420p[v]', f'format=yuv420p,trim=end_frame={n},setpts=PTS-STARTPTS[v]')
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
    fc = graded_filter() if graded else f"[0:v]{VF}[v]"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{out2src(t)}', '-i', RAW,
                    '-filter_complex', fc, '-map', '[v]', '-frames:v', '1', p], check=True)
    return Image.open(p).convert('RGBA')


def make_music(total):
    """Video 4's acoustic track, looped with crossfades until it covers the whole video."""
    src = os.path.join(WORK, '..', 'v4', 'music.m4a')
    n = int(total // 85) + 1
    ins = sum([['-i', src] for _ in range(n + 1)], [])
    fc, last = '', '[0:a]'
    for i in range(1, n + 1):
        fc += f"{last}[{i}:a]acrossfade=d=4:c1=tri:c2=tri[x{i}];"
        last = f'[x{i}]'
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', fc.rstrip(';'), '-map', last,
                    '-c:a', 'aac', '-b:a', '192k', MUSIC], check=True)


# ---------------------------------------------------------------- graphics
def name_card(name, role, w=760):
    """Dark name card; name may be a list of lines (plaque names), role may be a list too."""
    names = [name] if isinstance(name, str) else name
    roles = [role] if isinstance(role, str) else role
    sz = 60
    while max(font(F_XB, sz).getlength(n) for n in names) > w - 90:
        sz -= 2
    lh, rh = int(sz * 1.2), 48
    h = 44 + lh * len(names) + rh * len(roles) + 26
    im = rounded((w, h), 40, (16, 18, 34, 238))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 18, h], 9, fill=GOLD + (255,))
    y = 44 + lh / 2
    for n in names:
        d.text((52, y), n, font=font(F_XB, sz), fill=(255, 255, 255, 255), anchor='lm')
        y += lh
    y += (rh - lh) / 2 + 6
    for r in roles:
        rs = 38
        while font(F_B, rs).getlength(r) > w - 90:
            rs -= 2
        d.text((54, y), r, font=font(F_B, rs), fill=GOLD_L + (255,), anchor='lm')
        y += rh
    return with_shadow(im, 20, 10, 0.45)


def year_badge(top, big, w=640):
    im = rounded((w, 230), 44, (16, 18, 34, 238))
    d = ImageDraw.Draw(im)
    d.text((w / 2, 62), top, font=font(F_XB, 44), fill=(200, 202, 220, 255), anchor='mm')
    d.text((w / 2, 150), big, font=font(F_XB, 118), fill=GOLD_L + (255,), anchor='mm')
    return with_shadow(im, 20, 10, 0.45)


def growth_card(p, w=760, h=300):
    im = rounded((w, h), 40, NAVY_C)
    d = ImageDraw.Draw(im)
    d.text((40, 56), 'PERKEMBANGAN PUBLIC GOLD', font=font(F_XB, 38), fill=(255, 255, 255, 255), anchor='lm')
    d.text((40, 250), 'dari zero', font=font(F_B, 34), fill=(170, 174, 200, 255), anchor='lm')
    base, x0 = 225, 300
    for i in range(6):
        k = ease_out(min(1, max(0, (p - i * 0.1) / 0.35)))
        hh = (30 + i * 24) * k
        x = x0 + i * 70
        if hh > 1:
            d.rounded_rectangle([x, base - hh, x + 46, base], 10, fill=(RED if i < 2 else GOLD) + (255,))
    k = ease_out(min(1, max(0, (p - 0.55) / 0.3)))
    if k > 0:
        ax = x0 + 70 * 5 + 23
        d.polygon([(ax - 22, base - 175), (ax + 22, base - 175), (ax, base - 175 - 30 * k)], fill=GOLD_L + (255,))
    return with_shadow(im, 20, 10, 0.45)


def slam_text(txt, size=104, maxw=760):
    spr = text_sprite(txt, size, GOLD_L, GOLD, stroke=7, stroke_col=(40, 26, 8))
    if spr.width > maxw:    # leaves room for the slam overshoot and tilt inside the safe width
        spr = spr.resize((maxw, int(spr.height * maxw / spr.width)), Image.LANCZOS)
    return spr


def record_card(w=840, h=330):
    im = rounded((w, h), 40, (16, 18, 34, 240))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([34, 30, 300, 86], 28, fill=GOLD + (255,))
    d.text((167, 58), 'NATIONAL RECORD', font=font(F_XB, 26), fill=(30, 22, 10, 255), anchor='mm')
    d.text((36, 140), 'The Malaysia Book of Records', font=font(F_XB, 44), fill=(255, 255, 255, 255), anchor='lm')
    d.text((36, 210), 'Biggest Gold Bar', font=font(F_XB, 60), fill=GOLD_L + (255,), anchor='lm')
    d.text((36, 282), '28 Mac 2026', font=font(F_B, 38), fill=(190, 192, 210, 255), anchor='lm')
    # small medal
    cx, cy = w - 110, 120
    d.polygon([(cx - 34, cy + 20), (cx - 10, cy + 20), (cx - 30, cy + 110), (cx - 48, cy + 90)], fill=RED + (255,))
    d.polygon([(cx + 34, cy + 20), (cx + 10, cy + 20), (cx + 30, cy + 110), (cx + 48, cy + 90)], fill=RED + (255,))
    d.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], fill=GOLD + (255,), outline=GOLD_L + (255,), width=6)
    d.text((cx, cy), '1', font=font(F_XB, 70), fill=(60, 40, 10, 255), anchor='mm')
    return with_shadow(im, 20, 10, 0.45)


def quote_pill(text, size=54):
    f = font(F_XB, size)
    tw = int(f.getlength(text))
    w, h = tw + 150, size + 70
    im = rounded((w, h), h // 2, (16, 18, 34, 238))
    d = ImageDraw.Draw(im)
    d.text((40, h / 2 + 8), '“', font=font(F_XB, size + 30), fill=GOLD + (255,), anchor='lm')
    d.text((100, h / 2), text, font=f, fill=GOLD_L + (255,), anchor='lm')
    return with_shadow(im, 18, 8, 0.4)


def plane_icon(s=60, col=(30, 110, 230)):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = col + (255,)
    d.polygon([(s * .08, s * .55), (s * .92, s * .3), (s * .98, s * .38), (s * .2, s * .68)], fill=c)
    d.polygon([(s * .45, s * .45), (s * .55, s * .1), (s * .66, s * .12), (s * .62, s * .42)], fill=c)
    d.polygon([(s * .4, s * .58), (s * .58, s * .9), (s * .68, s * .88), (s * .58, s * .52)], fill=c)
    return im.rotate(10, resample=Image.BICUBIC)


def star_icon(s=60, col=GOLD):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    pts = []
    for i in range(10):
        r = s * (0.48 if i % 2 == 0 else 0.2)
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((s / 2 + r * math.cos(a), s / 2 + r * math.sin(a)))
    ImageDraw.Draw(im).polygon(pts, fill=col + (255,))
    return im


def write_word_list(words):
    """Word-by-word spelling sheet for the user (output timestamps; ⚠ = please check)."""
    lines = ['VIDEO 10 - Galeri Public Gold (Bahasa Sarawak)',
             'Senarai perkataan ikut bunyi. Tanda [?] = sila semak ejaan / bunyi.',
             'Masa = kedudukan dalam video siap (minit:saat).', '']
    cur = None
    for w in words:
        if w['cue'] != cur:
            cur = w['cue']
            mm, ss = divmod(w['os'], 60)
            lines += ['', f"[{int(mm)}:{ss:04.1f}]  {re.sub(r'~\d+', '', CUES[cur][2])}"]
        mm, ss = divmod(w['os'], 60)
        mark = '  [?]' if w['w'].lower() in FLAG else ''
        lines.append(f"    {int(mm)}:{ss:04.1f}  {w['w']}{mark}")
    p = os.path.join(WORK, 'SEMAK_EJAAN_video10.txt')
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
    if not os.path.exists(MUSIC):
        make_music(total)
    if not preview and '--audio-preview' not in sys.argv and '--skip-base' not in sys.argv:
        render_base()
    json.dump(words, open(os.path.join(OUT, 'words.json'), 'w'), indent=1)

    def ct(n, end=False):
        s, e, _ = CUES[n]
        return src2out(e if end else s)

    def wt(word, nth=1):
        k = 0
        for w in words:
            if w['w'].lower() == word.lower():
                k += 1
                if k == nth:
                    return w['os']
        raise KeyError(word)

    gold_words = {'public', 'gold', 'emas', 'perak', 'terbesar', 'pertama', 'kukuhnya', 'refinery', 'legacy',
                  'record', 'biggest', 'vvip', 'achievers', 'dealer', 'mahaguru', 'guru', 'founder'}
    keep_case = {'Public', 'Gold', "Dato'", 'Seri', 'Louis', 'Ng', 'Menara', 'Jalan', 'Tuanku', 'Abdul', 'Razak',
                 'Galeri', 'Malaysia', 'Refinery', 'Factory', 'Batu', 'Kawan', 'Penang', 'Global', 'Footprint',
                 'National', 'Record', 'Malaysia', 'Book', 'Biggest', 'Bar', 'Mac', 'VVIP', 'Trip', 'Leadership',
                 'Seminar', 'Million', 'Star', 'Triple', 'Diamond', 'G', 'Hundred', 'Mahaguru', 'Emas', 'Tuan',
                 'Cikgu', 'Hashim'}
    cap_cache = {}

    def cap(word):
        if word not in cap_cache:
            num = word[:1].isdigit()
            disp = word if num or word in keep_case else word.lower()
            sz = 104
            while font(F_XB, sz).getlength(disp) > 880:
                sz -= 4
            if word.lower() in gold_words or num:
                top, bot = GOLD_L, GOLD
            else:
                top, bot = (255, 255, 255), (247, 228, 160)
            cap_cache[word] = text_sprite(disp, sz, top, bot, stroke=5, stroke_col=(25, 18, 20))
        return cap_cache[word]
    cap_win = []
    for i, w in enumerate(words):
        nxt = words[i + 1]['os'] if i + 1 < len(words) else w['oe'] + 0.3
        cap_win.append((w['os'], nxt if nxt - w['oe'] < 0.35 else w['oe'] + 0.15, w['w']))

    # jump cuts where the camera moved on (source gap > 1.5 s): flash + soft whoosh
    jumps = [o for (a0, b0), (a1, b1), o in zip(SEGS, SEGS[1:], offs[1:]) if a1 - b0 > 1.5]

    CX = B.TT_CENTER_X
    t1 = text_sprite('GALERI', 132, RED, RED, stroke=9, stroke_col=(255, 255, 255))
    t2 = text_sprite('PUBLIC GOLD', 124, (255, 255, 255), GOLD_L, stroke=7, stroke_col=(30, 22, 10))
    p_scam = fit_pill('Scammer pun bukan nunjuk...', icon=warn_icon(60), size=52)
    n_louis = name_card("Dato' Seri Louis Ng", 'Founder Public Gold')
    p_menara = fit_pill('Menara Public Gold, Jalan Tuanku Abdul Razak', icon=pin_icon(56), size=40)
    p_galeri = fit_pill('Galeri Public Gold', icon=pin_icon(56), size=54, bg=(232, 190, 92, 255))
    b_tingkat = badge('4', 'TINGKAT', 'Galeri Public Gold')
    y2008 = year_badge('BERTAPAK DI MALAYSIA', 'SINCE 2008')
    p_besar1 = fit_pill('Syarikat jual beli emas & perak', icon=check_icon(56), size=48)
    p_besar2 = slam_text('TERBESAR DI MALAYSIA', 84)
    p_refinery = fit_pill('Public Gold Refinery Factory', size=52, bg=(232, 190, 92, 255))
    p_kilang = fit_pill('Kilang penulenan emas', icon=check_icon(56), size=50)
    p_batu = fit_pill('Batu Kawan, Penang', icon=pin_icon(56), size=50)
    s_pertama = slam_text('PERTAMA DI MALAYSIA', 88)
    p_kukuh = fit_pill('Betapa kukuhnya Public Gold', icon=check_icon(56), size=50)
    p_global = fit_pill('Public Gold Global Footprint', icon=pin_icon(56), size=50, bg=(232, 190, 92, 255))
    q_legacy = quote_pill('Many region, one legacy')
    p_awards = fit_pill('Awards Public Gold', icon=star_icon(56), size=52)
    c_record = record_card()
    p_vvip = fit_pill('VVIP Trip', icon=plane_icon(60), size=60, bg=(232, 190, 92, 255))
    p_seminar = fit_pill('Leadership Seminar', icon=plane_icon(60), size=56)
    p_achiever = fit_pill('Trip untuk para achievers', icon=check_icon(56), size=48)
    p_dealer = fit_pill('Kelebihan bila jadi dealer', icon=star_icon(56), size=50, bg=(232, 190, 92, 255))
    p_taja = fit_pill('VVIP Trip ditaja sepenuhnya oleh Public Gold', icon=check_icon(56), size=40)
    p_guru = fit_pill('Guru kami', icon=star_icon(56), size=56, bg=(232, 190, 92, 255))
    # names from the portrait plaques (user: "ikut plak")
    n_msd = name_card(['Mohd Zulkifli bin Shafie &', 'Najdah binti Mohammed Hussain'],
                      ['Million Star Triple Diamond', 'Guru kami'], w=840)
    n_g100 = name_card('Founder G100', 'Guru kami & suami', w=700)
    n_maha = name_card(['Syukor bin Hashim &', 'Jonaina binti Nordin'],
                       ['Mahaguru Emas Malaysia', 'Million Star Double Diamond'], w=840)
    p_cta1 = fit_pill('Berminat jadi dealer?', icon=star_icon(56), size=54, bg=(232, 190, 92, 255))
    p_cta2 = fit_pill('Join team kami', icon=arrow_icon(60, False, (232, 150, 40)), size=56)
    logo_c, logo_w = load_logos()
    wm = logo_w.resize((150, int(150 * logo_w.height / logo_w.width)), Image.LANCZOS)

    T = {'scam': wt('scammer'), 'founder': ct(3), 'louis': ct(4), 'menara': wt('Menara'), 'galeri': ct(7),
         'tingkat': wt('tingkat'), 'since': wt('since'), 'syarikat': wt('syarikat'), 'terbesar2': ct(16),
         'growth': ct(17), 'refinery': wt('Refinery'), 'kilang': ct(23), 'batu': wt('Batu'),
         'pertama': wt('pertama'), 'kukuh': ct(25), 'global': wt('Global'), 'legacy': ct(31),
         'awards': ct(33), 'record': wt('National'), 'vvip': wt('VVIP'), 'seminar': ct(48), 'achiever': ct(49),
         'dealer': wt('dealer'), 'taja': ct(56), 'guru': ct(63), 'msd': wt('Million'), 'g100': ct(70),
         'maha': ct(73), 'hashim': ct(74), 'cta1': ct(76), 'cta2': ct(77)}
    T['e_hook'] = ct(5) - 0.05
    pops = [T[k] for k in ('scam', 'founder', 'louis', 'menara', 'galeri', 'tingkat', 'syarikat', 'growth',
                           'refinery', 'kilang', 'batu', 'kukuh', 'global', 'legacy', 'awards', 'record', 'vvip',
                           'seminar', 'achiever', 'dealer', 'taja', 'guru', 'msd', 'g100', 'maha', 'cta1', 'cta2')]
    whooshes = [(0.0, 0.4, 0.24), (T['since'] - 0.15, 0.35, 0.2), (T['terbesar2'] - 0.15, 0.35, 0.2),
                (T['pertama'] - 0.15, 0.4, 0.24)] + [(j - 0.12, 0.3, 0.12) for j in jumps] + \
               [(base_dur - 0.15, 0.5, 0.22)]

    if '--audio-preview' in sys.argv:
        write_sfx(total, pops, whooshes, os.path.join(OUT, 'sfx.wav'))
        n = len(SEGS)
        chain = ''.join(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.03,"
                        f"afade=t=out:st={b-a-0.03:.3f}:d=0.03[s{i}];" for i, (a, b) in enumerate(SEGS))
        chain += ''.join(f'[s{i}]' for i in range(n)) + f'concat=n={n}:v=0:a=1[voice];'
        fc = chain + B.audio_mix_graph('[voice]', '[1:a]', total, '[2:a]', MUSIC_SS, MUSIC_DB, outro_at=base_dur,
                                       music_tempo=MUSIC_TEMPO)
        outp = os.path.join(WORK, 'PREVIEW_audio_music.m4a')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', RAW, '-i', os.path.join(OUT, 'sfx.wav'), '-i', MUSIC,
                        '-filter_complex', fc, '-map', '[a]', '-t', f'{total}', '-c:a', 'aac', '-b:a', '128k', outp],
                       check=True)
        print('audio preview', outp, 'total', round(total, 2))
        return

    def show(fr, spr, cx, cy, t0, t1, rot=0):
        s, a = pop(t, t0, t1)
        place(fr, spr, cx, cy, s, a, rot=rot)

    def slam(fr, spr, cx, cy, t0, t1):
        s, a = pop(t, t0, t1)
        k = 1 + 0.25 * max(0, 1 - (t - t0) / 0.16)
        place(fr, spr, cx, cy, s * k if s >= 1 else s, a, rot=-3)

    def overlay(tt):
        nonlocal t
        t = tt
        fr = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        if t >= base_dur:
            return outro_frame(t - base_dur, int(t * FPS), logo_w), False
        # HOOK: kinetic title + the scammer line
        show(fr, t1, CX - 60, 235, 0.03, T['founder'] + 0.5, rot=-4)
        show(fr, t2, CX + 30, 370, 0.25, T['founder'] + 0.5, rot=-4)
        show(fr, p_scam, CX, 520, T['scam'] - 0.1, T['founder'] - 0.05)
        show(fr, n_louis, CX, 300, T['founder'] + 0.6, T['e_hook'])
        # location
        show(fr, p_menara, CX, 250, T['menara'], T['galeri'] - 0.05)
        show(fr, p_galeri, CX, 250, T['galeri'] + 0.2, T['tingkat'] - 0.4)
        show(fr, b_tingkat, CX, 290, T['tingkat'], ct(10, True) + 0.3)
        slam(fr, y2008, CX, 300, T['since'] - 0.1, ct(13) + 1.2)
        show(fr, p_besar1, CX, 240, T['syarikat'], ct(16, True) + 0.4)
        slam(fr, p_besar2, CX, 380, T['terbesar2'], ct(16, True) + 0.4)
        if T['growth'] <= t < ct(17, True) + 0.8:
            s, a = pop(t, T['growth'], ct(17, True) + 0.8)
            place(fr, growth_card((t - T['growth']) / 2.5), CX, 300, s, a)
        # refinery
        show(fr, p_refinery, CX, 240, T['refinery'] - 0.2, ct(23, True) + 0.3)
        show(fr, p_kilang, CX, 370, T['kilang'] + 0.3, ct(23, True) + 0.3)
        show(fr, p_batu, CX, 490, T['batu'], ct(23, True) + 0.3)
        slam(fr, s_pertama, CX, 300, T['pertama'] - 0.1, ct(24, True) + 0.6)
        show(fr, p_kukuh, CX, 260, T['kukuh'] + 0.3, ct(25, True) + 0.4)
        # global footprint, awards
        show(fr, p_global, CX, 240, T['global'] - 0.2, ct(32, True) + 0.2)
        show(fr, q_legacy, CX, 380, T['legacy'], ct(32, True) + 0.2)
        show(fr, p_awards, CX, 240, T['awards'] + 0.2, T['record'] - 0.1)
        if T['record'] - 0.1 <= t < ct(37, True) + 0.6:
            s, a = pop(t, T['record'] - 0.1, ct(37, True) + 0.6)
            card = shine(c_record, (t - T['record']) / 1.2)
            place(fr, card, CX, 330, s, a)
        # VVIP trip / leadership seminar / dealer
        show(fr, p_vvip, CX, 260, T['vvip'] - 0.1, ct(45, True) + 0.5)
        show(fr, p_seminar, CX, 240, T['seminar'] + 0.1, ct(50, True) + 0.2)
        show(fr, p_achiever, CX, 370, T['achiever'] + 1.2, ct(50, True) + 0.2)
        show(fr, p_dealer, CX, 240, T['dealer'] - 0.2, ct(56, True) + 0.3)
        show(fr, p_taja, CX, 370, T['taja'] - 0.4, ct(57, True))
        # gurus
        show(fr, p_guru, CX, 240, T['guru'] + 0.8, T['msd'] - 0.1)
        show(fr, n_msd, CX, 330, T['msd'] - 0.1, ct(67, True) + 0.2)
        show(fr, n_g100, CX, 290, T['g100'], ct(70, True) + 1.0)
        show(fr, n_maha, CX, 330, T['maha'] + 1.0, ct(74, True) + 0.4)
        # CTA
        show(fr, p_cta1, CX, 240, T['cta1'] + 0.6, base_dur - 0.02)
        show(fr, p_cta2, CX, 370, T['cta2'] + 0.2, base_dur - 0.02)
        place(fr, wm, 95, 1010, 0.85, 0.85)
        for a0, a1, w in (cap_win if CAPTIONS else ()):
            if a0 <= t < a1:
                k = (t - a0) / 0.09
                place(fr, cap(w), W / 2, B.TT_CAPTION_Y, 0.82 + 0.18 * back_out(min(1, k)) if k < 1 else 1, 1)
                break
        for j in jumps:
            if j <= t < j + 0.14:
                fl = Image.new('RGBA', (W, H), (255, 255, 255, int(110 * (1 - (t - j) / 0.14))))
                fr = Image.alpha_composite(fl, fr)
        return fr, True
    t = 0.0

    if '--clip' in sys.argv:
        # short low-res sync-check clip on the rendered base (overlays + voice), e.g. --clip 135 162
        i = sys.argv.index('--clip')
        c0, c1 = float(sys.argv[i + 1]), float(sys.argv[i + 2])
        cdir = os.path.join(OUT, 'clip')
        os.makedirs(cdir, exist_ok=True)
        for k in range(int((c1 - c0) * FPS)):
            ov, _ = overlay(c0 + k / FPS)
            ov.resize((540, 960), Image.LANCZOS).save(os.path.join(cdir, f'c{k:05d}.png'), compress_level=1)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{c0}', '-t', f'{c1 - c0}', '-i', os.path.join(OUT, 'base.mov'),
                        '-framerate', f'{FPS}', '-i', os.path.join(cdir, 'c%05d.png'),
                        '-filter_complex', '[0:v]scale=540:960[b];[b][1:v]overlay=0:0:shortest=1[v]', '-map', '[v]',
                        '-map', '0:a', '-c:v', 'libx264', '-crf', '24', '-c:a', 'aac', '-b:a', '128k',
                        '-movflags', '+faststart', os.path.join(WORK, 'PREVIEW_sync_check.mp4')], check=True)
        print('clip ok')
        return

    if preview:
        shots = [('Hook', 2.2), ('Scammer', T['founder'] - 0.2), ('Founder', T['louis'] + 0.8),
                 ('Lokasi', T['galeri'] - 0.3), ('Tingkat 4', T['tingkat'] + 0.8), ('Since 2008', T['since'] + 0.8),
                 ('Terbesar', T['terbesar2'] + 0.8), ('Dari zero', T['growth'] + 2.6),
                 ('Refinery', T['batu'] + 0.6), ('Pertama', T['pertama'] + 0.6), ('Global', T['legacy'] + 0.6),
                 ('Rekod', T['record'] + 2.0), ('VVIP Trip', T['vvip'] + 0.6), ('Seminar', T['achiever'] + 1.6),
                 ('Dealer', T['taja'] + 0.6), ('Guru', T['msd'] + 1.0), ('G100', T['g100'] + 0.6),
                 ('Mahaguru', T['hashim'] + 0.6), ('CTA', base_dur - 0.5), ('Outro', base_dur + 1.6)]
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
        # before/after grade
        cmp_ = Image.new('RGB', (4 * 1100 + 20, 1000), (24, 24, 30))
        d = ImageDraw.Draw(cmp_)
        for i, tt in enumerate((T['louis'] + 0.5, T['since'], T['record'] + 1.0, T['hashim'])):
            for j, gr in enumerate((False, True)):
                im = base_still(tt, gr).resize((540, 960), Image.LANCZOS).convert('RGB')
                cmp_.paste(im, (20 + i * 1100 + j * 545, 36))
                d.text((20 + i * 1100 + j * 545, 18), 'Asal' if not gr else 'Fuji grade', font=font(F_B, 26),
                       fill=(255, 255, 255) if not gr else GOLD_L, anchor='lm')
        cmp_.save(os.path.join(WORK, 'PREVIEW_colorgrade.jpg'), quality=86)
        print('preview ok; segments', len(SEGS), 'jumps', len(jumps), 'base', round(base_dur, 2),
              'total', round(total, 2))
        return

    fdir = os.path.join(OUT, 'frames')
    os.makedirs(fdir, exist_ok=True)
    for fi in range(int(round(total * FPS))):
        ov, _ = overlay(fi / FPS)
        ov.save(os.path.join(fdir, f'f{fi:05d}.png'), compress_level=1)
    write_sfx(total, pops, whooshes, os.path.join(OUT, 'sfx.wav'))
    final = os.path.join(OUT, 'GaleriPublicGold_AzlanEza.mp4')
    composite(os.path.join(OUT, 'base.mov'), fdir, os.path.join(OUT, 'sfx.wav'), total, final,
              music=MUSIC, music_ss=MUSIC_SS, music_db=MUSIC_DB, music_tempo=MUSIC_TEMPO)
    print('done', final)


if __name__ == '__main__':
    main()
