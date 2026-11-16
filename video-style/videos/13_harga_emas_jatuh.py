#!/usr/bin/env python3
"""Video 13: "Harga emas tengah jatuh" (Eza, studio talking head with gold bars), edited with HyperFrames.

Stage 1 (this file, Python + ffmpeg): cut list from the Descript SRT + speech energy, retakes removed,
pauses tightened, graded base video with exact frame counts (A/V sync), word timings in output time.
Stage 2 (this file): writes the HyperFrames project (index.html + scene sub-compositions + captions),
music bed with a ducking lane, and bundled Pixabay SFX. HyperFrames renders the final MP4.

python3 13_harga_emas_jatuh.py edl       -> print the cut list / kept text
python3 13_harga_emas_jatuh.py base      -> render work/13/proj/assets/base.mp4
python3 13_harga_emas_jatuh.py project   -> (re)write the HyperFrames project
"""
import json, os, re, subprocess, sys, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
WORK = os.path.join(REPO, 'work', '13')
RAW = os.path.join(WORK, 'raw', 'raw.mov')
WAV16 = os.path.join(WORK, 'raw', 'audio16k.wav')
PROJ = os.path.join(WORK, 'proj')
SRT = os.path.join(HERE, '13_assets', 'transcript.srt')
FPS = 30

# ------------------------------------------------------------------ edit decisions (Descript cue numbers)
# Dropped: 2 (filler "Tapi saya nak tanya satu soalan"), 24-26 (retakes of the holding-period line, kept 27-28),
# 29-30 (unfinished, redone as 31-32), 36-39 (repeats of "harga boleh naik dan turun", kept 40),
# 41 ("Haa..."), 45-49 (stumbled CTA retakes, kept the clean last take 50).
KEEP = [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 27, 28,
        31, 32, 33, 34, 35, 40, 42, 43, 44, 50]
# Trims inside a cue: cue 14 starts on the second "saya nak"; cue 50 starts on the last "kalau" of cue 49.
OVERRIDE = {14: dict(s=60.40, text='Saya nak kongsi satu perkara.'),
            50: dict(s=243.30, text='Kalau anda nak menyimpan emas Public Gold dengan betul, boleh terus follow saya')}
MAX_GAP = 0.30     # pauses longer than this are cut
PAD = 0.08         # speech padding kept on each side of a cut


def parse_srt(path):
    cues = {}
    for blk in open(path, encoding='utf-8').read().strip().split('\n\n'):
        ln = blk.strip().split('\n')
        n = int(ln[0])
        a, b = ln[1].split(' --> ')
        ts = lambda s: sum(float(x) * m for x, m in zip(s.replace(',', '.').split(':'), (3600, 60, 1)))
        cues[n] = dict(n=n, s=ts(a), e=ts(b), text=' '.join(ln[2:]))
    return cues


def speech_regions():
    w = wave.open(WAV16)
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    hop = 160
    n = len(x) // hop
    e = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1))
    db = 20 * np.log10(e + 1e-6)
    sp = db > np.percentile(db, 10) + 14
    regs, i = [], 0
    while i < n:
        if sp[i]:
            j = i
            while j < n and (sp[j] or sp[j:j + 15].any()):
                j += 1
            if j - i >= 8:
                regs.append((i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    return regs


SYL = {'Public': 2, 'Gold': 1, 'spread': 1, 'follow': 2}


def syl(w):
    w = w.strip('.,?!…-')
    return SYL.get(w, max(1, len(re.findall(r'[aeiouAEIOU]+', w))))


def build():
    cues, regs = parse_srt(SRT), speech_regions()
    pieces, words = [], []          # pieces: source (a, b) with speech; words: per cue
    for n in KEEP:
        c = dict(cues[n]); c.update(OVERRIDE.get(n, {}))
        r = [(max(a, c['s'] - 0.06), min(b, c['e'] + 0.12)) for a, b in regs if b > c['s'] - 0.06 and a < c['e'] + 0.12]
        r = [(a, b) for a, b in r if b - a > 0.05]
        if not r:
            raise SystemExit(f'no speech in cue {n}')
        pieces.append(dict(n=n, regs=r, text=c['text']))
        toks = c['text'].split()
        wts = np.array([syl(t) for t in toks], float)
        tot = sum(b - a for a, b in r)
        cum = np.concatenate([[0], np.cumsum(wts)]) / wts.sum() * tot

        def sp2t(x):
            for a, b in r:
                if x <= b - a + 1e-9:
                    return a + x
                x -= b - a
            return r[-1][1]
        for i, t in enumerate(toks):
            words.append(dict(cue=n, w=t, s=sp2t(cum[i] + 1e-4), e=sp2t(cum[i + 1])))
    # flatten speech regions -> keep ranges, merging short gaps
    allr = [rg for p in pieces for rg in p['regs']]
    segs = []
    for a, b in allr:
        a, b = a - PAD, b + PAD
        if segs and a - segs[-1][1] <= MAX_GAP and a > segs[-1][0]:
            segs[-1][1] = max(segs[-1][1], b)
        else:
            segs.append([a, b])
    # snap to the frame grid
    segs = [(round(a * FPS) / FPS, round(b * FPS) / FPS) for a, b in segs]
    offs, t = [], 0.0
    for a, b in segs:
        offs.append(t); t += b - a

    def s2o(x):
        best = None
        for (a, b), o in zip(segs, offs):
            if a - 1e-6 <= x <= b + 1e-6:
                return o + x - a
            if x < a:
                return o if best is None else best
            best = o + b - a
        return best
    for w in words:
        w['os'], w['oe'] = round(s2o(w['s']), 3), round(s2o(w['e']), 3)
    return segs, words, t, pieces


def render_base(segs):
    os.makedirs(os.path.join(PROJ, 'assets'), exist_ok=True)
    tmp = os.path.join(WORK, 'segs'); os.makedirs(tmp, exist_ok=True)
    grade = ("eq=contrast=1.05:saturation=1.06:gamma=0.98,"
             "colorbalance=rm=0.02:gm=0.005:bm=-0.02:rh=0.01:bh=-0.01,unsharp=5:5:0.3")
    parts = []
    for i, (a, b) in enumerate(segs):
        n = int(round((b - a) * FPS))
        p = os.path.join(tmp, f's{i:03d}.mov')
        af = (f"aresample=48000,apad,atrim=end_sample={int(round(n / FPS * 48000))},"
              f"afade=t=in:d=0.025,afade=t=out:st={n / FPS - 0.025:.3f}:d=0.025")
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.4f}', '-t', f'{b - a + 0.3:.4f}', '-i', RAW,
                        '-filter_complex', f"[0:v]fps={FPS},{grade},format=yuv420p,trim=end_frame={n},"
                        f"setpts=PTS-STARTPTS[v];[0:a]{af}[au]", '-map', '[v]', '-map', '[au]',
                        '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', '-c:a', 'pcm_s16le', '-ac', '2',
                        '-video_track_timescale', '30000', p], check=True)
        parts.append(p)
    lst = os.path.join(tmp, 'list.txt')
    open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    cat = os.path.join(tmp, 'cat.mov')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', cat], check=True)
    # voice polish: rumble cut, gentle presence, level; keyframe every second so seeking never freezes
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', cat, '-c:v', 'libx264', '-crf', '16', '-preset', 'medium',
                    '-g', str(FPS), '-pix_fmt', 'yuv420p',
                    '-af', 'highpass=f=80,equalizer=f=3000:t=q:w=1:g=2,loudnorm=I=-16:TP=-1.5:LRA=9',
                    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart',
                    os.path.join(PROJ, 'assets', 'base.mp4')], check=True)


if __name__ == '__main__':
    segs, words, total, pieces = build()
    os.makedirs(PROJ, exist_ok=True)
    json.dump(dict(segs=segs, words=words, total=total), open(os.path.join(WORK, 'edl.json'), 'w'), indent=1)
    if 'edl' in sys.argv:
        for p in pieces:
            ws = [w for w in words if w['cue'] == p['n']]
            print(f"{ws[0]['os']:7.2f}  [{p['n']:2d}] {p['text']}")
        print(f'segments {len(segs)}, total {total:.2f}s')
    if 'base' in sys.argv:
        render_base(segs)
    if 'project' in sys.argv:
        import importlib.util
        spec = importlib.util.spec_from_file_location('hf13', os.path.join(HERE, '13_assets', 'hf_project.py'))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        m.write_project(PROJ, words, total)
