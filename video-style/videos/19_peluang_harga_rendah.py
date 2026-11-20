#!/usr/bin/env python3
"""Video 19: harga rendah = peluang menabung (voiceover only, full motion graphics), HyperFrames. Same cut pipeline as video 13;
`base` renders the cut voice (assets/voice.wav) instead of a base video.

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
WORK = os.path.join(REPO, 'work', '19')
RAW = os.path.join(WORK, 'raw', 'raw.m4a')
WAV16 = os.path.join(WORK, 'raw', 'audio16k.wav')
PROJ = os.path.join(WORK, 'proj')
SRT = os.path.join(HERE, '19_assets', 'transcript.srt')
FPS = 30

# ------------------------------------------------------------------ edit decisions (Descript cue numbers)
# Dropped: 15-16 ("Dengan duit yang sama, kita bal--" retakes), 38 + first half of 39 ("jangan sibuk tengok" x4),
# first "Yang ketiga, bank pusat dunia pun ag--" (29), "Orang yang sabar meram em," (43), first "Dan yang terakhir," (45).
KEEP = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
        33, 34, 35, 36, 37, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55]
OVERRIDE = {29: dict(s=139.1, text='Yang ketiga, bank pusat'),
            39: dict(s=184.75, text='jangan sibuk tengok carta setiap hari dan jangan'),
            43: dict(s=200.88, text='orang yang sabar peram emas selalunya yang paling'),
            45: dict(s=209.85, text='Dan yang terakhir, gunakan duit yang betul.')}
SKIP = []
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
    floor = np.percentile(db, 10)
    thr, thr_low = floor + 14, floor + 7
    sp = db > thr
    regs, i = [], 0
    while i < n:
        if sp[i]:
            j = i
            while j < n and (sp[j] or sp[j:j + 15].any()):
                j += 1
            if j - i >= 8:
                # follow a soft word ending (e.g. the trailing "-rah" of "murah") down to near-silence, but stop
                # at a new onset (energy rising back over the speech threshold); likewise for soft onsets
                e = j
                while e < min(n - 10, j + 45) and db[e:e + 6].max() > thr_low and db[e] <= thr:
                    e += 1
                s0 = i
                while s0 > max(10, i - 15) and db[s0 - 6:s0].max() > thr_low and db[s0 - 1] <= thr:
                    s0 -= 1
                regs.append((i * 0.01, j * 0.01, s0 * 0.01, e * 0.01))
            i = j
        else:
            i += 1
    return regs


SYL = {'RM503': 8, 'RM764': 11, '34%': 6, 'RM1,000': 5, '1.31': 7, '1.99': 9, '0.68': 7, '52%': 7, 'kilogram': 3}


def syl(w):
    w = w.strip('.,?!…-')
    return SYL.get(w, max(1, len(re.findall(r'[aeiouAEIOU]+', w))))


def build():
    cues, regs = parse_srt(SRT), speech_regions()
    pieces, words = [], []          # pieces: source (a, b) with speech; words: per cue
    for n in KEEP:
        c = dict(cues[n]); c.update(OVERRIDE.get(n, {}))
        hit = [g for g in regs if g[1] > c['s'] - 0.06 and g[0] < c['e'] + 0.12]
        hit = [g for g in hit if min(g[1], c['e'] + 0.12) - max(g[0], c['s'] - 0.06) > 0.05]
        cut = []
        for a, b, ae, be in hit:                    # subtract SKIP intervals (may split one region in two)
            parts = [(a, b, ae, be)]
            for x0, x1 in SKIP:
                nxt = []
                for pa, pb, pae, pbe in parts:
                    if pb <= x0 or pa >= x1:
                        nxt.append((pa, pb, pae, pbe)); continue
                    if pa < x0:
                        nxt.append((pa, x0, pae, x0))
                    if pb > x1:
                        nxt.append((x1, pb, x1, pbe))
                parts = nxt
            cut += [q for q in parts if min(q[1], c['e'] + 0.12) - max(q[0], c['s'] - 0.06) > 0.05]
        hit = cut
        r = [(max(a, c['s'] - 0.06), min(b, c['e'] + 0.12)) for a, b, _, _ in hit]
        ext = [(max(ae, c['s'] - 0.25), min(be, c['e'] + 0.45)) for _, _, ae, be in hit]
        if not r:
            raise SystemExit(f'no speech in cue {n}')
        pieces.append(dict(n=n, regs=r, ext=ext, text=c['text']))
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
    # merge on the core speech regions; then let each cut point follow the word's soft tail/onset
    allr = [(a, b, ae, be) for p in pieces for (a, b), (ae, be) in zip(p['regs'], p['ext'])]
    segs = []
    for a, b, ae, be in allr:
        lo, hi = min(a - PAD, ae - 0.03), max(b + PAD, be + 0.08)
        if segs and a - (segs[-1][2] + PAD) <= MAX_GAP and a > segs[-1][0]:
            segs[-1][1] = max(segs[-1][1], hi)
            segs[-1][2] = max(segs[-1][2], b)
        else:
            segs.append([lo, hi, b])
    segs = [s_[:2] for s_ in segs]
    for k in range(len(segs) - 1):        # tails must never run into the next kept piece
        if segs[k][1] > segs[k + 1][0] and segs[k][0] < segs[k + 1][0]:
            mid = (segs[k][1] + segs[k + 1][0]) / 2
            segs[k][1], segs[k + 1][0] = mid, mid
    # snap to the frame grid
    segs = [(round(a * FPS) / FPS, round(b * FPS) / FPS) for a, b in segs]
    offs, t = [], 0.0
    for a, b in segs:
        offs.append(t); t += b - a

    def s2o(x):
        for (a, b), o in zip(segs, offs):          # containment first: kept pieces may be out of source order
            if a - 1e-6 <= x <= b + 1e-6:
                return o + x - a
        near = min(zip(segs, offs), key=lambda so: min(abs(x - so[0][0]), abs(x - so[0][1])))
        (a, b), o = near
        return o if x < a else o + b - a
    for w in words:
        w['os'], w['oe'] = round(s2o(w['s']), 3), round(s2o(w['e']), 3)
    return segs, words, t, pieces


def render_base(segs):
    """Voiceover only: cut and join the speech with 25 ms fades, frame-exact lengths; voice polish + level."""
    os.makedirs(os.path.join(PROJ, 'assets'), exist_ok=True)
    fc, ins = '', []
    for i, (a, b) in enumerate(segs):
        n = int(round((b - a) * FPS))
        d = n / FPS
        fc += (f"[0:a]atrim=start={a:.4f}:end={a + d + 0.2:.4f},asetpts=PTS-STARTPTS,aresample=48000,apad,"
               f"atrim=end_sample={int(round(d * 48000))},afade=t=in:d=0.025,afade=t=out:st={d - 0.025:.3f}:d=0.025[s{i}];")
    fc += ''.join(f'[s{i}]' for i in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1,highpass=f=80,"
    fc += "equalizer=f=3000:t=q:w=1:g=2,loudnorm=I=-16:TP=-1.5:LRA=9[o]"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', RAW, '-filter_complex', fc, '-map', '[o]', '-ar', '48000',
                    '-c:a', 'pcm_s16le', os.path.join(PROJ, 'assets', 'voice.wav')], check=True)


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
        spec = importlib.util.spec_from_file_location('hf13', os.path.join(HERE, '19_assets', 'hf_project.py'))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        m.write_project(PROJ, words, total)
