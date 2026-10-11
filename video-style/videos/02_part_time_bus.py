#!/usr/bin/env python3
"""Video 2: 'Part time masih bekerja' (bus, Norway trip) in the saved Azlan & Eza style."""
import json, math, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import build as B
from build import (W, H, FPS, OUTRO, RED, F_XB, F_B, Image, ImageDraw, text_sprite, rounded,
                   with_shadow, place, pop, pill, check_icon, ticket, ease_out, back_out, font,
                   paper_texture, load_logos, outro_frame, write_sfx, composite, syllables)

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.environ.get('RAW', os.path.join(HERE, '..', 'work', 'v2', 'raw.mp4'))
OUT = os.environ.get('OUT', os.path.join(HERE, '..', 'work', 'v2', 'out'))
os.makedirs(OUT, exist_ok=True)

# Descript SRT cues (source time) -> captions are distributed by syllables inside each cue
CUES = [
    (7.094, 8.834, "Part time masih bekerja."),
    (9.694, 12.254, "Tak ada lagi cita-cita untuk berhenti sebab kerja saya"),
    (12.294, 14.114, "pun macam tak perlu berhenti."),
    (16.374, 18.534, "Tapi saya happy dengan PG punya income."),
    (18.614, 21.874, "Income PG saya sekarang setahun gaji saya kerja KK."),
    (22.374, 22.934, "Alhamdulillah."),
    (23.834, 29.134, "Jadi saya doakan semua dalam bas ni boleh dapat dua tiket ke Norway"),
    (29.654, 31.274, "supaya boleh teman saya lagi."),
    (31.514, 31.933, "InsyaAllah."),
    (32.514, 33.354, "Assalamualaikum."),
]
B.SYL.update({'PG': 2, 'KK': 2, 'Part': 1, 'time': 1, 'happy': 2, 'income': 2, 'Income': 2})
SEGS = [(6.95, 8.95), (9.55, 14.25), (16.25, 22.00), (22.25, 23.05), (23.70, 29.25),
        (29.55, 31.35), (31.40, 32.05), (32.40, 33.50)]
ZOOM = [1.0, 1.07, 1.0, 1.07, 1.0, 1.07, 1.0, 1.07]
CROP_CX = 1312 + 1215 / 2


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


def words_from_cues():
    out = []
    for s, e, text in CUES:
        toks = [t.strip('.,') for t in text.split()]
        wts = [syllables(t) for t in toks]
        tot = sum(wts)
        dur = e - s
        acc = 0
        for t, w in zip(toks, wts):
            ws = s + dur * acc / tot
            acc += w
            out.append({'w': t, 's': ws, 'e': s + dur * acc / tot})
    for w in out:
        w['os'], w['oe'] = src2out(w['s']), src2out(w['e'])
    return [w for w in out if w['os'] is not None]


def render_base():
    cy_face = 0.42 * 2160
    parts = []
    for i, ((a, b), z) in enumerate(zip(SEGS, ZOOM)):
        d = b - a
        cw, ch = 1215 / z, 2160 / z
        x = min(max(CROP_CX - cw / 2, 0), 3840 - cw)
        y = min(max(cy_face - ch / 2, 0), 2160 - ch)
        p = os.path.join(OUT, f'seg{i}.mov')
        vf = (f"crop={cw:.0f}:{ch:.0f}:{x:.0f}:{y:.0f},scale={W}:{H}:flags=lanczos,setsar=1,fps={FPS},"
              f"eq=contrast=1.05:saturation=1.12:gamma=1.02")
        af = f"aresample=48000,afade=t=in:d=0.03,afade=t=out:st={d-0.03:.3f}:d=0.03"
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a}', '-t', f'{d}', '-i', RAW,
                        '-map', '0:v:0', '-map', '0:a:0', '-vf', vf, '-af', af, '-c:v', 'libx264',
                        '-crf', '16', '-preset', 'fast', '-pix_fmt', 'yuv420p', '-c:a', 'pcm_s16le',
                        '-ac', '2', p], check=True)
        parts.append(p)
    lst = os.path.join(OUT, 'list.txt')
    open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy',
                    os.path.join(OUT, 'base.mov')], check=True)


# ---------------------------------------------------------------- new icons for this video
def x_icon(s=58):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, s - 1, s - 1], fill=(220, 38, 38, 255))
    k = s * 0.3
    d.line([(k, k), (s - k, s - k)], fill=(255, 255, 255, 255), width=max(4, s // 9))
    d.line([(s - k, k), (k, s - k)], fill=(255, 255, 255, 255), width=max(4, s // 9))
    return im


def smiley(s=170):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, s - 1, s - 1], fill=(255, 205, 60, 255), outline=(200, 140, 20, 255), width=6)
    d.ellipse([s * .28, s * .3, s * .38, s * .45], fill=(60, 40, 20, 255))
    d.ellipse([s * .62, s * .3, s * .72, s * .45], fill=(60, 40, 20, 255))
    d.arc([s * .22, s * .3, s * .78, s * .8], 20, 160, fill=(60, 40, 20, 255), width=max(6, s // 18))
    return with_shadow(im, 14, 8, 0.35)


def bus_icon(s=60):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([2, 6, s - 3, s * .8], 10, fill=RED + (255,))
    d.rectangle([8, 14, s * .45, s * .45], fill=(210, 235, 255, 255))
    d.rectangle([s * .52, 14, s - 9, s * .45], fill=(210, 235, 255, 255))
    for cx in (s * .27, s * .73):
        d.ellipse([cx - 8, s * .72, cx + 8, s * .72 + 16], fill=(30, 30, 40, 255))
    return im


def heart_icon(s=58):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = s * 0.26
    d.ellipse([s * .5 - 2 * r, s * .2, s * .5, s * .2 + 2 * r], fill=(236, 72, 100, 255))
    d.ellipse([s * .5, s * .2, s * .5 + 2 * r, s * .2 + 2 * r], fill=(236, 72, 100, 255))
    d.polygon([(s * .5 - 2 * r + 1, s * .2 + r * 1.25), (s * .5 + 2 * r - 1, s * .2 + r * 1.25), (s * .5, s * .92)],
              fill=(236, 72, 100, 255))
    return im


def sparkle(s=90, col=(255, 220, 110)):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, r1, r2 = s / 2, s / 2, s * 0.11
    pts = []
    for k in range(8):
        a = -math.pi / 2 + k * math.pi / 4
        r = r1 if k % 2 == 0 else r2
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    d.polygon(pts, fill=col + (255,))
    return im


def compare_card(p):
    """Cutaway: 'Income PG sekarang = gaji setahun kerja KK' as two equal bars (no figures)."""
    cw, ch = 900, 900
    im = rounded((cw, ch), 48, (18, 20, 36, 255))
    d = ImageDraw.Draw(im)
    d.text((cw / 2, 96), 'INCOME PG', font=font(F_XB, 84), fill=(255, 255, 255, 255), anchor='mm')
    d.text((cw / 2, 168), 'sekarang', font=font(F_B, 40), fill=(150, 154, 180, 255), anchor='mm')
    rows = [('Gaji setahun', 'kerja KK', (110, 116, 150), (170, 176, 205), 270),
            ('Income PG', 'sekarang', B.RED, (247, 210, 120), 610)]
    for i, (lab, sub, c0, c1, y) in enumerate(rows):
        k = ease_out((p - i * 0.25) / 0.55)
        d.text((60, y), lab, font=font(F_XB, 50), fill=(255, 255, 255, 255))
        d.text((60 + font(F_XB, 50).getlength(lab) + 18, y + 14), sub, font=font(F_B, 34), fill=(150, 154, 180, 255))
        d.rounded_rectangle([60, y + 84, cw - 60, y + 144], 30, fill=(45, 48, 70, 255))
        x1 = 60 + (cw - 120) * k
        if x1 > 120:
            n = int(x1 - 60)
            bar = Image.new('RGBA', (n, 60))
            bd = ImageDraw.Draw(bar)
            for xx in range(n):
                g = xx / max(1, cw - 120)
                bd.line([(xx, 0), (xx, 59)], fill=tuple(int(c0[j] * (1 - g) + c1[j] * g) for j in range(3)) + (255,))
            m = Image.new('L', (n, 60), 0)
            ImageDraw.Draw(m).rounded_rectangle([0, 0, n - 1, 59], 30, fill=255)
            bar.putalpha(m)
            im.alpha_composite(bar, (60, y + 84))
    if p > 0.75:
        k = back_out(min(1, (p - 0.75) / 0.2))
        eq = text_sprite('=', int(150 * max(0.05, k)), (255, 235, 150), (240, 190, 60), stroke=5, stroke_col=B.RED)
        im.alpha_composite(eq, (int(cw / 2 - eq.width / 2), int(530 - eq.height / 2)))
    d.text((cw / 2, ch - 80), 'Alhamdulillah', font=font(F_B, 40), fill=(247, 228, 160, 255), anchor='mm')
    return with_shadow(im, 28, 16, 0.4)


def main():
    if '--skip-base' not in sys.argv:
        render_base()
    words = words_from_cues()
    json.dump(words, open(os.path.join(OUT, 'words.json'), 'w'), indent=1)
    offs, base_dur = offsets()
    total = base_dur + OUTRO
    nfr = int(round(total * FPS))
    seg_t = [(o, o + (b - a)) for (a, b), o in zip(SEGS, offs)]

    def wt(word, nth=1, end=False):
        k = 0
        for w in words:
            if w['w'].lower() == word.lower():
                k += 1
                if k == nth:
                    return w['oe'] if end else w['os']
        raise KeyError(word)

    cap_cache = {}

    def cap(word):
        if word not in cap_cache:
            disp = word if word.isupper() else word.lower()
            sz = 104
            while font(F_XB, sz).getlength(disp) > 900:
                sz -= 4
            cap_cache[word] = text_sprite(disp, sz, (255, 255, 255), (247, 228, 160), stroke=5, stroke_col=(25, 18, 20))
        return cap_cache[word]
    cap_win = []
    for i, w in enumerate(words):
        nxt = words[i + 1]['os'] if i + 1 < len(words) else w['oe'] + 0.3
        cap_win.append((w['os'], nxt if nxt - w['oe'] < 0.35 else w['oe'] + 0.15, w['w']))

    # sprites
    t_l1 = text_sprite('PART TIME', 148, (255, 120, 135), RED, stroke=6, stroke_col=(255, 255, 255))
    t_l2 = text_sprite('MASIH KERJA', 132, (255, 255, 255), (232, 232, 240))
    p_stop = pill('Berhenti kerja?', icon=x_icon(60), size=56)
    p_no = pill('Tak perlu berhenti', icon=check_icon(60), size=56)
    p_happy = pill('Happy dengan income PG', size=50)
    face = smiley(170)
    p_alh = pill('Alhamdulillah', size=58)
    spk = [sparkle(s) for s in (90, 60, 74, 50)]
    p_bus = pill('Semua dalam bas ni', icon=bus_icon(62), size=54)
    tk1 = ticket(sub='2 TIKET • NORWAY')
    tk2 = ticket(sub='2 TIKET • NORWAY')
    x2 = text_sprite('x2', 150, (255, 235, 150), (240, 190, 60), stroke=6, stroke_col=RED)
    p_teman = pill('Teman saya lagi!', icon=heart_icon(60), size=56)
    logo_c, logo_w = load_logos()
    wm = logo_w.resize((150, int(150 * logo_w.height / logo_w.width)), Image.LANCZOS)
    paper = paper_texture(W, H)

    t_berhenti = wt('berhenti')
    t_tak2 = wt('tak', 2)
    t_happy = wt('happy')
    cut_in = wt('Income', 2) - 0.05          # "Income PG saya sekarang ..."
    cut_out = seg_t[2][1]                    # end of "... kerja KK"
    t_alh = seg_t[3][0]
    t_semua = wt('semua')
    t_dua = wt('dua')
    t_teman = wt('teman')

    fdir = os.path.join(OUT, 'frames')
    os.makedirs(fdir, exist_ok=True)
    for fi in range(nfr):
        t = fi / FPS
        fr = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        if t < base_dur:
            in_cut = cut_in <= t <= cut_out
            if in_cut:
                k_in = ease_out((t - cut_in) / 0.22)
                k_out = ease_out((cut_out - t) / 0.18)
                a = min(k_in, k_out)
                bgp = paper.copy()
                bgp.putalpha(int(255 * a))
                fr.alpha_composite(bgp)
                card = compare_card((t - cut_in - 0.15) / max(0.1, cut_out - cut_in - 0.8))
                place(fr, card, W / 2, H * 0.43 + (1 - k_in) * 120, 1.12 - 0.12 * k_in, a)
            else:
                # title (segment A)
                s1, a1 = pop(t, 0.10, seg_t[0][1] - 0.03, 0.32)
                s2, a2 = pop(t, 0.28, seg_t[0][1] - 0.03, 0.32)
                place(fr, t_l1, W / 2 - 40, 170, s1, a1, rot=4)
                place(fr, t_l2, W / 2 + 60, 300, s2, a2, rot=4)
                # segment B: quit job? -> no need
                b1 = seg_t[1][1] - 0.04
                s, a = pop(t, t_berhenti - 0.08, b1)
                place(fr, p_stop, W / 2 - 60, 180, s, a)
                s, a = pop(t, t_tak2 - 0.05, b1)
                place(fr, p_no, W / 2 + 60, 320, s, a)
                # segment C before cutaway: happy
                s, a = pop(t, t_happy - 0.08, cut_in, 0.34)
                place(fr, p_happy, W / 2 - 70, 200, s, a)
                place(fr, face, W - 150, 330, s, a, rot=-12 + 8 * math.sin(t * 6))
                # segment D: Alhamdulillah + sparkles
                d1 = seg_t[3][1] - 0.02
                s, a = pop(t, t_alh + 0.02, d1, 0.3, 0.12)
                place(fr, p_alh, W / 2, 230, s, a)
                for j, (sp, (cx, cy), dt) in enumerate(zip(spk, ((210, 140), (880, 150), (150, 330), (930, 330)), (0, .06, .1, .14))):
                    s2_, a2_ = pop(t, t_alh + dt, d1, 0.25, 0.12)
                    place(fr, sp, cx, cy, s2_, a2_, rot=(t * 90 + j * 30) % 90)
                # segment E: bus -> tickets
                s, a = pop(t, t_semua - 0.08, t_dua - 0.1)
                place(fr, p_bus, W / 2, 230, s, a)
                e1 = seg_t[4][1] - 0.03
                s, a = pop(t, t_dua - 0.08, e1, 0.34)
                s2, a2 = pop(t, t_dua + 0.1, e1, 0.34)
                place(fr, tk1, W / 2 - 140, 330, s * 0.92, a, rot=7)
                place(fr, tk2, W / 2 + 130, 360, s2 * 0.92, a2, rot=-5)
                s3, a3 = pop(t, t_dua + 0.25, e1, 0.3)
                place(fr, x2, W - 130, 520, s3, a3, rot=-10)
                # segment F: teman saya lagi
                s, a = pop(t, t_teman - 0.08, seg_t[5][1] - 0.03)
                place(fr, p_teman, W / 2, 230, s, a)
                place(fr, wm, W - 110, H - 330, 1, 0.9)
            for a0, a1, w in cap_win:
                if a0 <= t < a1:
                    k = (t - a0) / 0.09
                    place(fr, cap(w), W / 2, H * 0.875, 0.82 + 0.18 * back_out(min(1, k)) if k < 1 else 1, 1)
                    break
            for o in offs[1:]:
                if abs(t - o) < 0.05:
                    fr.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(70 * (1 - abs(t - o) / 0.05)))))
        else:
            fr = outro_frame(t - base_dur, fi, logo_w)
        fr.save(os.path.join(fdir, f'f{fi:05d}.png'), compress_level=1)
        if fi % 90 == 0:
            print('frame', fi, '/', nfr, flush=True)

    pops = (0.10, 0.28, t_berhenti - 0.08, t_tak2 - 0.05, t_happy - 0.08, t_alh, t_semua - 0.08,
            t_dua - 0.08, t_dua + 0.1, t_teman - 0.08)
    whooshes = ((cut_in - 0.12, 0.35, 0.18), (cut_out - 0.15, 0.35, 0.18), (base_dur - 0.15, 0.5, 0.22))
    write_sfx(total, pops, whooshes, os.path.join(OUT, 'sfx.wav'))
    final = os.path.join(OUT, 'PartTime_PG_Norway_AzlanEza.mp4')
    composite(os.path.join(OUT, 'base.mov'), fdir, os.path.join(OUT, 'sfx.wav'), total, final)
    print('done', final, 'base', round(base_dur, 2), 'total', round(total, 2))


if __name__ == '__main__':
    main()
