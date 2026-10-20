#!/usr/bin/env python3
"""Video 7: 'Bonus tahunan dah jadi harta?' (in-car selfie) in the Azlan & Eza style.

python3 build_v7.py --preview         -> storyboard stills (with TikTok safe-zone guides)
python3 build_v7.py --audio-preview   -> voice + sfx + music mix only
python3 build_v7.py                   -> full render
"""
import importlib.util, json, math, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_VS = os.path.join(HERE, '..')
WORK = os.path.join(HERE, '..', 'work', 'v7')   # raw footage, photos, licensed music (not in git)
ASSETS = os.path.join(HERE, '07_assets')
sys.path.insert(0, REPO_VS)
import numpy as np
import build as B
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
money_card, warn_icon, NAVY_C, ALERT = V5.money_card, V5.warn_icon, V5.NAVY_C, V5.ALERT
arrow_icon = V6.arrow_icon

RAW = os.environ.get('RAW', os.path.join(WORK, 'raw.mp4'))
IMG1 = os.path.join(WORK, 'img1.jpg')   # stacks of RM notes in hand
IMG2 = os.path.join(WORK, 'img2.jpg')   # Public Gold staff with a large gold bar (converted from iPhone ProRAW)
IMG3 = os.path.join(WORK, 'img3.jpg')   # BH Online screenshot: BNM governor, ~half can't raise RM1,000 for emergencies
CREDIT3 = 'Sumber: BH Online, 28 Okt 2023'
OUT = os.environ.get('OUT', os.path.join(WORK, 'out'))
MASK = os.path.join(REPO_VS, 'videos', '04_assets', 'facemask.png')    # same in-car setup as video 4
GRADE = open(os.path.join(REPO_VS, 'videos', '04_assets', 'grade_D.txt')).read().strip()
RELIGHT = "eq=brightness=0.06:gamma=1.12:saturation=1.04,colorbalance=rm=0.02:bm=-0.015"
MUSIC = os.path.join(WORK, 'music.m4a')
# Music: video 4's stock track "Positive Hopeful Acoustic Guitar Live Strum" (Descript/Audioblocks), two copies
# crossfaded to 172.7s (Descript AI credits ran out before a new track could be picked).
MUSIC_SS, MUSIC_DB, MUSIC_TEMPO = 0.0, -15.0, 1.0
os.makedirs(OUT, exist_ok=True)

CUES = [
    (1.910, 7.790, "Tak lama lagi, penjawat awam dan swasta akan menerima bonus tahunan."),
    (9.210, 13.270, "Ada yang terima sampai dua, tiga kali dalam setahun."),
    (14.710, 21.990, "Alhamdulillah, tapi persoalan yang perlu dijawab dengan jujur adalah"),
    (22.050, 26.730, "berapa banyak daripada bonus tahunan tersebut yang dah bertukar menjadi harta?"),
    (29.130, 35.030, "Kalau dah kerja 15~4 tahun, bonus sepanjang 15~4 tahun sepatutnya dah"),
    (35.090, 38.210, "jadi aset bernilai tinggi untuk masa tua."),
    (39.430, 44.630, "Kalau boleh simpan RM1,000~3 setahun, hasil daripada bonus, selepas 15~4"),
    (44.670, 46.790, "tahun dah ada RM15,000~5"),
    (47.250, 50.930, "Dah boleh nak tunaikan haji bagi yang beragama Islam."),
    (52.490, 59.150, "Tapi hakikatnya, ramai yang jadikan bonus tahunan sebagai kunci untuk"),
    (59.230, 61.410, "hanya berbelanja tanpa menabung."),
    (62.670, 67.810, "Mungkin sekarang tak nampak kenapa tabungan itu sangat penting."),
    (70.602, 75.582, "Tapi satu hari nanti bila dah bersara, masa itulah baru nak"),
    (75.642, 81.242, "sedar betapa pentingnya tabungan di usia muda dikala sudah senja."),
    (82.682, 85.422, "Statistik yang pernah dikeluarkan oleh Bank Negara"),
    (85.882, 88.082, "bukanlah spekulasi semata-mata."),
    (91.110, 96.310, "Ia adalah hakikat sebenar rakyat negara ini dalam kedudukan kewangan"),
    (98.954, 103.214, "Jangan jadikan penyesalan sebagai zikir di usia tua"),
    (105.802, 111.282, "Bertindak sekarang supaya kita senang dan tenang bila tiba masa untuk"),
    (111.342, 114.122, "kita berehat dan nikmati kehidupan."),
    (115.742, 121.942, "Jadikan bonus tahunan sebagai booster untuk kita tambah simpanan dan harta."),
    (123.422, 127.642, "Itu yang terbaik untuk diri kita dan keluarga kita di masa hadapan"),
    (131.878, 137.818, "Semoga tahun 2026~6 menjadi turning point untuk hidup mampu berubah kepada"),
    (137.918, 143.818, "lebih baik dengan adanya simpanan tambahan menggunakan bonus tahunan."),
    (148.146, 149.685, "Yang muda pula macam mana?"),
    (153.566, 158.546, "Belajarlah dari pengalaman mereka yang berusia tapi tak ada simpanan"),
    (163.846, 168.606, "Jadikan ia inspirasi untuk kita tidak berada dalam keadaan"),
    (168.646, 171.346, "yang sama bila dah tua nanti."),
]
B.SYL.update({'semata-mata': 5, 'booster': 2, 'turning': 2, 'point': 1, 'haji': 2})


def build_segs():
    regs = json.load(open(os.path.join(ASSETS, 'edl_all.json')))['regs']
    keep = [[max(0, a - 0.08), b + 0.10] for a, b in regs if b > 0.15 and a < 172.5]
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
    x, y = (1080 - cw) / 2, min(max(0.45 * 1920 - ch / 2, 0), 1920 - ch)
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
def photo_frame(img, w, radius=28, border=12):
    h = int(w * img.height / img.width)
    ph = img.resize((w, h), Image.LANCZOS).convert('RGBA')
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius, fill=255)
    ph.putalpha(m)
    fr = rounded((w + 2 * border, h + 2 * border), radius + border, (255, 255, 255, 255))
    fr.alpha_composite(ph, (border, border))
    return with_shadow(fr, 20, 10, 0.4)


def calc_card(p):
    """RM1,000 x 15 tahun = RM15,000 (as spoken), then 'boleh tunaikan haji'."""
    cw, ch = 900, 800
    im = rounded((cw, ch), 48, NAVY_C)
    d = ImageDraw.Draw(im)
    d.text((cw / 2, 80), 'SIMPAN DARI BONUS', font=font(F_XB, 54), fill=(255, 255, 255, 255), anchor='mm')
    rows = [('RM1,000', 'setahun'), ('x 15', 'tahun')]
    for i, (a, b) in enumerate(rows):
        k = ease_out((p - i * 0.2) / 0.3)
        if k <= 0:
            continue
        y = 190 + i * 140
        d.rounded_rectangle([60, y, cw - 60, y + 115], 30, fill=(30, 33, 52, int(255 * k)))
        d.text((110, y + 58), a, font=font(F_XB, 64), fill=(255, 255, 255, int(255 * k)), anchor='lm')
        d.text((cw - 110, y + 58), b, font=font(F_B, 40), fill=(170, 172, 190, int(255 * k)), anchor='rm')
    if p > 0.45:
        k = ease_out((p - 0.45) / 0.3)
        val = int(round(15000 * k / 100.0)) * 100
        d.line([(60, 500), (cw - 60, 500)], fill=(80, 84, 110, 255), width=4)
        d.text((cw / 2, 590), f'RM{val:,}', font=font(F_XB, 120), fill=GOLD_L + (255,), anchor='mm')
    if p > 0.8:
        k = ease_out((p - 0.8) / 0.15)
        d.rounded_rectangle([110, 680, cw - 110, 760], 40, fill=GOLD + (int(255 * k),))
        d.text((cw / 2, 720), 'boleh tunaikan haji', font=font(F_XB, 40), fill=(30, 22, 10, int(255 * k)), anchor='mm')
    return with_shadow(im, 28, 16, 0.4)


def bh_card(p, head, photo):
    cw = 940
    pw = cw - 80
    hh = int(pw * head.height / head.width)
    gh = int(pw * photo.height / photo.width)
    ch = 120 + hh + 20 + gh + 130
    im = rounded((cw, ch), 44, NAVY_C)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([40, 36, 300, 96], 30, fill=ALERT + (255,))
    d.text((170, 66), 'STATISTIK BNM', font=font(F_XB, 30), fill=(255, 255, 255, 255), anchor='mm')
    k = ease_out(min(1, max(0, p) / 0.3))
    for img, y, hgt in ((head, 120, hh), (photo, 120 + hh + 20, gh)):
        src = img.resize((pw, hgt), Image.LANCZOS).convert('RGBA')
        m = Image.new('L', src.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, pw - 1, hgt - 1], 22, fill=int(255 * k))
        src.putalpha(m)
        im.alpha_composite(src, (40, y))
    y = 120 + hh + 20 + gh
    d.text((cw - 50, y + 14), CREDIT3, font=font(F_B, 22), fill=(150, 154, 180, int(255 * k)), anchor='ra')
    kk = ease_out((p - 0.4) / 0.3)
    if kk > 0:
        d.text((cw / 2, y + 80 + (1 - kk) * 16), 'bukan spekulasi', font=font(F_XB, 46),
               fill=GOLD_L + (int(255 * kk),), anchor='mm')
    return with_shadow(im, 28, 16, 0.4)


def booster_card(p, photo):
    cw = 920
    pw = 560
    ph_h = int(pw * photo.height / photo.width)
    ch = 150 + ph_h + 190
    im = rounded((cw, ch), 48, NAVY_C)
    d = ImageDraw.Draw(im)
    d.text((cw / 2, 75), 'BONUS = BOOSTER', font=font(F_XB, 64), fill=GOLD_L + (255,), anchor='mm')
    k = back_out(min(1, max(0, p) / 0.35))
    if k > 0.02:
        fr = photo_frame(photo, int(pw * k), 26, 10)
        im.alpha_composite(fr, (int(cw / 2 - fr.width / 2), int(140 + ph_h / 2 - fr.height / 2)))
    for i, txt in enumerate(('+ simpanan', '+ harta')):
        kk = ease_out((p - 0.4 - i * 0.15) / 0.25)
        if kk > 0:
            x = cw / 2 - 210 + i * 420
            d.rounded_rectangle([x - 180, ch - 160, x + 180, ch - 70], 45, fill=GOLD + (int(255 * kk),))
            d.text((x, ch - 115), txt, font=font(F_XB, 48), fill=(30, 22, 10, int(255 * kk)), anchor='mm')
    return with_shadow(im, 28, 16, 0.4)


def quote_card(text_lines, w=900):
    f = font(F_XB, 60)
    lh = 80
    h = 110 + lh * len(text_lines) + 30
    im = rounded((w, h), 40, (16, 18, 34, 235))
    d = ImageDraw.Draw(im)
    d.text((34, 4), '“', font=font(F_XB, 90), fill=GOLD + (255,))
    for i, (t, col) in enumerate(text_lines):
        d.text((w / 2, 110 + i * lh), t, font=f, fill=col + (255,), anchor='mm')
    return with_shadow(im, 20, 10, 0.45)


def cash_card(p, photo):
    cw = 900
    pw = 640
    ph_h = int(pw * photo.height / photo.width)
    ch = 150 + ph_h + 70
    im = rounded((cw, ch), 48, NAVY_C)
    d = ImageDraw.Draw(im)
    d.text((cw / 2, 80), 'BONUS TAHUNAN', font=font(F_XB, 64), fill=GOLD_L + (255,), anchor='mm')
    k = back_out(min(1, max(0, p) / 0.35))
    if k > 0.02:
        fr = shine(photo_frame(photo, int(pw * k), 26, 10), (p - 0.3) / 0.6)
        im.alpha_composite(fr, (int(cw / 2 - fr.width / 2), int(140 + ph_h / 2 - fr.height / 2)))
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

    gold_words = {'harta', 'aset', 'simpanan', 'tabungan', 'menabung', 'booster', 'tenang', 'senang', 'bonus'}
    red_words = {'penyesalan', 'berbelanja', 'tanpa'}
    cap_cache = {}

    def cap(word):
        if word not in cap_cache:
            num = word[:1].isdigit() or word[:2] == 'RM'
            disp = word if num or word in ('Bank', 'Negara', 'Islam') else word.lower()
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
    cash_img = Image.open(IMG1).convert('RGB')
    staff = Image.open(IMG2).convert('RGB')
    raw3 = Image.open(IMG3).convert('RGB')
    head3, photo3 = raw3.crop((0, 215, 1290, 1080)), raw3.crop((0, 1300, 1290, 2060))
    h1 = text_sprite('BONUS TAHUNAN', 112, GOLD_L, GOLD, stroke=5, stroke_col=(60, 40, 10))
    h2 = text_sprite('DAH JADI HARTA?', 104, (255, 255, 255), (232, 232, 240))
    p_23 = fit_pill('Ada yang terima 2-3 kali setahun', size=52)
    p_alh = fit_pill('Alhamdulillah', icon=check_icon(60), size=56)
    p_q = fit_pill('Berapa banyak dah jadi HARTA?', icon=warn_icon(60), size=52, bg=(232, 190, 92, 255))
    qmark = text_sprite('?', 260, GOLD_L, GOLD, stroke=8, stroke_col=(60, 40, 10))
    p_15 = fit_pill('Kerja 15 tahun = bonus 15 tahun', size=52)
    p_aset = fit_pill('Sepatutnya dah jadi aset untuk masa tua', icon=arrow_icon(60), size=48, bg=(232, 190, 92, 255))
    p_kunci = fit_pill('Bonus = kunci berbelanja', icon=x_icon(60), size=54)
    p_tanpa = fit_pill('tanpa menabung', icon=x_icon(60), size=54)
    p_nampak = fit_pill('Sekarang mungkin tak nampak...', size=52)
    p_sedar = fit_pill('Bila bersara baru sedar', icon=warn_icon(60), size=54, bg=(232, 190, 92, 255))
    q_zikir = quote_card([('Jangan jadikan penyesalan', (255, 255, 255)), ('sebagai zikir di usia tua', GOLD_L)])
    p_act = fit_pill('Bertindak sekarang', icon=check_icon(60), size=56, bg=(232, 190, 92, 255))
    p_rest = fit_pill('Senang & tenang bila berehat', size=52)
    p_fam = fit_pill('Terbaik untuk diri & keluarga', icon=check_icon(60), size=52, bg=(232, 190, 92, 255))
    t2026 = text_sprite('2026', 170, GOLD_L, GOLD, stroke=6, stroke_col=(60, 40, 10))
    t_turn = text_sprite('TURNING POINT', 96, (255, 255, 255), (232, 232, 240))
    p_muda = fit_pill('Yang muda pula macam mana?', icon=warn_icon(60), size=54)
    p_ajar = fit_pill('Belajar dari pengalaman', icon=check_icon(60), size=54)
    p_sama = fit_pill('Jangan berada dalam keadaan sama', icon=x_icon(60), size=50, bg=(232, 190, 92, 255))
    logo_c, logo_w = load_logos()
    wm = logo_w.resize((150, int(150 * logo_w.height / logo_w.width)), Image.LANCZOS)
    paper = paper_texture(W, H)

    T0_M_IN, T0_M_OUT = wt('bonus') - 0.1, cue_t(1) - 0.05
    T = {'bonus': wt('bonus'), 'ada': cue_t(1), 'alh': cue_t(2), 'berapa': cue_t(3), 'harta': wt('harta'),
         'kerja15': cue_t(4), 'aset': cue_t(5),
         'm_in': T0_M_IN, 'm_out': T0_M_OUT, 'c_in': cue_t(6) - 0.05, 'c_out': cue_t(8, True) + 0.2,
         'hakikat': cue_t(9), 'tanpa': wt('tanpa'), 'mungkin': cue_t(11), 'bersara': cue_t(12),
         'b_in': cue_t(14) - 0.05, 'b_out': cue_t(16, True) + 0.2,
         'zikir': cue_t(17), 'act': cue_t(18), 'rehat': wt('berehat'),
         'k_in': cue_t(20) - 0.05, 'k_out': cue_t(20, True) + 0.25,
         'fam': cue_t(21), 'y2026': wt('2026'), 'turn': wt('turning'), 'muda': cue_t(24), 'ajar': cue_t(25),
         'sama': cue_t(26)}
    pops = [T[k] for k in ('bonus', 'ada', 'alh', 'berapa', 'kerja15', 'aset', 'hakikat', 'tanpa', 'mungkin',
                           'bersara', 'zikir', 'act', 'rehat', 'fam', 'y2026', 'turn', 'muda', 'ajar', 'sama')]
    whooshes = [(T['harta'] - 0.15, 0.4, 0.22)] + [(T[k + '_in'] - 0.12, 0.35, 0.18) for k in 'mcbk'] + \
               [(T[k + '_out'] - 0.15, 0.35, 0.18) for k in 'mcbk'] + [(base_dur - 0.15, 0.5, 0.22)]

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
        for a_, b_, kind in ((T['m_in'], T['m_out'], 'm'), (T['c_in'], T['c_out'], 'c'), (T['b_in'], T['b_out'], 'b'), (T['k_in'], T['k_out'], 'k')):
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
            card = {'m': lambda q: cash_card(q, cash_img), 'c': calc_card, 'b': lambda q: bh_card(q, head3, photo3), 'k': lambda q: booster_card(q, staff)}[kind](pr)
            sc = min(0.9, (B.TT_BOTTOM - 260) / card.height)
            place(fr, card, B.TT_CENTER_X, 170 + card.height * sc / 2 + (1 - k_in) * 100, sc * (1.1 - 0.1 * k_in), a)
        else:
            # HOOK: BONUS TAHUNAN / DAH JADI HARTA? + cash photo
            e0 = T['ada'] - 0.05
            s, a = pop(t, 0.03, e0, 0.28, 0.12)
            place(fr, h1, B.TT_CENTER_X + 20, 230, s, a, rot=-3)
            s, a = pop(t, 0.25, e0, 0.28, 0.12)
            place(fr, h2, B.TT_CENTER_X + 20, 350, s, a, rot=-3)
            s, a = pop(t, T['ada'], T['alh'] - 0.05)
            place(fr, p_23, B.TT_CENTER_X, 260, s, a)
            s, a = pop(t, T['alh'], T['berapa'] - 0.05)
            place(fr, p_alh, B.TT_CENTER_X - 120, 260, s, a)
            e1 = T['kerja15'] - 0.05
            s, a = pop(t, T['berapa'] + 0.2, e1, 0.3)
            place(fr, p_q, B.TT_CENTER_X, 260, s, a)
            place(fr, qmark, B.TT_CENTER_X + 300, 470, s * 0.8, a, rot=10 * math.sin(t * 5))
            two(fr, t, p_15, T['kerja15'] + 0.3, p_aset, T['aset'], T['c_in'])
            two(fr, t, p_kunci, T['hakikat'] + 1.0, p_tanpa, T['tanpa'] - 0.1, T['mungkin'] - 0.05)
            two(fr, t, p_nampak, T['mungkin'], p_sedar, T['bersara'], T['b_in'])
            s, a = pop(t, T['zikir'], T['act'] - 0.05, 0.3)
            place(fr, q_zikir, B.TT_CENTER_X, 320, s, a)
            two(fr, t, p_act, T['act'], p_rest, T['rehat'] - 0.3, T['k_in'])
            s, a = pop(t, T['fam'], T['y2026'] - 0.1)
            place(fr, p_fam, B.TT_CENTER_X, 280, s, a)
            e2 = T['muda'] - 0.05
            s, a = pop(t, T['y2026'] - 0.1, e2, 0.3)
            if a:
                slam = 1 + 0.5 * max(0, 1 - (t - T['y2026'] + 0.1) / 0.18)
                place(fr, t2026, B.TT_CENTER_X, 260, s * slam if s >= 1 else s, a, rot=-3)
            s, a = pop(t, T['turn'] - 0.1, e2, 0.28)
            place(fr, t_turn, B.TT_CENTER_X, 410, s, a, rot=-3)
            s, a = pop(t, T['muda'], T['ajar'] - 0.05)
            place(fr, p_muda, B.TT_CENTER_X, 280, s, a)
            two(fr, t, p_ajar, T['ajar'], p_sama, T['sama'] + 0.6, base_dur - 0.02)
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
        shots = [('Hook', T['bonus'] - 0.5), ('Cutaway: bonus (gambar 1)', T['m_out'] - 0.4), ('2-3 kali setahun', T['alh'] - 0.3), ('Dah jadi harta?', T['kerja15'] - 0.3),
                 ('15 tahun -> aset', T['c_in'] - 0.3), ('Cutaway: RM15,000', T['c_out'] - 0.5),
                 ('Kunci berbelanja', T['mungkin'] - 0.3), ('Bila bersara', T['b_in'] - 0.3),
                 ('Cutaway: BH / BNM', T['b_out'] - 0.5), ('Penyesalan', T['act'] - 0.3),
                 ('Bertindak sekarang', T['k_in'] - 0.3), ('Cutaway: booster', T['k_out'] - 0.5),
                 ('Diri & keluarga', T['y2026'] - 0.3), ('2026 turning point', T['muda'] - 0.3),
                 ('Yang muda?', T['ajar'] - 0.3), ('Penutup', base_dur - 0.4), ('Outro', base_dur + 1.6)]
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
    final = os.path.join(OUT, 'BonusTahunan_AzlanEza.mp4')
    composite(os.path.join(OUT, 'base.mov'), fdir, os.path.join(OUT, 'sfx.wav'), total, final,
              music=MUSIC if os.path.exists(MUSIC) else None, music_ss=MUSIC_SS, music_db=MUSIC_DB, music_tempo=MUSIC_TEMPO)
    print('done', final)


if __name__ == '__main__':
    main()
