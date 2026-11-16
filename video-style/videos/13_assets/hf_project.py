"""Writes the HyperFrames project for video 13 ("Ledger Emas" look).

Look (new, unlike videos 1-12): cream paper + ink + gold leaf, editorial serif (Playfair Display) over a clean
sans (Inter) with mono numbers (Space Mono). Two layouts:
  * FULL  - the talking head fills the frame; graphics only in the top band (y 175-395) and the caption band.
  * LEDGER - the camera eases back into a framed card at the top (face kept whole) and a paper panel below
             carries the big graphic (y 810-1225). Used for the six "explain" moments.
TikTok + Reels safe zones: nothing above y 168, every word above y 1335, nothing at x > 940 for y 760-1520.
"""
import json, os, shutil, subprocess

W, H, FPS = 1080, 1920, 30
OUTRO = 3.6
INK, CREAM, GOLD, GOLD_D, GREEN, RED = '#151515', '#F5EFE3', '#E3B547', '#A97A1C', '#1E7A4F', '#C8423B'
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SFX_DIR = os.path.join(REPO, 'work', '13', 'hf', 'node_modules', 'hyperframes', 'dist', 'skills', 'media-use',
                       'audio', 'assets', 'sfx')
MUSIC_SRC = os.path.join(REPO, 'work', '13', 'music', 'acoustic.m4a')
LOGO = os.path.join(REPO, 'video-style', 'assets', 'logo.png')

# camera card in LEDGER mode: source rows 250..1250 -> 170..790 on screen
CARD_SCALE, CARD_SRC_TOP, CARD_TOP = 0.62, 250, 170
CARD_SRC_BOT = 1250


class Words:
    def __init__(self, words):
        self.w = words

    def t(self, cue, word, which=0, end=False):
        hits = [x for x in self.w if x['cue'] == cue and word.lower() in x['w'].lower()]
        if not hits:
            raise KeyError((cue, word))
        x = hits[which]
        return round(x['oe'] if end else x['os'], 3)

    def cue(self, n, end=False):
        ws = [x for x in self.w if x['cue'] == n]
        return round(ws[-1]['oe'] if end else ws[0]['os'], 3)


# ------------------------------------------------------------------ scene file helper
def scene(cid, css, html, js):
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; overflow: visible; }}
    .serif {{ font-family: 'Playfair Display', serif; }}
    .sans {{ font-family: 'Inter', sans-serif; }}
    .mono {{ font-family: 'Space Mono', monospace; }}
{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}" data-layout-allow-overlap>
{html}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""


def blur_in(sel, t, d=0.45, y=24):
    return (f"    tl.fromTo('{sel}', {{opacity: 0, y: {y}, filter: 'blur(10px)'}}, "
            f"{{opacity: 1, y: 0, filter: 'blur(0px)', duration: {d}, ease: 'expo.out'}}, {t:.3f});\n")


def blur_out(sel, t, d=0.22):
    return (f"    tl.to('{sel}', {{opacity: 0, filter: 'blur(8px)', duration: {d}, ease: 'power2.in'}}, {t:.3f});\n")


def pop_in(sel, t, d=0.5):
    return (f"    tl.fromTo('{sel}', {{opacity: 0, scale: 0.6}}, "
            f"{{opacity: 1, scale: 1, duration: {d}, ease: 'back.out(1.5)'}}, {t:.3f});\n")


BAND_CSS = """
    .band { position: absolute; left: 60px; right: 60px; top: 178px; height: 220px; }
    .kicker { font: 700 30px 'Space Mono', monospace; letter-spacing: 3px; text-transform: uppercase; color: #6b5a3a; }
    .h1 { font: 700 84px/1.0 'Playfair Display', serif; color: #151515; letter-spacing: -1px; }
    .h1 em { font-style: italic; color: #A97A1C; }
    .paper { position: absolute; left: 60px; width: 870px; top: 812px; height: 410px; }
    .chip { position: absolute; display: flex; align-items: center; gap: 16px; padding: 18px 30px;
            border-radius: 18px; background: #fffaf0; border: 2px solid #151515; box-shadow: 6px 6px 0 #151515;
            font: 700 40px 'Inter', sans-serif; color: #151515; white-space: nowrap; }
"""


def gold_bar(w, h, label, cls=''):
    return (f"<div class='goldbar {cls}' style='width:{w}px;height:{h}px'>"
            f"<div class='gb-top'></div><div class='gb-face'><span>{label}</span></div><div class='gb-shine'></div></div>")


GOLD_CSS = """
    .goldbar { position: absolute; }
    .gb-face { position: absolute; inset: 18% 0 0 0; border-radius: 10px;
               background: linear-gradient(160deg, #FBE7A1 0%, #E8BE52 38%, #B9861F 72%, #8E6414 100%);
               box-shadow: inset 0 -8px 16px rgba(80,50,0,.35), inset 0 6px 10px rgba(255,255,255,.45), 0 18px 30px rgba(60,40,0,.28);
               display: flex; align-items: center; justify-content: center; }
    .gb-face span { font: 700 46px 'Space Mono', monospace; color: #6E4B0C; text-shadow: 0 1px 0 rgba(255,240,190,.8); }
    .gb-top { position: absolute; left: 7%; right: 7%; top: 0; height: 22%; border-radius: 8px 8px 0 0;
              background: linear-gradient(180deg, #FFF3C4, #EBC562); }
    .gb-shine { position: absolute; inset: 18% 0 0 0; border-radius: 10px; overflow: hidden;
                background: linear-gradient(105deg, transparent 35%, rgba(255,255,255,.75) 50%, transparent 65%);
                background-size: 300% 100%; background-position: 120% 0; }
"""


# ------------------------------------------------------------------ the scenes
def build_scenes(T, total):
    S = []   # (id, start, dur, html)

    # S0 hook: price falling ticker in the top band ---------------------------------------
    t0, t1 = 0.0, T.cue(3) - 0.05
    css = BAND_CSS + """
    #s0-card { position: absolute; left: 60px; top: 178px; width: 960px; height: 210px; border-radius: 26px;
               background: rgba(255,250,240,.92); border: 2px solid #151515; box-shadow: 8px 8px 0 #151515; }
    #s0-lbl { position: absolute; left: 34px; top: 24px; }
    #s0-big { position: absolute; left: 34px; top: 70px; font: 800 92px/1 'Inter', sans-serif; color: #151515; letter-spacing: -2px; }
    #s0-big b { color: #C8423B; }
    #s0-chart { position: absolute; right: 30px; top: 30px; width: 330px; height: 150px; }
    """
    html = """
    <div id="s0-card">
      <div id="s0-lbl" class="kicker">Harga emas &middot; sekarang</div>
      <div id="s0-big">JATUH <b id="s0-arrow">&#9660;</b></div>
      <svg id="s0-chart" viewBox="0 0 330 150"><path id="s0-line" d="M5 20 L60 35 L95 25 L140 62 L180 55 L220 95 L260 88 L325 140"
        fill="none" stroke="#C8423B" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" pathLength="100"
        stroke-dasharray="100 120" stroke-dashoffset="110"/><circle id="s0-dot" cx="325" cy="140" r="11" fill="#C8423B"/></svg>
    </div>"""
    js = (f"    tl.fromTo('#s0-card', {{opacity: 1, scale: 1.04}}, {{opacity: 1, scale: 1, duration: .5, ease: 'expo.out'}}, 0);\n"
          f"    tl.fromTo('#s0-line', {{attr: {{'stroke-dashoffset': 110}}}}, {{attr: {{'stroke-dashoffset': 0}}, duration: 1.1, ease: 'power2.inOut'}}, 0.3);\n"
          f"    tl.fromTo('#s0-dot', {{scale: 0, transformOrigin: '50% 50%'}}, {{scale: 1, duration: .3, ease: 'back.out(2)'}}, 1.35);\n"
          f"    tl.fromTo('#s0-arrow', {{y: -30, opacity: 0}}, {{y: 0, opacity: 1, duration: .35, ease: 'power4.out'}}, {T.t(1, 'jatuh') - t0:.3f});\n"
          + blur_out('#s0-card', t1 - t0 - 0.25))
    S.append(('s0', t0, t1 - t0, scene('s0', css, html, js)))

    # S1 question: naik -> berebut, turun -> takut, "Pelik kan?" -------------------------
    t0, t1 = T.cue(3) - 0.05, T.cue(6) - 0.1
    css = BAND_CSS + """
    .row { position: absolute; left: 60px; width: 960px; height: 98px; border-radius: 22px; display: flex; align-items: center;
           gap: 22px; padding: 0 30px; box-sizing: border-box; background: rgba(255,250,240,.93); border: 2px solid #151515; }
    .row .tag { font: 700 34px 'Space Mono', monospace; padding: 6px 18px; border-radius: 12px; color: #fff; }
    .row .txt { font: 800 46px 'Inter', sans-serif; color: #151515; }
    #s1-up { top: 182px; } #s1-up .tag { background: #1E7A4F; }
    #s1-dn { top: 296px; } #s1-dn .tag { background: #C8423B; }
    #s1-pelik { position: absolute; left: 0; right: 120px; top: 190px; text-align: center;
                font: italic 700 150px/1 'Playfair Display', serif; color: #151515;
                text-shadow: 0 4px 0 rgba(255,250,240,.9), 0 10px 30px rgba(255,250,240,.9); }
    #s1-pelik span { color: #A97A1C; }
    """
    html = """
    <div id="s1-up" class="row"><span class="tag">NAIK &#9650;</span><span class="txt">ramai berebut beli</span></div>
    <div id="s1-dn" class="row"><span class="tag">TURUN &#9660;</span><span class="txt">ramai pula takut</span></div>
    <div id="s1-pelik">Pelik <span>kan?</span></div>"""
    tp = T.cue(5) - t0
    js = (f"    tl.fromTo('#s1-up', {{opacity: 0, x: -80}}, {{opacity: 1, x: 0, duration: .5, ease: 'expo.out'}}, {T.t(3, 'naik') - t0:.3f});\n"
          f"    tl.fromTo('#s1-dn', {{opacity: 0, x: 80}}, {{opacity: 1, x: 0, duration: .5, ease: 'expo.out'}}, {T.t(4, 'turun') - t0:.3f});\n"
          f"    tl.to(['#s1-up', '#s1-dn'], {{opacity: 0, y: -20, filter: 'blur(8px)', duration: .2, ease: 'power2.in', stagger: .05}}, {tp - 0.25:.3f});\n"
          f"    tl.fromTo('#s1-pelik', {{opacity: 0, scale: 1.4, filter: 'blur(14px)'}}, {{opacity: 1, scale: 1, filter: 'blur(0px)', duration: .35, ease: 'expo.out'}}, {tp:.3f});\n"
          + blur_out('#s1-pelik', t1 - t0 - 0.25))
    S.append(('s1', t0, t1 - t0, scene('s1', css, html, js)))

    # S2 LEDGER: price tag RM1,000 -> RM800, gembira vs sedih -------------------------------
    t0, t1 = T.cue(7) - 0.3, T.cue(11) - 0.3
    css = BAND_CSS + """
    #s2-tag { position: absolute; left: 150px; top: 850px; width: 560px; height: 230px; }
    #s2-tag .body { position: absolute; inset: 0; background: #fffaf0; border: 3px solid #151515; border-radius: 26px 26px 26px 26px;
                    box-shadow: 10px 10px 0 #151515; clip-path: polygon(14% 0, 100% 0, 100% 100%, 14% 100%, 0 50%); }
    #s2-tag .hole { position: absolute; left: 34px; top: 100px; width: 30px; height: 30px; border-radius: 50%; border: 3px solid #151515; background: #F5EFE3; }
    #s2-tag .lbl { position: absolute; left: 120px; top: 26px; }
    #s2-old { position: absolute; left: 120px; top: 70px; font: 700 110px/1 'Space Mono', monospace; color: #151515; }
    #s2-strike { position: absolute; left: 112px; top: 128px; width: 420px; height: 10px; background: #C8423B; transform-origin: 0 50%; border-radius: 6px; }
    #s2-new { position: absolute; left: 150px; top: 1100px; font: 700 96px/1 'Space Mono', monospace; color: #1E7A4F; }
    #s2-new small { font: 700 34px 'Inter', sans-serif; color: #151515; margin-right: 14px; }
    #s2-q { position: absolute; left: 60px; width: 870px; top: 850px; height: 360px; }
    .mood { position: absolute; top: 60px; width: 400px; height: 220px; border-radius: 28px; border: 3px solid #151515;
            background: #fffaf0; box-shadow: 8px 8px 0 #151515; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; }
    .mood .face { width: 84px; height: 84px; }
    .mood .w { font: 800 48px 'Inter', sans-serif; color: #151515; }
    #s2-happy { left: 0; } #s2-sad { left: 450px; }
    #s2-check { position: absolute; left: 330px; top: 30px; width: 74px; height: 74px; border-radius: 50%; background: #1E7A4F;
                color: #fff; font: 800 48px/74px 'Inter', sans-serif; text-align: center; }
    #s2-cheap { position: absolute; left: 0; top: 300px; width: 870px; text-align: center; font: italic 700 54px 'Playfair Display', serif; color: #A97A1C; }
    """
    smile = ("<svg class='face' viewBox='0 0 84 84'><circle cx='42' cy='42' r='38' fill='#E3B547' stroke='#151515' stroke-width='4'/>"
             "<circle cx='29' cy='34' r='5' fill='#151515'/><circle cx='55' cy='34' r='5' fill='#151515'/>"
             "<path d='M24 50 Q42 68 60 50' fill='none' stroke='#151515' stroke-width='5' stroke-linecap='round'/></svg>")
    sad = smile.replace("M24 50 Q42 68 60 50", "M26 62 Q42 46 58 62").replace('#E3B547', '#d9d2c3')
    html = f"""
    <div id="s2-a">
      <div id="s2-tag"><div class="body"></div><div class="hole"></div><div class="lbl kicker">Harga barang</div>
        <div id="s2-old">RM1,000</div><div id="s2-strike"></div></div>
      <div id="s2-new"><small>Turun jadi</small>RM800</div>
    </div>
    <div id="s2-q">
      <div id="s2-happy" class="mood">{smile}<div class="w">Gembira?</div></div>
      <div id="s2-sad" class="mood">{sad}<div class="w">Sedih?</div></div>
      <div id="s2-check">&#10003;</div>
      <div id="s2-cheap">beli dengan harga lebih murah</div>
    </div>"""
    a = T.t(7, 'seribu') - t0
    b = T.t(8, 'lapan') - t0
    q = T.cue(9) - t0
    m = T.t(10, 'Mestilah') - t0
    c = T.t(10, 'beli') - t0
    js = (f"    tl.fromTo('#s2-tag', {{opacity: 0, rotation: -8, y: 60}}, {{opacity: 1, rotation: -3, y: 0, duration: .7, ease: 'back.out(1.4)'}}, {a - 0.3:.3f});\n"
          f"    tl.fromTo('#s2-strike', {{scaleX: 0}}, {{scaleX: 1, duration: .3, ease: 'power3.out'}}, {b:.3f});\n"
          f"    tl.to('#s2-old', {{color: '#9b9488', duration: .2}}, {b:.3f});\n"
          + blur_in('#s2-new', b + 0.25, 0.5, 30) +
          f"    tl.to('#s2-a', {{opacity: 0, y: -30, filter: 'blur(10px)', duration: .25, ease: 'power2.in'}}, {q - 0.3:.3f});\n"
          + pop_in('#s2-happy', q) + pop_in('#s2-sad', q + 0.12) +
          f"    tl.set('#s2-check', {{opacity: 0}}, 0);\n"
          f"    tl.to('#s2-sad', {{opacity: .35, scale: .94, duration: .3}}, {m:.3f});\n"
          f"    tl.to('#s2-happy', {{background: '#FFF1C9', borderColor: '#A97A1C', duration: .3}}, {m:.3f});\n"
          + pop_in('#s2-check', m + 0.05, 0.4) + blur_in('#s2-cheap', c - 0.35)
          + f"    tl.set('#s2-cheap', {{opacity: 0}}, 0);\n" + f"    tl.set('#s2-new', {{opacity: 0}}, 0);\n"
          + f"    tl.set(['#s2-happy','#s2-sad'], {{opacity: 0}}, 0);\n")
    S.append(('s2', t0, t1 - t0, scene('s2', css, html, js)))
    ledger = [(T.cue(7) - 0.75, T.cue(11) - 0.35)]

    # S3 focus on price vs forgotten goal -------------------------------------------------
    t0, t1 = T.cue(11) - 0.1, T.cue(14) - 0.15
    css = BAND_CSS + """
    #s3-card { position: absolute; left: 60px; top: 178px; width: 960px; height: 210px; border-radius: 26px;
               background: rgba(255,250,240,.93); border: 2px solid #151515; box-shadow: 8px 8px 0 #151515; }
    #s3-q { position: absolute; left: 36px; top: 34px; right: 30px; font: 700 64px/1.05 'Playfair Display', serif; color: #151515; }
    #s3-q em { color: #A97A1C; }
    #s3-harga { position: absolute; left: 40px; top: 50px; font: 900 96px/1 'Inter', sans-serif; color: #151515; letter-spacing: -2px; }
    #s3-x { position: absolute; left: 32px; top: 98px; width: 360px; height: 12px; background: #C8423B; border-radius: 6px; transform-origin: 0 50%; }
    #s3-goal { position: absolute; left: 430px; top: 40px; font: italic 700 72px/1 'Playfair Display', serif; color: #A97A1C; }
    #s3-goal small { display: block; font: 700 28px 'Space Mono', monospace; color: #6b5a3a; font-style: normal; margin-top: 8px; letter-spacing: 3px; }
    #s3-ul { position: absolute; left: 430px; top: 122px; width: 440px; height: 8px; background: #E3B547; transform-origin: 0 50%; }
    """
    html = """
    <div id="s3-card">
      <div id="s3-q">Bila melibatkan <em>emas</em>, kita fikir sebaliknya?</div>
      <div id="s3-b"><div id="s3-harga">HARGA</div><div id="s3-x"></div>
        <div id="s3-goal">matlamat asal<small>YANG TERLUPA</small></div><div id="s3-ul"></div></div>
    </div>"""
    f = T.t(12, 'fokus') - t0
    g = T.t(12, 'terlupa') - t0
    js = (f"    tl.fromTo('#s3-card', {{opacity: 0, y: -30}}, {{opacity: 1, y: 0, duration: .5, ease: 'expo.out'}}, 0.1);\n"
          + blur_in('#s3-q', 0.2) +
          f"    tl.to('#s3-q', {{opacity: 0, filter: 'blur(8px)', duration: .2}}, {f - 0.25:.3f});\n"
          + blur_in('#s3-harga', f) + f"    tl.set(['#s3-goal','#s3-ul'], {{opacity: 0}}, 0);\n"
          f"    tl.set('#s3-x', {{scaleX: 0}}, 0);\n"
          f"    tl.to('#s3-x', {{scaleX: 1, duration: .3, ease: 'power3.out'}}, {g:.3f});\n"
          f"    tl.to('#s3-harga', {{color: '#9b9488', duration: .25}}, {g:.3f});\n"
          + blur_in('#s3-goal', g + 0.2) +
          f"    tl.fromTo('#s3-ul', {{opacity: 1, scaleX: 0}}, {{scaleX: 1, duration: .5, ease: 'power2.out'}}, {g + 0.45:.3f});\n"
          f"    tl.set('#s3-harga', {{opacity: 0}}, 0);\n" + blur_out('#s3-card', t1 - t0 - 0.3))
    S.append(('s3', t0, t1 - t0, scene('s3', css, html, js)))

    # S4 LEDGER payoff: 100 g stays 100 g while the price moves --------------------------
    t0, t1 = T.cue(15) - 0.6, T.cue(19) - 0.3
    css = BAND_CSS + GOLD_CSS + """
    #s4-head { position: absolute; left: 60px; width: 870px; top: 822px; text-align: center; font: 700 52px/1.1 'Playfair Display', serif; color: #151515; }
    #s4-head em { color: #C8423B; font-style: italic; }
    #s4-bar { left: 285px; top: 950px; }
    #s4-tick { position: absolute; left: 60px; width: 230px; top: 990px; height: 150px; border-radius: 22px; border: 3px solid #151515;
               background: #fffaf0; box-shadow: 6px 6px 0 #151515; overflow: hidden; }
    #s4-tick .k { position: absolute; left: 20px; top: 12px; font: 700 28px 'Space Mono', monospace; color: #6b5a3a; letter-spacing: 2px; }
    .arr { position: absolute; left: 0; right: 0; top: 46px; text-align: center; font: 800 76px/1 'Inter', sans-serif; }
    #s4-up { color: #1E7A4F; } #s4-dn { color: #C8423B; }
    #s4-same { position: absolute; left: 650px; top: 1000px; width: 280px; font: 800 44px/1.1 'Inter', sans-serif; color: #151515; }
    #s4-same b { display: block; font: italic 700 64px 'Playfair Display', serif; color: #A97A1C; }
    #s4-val { position: absolute; left: 60px; width: 870px; top: 1160px; text-align: center; font: 700 40px 'Inter', sans-serif; color: #151515; }
    #s4-val span { background: #E3B547; padding: 4px 14px; border-radius: 10px; }
    """
    html = f"""
    <div id="s4-head">Harga turun <em>&ne;</em> gram berkurang</div>
    <div id="s4-tick"><div class="k">HARGA</div><div id="s4-up" class="arr">&#9650;</div><div id="s4-dn" class="arr">&#9660;</div></div>
    {gold_bar(340, 200, '100 g').replace("class='goldbar '", "id='s4-bar' class='goldbar'")}
    <div id="s4-same">tetap<b>100 g</b></div>
    <div id="s4-val">Yang berubah: <span>nilai semasa</span></div>"""
    h = T.cue(15) - t0
    bar = T.t(16, 'seratus', 0) - t0
    up = T.t(16, 'naik') - t0
    same1 = T.t(16, 'tetap') - t0
    dn = T.t(17, 'turun') - t0
    same2 = T.t(17, 'tetap') - t0
    val = T.t(18, 'nilai') - t0
    js = (blur_in('#s4-head', h + 0.05) +
          f"    tl.fromTo('#s4-bar', {{opacity: 0, y: -120, rotation: -6}}, {{opacity: 1, y: 0, rotation: 0, duration: .6, ease: 'bounce.out'}}, {bar - 0.15:.3f});\n"
          f"    tl.fromTo('#s4-bar .gb-shine', {{backgroundPosition: '120% 0'}}, {{backgroundPosition: '-60% 0', duration: 1.0, ease: 'power2.inOut'}}, {bar + 0.5:.3f});\n"
          f"    tl.set(['#s4-up','#s4-dn','#s4-same','#s4-val','#s4-tick'], {{opacity: 0}}, 0);\n"
          + pop_in('#s4-tick', up - 0.2, 0.4) +
          f"    tl.fromTo('#s4-up', {{opacity: 0, y: 50}}, {{opacity: 1, y: 0, duration: .35, ease: 'power4.out'}}, {up:.3f});\n"
          + blur_in('#s4-same', same1) +
          f"    tl.to('#s4-up', {{opacity: 0, y: -50, duration: .2, ease: 'power2.in'}}, {dn - 0.1:.3f});\n"
          f"    tl.fromTo('#s4-dn', {{opacity: 0, y: -50}}, {{opacity: 1, y: 0, duration: .35, ease: 'power4.out'}}, {dn:.3f});\n"
          f"    tl.fromTo('#s4-same b', {{scale: 1}}, {{scale: 1.18, duration: .15, yoyo: true, repeat: 1, ease: 'power2.out'}}, {same2:.3f});\n"
          f"    tl.fromTo('#s4-bar .gb-shine', {{backgroundPosition: '120% 0'}}, {{backgroundPosition: '-60% 0', duration: 1.0, immediateRender: false, ease: 'power2.inOut'}}, {same2:.3f});\n"
          + blur_in('#s4-val', val - 0.1))
    S.append(('s4', t0, t1 - t0, scene('s4', css, html, js)))
    ledger.append((T.cue(15) - 0.9, T.cue(19) - 0.35))

    # S5 risk chip (full) -----------------------------------------------------------------
    t0, t1 = T.cue(19) - 0.1, T.cue(20) - 0.4
    css = BAND_CSS + """
    #s5-card { position: absolute; left: 60px; top: 190px; width: 960px; border-radius: 26px; padding: 26px 34px; box-sizing: border-box;
               background: rgba(255,250,240,.94); border: 3px solid #C8423B; box-shadow: 8px 8px 0 #C8423B; }
    #s5-card .kicker { color: #C8423B; }
    #s5-t { font: 800 54px/1.12 'Inter', sans-serif; color: #151515; margin-top: 8px; }
    #s5-t em { font-style: normal; color: #C8423B; }
    """
    html = """<div id="s5-card"><div class="kicker">&#9888; Hakikat</div>
      <div id="s5-t">Jual ketika harga rendah, <em>mungkin rugi.</em></div></div>"""
    js = (f"    tl.fromTo('#s5-card', {{opacity: 0, y: -30, rotation: -1.5}}, {{opacity: 1, y: 0, rotation: 0, duration: .5, ease: 'expo.out'}}, {T.t(19, 'jual') - t0 - 0.2:.3f});\n"
          + blur_out('#s5-card', t1 - t0 - 0.25))
    S.append(('s5', t0, t1 - t0, scene('s5', css, html, js)))

    # S6 LEDGER checklist ----------------------------------------------------------------
    t0, t1 = T.cue(20) - 0.4, T.cue(22) - 0.3
    css = BAND_CSS + """
    #s6-h { position: absolute; left: 60px; top: 826px; width: 870px; font: 700 50px/1.1 'Playfair Display', serif; color: #151515; }
    #s6-h em { color: #A97A1C; }
    .it { position: absolute; left: 60px; width: 870px; height: 96px; display: flex; align-items: center; gap: 24px;
          border-bottom: 2px dashed #b9ad95; }
    .it .bx { width: 58px; height: 58px; border-radius: 14px; border: 3px solid #151515; background: #fffaf0; position: relative; flex: none; }
    .it .ck { position: absolute; inset: -4px; border-radius: 14px; background: #1E7A4F; color: #fff; font: 800 44px/66px 'Inter', sans-serif; text-align: center; }
    .it .n { font: 700 30px 'Space Mono', monospace; color: #4f4229; width: 56px; }
    .it .tx { font: 800 48px 'Inter', sans-serif; color: #151515; }
    #s6-1 { top: 905px; } #s6-2 { top: 1010px; } #s6-3 { top: 1115px; }
    """
    html = """
    <div id="s6-h">Sebelum simpan emas, <em>fahamkan:</em></div>
    <div id="s6-1" class="it"><div class="n">01</div><div class="bx"><div class="ck">&#10003;</div></div><div class="tx">Tempoh simpanan</div></div>
    <div id="s6-2" class="it"><div class="n">02</div><div class="bx"><div class="ck">&#10003;</div></div><div class="tx">Spread jual beli</div></div>
    <div id="s6-3" class="it"><div class="n">03</div><div class="bx"><div class="ck">&#10003;</div></div><div class="tx">Matlamat kewangan</div></div>"""
    js = blur_in('#s6-h', 0.45)
    for i, (cue, w) in enumerate([(20, 'tempoh'), (20, 'spread'), (21, 'matlamat')], 1):
        tt = T.t(cue, w) - t0
        js += (f"    tl.fromTo('#s6-{i}', {{opacity: 0, x: -40}}, {{opacity: 1, x: 0, duration: .45, ease: 'expo.out'}}, {tt - 0.15:.3f});\n"
               f"    tl.fromTo('#s6-{i} .ck', {{scale: 0}}, {{scale: 1, duration: .35, ease: 'back.out(2)'}}, {tt + 0.25:.3f});\n")
    S.append(('s6', t0, t1 - t0, scene('s6', css, html, js)))
    ledger.append((T.cue(20) - 0.65, T.cue(22) - 0.35))

    # S7 don't convert next month's money (full) --------------------------------------------
    t0, t1 = T.cue(22) - 0.1, T.cue(27) - 0.35
    css = BAND_CSS + """
    #s7-card { position: absolute; left: 60px; top: 182px; width: 960px; height: 214px; border-radius: 26px;
               background: rgba(255,250,240,.94); border: 2px solid #151515; box-shadow: 8px 8px 0 #151515; }
    #s7-q { position: absolute; left: 34px; top: 26px; font: 800 50px/1.1 'Inter', sans-serif; color: #151515; }
    #s7-q .kicker { display: block; margin-bottom: 8px; }
    #s7-stamp { position: absolute; right: 40px; top: 52px; padding: 10px 26px; border: 6px solid #C8423B; border-radius: 14px;
                font: 900 54px 'Inter', sans-serif; color: #C8423B; letter-spacing: 2px; }
    #s7-sub { position: absolute; left: 34px; top: 142px; font: italic 700 42px 'Playfair Display', serif; color: #6b5a3a; }
    """
    html = """<div id="s7-card"><div id="s7-q"><span class="kicker">Duit untuk</span>bulan depan?</div>
      <div id="s7-stamp">JANGAN</div><div id="s7-sub">tukar semuanya kepada emas</div></div>"""
    st = T.t(22, 'jangan') - t0
    js = (f"    tl.fromTo('#s7-card', {{opacity: 0, y: -30}}, {{opacity: 1, y: 0, duration: .5, ease: 'expo.out'}}, {T.t(22, 'bulan') - t0 - 0.4:.3f});\n"
          f"    tl.fromTo('#s7-stamp', {{opacity: 0, scale: 2.2, rotation: -14}}, {{opacity: 1, scale: 1, rotation: -8, duration: .28, ease: 'power4.in'}}, {st - 0.25:.3f});\n"
          + blur_in('#s7-sub', T.t(23, 'tukarkan') - t0 - 0.1) + f"    tl.set('#s7-sub', {{opacity: 0}}, 0);\n"
          + blur_out('#s7-card', t1 - t0 - 0.25))
    S.append(('s7', t0, t1 - t0, scene('s7', css, html, js)))

    # S8 LEDGER timeline: a few days vs 2+ years --------------------------------------------
    t0, t1 = T.cue(27) - 0.35, T.cue(31) - 0.3
    css = BAND_CSS + """
    #s8-h { position: absolute; left: 60px; top: 830px; width: 870px; font: 700 50px/1.1 'Playfair Display', serif; color: #151515; }
    .trk { position: absolute; left: 60px; width: 870px; height: 74px; border-radius: 40px; background: #e7dfcf; }
    .lab { position: absolute; left: 60px; font: 700 28px 'Space Mono', monospace; color: #6b5a3a; letter-spacing: 2px; }
    #s8-l1 { top: 930px; } #s8-t1 { top: 970px; }
    #s8-l2 { top: 1070px; } #s8-t2 { top: 1110px; }
    #s8-days { position: absolute; left: 60px; top: 970px; width: 70px; height: 74px; border-radius: 40px; background: #C8423B; }
    #s8-years { position: absolute; left: 60px; top: 1110px; width: 870px; height: 74px; border-radius: 40px; transform-origin: 0 50%;
                background: linear-gradient(90deg, #B9861F, #E3B547 60%, #FBE7A1); }
    #s8-yl { position: absolute; left: 90px; top: 1124px; font: 800 40px 'Inter', sans-serif; color: #151515; }
    #s8-panik { position: absolute; left: 160px; top: 966px; font: italic 700 64px/1 'Playfair Display', serif; color: #C8423B; }
    """
    html = """
    <div id="s8-h">Simpan untuk jangka panjang</div>
    <div id="s8-l1" class="lab">BEBERAPA HARI</div><div id="s8-t1" class="trk"></div><div id="s8-days"></div>
    <div id="s8-panik">kenapa panik?</div>
    <div id="s8-l2" class="lab">2 TAHUN KE ATAS</div><div id="s8-t2" class="trk"></div><div id="s8-years"></div>
    <div id="s8-yl">perancangan simpanan</div>"""
    yr = T.t(27, 'dua') - t0
    pk = T.t(28, 'panik') - t0
    dy = T.t(28, 'beberapa') - t0
    js = (blur_in('#s8-h', 0.5) +
          f"    tl.set(['#s8-l1','#s8-t1','#s8-days','#s8-panik','#s8-l2','#s8-t2','#s8-years','#s8-yl'], {{opacity: 0}}, 0);\n"
          f"    tl.to(['#s8-l2','#s8-t2'], {{opacity: 1, duration: .3}}, {yr - 0.3:.3f});\n"
          f"    tl.fromTo('#s8-years', {{opacity: 1, scaleX: 0}}, {{scaleX: 1, duration: 1.2, ease: 'power3.out'}}, {yr:.3f});\n"
          + blur_in('#s8-yl', yr + 0.8) +
          f"    tl.to(['#s8-l1','#s8-t1'], {{opacity: 1, duration: .3}}, {pk - 0.6:.3f});\n"
          f"    tl.fromTo('#s8-days', {{opacity: 1, x: -6}}, {{x: 6, duration: .06, repeat: 7, yoyo: true, ease: 'none'}}, {pk - 0.4:.3f});\n"
          + blur_in('#s8-panik', pk - 0.1) +
          f"    tl.to('#s8-panik', {{opacity: .0, duration: .2}}, {dy + 1.4:.3f});\n")
    S.append(('s8', t0, t1 - t0, scene('s8', css, html, js)))
    ledger.append((T.cue(27) - 0.6, T.cue(31) - 0.35))

    # S9 knowledge (full) ---------------------------------------------------------------------
    t0, t1 = T.cue(31) - 0.1, T.cue(33) - 0.35
    css = BAND_CSS + """
    #s9-card { position: absolute; left: 60px; top: 182px; width: 960px; height: 214px; border-radius: 26px;
               background: #151515; box-shadow: 8px 8px 0 #E3B547; }
    #s9-k { position: absolute; left: 36px; top: 28px; font: 700 28px 'Space Mono', monospace; color: #E3B547; letter-spacing: 4px; }
    #s9-t { position: absolute; left: 36px; top: 72px; right: 30px; font: 700 54px/1.12 'Playfair Display', serif; color: #F5EFE3; }
    #s9-t2 { position: absolute; left: 36px; top: 72px; right: 30px; font: 700 54px/1.12 'Playfair Display', serif; color: #F5EFE3; }
    #s9-t em, #s9-t2 em { color: #E3B547; }
    """
    html = """<div id="s9-card"><div id="s9-k">ORANG YANG ADA ILMU</div>
      <div id="s9-t">tak kisah harga <em>turun</em> atau <em>naik</em></div>
      <div id="s9-t2">tahu <em>tindakan</em> yang sesuai</div></div>"""
    k2 = T.t(32, 'tindakan') - t0
    js = (f"    tl.fromTo('#s9-card', {{opacity: 0, y: -30}}, {{opacity: 1, y: 0, duration: .5, ease: 'expo.out'}}, 0.15);\n"
          + blur_in('#s9-t', T.t(31, 'kisah') - t0 - 0.1) + f"    tl.set('#s9-t2', {{opacity: 0}}, 0);\n"
          + blur_out('#s9-t', k2 - 0.3) + blur_in('#s9-t2', k2 - 0.05) + blur_out('#s9-card', t1 - t0 - 0.25))
    S.append(('s9', t0, t1 - t0, scene('s9', css, html, js)))

    # S10 LEDGER: extra money -> add grams step by step; none -> don't starve ------------
    t0, t1 = T.cue(33) - 0.35, T.cue(40) - 0.3
    css = BAND_CSS + GOLD_CSS + """
    #s10-a { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
    #s10-h { position: absolute; left: 60px; top: 826px; width: 870px; font: 800 46px/1.1 'Inter', sans-serif; color: #151515; }
    #s10-h em { font: italic 700 52px 'Playfair Display', serif; color: #1E7A4F; }
    .stp { position: absolute; }
    #s10-cap { position: absolute; left: 60px; top: 1150px; width: 870px; text-align: right; font: italic 700 46px 'Playfair Display', serif; color: #A97A1C; }
    #s10-b { position: absolute; left: 60px; top: 900px; width: 870px; height: 250px; border-radius: 28px; background: #fffaf0;
             border: 3px solid #151515; box-shadow: 8px 8px 0 #151515; }
    #s10-b .kicker { position: absolute; left: 40px; top: 40px; }
    #s10-bt { position: absolute; left: 40px; top: 96px; right: 40px; font: 800 64px/1.1 'Inter', sans-serif; color: #151515; }
    #s10-bt em { font-style: italic; font-family: 'Playfair Display', serif; color: #A97A1C; }
    """
    steps = ''.join(gold_bar(150, 86, '', 'stp').replace("class='goldbar stp'", f"id='s10-g{i}' class='goldbar stp'")
                    .replace("style='", f"style='left:{120 + i * 190}px;top:{1080 - i * 70}px;")
                    for i in range(4))
    html = f"""
    <div id="s10-a">
      <div id="s10-h">Ada lebihan duit? <em>tambah gram</em></div>
      {steps}
      <div id="s10-cap">secara berperingkat</div>
    </div>
    <div id="s10-b"><div class="kicker">Tak ada duit lebihan?</div>
      <div id="s10-bt">Tak perlulah <em>paksa diri.</em></div></div>"""
    g0 = T.t(33, 'tambah') - t0
    br = T.t(34, 'berperingkat') - t0
    nb = T.cue(35) - t0
    js = blur_in('#s10-h', T.t(33, 'lebihan') - t0 - 0.2)
    for i in range(4):
        js += f"    tl.fromTo('#s10-g{i}', {{opacity: 0, y: -90}}, {{opacity: 1, y: 0, duration: .45, ease: 'bounce.out'}}, {g0 + i * 0.32:.3f});\n"
    js += (blur_in('#s10-cap', br) + f"    tl.set('#s10-cap', {{opacity: 0}}, 0);\n"
           f"    tl.to('#s10-a', {{opacity: 0, y: -30, filter: 'blur(10px)', duration: .25, ease: 'power2.in'}}, {nb - 0.3:.3f});\n"
           f"    tl.set('#s10-b', {{opacity: 0}}, 0);\n"
           f"    tl.fromTo('#s10-b', {{opacity: 0, y: 40}}, {{opacity: 1, y: 0, duration: .5, ease: 'expo.out'}}, {nb:.3f});\n")
    S.append(('s10', t0, t1 - t0, scene('s10', css, html, js)))
    ledger.append((T.cue(33) - 0.6, T.cue(40) - 0.35))

    # S11 up & down wave, emotion line (full) -----------------------------------------------
    t0, t1 = T.cue(40) - 0.1, T.cue(43) - 0.35
    css = BAND_CSS + """
    #s11-card { position: absolute; left: 60px; top: 182px; width: 960px; height: 214px; border-radius: 26px;
                background: rgba(255,250,240,.94); border: 2px solid #151515; box-shadow: 8px 8px 0 #151515; overflow: hidden; }
    #s11-wave { position: absolute; left: 20px; top: 20px; width: 920px; height: 174px; }
    #s11-lbl { position: absolute; left: 36px; top: 24px; }
    #s11-e { position: absolute; left: 36px; top: 40px; right: 30px; font: 700 62px/1.08 'Playfair Display', serif; color: #151515; }
    #s11-e em { color: #C8423B; }
    """
    html = """<div id="s11-card">
      <svg id="s11-wave" viewBox="0 0 920 174"><path id="s11-p" d="M0 120 C80 40 140 40 200 100 S320 170 380 90 S500 10 560 80 S700 160 760 70 S880 30 920 60"
        fill="none" stroke="#A97A1C" stroke-width="8" stroke-linecap="round" pathLength="100" stroke-dasharray="100 120" stroke-dashoffset="110"/></svg>
      <div id="s11-lbl" class="kicker">Naik &amp; turun &mdash; memang betul</div>
      <div id="s11-e">Jangan biar <em>emosi</em> kawal keputusan kewangan</div></div>"""
    em = T.t(42, 'jangan') - t0
    js = (f"    tl.fromTo('#s11-card', {{opacity: 0, y: -30}}, {{opacity: 1, y: 0, duration: .5, ease: 'expo.out'}}, 0.1);\n"
          + blur_in('#s11-lbl', 0.3) +
          f"    tl.fromTo('#s11-p', {{attr: {{'stroke-dashoffset': 110}}}}, {{attr: {{'stroke-dashoffset': 0}}, duration: 2.2, ease: 'power1.inOut'}}, 0.4);\n"
          f"    tl.to(['#s11-wave','#s11-lbl'], {{opacity: 0, filter: 'blur(8px)', duration: .25}}, {em - 0.3:.3f});\n"
          + blur_in('#s11-e', em) + f"    tl.set('#s11-e', {{opacity: 0}}, 0);\n" + blur_out('#s11-card', t1 - t0 - 0.25))
    S.append(('s11', t0, t1 - t0, scene('s11', css, html, js)))

    # S12 not rich tomorrow -> building the future (full, dark card) ------------------------
    t0, t1 = T.cue(43) - 0.1, T.cue(50) - 0.35
    css = BAND_CSS + """
    #s12-card { position: absolute; left: 60px; top: 182px; width: 960px; height: 214px; border-radius: 26px; background: #151515; box-shadow: 8px 8px 0 #E3B547; }
    #s12-a { position: absolute; left: 36px; top: 36px; font: 700 58px/1.1 'Playfair Display', serif; color: #8d877b; }
    #s12-x { position: absolute; left: 30px; top: 70px; width: 880px; height: 8px; background: #C8423B; transform-origin: 0 50%; }
    #s12-b { position: absolute; left: 36px; top: 112px; font: italic 700 64px/1.1 'Playfair Display', serif; color: #E3B547; }
    """
    html = """<div id="s12-card"><div id="s12-a">bukan untuk kaya esok pagi</div><div id="s12-x"></div>
      <div id="s12-b">untuk membina masa depan</div></div>"""
    js = (f"    tl.fromTo('#s12-card', {{opacity: 0, y: -30}}, {{opacity: 1, y: 0, duration: .5, ease: 'expo.out'}}, 0.1);\n"
          + blur_in('#s12-a', T.t(43, 'bukan') - t0 - 0.1) +
          f"    tl.fromTo('#s12-x', {{scaleX: 0}}, {{scaleX: 1, duration: .4, ease: 'power3.out'}}, {T.cue(44) - t0 - 0.2:.3f});\n"
          + blur_in('#s12-b', T.cue(44) - t0 + 0.1) + f"    tl.set('#s12-b', {{opacity: 0}}, 0);\n"
          + blur_out('#s12-card', t1 - t0 - 0.25))
    S.append(('s12', t0, t1 - t0, scene('s12', css, html, js)))

    # S13 LEDGER CTA ----------------------------------------------------------------------
    t0, t1 = T.cue(50) - 0.35, total
    css = BAND_CSS + GOLD_CSS + """
    #s13-h { position: absolute; left: 60px; top: 828px; width: 870px; text-align: center; font: 700 54px/1.12 'Playfair Display', serif; color: #151515; }
    #s13-h em { color: #A97A1C; }
    #s13-btn { position: absolute; left: 150px; top: 1040px; width: 690px; height: 120px; border-radius: 30px; background: #fffaf0;
               border: 3px solid #151515; box-shadow: 8px 8px 0 #151515; }
    #s13-av { position: absolute; left: 22px; top: 18px; width: 84px; height: 84px; border-radius: 50%; background: #151515;
              display: flex; align-items: center; justify-content: center; overflow: hidden; }
    #s13-av img { width: 74px; }
    #s13-n { position: absolute; left: 126px; top: 36px; font: 800 44px 'Inter', sans-serif; color: #151515; }
    #s13-f { position: absolute; right: 18px; top: 18px; width: 200px; height: 84px; border-radius: 20px; background: #C8423B;
             font: 800 40px/84px 'Inter', sans-serif; color: #fff; text-align: center; }
    """
    html = """<div id="s13-h">Nak simpan emas <em>Public Gold</em> dengan betul?</div>
      <div id="s13-btn"><div id="s13-av"><img src="assets/logo_white.png"></div><div id="s13-n">Azlan &amp; Eza</div>
        <div id="s13-f">Follow</div></div>"""
    fol = T.t(50, 'follow') - t0
    js = (blur_in('#s13-h', 0.5) + f"    tl.set('#s13-btn', {{opacity: 0}}, 0);\n"
          f"    tl.fromTo('#s13-btn', {{opacity: 0, y: 50}}, {{opacity: 1, y: 0, duration: .55, ease: 'expo.out'}}, {fol - 0.9:.3f});\n"
          f"    tl.to('#s13-f', {{scale: .9, duration: .08, ease: 'power2.in'}}, {fol:.3f});\n"
          f"    tl.to('#s13-f', {{scale: 1, background: '#1E7A4F', duration: .25, ease: 'back.out(3)'}}, {fol + 0.08:.3f});\n"
          f"    tl.call(() => {{}}, null, {fol + 0.1:.3f});\n")
    js += f"    tl.set('#s13-f', {{textContent: 'Following'}}, {fol + 0.1:.3f});\n"
    S.append(('s13', t0, t1 - t0, scene('s13', css, html, js)))
    ledger.append((T.cue(50) - 0.6, total + 0.5))
    return S, ledger


# ------------------------------------------------------------------ captions
def caption_scene(words, total):
    groups, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        brk = (len(cur) >= 4 or nxt is None or nxt['cue'] != w['cue'] or w['w'][-1] in '.,?!'
               or (nxt and nxt['os'] - w['oe'] > 0.25))
        if brk:
            groups.append(cur); cur = []
    html, js = [], []
    for gi, g in enumerate(groups):
        spans = ''.join(f"<span id='cw{gi}_{k}'>{w['w']}</span> " for k, w in enumerate(g))
        html.append(f"    <div id='cg{gi}' class='cg'><div class='cin'>{spans.strip()}</div></div>")
        a = max(0.0, g[0]['os'] - 0.08)
        nxt_start = groups[gi + 1][0]['os'] - 0.08 if gi + 1 < len(groups) else total
        b = min(g[-1]['oe'] + 0.35, nxt_start)
        js.append(f"    tl.set('#cg{gi}', {{opacity: 1, visibility: 'visible'}}, {a:.3f});")
        js.append(f"    tl.fromTo('#cg{gi} .cin', {{y: 14, opacity: 0}}, {{y: 0, opacity: 1, duration: .16, ease: 'power3.out'}}, {a:.3f});")
        for k, w in enumerate(g):
            js.append(f"    tl.set('#cw{gi}_{k}', {{color: '#E3B547'}}, {w['os']:.3f});")
            if k < len(g) - 1:
                js.append(f"    tl.set('#cw{gi}_{k}', {{color: '#FFFFFF'}}, {g[k + 1]['os']:.3f});")
        js.append(f"    tl.set('#cg{gi}', {{opacity: 0, visibility: 'hidden'}}, {b:.3f});")
    css = """
    .cg { position: absolute; left: 40px; width: 900px; top: 1238px; text-align: center; opacity: 0; visibility: hidden; }
    .cin { display: inline-block; padding: 10px 22px 12px; border-radius: 16px; background: rgba(21,21,21,.72);
           font: 700 48px/1.15 'Inter', sans-serif; color: #fff; letter-spacing: -0.3px; }
    """
    return scene('captions', css, '\n'.join(html), '\n'.join(js))


# ------------------------------------------------------------------ outro
def outro_scene():
    css = """
    #o-bg { position: absolute; inset: 0; background: #F5EFE3; }
    #o-grid { position: absolute; inset: 0; background-image: linear-gradient(#e5dccb 2px, transparent 2px), linear-gradient(90deg, #e5dccb 2px, transparent 2px);
              background-size: 90px 90px; opacity: .55; }
    #o-logo { position: absolute; left: 290px; top: 640px; width: 500px; }
    #o-rule { position: absolute; left: 240px; top: 1010px; width: 600px; height: 6px; background: #E3B547; transform-origin: 50% 50%; }
    #o-t { position: absolute; left: 0; width: 1080px; top: 1050px; text-align: center; font: italic 700 60px 'Playfair Display', serif; color: #151515; }
    #o-s { position: absolute; left: 0; width: 1080px; top: 1140px; text-align: center; font: 700 30px 'Space Mono', monospace; color: #6b5a3a; letter-spacing: 6px; }
    """
    html = """<div id="o-bg"></div><div id="o-grid"></div><img id="o-logo" src="assets/logo.png">
    <div id="o-rule"></div><div id="o-t">Azlan &amp; Eza</div><div id="o-s">SIMPAN EMAS &middot; BINA MASA DEPAN</div>"""
    js = ("    tl.fromTo('#o-bg', {opacity: 0}, {opacity: 1, duration: .35, ease: 'power2.inOut'}, 0);\n"
          "    tl.fromTo('#o-grid', {opacity: 0}, {opacity: .55, duration: .6}, 0.1);\n"
          "    tl.fromTo('#o-logo', {opacity: 0, scale: .8, filter: 'blur(12px)'}, {opacity: 1, scale: 1, filter: 'blur(0px)', duration: .7, ease: 'expo.out'}, 0.3);\n"
          "    tl.fromTo('#o-rule', {scaleX: 0}, {scaleX: 1, duration: .6, ease: 'power3.out'}, 0.8);\n"
          + blur_in('#o-t', 0.8) + blur_in('#o-s', 0.95) +
          f"    tl.to('#root', {{opacity: 0, duration: .45, ease: 'power2.in'}}, {OUTRO - 0.5:.2f});\n")
    return scene('outro', css, html, js)


# ------------------------------------------------------------------ audio prep
def prep_audio(proj, total, speech):
    a = os.path.join(proj, 'assets')
    shutil.copy(os.path.join(REPO, 'work', '13', 'hf', 'node_modules', 'gsap', 'dist', 'gsap.min.js'), os.path.join(a, 'gsap.min.js'))
    for f in ('whoosh', 'whoosh-short', 'whoosh-cinematic', 'pop', 'click-soft', 'sparkle', 'impact-bass-1',
              'impact-bass-2', 'riser', 'ping'):
        shutil.copy(os.path.join(SFX_DIR, f + '.mp3'), os.path.join(a, f'sfx-{f}.mp3'))
    # music bed: the approved acoustic track looped with a 4 s crossfade to cover the film
    bed = os.path.join(a, 'music-bed.m4a')
    need = total + OUTRO + 1
    n = int(need // 85) + 1
    ins = sum([['-i', MUSIC_SRC] for _ in range(n + 1)], [])
    fc, last = '', '[0:a]'
    for i in range(1, n + 1):
        fc += f"{last}[{i}:a]acrossfade=d=4:c1=tri:c2=tri[x{i}];"
        last = f'[x{i}]'
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', fc + f"{last}atrim=end={need}[o]",
                    '-map', '[o]', '-c:a', 'aac', '-b:a', '192k', bed], check=True)
    # ducking lane: 0.13 under speech, 0.32 in longer gaps, 0.45 on the outro
    pts, t = [{'t': 0, 'v': 0.32}], 0
    for a0, b0 in speech:
        pts += [{'t': round(max(0, a0 - 0.25), 3), 'v': 0.32 if a0 - t > 0.9 else 0.13}, {'t': round(a0, 3), 'v': 0.13},
                {'t': round(b0, 3), 'v': 0.13}]
        t = b0
    pts += [{'t': round(total, 3), 'v': 0.13}, {'t': round(total + 0.6, 3), 'v': 0.45}]
    # compress: drop points closer than 0.05 s and keep at most 500
    out = []
    for p in sorted(pts, key=lambda p: p['t']):
        if out and p['t'] - out[-1]['t'] < 0.05:
            out[-1] = p
        else:
            out.append(p)
    return out[:500]


def sfx_len(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                         capture_output=True, text=True).stdout
    return round(float(out) - 0.02, 3)


def logo_white(dst):
    from PIL import Image
    import numpy as np
    lg = Image.open(LOGO).convert('RGBA')
    lg = lg.crop(lg.getbbox())
    arr = np.asarray(lg).copy()
    dark = (arr[..., :3].astype(int).mean(-1) < 70) & (arr[..., 3] > 0)
    arr[dark, :3] = 255
    Image.fromarray(arr).save(dst)
    lg.save(dst.replace('logo_white', 'logo'))


# ------------------------------------------------------------------ project
def write_project(proj, words, total):
    T = Words(words)
    comp = os.path.join(proj, 'compositions'); os.makedirs(comp, exist_ok=True)
    os.makedirs(os.path.join(proj, 'assets'), exist_ok=True)
    logo_white(os.path.join(proj, 'assets', 'logo_white.png'))
    scenes, ledger = build_scenes(T, total)
    for sid, st, du, src in scenes:
        open(os.path.join(comp, f'{sid}.html'), 'w').write(src)
    open(os.path.join(comp, 'captions.html'), 'w').write(caption_scene(words, total))
    open(os.path.join(comp, 'outro.html'), 'w').write(outro_scene())
    # speech spans for ducking
    speech, cur = [], None
    for w in words:
        if cur and w['os'] - cur[1] < 0.6:
            cur[1] = w['oe']
        else:
            if cur: speech.append(tuple(cur))
            cur = [w['os'], w['oe']]
    speech.append(tuple(cur))
    lane = prep_audio(proj, total, speech)
    dur = round(total + OUTRO, 3)

    # ---- SFX cues (sound.md: few, exact, with a cause on screen; rotate takes)
    sfx = []
    sfx.append(('impact-bass-1', 0.05, 0.55))                       # hook card lands
    sfx.append(('whoosh-short', T.t(3, 'naik') - 0.12, 0.45))
    sfx.append(('whoosh-short', T.t(4, 'turun') - 0.12, 0.45))
    sfx.append(('pop', T.cue(5) - 0.02, 0.6))                        # "Pelik kan?"
    whooshes = ['whoosh', 'whoosh-cinematic', 'whoosh']
    for i, (a, b) in enumerate(ledger):
        sfx.append((whooshes[i % 3], a - 0.1, 0.5))
        if b < total:
            sfx.append((whooshes[(i + 1) % 3], b - 0.15, 0.4))
    sfx += [('pop', T.t(7, 'seribu') - 0.25, 0.5), ('click-soft', T.t(8, 'lapan'), 0.7),
            ('pop', T.cue(9), 0.45), ('ping', T.t(10, 'Mestilah') + 0.05, 0.35),
            ('riser', T.t(16, 'seratus', 0) - 2.2, 0.35), ('impact-bass-2', T.t(16, 'seratus', 0) - 0.35, 0.5),
            ('sparkle', T.t(16, 'seratus', 0) + 0.5, 0.45), ('sparkle', T.t(17, 'tetap'), 0.4),
            ('pop', T.t(16, 'naik'), 0.45), ('pop', T.t(17, 'turun'), 0.45),
            ('click-soft', T.t(20, 'tempoh') + 0.25, 0.7), ('click-soft', T.t(20, 'spread') + 0.25, 0.7),
            ('click-soft', T.t(21, 'matlamat') + 0.25, 0.7),
            ('pop', T.t(19, 'jual') - 0.2, 0.45), ('impact-bass-1', T.t(22, 'jangan') - 0.05, 0.35),
            ('pop', T.t(31, 'kisah') - 0.1, 0.35), ('pop', T.t(33, 'tambah'), 0.4), ('pop', T.t(33, 'tambah') + 0.32, 0.35),
            ('pop', T.t(33, 'tambah') + 0.64, 0.35), ('pop', T.t(33, 'tambah') + 0.96, 0.4),
            ('whoosh-short', T.t(42, 'jangan') - 0.1, 0.4), ('sparkle', T.t(44, 'membina') - 0.1, 0.4),
            ('click-soft', T.t(50, 'follow'), 0.9), ('whoosh-cinematic', total - 0.1, 0.5)]
    audio_tags, lanes_end = [], []
    for i, (name, t, vol) in enumerate(sorted(sfx, key=lambda s: s[1])):
        d = sfx_len(os.path.join(proj, 'assets', f'sfx-{name}.mp3'))
        t = max(0, t)
        k = next((j for j, e in enumerate(lanes_end) if e <= t), None)
        if k is None:
            lanes_end.append(0); k = len(lanes_end) - 1
        d = round(min(d, total + OUTRO - t - 0.01), 3)
        lanes_end[k] = t + d
        audio_tags.append(f'    <audio id="sfx{i}" class="clip" src="assets/sfx-{name}.mp3" data-start="{t:.3f}" '
                          f'data-duration="{d:.3f}" data-track-index="{10 + k}" data-volume="{vol}"></audio>')

    # ---- camera moves (root timeline): punch-ins in FULL, ease back into the card in LEDGER
    cam = []
    for t, s in [(0.0, 1.07), (T.cue(3) - 0.03, 1.0), (T.cue(5) - 0.03, 1.1), (T.cue(6) - 0.03, 1.0),
                 (T.cue(11) - 0.03, 1.06), (T.cue(14) - 0.03, 1.0), (T.cue(19) - 0.03, 1.05),
                 (T.cue(22) - 0.03, 1.0), (T.cue(31) - 0.03, 1.06), (T.cue(32) - 0.03, 1.0),
                 (T.t(42, 'jangan') - 0.03, 1.08), (T.cue(43) - 0.03, 1.0), (T.cue(44) - 0.03, 1.06)]:
        cam.append(f"    tl.set('#punch', {{scale: {s}}}, {t:.3f});")
    for a, b in ledger:
        y = CARD_TOP - CARD_SRC_TOP
        cam.append(f"    tl.to('#cam', {{scale: {CARD_SCALE}, y: {y}, duration: .65, ease: 'power3.inOut'}}, {a:.3f});")
        cam.append(f"    tl.to('#camclip', {{'--ct': '{CARD_SRC_TOP}px', '--cb': '{H - CARD_SRC_BOT}px', '--cr': '46px', duration: .65, ease: 'power3.inOut'}}, {a:.3f});")
        cam.append(f"    tl.to('#paper', {{opacity: 1, duration: .4, ease: 'power2.out'}}, {a + 0.1:.3f});")
        if b < total:
            cam.append(f"    tl.to('#cam', {{scale: 1, y: 0, duration: .55, ease: 'power3.inOut'}}, {b:.3f});")
            cam.append(f"    tl.to('#camclip', {{'--ct': '0px', '--cb': '0px', '--cr': '0px', duration: .55, ease: 'power3.inOut'}}, {b:.3f});")
            cam.append(f"    tl.to('#paper', {{opacity: 0, duration: .3, ease: 'power2.in'}}, {b + 0.25:.3f});")

    hosts = []
    for i, (sid, st, du, _) in enumerate(scenes):
        hosts.append(f'    <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
                     f'data-start="{st:.3f}" data-duration="{du:.3f}" data-track-index="{2 + i % 2}" data-track-kind="graphics" '
                     f'data-width="{W}" data-height="{H}" style="z-index: 20"></div>')
    lane_json = json.dumps({'version': 1, 'lanes': [{'target': 'volume', 'points': lane}]}).replace('"', '&quot;')
    index = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="assets/gsap.min.js"></script>
  <style>
    html, body {{ margin: 0; padding: 0; background: #F5EFE3; }}
    #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: #F5EFE3; }}
    #paper {{ position: absolute; inset: 0; opacity: 0; z-index: 1;
             background: radial-gradient(120% 70% at 50% 30%, #FBF7EE 0%, #F2EADB 60%, #E9DFCB 100%); }}
    #paper::after {{ content: ''; position: absolute; inset: 0; opacity: .5;
             background-image: linear-gradient(#e2d8c4 2px, transparent 2px), linear-gradient(90deg, #e2d8c4 2px, transparent 2px);
             background-size: 90px 90px; }}
    #cam {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; z-index: 5; transform-origin: 540px {CARD_SRC_TOP}px; }}
    #camclip {{ position: absolute; inset: 0; --ct: 0px; --cb: 0px; --cr: 0px;
               clip-path: inset(var(--ct) 0px var(--cb) 0px round var(--cr)); overflow: hidden; }}
    #punch {{ position: absolute; inset: 0; transform-origin: 540px 780px; }}
    #base {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="{W}" data-height="{H}">
    <div id="paper"></div>
    <div id="cam"><div id="camclip"><div id="punch">
      <video id="base" class="clip" src="assets/base.mp4" data-start="0" data-duration="{total:.3f}" data-track-index="0"
             data-has-audio="true" data-volume="1" playsinline></video>
    </div></div></div>
{chr(10).join(hosts)}
    <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0"
         data-duration="{total:.3f}" data-track-index="4" data-track-kind="captions" data-width="{W}" data-height="{H}" style="z-index: 30"></div>
    <div id="outro" data-composition-id="outro" data-composition-src="compositions/outro.html" data-start="{total:.3f}"
         data-duration="{OUTRO}" data-track-index="5" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index: 40"></div>
    <audio id="music" class="clip" src="assets/music-bed.m4a" data-start="0" data-duration="{dur}" data-track-index="8"
           data-volume="1" data-fade-in="0.4" data-fade-out="1.5" data-automation="{lane_json}"></audio>
{chr(10).join(audio_tags)}
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(cam)}
    tl.set({{}}, {{}}, {dur});
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
"""
    open(os.path.join(proj, 'index.html'), 'w').write(index)
    if not os.path.exists(os.path.join(proj, 'hyperframes.json')):
        json.dump({'name': '13-harga-emas-jatuh'}, open(os.path.join(proj, 'meta.json'), 'w'))
    return scenes, ledger
