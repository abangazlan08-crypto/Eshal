#!/usr/bin/env python3
"""Video 9: '10 tahun bekerja, apa harta anda?' (studio) with 3D motion design, no zoom, Azlan & Eza style.

python3 build_v9.py --preview         -> storyboard stills (with TikTok safe-zone guides)
python3 build_v9.py --audio-preview   -> voice + sfx + music mix only
python3 build_v9.py                   -> full render
"""
import importlib.util, json, math, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_VS = os.path.join(HERE, '..')
WORK = os.path.join(HERE, '..', 'work', 'v9')   # raw footage, licensed music (not in git)
ASSETS = os.path.join(HERE, '09_assets')
sys.path.insert(0, REPO_VS)
import numpy as np
import build as B
import fx3d
from build import (W, H, FPS, OUTRO, RED, F_XB, F_B, Image, ImageDraw, ImageFilter, text_sprite, rounded,
                   with_shadow, place, pop, pill, fit_pill, check_icon, ease_out, back_out, font, paper_texture,
                   load_logos, outro_frame, write_sfx, composite, syllables)


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REPO_VS, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V3 = _load('v3', 'videos/03_konsisten_emas.py')
V5 = _load('v5', 'videos/05_jangan_simpan_dalam_bank.py')
V6 = _load('v6', 'videos/06_kenapa_china_beli_emas.py')
x_icon, shine, GOLD, GOLD_L = V3.x_icon, V3.shine, V3.GOLD, V3.GOLD_L
warn_icon, NAVY_C, ALERT = V5.warn_icon, V5.NAVY_C, V5.ALERT
arrow_icon = V6.arrow_icon

RAW = os.environ.get('RAW', os.path.join(WORK, 'raw.mp4'))
OUT = os.environ.get('OUT', os.path.join(WORK, 'out'))
MASK = os.path.join(REPO_VS, 'videos', '03_assets', 'facemask.png')    # same studio as videos 3, 5, 6, 8
GRADE, RELIGHT = V3.GRADE, V3.RELIGHT
# Music: video 5's stock track "Cautious Search" (Descript/Audioblocks), two copies crossfaded (Descript AI credits are out).
MUSIC = os.path.join(WORK, "music.m4a")
MUSIC_SS, MUSIC_DB, MUSIC_TEMPO = 0.0, -16.0, 1.0
os.makedirs(OUT, exist_ok=True)

CUES = [
    (0.000, 3.180, "Gaji masuk setiap bulan tetapi selepas 10~3 tahun"),
    (3.200, 6.620, "bekerja, apa harta yang anda ada?"),
    (7.600, 12.460, "Maaf kalau soalan ini agak pedas, tetapi inilah realiti"),
    (12.540, 15.680, "yang ramai orang tak mahu hadapi."),
    (16.520, 20.460, "Setiap bulan kita bekerja keras untuk mendapatkan gaji."),
    (20.800, 26.600, "Tetapi setiap kali gaji masuk, duit itu hanya singgah sebentar dalam akaun"),
    (26.700, 29.560, "sebelum berpindah ke tangan orang lain."),
    (29.680, 34.780, "Bayar rumah, bayar kereta, bayar bil, beli barang dan macam-macam lagi."),
    (35.800, 42.320, "Akhirnya, selepas bertahun-tahun bekerja, kita hanya mampu menunjukkan slip gaji"),
    (42.400, 45.440, "sebagai bukti pernah menerima pendapatan."),
    (45.660, 50.840, "Tetapi di mana hasil daripada semua gaji yang pernah kita terima?"),
    (51.640, 56.020, "Sebab itulah guru saya selalu berpesan, Setiap kali menerima gaji,"),
    (56.400, 61.640, "jangan biarkan semuanya kekal dalam bentuk wang untuk dibelanjakan."),
    (62.500, 68.340, "Alihkan sebahagian daripada gaji anda kepada aset seperti emas."),
    (69.260, 70.440, "Tidak perlu tunggu kaya."),
    (70.960, 77.840, "Mulakan dulu dengan RM100~5 ataupun RM300~6 ataupun"),
    (77.900, 80.600, "RM500~6 mengikut kemampuan."),
    (81.820, 82.740, "Kenapa emas?"),
    (83.420, 90.340, "Kerana wang tunai sangat mudah untuk dibelanjakan, sedangkan emas"),
    (90.400, 95.960, "boleh membantu kita membina disiplin menyimpan untuk jangka panjang."),
    (96.020, 101.140, "Walaupun harga emas turun naik, setiap gram yang dikumpulkan"),
    (101.180, 103.820, "merupakan aset yang kita miliki."),
    (104.820, 109.940, "Pastikan juga simpanan kecemasan dan komitmen asas mencukupi"),
    (110.020, 111.900, "sebelum kita membeli emas."),
    (112.160, 116.760, "Ingat, bekerja selama 20~4 tahun tidak semestinya menjadikan"),
    (116.820, 122.520, "seseorang itu berharta jika setiap sen yang diperoleh habis dibelanjakan."),
    (122.840, 126.540, "Jangan hanya fokus kepada berapa banyak gaji yang masuk."),
    (127.220, 132.560, "Fokus juga kepada berapa banyak aset yang berjaya kita kumpulkan."),
    (132.740, 140.080, "Kerana yang menentukan kedudukan kewangan kita bukan sekadar berapa banyak wang"),
    (140.140, 146.580, "yang pernah kita peroleh, tetapi berapa banyak yang berjaya kita kekalkan."),
    (146.780, 151.380, "Gaji bulan ini cuba tukarkan sebahagiannya ke dalam bentuk emas."),
    (151.420, 155.720, "Jika anda mahu bermula menyimpan emas di Public Gold, boleh terus"),
    (155.780, 156.880, "klik sign up form di bawah."),
    (156.920, 158.920, "Insya-Allah saya akan bantu sebaiknya."),
]
B.SYL.update({'macam-macam': 4, 'bertahun-tahun': 6, 'sign': 1, 'up': 1, 'form': 1, 'Insya-Allah': 4,
              'Public': 2, 'Gold': 1})


def slow_amt(a, b):     # user: no zoom in this video
    return 0.0


def build_segs():
    regs = json.load(open(os.path.join(ASSETS, 'edl_all.json')))['regs']
    keep = [[max(0, a - 0.08), b + 0.10] for a, b in regs if b > 0.15 and a < 159.0]
    segs = []
    for a, b in sorted(keep):
        if segs and a - segs[-1][1] < 0.18:
            segs[-1][1] = max(segs[-1][1], b)
        else:
            segs.append([a, b])
    zoom, z = [], 1.0
    for i, (a, b) in enumerate(segs):
        zoom.append(1.0)          # user: no zoom-in (no punch-ins, no slow zoom)
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


def zoom_vf(z, amt, d):
    """Static punch z, plus a slow zoom-in of +amt over d seconds (fixed point near the face)."""
    if not amt:
        return vf_for(z)
    return (vf_for(z) + f",scale=w='1080*(1+{amt}*t/{d:.3f})':h='1920*(1+{amt}*t/{d:.3f})':eval=frame:flags=lanczos,"
            f"crop=1080:1920:(iw-1080)/2:(ih-1920)*0.40")


def graded_filter(z, amt=0.0, d=1.0):
    return (f"[0:v]{zoom_vf(z, amt, d)},fps={FPS},{GRADE},split[a][b];[b]{RELIGHT}[bb];[1:v]format=gray[m];"
            f"[bb][m]alphamerge[lit];[a][lit]overlay=format=auto,vignette=PI/4.6,unsharp=5:5:0.35,format=yuv420p[v]")


def render_base():
    parts = []
    for i, ((a, b), z) in enumerate(zip(SEGS, ZOOM)):
        d = b - a
        p = os.path.join(OUT, f'seg{i}.mov')
        af = f"aresample=48000,afade=t=in:d=0.03,afade=t=out:st={d-0.03:.3f}:d=0.03"
        amt = slow_amt(a, b)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a}', '-t', f'{d}', '-i', RAW, '-loop', '1', '-i', MASK,
                        '-filter_complex', graded_filter(z, amt, d) + f";[0:a]{af}[au]", '-map', '[v]', '-map', '[au]',
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
    a, b = SEGS[k]
    amt = slow_amt(a, b)
    z = ZOOM[k] * (1 + amt * (t - offs[k]) / (b - a)) if amt else ZOOM[k]
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{out2src(t)}', '-i', RAW, '-i', MASK,
                    '-filter_complex', graded_filter(z), '-map', '[v]', '-frames:v', '1', p], check=True)
    return Image.open(p).convert('RGBA')


# ---------------------------------------------------------------- 3D graphics helpers
_cache = {}


def bar3d(angle, size=520, rx=24.0):
    key = ('bar', int(angle) % 360, size, int(rx))
    if key not in _cache:
        if 'tex' not in _cache:
            _cache['tex'] = fx3d.bar_texture(font_path=F_XB)
        _cache[key] = fx3d.render_bar(int(angle) % 360, rx=rx, size=size, texture=_cache['tex'])
    return _cache[key]


def coin3d(angle, size=300, label='RM', rx=-8.0):
    key = ('coin', int(angle) % 360, size, label, int(rx))
    if key not in _cache:
        _cache[key] = fx3d.render_coin(int(angle) % 360, rx=rx, size=size, label=label, font_path=F_XB)
    return _cache[key]


def flip_place(fr, spr, cx, cy, t, t0, t1, axis='y', sway=3.0, dur_in=0.38, dur_out=0.2):
    """3D flip-in / flip-out with a gentle idle sway (no scaling)."""
    if t < t0 or t > t1:
        return
    if t < t0 + dur_in:
        k = back_out((t - t0) / dur_in, 1.3)
        ang, a = 88 * (1 - k), min(1, (t - t0) / dur_in * 2.2)
    elif t > t1 - dur_out:
        k = (t1 - t) / dur_out
        ang, a = -88 * (1 - k), k
    else:
        ang, a = sway * math.sin((t - t0) * 2.2), 1
    w = fx3d.warp3d(spr, rx=ang if axis == 'x' else 0, ry=ang if axis == 'y' else 0)
    place(fr, w, cx, cy, 1, a)


def paper_card_in(fr, card, t, a_, b_, paper):
    """Full-screen cutaway: paper fades in, card flips in around Y (no zoom)."""
    k_in, k_out = ease_out((t - a_) / 0.3), ease_out((b_ - t) / 0.2)
    a = min(k_in, k_out)
    bgp = paper.copy()
    bgp.putalpha(int(255 * a))
    fr.alpha_composite(bgp)
    sc = min(0.92, (B.TT_BOTTOM - 260) / card.height, 880 / card.width)
    if sc < 0.999:
        card = card.resize((int(card.width * sc), int(card.height * sc)), Image.LANCZOS)
    ang = 75 * (1 - k_in) if t - a_ < 0.3 else (-75 * (1 - k_out) if b_ - t < 0.2 else 2.5 * math.sin((t - a_) * 1.6))
    w = fx3d.warp3d(card, ry=ang)
    place(fr, w, B.TT_CENTER_X, 170 + card.height / 2, 1, a)


def payslip(w=470, h=320):
    im = rounded((w, h), 28, (250, 250, 252, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, 80], fill=(40, 46, 70, 255))
    d.rounded_rectangle([0, 0, w - 1, 90], 28, fill=(40, 46, 70, 255))
    d.text((32, 42), 'SLIP GAJI', font=font(F_XB, 36), fill=(255, 255, 255, 255), anchor='lm')
    for i, (a, b) in enumerate((('Gaji pokok', '••••'), ('Elaun', '••••'), ('Potongan', '- ••••'))):
        y = 120 + i * 50
        d.text((36, y), a, font=font(F_B, 26), fill=(70, 74, 90, 255), anchor='lm')
        d.text((w - 36, y), b, font=font(F_B, 26), fill=(70, 74, 90, 255), anchor='rm')
        d.line([(36, y + 28), (w - 36, y + 28)], fill=(225, 226, 232, 255), width=2)
    d.text((36, h - 50), 'Gaji bersih', font=font(F_XB, 30), fill=(30, 30, 40, 255), anchor='lm')
    d.text((w - 36, h - 50), 'RM ••••', font=font(F_XB, 30), fill=(30, 30, 40, 255), anchor='rm')
    return with_shadow(im, 20, 12, 0.4)


def quote_card(text_lines, w=900):
    lh = 70
    h = 110 + lh * len(text_lines) + 30
    im = rounded((w, h), 40, (16, 18, 34, 240))
    d = ImageDraw.Draw(im)
    d.text((34, 4), '“', font=font(F_XB, 90), fill=GOLD + (255,))
    for i, (t, col) in enumerate(text_lines):
        sz = 52
        while font(F_XB, sz).getlength(t) > w - 80:
            sz -= 2
        d.text((w / 2, 110 + i * lh), t, font=font(F_XB, sz), fill=col + (255,), anchor='mm')
    return with_shadow(im, 20, 10, 0.45)


def bar_cut_card(t_rel, lines):
    cw, ch = 900, 900
    im = rounded((cw, ch), 48, NAVY_C)
    d = ImageDraw.Draw(im)
    for i, (txt, sz, col) in enumerate(lines):
        d.text((cw / 2, 80 + i * 78), txt, font=font(F_XB, sz), fill=col + (255,), anchor='mm')
    bar = bar3d(50 * math.sin(t_rel * 1.1), size=720)
    im.alpha_composite(bar, (int(cw / 2 - bar.width / 2), int(560 - bar.height / 2)))
    return with_shadow(im, 28, 16, 0.4)


def compare_card(p, t_rel):
    cw, ch = 920, 860
    im = rounded((cw, ch), 48, NAVY_C)
    d = ImageDraw.Draw(im)
    d.text((cw / 2, 70), 'KENAPA EMAS?', font=font(F_XB, 60), fill=GOLD_L + (255,), anchor='mm')
    cols = [('WANG TUNAI', 'mudah', 'dibelanjakan', (255, 140, 150), False),
            ('EMAS', 'disiplin', 'jangka panjang', GOLD, True)]
    for i, (title, a, b, col, good) in enumerate(cols):
        k = ease_out((p - i * 0.3) / 0.3)
        if k <= 0:
            continue
        box = rounded((410, 640), 36, (30, 33, 52, 255))
        bd = ImageDraw.Draw(box)
        bd.rounded_rectangle([30, 26, 380, 116], 30, fill=col + (255,))
        bd.text((205, 71), title, font=font(F_XB, 44), fill=(20, 20, 30, 255), anchor='mm')
        if good:
            c = coin3d(50 * math.sin(t_rel * 1.6), size=230, label='999')
            box.alpha_composite(c, (205 - c.width // 2, 165))
        else:
            for j in range(3):
                bd.rounded_rectangle([90 + j * 22, 190 + j * 30, 320 + j * 22, 300 + j * 30], 16,
                                     fill=(120, 190, 140, 255), outline=(70, 130, 90, 255), width=4)
                bd.text((205 + j * 22, 245 + j * 30), 'RM', font=font(F_XB, 40), fill=(40, 90, 55, 255), anchor='mm')
        bd.text((205, 450), a, font=font(F_XB, 46), fill=(255, 255, 255, 255), anchor='mm')
        bd.text((205, 510), b, font=font(F_B, 38), fill=(190, 192, 210, 255), anchor='mm')
        ic = check_icon(70) if good else x_icon(70)
        box.alpha_composite(ic, (205 - 35, 560))
        w = fx3d.warp3d(box, ry=80 * (1 - k))
        im.alpha_composite(w, (int(40 + i * 450 + 205 - w.width / 2), int(450 - w.height / 2)))
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

    gold_words = {'harta', 'aset', 'emas', 'disiplin', 'kekalkan', 'berharta', 'simpanan'}
    red_words = {'pedas', 'realiti', 'habis', 'dibelanjakan'}
    cap_cache = {}

    def cap(word):
        if word not in cap_cache:
            num = word[:1].isdigit() or word[:2] == 'RM'
            disp = word if num or word in ('Public', 'Gold') else word.lower()
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

    def fitw(spr, maxw=860):
        return spr if spr.width <= maxw else spr.resize((maxw, int(spr.height * maxw / spr.width)), Image.LANCZOS)

    # sprites
    h1 = fitw(fx3d.extrude_text('10 TAHUN BEKERJA', 96, F_XB, depth=14))
    h2 = fitw(fx3d.extrude_text('APA HARTA ANDA?', 104, F_XB, top=(255, 255, 255), bot=(220, 222, 232),
                           side=(70, 74, 100), outline=(30, 30, 45), depth=14))
    q3d = fx3d.extrude_text('?', 240, F_XB, depth=22)
    p_pedas = fit_pill('Maaf kalau soalan ni pedas', icon=warn_icon(60), size=52)
    p_real = fit_pill('Realiti yang ramai tak mahu hadapi', size=48, bg=(232, 190, 92, 255))
    p_singgah = fit_pill('Duit hanya singgah sebentar', icon=warn_icon(60), size=52)
    bills = [fit_pill(t, size=50) for t in ('Bayar rumah', 'Bayar kereta', 'Bayar bil', 'Beli barang')]
    slip = payslip()
    p_bukti = fit_pill('Satu-satunya bukti: slip gaji?', size=50)
    p_mana = fit_pill('Di mana hasil semua gaji?', icon=warn_icon(60), size=52, bg=(232, 190, 92, 255))
    q_guru = quote_card([('Setiap kali terima gaji, jangan biarkan', (255, 255, 255)),
                         ('semuanya kekal dalam bentuk wang', GOLD_L)])
    p_kaya = fit_pill('Tak perlu tunggu kaya', icon=check_icon(60), size=54)
    amt_lbl = {k: fit_pill(k, size=50, bg=(232, 190, 92, 255)) for k in ('RM100', 'RM300', 'RM500')}
    p_ikut = fit_pill('ikut kemampuan', size=46)
    kenapa = fitw(fx3d.extrude_text('KENAPA EMAS?', 110, F_XB, depth=16))
    p_kecemasan = fit_pill('Pastikan simpanan kecemasan & komitmen asas cukup dulu', icon=warn_icon(60), size=40)
    t20 = fitw(fx3d.extrude_text('20 TAHUN BEKERJA', 96, F_XB, depth=14))
    p_tak = fit_pill('tak semestinya berharta', icon=x_icon(60), size=54)
    p_masuk = fit_pill('Gaji yang masuk', size=56)
    p_aset = fit_pill('Aset yang berjaya dikumpul', icon=check_icon(60), size=52, bg=(232, 190, 92, 255))
    q_kekal = quote_card([('Bukan berapa banyak diperoleh,', (255, 255, 255)),
                          ('tapi berapa banyak dikekalkan', GOLD_L)])
    p_tukar = fit_pill('Tukar sebahagian gaji ke emas', icon=check_icon(60), size=50, bg=(232, 190, 92, 255))
    p_form = fit_pill('Klik sign up form di bawah', icon=arrow_icon(60, False, (232, 150, 40)), size=52)
    p_bantu = fit_pill('Saya akan bantu sebaiknya', icon=check_icon(60), size=52)
    logo_c, logo_w = load_logos()
    wm = logo_w.resize((150, int(150 * logo_w.height / logo_w.width)), Image.LANCZOS)
    paper = paper_texture(W, H)

    T = {'bekerja': wt('bekerja'), 'apa': wt('apa'), 'maaf': cue_t(2), 'realiti': wt('realiti'),
         'gaji_masuk': cue_t(5), 'singgah': wt('singgah'), 'rumah': wt('rumah'), 'kereta': wt('kereta'),
         'bil': wt('bil'), 'barang': wt('barang'), 'slip': wt('slip'), 'bukti': wt('bukti'), 'mana': cue_t(10),
         'guru': cue_t(11),
         'a_in': cue_t(13) - 0.05, 'a_out': cue_t(13, True) + 0.2,
         'kaya': cue_t(14), 'r100': wt('RM100'), 'r300': wt('RM300'), 'r500': wt('RM500'), 'ikut': wt('kemampuan'),
         'kenapa': cue_t(17),
         'c_in': cue_t(18) - 0.05, 'c_out': cue_t(21, True) + 0.2,
         'kecemasan': cue_t(22), 'y20': wt('20'), 'berharta': wt('berharta'),
         'fokus1': cue_t(26), 'fokus2': cue_t(27), 'kekal': cue_t(28),
         'tukar': cue_t(30), 'form': cue_t(32), 'bantu': cue_t(33)}
    pops = [T[k] for k in ('bekerja', 'apa', 'maaf', 'realiti', 'singgah', 'rumah', 'kereta', 'bil', 'barang',
                           'slip', 'mana', 'guru', 'kaya', 'r100', 'r300', 'r500', 'kenapa', 'kecemasan', 'y20',
                           'berharta', 'fokus1', 'fokus2', 'kekal', 'tukar', 'form', 'bantu')]
    whooshes = [(T['apa'] - 0.15, 0.4, 0.24)] + [(T[k + '_in'] - 0.12, 0.35, 0.18) for k in 'ac'] + \
               [(T[k + '_out'] - 0.15, 0.35, 0.18) for k in 'ac'] + [(base_dur - 0.15, 0.5, 0.22)]

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

    CX = B.TT_CENTER_X

    def overlay(t):
        fr = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        if t >= base_dur:
            return outro_frame(t - base_dur, int(t * FPS), logo_w), False
        if T['a_in'] <= t <= T['a_out']:
            pr = t - T['a_in']
            paper_card_in(fr, bar_cut_card(pr, [('ALIHKAN SEBAHAGIAN GAJI', 50, (255, 255, 255)),
                                                ('KEPADA ASET', 50, (255, 255, 255)),
                                                ('SEPERTI EMAS', 64, GOLD_L)]), t, T['a_in'], T['a_out'], paper)
        elif T['c_in'] <= t <= T['c_out']:
            pr = (t - T['c_in'] - 0.15) / max(0.1, T['c_out'] - T['c_in'] - 0.7)
            card = compare_card(pr, t - T['c_in'])
            if t > T['c_in'] + (T['c_out'] - T['c_in']) * 0.62:      # "setiap gram ... aset yang kita miliki"
                d = ImageDraw.Draw(card)
                d.rounded_rectangle([140, 780, 820, 860], 40, fill=GOLD + (255,))
                d.text((480, 820), 'setiap gram = aset milik kita', font=font(F_XB, 38), fill=(30, 22, 10, 255), anchor='mm')
            paper_card_in(fr, card, t, T['c_in'], T['c_out'], paper)
        else:
            # HOOK: 3D extruded titles flip down into place
            e0 = T['maaf'] - 0.05
            flip_place(fr, h1, CX + 20, 240, t, 0.03, e0, axis='x', sway=2)
            flip_place(fr, h2, CX + 20, 380, t, T['apa'] - 0.1, e0, axis='x', sway=2)
            e1 = T['gaji_masuk'] - 0.05
            flip_place(fr, p_pedas, CX, 250, t, T['maaf'], e1)
            flip_place(fr, p_real, CX + 20, 390, t, T['realiti'] - 0.1, e1)
            # gaji masuk -> singgah -> bills
            e2 = T['slip'] - 0.3
            if T['gaji_masuk'] <= t < e2:
                tc = t - T['gaji_masuk']
                c = coin3d(50 * math.sin(tc * 2.2), size=230)
                x = CX + 330 + (0 if t < T['singgah'] else min(1, (t - T['singgah']) / 1.2) * 260)
                place(fr, c, x, 470, 1, 1 if t < T['singgah'] + 0.9 else max(0, 1 - (t - T['singgah'] - 0.9) / 0.3))
            flip_place(fr, p_singgah, CX, 250, t, T['singgah'] - 0.1, T['rumah'] - 0.1)
            for i, key in enumerate(('rumah', 'kereta', 'bil', 'barang')):
                flip_place(fr, bills[i], CX - 200 + (i % 2) * 400, 250 + (i // 2) * 130, t, T[key] - 0.1, e2)
            # slip gaji in 3D (tilting), then "di mana hasil"
            e3 = T['guru'] - 0.05
            if T['slip'] - 0.2 <= t < T['mana'] - 0.05:
                k = ease_out((t - T['slip'] + 0.2) / 0.45)
                w = fx3d.warp3d(slip, rx=8 + 6 * math.sin(t * 1.5), ry=-18 + 70 * (1 - k) + 8 * math.sin(t * 1.1))
                place(fr, w, CX + 40, 405, 1, min(1, k * 1.5))
            flip_place(fr, p_bukti, CX, 650, t, T['bukti'] - 0.1, T['mana'] - 0.05, axis='x')
            flip_place(fr, p_mana, CX - 60, 260, t, T['mana'], e3)
            if T['mana'] <= t < e3:
                place(fr, fx3d.warp3d(q3d, ry=25 * math.sin((t - T['mana']) * 2.5)), CX + 300, 430, 1,
                      min(1, (t - T['mana']) / 0.3))
            flip_place(fr, q_guru, CX, 320, t, T['guru'] + 0.4, T['a_in'], axis='x')
            # after "alihkan" cutaway: RM100 / RM300 / RM500 as stacked 3D coins
            e4 = T['kenapa'] - 0.05
            flip_place(fr, p_kaya, CX, 230, t, T['kaya'], T['r100'] - 0.15)
            for i, key in enumerate(('r100', 'r300', 'r500')):
                t0 = T[key] - 0.1
                if t0 <= t < e4:
                    drop = ease_out(min(1, (t - t0) / 0.45))
                    x = CX - 280 + i * 280
                    y = 420 - (1 - drop) * 240
                    place(fr, coin3d(45 * math.sin((t - t0) * 2.0 + i), size=290, label=key[1:]), x, y, 1, min(1, (t - t0) / 0.2))
                    flip_place(fr, amt_lbl['RM' + key[1:]], x, 250, t, t0 + 0.15, e4, axis='x', sway=0)
            flip_place(fr, p_ikut, CX, 560, t, T['ikut'] - 0.1, e4, axis='x')
            flip_place(fr, kenapa, CX + 20, 300, t, T['kenapa'] - 0.05, T['c_in'], axis='x', sway=2)
            # after compare cutaway
            flip_place(fr, p_kecemasan, CX, 300, t, T['kecemasan'], T['y20'] - 0.2)
            e5 = T['fokus1'] - 0.05
            flip_place(fr, t20, CX + 20, 260, t, T['y20'] - 0.2, e5, axis='x', sway=2)
            flip_place(fr, p_tak, CX + 20, 410, t, T['berharta'] - 0.4, e5)
            e6 = T['kekal'] - 0.05
            flip_place(fr, p_masuk, CX, 250, t, T['fokus1'] + 0.4, e6)
            flip_place(fr, p_aset, CX + 20, 390, t, T['fokus2'] + 0.4, e6)
            flip_place(fr, q_kekal, CX, 320, t, T['kekal'] + 1.0, T['tukar'] - 0.05, axis='x')
            # CTA: spinning bar + pills
            e7 = base_dur - 0.02
            if T['tukar'] <= t < e7:
                tb = t - T['tukar']
                place(fr, bar3d(45 * math.sin(tb * 1.2), size=320), CX + 300, 660, 1, min(1, tb / 0.4))
            flip_place(fr, p_tukar, CX - 20, 250, t, T['tukar'] + 0.2, e7)
            flip_place(fr, p_form, CX - 20, 390, t, T['form'], e7)
            flip_place(fr, p_bantu, CX - 60, 520, t, T['bantu'], e7, axis='x')
            place(fr, wm, 95, 1010, 0.85, 0.85)
        for a0, a1, w in cap_win:
            if a0 <= t < a1:
                k = (t - a0) / 0.09
                place(fr, cap(w), W / 2, B.TT_CAPTION_Y, 0.82 + 0.18 * back_out(min(1, k)) if k < 1 else 1, 1)
                break
        return fr, True

    if '--demo' in sys.argv:
        # short low-res motion demo of the 3D section (coins -> bar cutaway), 15 fps, real graded footage
        t0, t1 = T['a_in'] - 0.6, T['kenapa'] + 1.2
        ddir = os.path.join(OUT, 'demo')
        os.makedirs(ddir, exist_ok=True)
        n = int((t1 - t0) * 15)
        for i in range(n):
            t = t0 + i / 15
            ov, has_base = overlay(t)
            fr = base_still(t) if has_base else Image.new('RGBA', (W, H), (0, 0, 0, 255))
            fr.alpha_composite(ov)
            fr.convert('RGB').resize((540, 960), Image.LANCZOS).save(os.path.join(ddir, f'd{i:04d}.jpg'), quality=85)
        a0 = out2src(t0)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '15', '-i', os.path.join(ddir, 'd%04d.jpg'),
                        '-c:v', 'libx264', '-crf', '24', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                        os.path.join(WORK, 'PREVIEW_3d_motion.mp4')], check=True)
        print('demo', t0, t1)
        return

    if preview:
        shots = [('Hook (3D teks)', T['apa'] + 0.7), ('Soalan pedas', T['gaji_masuk'] - 0.3),
                 ('Gaji singgah (syiling 3D)', T['singgah'] + 0.5), ('Bil (flip 3D)', T['barang'] + 0.6),
                 ('Slip gaji 3D', T['bukti'] + 0.4), ('Di mana hasil?', T['guru'] - 0.3), ('Pesan guru', T['a_in'] - 0.3),
                 ('Cutaway: bar emas 3D', T['a_out'] - 0.6), ('RM100/300/500 syiling 3D', T['kenapa'] - 0.3),
                 ('Kenapa emas?', T['c_in'] - 0.2), ('Cutaway: tunai vs emas', T['c_out'] - 0.5),
                 ('Simpanan kecemasan', T['y20'] - 0.4), ('20 tahun bekerja', T['fokus1'] - 0.3),
                 ('Masuk vs aset', T['kekal'] - 0.3), ('Dikekalkan', T['tukar'] - 0.3), ('CTA (bar 3D)', base_dur - 0.5),
                 ('Outro', base_dur + 1.6)]
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
    final = os.path.join(OUT, 'ApaHartaAnda_AzlanEza.mp4')
    composite(os.path.join(OUT, 'base.mov'), fdir, os.path.join(OUT, 'sfx.wav'), total, final,
              music=MUSIC if os.path.exists(MUSIC) else None, music_ss=MUSIC_SS, music_db=MUSIC_DB, music_tempo=MUSIC_TEMPO)
    print('done', final)


if __name__ == '__main__':
    main()
