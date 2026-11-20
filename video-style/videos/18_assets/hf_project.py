"""HyperFrames project for video 18 (China beli 26 tan emas). Look: "Gold Terminal" (new, unlike videos 1-17).

Black market-terminal panels, amber data, cyan accents, green/red moves; Outfit (headlines), Source Code Pro (data).
  * FULL  - talking head fills the frame; a terminal deck sits on the wall above the head (y 176-470).
  * SPLIT - the camera rides up so the face sits in the top half (face whole), the picture is cut at y 840 and a
            terminal chart panel fills y 860-1215 below it. Captions stay at y ~1236.
Subtitles (asked to look professional): clean Outfit on a soft dark gradient band, phrase by phrase, keywords amber,
the spoken word lifts slightly.
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
MUSIC_SRC = os.path.join(REPO, 'work', '15', 'proj', 'assets', 'music-bed.m4a')   # approved documentary track
SHIFT = -400        # SPLIT: camera moves up so the face (y ~560-1190) sits at ~160-790
CUT = 840           # picture cut line in SPLIT

CSS = """
    .deck { position: absolute; left: 50px; top: 176px; width: 980px; height: 294px; border-radius: 14px; overflow: hidden;
            background: rgba(8,10,14,.93); box-shadow: 0 24px 60px rgba(0,0,0,.4), inset 0 0 0 1px rgba(255,176,0,.35); }
    .deck::before, .pan::before { content: ''; position: absolute; inset: 0; pointer-events: none;
            background-image: linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px); background-size: 100% 6px; }
    .bar { position: absolute; left: 0; right: 0; top: 0; height: 46px; background: rgba(255,176,0,.10); border-bottom: 1px solid rgba(255,176,0,.35);
           display: flex; align-items: center; gap: 18px; padding: 0 24px; box-sizing: border-box;
           font: 600 28px 'Source Code Pro', monospace; color: #FFB000; letter-spacing: 2px; }
    .bar i { width: 12px; height: 12px; border-radius: 50%; background: #3DDC84; box-shadow: 0 0 10px #3DDC84; }
    .bar .r { margin-left: auto; color: #6EE7F9; }
    .hl { font: 800 70px/1.02 'Outfit', sans-serif; color: #F5F5F0; letter-spacing: -1px; }
    .md { font: 600 40px/1.2 'Outfit', sans-serif; color: #cfd3da; }
    .am { color: #FFB000; } .cy { color: #6EE7F9; } .up { color: #3DDC84; } .dn { color: #FF5A5F; }
    .num { font: 700 120px/1 'Source Code Pro', monospace; letter-spacing: -4px; }
    .pan { position: absolute; left: 50px; top: 862px; width: 980px; height: 350px; border-radius: 16px; overflow: hidden;
           background: rgba(8,10,14,.96); box-shadow: 0 -10px 40px rgba(0,0,0,.4), inset 0 0 0 1px rgba(255,176,0,.35); }
    .src { position: absolute; right: 22px; bottom: 14px; font: 500 28px 'Source Code Pro', monospace; color: #7c8592; }
"""


def deck(sid, label, right=''):
    return (f"<div id='{sid}' class='deck'><div class='bar'><i></i>{label}<span class='r'>{right}</span></div>")


def pan(sid, label, right=''):
    return (f"<div id='{sid}' class='pan'><div class='bar'><i></i>{label}<span class='r'>{right}</span></div>")


def wipe_in(sel, t):
    return (f"    tl.fromTo('{sel}', {{opacity: 0, clipPath: 'inset(0 0 100% 0)'}}, {{opacity: 1, clipPath: 'inset(0 0 0% 0)', duration: .5, ease: 'power3.out'}}, {t:.3f});\n")


def swap(a, b, t):
    return blur_out(a, t - 0.22, 0.2) + blur_in(b, t, 0.4, 18) + f"    tl.set('{b}', {{opacity: 0}}, 0);\n"


def typed(sel, text, t, rate=0.035):
    js = f"    tl.set('{sel}', {{textContent: ''}}, 0);\n"
    for k in range(1, len(text) + 1, 2):
        js += f"    tl.set('{sel}', {{textContent: {json.dumps(text[:k])}}}, {t + k * rate:.3f});\n"
    js += f"    tl.set('{sel}', {{textContent: {json.dumps(text)}}}, {t + len(text) * rate:.3f});\n"
    return js


def count(sel, a, b, t, d, fmt='int', suffix=''):
    f = {'int': "Math.round(o.v).toLocaleString('en-US')", 'd1': "o.v.toFixed(1)"}[fmt]
    return (f"    (() => {{ const o = {{v: {a}}}; tl.to(o, {{v: {b}, duration: {d}, ease: 'power3.out', onUpdate: () => "
            f"{{ document.querySelector('{sel}').textContent = {f} + '{suffix}'; }}}}, {t:.3f}); }})();\n")


def build(T, total):
    S, split = [], []
    c = T.cue

    # S0 HOOK -----------------------------------------------------------------------------------
    t0, t1 = 0.0, c(5) - 0.1
    html = deck('a-d', 'XAU &middot; HARGA EMAS', 'PBOC') + """
      <div style="position:absolute;left:28px;top:66px"><div class="md">Harga emas</div><div class="hl dn">JATUH &#9660;</div></div>
      <div style="position:absolute;left:470px;top:66px;width:480px"><div class="md">China beli</div>
        <div><span id="a-n" class="num am">??</span><span class="hl am" style="font-size:60px"> TAN</span></div></div>
      <div id="a-s" style="position:absolute;left:470px;top:232px" class="md">dalam <span class="cy">sebulan</span></div>
      <div id="a-q" style="position:absolute;left:0;right:0;top:110px;text-align:center" class="hl">MENGAPA<span class="am">?</span><span id="a-cur" class="am">_</span></div></div>"""
    n = T.t(1, '26') - t0
    js = ("    tl.set('#a-d', {opacity: 1}, 0);\n    tl.set('#a-s', {opacity: 0}, 0);\n" + count('#a-n', 0, 26, n - 0.5, 0.7)
          + blur_in('#a-s', T.t(2, 'sebulan') - t0 - 0.3) +
          f"    tl.to('#a-d > div:not(.bar):not(#a-q)', {{opacity: 0, filter: 'blur(8px)', duration: .2}}, {c(3) - t0 - 0.25:.3f});\n"
          f"    tl.fromTo('#a-q', {{opacity: 0, scale: 1.3}}, {{opacity: 1, scale: 1, duration: .25, ease: 'expo.out'}}, {c(3) - t0:.3f});\n"
          f"    tl.set('#a-q', {{opacity: 0}}, 0);\n")
    for k in range(6):
        js += f"    tl.set('#a-cur', {{opacity: {k % 2}}}, {c(3) - t0 + k * 0.25:.3f});\n"
    js += blur_out('#a-d', t1 - t0 - 0.3)
    S.append(('sa', t0, t1 - t0, scene('sa', CSS, html, js)))

    # S1 panic vs China adding reserves ---------------------------------------------------------
    t0, t1 = c(5) - 0.1, c(8) - 0.15
    html = deck('b-d', 'SENTIMEN PASARAN') + """
      <div id="b-1" style="position:absolute;left:28px;top:70px;width:440px"><div class="md">Ramai orang</div><div class="hl dn" style="font-size:58px">PANIK</div>
        <div class="md" style="font-size:32px">harga emas turun</div></div>
      <div style="position:absolute;left:490px;top:70px;width:2px;height:190px;background:rgba(255,176,0,.35)"></div>
      <div id="b-2" style="position:absolute;left:520px;top:70px;width:440px"><div class="md">China pula</div><div class="hl up" style="font-size:58px;white-space:nowrap">TAMBAH RIZAB</div>
        <div class="md" style="font-size:32px">emas negara &#9650;</div></div></div>"""
    js = (wipe_in('#b-d', 0.1) + "    tl.set(['#b-1','#b-2'], {opacity: 0}, 0);\n" + blur_in('#b-1', T.t(5, 'panik') - t0 - 0.2)
          + blur_in('#b-2', T.t(7, 'menambah') - t0 - 0.3) + blur_out('#b-d', t1 - t0 - 0.3))
    S.append(('sb', t0, t1 - t0, scene('sb', CSS, html, js)))

    # S2 the question --------------------------------------------------------------------------
    t0, t1 = c(8) - 0.15, c(10) - 0.15
    html = deck('c-d', 'PERSOALAN') + """
      <div style="position:absolute;left:28px;top:70px;font:600 40px 'Source Code Pro',monospace;color:#6EE7F9">&gt; <span id="c-t1"></span></div>
      <div id="c-a" style="position:absolute;left:28px;top:130px" class="hl" >Pakar China <span class="dn">tak tahu?</span></div>
      <div id="c-b" style="position:absolute;left:28px;top:130px" class="hl">Atau <span class="am">strategi berbeza?</span></div></div>"""
    js = (wipe_in('#c-d', 0.1) + typed('#c-t1', 'harga_emas.sedang_jatuh()', 0.4) + "    tl.set(['#c-a','#c-b'], {opacity: 0}, 0);\n"
          + blur_in('#c-a', T.t(8, 'pakar') - t0) + swap('#c-a', '#c-b', T.cue(9) - t0) + blur_out('#c-d', t1 - t0 - 0.3))
    S.append(('sc', t0, t1 - t0, scene('sc', CSS, html, js)))

    # S3 SPLIT: the facts -- price -6.3%, China +26 t, biggest in 3 years, 24-month streak -----------
    t0, t1 = c(10) - 0.15, c(18) - 0.15
    split.append((c(11) - 0.4, c(20) - 0.35))
    dots = ''.join(f"<div class='sq' id='d-q{i}' style='left:{30 + (i % 12) * 78}px;top:{232 + (i // 12) * 50}px'></div>" for i in range(24))
    html = deck('d-d', 'FAKTA', '') + """
      <div style="position:absolute;left:28px;top:84px" class="hl">Beberapa fakta <span class="am">menarik</span></div></div>
      """ + pan('d-p', 'WORLD GOLD COUNCIL &middot; 17 NOV 2026', 'OKTOBER') + f"""
        <div id="d-k1" class="kp" style="left:30px"><div class="kl">HARGA EMAS DUNIA</div><div class="kv dn">&#9660; <span id="d-v1">0.0</span>%</div></div>
        <div id="d-k2" class="kp" style="left:520px"><div class="kl">BANK PUSAT CHINA</div><div class="kv up">+<span id="d-v2">0</span> TAN</div></div>
        <div id="d-tag" style="position:absolute;left:520px;top:200px;padding:6px 14px;border-radius:8px;background:#FFB000;color:#0a0c10;font:700 30px 'Outfit',sans-serif">Belian bulanan terbesar &middot; 3 tahun</div>
        <div id="d-st">{dots}<div style="position:absolute;left:30px;top:196px;font:600 28px 'Source Code Pro',monospace;color:#FFB000">24 BULAN BERTURUT-TURUT</div></div></div>"""
    css = CSS + """
    .kp { position: absolute; top: 64px; width: 440px; }
    .kl { font: 600 28px 'Source Code Pro', monospace; color: #8b94a3; letter-spacing: 2px; }
    .kv { font: 700 96px/1.05 'Source Code Pro', monospace; letter-spacing: -3px; }
    .sq { position: absolute; width: 62px; height: 38px; border-radius: 6px; background: rgba(255,176,0,.12); border: 1px solid rgba(255,176,0,.35); }"""
    p63 = T.t(12, '6.3%') - t0
    t26 = T.t(14, '26') - t0
    st = T.t(16, '24') - t0
    js = (wipe_in('#d-d', 0.1) + blur_out('#d-d', c(11) - t0 - 0.6) +
          f"    tl.fromTo('#d-p', {{opacity: 0, y: 80}}, {{opacity: 1, y: 0, duration: .6, ease: 'expo.out'}}, {c(11) - t0 - 0.2:.3f});\n"
          "    tl.set(['#d-k1','#d-k2','#d-tag','#d-st'], {opacity: 0}, 0);\n"
          + blur_in('#d-k1', p63 - 0.4) + count('#d-v1', 0, 6.3, p63 - 0.3, 0.8, 'd1')
          + blur_in('#d-k2', t26 - 0.4) + count('#d-v2', 0, 26, t26 - 0.3, 0.8)
          + pop_in('#d-tag', T.t(15, 'terbesar') - t0 - 0.1)
          + f"    tl.to(['#d-k1','#d-k2','#d-tag'], {{y: -40, opacity: .0, duration: .3}}, {st - 1.2:.3f});\n"
          + f"    tl.to('#d-st', {{opacity: 1, duration: .2}}, {st - 0.9:.3f});\n")
    for i in range(24):
        js += f"    tl.to('#d-q{i}', {{background: '#FFB000', duration: .08}}, {st - 0.8 + i * 0.06:.3f});\n"
    S.append(('sd', t0, t1 - t0, scene('sd', css, html, js)))

    # S4 SPLIT: 2,435 tonnes + the WGC chart + BNC quote ------------------------------------------
    t0, t1 = c(18) - 0.15, c(20) - 0.15
    html = pan('e-p', 'RIZAB EMAS RASMI CHINA', 'TAN') + """
        <div style="position:absolute;left:30px;top:70px"><span id="e-n" class="num am">0</span><span class="hl am" style="font-size:60px"> TAN</span></div>
        <div id="e-w" style="position:absolute;left:560px;top:60px;width:400px;height:270px;border-radius:10px;overflow:hidden;background:#fff">
          <img src="assets/wgc_chart.jpg" style="width:400px"></div>
        <div id="e-q" style="position:absolute;left:30px;top:200px;width:500px;font:500 28px/1.3 'Outfit',sans-serif;color:#cfd3da">
          &ldquo;China&rsquo;s central bank added nearly <b class="am">26 tonnes</b> of gold in October, extending its buying streak to <b class="am">24 months</b>&hellip;&rdquo;
          <div style="font:500 28px 'Source Code Pro',monospace;color:#7c8592;margin-top:6px">&mdash; BNC, 9 Nov 2026</div></div></div>"""
    js = ("    tl.set('#e-p', {opacity: 1}, 0);\n    tl.set(['#e-w','#e-q'], {opacity: 0}, 0);\n"
          + count('#e-n', 0, 2435, T.t(18, '2,435') - t0 - 0.6, 1.2)
          + f"    tl.fromTo('#e-w', {{opacity: 0, x: 60, rotation: 3}}, {{opacity: 1, x: 0, rotation: 0, duration: .6, ease: 'expo.out'}}, 0.3);\n"
          + blur_in('#e-q', 1.0))
    S.append(('se', t0, t1 - t0, scene('se', CSS, html, js)))

    # S5 FULL: the fact few know -- tonnes up, USD value down 5.3% ---------------------------------
    t0, t1 = c(20) - 0.15, c(28) - 0.15
    html = deck('f-d', 'FAKTA YANG RAMAI TAK TAHU', 'OKTOBER') + """
      <div id="f-1" class="kc" style="left:28px"><div class="kl">TAN EMAS</div><div class="kv up">+26 &#9650;</div></div>
      <div id="f-2" class="kc" style="left:520px"><div class="kl">NILAI RIZAB (USD)</div><div class="kv dn">&minus;5.3% &#9660;</div></div>
      <div id="f-w" style="position:absolute;left:28px;top:70px" class="hl">Kenapa? <span class="dn">Harga emas turun.</span></div></div>"""
    css = CSS + """
    .kc { position: absolute; top: 76px; width: 440px; }
    .kl { font: 600 28px 'Source Code Pro', monospace; color: #8b94a3; letter-spacing: 2px; }
    .kv { font: 700 100px/1.05 'Source Code Pro', monospace; letter-spacing: -3px; }"""
    js = (wipe_in('#f-d', 0.1) + "    tl.set(['#f-1','#f-2','#f-w'], {opacity: 0}, 0);\n" + blur_in('#f-1', T.t(22, '26') - t0 - 0.3)
          + blur_in('#f-2', T.t(24, '5.3%') - t0 - 0.3)
          + f"    tl.to(['#f-1','#f-2'], {{opacity: 0, filter: 'blur(8px)', duration: .2}}, {c(25) - t0 - 0.25:.3f});\n"
          + blur_in('#f-w', c(25) - t0) + blur_out('#f-d', t1 - t0 - 0.3))
    S.append(('sf', t0, t1 - t0, scene('sf', css, html, js)))

    # S6 FULL: still risky -> why they still buy (3 reasons) --------------------------------------
    t0, t1 = c(28) - 0.15, c(34) - 0.15
    html = deck('g-d', 'KENAPA MASIH BELI?') + """
      <div id="g-r" style="position:absolute;left:28px;top:80px" class="hl">China juga terdedah <span class="dn">risiko</span></div>
      <div id="g-n" style="position:absolute;left:28px;top:80px" class="hl">Bukan semata-mata <span class="am">untung</span></div>
      <div id="g-1" class="rs" style="top:66px"><b>01</b>Pelbagaikan <span class="am">rizab negara</span></div>
      <div id="g-2" class="rs" style="top:136px"><b>02</b>Kurang bergantung pada <span class="am">aset USD</span></div>
      <div id="g-3" class="rs" style="top:206px"><b>03</b>Urus risiko <span class="am">ekonomi &amp; geopolitik</span></div></div>"""
    css = CSS + """
    .rs { position: absolute; left: 28px; width: 920px; height: 62px; display: flex; align-items: center; gap: 18px;
          border-bottom: 1px solid rgba(255,176,0,.25); font: 600 40px 'Outfit', sans-serif; color: #F5F5F0; }
    .rs b { font: 700 30px 'Source Code Pro', monospace; color: #6EE7F9; }"""
    js = (wipe_in('#g-d', 0.1) + "    tl.set(['#g-r','#g-n','#g-1','#g-2','#g-3'], {opacity: 0}, 0);\n" + blur_in('#g-r', T.t(28, 'terdedah') - t0 - 0.3)
          + swap('#g-r', '#g-n', T.t(30, 'bukan') - t0)
          + f"    tl.to('#g-n', {{opacity: 0, duration: .2}}, {c(32) - t0 - 0.3:.3f});\n")
    for i, (cu, w) in enumerate([(32, 'mempelbagaikan'), (32, 'mengurangkan'), (33, 'mengurus')], 1):
        js += f"    tl.fromTo('#g-{i}', {{opacity: 0, x: -40}}, {{opacity: 1, x: 0, duration: .4, ease: 'expo.out'}}, {T.t(cu, w) - t0 - 0.2:.3f});\n"
    js += blur_out('#g-d', t1 - t0 - 0.3)
    S.append(('sg', t0, t1 - t0, scene('sg', css, html, js)))

    # S7 SPLIT: central banks 675 t in 9M 2026, +6% -------------------------------------------------
    t0, t1 = c(34) - 0.15, c(42) - 0.15
    split.append((c(35) - 0.4, c(42) - 0.35))
    html = deck('h-d', 'BUKAN CHINA SAHAJA') + """
      <div style="position:absolute;left:28px;top:84px" class="hl">Bank pusat <span class="am">dunia</span> pun beli</div></div>
      """ + pan('h-p', 'BANK PUSAT DUNIA &middot; BELIAN BERSIH', '9 BULAN PERTAMA') + """
        <div class="hb" id="h-b1" style="left:60px;height:150px;background:#3a4150"></div>
        <div class="hb" id="h-b2" style="left:250px;height:160px;background:linear-gradient(180deg,#FFD166,#FFB000)"></div>
        <div class="hx" style="left:40px">TAHUN LEPAS</div><div class="hx" style="left:236px">2026</div>
        <div id="h-v" style="position:absolute;left:236px;top:58px;font:700 52px 'Source Code Pro',monospace;color:#FFB000"><span id="h-n">0</span> T</div>
        <div id="h-u" style="position:absolute;left:470px;top:90px"><div class="num up" style="font-size:120px">+6%</div>
          <div class="md" style="font-size:34px">berbanding tempoh sama tahun lepas</div></div>
        <div id="h-s" style="position:absolute;left:470px;top:90px;width:470px;font:700 46px/1.15 'Outfit',sans-serif;color:#6EE7F9">Peranan strategik dalam sistem kewangan global</div>
        <div class="src">Sumber: World Gold Council</div></div>"""
    css = CSS + """
    .hb { position: absolute; bottom: 70px; width: 150px; border-radius: 8px 8px 0 0; transform-origin: 50% 100%; }
    .hx { position: absolute; bottom: 24px; width: 190px; text-align: center; font: 600 28px 'Source Code Pro', monospace; color: #8b94a3; }"""
    js = (wipe_in('#h-d', 0.1) + blur_out('#h-d', c(35) - t0 - 0.6) +
          f"    tl.fromTo('#h-p', {{opacity: 0, y: 80}}, {{opacity: 1, y: 0, duration: .6, ease: 'expo.out'}}, {c(35) - t0 - 0.2:.3f});\n"
          "    tl.set(['#h-v','#h-u','#h-s'], {opacity: 0}, 0);\n    tl.set(['#h-b1','#h-b2'], {scaleY: 0}, 0);\n"
          f"    tl.to('#h-b2', {{scaleY: 1, duration: .8, ease: 'power3.out'}}, {T.t(36, '675') - t0 - 0.4:.3f});\n"
          + blur_in('#h-v', T.t(36, '675') - t0 - 0.3) + count('#h-n', 0, 675, T.t(36, '675') - t0 - 0.3, 1.0)
          + f"    tl.to('#h-b1', {{scaleY: 1, duration: .7, ease: 'power3.out'}}, {T.t(38, 'meningkat') - t0 - 0.2:.3f});\n"
          + blur_in('#h-u', T.t(38, '6%') - t0 - 0.2) + swap('#h-u', '#h-s', T.t(40, 'strategik') - t0 - 0.3))
    S.append(('sh', t0, t1 - t0, scene('sh', css, html, js)))

    # S8 FULL: gold can still fall (3 drivers) --------------------------------------------------------
    t0, t1 = c(42) - 0.15, c(46) - 0.15
    html = deck('i-d', 'RISIKO', 'XAU') + """
      <div id="i-a" style="position:absolute;left:28px;top:70px;font-size:56px;white-space:nowrap" class="hl">Harga emas <span class="dn">masih boleh turun</span></div>
      <div id="i-c1" class="ch" style="left:28px">Kadar faedah</div><div id="i-c2" class="ch" style="left:298px">Kekuatan USD</div>
      <div id="i-c3" class="ch" style="left:576px">Sentimen pasaran</div></div>"""
    css = CSS + """
    .ch { position: absolute; top: 170px; padding: 12px 20px; border-radius: 10px; border: 2px solid #FF5A5F; color: #F5F5F0; white-space: nowrap;
          font: 600 36px 'Outfit', sans-serif; background: rgba(255,90,95,.08); }"""
    js = (wipe_in('#i-d', 0.1) + "    tl.set(['#i-a','#i-c1','#i-c2','#i-c3'], {opacity: 0}, 0);\n" + blur_in('#i-a', T.t(44, 'harga') - t0 - 0.2))
    for i, (cu, w) in enumerate([(44, 'kadar'), (44, 'kekuatan'), (45, 'sentimen')], 1):
        js += pop_in(f'#i-c{i}', T.t(cu, w) - t0 - 0.1, 0.4)
    js += blur_out('#i-d', t1 - t0 - 0.3)
    S.append(('si', t0, t1 - t0, scene('si', css, html, js)))

    # S9 FULL: the lesson -- price today vs long-term function; China vs family ------------------------
    t0, t1 = c(46) - 0.15, c(51) - 0.15
    html = deck('j-d', 'PENGAJARAN') + """
      <div id="j-a" style="position:absolute;left:28px;top:70px;width:920px"><div class="md"><s style="text-decoration-color:#FF5A5F">Harga hari ini</s></div>
        <div class="hl">Fungsi emas <span class="am">jangka panjang</span></div></div>
      <div id="j-b" style="position:absolute;left:28px;top:66px;width:920px">
        <div class="rw"><span class="cy">CHINA</span>&rarr; strategi urus <b class="am">rizab negara</b></div>
        <div class="rw"><span class="cy">KITA</span>&rarr; strategi urus <b class="am">kewangan keluarga</b></div></div></div>"""
    css = CSS + """
    .rw { display: flex; gap: 18px; align-items: baseline; height: 96px; border-bottom: 1px solid rgba(255,176,0,.25);
          font: 600 46px 'Outfit', sans-serif; color: #F5F5F0; }
    .rw .cy { font: 700 34px 'Source Code Pro', monospace; width: 150px; }"""
    js = (wipe_in('#j-d', 0.1) + "    tl.set(['#j-a','#j-b'], {opacity: 0}, 0);\n" + blur_in('#j-a', T.t(47, 'jangan') - t0)
          + swap('#j-a', '#j-b', T.cue(49) - t0) + blur_out('#j-d', t1 - t0 - 0.3))
    S.append(('sj', t0, t1 - t0, scene('sj', css, html, js)))

    # S10 FULL: three don'ts -> keep gold with knowledge, goal, ability -----------------------------------
    t0, t1 = c(51) - 0.15, c(62) - 0.15
    html = deck('k-d', 'PERATURAN SIMPAN EMAS') + """
      <div id="k-x">
        <div id="k-1" class="xr" style="top:62px"><b>&#10005;</b>Beli kerana ikut-ikutan</div>
        <div id="k-2" class="xr" style="top:132px"><b>&#10005;</b>Jual semata-mata kerana panik</div>
        <div id="k-3" class="xr" style="top:202px"><b>&#10005;</b>Guna duit kecemasan</div></div>
      <div id="k-y" style="position:absolute;left:28px;top:70px;width:920px"><div class="md">Simpan emas dengan</div>
        <div style="display:flex;gap:16px;margin-top:12px"><div id="k-a" class="pl">ILMU</div><div id="k-b" class="pl">MATLAMAT</div><div id="k-c" class="pl">KEMAMPUAN</div></div></div></div>"""
    css = CSS + """
    .xr { position: absolute; left: 28px; width: 920px; height: 62px; display: flex; align-items: center; gap: 18px;
          border-bottom: 1px solid rgba(255,90,95,.3); font: 600 40px 'Outfit', sans-serif; color: #F5F5F0; }
    .xr b { color: #FF5A5F; font-size: 40px; }
    .pl { padding: 14px 26px; border-radius: 12px; background: #FFB000; color: #0a0c10; font: 800 46px 'Outfit', sans-serif; }"""
    js = (wipe_in('#k-d', 0.1) + "    tl.set(['#k-1','#k-2','#k-3','#k-y','#k-a','#k-b','#k-c'], {opacity: 0}, 0);\n")
    for i, (cu, w) in enumerate([(51, 'ikut-ikutan'), (52, 'panik'), (53, 'kecemasan')], 1):
        js += f"    tl.fromTo('#k-{i}', {{opacity: 0, x: -40}}, {{opacity: 1, x: 0, duration: .4, ease: 'expo.out'}}, {T.t(cu, w) - t0 - 0.4:.3f});\n"
    js += (f"    tl.to('#k-x', {{opacity: 0, filter: 'blur(8px)', duration: .25}}, {c(54) - t0 - 0.35:.3f});\n"
           f"    tl.to('#k-y', {{opacity: 1, duration: .2}}, {c(54) - t0 - 0.1:.3f});\n")
    for k, (cu, w) in zip('abc', [(54, 'ilmu'), (55, 'matlamat'), (56, 'kemampuan')]):
        js += pop_in(f'#k-{k}', T.t(cu, w) - t0 - 0.15, 0.4)
    js += blur_out('#k-d', t1 - t0 - 0.3)
    S.append(('sk', t0, t1 - t0, scene('sk', css, html, js)))

    # S11 SPLIT CTA ----------------------------------------------------------------------------------
    t0, t1 = c(62) - 0.15, total
    split.append((c(62) - 0.4, total + 1))
    html = pan('l-p', 'SIMPANAN EMAS KONSISTEN', 'PUBLIC GOLD') + """
        <div id="l-h" style="position:absolute;left:30px;top:70px;width:900px" class="hl">Belajar bina simpanan emas <span class="am">secara konsisten</span></div>
        <div id="l-b" style="position:absolute;left:30px;top:230px;width:900px;height:96px;border-radius:14px;background:#14181f;border:1px solid rgba(255,176,0,.4)">
          <div style="position:absolute;left:16px;top:12px;width:72px;height:72px;border-radius:50%;background:#000;display:flex;align-items:center;justify-content:center"><img src="assets/logo_white.png" style="width:62px"></div>
          <div style="position:absolute;left:108px;top:24px;font:700 42px 'Outfit',sans-serif;color:#F5F5F0">Azlan &amp; Eza</div>
          <div id="l-f" style="position:absolute;right:14px;top:12px;width:220px;height:72px;border-radius:12px;background:#FFB000;color:#0a0c10;font:800 38px/72px 'Outfit',sans-serif;text-align:center">Follow</div></div></div>"""
    fo = T.t(63, 'follow') - t0
    js = ("    tl.set('#l-p', {opacity: 1}, 0);\n    tl.set(['#l-h','#l-b'], {opacity: 0}, 0);\n" + blur_in('#l-h', 0.5)
          + f"    tl.fromTo('#l-b', {{opacity: 0, y: 40}}, {{opacity: 1, y: 0, duration: .5, ease: 'expo.out'}}, {fo - 1.0:.3f});\n"
          f"    tl.to('#l-f', {{scale: .9, duration: .08}}, {fo:.3f});\n"
          f"    tl.to('#l-f', {{scale: 1, background: '#3DDC84', duration: .25, ease: 'back.out(3)'}}, {fo + 0.08:.3f});\n"
          f"    tl.set('#l-f', {{textContent: 'Following'}}, {fo + 0.1:.3f});\n")
    S.append(('sl', t0, t1 - t0, scene('sl', CSS, html, js)))
    return S, split


KEYWORDS = {'jatuh', 'china', '26', 'tan', 'sebulan', 'mengapa?', 'panik', 'rizab', 'strategi', 'fakta', 'world', 'gold', 'council',
            '6.3%', 'oktober', 'terbesar', '24', 'berturut-turut', '2,435', '5.3%', 'dolar', 'risiko', 'keuntungan', 'geopolitik',
            '675', '2026', '6%', 'strategik', 'turun', 'faedah', 'sentimen', 'jangka', 'panjang', 'keluarga', 'ikut-ikutan',
            'kecemasan', 'ilmu', 'matlamat', 'kemampuan', 'konsisten', 'public', 'follow'}


def caption_scene(words, total):
    groups, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        if (len(cur) >= 5 or nxt is None or nxt['cue'] != w['cue'] or w['w'][-1] in '.,?!' or nxt['os'] - w['oe'] > 0.25):
            groups.append(cur); cur = []
    html, js = [], []
    for gi, g in enumerate(groups):
        spans = ''.join(f"<span id='cw{gi}_{k}' class='{'kw' if w['w'].strip('.,?!').lower() in KEYWORDS else ''}'>{w['w']}</span>"
                        for k, w in enumerate(g))
        html.append(f"    <div id='cg{gi}' class='cg'><div class='cin'>{spans}</div></div>")
        a = max(0.0, g[0]['os'] - 0.08)
        b = min(g[-1]['oe'] + 0.35, groups[gi + 1][0]['os'] - 0.08 if gi + 1 < len(groups) else total)
        js.append(f"    tl.set('#cg{gi}', {{opacity: 1, visibility: 'visible'}}, {a:.3f});")
        js.append(f"    tl.fromTo('#cg{gi} .cin', {{opacity: 0, y: 10}}, {{opacity: 1, y: 0, duration: .2, ease: 'power2.out'}}, {a:.3f});")
        for k, w in enumerate(g):
            js.append(f"    tl.fromTo('#cw{gi}_{k}', {{opacity: .55}}, {{opacity: 1, duration: .12, immediateRender: false}}, {w['os']:.3f});")
        js.append(f"    tl.set('#cg{gi}', {{opacity: 0, visibility: 'hidden'}}, {b:.3f});")
    css = """
    #band { position: absolute; left: 0; right: 0; top: 1170px; height: 190px;
            background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,.55) 45%, rgba(0,0,0,.55) 70%, rgba(0,0,0,0) 100%); }
    .cg { position: absolute; left: 50px; width: 880px; top: 1226px; text-align: center; opacity: 0; visibility: hidden; }
    .cin { display: inline-block; font: 600 50px/1.22 'Outfit', sans-serif; color: #FFFFFF; letter-spacing: .2px;
           text-shadow: 0 2px 4px rgba(0,0,0,.6), 0 0 18px rgba(0,0,0,.35); }
    .cin span { display: inline-block; margin: 0 .16em; }
    .cin .kw { color: #FFB000; font-weight: 700; }"""
    return scene('captions', css, "    <div id='band'></div>\n" + '\n'.join(html), '\n'.join(js))


def outro_scene():
    css = """
    #o-bg { position: absolute; inset: 0; background: #07090c; }
    #o-bg::before { content: ''; position: absolute; inset: 0; background-image: linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px); background-size: 100% 6px; }
    #o-logo { position: absolute; left: 340px; top: 640px; width: 400px; }
    #o-l { position: absolute; left: 140px; top: 1040px; width: 800px; height: 4px; background: #FFB000; transform-origin: 0 50%; }
    #o-t { position: absolute; left: 0; width: 1080px; top: 1080px; text-align: center; font: 600 30px 'Source Code Pro', monospace; letter-spacing: 8px; color: #FFB000; }"""
    html = """<div id="o-bg"></div><img id="o-logo" src="assets/logo_white.png"><div id="o-l"></div><div id="o-t">AZLAN &amp; EZA</div>"""
    js = ("    tl.fromTo('#o-bg', {opacity: 0}, {opacity: 1, duration: .3}, 0);\n"
          "    tl.fromTo('#o-logo', {opacity: 0, scale: .9}, {opacity: 1, scale: 1, duration: .6, ease: 'expo.out'}, .25);\n"
          "    tl.fromTo('#o-l', {scaleX: 0}, {scaleX: 1, duration: .6, ease: 'power3.out'}, .5);\n"
          + blur_in('#o-t', .8) + f"    tl.to('#root', {{opacity: 0, duration: .45, ease: 'power2.in'}}, {OUTRO - 0.5:.2f});\n")
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
    os.makedirs(comp, exist_ok=True)
    for src in (('13', 'proj', 'assets', 'logo_white.png'), ('13', 'proj', 'assets', 'gsap.min.js'), ('18', 'img', 'wgc_chart.jpg')):
        shutil.copy(os.path.join(REPO, 'work', *src), a)
    for f in ('whoosh', 'whoosh-short', 'whoosh-cinematic', 'pop', 'click-soft', 'click', 'sparkle', 'impact-bass-1',
              'impact-bass-2', 'riser', 'ping', 'key-press', 'glitch-3', 'notification'):
        shutil.copy(os.path.join(SFX_DIR, f + '.mp3'), os.path.join(a, f'sfx-{f}.mp3'))
    dur = round(total + OUTRO, 3)
    # the documentary bed is 172 s: loop it with a 4 s crossfade to cover a ~4 min film
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', MUSIC_SRC, '-ss', '30', '-i', MUSIC_SRC, '-filter_complex',
                    '[0:a][1:a]acrossfade=d=4:c1=tri:c2=tri[m]', '-map', '[m]', '-t', str(dur + 1), '-c:a', 'aac', '-b:a', '192k',
                    os.path.join(a, 'music-bed.m4a')], check=True)
    scenes, split = build(T, total)
    merged = []
    for a0, b0 in split:
        if merged and a0 - merged[-1][1] < 1.0:
            merged[-1] = (merged[-1][0], b0)
        else:
            merged.append((a0, b0))
    split = merged
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
        pts += [{'t': round(max(0, a0 - 0.25), 3), 'v': 0.3 if a0 - t > 0.9 else 0.12}, {'t': round(a0, 3), 'v': 0.12}, {'t': round(b0, 3), 'v': 0.12}]
        t = b0
    pts += [{'t': round(total, 3), 'v': 0.12}, {'t': round(total + 0.6, 3), 'v': 0.45}]
    lane = []
    for p in sorted(pts, key=lambda p: p['t']):
        if lane and p['t'] - lane[-1]['t'] < 0.05:
            lane[-1] = p
        else:
            lane.append(p)

    c = T.cue
    sfx = [('glitch-3', 0.0, .3), ('impact-bass-1', T.t(1, '26') - 0.1, .5), ('ping', T.t(2, 'sebulan'), .3), ('pop', c(3), .45)]
    for i, d in enumerate([c(5), c(8), c(20), c(28), c(42), c(46), c(51)]):
        sfx.append((['whoosh-short', 'whoosh'][i % 2], d - 0.05, .35))
    for i, (a0, b0) in enumerate(split):
        sfx.append((['whoosh-cinematic', 'whoosh'][i % 2], a0 - 0.1, .5))
        if b0 < total:
            sfx.append(('whoosh-short', b0 - 0.05, .35))
    sfx += [('key-press', c(8) + 0.25, .35), ('key-press', c(8) + 0.6, .3), ('pop', T.t(12, '6.3%') - 0.3, .35),
            ('pop', T.t(14, '26') - 0.3, .4), ('ping', T.t(15, 'terbesar'), .3), ('riser', T.t(16, '24') - 2.0, .25),
            ('sparkle', T.t(16, '24') - 0.4, .35), ('impact-bass-2', T.t(18, '2,435') - 0.7, .4),
            ('pop', T.t(22, '26') - 0.3, .35), ('impact-bass-1', T.t(24, '5.3%') - 0.2, .35),
            ('click-soft', T.t(32, 'mempelbagaikan') - 0.2, .6), ('click-soft', T.t(32, 'mengurangkan') - 0.2, .6),
            ('click-soft', T.t(33, 'mengurus') - 0.2, .6), ('sparkle', T.t(36, '675') - 0.2, .35), ('ping', T.t(38, '6%') - 0.1, .3),
            ('pop', T.t(44, 'kadar'), .35), ('pop', T.t(44, 'kekuatan'), .35), ('pop', T.t(45, 'sentimen'), .35),
            ('click-soft', T.t(51, 'ikut-ikutan') - 0.4, .6), ('click-soft', T.t(52, 'panik') - 0.4, .6), ('click-soft', T.t(53, 'kecemasan') - 0.4, .6),
            ('pop', T.t(54, 'ilmu') - 0.15, .4), ('pop', T.t(55, 'matlamat') - 0.15, .4), ('pop', T.t(56, 'kemampuan') - 0.15, .45),
            ('click', T.t(63, 'follow'), .8), ('whoosh-cinematic', total - 0.1, .45)]
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

    cam = [f"    tl.set('#punch', {{scale: {s}}}, {t:.3f});" for t, s in
           [(0.0, 1.06), (c(2) - 0.03, 1.0), (c(3) - 0.03, 1.12), (c(5) - 0.03, 1.0), (c(8) - 0.03, 1.05), (c(9) - 0.03, 1.0),
            (c(20) - 0.03, 1.06), (c(22) - 0.03, 1.0), (c(25) - 0.03, 1.08), (c(26) - 0.03, 1.0), (c(29) - 0.03, 1.06),
            (c(30) - 0.03, 1.0), (c(42) - 0.03, 1.06), (c(44) - 0.03, 1.0), (c(46) - 0.03, 1.07), (c(47) - 0.03, 1.0),
            (c(54) - 0.03, 1.05), (c(55) - 0.03, 1.08), (c(56) - 0.03, 1.11), (c(62) - 0.03, 1.0)]]
    for a0, b0 in split:
        cam += [f"    tl.to('#cam', {{y: {SHIFT}, duration: .7, ease: 'power3.inOut'}}, {a0:.3f});",
                f"    tl.to('#camclip', {{'--b': '{H - (CUT - SHIFT)}px', duration: .7, ease: 'power3.inOut'}}, {a0:.3f});",
                f"    tl.to('#tbg', {{opacity: 1, duration: .5}}, {a0 + 0.1:.3f});",
                f"    tl.to('#cutline', {{opacity: 1, scaleX: 1, duration: .5, ease: 'power3.out'}}, {a0 + 0.4:.3f});"]
        if b0 < total:
            cam += [f"    tl.to('#cam', {{y: 0, duration: .6, ease: 'power3.inOut'}}, {b0:.3f});",
                    f"    tl.to('#camclip', {{'--b': '0px', duration: .6, ease: 'power3.inOut'}}, {b0:.3f});",
                    f"    tl.to('#cutline', {{opacity: 0, duration: .2}}, {b0:.3f});",
                    f"    tl.to('#tbg', {{opacity: 0, duration: .4}}, {b0 + 0.25:.3f});"]
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
    html, body {{ margin: 0; padding: 0; background: #07090c; }}
    #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: #07090c; }}
    #tbg {{ position: absolute; inset: 0; opacity: 0; z-index: 1; background: radial-gradient(90% 40% at 50% 70%, #151a22 0%, #07090c 70%); }}
    #tbg::after {{ content: ''; position: absolute; inset: 0; opacity: .6; background-image: linear-gradient(rgba(255,176,0,.06) 1px, transparent 1px),
               linear-gradient(90deg, rgba(255,176,0,.06) 1px, transparent 1px); background-size: 60px 60px; }}
    #cam {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; z-index: 5; }}
    #camclip {{ position: absolute; inset: 0; --b: 0px; clip-path: inset(0px 0px var(--b) 0px); overflow: hidden; }}
    #punch {{ position: absolute; inset: 0; transform-origin: 520px 860px; }}
    #base {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
    #cutline {{ position: absolute; left: 0; right: 0; top: {CUT - 2}px; height: 4px; z-index: 6; opacity: 0; transform-origin: 0 50%;
               background: linear-gradient(90deg, #FFB000, #6EE7F9); box-shadow: 0 0 18px rgba(255,176,0,.6); }}
    #capwrap {{ position: absolute; inset: 0; z-index: 30; }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="{W}" data-height="{H}">
    <div id="tbg"></div>
    <div id="cam"><div id="camclip"><div id="punch">
      <video id="base" class="clip" src="assets/base.mp4" data-start="0" data-duration="{total:.3f}" data-track-index="0"
             data-has-audio="true" data-volume="1" playsinline></video>
    </div></div></div>
    <div id="cutline"></div>
{chr(10).join(hosts)}
    <div id="capwrap"><div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0"
         data-duration="{total:.3f}" data-track-index="4" data-track-kind="captions" data-width="{W}" data-height="{H}"></div></div>
    <div id="outro" data-composition-id="outro" data-composition-src="compositions/outro.html" data-start="{total:.3f}"
         data-duration="{OUTRO}" data-track-index="5" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index: 40"></div>
    <audio id="music" class="clip" src="assets/music-bed.m4a" data-start="0" data-duration="{dur}" data-track-index="8"
           data-volume="1" data-fade-in="0.4" data-fade-out="1.5" data-automation="{lane_json}"></audio>
{chr(10).join(tags)}
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.set('#cutline', {{scaleX: 0}}, 0);
{chr(10).join(cam)}
    tl.set({{}}, {{}}, {dur});
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
"""
    open(os.path.join(proj, 'index.html'), 'w').write(index)
    return scenes, split
