#!/usr/bin/env python3
"""Video 12: lifestyle montage, the routine NDO Fizikal class in Kuching (every 2nd week).
3 phone clips + 4 photos, NO subtitles, natural room audio, Azlan & Eza brand kit.

Every frame is built in Python (video frames decoded through ffmpeg pipes) so whip-blur cuts,
Ken Burns photos, polaroids and the framed group clip all share one timeline.

python3 12_ndo_fizikal_kuching.py --preview   -> storyboard (TikTok safe zones drawn) + 30 fps 720p demo
python3 12_ndo_fizikal_kuching.py             -> full 1080x1920 render
"""
import importlib.util, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_VS = os.path.join(HERE, '..')
sys.path.insert(0, REPO_VS)
import numpy as np
import build as B
from build import (W, H, FPS, OUTRO, RED, F_XB, F_B, Image, ImageDraw, ImageFilter, text_sprite, rounded,
                   with_shadow, place, pop, fit_pill, pin_icon, cal_icon, ease_out, back_out, load_logos,
                   outro_frame, write_sfx, audio_mix_graph, TT_CENTER_X, TT_TOP, TT_BOTTOM, TT_RIGHT, TT_RAIL_Y)

WORK = os.environ.get('WORK', os.path.join(REPO_VS, '..', 'work', '12'))
RAWD = os.path.join(WORK, 'raw')
OUT = os.path.join(WORK, 'out')
os.makedirs(OUT, exist_ok=True)
V1, V2, V3 = (os.path.join(RAWD, f) for f in ('v1.mov', 'v2.mov', 'v3.mp4'))
# p3.jpg (class photo) was removed at the user's request.
P_GROUP1, P_GROUP2, P_LOBBY = (os.path.join(RAWD, f) for f in ('p1.jpg', 'p2.jpg', 'p4.jpg'))

# Bright, clean lifestyle grade: gentle contrast, warm mids, a touch of saturation (white training room).
GRADE = ("eq=contrast=1.06:saturation=1.10:gamma=0.97,"
         "colorbalance=rs=-0.02:bs=0.03:rm=0.03:gm=0.005:bm=-0.025:rh=0.01:bh=-0.01,unsharp=5:5:0.25")

# Scene list. kind: 'vid' (full-bleed vertical clip), 'photo' (Ken Burns), 'polaroid', 'card' (framed clip).
# audio = (file, start): the natural sound under the scene (J/L-cuts keep the room sound continuous).
SCENES = [
    dict(kind='vid', src=V1, a=0.20, d=2.40, audio=(V1, 0.20), tag='title'),          # presenter opens
    dict(kind='vid', src=V1, a=4.80, d=3.00, audio=(V1, 4.80), tag='loc'),   # pan across participants
    dict(kind='vid', src=V1, a=10.0, d=3.40, audio=(V1, 10.0), tag='cal'),
    dict(kind='vid', src=V2, a=5.50, d=4.00, audio=(V2, 5.50)),          # presenter walks the room
    dict(kind='vid', src=V2, a=12.0, d=3.80, audio=(V2, 12.0)),
    dict(kind='vid', src=V1, a=17.0, d=2.40, audio=(V1, 17.0)),
    # user: lobby photo moved towards the end, captioned "Sesi Private coaching dengan dealer"
    dict(kind='photo', src=P_LOBBY, d=2.80, audio=(V2, 0.0), kb=(1.00, 1.09, 0.55, 0.45), tag='coach'),
    dict(kind='polaroid', d=2.80, audio=(V3, 0.0)),                     # group photos drop in
    dict(kind='card', src=V3, a=2.80, d=7.80, audio=(V3, 2.80), gain=-5),  # group wave
]
WHIP = 4          # frames of directional blur on each side of a whip cut
for s in SCENES:
    s['n'] = int(round(s['d'] * FPS))
starts = np.cumsum([0] + [s['n'] for s in SCENES])
NMAIN = int(starts[-1])
NTOT = NMAIN + int(round(OUTRO * FPS))
TOTAL = NTOT / FPS
SC_T0 = [f / FPS for f in starts]


# ---------------------------------------------------------------- sources
def vid_frames(path, a, n, w=W, h=H, cover=True):
    """Graded rgb frames of a clip, exactly n frames at 30 fps (last frame held if the clip runs short)."""
    fit = (f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}" if cover
           else f"scale={w}:-2")
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{a}', '-i', path, '-vf', f"fps={FPS},{fit},setsar=1,{GRADE}",
           '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    fh = h if cover else CARD_H
    last = None
    for i in range(n):
        buf = p.stdout.read(w * fh * 3)
        if len(buf) == w * fh * 3:
            last = np.frombuffer(buf, np.uint8).reshape(fh, w, 3)
        yield last
    p.stdout.close(); p.wait()


def graded_image(path, w, h):
    """Photo -> cover-cropped to w x h, same grade as the clips."""
    out = os.path.join(OUT, os.path.basename(path) + f'_{w}x{h}.png')
    if not os.path.exists(out):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-vf',
                        f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,{GRADE}",
                        '-frames:v', '1', out], check=True)
    return Image.open(out).convert('RGB')


CARD_W = 880
CARD_H = int(round(CARD_W * 480 / 848 / 2)) * 2      # v3 is 848x480 landscape


# ---------------------------------------------------------------- graphics
def title_sprites():
    l1 = text_sprite('RUTIN SETIAP', 92, RED, (150, 20, 36), stroke=10, stroke_col=(255, 255, 255))
    l2 = text_sprite('MINGGU KE-2', 124, (255, 255, 255), (247, 228, 160), stroke=8, stroke_col=(20, 20, 30))
    return l1, l2


def polaroid(path, pw=720, cap=None):
    ph = int(pw * 0.75)
    ph_im = graded_image(path, pw, ph).convert('RGBA')
    bd, bot = 22, 96
    im = rounded((pw + bd * 2, ph + bd + bot), 10, (253, 252, 248, 255))
    im.alpha_composite(ph_im, (bd, bd))
    if cap:
        d = ImageDraw.Draw(im)
        d.text((im.width / 2, ph + bd + bot / 2), cap, font=B.font(F_B, 44), fill=(40, 40, 50, 255), anchor='mm')
    return with_shadow(im, 24, 14, 0.5)


def caption_card(line1, line2):
    """Two-line white caption card (brand-red accent bar) for longer captions."""
    f1, f2 = B.font(F_XB, 60), B.font(F_B, 50)
    w = int(max(f1.getlength(line1), f2.getlength(line2))) + 110
    h = 190
    im = rounded((w, h), 34, (255, 255, 255, 248))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([26, 34, 38, h - 34], 6, fill=RED + (255,))
    d.text((64, 62), line1, font=f1, fill=(20, 20, 30, 255), anchor='lm')
    d.text((64, 134), line2, font=f2, fill=RED + (255,), anchor='lm')
    return with_shadow(im, 18, 10, 0.4)


def whip_blur(arr, k, direction=1):
    """Horizontal motion blur of strength k (0..1), plus a slide in `direction`."""
    if k <= 0.01:
        return arr
    small = arr[::2, ::2].astype(np.float32)
    span = int(6 + 70 * k)                      # smooth box blur (cumulative sum), edge-padded
    pad = np.pad(small, ((0, 0), (span, span), (0, 0)), mode='edge')
    cs = np.cumsum(pad, axis=1)
    cs = np.concatenate([np.zeros_like(cs[:, :1]), cs], axis=1)
    acc = (cs[:, 2 * span:2 * span + small.shape[1]] - cs[:, :small.shape[1]]) / (2 * span)
    up = np.asarray(Image.fromarray(acc.clip(0, 255).astype(np.uint8)).resize((arr.shape[1], arr.shape[0]),
                                                                              Image.BILINEAR))
    shift = int(direction * 140 * k)
    return np.roll(up, shift, axis=1)


def blur_bg(arr, dark=0.72):
    im = Image.fromarray(arr).resize((W // 10, H // 10), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3))
    im = im.resize((W, H), Image.BILINEAR)
    return (np.asarray(im, np.float32) * dark).astype(np.uint8)


# ---------------------------------------------------------------- timeline
def frames(preview_stills=None):
    """Yield (global frame index, RGB numpy frame). preview_stills: set of frame indices to yield only."""
    logo, logo_w = load_logos()
    wm = logo_w.resize((150, int(150 * logo_w.height / logo_w.width)), Image.LANCZOS)
    wm.putalpha(wm.getchannel('A').point(lambda v: int(v * 0.9)))
    l1, l2 = title_sprites()
    loc = fit_pill('NDO Fizikal  •  Kuching', icon=pin_icon(54), size=50)
    city = fit_pill('Kuching, Sarawak', icon=pin_icon(54), size=50)
    coach = caption_card('Sesi Private coaching', 'dengan dealer')
    cal = fit_pill('Setiap minggu ke-2', icon=cal_icon(50), size=48)
    # user: closing line "Yang nak explore bisnes Public Gold boleh join kami!" (2 lines, shrunk to the safe width)
    lines = ('Yang nak explore bisnes', 'Public Gold boleh join kami!')
    sz = 80          # one size for both lines: shrink until the longer line fits the safe width
    while sz > 40 and max(B.font(F_XB, sz).getlength(ln) + 12 for ln in lines) > 840:
        sz -= 2
    bye = [text_sprite(ln, sz, (255, 255, 255), (247, 228, 160), stroke=6, stroke_col=(20, 20, 30))
           for ln in lines]
    ndo = text_sprite('NDO FIZIKAL', 110, RED, (150, 20, 36), stroke=9, stroke_col=(255, 255, 255))
    pol1, pol2 = polaroid(P_GROUP1, cap='Kuching'), polaroid(P_GROUP2, cap='NDO Fizikal')
    photos = {}
    rng = np.random.default_rng(7)

    for si, sc in enumerate(SCENES):
        f0, n = int(starts[si]), sc['n']
        want = None if preview_stills is None else [f - f0 for f in preview_stills if f0 <= f < f0 + n]
        if want == []:
            continue
        if sc['kind'] == 'vid':
            src = vid_frames(sc['src'], sc['a'], n)
        elif sc['kind'] == 'card':
            src = vid_frames(sc['src'], sc['a'], n, w=CARD_W, cover=False)
        elif sc['kind'] == 'photo':
            if sc['src'] not in photos:
                photos[sc['src']] = graded_image(sc['src'], int(W * 1.12), int(H * 1.12))
            src = None
        else:
            bgp = blur_bg(np.asarray(graded_image(P_GROUP1, W, H)), 0.6)
            src = None
        for i in range(n):
            arr = next(src) if src is not None else None
            if want is not None and i not in want:
                continue
            t = i / FPS
            gt = (f0 + i) / FPS
            k = i / max(1, n - 1)
            if sc['kind'] == 'vid':
                base = arr
            elif sc['kind'] == 'photo':
                z0, z1, cx, cy = sc['kb']
                z = z0 + (z1 - z0) * (3 * k * k - 2 * k ** 3)
                im = photos[sc['src']]
                cw, ch = im.width / z / 1.12 * 1.0, im.height / z / 1.12
                x0 = (im.width - cw) * cx
                y0 = (im.height - ch) * cy
                base = np.asarray(im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)))
            elif sc['kind'] == 'polaroid':
                base = bgp
            else:  # framed group clip on its own blurred copy
                big = np.asarray(Image.fromarray(arr).resize((int(H * CARD_W / CARD_H), H), Image.BILINEAR))
                xo = (big.shape[1] - W) // 2
                base = blur_bg(np.ascontiguousarray(big[:, xo:xo + W]), 0.62)
            fr = Image.fromarray(base).convert('RGBA')

            # ---- scene overlays
            tag = sc.get('tag')
            if tag == 'title':
                s1, a1 = pop(t, 0.15, 2.40, 0.40, 0.01)
                s2, a2 = pop(t, 0.45, 2.40, 0.40, 0.01)
                place(fr, l1, TT_CENTER_X - 40, 330, s1, a1, rot=4)
                place(fr, l2, TT_CENTER_X + 20, 450, s2, a2, rot=4)
            if tag == 'loc':
                s, a = pop(t, 0.20, 2.90, 0.35, 0.20)
                place(fr, loc, TT_CENTER_X, 330, s, a)
            if tag == 'coach':
                s, a = pop(t, 0.20, sc['d'], 0.35, 0.01)
                place(fr, coach, TT_CENTER_X, 360, s, a)
            if tag == 'cal':
                s, a = pop(t, 0.30, 3.30, 0.35, 0.20)
                place(fr, cal, TT_CENTER_X, 330, s, a)
            if sc['kind'] == 'polaroid':
                for spr, tin, rot, dx, dy in ((pol1, 0.0, -6, -18, -10), (pol2, 0.9, 5, 22, 40)):
                    if t >= tin:
                        q = ease_out((t - tin) / 0.55)
                        place(fr, spr, TT_CENTER_X + dx, 900 + dy - (1 - q) * 1300, 1.0 + 0.25 * (1 - q),
                              min(1, q * 2), rot=rot + (1 - q) * 18)
                s, a = pop(t, 0.2, sc['d'], 0.4, 0.01)
                place(fr, ndo, TT_CENTER_X, 300, s, a, rot=-3)
            if sc['kind'] == 'card':
                q = ease_out(t / 0.45)
                card = Image.fromarray(arr).convert('RGBA')
                frame_im = rounded((CARD_W + 28, CARD_H + 28), 26, (255, 255, 255, 255))
                m = Image.new('L', card.size, 0)
                ImageDraw.Draw(m).rounded_rectangle([0, 0, CARD_W - 1, CARD_H - 1], 16, fill=255)
                card.putalpha(m)
                frame_im.alpha_composite(card, (14, 14))
                place(fr, with_shadow(frame_im, 24, 14, 0.5), TT_CENTER_X, 900 + (1 - q) * 160,
                      0.9 + 0.1 * q, q)
                place(fr, ndo, TT_CENTER_X, 330, 1, 1, rot=-3)
                s, a = pop(t, 0.3, sc['d'], 0.35, 0.01)
                place(fr, city, TT_CENTER_X, 480, s, a)
                s, a = pop(t, 1.6, sc['d'], 0.45, 0.01)
                s2, a2 = pop(t, 1.85, sc['d'], 0.45, 0.01)
                place(fr, bye[0], TT_CENTER_X, 1270, s, a, rot=-2)
                place(fr, bye[1], TT_CENTER_X, 1375, s2, a2, rot=-2)
            place(fr, wm, 95 + 40, 1010, 1, 1)

            out = np.asarray(fr.convert('RGB'))
            # ---- cut transitions: whip blur out of / into the cut, faint white flash on the first frame
            d = 1 if si % 2 == 0 else -1
            if si < len(SCENES) - 1 and i >= n - WHIP:
                out = whip_blur(out, (i - (n - WHIP) + 1) / WHIP, d)
            if si > 0 and i < WHIP:
                pd = 1 if (si - 1) % 2 == 0 else -1
                out = whip_blur(out, (WHIP - i) / WHIP, -pd * -1)
                if i == 0:
                    out = (out.astype(np.float32) * 0.75 + 255 * 0.25).astype(np.uint8)
            yield f0 + i, out

    for i in range(NTOT - NMAIN):
        f = NMAIN + i
        if preview_stills is not None and f not in preview_stills:
            continue
        yield f, np.asarray(outro_frame(i / FPS, i, logo_w).convert('RGB'))


# ---------------------------------------------------------------- audio
def build_audio(path):
    parts, fc = [], ''
    for j, sc in enumerate(SCENES):
        f, a = sc['audio']
        n = sc['n']
        parts += ['-ss', f'{a}', '-t', f'{n / FPS + 0.3}', '-i', f]
        g = sc.get('gain', 0)
        fc += (f"[{j}:a]aresample=48000,aformat=channel_layouts=stereo,volume={g}dB,apad,"
               f"atrim=end_sample={int(round(n / FPS * 48000))},afade=t=in:d=0.08,"
               f"afade=t=out:st={n / FPS - 0.08:.3f}:d=0.08[s{j}];")
    fc += ''.join(f'[s{j}]' for j in range(len(SCENES))) + f"concat=n={len(SCENES)}:v=0:a=1[cat]"
    voice = os.path.join(OUT, 'nat.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + parts + ['-filter_complex', fc, '-map', '[cat]', voice],
                   check=True)
    sfx = os.path.join(OUT, 'sfx.wav')
    cuts = SC_T0[1:-1]
    whoosh = [(c - 0.18, 0.36, 0.05) for c in cuts] + [(NMAIN / FPS - 0.2, 0.6, 0.08)]
    pops = [SC_T0[1] + 0.2, SC_T0[2] + 0.3, SC_T0[6] + 0.2, SC_T0[7] + 0.05, SC_T0[7] + 0.95, SC_T0[8] + 1.6]
    write_sfx(TOTAL, pops, whoosh, sfx)
    g = audio_mix_graph('[0:a]', '[1:a]', TOTAL, outro_at=NMAIN / FPS)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', voice, '-i', sfx, '-filter_complex', g, '-map', '[a]',
                    '-c:a', 'pcm_s16le', path], check=True)


# ---------------------------------------------------------------- output
def encode(final, scale=None, crf=19):
    aud = os.path.join(OUT, 'mix.wav')
    build_audio(aud)
    vf = f"scale={scale}:flags=lanczos," if scale else ''
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', '-', '-i', aud, '-map', '0:v', '-map', '1:a', '-vf', vf + 'format=yuv420p',
           '-c:v', 'libx264', '-crf', str(crf), '-preset', 'medium', '-c:a', 'aac', '-b:a', '160k',
           '-movflags', '+faststart', '-shortest', final]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f, arr in frames():
        p.stdin.write(np.ascontiguousarray(arr).tobytes())
        if f % 150 == 0:
            print(f'frame {f}/{NTOT}', flush=True)
    p.stdin.close(); p.wait()


def zones(im):
    o = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(o)
    d.rectangle([0, 0, W, TT_TOP], fill=(255, 0, 0, 70))
    d.rectangle([0, TT_BOTTOM, W, H], fill=(255, 0, 0, 70))
    d.rectangle([TT_RIGHT, TT_RAIL_Y[0], W, TT_RAIL_Y[1]], fill=(255, 0, 0, 70))
    im = im.convert('RGBA'); im.alpha_composite(o)
    return im


def storyboard(path):
    picks = []
    for si, sc in enumerate(SCENES):
        picks.append(int(starts[si]) + int(sc['n'] * 0.6))
    picks.append(NMAIN + 50)
    got = dict(frames(set(picks)))
    th = [zones(Image.fromarray(got[f])).resize((270, 480), Image.LANCZOS) for f in picks]
    cols = 6
    rows = (len(th) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * 280 + 10, rows * 530 + 10), (245, 245, 245))
    d = ImageDraw.Draw(sheet)
    for j, (f, im) in enumerate(zip(picks, th)):
        x, y = 10 + (j % cols) * 280, 10 + (j // cols) * 530
        sheet.paste(im.convert('RGB'), (x, y))
        d.text((x, y + 486), f'{j + 1}. {f / FPS:0.1f}s', font=B.font(F_B, 26), fill=(30, 30, 40))
    sheet.save(path, quality=90)


if __name__ == '__main__':
    print(f'total {TOTAL:.2f}s ({NMAIN / FPS:.2f}s + outro)')
    if '--preview' in sys.argv:
        storyboard(os.path.join(OUT, 'PREVIEW_storyboard_safezone.jpg'))
        encode(os.path.join(OUT, 'PREVIEW_demo_720p.mp4'), scale='720:1280', crf=20)
    else:
        encode(os.path.join(OUT, '12_ndo_fizikal_kuching.mp4'))
