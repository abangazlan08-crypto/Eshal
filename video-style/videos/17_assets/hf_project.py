"""HyperFrames project for video 17 (harga emas RM515 segram). Look: "Crimson Newsroom" (new, unlike videos 1-16).

Gold-price news desk: crimson + deep wine panels, white type, gold numbers; League Gothic (condensed display), Lato (body),
JetBrains Mono (labels / tickers).
  * FULL     - talking head fills the frame; a crimson news deck sits on the wall above the head (y 175-500).
  * TAKEOVER - the frame becomes a wine studio desk, the camera shrinks into a "LIVE" box top-left (face whole),
               a headline sits beside it and the chart takes y 560-1200. Captions stay at y ~1236.
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
MUSIC_SRC = os.path.join(REPO, 'work', '15', 'proj', 'assets', 'music-bed.m4a')   # video 6's approved documentary track (from 8 s)
MUSIC_SS = 20.0
FACE_X, FACE_Y, SCALE = 518, 900, 0.56
BOX = dict(x=60, y=190, w=440, h=330)

CSS = """
    .deck { position: absolute; left: 50px; top: 176px; width: 980px; height: 320px; border-radius: 22px; overflow: hidden;
            background: linear-gradient(135deg, #9B1B30 0%, #6A0F1F 100%); box-shadow: 0 24px 60px rgba(40,0,8,.35); }
    .deck::after { content: ''; position: absolute; left: 0; right: 0; bottom: 0; height: 8px; background: linear-gradient(90deg, #F5C451, #C8902A); }
    .tag { position: absolute; left: 34px; top: 26px; display: flex; gap: 12px; align-items: center; font: 700 28px 'JetBrains Mono', monospace; letter-spacing: 3px; color: #FFE7A8; }
    .tag b { padding: 4px 12px; border-radius: 6px; background: #F5C451; color: #5E0B18; }
    .hd { font: 400 110px/0.95 'League Gothic', sans-serif; color: #fff; text-transform: uppercase; letter-spacing: 1px; }
    .bd { font: 900 44px/1.15 'Lato', sans-serif; color: #fff; }
    .au { color: #F5C451; } .wn { color: #9B1B30; }
    .studio { position: absolute; left: 50px; top: 545px; width: 980px; height: 670px; border-radius: 26px; overflow: hidden;
              background: rgba(255,255,255,.96); box-shadow: 0 30px 70px rgba(0,0,0,.35); }
    .studio::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 10px; background: #9B1B30; }
    .lbl { font: 700 28px 'JetBrains Mono', monospace; letter-spacing: 3px; color: #9B1B30; }
    .ink { font: 900 44px/1.15 'Lato', sans-serif; color: #1c1214; }
    .side { position: absolute; left: 530px; top: 200px; width: 480px; }
"""


def deck_in(sel, t):
    return (f"    tl.fromTo('{sel}', {{opacity: 0, clipPath: 'inset(0 100% 0 0)'}}, {{opacity: 1, clipPath: 'inset(0 0% 0 0)', duration: .55, ease: 'power3.out'}}, {t:.3f});\n")


def swap(a, b, t):
    return blur_out(a, t - 0.22, 0.2) + blur_in(b, t, 0.4, 18) + f"    tl.set('{b}', {{opacity: 0}}, 0);\n"


def build(T, total):
    S, take = [], []
    c = T.cue

    # S0 HOOK: price slot rolls and lands on RM515 / gram ---------------------------------------
    t0, t1 = 0.0, c(3) - 0.15
    html = """<div id="a-d" class="deck"><div class="tag"><b>TERKINI</b> HARGA EMAS HARI INI</div>
      <div style="position:absolute;left:34px;top:84px;display:flex;align-items:flex-end;gap:10px">
        <div style="font:400 200px/0.9 'League Gothic',sans-serif;color:#fff">RM</div>
        <div style="position:relative;height:190px;width:300px"><div id="a-roll" style="position:absolute;left:0;top:0;font:400 200px/190px 'League Gothic',sans-serif;color:#F5C451">???</div></div>
        <div style="font:900 50px 'Lato',sans-serif;color:#FFE7A8;margin-bottom:22px">/ gram</div></div>
      <div id="a-al" style="position:absolute;right:34px;top:30px;font:italic 900 40px 'Lato',sans-serif;color:#FFE7A8">Alhamdulillah</div></div>"""
    land = T.t(2, 'RM515') - t0
    js = ("    tl.set('#a-d', {opacity: 1}, 0);\n"
          "    document.getElementById('a-roll').textContent = '???';\n"
          "    const cu = {v: 0};\n"
          f"    tl.call(() => {{}}, null, 0);\n"
          f"    tl.to(cu, {{v: 515, duration: .8, ease: 'power3.out', onUpdate: () => {{ document.getElementById('a-roll').textContent = Math.round(cu.v); }}}}, {land - 0.85:.3f});\n"
          f"    tl.set('#a-roll', {{textContent: '515'}}, {land:.3f});\n"
          f"    tl.fromTo('#a-roll', {{scale: 1.15, transformOrigin: '0 50%'}}, {{scale: 1, duration: .3, ease: 'back.out(3)', immediateRender: false}}, {land:.3f});\n"
          + blur_out('#a-d', t1 - t0 - 0.3))
    S.append(('sa', t0, t1 - t0, scene('sa', CSS, html, js)))

    # S1 TAKEOVER: last time at this level -- the real 1 Sep 2025 G100 poster + comparison bars ----
    t0, t1 = c(3) - 0.15, c(5) - 0.2
    take.append((c(3) - 0.15, c(5) - 0.35))
    html = """<div class="side"><div class="lbl" style="color:#F5C451">KALI TERAKHIR</div><div class="hd" style="color:#fff;font-size:96px">DI PARAS INI</div></div>
      <div class="studio"></div>
      <div id="b-p" style="position:absolute;left:84px;top:585px;width:470px;height:470px;border-radius:18px;overflow:hidden;box-shadow:0 20px 40px rgba(0,0,0,.35)">
        <img src="assets/poster.jpg" style="width:470px;height:470px"></div>
      <div id="b-st" style="position:absolute;left:96px;top:1075px;padding:8px 16px;border-radius:8px;background:#9B1B30;color:#fff;font:700 28px 'JetBrains Mono',monospace">1 SEP 2025 &middot; RM514 = 1 g</div>
      <div style="position:absolute;left:600px;top:590px;width:330px" class="lbl">HARGA / GRAM</div>
      <div class="cb" id="b-c1" style="left:615px"><div class="cv">RM514</div></div>
      <div class="cb" id="b-c2" style="left:785px;background:linear-gradient(180deg,#F5C451,#C8902A)"><div class="cv">RM515</div></div>
      <div class="cl" style="left:580px">1 SEP 2025</div><div class="cl" style="left:750px">HARI INI</div>
      <div id="b-ln" style="position:absolute;left:600px;top:676px;width:330px;border-top:4px dashed #9B1B30"></div>
      <div id="b-ys" style="position:absolute;left:600px;top:1112px;width:330px;text-align:center;padding:6px 0;border-radius:8px;background:#1c1214;color:#F5C451;font:700 28px 'JetBrains Mono',monospace">&larr; LEBIH SETAHUN &rarr;</div>"""
    css = CSS + """
    .cb { position: absolute; top: 680px; width: 130px; height: 360px; border-radius: 12px 12px 0 0; background: #c9b3b7; transform-origin: 50% 100%; }
    .cv { position: absolute; left: -10px; right: -10px; top: -56px; text-align: center; font: 400 52px 'League Gothic', sans-serif; color: #1c1214; }
    .cl { position: absolute; top: 1050px; width: 200px; text-align: center; font: 700 28px 'JetBrains Mono', monospace; color: #1c1214; }"""
    sp = T.t(3, 'September') - t0
    js = ("    tl.set(['#b-p','#b-st','#b-ln','#b-ys'], {opacity: 0}, 0);\n    tl.set(['#b-c1','#b-c2'], {scaleY: 0}, 0);\n"
          f"    tl.fromTo('#b-p', {{opacity: 0, rotation: -8, y: 80}}, {{opacity: 1, rotation: -2, y: 0, duration: .7, ease: 'expo.out'}}, 0.55);\n"
          f"    tl.fromTo('#b-st', {{opacity: 0, scale: 1.8, rotation: -10}}, {{opacity: 1, scale: 1, rotation: -3, duration: .3, ease: 'power4.in'}}, {sp:.3f});\n"
          f"    tl.to('#b-c1', {{scaleY: 1, duration: .6, ease: 'power3.out'}}, {sp + 0.3:.3f});\n"
          f"    tl.to('#b-c2', {{scaleY: 1.003, duration: .6, ease: 'power3.out'}}, {sp + 0.6:.3f});\n"
          f"    tl.fromTo('#b-ln', {{opacity: 1, clipPath: 'inset(0 100% 0 0)'}}, {{clipPath: 'inset(0 0% 0 0)', duration: .5}}, {sp + 1.3:.3f});\n"
          + blur_in('#b-ys', T.t(4, 'setahun') - t0 - 0.2))
    S.append(('sb', t0, t1 - t0, scene('sb', css, html, js)))

    # S2 one gram today, no big budget -----------------------------------------------------------
    t0, t1 = c(5) - 0.2, c(7) - 0.15
    html = """<div id="c-d" class="deck"><div class="tag"><b>PERIBADI</b> SAYA SANGAT HAPPY</div>
      <div id="c-a" style="position:absolute;left:34px;top:86px" class="hd">BELI <span class="au">SEGRAM</span> HARI INI</div>
      <div id="c-b" style="position:absolute;left:34px;top:200px" class="bd">tak perlukan <span class="au">bajet yang besar</span></div>
      <div id="c-g" style="position:absolute;right:40px;top:70px;width:170px;height:170px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#FFF1C2,#F5C451 45%,#B87B1C);
           display:flex;align-items:center;justify-content:center;font:400 72px 'League Gothic',sans-serif;color:#5E0B18;box-shadow:0 10px 30px rgba(0,0,0,.35)">1 g</div></div>"""
    js = (deck_in('#c-d', 0.1) + "    tl.set(['#c-a','#c-b','#c-g'], {opacity: 0}, 0);\n" + blur_in('#c-a', T.t(5, 'segram') - t0 - 0.3)
          + f"    tl.fromTo('#c-g', {{opacity: 0, rotationY: 90}}, {{opacity: 1, rotationY: 0, duration: .6, ease: 'back.out(1.6)'}}, {T.t(5, 'segram') - t0:.3f});\n"
          + blur_in('#c-b', T.t(6, 'bajet') - t0 - 0.3) + blur_out('#c-d', t1 - t0 - 0.3))
    S.append(('sc', t0, t1 - t0, scene('sc', CSS, html, js)))

    # S3 "harga emas pasti akan melonjak lagi" (her view) ---------------------------------------
    t0, t1 = c(7) - 0.15, c(8) - 0.15
    html = """<div id="d-d" class="deck"><div class="tag"><b>MASA AKAN DATANG</b></div>
      <svg viewBox="0 0 460 230" style="position:absolute;left:600px;top:80px;width:360px;height:200px">
        <polyline points="0,200 80,170 140,185 210,120" fill="none" stroke="#fff" stroke-width="8" stroke-linejoin="round"/>
        <polyline id="d-f" points="210,120 300,80 380,40 450,10" fill="none" stroke="#F5C451" stroke-width="8" stroke-dasharray="18 12" stroke-linejoin="round"/>
        <polygon id="d-ah" points="450,10 420,12 438,38" fill="#F5C451"/></svg>
      <div id="d-a" style="position:absolute;left:34px;top:84px;width:560px;font-size:86px" class="hd">HARGA EMAS<br><span class="au">AKAN MELONJAK</span> LAGI</div></div>"""
    mj = T.t(7, 'melonjak') - t0
    js = (deck_in('#d-d', 0.1) + "    tl.set(['#d-a','#d-ah'], {opacity: 0}, 0);\n" + blur_in('#d-a', T.t(7, 'harga') - t0 - 0.2)
          + f"    tl.fromTo('#d-f', {{clipPath: 'inset(0 100% 0 0)'}}, {{clipPath: 'inset(0 0% 0 0)', duration: .8, ease: 'power2.out'}}, {mj - 0.2:.3f});\n"
          + f"    tl.to('#d-ah', {{opacity: 1, duration: .15}}, {mj + 0.5:.3f});\n" + blur_out('#d-d', t1 - t0 - 0.3))
    S.append(('sd', t0, t1 - t0, scene('sd', CSS, html, js)))

    # S4 TAKEOVER: target 1 kilogram, rich in gold = many grams ------------------------------------
    t0, t1 = c(8) - 0.15, c(10) - 0.2
    take.append((c(8) - 0.15, c(10) - 0.35))
    R = 210
    circ = 2 * 3.14159 * R
    stacks = ''.join(f"<div class='gs' id='e-s{i}' style='left:{600 + (i % 4) * 82}px;top:{1090 - (i // 4) * 46}px'>1 g</div>" for i in range(16))
    html = f"""<div class="side"><div class="lbl" style="color:#F5C451">SEKARANG</div><div class="hd" style="color:#fff;font-size:96px">TARGET DULU</div></div>
      <div class="studio"></div>
      <svg viewBox="0 0 520 520" style="position:absolute;left:84px;top:600px;width:500px;height:500px">
        <circle cx="260" cy="260" r="{R}" fill="none" stroke="#efe3e5" stroke-width="44"/>
        <circle id="e-r" cx="260" cy="260" r="{R}" fill="none" stroke="#F5C451" stroke-width="44" stroke-linecap="round" stroke-dasharray="0 {circ:.0f}" transform="rotate(-90 260 260)"/>
        <text x="260" y="250" text-anchor="middle" font-family="League Gothic" font-size="130" fill="#9B1B30">1 KG</text>
        <text x="260" y="310" text-anchor="middle" font-family="JetBrains Mono" font-weight="700" font-size="30" fill="#1c1214">= 1,000 GRAM</text></svg>
      <div id="e-q" style="position:absolute;left:600px;top:610px;width:330px" class="ink">Orang yang <span style="color:#9B1B30">kaya dengan emas</span> =</div>
      <div id="e-q2" style="position:absolute;left:600px;top:760px;width:330px;font:400 72px/1 'League Gothic',sans-serif;color:#C8902A">BANYAK GRAM EMAS</div>
      {stacks}"""
    css = CSS + """
    .gs { position: absolute; width: 74px; height: 40px; border-radius: 6px; background: linear-gradient(180deg, #FFE7A8, #E0A93C);
          box-shadow: inset 0 -4px 0 rgba(120,70,0,.35); font: 700 26px/40px 'JetBrains Mono', monospace; color: #5E0B18; text-align: center; }"""
    kg = T.t(8, 'kilogram') - t0
    js = ("    tl.set(['#e-q','#e-q2','.gs'], {opacity: 0}, 0);\n"
          f"    tl.to('#e-r', {{attr: {{'stroke-dasharray': '{circ:.0f} {circ:.0f}'}}, duration: 1.6, ease: 'power2.inOut'}}, {kg - 0.6:.3f});\n"
          + blur_in('#e-q', T.t(9, 'kaya') - t0 - 0.3) + blur_in('#e-q2', T.t(9, 'banyak') - t0 - 0.2))
    for i in range(16):
        js += f"    tl.fromTo('#e-s{i}', {{opacity: 0, y: -60}}, {{opacity: 1, y: 0, duration: .3, ease: 'bounce.out'}}, {T.t(9, 'banyak') - t0 + i * 0.07:.3f});\n"
    S.append(('se', t0, t1 - t0, scene('se', css, html, js)))

    # S5 to Eza & Azlan's savers: buy many grams while the price is good ---------------------------
    t0, t1 = c(10) - 0.2, c(13) - 0.2
    html = """<div id="f-d" class="deck"><div class="tag"><b>PENYIMPAN EMAS</b> EZA &amp; AZLAN</div>
      <div id="f-a" style="position:absolute;left:34px;top:86px;width:600px" class="hd">HARGA <span class="au">CANTIK</span> SEKARANG</div>
      <div id="f-b" style="position:absolute;left:34px;top:208px" class="bd">beli gram <span class="au">banyak-banyak</span> ya</div>
      <img id="f-g1" src="assets/goldbar_100g.png" style="position:absolute;left:700px;top:50px;width:120px">
      <img id="f-g2" src="assets/goldbar_100g.png" style="position:absolute;left:800px;top:70px;width:120px">
      <img id="f-g3" src="assets/goldbar_100g.png" style="position:absolute;left:750px;top:110px;width:120px"></div>"""
    bb = T.t(11, 'banyak') - t0
    js = (deck_in('#f-d', 0.1) + "    tl.set(['#f-a','#f-b','#f-g1','#f-g2','#f-g3'], {opacity: 0}, 0);\n" + blur_in('#f-a', T.t(10, 'cantik') - t0 - 0.3)
          + blur_in('#f-b', T.t(11, 'gram') - t0 - 0.2))
    for i in range(3):
        js += f"    tl.fromTo('#f-g{i + 1}', {{opacity: 0, y: -140, rotation: {-20 + i * 15}}}, {{opacity: 1, y: 0, rotation: {-8 + i * 8}, duration: .5, ease: 'bounce.out'}}, {bb + i * 0.18:.3f});\n"
    js += blur_out('#f-d', t1 - t0 - 0.3)
    S.append(('sf', t0, t1 - t0, scene('sf', CSS, html, js)))

    # S6 TAKEOVER CTA: lucky draw coming soon --------------------------------------------------------
    t0, t1 = c(13) - 0.2, total
    take.append((c(13) - 0.2, total + 1))
    html = """<div class="side"><div class="lbl" style="color:#F5C451">KAMI AKAN UMUMKAN</div><div class="hd" style="color:#fff;font-size:96px">LUCKY DRAW</div></div>
      <div class="studio"></div>
      <div id="g-t" style="position:absolute;left:110px;top:610px;width:820px;height:330px;border-radius:26px;overflow:hidden;
           background:linear-gradient(135deg,#9B1B30,#5E0B18);box-shadow:0 24px 50px rgba(94,11,24,.45)">
        <div style="position:absolute;left:600px;top:-20px;bottom:-20px;width:0;border-left:6px dashed rgba(255,231,168,.6)"></div>
        <div style="position:absolute;left:40px;top:34px;font:700 28px 'JetBrains Mono',monospace;letter-spacing:4px;color:#FFE7A8">KHAS UNTUK</div>
        <div style="position:absolute;left:40px;top:80px;font:400 104px/0.95 'League Gothic',sans-serif;color:#fff">PENYIMPAN EMAS<br><span style="color:#F5C451">EZA &amp; AZLAN</span></div>
        <div style="position:absolute;left:640px;top:70px;width:150px;height:190px;display:flex;align-items:center;justify-content:center">
          <img src="assets/logo_white.png" style="width:150px"></div>
        <div id="g-sh" style="position:absolute;inset:0;background:linear-gradient(105deg,transparent 38%,rgba(255,240,200,.45) 50%,transparent 62%);background-size:300% 100%;background-position:120% 0"></div></div>
      <div id="g-s" style="position:absolute;left:330px;top:990px;padding:14px 34px;border:6px solid #9B1B30;border-radius:14px;color:#9B1B30;
           font:400 76px/1 'League Gothic',sans-serif;letter-spacing:3px;background:#fff">TAK LAMA LAGI</div>"""
    js = ("    tl.set(['#g-t','#g-s'], {opacity: 0}, 0);\n"
          f"    tl.fromTo('#g-t', {{opacity: 0, rotationX: 70, y: 60, transformPerspective: 1200}}, {{opacity: 1, rotationX: 0, y: 0, duration: .8, ease: 'expo.out'}}, {T.t(13, 'lucky') - t0 - 0.3:.3f});\n"
          f"    tl.fromTo('#g-sh', {{backgroundPosition: '120% 0'}}, {{backgroundPosition: '-60% 0', duration: 1.1, ease: 'power2.inOut'}}, {T.t(13, 'penyimpan') - t0:.3f});\n"
          f"    tl.fromTo('#g-s', {{opacity: 0, scale: 2, rotation: -14}}, {{opacity: 1, scale: 1, rotation: -5, duration: .3, ease: 'power4.in'}}, {T.t(14, 'Eza') - t0 - 0.1:.3f});\n")
    S.append(('sg', t0, t1 - t0, scene('sg', CSS, html, js)))
    return S, take


KEYWORDS = {'alhamdulillah', 'emas', 'rm515', 'gram', 'september', '2025', 'setahun', 'happy', 'segram', 'bajet', 'melonjak',
            'target', 'kilogram', 'kaya', 'banyak', 'cantik', 'banyak-banyak', 'lucky', 'draw', 'eza', 'azlan'}


def caption_scene(words, total):
    groups, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        if (len(cur) >= 4 or nxt is None or nxt['cue'] != w['cue'] or w['w'][-1] in '.,?!' or nxt['os'] - w['oe'] > 0.25):
            groups.append(cur); cur = []
    html, js = [], []
    for gi, g in enumerate(groups):
        spans = ''.join(f"<span id='cw{gi}_{k}' class='{'kw' if w['w'].strip('.,?!').lower() in KEYWORDS else ''}'>{w['w']}</span>"
                        for k, w in enumerate(g))
        html.append(f"    <div id='cg{gi}' class='cg'><div class='cin'>{spans}</div></div>")
        a = max(0.0, g[0]['os'] - 0.08)
        b = min(g[-1]['oe'] + 0.35, groups[gi + 1][0]['os'] - 0.08 if gi + 1 < len(groups) else total)
        js.append(f"    tl.set('#cg{gi}', {{opacity: 1, visibility: 'visible'}}, {a:.3f});")
        js.append(f"    tl.fromTo('#cg{gi} .cin', {{clipPath: 'inset(0 100% 0 0)'}}, {{clipPath: 'inset(0 0% 0 0)', duration: .18, ease: 'power3.out'}}, {a:.3f});")
        for k, w in enumerate(g):
            js.append(f"    tl.set('#cw{gi}_{k}', {{borderBottomColor: '#F5C451'}}, {w['os']:.3f});")
            if k < len(g) - 1:
                js.append(f"    tl.set('#cw{gi}_{k}', {{borderBottomColor: 'rgba(0,0,0,0)'}}, {g[k + 1]['os']:.3f});")
        js.append(f"    tl.set('#cg{gi}', {{opacity: 0, visibility: 'hidden'}}, {b:.3f});")
    css = """
    .cg { position: absolute; left: 40px; width: 900px; top: 1236px; text-align: center; opacity: 0; visibility: hidden; }
    .cin { display: inline-block; padding: 8px 18px 10px; border-radius: 8px; background: rgba(28,10,14,.82); border-left: 8px solid #9B1B30;
           font: 900 48px/1.2 'Lato', sans-serif; color: #FFFFFF; }
    .cin span { display: inline-block; margin: 0 .18em; border-bottom: 5px solid rgba(0,0,0,0); }
    .cin .kw { color: #F5C451; }"""
    return scene('captions', css, '\n'.join(html), '\n'.join(js))


def outro_scene():
    css = """
    #o-bg { position: absolute; inset: 0; background: linear-gradient(160deg, #9B1B30 0%, #5E0B18 70%, #3a0610 100%); }
    #o-bar { position: absolute; left: 0; right: 0; top: 1080px; height: 10px; background: linear-gradient(90deg, #F5C451, #C8902A); transform-origin: 0 50%; }
    #o-logo { position: absolute; left: 330px; top: 640px; width: 420px; }
    #o-t { position: absolute; left: 0; width: 1080px; top: 1120px; text-align: center; font: 700 30px 'JetBrains Mono', monospace; letter-spacing: 8px; color: #F5C451; }"""
    html = """<div id="o-bg"></div><img id="o-logo" src="assets/logo_white.png"><div id="o-bar"></div><div id="o-t">AZLAN &amp; EZA</div>"""
    js = ("    tl.fromTo('#o-bg', {opacity: 0}, {opacity: 1, duration: .35}, 0);\n"
          "    tl.fromTo('#o-logo', {opacity: 0, scale: .85}, {opacity: 1, scale: 1, duration: .6, ease: 'expo.out'}, .25);\n"
          "    tl.fromTo('#o-bar', {scaleX: 0}, {scaleX: 1, duration: .6, ease: 'power3.out'}, .5);\n"
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
    for src in (('13', 'proj', 'assets', 'logo_white.png'), ('13', 'proj', 'assets', 'logo.png'), ('13', 'proj', 'assets', 'gsap.min.js'),
                ('13', 'gold', 'goldbar_100g.png')):
        shutil.copy(os.path.join(REPO, 'work', *src), a)
    shutil.copy(os.path.join(REPO, 'work', '17', 'poster', 'poster_blur.jpg'), os.path.join(a, 'poster.jpg'))
    for f in ('whoosh', 'whoosh-short', 'whoosh-cinematic', 'pop', 'click-soft', 'click', 'sparkle', 'impact-bass-1',
              'impact-bass-2', 'riser', 'ping', 'notification', 'chime'):
        shutil.copy(os.path.join(SFX_DIR, f + '.mp3'), os.path.join(a, f'sfx-{f}.mp3'))
    dur = round(total + OUTRO, 3)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(MUSIC_SS), '-i', MUSIC_SRC, '-t', str(dur + 1),
                    '-c:a', 'aac', '-b:a', '192k', os.path.join(a, 'music-bed.m4a')], check=True)
    scenes, take = build(T, total)
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
    land = T.t(2, 'RM515')
    sfx = [('whoosh-short', 0.02, .35), ('riser', land - 2.2, .3), ('impact-bass-1', land - 0.05, .55), ('chime', land + 0.05, .35)]
    for i, d in enumerate([c(5), c(7), c(10)]):
        sfx.append((['whoosh-short', 'whoosh'][i % 2], d - 0.05, .35))
    for i, (a0, b0) in enumerate(take):
        sfx.append((['whoosh-cinematic', 'whoosh'][i % 2], a0 - 0.1, .5))
        if b0 < total:
            sfx.append(('whoosh-short', b0 - 0.05, .35))
    sfx += [('click', T.t(3, 'September'), .7), ('pop', T.t(3, 'September') + 0.6, .35), ('ping', T.t(4, 'setahun') - 0.2, .3),
            ('sparkle', T.t(5, 'segram'), .4), ('whoosh-short', T.t(7, 'melonjak') - 0.2, .35),
            ('sparkle', T.t(8, 'kilogram') + 0.8, .4), ('pop', T.t(9, 'banyak'), .35), ('pop', T.t(9, 'banyak') + 0.5, .3),
            ('pop', T.t(11, 'banyak'), .4), ('pop', T.t(11, 'banyak') + 0.18, .35), ('pop', T.t(11, 'banyak') + 0.36, .4),
            ('sparkle', T.t(13, 'penyimpan'), .4), ('impact-bass-2', T.t(14, 'Eza') - 0.4, .45), ('whoosh-cinematic', total - 0.1, .45)]
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

    cx, cy = BOX['x'] + BOX['w'] / 2, BOX['y'] + BOX['h'] / 2
    sw, sh = BOX['w'] / SCALE, BOX['h'] / SCALE
    ins = (FACE_Y - sh / 2, W - (FACE_X + sw / 2), H - (FACE_Y + sh / 2), FACE_X - sw / 2, 18 / SCALE)
    cam = [f"    tl.set('#punch', {{scale: {s}}}, {t:.3f});" for t, s in
           [(0.0, 1.06), (c(2) - 0.03, 1.12), (c(3) - 0.03, 1.0), (c(5) - 0.03, 1.05), (c(6) - 0.03, 1.0), (c(7) - 0.03, 1.07),
            (c(8) - 0.03, 1.0), (c(10) - 0.03, 1.05), (c(11) - 0.03, 1.1), (c(13) - 0.03, 1.0)]]
    for a0, b0 in take:
        cam += [f"    tl.to('#cam', {{scale: {SCALE}, x: {cx - FACE_X:.0f}, y: {cy - FACE_Y:.0f}, duration: .7, ease: 'power3.inOut'}}, {a0:.3f});",
                f"    tl.to('#camclip', {{'--t': '{ins[0]:.0f}px', '--r': '{ins[1]:.0f}px', '--b': '{ins[2]:.0f}px', '--l': '{ins[3]:.0f}px', '--rad': '{ins[4]:.0f}px', duration: .7, ease: 'power3.inOut'}}, {a0:.3f});",
                f"    tl.to('#live', {{opacity: 1, duration: .3}}, {a0 + 0.55:.3f});",
                f"    tl.to('#studiobg', {{opacity: 1, duration: .5, ease: 'power2.out'}}, {a0 + 0.05:.3f});"]
        if b0 < total:
            cam += [f"    tl.to('#cam', {{scale: 1, x: 0, y: 0, duration: .6, ease: 'power3.inOut'}}, {b0:.3f});",
                    f"    tl.to('#camclip', {{'--t': '0px', '--r': '0px', '--b': '0px', '--l': '0px', '--rad': '0px', duration: .6, ease: 'power3.inOut'}}, {b0:.3f});",
                    f"    tl.to('#live', {{opacity: 0, duration: .2}}, {b0:.3f});",
                    f"    tl.to('#studiobg', {{opacity: 0, duration: .4}}, {b0 + 0.25:.3f});"]
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
    html, body {{ margin: 0; padding: 0; background: #3a0610; }}
    #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: #3a0610; }}
    #studiobg {{ position: absolute; inset: 0; opacity: 0; z-index: 1;
               background: radial-gradient(80% 50% at 70% 15%, #B3243C 0%, rgba(179,36,60,0) 60%), linear-gradient(170deg, #7A1325 0%, #4A0914 60%, #2b040b 100%); }}
    #studiobg::after {{ content: ''; position: absolute; inset: 0; opacity: .35;
               background-image: repeating-linear-gradient(90deg, rgba(255,255,255,.06) 0 2px, transparent 2px 90px); }}
    #cam {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; z-index: 5; transform-origin: {FACE_X}px {FACE_Y}px; }}
    #camclip {{ position: absolute; inset: 0; --t: 0px; --r: 0px; --b: 0px; --l: 0px; --rad: 0px;
               clip-path: inset(var(--t) var(--r) var(--b) var(--l) round var(--rad)); overflow: hidden; }}
    #punch {{ position: absolute; inset: 0; transform-origin: 540px 880px; }}
    #base {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
    #live {{ position: absolute; left: {BOX['x'] - 6}px; top: {BOX['y'] - 6}px; width: {BOX['w'] + 12}px; height: {BOX['h'] + 12}px; z-index: 6; opacity: 0;
            border-radius: 22px; border: 6px solid #F5C451; box-sizing: border-box; }}
    #live b {{ position: absolute; left: 18px; top: 16px; padding: 4px 12px; border-radius: 6px; background: #E11D48; color: #fff;
              font: 700 28px 'JetBrains Mono', monospace; letter-spacing: 2px; }}
    #live b::before {{ content: ''; display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: #fff; margin-right: 8px; vertical-align: 1px; }}
    #capwrap {{ position: absolute; inset: 0; z-index: 30; }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="{W}" data-height="{H}">
    <div id="studiobg"></div>
    <div id="cam"><div id="camclip"><div id="punch">
      <video id="base" class="clip" src="assets/base.mp4" data-start="0" data-duration="{total:.3f}" data-track-index="0"
             data-has-audio="true" data-volume="1" playsinline></video>
    </div></div></div>
    <div id="live"><b>LIVE</b></div>
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
{chr(10).join(cam)}
    tl.set({{}}, {{}}, {dur});
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
"""
    open(os.path.join(proj, 'index.html'), 'w').write(index)
    return scenes, take
