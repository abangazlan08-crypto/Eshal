#!/usr/bin/env python3
"""Video 4: 'Simpan dulu, baru berseronok' (in-car selfie) in the Azlan & Eza style.

python3 build_v4.py --preview   -> storyboard stills only
python3 build_v4.py             -> full render
"""
import importlib.util, json, math, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_VS = os.path.join(HERE, '..')
WORK = os.path.join(HERE, '..', 'work', 'v4')   # raw footage + licensed music (not in git)
ASSETS = os.path.join(HERE, '04_assets')
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
OUT = os.environ.get('OUT', os.path.join(WORK, 'out'))
MASK = os.path.join(ASSETS, 'facemask.png')
# Descript stock (Audioblocks): "Positive Hopeful Acoustic Guitar Live Strum", 91.65s. Start 16s in so the
# fade-out stays after the outro.
MUSIC = os.path.join(WORK, 'music.m4a')
MUSIC_SS = 9.0
MUSIC_DB = -15.0
os.makedirs(OUT, exist_ok=True)

CUES = [
    (1.093, 3.634, "Hidup bukan semata-mata kerja dan simpan."),
    (3.994, 8.173, "Ada hobi, ada benda yang kita suka buat, ada perkara yang buat kita"),
    (8.214, 11.234, "rasa hidup, itu semua bukan salah."),
    (11.514, 12.174, "Itu perlu."),
    (14.094, 14.794, "Suka golf?"), (15.054, 15.614, "Mainlah."),
    (16.073, 16.753, "Suka travel?"), (17.134, 17.814, "Rancanglah."),
    (18.294, 19.374, "Suka kopi mahal?"), (19.674, 20.434, "Nikmatilah."),
    (20.934, 25.814, "Tak ada sesiapa yang kata kita kena jadi kedekut untuk berjaya dalam kewangan."),
    (27.714, 30.834, "Tapi ada satu soalan yang perlu kita tanya diri sendiri setiap"),
    (30.874, 33.373, "bulan sebelum duit habis untuk hobi."),
    (33.754, 36.273, "Adakah simpanan masa depan kita dah selamat dulu?"),
    (41.797, 45.378, "Itulah bezanya orang yang sekadar enjoy hidup dengan orang"),
    (45.418, 47.178, "yang enjoy hidup dengan bijak."),
    (47.778, 51.538, "Bukan tak boleh berseronok tapi pastikan simpanan masuk"),
    (51.577, 54.178, "dulu sebelum belanja keluar."),
    (54.498, 55.998, "Simpan dulu baru berseronok."),
    (56.378, 59.697, "Bukan berseronok dulu baru simpan kalau ada lebih."),
    (63.122, 67.642, "Sebab bila kita dah ada simpanan yang kukuh, hobi kita pun jadi lebih seronok."),
    (67.982, 72.622, "Kita tak perlu rasa bersalah bila keluar duit untuk benda yang kita suka sebab"),
    (72.662, 75.562, "kita tahu masa depan kita dah terjaga"),
    (79.018, 81.358, "Hobi bagi kita kebahagiaan hari ini."),
    (81.777, 84.058, "Simpanan bagi kita ketenangan untuk esok."),
    (84.498, 89.497, "Dua-dua boleh wujud serentak asalkan kita tahu mana yang datang dahulu."),
    (90.038, 93.198, "Nak mulakan simpanan emas, boleh hubungi kami hari ini."),
]
B.SYL.update({'golf': 1, 'travel': 2, 'enjoy': 2, 'semata-mata': 5, 'dua-dua': 4})
GRADE = open(os.path.join(ASSETS, 'grade_D.txt')).read().strip()
RELIGHT = "eq=brightness=0.06:gamma=1.12:saturation=1.04,colorbalance=rm=0.02:bm=-0.015"


def build_segs():
    keep = json.load(open(os.path.join(ASSETS, 'edl.json')))['keep']
    segs = []
    for a, b in keep:      # keep breaths < 0.3s: no micro jump cuts
        if segs and a - segs[-1][1] < 0.30:
            segs[-1][1] = b
        else:
            segs.append([a, b])
    zoom, z = [], 1.0
    for i, (a, b) in enumerate(segs):
        if i and a - segs[i - 1][1] >= 0.5:
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
    # inside a removed gap: snap to the next kept segment
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


# ---------------------------------------------------------------- icons / cards
def icon_tile(kind, s=230):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, s - 1, s - 1], 54, fill=(255, 255, 255, 255))
    c = s / 2
    if kind == 'golf':
        d.ellipse([c - 70, s * .72, c + 70, s * .86], fill=(34, 160, 80, 255))
        d.ellipse([c - 16, s * .74, c + 16, s * .82], fill=(30, 30, 40, 255))
        d.line([(c + 2, s * .78), (c + 2, s * .18)], fill=(40, 40, 50, 255), width=8)
        d.polygon([(c + 6, s * .18), (c + 78, s * .29), (c + 6, s * .40)], fill=RED + (255,))
        d.ellipse([c - 62, s * .58, c - 36, s * .68], fill=(250, 250, 250, 255), outline=(180, 180, 190, 255), width=3)
    elif kind == 'travel':
        pl = [(c + 85, c), (c - 70, c - 14), (c - 70, c + 14)]
        d.polygon(pl, fill=(40, 110, 230, 255))
        d.polygon([(c + 20, c), (c - 20, c - 80), (c - 42, c - 80), (c - 12, c)], fill=(40, 110, 230, 255))
        d.polygon([(c + 20, c), (c - 20, c + 80), (c - 42, c + 80), (c - 12, c)], fill=(40, 110, 230, 255))
        d.polygon([(c - 55, c), (c - 80, c - 36), (c - 92, c - 36), (c - 70, c)], fill=(40, 110, 230, 255))
        d.polygon([(c - 55, c), (c - 80, c + 36), (c - 92, c + 36), (c - 70, c)], fill=(40, 110, 230, 255))
    elif kind == 'kopi':
        d.rounded_rectangle([c - 62, s * .36, c + 42, s * .80], 22, fill=(120, 72, 40, 255))
        d.ellipse([c + 26, s * .44, c + 82, s * .68], outline=(120, 72, 40, 255), width=14)
        d.ellipse([c - 90, s * .78, c + 70, s * .88], fill=(225, 225, 230, 255))
        for dx in (-34, -4, 26):
            d.arc([c + dx - 14, s * .12, c + dx + 14, s * .32], 200, 340, fill=(170, 170, 180, 255), width=6)
    return with_shadow(im, 18, 10, 0.4)


def question_card(p):
    cw, ch = 920, 900
    im = rounded((cw, ch), 48, (18, 20, 36, 255))
    d = ImageDraw.Draw(im)
    d.text((cw / 2, 90), 'SATU SOALAN', font=font(F_B, 40), fill=(150, 154, 180, 255), anchor='mm')
    d.text((cw / 2, 150), 'setiap bulan, sebelum duit habis untuk hobi', font=font(F_B, 30), fill=(150, 154, 180, 255), anchor='mm')
    # shield
    k = back_out(min(1, max(0, p) / 0.35))
    sx, sy, sr = cw / 2, 420, 150 * k
    if sr > 4:
        pts = [(sx - sr, sy - sr * .85), (sx, sy - sr * 1.05), (sx + sr, sy - sr * .85), (sx + sr * .9, sy + sr * .2),
               (sx, sy + sr * 1.05), (sx - sr * .9, sy + sr * .2)]
        d.polygon(pts, fill=GOLD + (255,))
        if p > 0.55:
            d.line([(sx - sr * .42, sy), (sx - sr * .1, sy + sr * .32), (sx + sr * .48, sy - sr * .36)],
                   fill=(30, 22, 10, 255), width=max(6, int(sr * .16)))
    d.text((cw / 2, 680), 'Simpanan masa depan', font=font(F_XB, 58), fill=(255, 255, 255, 255), anchor='mm')
    d.text((cw / 2, 760), 'dah selamat DULU?', font=font(F_XB, 62), fill=GOLD_L + (255,), anchor='mm')
    return with_shadow(im, 28, 16, 0.4)


def order_card(p):
    """Simpanan masuk dulu (1) -> belanja keluar (2)."""
    cw, ch = 920, 960
    im = rounded((cw, ch), 48, (18, 20, 36, 255))
    d = ImageDraw.Draw(im)
    d.text((cw / 2, 90), 'SIMPAN DULU,', font=font(F_XB, 64), fill=(255, 255, 255, 255), anchor='mm')
    d.text((cw / 2, 165), 'BARU BERSERONOK', font=font(F_XB, 64), fill=GOLD_L + (255,), anchor='mm')
    rows = [('1', 'Simpanan masuk', GOLD, (30, 22, 10)), ('2', 'Belanja & hobi keluar', (60, 64, 92), (255, 255, 255))]
    for i, (n, lab, bg, fg) in enumerate(rows):
        k = ease_out((p - i * 0.3) / 0.35)
        if k <= 0:
            continue
        y = 300 + i * 230
        x = 60 - (1 - k) * 200
        d.rounded_rectangle([x, y, x + cw - 120, y + 170], 36, fill=bg + (int(255 * k),))
        d.text((x + 80, y + 85), n, font=font(F_XB, 90), fill=fg + (int(255 * k),), anchor='mm')
        d.text((x + 160, y + 85), lab, font=font(F_XB, 50), fill=fg + (int(255 * k),), anchor='lm')
    if p > 0.75:
        k = ease_out((p - 0.75) / 0.2)
        d.text((cw / 2, 830), 'bukan "simpan kalau ada lebih"', font=font(F_B, 36), fill=(255, 140, 150, int(255 * k)), anchor='mm')
    return with_shadow(im, 28, 16, 0.4)


def split_card(p):
    cw, ch = 940, 760
    im = rounded((cw, ch), 48, (18, 20, 36, 255))
    d = ImageDraw.Draw(im)
    for i, (title, a, b, col) in enumerate((('HOBI', 'kebahagiaan', 'hari ini', (90, 170, 255)),
                                           ('SIMPANAN', 'ketenangan', 'untuk esok', GOLD))):
        k = back_out(min(1, max(0, p - i * 0.4) / 0.3))
        if k <= 0.02:
            continue
        x0 = 40 + i * 450
        box = rounded((410, 600), 36, (30, 33, 52, 255))
        bd = ImageDraw.Draw(box)
        bd.rounded_rectangle([30, 30, 380, 140], 30, fill=col + (255,))
        bd.text((205, 85), title, font=font(F_XB, 54), fill=(20, 20, 30, 255), anchor='mm')
        bd.text((205, 300), '=', font=font(F_XB, 90), fill=(200, 202, 220, 255), anchor='mm')
        bd.text((205, 430), a, font=font(F_XB, 50), fill=(255, 255, 255, 255), anchor='mm')
        bd.text((205, 500), b, font=font(F_B, 40), fill=(170, 172, 190, 255), anchor='mm')
        box = box.resize((max(1, int(410 * k)), max(1, int(600 * k))), Image.BICUBIC)
        im.alpha_composite(box, (int(x0 + 205 - box.width / 2), int(380 - box.height / 2)))
    return with_shadow(im, 28, 16, 0.4)


def main():
    preview = '--preview' in sys.argv
    if not preview and '--skip-base' not in sys.argv:
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

    gold_words = {'simpan', 'simpanan', 'dulu', 'dahulu', 'emas', 'perlu', 'bijak', 'selamat', 'terjaga', 'ketenangan'}
    cap_cache = {}

    def cap(word):
        if word not in cap_cache:
            disp = word.lower()
            sz = 104
            while font(F_XB, sz).getlength(disp) > 900:
                sz -= 4
            g = disp in gold_words
            cap_cache[word] = text_sprite(disp, sz, GOLD_L if g else (255, 255, 255), GOLD if g else (247, 228, 160),
                                          stroke=5, stroke_col=(25, 18, 20))
        return cap_cache[word]
    cap_win = []
    for i, w in enumerate(words):
        nxt = words[i + 1]['os'] if i + 1 < len(words) else w['oe'] + 0.3
        cap_win.append((w['os'], nxt if nxt - w['oe'] < 0.35 else w['oe'] + 0.15, w['w']))

    # sprites
    h1 = text_sprite('HIDUP BUKAN', 120, (255, 255, 255), (232, 232, 240))
    h2 = text_sprite('KERJA & SIMPAN', 112, GOLD_L, GOLD, stroke=5, stroke_col=(60, 40, 10))
    h3 = text_sprite('SEMATA-MATA', 96, (255, 120, 135), RED, stroke=5, stroke_col=(255, 255, 255))
    perlu = text_sprite('ITU PERLU.', 168, GOLD_L, GOLD, stroke=7, stroke_col=(60, 40, 10))
    tiles = {k: icon_tile(k) for k in ('golf', 'travel', 'kopi')}
    verbs = {'golf': text_sprite('MAINLAH', 92, (255, 255, 255), (232, 232, 240), stroke=4, stroke_col=(20, 20, 30)),
             'travel': text_sprite('RANCANGLAH', 92, (255, 255, 255), (232, 232, 240), stroke=4, stroke_col=(20, 20, 30)),
             'kopi': text_sprite('NIKMATILAH', 92, (255, 255, 255), (232, 232, 240), stroke=4, stroke_col=(20, 20, 30))}
    p_kedekut = pill('Kena jadi kedekut?', icon=x_icon(60), size=56)
    p_enjoy = pill('Sekadar enjoy hidup', size=54, bg=(255, 255, 255, 235))
    p_bijak = pill('Enjoy hidup dengan BIJAK', icon=check_icon(60), size=54, bg=(232, 190, 92, 255))
    p_guilt = pill('Tak perlu rasa bersalah', icon=check_icon(60), size=54)
    p_safe = pill('Masa depan dah terjaga', icon=check_icon(60), size=54, bg=(232, 190, 92, 255))
    p_serentak = pill('Dua-dua boleh wujud serentak', size=52)
    b_first = badge('1', 'Simpanan', 'datang dahulu')
    p_cta = pill('Nak mulakan simpanan emas?', size=54)
    p_call = pill('Hubungi kami hari ini', icon=check_icon(60), size=58, bg=(232, 190, 92, 255))
    logo_c, logo_w = load_logos()
    wm = logo_w.resize((150, int(150 * logo_w.height / logo_w.width)), Image.LANCZOS)
    paper = paper_texture(W, H)

    T = {'semata': wt('semata-mata'), 'perlu': cue_t(3), 'golf': cue_t(4), 'main': cue_t(5), 'travel': cue_t(6),
         'rancang': cue_t(7), 'kopi': cue_t(8), 'nikmat': cue_t(9), 'kedekut': wt('kedekut'),
         'q_in': cue_t(11) - 0.05, 'q_out': cue_t(13, True) + 0.15,
         'enjoy': cue_t(14), 'bijak': wt('bijak'),
         'o_in': cue_t(16) - 0.05, 'o_out': cue_t(19, True) + 0.15,
         'kukuh': cue_t(20), 'guilt': cue_t(21), 'safe': cue_t(22),
         's_in': cue_t(23) - 0.05, 's_out': cue_t(24, True) + 0.15,
         'serentak': cue_t(25), 'dahulu': wt('dahulu'), 'cta': cue_t(26), 'hubungi': wt('hubungi')}
    hook_end = cue_t(4) - 0.05
    pops = [T[k] for k in ('golf', 'main', 'travel', 'rancang', 'kopi', 'nikmat', 'kedekut', 'enjoy', 'bijak', 'guilt',
                           'safe', 'serentak', 'dahulu', 'cta', 'hubungi')] + [T['semata']]
    whooshes = [(T['perlu'] - 0.2, 0.4, 0.24)] + [(T[k + '_in'] - 0.12, 0.35, 0.18) for k in 'qos'] + \
               [(T[k + '_out'] - 0.15, 0.35, 0.18) for k in 'qos'] + [(base_dur - 0.15, 0.5, 0.22)]

    if '--audio-preview' in sys.argv:
        write_sfx(total, pops, whooshes, os.path.join(OUT, 'sfx.wav'))
        n = len(SEGS)
        chain = ''.join(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.03,"
                        f"afade=t=out:st={b-a-0.03:.3f}:d=0.03[s{i}];" for i, (a, b) in enumerate(SEGS))
        chain += ''.join(f'[s{i}]' for i in range(n)) + f'concat=n={n}:v=0:a=1[voice];'
        fc = chain + B.audio_mix_graph('[voice]', '[1:a]', total, '[2:a]', MUSIC_SS, MUSIC_DB, outro_at=base_dur)
        outp = os.path.join(OUT, 'PREVIEW_audio_music.m4a')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', RAW, '-i', os.path.join(OUT, 'sfx.wav'), '-i', MUSIC,
                        '-filter_complex', fc, '-map', '[a]', '-t', f'{total}', '-c:a', 'aac', '-b:a', '160k', outp],
                       check=True)
        print('audio preview', outp)
        return

    def overlay(t):
        fr = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        if t >= base_dur:
            return outro_frame(t - base_dur, int(t * FPS), logo_w), False
        cut = None
        for a_, b_, kind in ((T['q_in'], T['q_out'], 'q'), (T['o_in'], T['o_out'], 'o'), (T['s_in'], T['s_out'], 's')):
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
            card = {'q': question_card, 'o': order_card, 's': split_card}[kind](pr)
            place(fr, card, W / 2, H * 0.42 + (1 - k_in) * 120, 1.12 - 0.12 * k_in, a)
        else:
            # HOOK
            s, a = pop(t, 0.03, T['perlu'] - 0.05, 0.28, 0.12)
            place(fr, h1, W / 2 - 10, 200, s, a, rot=3)
            s, a = pop(t, T['semata'] - 0.05, T['perlu'] - 0.05, 0.25, 0.12)
            place(fr, h3, W / 2 + 120, 315, s, a, rot=3)
            s, a = pop(t, T['semata'] + 0.35, T['perlu'] - 0.05, 0.28, 0.12)
            place(fr, h2, W / 2 + 10, 440, s, a, rot=3)
            s, a = pop(t, T['perlu'] - 0.03, hook_end, 0.22, 0.12)
            if a:
                slam = 1 + 0.6 * max(0, 1 - (t - T['perlu'] + 0.03) / 0.18)
                place(fr, shine(perlu, (t - T['perlu'] - 0.15) / 0.5), W / 2, 320, s * slam if s >= 1 else s, a)
            # rapid fire hobbies
            for key, ta, tb, nxt in (('golf', T['golf'], T['main'], T['travel']), ('travel', T['travel'], T['rancang'], T['kopi']),
                                     ('kopi', T['kopi'], T['nikmat'], T['kedekut'] - 0.6)):
                s, a = pop(t, ta - 0.03, nxt - 0.05, 0.25, 0.1)
                place(fr, tiles[key], W / 2, 330, s, a, rot=-6 + 4 * math.sin(t * 7))
                s, a = pop(t, tb - 0.03, nxt - 0.05, 0.22, 0.1)
                place(fr, verbs[key], W / 2, 520, s, a, rot=-3)
            s, a = pop(t, T['kedekut'] - 0.1, T['q_in'])
            place(fr, p_kedekut, W / 2, 300, s, a)
            # enjoy vs bijak
            s, a = pop(t, T['enjoy'] + 0.3, T['o_in'])
            place(fr, p_enjoy, W / 2 - 120, 250, s, a)
            s, a = pop(t, T['bijak'] - 0.1, T['o_in'])
            place(fr, p_bijak, W / 2 + 40, 390, s, a)
            # after order cutaway: kukuh / guilt / safe
            e = T['s_in']
            s, a = pop(t, T['guilt'] + 0.2, e)
            place(fr, p_guilt, W / 2 - 60, 250, s, a)
            s, a = pop(t, T['safe'], e)
            place(fr, p_safe, W / 2 + 40, 390, s, a)
            # serentak + 1 simpanan dahulu
            e2 = T['cta'] - 0.05
            s, a = pop(t, T['serentak'], e2)
            place(fr, p_serentak, W / 2, 230, s, a)
            s, a = pop(t, T['dahulu'] - 0.15, e2, 0.3)
            place(fr, b_first, W / 2, 400, s, a)
            # CTA
            e3 = base_dur - 0.02
            s, a = pop(t, T['cta'], e3)
            place(fr, p_cta, W / 2, 250, s, a)
            s, a = pop(t, T['hubungi'] - 0.1, e3, 0.3)
            place(fr, shine(p_call, (t - T['hubungi'] - 0.3) / 0.6), W / 2, 400, s, a)
            place(fr, wm, W - 110, H - 300, 1, 0.9)
        for a0, a1, w in cap_win:
            if a0 <= t < a1:
                k = (t - a0) / 0.09
                place(fr, cap(w), W / 2, H * 0.84, 0.82 + 0.18 * back_out(min(1, k)) if k < 1 else 1, 1)
                break
        for o, z0, z1 in zip(offs[1:], ZOOM[:-1], ZOOM[1:]):
            if z0 != z1 and abs(t - o) < 0.05:
                fr.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(60 * (1 - abs(t - o) / 0.05)))))
        return fr, True

    if preview:
        shots = [('Hook: HIDUP BUKAN…', T['semata'] + 0.9), ('Hook: ITU PERLU', T['perlu'] + 0.35),
                 ('Suka golf? Mainlah', T['main'] + 0.25), ('Suka travel? Rancanglah', T['rancang'] + 0.25),
                 ('Suka kopi mahal? Nikmatilah', T['nikmat'] + 0.25), ('Kena kedekut?', T['kedekut'] + 0.5),
                 ('Cutaway: satu soalan', T['q_out'] - 0.4), ('Enjoy vs bijak', T['o_in'] - 0.3),
                 ('Cutaway: simpan dulu', T['o_out'] - 0.4), ('Tak rasa bersalah / terjaga', T['s_in'] - 0.3),
                 ('Cutaway: hobi vs simpanan', T['s_out'] - 0.4), ('1 Simpanan dahulu', T['cta'] - 0.3),
                 ('CTA', base_dur - 0.4), ('Outro', base_dur + 1.6)]
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
        cols = 7
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
    final = os.path.join(OUT, 'SimpanDulu_BaruBerseronok_AzlanEza.mp4')
    composite(os.path.join(OUT, 'base.mov'), fdir, os.path.join(OUT, 'sfx.wav'), total, final,
              music=MUSIC, music_ss=MUSIC_SS, music_db=MUSIC_DB)
    print('done', final)


if __name__ == '__main__':
    main()
