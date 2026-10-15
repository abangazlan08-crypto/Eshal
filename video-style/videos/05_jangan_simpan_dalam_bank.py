#!/usr/bin/env python3
"""Video 5: 'Jangan simpan duit banyak-banyak dalam akaun bank' (studio, Public Gold) in the Azlan & Eza style.

python3 build_v5.py --preview         -> storyboard stills only
python3 build_v5.py --audio-preview   -> voice + sfx + music mix only
python3 build_v5.py                   -> full render
"""
import importlib.util, json, math, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_VS = os.path.join(HERE, '..')
WORK = os.path.join(HERE, '..', 'work', 'v5')   # raw footage, news photo, licensed music (not in git)
ASSETS = os.path.join(HERE, '05_assets')
sys.path.insert(0, REPO_VS)
import numpy as np
import build as B
from build import (W, H, FPS, OUTRO, RED, F_XB, F_B, Image, ImageDraw, ImageFilter, text_sprite, rounded,
                   with_shadow, place, pop, pill, check_icon, ease_out, back_out, font, paper_texture,
                   load_logos, outro_frame, write_sfx, composite, syllables)
_spec = importlib.util.spec_from_file_location('v3', os.path.join(REPO_VS, 'videos', '03_konsisten_emas.py'))
V3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V3)
x_icon, shine, badge, GOLD, GOLD_L = V3.x_icon, V3.shine, V3.badge, V3.GOLD, V3.GOLD_L

RAW = os.environ.get('RAW', os.path.join(WORK, 'raw.mp4'))
IMG1 = os.path.join(WORK, 'img1.jpg')      # news photo: Kompleks Mahkamah Kuala Terengganu
PHOTO_CREDIT = os.environ.get('PHOTO_CREDIT', 'Gambar: ihsan laporan media')   # replace with the outlet name when known
OUT = os.environ.get('OUT', os.path.join(WORK, 'out'))
MASK = os.path.join(HERE, '03_assets', 'facemask.png')   # same studio as video 3
# Descript stock (Audioblocks): "Cautious Search", 122.8s, ~128 BPM, builds toward the end.
MUSIC = os.path.join(WORK, "music.m4a")
MUSIC_SS, MUSIC_DB = 0.0, -18.0
MUSIC_TEMPO = 0.955   # track's ending hits at ~119s; stretch 4.5% (same pitch) so it lands on the end of the outro
os.makedirs(OUT, exist_ok=True)
GRADE = V3.GRADE        # same studio + lighting as video 3
RELIGHT = V3.RELIGHT

# Descript SRT cues. Tokens "display~syllables" show a compact caption (e.g. numbers) for a long spoken phrase.
CUES = [
    (0.850, 3.750, "Jangan simpan duit banyak-banyak dalam akaun bank."),
    (4.650, 11.390, "Bayangkan duit RM1.99~9 juta ringgit dalam akaun"),
    (11.450, 13.770, "bank tiba-tiba dilaporkan hilang."),
    (14.590, 19.750, "Baki yang tinggal RM73~6 dan RM99~5"),
    (19.790, 21.850, "ringgit~2 sahaja."),
    (22.730, 25.050, "Ini bukan cerita rekaan."),
    (25.570, 30.730, "Seorang kerabat diraja Terengganu dilaporkan menyaman dua buah bank"),
    (31.170, 37.690, "selepas mendakwa wang simpanannya hilang akibat transaksi mencurigakan."),
    (38.350, 43.550, "Sebab itulah pakar kewangan selalu pesan, kalau anda mempunyai simpanan"),
    (43.610, 49.330, "100~3 ribu, 500~4 ribu ringgit ataupun 1~2 juta ringgit, jangan"),
    (49.370, 51.610, "letakkan semuanya dalam satu tempat."),
    (52.330, 55.510, "Bukan bermaksud bank tidak selamat."),
    (56.010, 61.350, "Tetapi orang yang bijak menguruskan kekayaan faham satu perkara."),
    (62.290, 67.710, "Duit yang kita cari perlu dijaga, bukan sekadar dikumpul."),
    (69.914, 74.854, "Simpan sebahagian dalam bank untuk keperluan dan kecemasan."),
    (75.194, 81.174, "Sebahagian lagi boleh diperbagaikan daripada aset seperti emas fizikal."),
    (81.954, 86.994, "Contohnya emas 100~3 gram, 250~7 gram ataupun"),
    (87.554, 93.054, "1~2 kilogram bergantung kepada kemampuan dan matlamat kewangan anda."),
    (94.094, 97.394, "Emas juga ada risiko harga dan penyimpanan."),
    (97.774, 101.674, "Jadi penting untuk faham sebelum membeli."),
    (102.314, 108.294, "Ingat, membina kekayaan mengambil masa bertahun-tahun tetapi melindungi"),
    (108.334, 111.474, "kekayaan memerlukan ilmu dan perancangan."),
    (112.533, 119.214, "Kalau anda mempunyai simpanan 100~3 ribu ringgit ataupun 1~2 juta ringgit"),
    (119.234, 125.634, "sekali pun, jangan tunggu sesuatu berlaku baru nak belajar tentang pengurusan aset."),
    (125.954, 130.694, "Saya boleh bantu anda untuk memahami bagaimana nak memperbagaikan simpanan"),
    (130.714, 133.334, "melalui emas fizikal di Public Gold."),
]
CUT_OUT = []   # user: keep original context even if it goes past 2 minutes
B.SYL.update({'banyak-banyak': 4, 'tiba-tiba': 4, 'bertahun-tahun': 5, 'Public': 2, 'Gold': 1})


def build_segs():
    regs = json.load(open(os.path.join(ASSETS, 'edl_all.json')))['regs']
    keep = []
    for a, b in regs:
        if b < 0.7 or a > 133.5:
            continue
        a2, b2 = max(0, a - 0.08), b + 0.10
        for c0, c1 in CUT_OUT:
            if a2 < c1 and b2 > c0:
                if a2 < c0:
                    keep.append([a2, c0])
                if b2 > c1:
                    keep.append([c1, b2])
                break
        else:
            keep.append([a2, b2])
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
                toks.append(d.strip('.,?')), wts.append(int(n))
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
NAVY_C = (18, 20, 36, 255)
ALERT = (220, 38, 38)


def warn_icon(s=60):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(s / 2, 2), (s - 2, s - 4), (2, s - 4)], fill=(245, 180, 40, 255))
    d.rounded_rectangle([s / 2 - 4, s * .3, s / 2 + 4, s * .66], 3, fill=(30, 22, 10, 255))
    d.ellipse([s / 2 - 5, s * .72, s / 2 + 5, s * .84], fill=(30, 22, 10, 255))
    return im


def money_card(value, label, col=(255, 255, 255), sub=None, w=760):
    im = rounded((w, 300), 44, NAVY_C)
    d = ImageDraw.Draw(im)
    d.text((w / 2, 70), label, font=font(F_B, 38), fill=(150, 154, 180, 255), anchor='mm')
    sz = 120
    while font(F_XB, sz).getlength(value) > w - 80:
        sz -= 4
    d.text((w / 2, 175), value, font=font(F_XB, sz), fill=col + (255,), anchor='mm')
    if sub:
        d.text((w / 2, 258), sub, font=font(F_B, 32), fill=(170, 172, 190, 255), anchor='mm')
    return with_shadow(im, 22, 12, 0.45)


def stamp(text, col=ALERT):
    f = font(F_XB, 110)
    tw = int(f.getlength(text))
    im = Image.new('RGBA', (tw + 80, 190), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, tw + 74, 184], 26, outline=col + (255,), width=12)
    d.text(((tw + 80) / 2, 95), text, font=f, fill=col + (255,), anchor='mm')
    return im.rotate(-8, resample=Image.BICUBIC, expand=True)


def news_card(p, photo):
    cw, ch = 940, 960
    im = rounded((cw, ch), 44, NAVY_C)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([40, 36, 300, 96], 30, fill=ALERT + (255,))
    d.text((170, 66), 'DILAPORKAN', font=font(F_XB, 32), fill=(255, 255, 255, 255), anchor='mm')
    # the photo is two shots stacked: show the top one, then dissolve to the bottom one
    pw = cw - 80
    halves = [photo.crop((0, 0, photo.width, photo.height // 2)), photo.crop((0, photo.height // 2, photo.width, photo.height))]
    phh = int(pw * halves[0].height / halves[0].width)
    k = ease_out(min(1, max(0, p) / 0.3))
    zoom = 1.0 + 0.06 * max(0, p)
    mix = min(1, max(0, (p - 0.45) / 0.15))
    ph = Image.blend(halves[0].resize((pw, phh), Image.LANCZOS), halves[1].resize((pw, phh), Image.LANCZOS), mix)
    phz = ph.resize((int(pw * zoom), int(phh * zoom)), Image.LANCZOS).crop(
        (int(pw * (zoom - 1) / 2), int(phh * (zoom - 1) / 2), int(pw * (zoom - 1) / 2) + pw, int(phh * (zoom - 1) / 2) + phh)).convert('RGBA')
    m = Image.new('L', (pw, phh), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, pw - 1, phh - 1], 28, fill=int(255 * k))
    phz.putalpha(m)
    im.alpha_composite(phz, (40, 120))
    d.text((cw - 50, 120 + phh + 14), PHOTO_CREDIT, font=font(F_B, 22), fill=(150, 154, 180, int(255 * k)), anchor='ra')
    y = 120 + phh + 70
    lines = [('Kerabat diraja Terengganu', F_XB, 50, (255, 255, 255)),
             ('saman 2 buah bank', F_XB, 50, GOLD_L),
             ('dakwa wang hilang akibat transaksi mencurigakan', F_B, 30, (170, 172, 190))]
    for i, (txt, f, sz, col) in enumerate(lines):
        kk = ease_out((p - 0.25 - i * 0.12) / 0.25)
        if kk > 0:
            d.text((cw / 2, y + i * 64 + (1 - kk) * 20), txt, font=font(f, sz), fill=col + (int(255 * kk),), anchor='mm')
    return with_shadow(im, 28, 16, 0.4)


def basket_card(p):
    """All savings in one place -> spread across places."""
    cw, ch = 920, 900
    im = rounded((cw, ch), 48, NAVY_C)
    d = ImageDraw.Draw(im)
    d.text((cw / 2, 90), 'JANGAN LETAK SEMUA', font=font(F_XB, 58), fill=(255, 255, 255, 255), anchor='mm')
    d.text((cw / 2, 160), 'DALAM SATU TEMPAT', font=font(F_XB, 58), fill=GOLD_L + (255,), anchor='mm')
    k = ease_out(min(1, max(0, p - 0.15) / 0.45))
    coins = [(cw / 2 + dx, 470 + dy) for dx, dy in ((-60, 0), (0, -30), (60, 0), (-30, 50), (30, 50), (0, 100))]
    targets = [(200, 470), (200, 560), (cw / 2, 430), (cw / 2, 520), (cw - 200, 470), (cw - 200, 560)]
    if k > 0.05:
        for tx, lab in ((200, 'Bank'), (cw / 2, 'Emas fizikal'), (cw - 200, 'Aset lain')):
            d.rounded_rectangle([tx - 130, 360, tx + 130, 660], 30, outline=(80, 84, 110, int(255 * k)), width=5)
            d.text((tx, 700), lab, font=font(F_B, 34), fill=(220, 222, 235, int(255 * k)), anchor='mm')
    else:
        d.rounded_rectangle([cw / 2 - 170, 360, cw / 2 + 170, 660], 30, outline=(80, 84, 110, 255), width=5)
    for (sx, sy), (tx, ty) in zip(coins, targets):
        x, y = sx + (tx - sx) * k, sy + (ty - sy) * k
        d.ellipse([x - 38, y - 38, x + 38, y + 38], fill=GOLD + (255,), outline=(255, 240, 190, 255), width=5)
        d.text((x, y), 'RM', font=font(F_XB, 26), fill=(60, 40, 10, 255), anchor='mm')
    if p > 0.75:
        kk = ease_out((p - 0.75) / 0.2)
        d.text((cw / 2, 800), 'bukan bermaksud bank tak selamat', font=font(F_B, 32), fill=(150, 154, 180, int(255 * kk)), anchor='mm')
    return with_shadow(im, 28, 16, 0.4)


def gold_bar(w, label):
    h = int(w * 0.56)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(w * .1, 0), (w * .9, 0), (w, h), (0, h)], fill=(214, 168, 60, 255))
    d.polygon([(w * .16, h * .12), (w * .84, h * .12), (w * .9, h * .88), (w * .1, h * .88)], fill=(246, 210, 110, 255))
    sz = int(h * 0.36)
    d.text((w / 2, h / 2), label, font=font(F_XB, sz), fill=(110, 75, 15, 255), anchor='mm')
    return with_shadow(im, 12, 6, 0.4)


def split_card(p):
    """Simpan sebahagian dalam bank + sebahagian dalam emas fizikal (no percentages)."""
    cw, ch = 940, 900
    im = rounded((cw, ch), 48, NAVY_C)
    d = ImageDraw.Draw(im)
    d.text((cw / 2, 90), 'PERBAGAIKAN SIMPANAN', font=font(F_XB, 56), fill=(255, 255, 255, 255), anchor='mm')
    for i, (title, a, b, col, icon) in enumerate((('BANK', 'keperluan &', 'kecemasan', (90, 170, 255), 'bank'),
                                                 ('EMAS FIZIKAL', 'aset untuk', 'jangka panjang', GOLD, 'gold'))):
        k = back_out(min(1, max(0, p - i * 0.35) / 0.3))
        if k <= 0.02:
            continue
        box = rounded((410, 640), 36, (30, 33, 52, 255))
        bd = ImageDraw.Draw(box)
        bd.rounded_rectangle([30, 30, 380, 130], 30, fill=col + (255,))
        bd.text((205, 80), title, font=font(F_XB, 44 if i else 54), fill=(20, 20, 30, 255), anchor='mm')
        if icon == 'bank':
            bd.polygon([(205, 190), (330, 260), (80, 260)], fill=(220, 222, 235, 255))
            for x in (110, 170, 240, 300):
                bd.rectangle([x - 12, 275, x + 12, 380], fill=(220, 222, 235, 255))
            bd.rectangle([80, 390, 330, 410], fill=(220, 222, 235, 255))
        else:
            gb = gold_bar(230, 'EMAS')
            box.alpha_composite(gb, (int(205 - gb.width / 2), int(300 - gb.height / 2)))
        bd.text((205, 500), a, font=font(F_XB, 44), fill=(255, 255, 255, 255), anchor='mm')
        bd.text((205, 560), b, font=font(F_XB, 44), fill=(255, 255, 255, 255), anchor='mm')
        box = box.resize((max(1, int(410 * k)), max(1, int(640 * k))), Image.BICUBIC)
        im.alpha_composite(box, (int(40 + i * 450 + 205 - box.width / 2), int(500 - box.height / 2)))
    return with_shadow(im, 28, 16, 0.4)


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

    gold_words = {'emas', 'fizikal', 'dijaga', 'ilmu', 'perancangan', 'bijak', 'rm1.99', 'gold'}
    red_words = {'hilang', 'jangan', 'risiko', 'mencurigakan'}
    cap_cache = {}

    def cap(word):
        if word not in cap_cache:
            disp = word if word[:2] == 'RM' or word[:1].isdigit() or word in ('Public', 'Gold', 'Terengganu') else word.lower()
            sz = 104
            while font(F_XB, sz).getlength(disp) > 900:
                sz -= 4
            lw = word.lower()
            if lw in red_words:
                top, bot = (255, 150, 150), (240, 70, 80)
            elif lw in gold_words or word[:2] == 'RM' or word[:1].isdigit():
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
    h1 = text_sprite('JANGAN SIMPAN', 108, (255, 150, 150), (240, 70, 80), stroke=5, stroke_col=(255, 255, 255))
    h2 = text_sprite('BANYAK-BANYAK', 100, (255, 255, 255), (232, 232, 240))
    h3 = text_sprite('DALAM BANK!', 120, GOLD_L, GOLD, stroke=5, stroke_col=(60, 40, 10))
    st_hilang = stamp('HILANG')
    p_real = pill('Bukan cerita rekaan', icon=warn_icon(60), size=56)
    amounts = [pill(t, size=58, bg=(232, 190, 92, 255)) for t in ('RM100 ribu', 'RM500 ribu', 'RM1 juta')]
    p_bank_ok = pill('Bukan bermaksud bank tak selamat', icon=check_icon(60), size=48)
    p_kumpul = pill('Sekadar dikumpul', icon=x_icon(60), size=54)
    p_jaga = pill('Duit perlu DIJAGA', icon=check_icon(60), size=56, bg=(232, 190, 92, 255))
    bars = [gold_bar(w, l) for w, l in ((230, '100g'), (300, '250g'), (380, '1kg'))]
    p_ikut = pill('ikut kemampuan & matlamat', size=46)
    p_risk = pill('Emas juga ada risiko: harga & penyimpanan', icon=warn_icon(56), size=40)
    p_faham = pill('Faham sebelum membeli', icon=check_icon(60), size=54)
    p_bina = pill('Bina kekayaan: bertahun-tahun', size=50)
    p_lindung = pill('Lindungi: ilmu & perancangan', icon=check_icon(60), size=50, bg=(232, 190, 92, 255))
    p_tunggu = pill('Jangan tunggu sesuatu berlaku', icon=warn_icon(60), size=50)
    p_cta = pill('Perbagaikan simpanan dengan emas fizikal', size=42)
    p_pg = pill('Saya boleh bantu anda', icon=check_icon(60), size=56, bg=(232, 190, 92, 255))
    photo = Image.open(IMG1).convert('RGB')
    logo_c, logo_w = load_logos()
    wm = logo_w.resize((150, int(150 * logo_w.height / logo_w.width)), Image.LANCZOS)
    paper = paper_texture(W, H)

    T = {'banyak': wt('banyak-banyak'), 'bank': wt('bank'), 'bayang': cue_t(1), 'rm199': wt('RM1.99'),
         'hilang': wt('hilang'), 'baki': cue_t(3), 'rm73': wt('RM73'), 'rm99': wt('RM99'), 'rekaan': cue_t(5),
         'n_in': cue_t(6) - 0.05, 'n_out': cue_t(7, True) + 0.2,
         'pakar': cue_t(8), 'a100': wt('100'), 'a500': wt('500'), 'a1j': wt('1'),
         'b_in': wt('jangan', 2) - 0.05, 'b_out': cue_t(11, True) + 0.2,
         'bijak': cue_t(12), 'dijaga': wt('dijaga'), 'dikumpul': wt('dikumpul'),
         's_in': cue_t(14) - 0.05, 's_out': cue_t(15, True) + 0.2,
         'g100': wt('100', 2), 'g250': wt('250'), 'g1k': wt('1', 2), 'ikut': wt('kemampuan'),
         'risiko': cue_t(18), 'faham': cue_t(19), 'bina': cue_t(20), 'lindung': wt('melindungi'),
         'kalau2': cue_t(22), 'a100b': wt('100', 3), 'a1jb': wt('1', 3), 'tunggu': wt('jangan', 3), 'bantu': cue_t(24), 'pg': wt('Public')}
    hook_end = T['bayang'] - 0.05
    pops = [T[k] for k in ('rm199', 'rm73', 'rm99', 'rekaan', 'a100', 'a500', 'a1j', 'bijak', 'dijaga', 'g100',
                           'g250', 'g1k', 'risiko', 'faham', 'bina', 'lindung', 'tunggu', 'bantu', 'pg')]
    whooshes = [(T['bank'] - 0.15, 0.4, 0.24), (T['hilang'] - 0.1, 0.4, 0.26)] + \
               [(T[k + '_in'] - 0.12, 0.35, 0.18) for k in 'nbs'] + [(T[k + '_out'] - 0.15, 0.35, 0.18) for k in 'nbs'] + \
               [(base_dur - 0.15, 0.5, 0.22)]

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

    def counter(t, t0, dur, target, fmt):
        k = ease_out(min(1, max(0, (t - t0) / dur)))
        return fmt(target * k)

    def overlay(t):
        fr = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        if t >= base_dur:
            return outro_frame(t - base_dur, int(t * FPS), logo_w), False
        cut = None
        for a_, b_, kind in ((T['n_in'], T['n_out'], 'n'), (T['b_in'], T['b_out'], 'b'), (T['s_in'], T['s_out'], 's')):
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
            card = {'n': lambda q: news_card(q, photo), 'b': basket_card, 's': split_card}[kind](pr)
            place(fr, card, W / 2, H * 0.40 + (1 - k_in) * 120, 1.10 - 0.12 * k_in if kind == 'n' else 1.12 - 0.12 * k_in, a)
        else:
            # HOOK
            s, a = pop(t, 0.03, hook_end, 0.28, 0.12)
            place(fr, h1, W / 2 - 10, 200, s, a, rot=-3)
            s, a = pop(t, T['banyak'] - 0.05, hook_end, 0.25, 0.12)
            place(fr, h2, W / 2 + 10, 320, s, a, rot=-3)
            s, a = pop(t, T['bank'] - 0.05, hook_end, 0.22, 0.12)
            if a:
                slam = 1 + 0.5 * max(0, 1 - (t - T['bank'] + 0.05) / 0.18)
                place(fr, h3, W / 2, 450, s * slam if s >= 1 else s, a, rot=-3)
            # RM1.99 juta -> HILANG
            e1 = T['rm73'] - 0.12
            s, a = pop(t, T['rm199'] - 0.1, e1)
            if a:
                val = counter(t, T['rm199'] - 0.1, 1.0, 1.99, lambda v: f'RM{v:.2f} JUTA')
                place(fr, money_card(val, 'dalam akaun bank', GOLD_L), W / 2, 330, s, a)
            s, a = pop(t, T['hilang'] - 0.05, e1, 0.2, 0.12)
            if a:
                slam = 1 + 0.7 * max(0, 1 - (t - T['hilang'] + 0.05) / 0.16)
                place(fr, st_hilang, W / 2 + 120, 420, s * slam if s >= 1 else s, a)
            # baki RM73 & RM99
            e2 = T['rekaan'] - 0.05
            s, a = pop(t, T['rm73'] - 0.1, e2)
            if a:
                place(fr, money_card('RM73', 'baki tinggal', (255, 150, 150), w=470), W / 2 - 250, 330, s * 0.9, a)
            s, a = pop(t, T['rm99'] - 0.1, e2)
            if a:
                place(fr, money_card('RM99', 'baki tinggal', (255, 150, 150), w=470), W / 2 + 250, 330, s * 0.9, a)
            s, a = pop(t, T['rekaan'] - 0.05, T['n_in'])
            place(fr, p_real, W / 2, 300, s, a)
            # pakar: 100 ribu / 500 ribu / 1 juta
            for i, key in enumerate(('a100', 'a500', 'a1j')):
                s, a = pop(t, T[key] - 0.08, T['b_in'])
                place(fr, amounts[i], [250, W - 250, W / 2][i], [230, 230, 370][i], s, a)
            # bijak: dikumpul vs dijaga
            e3 = T['s_in']
            s, a = pop(t, T['dijaga'] - 0.1, e3)
            place(fr, p_jaga, W / 2 - 40, 240, s, a)
            s, a = pop(t, T['dikumpul'] - 0.1, e3)
            place(fr, p_kumpul, W / 2 + 80, 380, s, a)
            # gold bar sizes
            e4 = T['risiko'] - 0.05
            for i, key in enumerate(('g100', 'g250', 'g1k')):
                s, a = pop(t, T[key] - 0.08, e4, 0.3)
                place(fr, bars[i], [190, W / 2, W - 220][i], [330, 310, 290][i], s, a, rot=[-8, 0, 8][i])
            s, a = pop(t, T['ikut'] - 0.1, e4)
            place(fr, p_ikut, W / 2, 520, s, a)
            # risk + faham
            e5 = T['bina'] - 0.05
            s, a = pop(t, T['risiko'], e5)
            place(fr, p_risk, W / 2, 240, s, a)
            s, a = pop(t, T['faham'], e5)
            place(fr, p_faham, W / 2, 380, s, a)
            # bina vs lindung
            e6 = T['kalau2'] - 0.05
            s, a = pop(t, T['bina'] + 0.2, e6)
            place(fr, p_bina, W / 2 - 40, 240, s, a)
            s, a = pop(t, T['lindung'] - 0.1, e6)
            place(fr, p_lindung, W / 2 + 40, 380, s, a)
            # closing reminder: 100 ribu / 1 juta again, then jangan tunggu
            for i, key in enumerate(('a100b', 'a1jb')):
                s, a = pop(t, T[key] - 0.08, T['tunggu'] - 0.05)
                place(fr, amounts[[0, 2][i]], [W / 2 - 200, W / 2 + 200][i], 300, s, a)
            s, a = pop(t, T['tunggu'], T['bantu'] - 0.05)
            place(fr, p_tunggu, W / 2, 300, s, a)
            # CTA
            e7 = base_dur - 0.02
            s, a = pop(t, T['bantu'], e7)
            place(fr, p_pg, W / 2, 240, s, a)
            s, a = pop(t, T['pg'] - 0.6, e7)
            place(fr, shine(p_cta, (t - T['pg']) / 0.6), W / 2, 380, s, a)
            place(fr, wm, W - 110, H - 300, 1, 0.9)
        for a0, a1, w in cap_win:
            if a0 <= t < a1:
                k = (t - a0) / 0.09
                place(fr, cap(w), W / 2, H * 0.80, 0.82 + 0.18 * back_out(min(1, k)) if k < 1 else 1, 1)
                break
        for o, z0, z1 in zip(offs[1:], ZOOM[:-1], ZOOM[1:]):
            if z0 != z1 and abs(t - o) < 0.05:
                fr.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(60 * (1 - abs(t - o) / 0.05)))))
        return fr, True

    if preview:
        shots = [('Hook', T['bank'] + 0.4), ('RM1.99 juta', T['hilang'] - 0.3), ('HILANG', T['hilang'] + 0.5),
                 ('Baki RM73 & RM99', T['rm99'] + 0.6), ('Bukan cerita rekaan', T['rekaan'] + 0.8),
                 ('Cutaway: berita + gambar', T['n_out'] - 0.5), ('100 ribu / 500 ribu / 1 juta', T['a1j'] + 0.4),
                 ('Cutaway: satu tempat', T['b_out'] - 0.4), ('Dijaga vs dikumpul', T['s_in'] - 0.3),
                 ('Cutaway: bank + emas', T['s_out'] - 0.4), ('100g / 250g / 1kg', T['ikut'] + 0.5),
                 ('Risiko & faham', T['bina'] - 0.3), ('Bina vs lindungi', T['kalau2'] - 0.3),
                 ('Ulang: 100 ribu / 1 juta', T['tunggu'] - 0.3), ('Jangan tunggu', T['bantu'] - 0.3), ('CTA', base_dur - 0.3), ('Outro', base_dur + 1.6)]
        tiles_ = []
        for label, t in shots:
            ov, has_base = overlay(t)
            fr = base_still(t) if has_base else Image.new('RGBA', (W, H), (0, 0, 0, 255))
            fr.alpha_composite(ov)
            tile = fr.convert('RGB').resize((360, 640), Image.LANCZOS)
            mm, ss = divmod(t, 60)
            t2 = Image.new('RGB', (360, 684), (24, 24, 30))
            t2.paste(tile, (0, 0))
            ImageDraw.Draw(t2).text((6, 662), f'{int(mm)}:{ss:04.1f}  {label}', font=font(F_B, 21), fill=(255, 255, 255), anchor='lm')
            tiles_.append(t2)
        cols = 9
        rows = math.ceil(len(tiles_) / cols)
        sheet = Image.new('RGB', (cols * 372 + 12, rows * 696 + 12), (24, 24, 30))
        for i, tl in enumerate(tiles_):
            sheet.paste(tl, (12 + (i % cols) * 372, 12 + (i // cols) * 696))
        sheet.save(os.path.join(OUT, 'preview_storyboard.jpg'), quality=90)
        print('preview ok; segments', len(SEGS), 'base', round(base_dur, 2), 'total', round(total, 2))
        return

    fdir = os.path.join(OUT, 'frames')
    os.makedirs(fdir, exist_ok=True)
    for fi in range(int(round(total * FPS))):
        ov, _ = overlay(fi / FPS)
        ov.save(os.path.join(fdir, f'f{fi:05d}.png'), compress_level=1)
    write_sfx(total, pops, whooshes, os.path.join(OUT, 'sfx.wav'))
    final = os.path.join(OUT, 'JanganSimpanDalamBank_AzlanEza.mp4')
    composite(os.path.join(OUT, 'base.mov'), fdir, os.path.join(OUT, 'sfx.wav'), total, final,
              music=MUSIC if os.path.exists(MUSIC) else None, music_ss=MUSIC_SS, music_db=MUSIC_DB, music_tempo=MUSIC_TEMPO)
    print('done', final)


if __name__ == '__main__':
    main()
