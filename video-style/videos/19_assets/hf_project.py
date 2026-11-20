"""HyperFrames project for video 19 (voiceover only): 5 sebab harga emas rendah ialah peluang menabung.

User rule (CLAUDE.md, video 11) for voiceover videos: light Apple-ad look, NO floating spheres, real product photos
with backgrounds removed, small Jost subtitles, smooth 30 fps motion. New for this video: HyperFrames scenes with
professional charts (price drop bars, gram comparison, 12-month gap, gold vs a failed stock, 1 kg ring).
White studio, bold black Jost headlines that slide up, frosted glass prompt bar that types itself, dashed pastel-
gradient pills, numbered chapter tiles, product label card with a blue button, slow push-in on every scene and a
whip blur between scenes. Real cut-outs: gold bar (11_assets/goldbar_cut.png, work/13/gold/goldbar_100g.png), cash.
TikTok + Reels safe zones: nothing above y 168, words above y 1335, nothing at x > 940 for y 760-1520.
"""
import importlib.util, json, os, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('hf13', os.path.join(HERE, '..', '13_assets', 'hf_project.py'))
H13 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(H13)
Words, scene, blur_in, blur_out, pop_in, sfx_len = H13.Words, H13.scene, H13.blur_in, H13.blur_out, H13.pop_in, H13.sfx_len

W, H = 1080, 1920
OUTRO = 3.4
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SFX_DIR = os.path.join(REPO, 'work', '13', 'hf', 'node_modules', 'hyperframes', 'dist', 'skills', 'media-use', 'audio', 'assets', 'sfx')
MUSIC_SRC = os.path.join(REPO, 'work', '13', 'music', 'acoustic.m4a')
FONTS = os.path.join(REPO, 'video-style', 'assets', 'fonts')

FACES = """
    @font-face { font-family: 'Jost'; font-weight: 500; src: url('assets/fonts/Jost-Medium.ttf'); }
    @font-face { font-family: 'Jost'; font-weight: 600; src: url('assets/fonts/Jost-SemiBold.ttf'); }
    @font-face { font-family: 'Jost'; font-weight: 700; src: url('assets/fonts/Jost-Bold.ttf'); }
    @font-face { font-family: 'Jost'; font-weight: 800; src: url('assets/fonts/Jost-ExtraBold.ttf'); }
"""
CSS = FACES + """
    #root { background: transparent; }
    .wd { position: absolute; inset: 0; transform-origin: 50% 45%; }
    .k { font: 600 30px 'Jost', sans-serif; letter-spacing: 6px; color: #8a8f98; text-transform: uppercase; }
    .h { font: 800 96px/0.98 'Jost', sans-serif; color: #0b0b0f; letter-spacing: -2px; }
    .h2 { font: 800 72px/1.02 'Jost', sans-serif; color: #0b0b0f; letter-spacing: -1px; }
    .b { font: 500 42px/1.25 'Jost', sans-serif; color: #3a3f47; }
    .g { color: #C9952B; } .r { color: #E5484D; } .bl { color: #2F6BFF; } .gr { color: #16A34A; }
    .line { overflow: hidden; display: block; }
    .line > span { display: inline-block; }
    .pill { position: absolute; isolation: isolate; z-index: 1; display: inline-flex; align-items: center; gap: 16px; padding: 16px 30px; border-radius: 999px; background: #fff;
            font: 600 40px 'Jost', sans-serif; color: #0b0b0f; box-shadow: 0 14px 34px rgba(20,24,40,.10); }
    .pill::after { content: ''; position: absolute; inset: 3px; border-radius: 999px; z-index: -1; background: #fff; }
    .pill::before { content: ''; position: absolute; inset: -3px; border-radius: 999px; z-index: -2;
            background: repeating-linear-gradient(90deg, #ffb3d1 0 14px, transparent 14px 22px, #a5c8ff 22px 36px, transparent 36px 44px, #ffe08a 44px 58px, transparent 58px 66px); }
    .glass { position: absolute; border-radius: 30px; background: rgba(255,255,255,.72); backdrop-filter: blur(18px);
             box-shadow: 0 20px 50px rgba(20,24,40,.10), inset 0 0 0 1.5px rgba(255,255,255,.9); }
    .card { position: absolute; border-radius: 32px; background: #fff; box-shadow: 0 24px 60px rgba(20,24,40,.12); }
    .tile { position: absolute; width: 150px; height: 150px; border-radius: 34px; background: #0b0b0f; color: #fff;
            display: flex; align-items: center; justify-content: center; font: 800 76px 'Jost', sans-serif; }
    .ill { position: absolute; font: 600 28px 'Jost', sans-serif; letter-spacing: 4px; color: #9aa0a8; border: 2px solid #d5d8de; padding: 2px 12px; border-radius: 10px; }
    .shadow { position: absolute; border-radius: 50%; background: radial-gradient(closest-side, rgba(20,20,30,.22), rgba(20,20,30,0)); }
"""


def up(sel, t, d=0.55, y=70):
    """Headline line slides up out of its mask."""
    return f"    tl.fromTo('{sel}', {{yPercent: 110}}, {{yPercent: 0, duration: {d}, ease: 'expo.out'}}, {t:.3f});\n"


def typed(sel, text, t, rate=0.045):
    js = f"    tl.set('{sel}', {{textContent: ''}}, 0);\n"
    for k in range(1, len(text) + 1):
        js += f"    tl.set('{sel}', {{textContent: {json.dumps(text[:k])}}}, {t + k * rate:.3f});\n"
    return js


def count(sel, a, b, t, d, dec=0, pre='', suf=''):
    return (f"    (() => {{ const o = {{v: {a}}}; tl.to(o, {{v: {b}, duration: {d}, ease: 'power3.out', onUpdate: () => "
            f"{{ document.querySelector('{sel}').textContent = '{pre}' + o.v.toFixed({dec}) + '{suf}'; }}}}, {t:.3f}); }})();\n")


def shell(sid, inner_css, html, js, dur):
    """Scene with a slow push-in world, whip in/out."""
    js_all = (f"    tl.fromTo('#{sid}-w', {{scale: 1}}, {{scale: 1.045, duration: {dur:.2f}, ease: 'none'}}, 0);\n"
              f"    tl.fromTo('#{sid}-w', {{x: 260, filter: 'blur(18px)', opacity: 0}}, {{x: 0, filter: 'blur(0px)', opacity: 1, duration: .32, ease: 'power3.out'}}, 0);\n"
              + js +
              f"    tl.to('#{sid}-w', {{x: -260, filter: 'blur(18px)', opacity: 0, duration: .26, ease: 'power3.in'}}, {dur - 0.27:.3f});\n")
    return scene(sid, CSS + inner_css, f"<div id='{sid}-w' class='wd'>{html}</div>", js_all)


def floaty(sel, t0, dur, amp=10, rot=4):
    """Smooth 3D sway for a product cut-out (deterministic sine via yoyo tweens)."""
    n = max(1, int(dur / 1.6))
    js = ""
    for i in range(n):
        js += (f"    tl.to('{sel}', {{y: {(-amp if i % 2 == 0 else amp)}, rotationY: {(rot if i % 2 == 0 else -rot)}, duration: 1.6, ease: 'sine.inOut'}}, {t0 + i * 1.6:.3f});\n")
    return js


def build(T, total):
    S = []
    c = T.cue

    def span(a_cue, b_cue):
        t0 = 0 if a_cue == 1 else c(a_cue) - 0.2
        t1 = total if b_cue is None else c(b_cue) - 0.2
        return t0, t1

    # S0 hook ---------------------------------------------------------------------------------------------
    t0, t1 = span(1, 5)
    html = """
      <div style="position:absolute;left:70px;top:230px;width:900px"><div class="k">Harga emas dunia</div>
        <div class="h" style="margin-top:18px"><span class="line"><span id="a-l1">Bila harga</span></span><span class="line"><span id="a-l2" class="g">rendah&hellip;</span></span></div></div>
      <div id="a-gb" style="position:absolute;left:560px;top:560px;width:340px;height:420px;transform-style:preserve-3d">
        <img src="assets/goldbar_100g.png" style="width:300px;filter:drop-shadow(0 30px 30px rgba(80,50,0,.25))"></div>
      <div class="shadow" style="left:560px;top:1000px;width:300px;height:50px"></div>
      <div id="a-q" class="glass" style="left:70px;top:1080px;width:860px;height:120px">
        <div style="position:absolute;left:34px;top:30px;width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,#a5c8ff,#ffb3d1)"></div>
        <div style="position:absolute;left:112px;top:28px;font:500 46px 'Jost',sans-serif;color:#0b0b0f"><span id="a-t"></span><span id="a-c" style="color:#2F6BFF">|</span></div></div>
      <div id="a-p" class="pill" style="left:70px;top:700px">waktu paling <b class="g">menarik</b> untuk menabung</div>
      <div id="a-s" style="position:absolute;left:70px;top:860px" class="h2">Jom saya kongsikan <span class="bl">sebabnya.</span></div>"""
    q = c(2) - t0
    js = ("    tl.fromTo(['#a-l1','#a-l2'], {scale: 1.06}, {scale: 1, duration: .6, ease: 'expo.out'}, 0);\n" + "    tl.set(['#a-q','#a-p','#a-s'], {opacity: 0}, 0);\n"
          f"    tl.fromTo('#a-gb', {{opacity: 1, y: 30, rotationX: 12}}, {{opacity: 1, y: 0, rotationX: 0, duration: .9, ease: 'expo.out'}}, 0);\n"
          + floaty('#a-gb', 1.2, t1 - t0 - 1.5) +
          f"    tl.fromTo('#a-q', {{opacity: 0, y: 40, scale: .96}}, {{opacity: 1, y: 0, scale: 1, duration: .45, ease: 'expo.out'}}, {q - 0.5:.3f});\n"
          + typed('#a-t', 'Patut ke saya beli sekarang?', q - 0.1, 0.04) +
          f"    tl.to(['#a-gb','#a-q'], {{opacity: 0, y: -40, duration: .3, ease: 'power2.in'}}, {c(3) - t0 - 0.2:.3f});\n"
          + blur_in('#a-p', T.t(3, 'paling') - t0 - 0.3) + blur_in('#a-s', T.cue(4) - t0 - 0.1))
    sa = shell('sa', "", html, js, t1 - t0).replace(
        "tl.fromTo('#sa-w', {x: 260, filter: 'blur(18px)', opacity: 0}, {x: 0, filter: 'blur(0px)', opacity: 1, duration: .32, ease: 'power3.out'}, 0);", "")
    S.append(('sa', t0, t1 - t0, sa))

    # S1 reason 1: price drop bars -----------------------------------------------------------------------
    t0, t1 = span(5, 10)
    html = """
      <div id="b-n" class="tile" style="left:70px;top:220px">01</div>
      <div style="position:absolute;left:250px;top:226px;width:720px" class="h2"><span class="line"><span id="b-l1">Lebih banyak gram</span></span>
        <span class="line"><span id="b-l2" class="g">pada harga diskaun</span></span></div>
      <div class="card" style="left:70px;top:520px;width:880px;height:660px">
        <div style="position:absolute;left:40px;top:34px" class="k">Harga emas / gram</div>
        <div class="bb" id="b-b1" style="left:140px;height:360px;background:#d9dce2"><div class="bv">RM764</div><div class="bx">Tertinggi</div></div>
        <div class="bb" id="b-b2" style="left:480px;height:237px;background:linear-gradient(180deg,#F5D27A,#C9952B)"><div class="bv">RM503</div><div class="bx">Hari ini</div></div>
        <div id="b-d" style="position:absolute;left:640px;top:150px;padding:14px 22px;border-radius:20px;background:#E5484D;color:#fff;font:800 56px 'Jost',sans-serif">&minus;34%</div>
        <svg id="b-ar" viewBox="0 0 120 200" style="position:absolute;left:390px;top:130px;width:90px;height:150px"><path d="M10 10 C 80 20 100 90 90 180" fill="none" stroke="#E5484D" stroke-width="7" stroke-dasharray="14 10"/>
          <polygon points="90,195 74,165 106,168" fill="#E5484D"/></svg></div>"""
    css = """
    .bb { position: absolute; bottom: 110px; width: 220px; border-radius: 22px 22px 8px 8px; transform-origin: 50% 100%; }
    .bv { position: absolute; left: -20px; right: -20px; top: -70px; text-align: center; font: 800 54px 'Jost', sans-serif; color: #0b0b0f; }
    .bx { position: absolute; left: -20px; right: -20px; bottom: -64px; text-align: center; font: 600 34px 'Jost', sans-serif; color: #6b7079; }"""
    js = (f"    tl.fromTo('#b-n', {{opacity: 0, scale: .4, rotation: -20}}, {{opacity: 1, scale: 1, rotation: 0, duration: .5, ease: 'back.out(2)'}}, 0.2);\n"
          + up('#b-l1', 0.3) + up('#b-l2', 0.45) + "    tl.set(['#b-b1','#b-b2'], {scaleY: 0}, 0);\n    tl.set(['#b-d','#b-ar'], {opacity: 0}, 0);\n"
          f"    tl.to('#b-b2', {{scaleY: 1, duration: .8, ease: 'power3.out'}}, {T.t(6, 'RM503') - t0 - 0.2:.3f});\n"
          f"    tl.to('#b-b1', {{scaleY: 1, duration: .8, ease: 'power3.out'}}, {T.t(7, 'RM764') - t0 - 0.2:.3f});\n"
          f"    tl.to('#b-ar', {{opacity: 1, duration: .3}}, {T.t(9, '34%') - t0 - 0.6:.3f});\n"
          + pop_in('#b-d', T.t(9, '34%') - t0 - 0.2, 0.45))
    S.append(('sb', t0, t1 - t0, shell('sb', css, html, js, t1 - t0)))

    # S2 same RM1,000 budget: 1.31 g vs 1.99 g, +0.68 g (+52%) --------------------------------------------
    t0, t1 = span(10, 19)
    html = """
      <div style="position:absolute;left:70px;top:226px;width:900px" class="h2"><span class="line"><span id="c-l1">Bajet sama,</span></span>
        <span class="line"><span id="c-l2"><span class="g">RM1,000</span></span></span></div>
      <img id="c-m" src="assets/money_cut.png" style="position:absolute;left:640px;top:170px;width:300px;filter:drop-shadow(0 24px 24px rgba(0,40,0,.18))">
      <div id="c-k1" class="card gc" style="left:70px;top:520px"><div class="k">Harga puncak</div><div class="gp">RM764/g</div>
        <div class="gg"><span id="c-v1">0.00</span> g</div></div>
      <div id="c-k2" class="card gc" style="left:520px;top:520px;border:4px solid #C9952B"><div class="k">Harga hari ini</div><div class="gp">RM503/g</div>
        <div class="gg g"><span id="c-v2">0.00</span> g</div></div>
      <div id="c-x" class="card" style="left:70px;top:930px;width:880px;height:230px;background:#0b0b0f">
        <div style="position:absolute;left:40px;top:30px;font:600 34px 'Jost',sans-serif;color:#b9bec6">Dengan duit yang sama, bawa pulang</div>
        <div style="position:absolute;left:40px;top:86px;font:800 100px 'Jost',sans-serif;color:#F5D27A">+0.68 g</div>
        <div id="c-p" style="position:absolute;right:40px;top:96px;padding:12px 24px;border-radius:999px;background:#16A34A;color:#fff;font:800 60px 'Jost',sans-serif">+52%</div></div>"""
    css = """
    .gc { width: 430px; height: 360px; box-sizing: border-box; padding: 34px 36px; }
    .gp { font: 700 50px 'Jost', sans-serif; color: #3a3f47; margin-top: 12px; }
    .gg { font: 800 110px/1 'Jost', sans-serif; color: #0b0b0f; margin-top: 40px; letter-spacing: -3px; }"""
    js = (up('#c-l1', 0.2) + up('#c-l2', 0.35) + "    tl.set(['#c-k1','#c-k2','#c-x','#c-p','#c-m'], {opacity: 0}, 0);\n"
          f"    tl.fromTo('#c-m', {{opacity: 0, y: -80, rotation: -14}}, {{opacity: 1, y: 0, rotation: -4, duration: .8, ease: 'back.out(1.4)'}}, {T.t(10, 'RM1,000') - t0 - 0.3:.3f});\n"
          + floaty('#c-m', T.t(10, 'RM1,000') - t0 + 0.6, 5, 8, 6)
          + blur_in('#c-k1', T.t(11, 'puncak') - t0 - 0.3) + count('#c-v1', 0, 1.31, T.t(12, '1.31') - t0 - 0.3, 0.9, 2)
          + blur_in('#c-k2', T.cue(13) - t0) + count('#c-v2', 0, 1.99, T.t(14, '1.99') - t0 - 0.3, 0.9, 2)
          + f"    tl.fromTo('#c-x', {{opacity: 0, y: 60}}, {{opacity: 1, y: 0, duration: .55, ease: 'expo.out'}}, {T.t(17, '0.68') - t0 - 0.5:.3f});\n"
          + pop_in('#c-p', T.t(18, '52%') - t0 - 0.2, 0.45))
    S.append(('sc', t0, t1 - t0, shell('sc', css, html, js, t1 - t0)))

    # S3 RM1,000 a month for a year: the gap grows (illustrative); opportunity, not a threat ---------------
    t0, t1 = span(19, 23)
    n = 12
    hi = [round((k + 1) * 1.31, 2) for k in range(n)]
    lo = [round((k + 1) * 1.99, 2) for k in range(n)]
    mx = lo[-1]
    X0, X1, Y0, Y1 = 90, 830, 520, 120
    px = lambda k: X0 + k * (X1 - X0) / (n - 1)
    py = lambda v: Y0 - v / mx * (Y0 - Y1)
    l_hi = ' '.join(f"{px(k):.0f},{py(v):.0f}" for k, v in enumerate(hi))
    l_lo = ' '.join(f"{px(k):.0f},{py(v):.0f}" for k, v in enumerate(lo))
    area = f"{l_lo} {' '.join(f'{px(k):.0f},{py(v):.0f}' for k, v in reversed(list(enumerate(hi))))}"
    html = f"""
      <div style="position:absolute;left:70px;top:226px;width:900px" class="h2"><span class="line"><span id="d-l1"><span class="g">RM1,000</span> setiap bulan</span></span>
        <span class="line"><span id="d-l2">dalam setahun</span></span></div>
      <div class="card" style="left:70px;top:480px;width:880px;height:640px">
        <div class="ill" style="right:30px;top:26px">ILUSTRASI</div>
        <div style="position:absolute;left:40px;top:30px" class="k">Gram terkumpul</div>
        <svg viewBox="0 0 880 600" style="position:absolute;left:0;top:40px;width:880px;height:600px">
          <polygon id="d-ar" points="{area}" fill="rgba(201,149,43,.18)"/>
          <polyline id="d-p1" points="{l_hi}" fill="none" stroke="#9aa0a8" stroke-width="7" stroke-linejoin="round" pathLength="100" stroke-dasharray="100 120" stroke-dashoffset="110"/>
          <polyline id="d-p2" points="{l_lo}" fill="none" stroke="#C9952B" stroke-width="9" stroke-linejoin="round" pathLength="100" stroke-dasharray="100 120" stroke-dashoffset="110"/>
          <line x1="{X0}" y1="{Y0}" x2="{X1}" y2="{Y0}" stroke="#d5d8de" stroke-width="3"/>
          <text x="{X0}" y="{Y0 + 50}" font-family="Jost" font-size="30" fill="#8a8f98">Bulan 1</text>
          <text x="{X1}" y="{Y0 + 50}" text-anchor="end" font-family="Jost" font-size="30" fill="#8a8f98">Bulan 12</text>
          <text x="{X1 - 10}" y="{py(lo[-1]) - 22:.0f}" text-anchor="end" font-family="Jost" font-weight="700" font-size="34" fill="#C9952B">harga hari ini</text>
          <text x="{X1 - 10}" y="{py(hi[-1]) + 50:.0f}" text-anchor="end" font-family="Jost" font-weight="700" font-size="34" fill="#8a8f98">harga puncak</text></svg>
        <div id="d-k" style="position:absolute;left:60px;top:160px;padding:10px 20px;border-radius:14px;background:#0b0b0f;color:#F5D27A;font:700 38px 'Jost',sans-serif">perbezaan ketara</div></div>
      <div id="d-a" class="pill" style="left:70px;top:1180px">harga rendah = <b class="gr">peluang</b>, bukan <s class="r">ancaman</s></div>"""
    js = (up('#d-l1', 0.2) + up('#d-l2', 0.35) + "    tl.set(['#d-ar','#d-k','#d-a'], {opacity: 0}, 0);\n"
          f"    tl.to('#d-p1', {{attr: {{'stroke-dashoffset': 0}}, duration: 1.6, ease: 'power2.inOut'}}, 0.7);\n"
          f"    tl.to('#d-p2', {{attr: {{'stroke-dashoffset': 0}}, duration: 1.6, ease: 'power2.inOut'}}, 0.9);\n"
          f"    tl.to('#d-ar', {{opacity: 1, duration: .5}}, {T.t(20, 'ketara') - t0 - 0.4:.3f});\n"
          + pop_in('#d-k', T.t(20, 'ketara') - t0 - 0.2, 0.4) + blur_in('#d-a', T.t(22, 'peluang') - t0 - 0.2))
    S.append(('sd', t0, t1 - t0, shell('sd', "", html, js, t1 - t0)))

    # S4 reason 2: gold moves but never goes to zero (vs a failed company stock), illustrative ----------------
    t0, t1 = span(23, 29)
    html = """
      <div id="e-n" class="tile" style="left:70px;top:220px">02</div>
      <div style="position:absolute;left:250px;top:226px;width:720px" class="h2"><span class="line"><span id="e-l1">Naik turun,</span></span>
        <span class="line"><span id="e-l2">takkan jatuh <span class="g">kosong</span></span></span></div>
      <div class="card" style="left:70px;top:520px;width:880px;height:600px">
        <div class="ill" style="right:30px;top:26px">ILUSTRASI</div>
        <svg viewBox="0 0 880 560" style="position:absolute;left:0;top:40px;width:880px;height:560px">
          <line x1="70" y1="470" x2="830" y2="470" stroke="#E5484D" stroke-width="3" stroke-dasharray="10 10"/>
          <text x="830" y="510" text-anchor="end" font-family="Jost" font-size="30" fill="#E5484D">0 (kosong)</text>
          <polyline id="e-g" points="70,260 140,200 200,250 260,170 330,230 400,150 470,240 540,180 610,260 680,190 750,230 830,160" fill="none" stroke="#C9952B" stroke-width="9" stroke-linejoin="round" pathLength="100" stroke-dasharray="100 120" stroke-dashoffset="110"/>
          <polyline id="e-s" points="70,140 160,160 240,150 320,230 400,300 470,330 540,420 620,468 830,470" fill="none" stroke="#6b7079" stroke-width="7" stroke-linejoin="round" pathLength="100" stroke-dasharray="100 120" stroke-dashoffset="110"/>
          <text id="e-gl" x="830" y="140" text-anchor="end" font-family="Jost" font-weight="700" font-size="36" fill="#C9952B">Emas</text>
          <text id="e-sl" x="600" y="440" text-anchor="end" font-family="Jost" font-weight="700" font-size="32" fill="#6b7079">Saham syarikat lingkup</text></svg></div>
      <div id="e-p1" class="pill" style="left:70px;top:1160px">nilai <b class="g">intrinsik</b> &middot; diiktiraf seluruh dunia</div>"""
    js = (f"    tl.fromTo('#e-n', {{opacity: 0, scale: .4, rotation: -20}}, {{opacity: 1, scale: 1, rotation: 0, duration: .5, ease: 'back.out(2)'}}, 0.2);\n"
          + up('#e-l1', 0.3) + up('#e-l2', 0.45) + "    tl.set(['#e-gl','#e-sl','#e-p1'], {opacity: 0}, 0);\n"
          f"    tl.to('#e-g', {{attr: {{'stroke-dashoffset': 0}}, duration: 2.2, ease: 'power1.inOut'}}, {T.cue(24) - t0:.3f});\n"
          f"    tl.to('#e-gl', {{opacity: 1, duration: .3}}, {T.cue(24) - t0 + 1.8:.3f});\n"
          f"    tl.to('#e-s', {{attr: {{'stroke-dashoffset': 0}}, duration: 1.6, ease: 'power2.in'}}, {T.t(26, 'saham') - t0:.3f});\n"
          f"    tl.to('#e-sl', {{opacity: 1, duration: .3}}, {T.t(26, 'lingkup') - t0:.3f});\n"
          + blur_in('#e-p1', T.t(27, 'intrinsik') - t0 - 0.3))
    S.append(('se', t0, t1 - t0, shell('se', "", html, js, t1 - t0)))

    # S5 reason 3: central banks collect gold aggressively ------------------------------------------------
    t0, t1 = span(29, 37)
    bars = ''.join(f"<img class='sb' id='f-b{i}' src='assets/goldbar_cut.png' style='left:{170 + (i % 4) * 165}px;top:{830 - (i // 4) * 85}px'>" for i in range(12))
    html = f"""
      <div id="f-n" class="tile" style="left:70px;top:220px">03</div>
      <div style="position:absolute;left:250px;top:226px;width:720px" class="h2"><span class="line"><span id="f-l1">Bank pusat dunia</span></span>
        <span class="line"><span id="f-l2"><span class="g">agresif</span> kumpul emas</span></span></div>
      <svg id="f-bk" viewBox="0 0 300 260" style="position:absolute;left:390px;top:420px;width:300px;height:240px">
        <polygon points="150,10 290,80 10,80" fill="#0b0b0f"/><rect x="30" y="90" width="240" height="14" fill="#0b0b0f"/>
        <rect x="50" y="110" width="26" height="110" fill="#0b0b0f"/><rect x="110" y="110" width="26" height="110" fill="#0b0b0f"/>
        <rect x="164" y="110" width="26" height="110" fill="#0b0b0f"/><rect x="224" y="110" width="26" height="110" fill="#0b0b0f"/>
        <rect x="20" y="226" width="260" height="22" fill="#0b0b0f"/></svg>
      {bars}
      <div id="f-q" class="glass" style="left:70px;top:1110px;width:860px;height:150px">
        <div style="position:absolute;left:36px;right:36px;top:24px;font:500 38px/1.25 'Jost',sans-serif;color:#0b0b0f"><span id="f-t"></span></div></div>"""
    css = """
    .sb { position: absolute; width: 130px; filter: drop-shadow(0 10px 10px rgba(80,50,0,.22)); }"""
    js = (f"    tl.fromTo('#f-n', {{opacity: 0, scale: .4, rotation: -20}}, {{opacity: 1, scale: 1, rotation: 0, duration: .5, ease: 'back.out(2)'}}, 0.2);\n"
          + up('#f-l1', 0.3) + up('#f-l2', 0.45) + "    tl.set(['#f-bk','#f-q','.sb'], {opacity: 0}, 0);\n"
          f"    tl.fromTo('#f-bk', {{opacity: 0, y: 40}}, {{opacity: 1, y: 0, duration: .6, ease: 'expo.out'}}, {T.cue(32) - t0 - 0.2:.3f});\n")
    for i in range(12):
        js += f"    tl.fromTo('#f-b{i}', {{opacity: 0, y: -160}}, {{opacity: 1, y: 0, duration: .45, ease: 'bounce.out'}}, {T.t(33, 'mengumpul') - t0 + i * 0.12:.3f});\n"
    js += (f"    tl.fromTo('#f-q', {{opacity: 0, y: 40}}, {{opacity: 1, y: 0, duration: .45, ease: 'expo.out'}}, {T.cue(34) - t0 - 0.4:.3f});\n"
           + typed('#f-t', 'Takkanlah mereka kumpul sesuatu yang tak bernilai.', T.cue(34) - t0 - 0.1, 0.03))
    S.append(('sf', t0, t1 - t0, shell('sf', css, html, js, t1 - t0)))

    # S6 reason 4: reach 1 kg, then hold ----------------------------------------------------------------------
    t0, t1 = span(37, 45)
    R = 230
    circ = 2 * 3.14159 * R
    html = f"""
      <div id="g-n" class="tile" style="left:70px;top:220px">04</div>
      <div style="position:absolute;left:250px;top:226px;width:720px" class="h2"><span class="line"><span id="g-l1">Capai <span class="g">1 kilogram</span>,</span></span>
        <span class="line"><span id="g-l2">kemudian peram</span></span></div>
      <svg viewBox="0 0 560 560" style="position:absolute;left:260px;top:470px;width:560px;height:560px">
        <circle cx="280" cy="280" r="{R}" fill="none" stroke="#eceef2" stroke-width="46"/>
        <circle id="g-r" cx="280" cy="280" r="{R}" fill="none" stroke="#C9952B" stroke-width="46" stroke-linecap="round" stroke-dasharray="0 {circ:.0f}" transform="rotate(-90 280 280)"/>
        <text x="280" y="290" text-anchor="middle" font-family="Jost" font-weight="800" font-size="120" fill="#0b0b0f">1 KG</text>
        <text x="280" y="350" text-anchor="middle" font-family="Jost" font-weight="600" font-size="34" fill="#8a8f98">sasaran jelas</text></svg>
      <div id="g-c" class="card" style="left:70px;top:1080px;width:420px;height:150px;display:flex;align-items:center;gap:16px;padding:0 26px;box-sizing:border-box">
        <svg width="80" height="60" viewBox="0 0 80 60"><polyline points="0,40 15,20 30,35 45,10 60,30 80,15" fill="none" stroke="#9aa0a8" stroke-width="5"/>
          <line x1="0" y1="0" x2="80" y2="60" stroke="#E5484D" stroke-width="6"/></svg>
        <div style="font:600 34px/1.1 'Jost',sans-serif;color:#0b0b0f">Jangan tengok carta setiap hari</div></div>
      <div id="g-p" class="card" style="left:520px;top:1080px;width:420px;height:150px;display:flex;align-items:center;gap:16px;padding:0 26px;box-sizing:border-box;background:#0b0b0f">
        <div style="font:800 44px 'Jost',sans-serif;color:#F5D27A">Peram &amp; sabar</div></div>"""
    kg = T.t(41, 'kilogram') - t0
    js = (f"    tl.fromTo('#g-n', {{opacity: 0, scale: .4, rotation: -20}}, {{opacity: 1, scale: 1, rotation: 0, duration: .5, ease: 'back.out(2)'}}, 0.2);\n"
          + up('#g-l1', 0.3) + up('#g-l2', 0.45) + "    tl.set(['#g-c','#g-p'], {opacity: 0}, 0);\n"
          + blur_in('#g-c', T.t(39, 'carta') - t0 - 0.3) +
          f"    tl.to('#g-r', {{attr: {{'stroke-dasharray': '{circ:.0f} {circ:.0f}'}}, duration: 1.8, ease: 'power2.inOut'}}, {kg - 0.6:.3f});\n"
          + blur_in('#g-p', T.t(42, 'peram') - t0 - 0.3))
    S.append(('sg', t0, t1 - t0, shell('sg', "", html, js, t1 - t0)))

    # S7 reason 5: use the right money --------------------------------------------------------------------------
    t0, t1 = span(45, 53)
    html = """
      <div id="h-n" class="tile" style="left:70px;top:220px">05</div>
      <div style="position:absolute;left:250px;top:226px;width:720px" class="h2"><span class="line"><span id="h-l1">Guna duit</span></span>
        <span class="line"><span id="h-l2" class="g">yang betul</span></span></div>
      <div id="h-x1" class="xr" style="top:520px"><b>&#10005;</b>Duit sewa</div>
      <div id="h-x2" class="xr" style="top:650px"><b>&#10005;</b>Yuran anak</div>
      <div id="h-x3" class="xr" style="top:780px"><b>&#10005;</b>Dana kecemasan</div>
      <div id="h-t" class="card" style="left:70px;top:930px;width:880px;height:150px">
        <div style="position:absolute;left:40px;top:62px;width:800px;height:12px;border-radius:6px;background:#eceef2"></div>
        <div id="h-tf" style="position:absolute;left:40px;top:62px;width:800px;height:12px;border-radius:6px;background:linear-gradient(90deg,#F5D27A,#C9952B);transform-origin:0 50%"></div>
        <div style="position:absolute;left:40px;top:90px;font:600 30px 'Jost',sans-serif;color:#8a8f98">Peram</div>
        <div style="position:absolute;right:40px;top:90px;font:800 34px 'Jost',sans-serif;color:#0b0b0f">3 tahun ke atas</div></div>
      <div id="h-ok" class="pill" style="left:70px;top:1130px"><b class="gr">&#10003;</b> Duit <b class="g">lebihan</b> untuk jangka panjang</div>"""
    css = """
    .xr { position: absolute; left: 70px; width: 880px; height: 110px; border-radius: 24px; background: #fff; box-shadow: 0 14px 34px rgba(20,24,40,.08);
          display: flex; align-items: center; gap: 24px; padding: 0 34px; box-sizing: border-box; font: 700 50px 'Jost', sans-serif; color: #0b0b0f; }
    .xr b { width: 64px; height: 64px; border-radius: 50%; background: #FDE2E3; color: #E5484D; font-size: 38px; display: flex; align-items: center; justify-content: center; }"""
    js = (f"    tl.fromTo('#h-n', {{opacity: 0, scale: .4, rotation: -20}}, {{opacity: 1, scale: 1, rotation: 0, duration: .5, ease: 'back.out(2)'}}, 0.2);\n"
          + up('#h-l1', 0.3) + up('#h-l2', 0.45) + "    tl.set(['#h-x1','#h-x2','#h-x3','#h-t','#h-ok'], {opacity: 0}, 0);\n    tl.set('#h-tf', {scaleX: 0}, 0);\n")
    for i, w in enumerate(['sewa', 'yuran', 'kecemasan'], 1):
        js += f"    tl.fromTo('#h-x{i}', {{opacity: 0, x: -60}}, {{opacity: 1, x: 0, duration: .45, ease: 'expo.out'}}, {T.t(48, w) - t0 - 0.25:.3f});\n"
    js += (f"    tl.to(['#h-x1','#h-x2','#h-x3'], {{opacity: .35, duration: .3}}, {T.cue(49) - t0 - 0.2:.3f});\n"
           f"    tl.fromTo('#h-t', {{opacity: 0, y: 40}}, {{opacity: 1, y: 0, duration: .45, ease: 'expo.out'}}, {T.cue(49) - t0:.3f});\n"
           f"    tl.to('#h-tf', {{scaleX: 1, duration: 1.4, ease: 'power2.inOut'}}, {T.t(49, 'tiga') - t0 - 0.6:.3f});\n"
           + blur_in('#h-ok', T.t(51, 'lebihan') - t0 - 0.3))
    S.append(('sh', t0, t1 - t0, shell('sh', css, html, js, t1 - t0)))

    # S8 closing + CTA (product label card with a blue button) --------------------------------------------------
    t0, t1 = span(53, None)
    html = """
      <div style="position:absolute;left:70px;top:230px;width:900px" class="h2"><span class="line"><span id="i-l1">Orang lain <span class="r">takut</span>,</span></span>
        <span class="line"><span id="i-l2">kita <span class="g">bersedia.</span></span></span></div>
      <div id="i-pl" class="pill" style="left:70px;top:470px">perancangan yang <b class="bl">tenang</b> &amp; <b class="bl">jelas</b></div>
      <img id="i-gb" src="assets/goldbar_100g.png" style="position:absolute;left:380px;top:600px;width:320px;filter:drop-shadow(0 30px 30px rgba(80,50,0,.25))">
      <div id="i-cd" class="card" style="left:110px;top:1030px;width:800px;height:220px">
        <div style="position:absolute;left:36px;top:30px;font:600 30px 'Jost',sans-serif;letter-spacing:4px;color:#8a8f98">SIMPAN EMAS HARI INI</div>
        <div style="position:absolute;left:36px;top:78px;font:800 54px 'Jost',sans-serif;color:#0b0b0f">Azlan &amp; Eza</div>
        <div style="position:absolute;left:36px;top:148px;font:500 32px 'Jost',sans-serif;color:#6b7079">kami bantu sebaiknya</div>
        <div id="i-bt" style="position:absolute;right:32px;top:70px;padding:22px 34px;border-radius:999px;background:#2F6BFF;color:#fff;font:700 40px 'Jost',sans-serif">Hubungi kami</div></div>"""
    hb = T.t(55, 'hubungi') - t0
    js = (up('#i-l1', 0.2) + up('#i-l2', T.t(53, 'itulah') - t0 - 0.2) + "    tl.set(['#i-pl','#i-gb','#i-cd'], {opacity: 0}, 0);\n"
          + blur_in('#i-pl', T.t(54, 'tenang') - t0 - 0.3) +
          f"    tl.fromTo('#i-gb', {{opacity: 0, y: 100, rotationY: 40}}, {{opacity: 1, y: 0, rotationY: 0, duration: .9, ease: 'expo.out'}}, {T.t(54, 'perancangan') - t0:.3f});\n"
          + floaty('#i-gb', T.t(54, 'perancangan') - t0 + 0.9, t1 - t0 - 2, 10, 6) +
          f"    tl.fromTo('#i-cd', {{opacity: 0, y: 80}}, {{opacity: 1, y: 0, duration: .55, ease: 'expo.out'}}, {T.cue(55) - t0 - 0.1:.3f});\n"
          f"    tl.to('#i-bt', {{scale: .92, duration: .1, yoyo: true, repeat: 1}}, {hb + 0.4:.3f});\n")
    js_scene = (f"    tl.fromTo('#si-w', {{scale: 1}}, {{scale: 1.045, duration: {t1 - t0:.2f}, ease: 'none'}}, 0);\n"
                f"    tl.fromTo('#si-w', {{x: 260, filter: 'blur(18px)', opacity: 0}}, {{x: 0, filter: 'blur(0px)', opacity: 1, duration: .32, ease: 'power3.out'}}, 0);\n" + js)
    S.append(('si', t0, t1 - t0, scene('si', CSS, f"<div id='si-w' class='wd'>{html}</div>", js_scene)))
    return S


def caption_scene(words, total):
    groups, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        if (len(cur) >= 5 or nxt is None or nxt['cue'] != w['cue'] or w['w'][-1] in '.,?!' or nxt['os'] - w['oe'] > 0.25):
            groups.append(cur); cur = []
    html, js = [], []
    for gi, g in enumerate(groups):
        spans = ''.join(f"<span id='cw{gi}_{k}'>{w['w']}</span>" for k, w in enumerate(g))
        html.append(f"    <div id='cg{gi}' class='cg'><div class='cin'>{spans}</div></div>")
        a = max(0.0, g[0]['os'] - 0.08)
        b = min(g[-1]['oe'] + 0.35, groups[gi + 1][0]['os'] - 0.08 if gi + 1 < len(groups) else total)
        js.append(f"    tl.set('#cg{gi}', {{opacity: 1, visibility: 'visible'}}, {a:.3f});")
        js.append(f"    tl.fromTo('#cg{gi} .cin', {{y: 10, opacity: 0}}, {{y: 0, opacity: 1, duration: .16, ease: 'power2.out'}}, {a:.3f});")
        for k, w in enumerate(g):
            js.append(f"    tl.set('#cw{gi}_{k}', {{color: '#F5D27A'}}, {w['os']:.3f});")
            if k < len(g) - 1:
                js.append(f"    tl.set('#cw{gi}_{k}', {{color: '#FFFFFF'}}, {g[k + 1]['os']:.3f});")
        js.append(f"    tl.set('#cg{gi}', {{opacity: 0, visibility: 'hidden'}}, {b:.3f});")
    css = FACES + """
    .cg { position: absolute; left: 60px; width: 860px; top: 1290px; text-align: center; opacity: 0; visibility: hidden; }
    .cin { display: inline-block; padding: 8px 20px 10px; border-radius: 16px; background: rgba(11,11,15,.82);
           font: 600 46px/1.2 'Jost', sans-serif; color: #FFFFFF; }
    .cin span { display: inline-block; margin: 0 .14em; }"""
    return scene('captions', css, '\n'.join(html), '\n'.join(js))


def outro_scene():
    css = FACES + """
    #o-bg { position: absolute; inset: 0; background: #F5F5F7; }
    #o-logo { position: absolute; left: 340px; top: 660px; width: 400px; }
    #o-t { position: absolute; left: 0; width: 1080px; top: 1110px; text-align: center; font: 600 32px 'Jost', sans-serif; letter-spacing: 10px; color: #0b0b0f; }"""
    html = """<div id="o-bg"></div><img id="o-logo" src="assets/logo.png"><div id="o-t">AZLAN &amp; EZA</div>"""
    js = ("    tl.fromTo('#o-bg', {opacity: 0}, {opacity: 1, duration: .3}, 0);\n"
          "    tl.fromTo('#o-logo', {opacity: 0, y: 40, scale: .92}, {opacity: 1, y: 0, scale: 1, duration: .7, ease: 'expo.out'}, .2);\n"
          + blur_in('#o-t', .7) + f"    tl.to('#root', {{opacity: 0, duration: .45, ease: 'power2.in'}}, {OUTRO - 0.5:.2f});\n")
    return scene('outro', css, html, js)


def css_initial(src):
    import re
    rules = []
    for m in re.finditer(r"tl\.set\((\[[^\]]*\]|'[^']*'), \{(opacity: 0)\}, 0\);", src):
        sels = [x.strip().strip("'") for x in m.group(1).strip('[]').split(',')]
        rules.append(f"    {', '.join(sels)} {{ opacity: 0; }}")
    return src.replace('  </style>', '\n'.join(rules) + '\n  </style>', 1)


def write_project(proj, words, total):
    T = Words(words)
    a = os.path.join(proj, 'assets'); comp = os.path.join(proj, 'compositions')
    os.makedirs(comp, exist_ok=True); os.makedirs(os.path.join(a, 'fonts'), exist_ok=True)
    for f in ('Jost-Medium.ttf', 'Jost-SemiBold.ttf', 'Jost-Bold.ttf', 'Jost-ExtraBold.ttf'):
        shutil.copy(os.path.join(FONTS, f), os.path.join(a, 'fonts', f))
    for src in (('13', 'proj', 'assets', 'logo.png'), ('13', 'proj', 'assets', 'gsap.min.js'), ('13', 'gold', 'goldbar_100g.png')):
        shutil.copy(os.path.join(REPO, 'work', *src), a)
    for f in ('goldbar_cut.png', 'money_cut.png'):
        shutil.copy(os.path.join(REPO, 'video-style', 'videos', '11_assets', f), a)
    for f in ('whoosh', 'whoosh-short', 'pop', 'click-soft', 'click', 'key-press', 'sparkle', 'impact-bass-1', 'riser', 'ping', 'chime'):
        shutil.copy(os.path.join(SFX_DIR, f + '.mp3'), os.path.join(a, f'sfx-{f}.mp3'))
    dur = round(total + OUTRO, 3)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '14', '-i', MUSIC_SRC, '-ss', '20', '-i', MUSIC_SRC, '-ss', '20', '-i', MUSIC_SRC,
                    '-filter_complex', '[0:a][1:a]acrossfade=d=4:c1=tri:c2=tri[x];[x][2:a]acrossfade=d=4:c1=tri:c2=tri[m]', '-map', '[m]',
                    '-t', str(dur + 1), '-c:a', 'aac', '-b:a', '192k', os.path.join(a, 'music-bed.m4a')], check=True)
    scenes = build(T, total)
    for sid, st, du, src in scenes:
        open(os.path.join(comp, f'{sid}.html'), 'w').write(css_initial(src))
    open(os.path.join(comp, 'captions.html'), 'w').write(caption_scene(words, total))
    open(os.path.join(comp, 'outro.html'), 'w').write(outro_scene())

    speech, cur = [], None
    for w in words:
        if cur and w['os'] - cur[1] < 0.6:
            cur[1] = w['oe']
        else:
            if cur: speech.append(tuple(cur))
            cur = [w['os'], w['oe']]
    speech.append(tuple(cur))
    pts, t = [{'t': 0, 'v': 0.3}], 0
    for a0, b0 in speech:
        pts += [{'t': round(max(0, a0 - 0.25), 3), 'v': 0.3 if a0 - t > 0.9 else 0.13}, {'t': round(a0, 3), 'v': 0.13}, {'t': round(b0, 3), 'v': 0.13}]
        t = b0
    pts += [{'t': round(total, 3), 'v': 0.13}, {'t': round(total + 0.6, 3), 'v': 0.45}]
    lane = []
    for p in sorted(pts, key=lambda p: p['t']):
        if lane and p['t'] - lane[-1]['t'] < 0.05:
            lane[-1] = p
        else:
            lane.append(p)

    sfx = []
    for i, (sid, st, du, _) in enumerate(scenes[1:]):
        sfx.append((['whoosh-short', 'whoosh'][i % 2], st - 0.05, .4))
    sfx += [('chime', 0.1, .3), ('key-press', T.cue(2) - 0.1, .3), ('key-press', T.cue(2) + 0.4, .3), ('pop', T.t(3, 'paling') - 0.3, .35)]
    for cu in (5, 23, 29, 37, 45):
        sfx.append(('pop', T.cue(cu), .45))
    sfx += [('click-soft', T.t(6, 'RM503') - 0.2, .6), ('click-soft', T.t(7, 'RM764') - 0.2, .6), ('impact-bass-1', T.t(9, '34%') - 0.2, .4),
            ('sparkle', T.t(10, 'RM1,000') - 0.3, .35), ('ping', T.t(12, '1.31'), .3), ('ping', T.t(14, '1.99'), .3),
            ('riser', T.t(17, '0.68') - 2.0, .25), ('impact-bass-1', T.t(18, '52%') - 0.2, .45), ('sparkle', T.t(20, 'ketara') - 0.2, .35),
            ('pop', T.t(22, 'peluang') - 0.2, .35), ('whoosh-short', T.t(26, 'saham'), .3), ('sparkle', T.t(27, 'intrinsik') - 0.3, .3),
            ('pop', T.t(33, 'mengumpul'), .35), ('pop', T.t(33, 'mengumpul') + 0.6, .3), ('pop', T.t(33, 'mengumpul') + 1.2, .3),
            ('sparkle', T.t(41, 'kilogram') + 0.9, .4), ('click-soft', T.t(48, 'sewa') - 0.25, .6), ('click-soft', T.t(48, 'yuran') - 0.25, .6),
            ('click-soft', T.t(48, 'kecemasan') - 0.25, .6), ('ping', T.t(51, 'lebihan') - 0.3, .3), ('click', T.t(55, 'hubungi') + 0.4, .8),
            ('whoosh', total - 0.1, .4)]
    tags, lanes_end = [], []
    for i, (n, t, v) in enumerate(sorted(sfx, key=lambda s: s[1])):
        t = max(0.0, t)
        d = round(min(sfx_len(os.path.join(a, f'sfx-{n}.mp3')), dur - t - 0.01), 3)
        k = next((j for j, e in enumerate(lanes_end) if e <= t), None)
        if k is None:
            lanes_end.append(0); k = len(lanes_end) - 1
        lanes_end[k] = t + d
        tags.append(f'    <audio id="sfx{i}" class="clip" src="assets/sfx-{n}.mp3" data-start="{t:.3f}" data-duration="{d:.3f}" '
                    f'data-track-index="{10 + k}" data-volume="{v}"></audio>')
    hosts = [f'    <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{st:.3f}" '
             f'data-duration="{du:.3f}" data-track-index="{2 + i % 2}" data-track-kind="graphics" data-width="{W}" data-height="{H}" '
             f'style="z-index: 20"></div>' for i, (sid, st, du, _) in enumerate(scenes)]
    lane_json = json.dumps({'version': 1, 'lanes': [{'target': 'volume', 'points': lane[:500]}]}).replace('"', '&quot;')
    index = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="assets/gsap.min.js"></script>
  <style>
    html, body {{ margin: 0; padding: 0; background: #F5F5F7; }}
    #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: #F5F5F7; }}
    #studio {{ position: absolute; inset: 0; background: radial-gradient(90% 55% at 50% 30%, #FFFFFF 0%, #F5F5F7 60%, #ECEDF1 100%); }}
    #capwrap {{ position: absolute; inset: 0; z-index: 30; }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="{W}" data-height="{H}">
    <div id="studio"></div>
{chr(10).join(hosts)}
    <div id="capwrap"><div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0"
         data-duration="{total:.3f}" data-track-index="4" data-track-kind="captions" data-width="{W}" data-height="{H}"></div></div>
    <div id="outro" data-composition-id="outro" data-composition-src="compositions/outro.html" data-start="{total:.3f}"
         data-duration="{OUTRO}" data-track-index="5" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index: 40"></div>
    <audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{total:.3f}" data-track-index="0" data-volume="1"></audio>
    <audio id="music" class="clip" src="assets/music-bed.m4a" data-start="0" data-duration="{dur}" data-track-index="8"
           data-volume="1" data-fade-in="0.4" data-fade-out="1.5" data-automation="{lane_json}"></audio>
{chr(10).join(tags)}
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.set({{}}, {{}}, {dur});
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
"""
    open(os.path.join(proj, 'index.html'), 'w').write(index)
    return scenes
