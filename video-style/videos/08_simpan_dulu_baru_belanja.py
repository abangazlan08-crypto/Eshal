#!/usr/bin/env python3
"""Video 8: 'Bila ada duit, baru simpan' -> dapat gaji, simpan dulu, baru belanja (studio) in the Azlan & Eza style.

python3 build_v8.py --preview         -> storyboard stills (with TikTok safe-zone guides)
python3 build_v8.py --audio-preview   -> voice + sfx + music mix only
python3 build_v8.py                   -> full render
"""
import importlib.util, json, math, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_VS = os.path.join(HERE, '..')
WORK = os.path.join(HERE, '..', 'work', 'v8')   # raw footage, infographic, licensed music (not in git)
ASSETS = os.path.join(HERE, '08_assets')
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
IMG1 = os.path.join(WORK, 'img1.png')   # infographic: DAPAT GAJI / SIMPAN DULU / BARU BELANJA
OUT = os.environ.get('OUT', os.path.join(WORK, 'out'))
MASK = os.path.join(REPO_VS, 'videos', '03_assets', 'facemask.png')    # same studio as videos 3, 5, 6
GRADE, RELIGHT = V3.GRADE, V3.RELIGHT
# Music: video 6's stock track "Technological Documentary (Loop)" x3 (Descript/Audioblocks); Descript AI credits are out.
MUSIC = os.path.join(WORK, 'music.m4a')
MUSIC_SS, MUSIC_DB, MUSIC_TEMPO = 0.0, -16.0, 1.0
os.makedirs(OUT, exist_ok=True)

CUES = [
    (0.020, 2.100, "Bila ada duit, baru simpan."),
    (3.400, 8.900, "Inilah antara kesilapan kewangan yang paling ramai orang buat tanpa sedar."),
    (9.780, 11.260, "Kita bekerja bertahun-tahun."),
    (11.900, 16.460, "Gaji semakin meningkat tetapi simpanan masih di tahap yang sama."),
    (17.120, 21.420, "Kadang-kadang simpanan kecemasan untuk bertahan selama 3~2"),
    (21.480, 23.440, "bulan pun belum tentu cukup."),
    (24.600, 26.180, "Kenapa perkara ini berlaku?"),
    (27.060, 34.600, "Sebab kita sudah terbiasa dengan formula dapat gaji tolak belanja barulah simpan."),
    (35.200, 39.700, "Maksudnya setiap kali dapat gaji, kita bayar segala komitmen beli"),
    (39.800, 44.240, "apa yang kita mahu dan kalau ada baki barulah kita simpan."),
    (45.100, 48.900, "Masalahnya selalu memang tak akan ada baki."),
    (49.980, 56.360, "Sebab itulah kita perlu ubah cara mengurus duit kepada formula dapat"),
    (56.440, 59.840, "gaji tolak simpan baru belanja."),
    (60.900, 65.720, "Setiap kali kita dapat gaji, asingkan dahulu sekurang-kurangnya"),
    (65.860, 67.640, "10%~5 untuk simpanan."),
    (68.320, 74.900, "Kalau mampu tingkatkan kepada 20%~6 hingga 30%~6"),
    (75.300, 80.640, "Selebihnya barulah digunakan untuk membayar komitmen dan perbelanjaan harian."),
    (82.654, 86.033, "Tak perlu tunggu gaji besar untuk mula menabung."),
    (86.874, 91.774, "Kalau gaji RM2,000~5 mulakan dengan RM200~5"),
    (92.393, 95.714, "Kalau belum mampu, simpanlah mengikut kemampuan."),
    (96.574, 100.654, "Yang penting bina tabiat menyimpan secara konsisten."),
    (101.274, 104.714, "Sebab kita kena ingat kita tak selamanya mampu bekerja."),
    (105.274, 110.973, "Akan tiba masanya kita bersara, berhenti kerja atau mungkin diuji"),
    (111.014, 113.514, "dengan kehilangan sumber pendapatan."),
    (114.334, 118.533, "Ketika itu, apa yang akan membantu kita meneruskan kehidupan?"),
    (119.374, 123.454, "Sudah tentu simpanan dan aset yang kita bina sepanjang bekerja."),
    (124.473, 130.334, "Sebab itulah penting untuk kita mempunyai tabung kecemasan sekurang-kurangnya"),
    (130.413, 134.154, "3~2 hingga 6~3 bulan perbelanjaan."),
    (134.673, 140.094, "Kemudian usaha tingkatkan sehingga 12~4 bulan."),
    (140.534, 144.793, "Kita usahakan supaya sekurang-kurangnya kita tak menyusahkan orang"),
    (144.834, 147.394, "lain apabila ditimpa kesusahan."),
    (148.014, 154.173, "Kalau sudah berusaha dan membuat persediaan tetapi masih diuji, itu takdir."),
    (154.574, 158.574, "Namun kalau langsung tidak membuat persediaan sedangkan"),
    (158.613, 161.034, "kita mampu, itu soal tadbir."),     # Descript heard "takbir"; user confirmed "tadbir"
    (161.934, 164.934, "Ingat, jangan tunggu duit lebih baru nak menyimpan."),
    (165.553, 170.034, "Sebaliknya simpan dahulu dan belanjakan selebihnya."),
    (170.714, 175.374, "Kerana masa depan kewangan kita bukan ditentukan oleh"),
    (175.414, 177.714, "berapa besar gaji semata-mata."),
    (178.254, 183.974, "Tetapi bagaimana kita menguruskan setiap ringgit yang diterima."),
]
B.SYL.update({'bertahun-tahun': 6, 'kadang-kadang': 6, 'sekurang-kurangnya': 7, 'semata-mata': 5})

# slow zoom-in (+8%) on emphasis moments (source-time ranges)
SLOW = [(0.0, 9.0), (45.0, 49.0), (101.0, 124.0), (148.0, 161.5), (170.5, 184.0)]


def slow_amt(a, b):
    mid = (a + b) / 2
    return 0.08 if any(s <= mid <= e for s, e in SLOW) else 0.0


def build_segs():
    regs = json.load(open(os.path.join(ASSETS, 'edl_all.json')))['regs']
    keep = [[max(0, a - 0.08), b + 0.10] for a, b in regs if b > 0.15 and a < 184.0]
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


# ---------------------------------------------------------------- graphics
def formula_card(p, wrong=True):
    """GAJI - BELANJA = SIMPAN (wrong)  /  GAJI - SIMPAN = BELANJA (right)."""
    cw, ch = 920, 640
    im = rounded((cw, ch), 48, NAVY_C)
    d = ImageDraw.Draw(im)
    d.text((cw / 2, 80), 'FORMULA BIASA' if wrong else 'FORMULA BETUL', font=font(F_XB, 52),
           fill=(255, 150, 150, 255) if wrong else (GOLD_L + (255,)), anchor='mm')
    parts = ['GAJI', '-', 'BELANJA', '=', 'SIMPAN'] if wrong else ['GAJI', '-', 'SIMPAN', '=', 'BELANJA']
    hi = 4 if wrong else 2
    sz = 64
    while sum(font(F_XB, sz).getlength(t) for t in parts) + 28 * (len(parts) - 1) > cw - 120:
        sz -= 2
    x = 60
    for i, t in enumerate(parts):
        k = ease_out((p - i * 0.1) / 0.25)
        f = font(F_XB, sz)
        w = f.getlength(t)
        if k > 0:
            col = (GOLD_L if (i == hi and not wrong) else (255, 150, 150) if (i == hi and wrong) else (255, 255, 255))
            d.text((x, 260 + (1 - k) * 30), t, font=f, fill=col + (int(255 * k),), anchor='lm')
        x += w + 28
    if p > 0.6:
        k = back_out(min(1, (p - 0.6) / 0.2))
        icon = x_icon(int(150 * max(0.05, k))) if wrong else check_icon(int(150 * max(0.05, k)))
        im.alpha_composite(icon, (int(cw / 2 - icon.width / 2), int(450 - icon.height / 2)))
    return with_shadow(im, 28, 16, 0.4)


def info_card(p, info):
    cw = 940
    pw = cw - 60
    ph = int(pw * info.height / info.width)
    ch = 110 + ph + 40
    im = rounded((cw, ch), 44, NAVY_C)
    d = ImageDraw.Draw(im)
    d.text((cw / 2, 60), 'UBAH FORMULA', font=font(F_XB, 52), fill=GOLD_L + (255,), anchor='mm')
    k = ease_out(min(1, max(0, p) / 0.3))
    z = 1.0 + 0.05 * max(0, p)
    src = info.resize((int(pw * z), int(ph * z)), Image.LANCZOS)
    src = src.crop(((src.width - pw) // 2, (src.height - ph) // 2, (src.width - pw) // 2 + pw, (src.height - ph) // 2 + ph)).convert('RGBA')
    m = Image.new('L', src.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, pw - 1, ph - 1], 26, fill=int(255 * k))
    src.putalpha(m)
    im.alpha_composite(shine(src, (p - 0.5) / 0.5), (30, 110))
    return with_shadow(im, 28, 16, 0.4)


def fund_card(p):
    """Tabung kecemasan: min 3-6 bulan, then work up to 12 bulan."""
    cw, ch = 920, 760
    im = rounded((cw, ch), 48, NAVY_C)
    d = ImageDraw.Draw(im)
    d.text((cw / 2, 80), 'TABUNG KECEMASAN', font=font(F_XB, 58), fill=(255, 255, 255, 255), anchor='mm')
    d.text((cw / 2, 145), 'berapa bulan perbelanjaan?', font=font(F_B, 34), fill=(170, 172, 190, 255), anchor='mm')
    rows = [('Minimum', '3-6 bulan', 6 / 12, GOLD), ('Sasaran', '12 bulan', 1.0, (90, 200, 120))]
    for i, (lab, val, frac, col) in enumerate(rows):
        k = ease_out((p - i * 0.35) / 0.35)
        y = 230 + i * 220
        d.text((60, y), lab, font=font(F_XB, 44), fill=(255, 255, 255, 255))
        d.text((cw - 60, y), val, font=font(F_XB, 44), fill=col + (255,), anchor='ra')
        d.rounded_rectangle([60, y + 80, cw - 60, y + 140], 30, fill=(45, 48, 70, 255))
        if k > 0.02:
            d.rounded_rectangle([60, y + 80, 60 + (cw - 120) * frac * k, y + 140], 30, fill=col + (255,))
    for mo in range(1, 13):
        x = 60 + (cw - 120) * mo / 12
        d.line([(x, 690), (x, 705)], fill=(90, 94, 120, 255), width=3)
    d.text((60, 725), '1', font=font(F_B, 24), fill=(150, 154, 180, 255), anchor='lm')
    d.text((cw - 60, 725), '12 bulan', font=font(F_B, 24), fill=(150, 154, 180, 255), anchor='rm')
    return with_shadow(im, 28, 16, 0.4)


def quote_card(text_lines, w=900):
    f = font(F_XB, 54)
    lh = 72
    h = 110 + lh * len(text_lines) + 30
    im = rounded((w, h), 40, (16, 18, 34, 235))
    d = ImageDraw.Draw(im)
    d.text((34, 4), '“', font=font(F_XB, 90), fill=GOLD + (255,))
    for i, (t, col) in enumerate(text_lines):
        sz = 54
        while font(F_XB, sz).getlength(t) > w - 80:
            sz -= 2
        d.text((w / 2, 110 + i * lh), t, font=font(F_XB, sz), fill=col + (255,), anchor='mm')
    return with_shadow(im, 20, 10, 0.45)


def stamp(text, col=ALERT, size=96):
    f = font(F_XB, size)
    tw = int(f.getlength(text))
    im = Image.new('RGBA', (tw + 80, size + 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, tw + 74, size + 74], 24, outline=col + (255,), width=11)
    d.text(((tw + 80) / 2, (size + 80) / 2), text, font=f, fill=col + (255,), anchor='mm')
    return im.rotate(-7, resample=Image.BICUBIC, expand=True)


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

    gold_words = {'simpan', 'simpanan', 'menyimpan', 'menabung', 'aset', 'konsisten', 'dahulu', 'tadbir', 'tabiat'}
    red_words = {'kesilapan', 'tak', 'belum', 'kehilangan', 'kesusahan'}
    cap_cache = {}

    def cap(word):
        if word not in cap_cache:
            num = word[:1].isdigit() or word[:2] == 'RM'
            disp = word if num else word.lower()
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
    info = Image.open(IMG1).convert('RGB')
    h1 = text_sprite('BILA ADA DUIT,', 112, (255, 255, 255), (232, 232, 240))
    h2 = text_sprite('BARU SIMPAN?', 120, GOLD_L, GOLD, stroke=5, stroke_col=(60, 40, 10))
    st_silap = stamp('KESILAPAN', size=80)
    p_gaji = fit_pill('Gaji semakin meningkat', icon=arrow_icon(60), size=54)
    p_sama = fit_pill('Simpanan masih sama', icon=warn_icon(60), size=54, bg=(232, 190, 92, 255))
    p_3bln = fit_pill('Kecemasan 3 bulan pun belum tentu cukup', icon=warn_icon(60), size=48)
    qmark = text_sprite('?', 260, GOLD_L, GOLD, stroke=8, stroke_col=(60, 40, 10))
    p_kenapa = fit_pill('Kenapa berlaku?', size=60)
    p_komit = fit_pill('Bayar komitmen', size=54)
    p_mahu = fit_pill('Beli apa yang mahu', size=54)
    p_baki = fit_pill('Ada baki? Baru simpan', icon=warn_icon(60), size=54)
    st_baki = stamp('TAK ADA BAKI', size=90)
    chips = {'10': fit_pill('10%', size=80, bg=(232, 190, 92, 255)), '20': fit_pill('20%', size=80, bg=(232, 190, 92, 255)),
             '30': fit_pill('30%', size=80, bg=(232, 190, 92, 255))}
    p_asing = fit_pill('Asingkan dahulu untuk simpanan', icon=check_icon(60), size=50)
    p_lebih = fit_pill('Selebihnya: komitmen & belanja harian', size=46)
    p_tunggu = fit_pill('Tak perlu tunggu gaji besar', icon=check_icon(60), size=52)
    p_mampu = fit_pill('Simpan ikut kemampuan', icon=check_icon(60), size=54)
    p_tabiat = fit_pill('Bina tabiat menyimpan secara konsisten', icon=check_icon(60), size=48, bg=(232, 190, 92, 255))
    p_kerja = fit_pill('Tak selamanya mampu bekerja', icon=warn_icon(60), size=52)
    risk = [fit_pill(t, size=46) for t in ('Bersara', 'Berhenti kerja', 'Hilang pendapatan')]
    p_bantu = fit_pill('Apa yang akan bantu kita?', size=54)
    p_aset = fit_pill('Simpanan & aset yang kita bina', icon=check_icon(60), size=50, bg=(232, 190, 92, 255))
    p_orang = fit_pill('Tak menyusahkan orang lain', icon=check_icon(60), size=52)
    q_takdir = quote_card([('Dah bersedia, masih diuji = takdir', (255, 255, 255)),
                           ('Mampu, tapi tak bersedia = soal tadbir', GOLD_L)])
    p_jgn = fit_pill('Jangan tunggu duit lebih', icon=x_icon(60), size=54)
    p_dulu = fit_pill('Simpan dahulu, belanja selebihnya', icon=check_icon(60), size=50, bg=(232, 190, 92, 255))
    q_end = quote_card([('Bukan berapa besar gaji,', (255, 255, 255)), ('tapi cara urus setiap ringgit', GOLD_L)])
    logo_c, logo_w = load_logos()
    wm = logo_w.resize((150, int(150 * logo_w.height / logo_w.width)), Image.LANCZOS)
    paper = paper_texture(W, H)

    T = {'baru': wt('baru'), 'silap': wt('kesilapan'), 'gaji': cue_t(3), 'sama': wt('sama'), 'kecemasan': cue_t(4),
         'kenapa': cue_t(6),
         'w_in': cue_t(7) - 0.05, 'w_out': cue_t(7, True) + 0.2,
         'komit': wt('komitmen'), 'mahu': wt('mahu'), 'bakiq': wt('baki'), 'masalah': cue_t(10), 'baki2': wt('baki', 2),
         'i_in': cue_t(11) - 0.05, 'i_out': cue_t(12, True) + 0.25,
         'asing': wt('asingkan'), 'p10': wt('10%'), 'p20': wt('20%'), 'p30': wt('30%'), 'lebih': cue_t(16),
         'tunggu': cue_t(17), 'rm2000': wt('RM2,000'), 'rm200': wt('RM200'), 'mampu': cue_t(19), 'tabiat': cue_t(20),
         'kerja': cue_t(21), 'bersara': wt('bersara'), 'berhenti': wt('berhenti'), 'hilang': wt('kehilangan'),
         'bantu': cue_t(24), 'aset': cue_t(25),
         'f_in': cue_t(26) - 0.05, 'f_out': cue_t(28, True) + 0.2,
         'orang': cue_t(29), 'takdir': cue_t(31), 'tadbir': wt('tadbir'), 'jgn': cue_t(34), 'dulu': cue_t(35),
         'end': cue_t(36)}
    hook_end = T['gaji'] - 0.05
    pops = [T[k] for k in ('baru', 'gaji', 'sama', 'kecemasan', 'kenapa', 'komit', 'mahu', 'bakiq', 'asing', 'p10',
                           'p20', 'p30', 'lebih', 'tunggu', 'rm2000', 'mampu', 'tabiat', 'kerja', 'bersara', 'berhenti',
                           'hilang', 'bantu', 'aset', 'orang', 'takdir', 'jgn', 'dulu', 'end')]
    whooshes = [(T['silap'] - 0.15, 0.4, 0.24), (T['baki2'] - 0.15, 0.4, 0.24)] + \
               [(T[k + '_in'] - 0.12, 0.35, 0.18) for k in 'wif'] + [(T[k + '_out'] - 0.15, 0.35, 0.18) for k in 'wif'] + \
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
        for a_, b_, kind in ((T['w_in'], T['w_out'], 'w'), (T['i_in'], T['i_out'], 'i'), (T['f_in'], T['f_out'], 'f')):
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
            if kind == 'w':
                card = formula_card(pr, True)
            elif kind == 'i':
                # infographic first, then the corrected formula
                card = info_card(pr / 0.6, info) if pr < 0.6 else formula_card((pr - 0.6) / 0.4 * 1.2, False)
            else:
                card = fund_card(pr)
            sc = min(0.9, (B.TT_BOTTOM - 260) / card.height)
            place(fr, card, B.TT_CENTER_X, 170 + card.height * sc / 2 + (1 - k_in) * 100, sc * (1.1 - 0.1 * k_in), a)
        else:
            # HOOK: BILA ADA DUIT, / BARU SIMPAN? -> KESILAPAN stamp
            s, a = pop(t, 0.03, hook_end, 0.28, 0.12)
            place(fr, h1, B.TT_CENTER_X + 20, 230, s, a, rot=-3)
            s, a = pop(t, T['baru'] - 0.05, hook_end, 0.25, 0.12)
            place(fr, h2, B.TT_CENTER_X + 20, 355, s, a, rot=-3)
            s, a = pop(t, T['silap'] - 0.05, hook_end, 0.2, 0.12)
            if a:
                slam = 1 + 0.6 * max(0, 1 - (t - T['silap'] + 0.05) / 0.16)
                place(fr, st_silap, B.TT_CENTER_X + 80, 480, s * slam if s >= 1 else s, a)
            two(fr, t, p_gaji, T['gaji'] + 0.3, p_sama, T['sama'] - 0.3, T['kecemasan'] - 0.05)
            s, a = pop(t, T['kecemasan'] + 0.3, T['kenapa'] - 0.05)
            place(fr, p_3bln, B.TT_CENTER_X, 280, s, a)
            s, a = pop(t, T['kenapa'], T['w_in'], 0.3)
            place(fr, p_kenapa, B.TT_CENTER_X - 60, 260, s, a)
            place(fr, qmark, B.TT_CENTER_X + 300, 440, s * 0.8, a, rot=10 * math.sin(t * 5))
            e1 = T['masalah'] - 0.05
            for spr, ta, y in ((p_komit, T['komit'] - 0.1, 220), (p_mahu, T['mahu'] - 0.2, 340), (p_baki, T['bakiq'] - 0.1, 460)):
                s, a = pop(t, ta, e1)
                place(fr, spr, B.TT_CENTER_X, y, s, a)
            s, a = pop(t, T['baki2'] - 0.1, T['i_in'], 0.2, 0.12)
            if a:
                slam = 1 + 0.6 * max(0, 1 - (t - T['baki2'] + 0.1) / 0.16)
                place(fr, st_baki, B.TT_CENTER_X, 320, s * slam if s >= 1 else s, a)
            # 10 / 20 / 30 %
            e2 = T['tunggu'] - 0.05
            s, a = pop(t, T['asing'] - 0.1, e2)
            place(fr, p_asing, B.TT_CENTER_X, 220, s, a)
            for key, x in (('10', B.TT_CENTER_X - 280), ('20', B.TT_CENTER_X), ('30', B.TT_CENTER_X + 280)):
                s, a = pop(t, T['p' + key] - 0.1, e2, 0.3)
                place(fr, chips[key], x, 360, s, a)
            s, a = pop(t, T['lebih'], e2)
            place(fr, p_lebih, B.TT_CENTER_X, 490, s, a)
            # RM2,000 -> RM200
            e3 = T['tabiat'] - 0.05
            s, a = pop(t, T['tunggu'], T['rm2000'] - 0.1)
            place(fr, p_tunggu, B.TT_CENTER_X, 260, s, a)
            s, a = pop(t, T['rm2000'] - 0.1, T['mampu'] - 0.05)
            if a:
                val = 'RM2,000' if t < T['rm200'] - 0.1 else 'simpan RM200'
                place(fr, money_card(val, 'gaji' if t < T['rm200'] - 0.1 else 'mulakan dengan', GOLD_L, w=700),
                      B.TT_CENTER_X, 330, s, a)
            s, a = pop(t, T['mampu'], e3)
            place(fr, p_mampu, B.TT_CENTER_X, 280, s, a)
            s, a = pop(t, T['tabiat'], T['kerja'] - 0.05)
            place(fr, p_tabiat, B.TT_CENTER_X, 280, s, a)
            # tak selamanya mampu bekerja
            e4 = T['bantu'] - 0.05
            s, a = pop(t, T['kerja'], e4)
            place(fr, p_kerja, B.TT_CENTER_X, 220, s, a)
            for i, key in enumerate(('bersara', 'berhenti', 'hilang')):
                s, a = pop(t, T[key] - 0.1, e4)
                place(fr, risk[i], [B.TT_CENTER_X - 250, B.TT_CENTER_X + 200, B.TT_CENTER_X][i], [350, 350, 470][i], s, a)
            two(fr, t, p_bantu, T['bantu'], p_aset, T['aset'], T['f_in'])
            s, a = pop(t, T['orang'], T['takdir'] - 0.05)
            place(fr, p_orang, B.TT_CENTER_X, 280, s, a)
            s, a = pop(t, T['takdir'] + 0.6, T['jgn'] - 0.05, 0.3)
            place(fr, q_takdir, B.TT_CENTER_X, 320, s, a)
            two(fr, t, p_jgn, T['jgn'], p_dulu, T['dulu'], T['end'] - 0.05)
            s, a = pop(t, T['end'] + 0.3, base_dur - 0.02, 0.3)
            place(fr, q_end, B.TT_CENTER_X, 320, s, a)
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
        shots = [('Hook', T['silap'] + 0.6), ('Gaji naik, simpanan sama', T['kecemasan'] - 0.3),
                 ('Kenapa?', T['w_in'] - 0.3), ('Cutaway: formula biasa', T['w_out'] - 0.4),
                 ('Komitmen / baki', T['masalah'] - 0.3), ('TAK ADA BAKI (slow zoom)', T['i_in'] - 0.2),
                 ('Cutaway: infografik', T['i_in'] + (T['i_out'] - T['i_in']) * 0.45),
                 ('Cutaway: formula betul', T['i_out'] - 0.4), ('10/20/30%', T['tunggu'] - 0.3),
                 ('RM2,000 -> RM200', T['mampu'] - 0.3), ('Tabiat konsisten', T['kerja'] - 0.3),
                 ('Tak selamanya bekerja', T['bantu'] - 0.3), ('Cutaway: tabung kecemasan', T['f_out'] - 0.4),
                 ('Takdir / tadbir', T['jgn'] - 0.3), ('Simpan dahulu', T['end'] - 0.3), ('Penutup', base_dur - 0.4),
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
        print('preview ok; segments', len(SEGS), 'slow-zoom segs', sum(1 for a, b in SEGS if slow_amt(a, b)),
              'base', round(base_dur, 2), 'total', round(total, 2))
        return

    fdir = os.path.join(OUT, 'frames')
    os.makedirs(fdir, exist_ok=True)
    for fi in range(int(round(total * FPS))):
        ov, _ = overlay(fi / FPS)
        ov.save(os.path.join(fdir, f'f{fi:05d}.png'), compress_level=1)
    write_sfx(total, pops, whooshes, os.path.join(OUT, 'sfx.wav'))
    final = os.path.join(OUT, 'SimpanDuluBaruBelanja_AzlanEza.mp4')
    composite(os.path.join(OUT, 'base.mov'), fdir, os.path.join(OUT, 'sfx.wav'), total, final,
              music=MUSIC if os.path.exists(MUSIC) else None, music_ss=MUSIC_SS, music_db=MUSIC_DB, music_tempo=MUSIC_TEMPO)
    print('done', final)


if __name__ == '__main__':
    main()
