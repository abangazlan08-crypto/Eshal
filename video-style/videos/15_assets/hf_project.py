"""HyperFrames project for video 15 (DCA emas). Look: "Market Desk" (new, unlike videos 1-14).

Deep forest-green glass panels with chart grids, market green/red, gold accent; Oswald (condensed display),
IBM Plex Mono (numbers, labels), Inter (body). Two layouts:
  * FULL     - talking head fills the frame; a chart deck sits above the head on the wall (y 175-560).
  * TAKEOVER - the camera shrinks into a gold-ringed circle (bottom-left, face kept whole), the frame turns
               into a green chart desk and the big chart takes y 190-890; captions move up to y ~930.
TikTok + Reels safe zones: nothing above y 168, words above y 1335, nothing at x > 940 for y 760-1520.
"""
import importlib.util, json, os, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('hf13', os.path.join(HERE, '..', '13_assets', 'hf_project.py'))
H13 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(H13)
Words, scene, blur_in, blur_out, pop_in, sfx_len = H13.Words, H13.scene, H13.blur_in, H13.blur_out, H13.pop_in, H13.sfx_len

W, H, FPS = 1080, 1920, 30
OUTRO = 3.6
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SFX_DIR = os.path.join(REPO, 'work', '13', 'hf', 'node_modules', 'hyperframes', 'dist', 'skills', 'media-use',
                       'audio', 'assets', 'sfx')
MUSIC_SRC = os.path.join(REPO, 'work', '13', 'music', 'techdoc.m4a')   # video 6's approved track
MUSIC_SS = 8.0
GREEN, RED, GOLD, INK, PAPER = '#2FBF71', '#E5484D', '#F2C14E', '#0B231C', '#F4F1EA'
# face centre in the source and the bubble it shrinks into
FACE_X, FACE_Y, BUB_X, BUB_Y, BUB_R_SRC, BUB_SCALE = 490, 900, 235, 1135, 300, 0.58

DECK = """
    .deck { position: absolute; left: 50px; top: 178px; width: 980px; height: 355px; border-radius: 30px; overflow: hidden;
            background: rgba(9,30,23,.90); box-shadow: 0 24px 60px rgba(0,0,0,.35), inset 0 0 0 2px rgba(242,193,78,.35); }
    .deck::before { content: ''; position: absolute; inset: 0; opacity: .5;
            background-image: linear-gradient(rgba(255,255,255,.07) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.07) 1px, transparent 1px);
            background-size: 60px 60px; }
    .tag { position: absolute; left: 36px; top: 26px; font: 600 28px 'IBM Plex Mono', monospace; letter-spacing: 4px; color: #F2C14E; }
    .tag::before { content: ''; display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: #2FBF71; margin-right: 12px; vertical-align: 2px; }
    .big { font: 700 74px/1.02 'Oswald', sans-serif; color: #F4F1EA; letter-spacing: .5px; text-transform: uppercase; }
    .mid { font: 700 46px/1.15 'Inter', sans-serif; color: #F4F1EA; }
    .up { color: #2FBF71; } .dn { color: #E5484D; } .au { color: #F2C14E; }
    .chipx { display: inline-flex; align-items: center; gap: 12px; padding: 10px 22px; border-radius: 14px; font: 700 36px 'Inter', sans-serif; }
    .ill { position: absolute; right: 26px; top: 24px; font: 600 28px 'IBM Plex Mono', monospace; letter-spacing: 3px; color: rgba(244,241,234,.55);
           border: 1px solid rgba(244,241,234,.35); padding: 4px 10px; border-radius: 8px; }
"""
DESK = """
    .desk { position: absolute; left: 50px; top: 185px; width: 980px; height: 715px; border-radius: 34px; overflow: hidden;
            background: rgba(9,30,23,.55); box-shadow: inset 0 0 0 2px rgba(242,193,78,.35); }
    .side { position: absolute; left: 450px; top: 1075px; width: 480px; }
"""
CSS = DECK + DESK


def deck_in(sel, t):
    return (f"    tl.fromTo('{sel}', {{opacity: 0, y: -30, clipPath: 'inset(0 0 100% 0 round 30px)'}}, "
            f"{{opacity: 1, y: 0, clipPath: 'inset(0 0 0% 0 round 30px)', duration: .6, ease: 'expo.out'}}, {t:.3f});\n")


def swap(out_sel, in_sel, t):
    return blur_out(out_sel, t - 0.22, 0.2) + blur_in(in_sel, t, 0.4, 18) + f"    tl.set('{in_sel}', {{opacity: 0}}, 0);\n"


def build(T, total):
    S, take = [], []
    c = T.cue

    # S0 hook: rising then falling line with the two reactions --------------------------------
    t0, t1 = 0.0, c(3) - 0.1
    html = """<div id="a-deck" class="deck"><div class="tag">HARGA EMAS</div>
      <svg id="a-ch" viewBox="0 0 560 300" style="position:absolute;left:400px;top:50px;width:560px;height:300px">
        <path id="a-up" d="M10 260 L90 220 L150 235 L230 150 L290 165 L360 60" fill="none" stroke="#2FBF71" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" pathLength="100" stroke-dasharray="100 120" stroke-dashoffset="110"/>
        <path id="a-dn" d="M360 60 L420 120 L470 100 L550 250" fill="none" stroke="#E5484D" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" pathLength="100" stroke-dasharray="100 120" stroke-dashoffset="110"/>
        <circle id="a-d1" cx="360" cy="60" r="13" fill="#2FBF71"/><circle id="a-d2" cx="550" cy="250" r="13" fill="#E5484D"/></svg>
      <div id="a-l1" style="position:absolute;left:36px;top:92px"><div class="big up">NAIK &#9650;</div><div class="mid">takut nak beli</div></div>
      <div id="a-l2" style="position:absolute;left:36px;top:92px"><div class="big dn">TURUN &#9660;</div><div class="mid">masih tunggu lagi</div></div></div>"""
    up, dn = T.t(1, 'naik') - t0, T.t(2, 'turun') - t0
    js = ("    tl.set('#a-deck', {opacity: 1}, 0);\n"
          f"    tl.fromTo('#a-up', {{attr: {{'stroke-dashoffset': 110}}}}, {{attr: {{'stroke-dashoffset': 0}}, duration: 1.0, ease: 'power2.inOut'}}, 0.05);\n"
          f"    tl.fromTo('#a-d1', {{scale: 0, transformOrigin: '50% 50%'}}, {{scale: 1, duration: .3, ease: 'back.out(2)'}}, 1.0);\n"
          f"    tl.fromTo('#a-l1', {{opacity: 1, y: 0}}, {{opacity: 1, y: 0, duration: .01}}, 0);\n"
          f"    tl.fromTo('#a-dn', {{attr: {{'stroke-dashoffset': 110}}}}, {{attr: {{'stroke-dashoffset': 0}}, duration: .8, ease: 'power2.in'}}, {dn - 0.2:.3f});\n"
          f"    tl.fromTo('#a-d2', {{scale: 0, transformOrigin: '50% 50%'}}, {{scale: 1, duration: .3, ease: 'back.out(2)'}}, {dn + 0.6:.3f});\n"
          + swap('#a-l1', '#a-l2', dn) + blur_out('#a-deck', t1 - t0 - 0.3))
    S.append(('sa', t0, t1 - t0, scene('sa', CSS, html, js)))

    # S1 necessities: price up, still buy ------------------------------------------------------
    t0, t1 = c(3) - 0.1, c(5) - 0.15
    html = """<div id="b-deck" class="deck"><div class="tag">BARANG KEPERLUAN</div>
      <div id="b-a" style="position:absolute;left:36px;top:96px" class="big">HARGA NAIK <span class="up">&#9650;</span></div>
      <div id="b-b" style="position:absolute;left:36px;top:200px"><span class="chipx" style="background:#2FBF71;color:#0B231C">&#10003; Kita tetap beli</span></div>
      <div id="b-c" style="position:absolute;left:36px;top:290px" class="mid">sebab kita tahu ia <span class="au">diperlukan</span></div></div>"""
    js = (deck_in('#b-deck', 0.1) + blur_in('#b-a', T.t(3, 'keperluan') - t0 - 0.2) + f"    tl.set(['#b-a','#b-b','#b-c'], {{opacity: 0}}, 0);\n"
          + pop_in('#b-b', T.t(3, 'tetap') - t0) + blur_in('#b-c', T.t(4, 'diperlukan') - t0 - 0.3) + blur_out('#b-deck', t1 - t0 - 0.3))
    S.append(('sb', t0, t1 - t0, scene('sb', CSS, html, js)))

    # S2 hunting the lowest price vs the real goal --------------------------------------------
    t0, t1 = c(5) - 0.15, c(7) - 0.15
    html = """<div id="c-deck" class="deck"><div class="tag">SIMPANAN EMAS</div>
      <svg viewBox="0 0 520 280" style="position:absolute;left:440px;top:60px;width:520px;height:280px">
        <path id="c-p" d="M10 90 L70 140 L120 110 L180 190 L240 150 L300 230 L360 170 L420 120 L510 150" fill="none" stroke="#F4F1EA" stroke-opacity=".7" stroke-width="6" stroke-linejoin="round" pathLength="100" stroke-dasharray="100 120" stroke-dashoffset="110"/>
        <g id="c-tgt"><circle cx="0" cy="0" r="34" fill="none" stroke="#F2C14E" stroke-width="5"/><line x1="-50" y1="0" x2="50" y2="0" stroke="#F2C14E" stroke-width="3"/><line x1="0" y1="-50" x2="0" y2="50" stroke="#F2C14E" stroke-width="3"/></g></svg>
      <div id="c-a" style="position:absolute;left:36px;top:96px;width:400px" class="big">CARI HARGA PALING RENDAH?</div>
      <div id="c-b" style="position:absolute;left:36px;top:84px;width:420px"><div class="mid" style="color:#9fb3aa">Matlamat sebenar:</div><div class="big au">BINA SIMPANAN</div></div></div>"""
    lo = T.t(6, 'rendah') - t0
    js = (deck_in('#c-deck', 0.1) +
          f"    tl.fromTo('#c-p', {{attr: {{'stroke-dashoffset': 110}}}}, {{attr: {{'stroke-dashoffset': 0}}, duration: 1.4, ease: 'power2.inOut'}}, 0.4);\n"
          + blur_in('#c-a', T.t(5, 'fokus') - t0 - 0.2) + f"    tl.set(['#c-a','#c-b'], {{opacity: 0}}, 0);\n"
          f"    tl.fromTo('#c-tgt', {{opacity: 0, x: 120, y: 80}}, {{opacity: 1, x: 180, y: 150, duration: .5, ease: 'power2.out'}}, {T.t(5, 'mencari') - t0:.3f});\n"
          f"    tl.to('#c-tgt', {{x: 360, y: 120, duration: .7, ease: 'power2.inOut'}}, {T.t(5, 'mencari') - t0 + 0.6:.3f});\n"
          f"    tl.to('#c-tgt', {{x: 300, y: 230, duration: .45, ease: 'back.out(1.6)'}}, {lo - 0.3:.3f});\n"
          f"    tl.to('#c-tgt', {{opacity: .25, duration: .3}}, {T.t(6, 'terlupa') - t0:.3f});\n"
          + swap('#c-a', '#c-b', T.t(6, 'matlamat') - t0) + blur_out('#c-deck', t1 - t0 - 0.3))
    S.append(('sc', t0, t1 - t0, scene('sc', CSS, html, js)))

    # S3 the real challenge: consistency streak -------------------------------------------------
    t0, t1 = c(7) - 0.15, c(9) - 0.2
    dots = ''.join(f"<div class='dt' id='d-dt{i}' style='left:{36 + i * 76}px'></div>" for i in range(12))
    html = f"""<div id="d-deck" class="deck"><div class="tag">CABARAN TERBESAR</div>
      <div id="d-a" style="position:absolute;left:36px;top:90px" class="big">BUKAN <span id="d-x" style="position:relative">TURUN NAIK HARGA<i id="d-s" style="position:absolute;left:-4px;right:-4px;top:48%;height:8px;background:#E5484D;border-radius:4px"></i></span></div>
      <div id="d-b" style="position:absolute;left:36px;top:180px" class="big au">TAPI KEKAL KONSISTEN</div>
      <div style="position:absolute;left:0;top:290px;width:980px;height:60px">{dots}</div></div>"""
    css = CSS + """
    .dt { position: absolute; top: 0; width: 54px; height: 54px; border-radius: 12px; background: rgba(244,241,234,.12); }
    .dt.on { background: #F2C14E; box-shadow: 0 0 18px rgba(242,193,78,.6); }"""
    tk = T.t(8, 'tetapi') - t0
    kk = T.t(8, 'konsisten') - t0
    js = (deck_in('#d-deck', 0.1) + blur_in('#d-a', T.t(7, 'bukan') - t0 - 0.2) + f"    tl.set(['#d-a','#d-b'], {{opacity: 0}}, 0);\n"
          f"    tl.fromTo('#d-s', {{scaleX: 0, transformOrigin: '0 50%'}}, {{scaleX: 1, duration: .3, ease: 'power3.out'}}, {tk:.3f});\n"
          f"    tl.to('#d-x', {{opacity: .45, duration: .2}}, {tk:.3f});\n" + blur_in('#d-b', tk + 0.5))
    for i in range(12):
        js += f"    tl.to('#d-dt{i}', {{background: '#F2C14E', boxShadow: '0 0 18px rgba(242,193,78,.6)', duration: .12}}, {kk - 0.6 + i * 0.08:.3f});\n"
    js += blur_out('#d-deck', t1 - t0 - 0.3)
    S.append(('sd', t0, t1 - t0, scene('sd', css, html, js)))

    # S4 TAKEOVER: DCA title + 3 rules ---------------------------------------------------------
    t0, t1 = c(9) - 0.2, c(13) - 0.25
    take.append((c(9) + 0.6, c(13) - 0.25))
    html = """<div class="desk"></div>
      <div id="e-k" style="position:absolute;left:96px;top:236px;font:600 30px 'IBM Plex Mono',monospace;letter-spacing:6px;color:#F2C14E">PENDEKATAN</div>
      <div id="e-t" style="position:absolute;left:92px;top:286px;font:700 128px/0.95 'Oswald',sans-serif;color:#F4F1EA;text-transform:uppercase">Dollar Cost<br><span style="color:#F2C14E">Averaging</span></div>
      <div id="e-dca" style="position:absolute;right:110px;top:250px;width:170px;height:170px;border-radius:50%;border:5px solid #F2C14E;color:#F2C14E;font:700 58px/160px 'Oswald',sans-serif;text-align:center">DCA</div>
      <div id="e-r1" class="rule" style="top:580px"><b>01</b>Jumlah wang yang <span class="au">tetap</span></div>
      <div id="e-r2" class="rule" style="top:680px"><b>02</b>Beli emas secara <span class="au">berkala</span></div>
      <div id="e-r3" class="rule" style="top:780px"><b>03</b>Tak terlalu ikut harga <span class="au">jangka pendek</span></div>
      <div id="e-side" class="side"><div style="font:600 28px 'IBM Plex Mono',monospace;letter-spacing:4px;color:#F2C14E">KONSEP</div>
        <div style="font:700 64px/1 'Oswald',sans-serif;color:#F4F1EA;text-transform:uppercase">Mudah.</div></div>"""
    css = CSS + """
    .rule { position: absolute; left: 92px; width: 896px; height: 82px; display: flex; align-items: center; gap: 22px;
            border-top: 2px solid rgba(242,193,78,.35); font: 700 44px 'Inter', sans-serif; color: #F4F1EA; }
    .rule b { font: 700 32px 'IBM Plex Mono', monospace; color: #F2C14E; width: 56px; }"""
    m = T.cue(10) - t0
    js = ("    tl.set(['#e-k','#e-t','#e-dca','#e-r1','#e-r2','#e-r3','#e-side'], {opacity: 0}, 0);\n"
          + blur_in('#e-k', 1.0) +
          f"    tl.fromTo('#e-t', {{opacity: 0, clipPath: 'inset(0 100% 0 0)'}}, {{opacity: 1, clipPath: 'inset(0 0% 0 0)', duration: .8, ease: 'power3.out'}}, {T.t(9, 'Dollar') - t0:.3f});\n"
          f"    tl.fromTo('#e-dca', {{opacity: 0, rotation: -90, scale: .5}}, {{opacity: 1, rotation: 0, scale: 1, duration: .6, ease: 'back.out(1.6)'}}, {T.t(9, 'DCA') - t0 - 0.1:.3f});\n"
          + blur_in('#e-side', m))
    for i, (cu, w) in enumerate([(11, 'tetap'), (12, 'berkala'), (12, 'tanpa')], 1):
        js += f"    tl.fromTo('#e-r{i}', {{opacity: 0, x: -60}}, {{opacity: 1, x: 0, duration: .5, ease: 'expo.out'}}, {T.t(cu, w) - t0 - 0.25:.3f});\n"
    S.append(('se', t0, t1 - t0, scene('se', css, html, js)))

    # S5 TAKEOVER: the DCA chart (RM500 a month, grams vs price, average cost) ------------------
    t0, t1 = c(13) - 0.25, c(21) - 0.2
    take.append((c(13) - 0.25, c(21) - 0.35))
    P = [100, 108, 116, 106, 95, 88, 97, 107, 113, 101, 92, 99]          # illustrative price path
    G = [1 / p for p in P]
    avg = len(P) / sum(G)
    X0, X1, PY0, PY1 = 140, 960, 300, 600                                  # price plot box
    BY = 860                                                                # gram bars baseline
    px = [X0 + i * (X1 - X0) / 11 for i in range(12)]
    py = [PY1 - (p - 80) / (120 - 80) * (PY1 - PY0) for p in P]
    gmax = max(G)
    bh = [g / gmax * 190 for g in G]
    pts = ' '.join(f"{x:.0f},{y:.0f}" for x, y in zip(px, py))
    ay = PY1 - (avg - 80) / 40 * (PY1 - PY0)
    hi = [i for i, p in enumerate(P) if p >= 106]
    lo = [i for i, p in enumerate(P) if p <= 95]
    bars = ''.join(f"<div class='br' id='f-b{i}' style='left:{x - 26:.0f}px;top:{BY - h:.0f}px;height:{h:.0f}px'></div>" for i, (x, h) in enumerate(zip(px, bh)))
    coins = ''.join(f"<div class='cn' id='f-c{i}' style='left:{x - 52:.0f}px'>RM500</div>" for i, x in enumerate(px))
    mdots = ''.join(f"<circle id='f-m{i}' cx='{x:.0f}' cy='{y:.0f}' r='9' fill='#F2C14E'/>" for i, (x, y) in enumerate(zip(px, py)))
    html = f"""<div class="desk"></div>
      <div style="position:absolute;left:84px;top:208px;font:600 28px 'IBM Plex Mono',monospace;letter-spacing:4px;color:#F2C14E">HARGA EMAS &middot; 12 BULAN</div>
      <div class="ill" style="position:absolute;left:auto;right:76px;top:204px">ILUSTRASI</div>
      <svg viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0;width:1080px;height:1920px">
        <polyline id="f-line" points="{pts}" fill="none" stroke="#F4F1EA" stroke-width="7" stroke-linejoin="round" stroke-linecap="round" pathLength="100" stroke-dasharray="100 120" stroke-dashoffset="110"/>
        {mdots}
        <line id="f-avg" x1="{X0 - 20}" y1="{ay:.0f}" x2="{X1 + 20}" y2="{ay:.0f}" stroke="#F2C14E" stroke-width="6" stroke-dasharray="18 14"/>
      </svg>
      <div id="f-avl" style="position:absolute;left:{X0 - 10}px;top:{ay - 64:.0f}px;padding:6px 16px;border-radius:10px;background:#F2C14E;color:#0B231C;font:800 32px 'Inter',sans-serif">Kos purata belian</div>
      <div style="position:absolute;left:84px;top:640px;font:600 28px 'IBM Plex Mono',monospace;letter-spacing:4px;color:rgba(244,241,234,.6)">GRAM DIPEROLEH</div>
      {bars}{coins}
      <div id="f-n1" class="note" style="top:1075px"><span class="dn">&#9650; Harga naik</span><br>gram mungkin sedikit berkurang</div>
      <div id="f-n2" class="note" style="top:1075px"><span class="up">&#9660; Harga turun</span><br>gram mungkin lebih banyak</div>
      <div id="f-n3" class="note" style="top:1075px"><span class="au">Kumpul emas</span><br>pada pelbagai paras harga</div>
      <div id="f-n0" class="note" style="top:1075px"><span class="au">RM500</span><br>setiap bulan</div>"""
    css = CSS + """
    .br { position: absolute; width: 52px; border-radius: 8px 8px 2px 2px; background: rgba(244,241,234,.55); transform-origin: 50% 100%; }
    .cn { position: absolute; top: 236px; width: 104px; height: 42px; border-radius: 21px; background: #F2C14E; color: #0B231C;
          font: 700 28px/42px 'IBM Plex Mono', monospace; text-align: center; }
    .note { position: absolute; left: 450px; width: 480px; font: 700 40px/1.25 'Inter', sans-serif; color: #F4F1EA; }"""
    rm = T.t(13, 'lima') - t0
    js = ("    tl.set(['#f-avg','#f-avl','.cn','#f-n0','#f-n1','#f-n2','#f-n3'], {opacity: 0}, 0);\n"
          "    tl.set('.br', {scaleY: 0}, 0);\n" + "    tl.set('circle[id^=f-m]', {scale: 0, transformOrigin: '50% 50%'}, 0);\n"
          f"    tl.fromTo('#f-line', {{attr: {{'stroke-dashoffset': 110}}}}, {{attr: {{'stroke-dashoffset': 0}}, duration: 1.6, ease: 'power2.inOut'}}, 0.5);\n"
          + blur_in('#f-n0', rm))
    for i in range(12):
        tt = rm + 0.15 + i * 0.16
        js += (f"    tl.fromTo('#f-c{i}', {{opacity: 0, y: -40}}, {{opacity: 1, y: 0, duration: .25, ease: 'power3.out'}}, {tt:.3f});\n"
               f"    tl.to('#f-c{i}', {{opacity: 0, y: 360, duration: .45, ease: 'power2.in'}}, {tt + 0.4:.3f});\n"
               f"    tl.to('#f-b{i}', {{scaleY: 1, duration: .4, ease: 'back.out(1.6)'}}, {tt + 0.8:.3f});\n")
    up = T.t(14, 'meningkat') - t0
    dn = T.t(17, 'menurun') - t0
    js += swap('#f-n0', '#f-n1', up)
    for i in hi:
        js += f"    tl.to('#f-b{i}', {{background: '#E5484D', duration: .25}}, {up + 0.2:.3f});\n"
    js += f"    tl.to('.br', {{background: 'rgba(244,241,234,.30)', duration: .25}}, {dn - 0.1:.3f});\n" + swap('#f-n1', '#f-n2', dn)
    for i in lo:
        js += f"    tl.to('#f-b{i}', {{background: '#2FBF71', duration: .25}}, {dn + 0.2:.3f});\n"
    lv = T.t(20, 'pelbagai') - t0
    av = T.t(20, 'kos') - t0
    js += (f"    tl.to('.br', {{background: 'rgba(244,241,234,.45)', duration: .3}}, {lv - 0.6:.3f});\n" + swap('#f-n2', '#f-n3', lv - 0.4))
    for i in range(12):
        js += f"    tl.to('#f-m{i}', {{scale: 1, duration: .25, ease: 'back.out(2.5)'}}, {lv + i * 0.07:.3f});\n"
    js += (f"    tl.fromTo('#f-avg', {{opacity: 1, attr: {{x2: {X0 - 20}}}}}, {{attr: {{x2: {X1 + 20}}}, duration: .9, ease: 'power2.inOut'}}, {av - 0.3:.3f});\n"
           + pop_in('#f-avl', av + 0.5))
    S.append(('sf', t0, t1 - t0, scene('sf', css, html, js)))

    # S6 DCA is not about the cheapest price ------------------------------------------------------
    t0, t1 = c(21) - 0.2, c(25) - 0.15
    html = """<div id="g-deck" class="deck"><div class="tag">DCA</div>
      <div id="g-a" style="position:absolute;left:36px;top:90px"><div class="big">BUKAN CARI HARGA</div><div class="big dn">PALING MURAH</div></div>
      <div id="g-b" style="position:absolute;left:36px;top:90px"><div class="mid" style="color:#9fb3aa">Urus ketidakpastian harga melalui</div><div class="big au">DISIPLIN PEMBELIAN</div></div>
      <div id="g-x" style="position:absolute;right:46px;top:100px;width:170px;height:170px;border-radius:50%;border:8px solid #E5484D;color:#E5484D;font:700 120px/150px 'Oswald',sans-serif;text-align:center">&#8800;</div></div>"""
    sb = T.t(22, 'Sebaliknya') - t0
    js = (deck_in('#g-deck', 0.1) + blur_in('#g-a', 0.35) + f"    tl.set(['#g-a','#g-b'], {{opacity: 0}}, 0);\n"
          + pop_in('#g-x', T.t(21, 'bukan') - t0) +
          f"    tl.to('#g-x', {{borderColor: '#2FBF71', color: '#2FBF71', duration: .3}}, {T.t(23, 'disiplin') - t0:.3f});\n"
          f"    tl.set('#g-x', {{textContent: '\\u2713'}}, {T.t(23, 'disiplin') - t0:.3f});\n"
          + swap('#g-a', '#g-b', sb) + blur_out('#g-deck', t1 - t0 - 0.3))
    S.append(('sg', t0, t1 - t0, scene('sg', CSS, html, js)))

    # S7 emotion gauge -----------------------------------------------------------------------------
    t0, t1 = c(25) - 0.15, c(27) - 0.2
    html = """<div id="h-deck" class="deck"><div class="tag">KEPUTUSAN</div>
      <svg viewBox="0 0 360 220" style="position:absolute;left:600px;top:80px;width:360px;height:220px">
        <path d="M30 190 A150 150 0 0 1 180 40" fill="none" stroke="#E5484D" stroke-width="26"/>
        <path d="M180 40 A150 150 0 0 1 330 190" fill="none" stroke="#2FBF71" stroke-width="26"/>
        <g id="h-n"><line x1="180" y1="190" x2="180" y2="70" stroke="#F4F1EA" stroke-width="10" stroke-linecap="round"/></g>
        <circle cx="180" cy="190" r="18" fill="#F4F1EA"/></svg>
      <div style="position:absolute;left:612px;top:310px;font:600 28px 'IBM Plex Mono',monospace;color:#E5484D;letter-spacing:3px">EMOSI</div>
      <div style="position:absolute;left:790px;top:310px;font:600 28px 'IBM Plex Mono',monospace;color:#2FBF71;letter-spacing:3px">DISIPLIN</div>
      <div id="h-a" style="position:absolute;left:36px;top:96px;width:540px"><div class="mid">Kurangkan keputusan</div><div class="big">BERDASARKAN <span class="dn">EMOSI</span></div></div></div>"""
    js = (deck_in('#h-deck', 0.1) + blur_in('#h-a', T.t(25, 'mengurangkan') - t0 - 0.2) + f"    tl.set('#h-a', {{opacity: 0}}, 0);\n"
          f"    tl.fromTo('#h-n', {{rotation: -70, svgOrigin: '180 190'}}, {{rotation: -35, duration: .4, ease: 'power2.out'}}, 0.5);\n"
          f"    tl.to('#h-n', {{rotation: -62, duration: .25, yoyo: true, repeat: 3, ease: 'sine.inOut'}}, 1.0);\n"
          f"    tl.to('#h-n', {{rotation: 58, duration: .9, ease: 'elastic.out(1, .6)'}}, {T.t(26, 'emosi') - t0 + 0.2:.3f});\n"
          + blur_out('#h-deck', t1 - t0 - 0.3))
    S.append(('sh', t0, t1 - t0, scene('sh', CSS, html, js)))

    # S8 TAKEOVER: GAP account, start with RM100, add step by step -------------------------------
    t0, t1 = c(27) - 0.2, c(29) - 0.2
    take.append((c(27) - 0.2, c(29) - 0.35))
    # the user's real GAP app screenshot (name, account no. and wallet blurred), 1290x1050 -> 640x521 screen
    html = """<div class="desk"></div>
      <div style="position:absolute;left:84px;top:208px;font:600 28px 'IBM Plex Mono',monospace;letter-spacing:4px;color:#F2C14E">AKAUN GAP &middot; PUBLIC GOLD</div>
      <div id="i-ph" style="position:absolute;left:206px;top:262px;width:668px;height:600px;border-radius:58px;background:#111;
           box-shadow:0 40px 90px rgba(0,0,0,.55), inset 0 0 0 3px #2b2b2b">
        <div id="i-scr" style="position:absolute;left:14px;top:14px;width:640px;height:586px;border-radius:46px 46px 0 0;overflow:hidden;background:#fff6c9">
          <img src="assets/gap_app.jpg" style="position:absolute;left:0;top:44px;width:640px;height:521px">
          <div style="position:absolute;left:0;top:0;width:640px;height:46px;background:#F8DD5A"></div>
          <div style="position:absolute;left:250px;top:10px;width:140px;height:30px;border-radius:16px;background:#111"></div>
          <div id="i-hl" style="position:absolute;left:18px;top:478px;width:250px;height:64px;border-radius:14px;border:5px solid #E5484D;box-shadow:0 0 0 6px rgba(229,72,77,.25)"></div>
          <div id="i-tap" style="position:absolute;left:79px;top:313px;width:84px;height:84px;border-radius:50%;border:6px solid #F2C14E;box-shadow:0 0 24px rgba(242,193,78,.8)"></div>
          <div id="i-glare" style="position:absolute;inset:0;background:linear-gradient(115deg,transparent 35%,rgba(255,255,255,.45) 50%,transparent 65%);background-size:300% 100%;background-position:120% 0"></div>
        </div>
        <div style="position:absolute;left:0;right:0;bottom:-2px;height:120px;background:linear-gradient(180deg,rgba(9,30,23,0),rgba(9,30,23,1));border-radius:0 0 58px 58px"></div></div>
      <div id="i-s1" class="side"><div style="font:600 28px 'IBM Plex Mono',monospace;letter-spacing:4px;color:#F2C14E">MULA DENGAN</div>
        <div style="font:700 92px/1 'Oswald',sans-serif;color:#F4F1EA">RM100</div></div>
      <div id="i-s2" class="side"><div style="font:700 44px/1.2 'Inter',sans-serif;color:#F4F1EA">Tambah ikut <span class="au">kemampuan</span></div></div>"""
    css = CSS
    n0 = T.t(27, 'RM') - t0
    tp = T.t(28, 'menambah') - t0
    js = ("    tl.set(['#i-ph','#i-hl','#i-tap','#i-s1','#i-s2'], {opacity: 0}, 0);\n"
          f"    tl.fromTo('#i-ph', {{opacity: 0, y: 140, rotationX: 28, transformPerspective: 1200}}, {{opacity: 1, y: 0, rotationX: 0, duration: .9, ease: 'expo.out'}}, 0.55);\n"
          f"    tl.fromTo('#i-glare', {{backgroundPosition: '120% 0'}}, {{backgroundPosition: '-60% 0', duration: 1.1, ease: 'power2.inOut'}}, 1.2);\n"
          f"    tl.fromTo('#i-hl', {{opacity: 0, scale: 1.25}}, {{opacity: 1, scale: 1, duration: .35, ease: 'back.out(2)'}}, {n0 - 0.1:.3f});\n"
          + blur_in('#i-s1', n0 - 0.1) +
          f"    tl.to('#i-hl', {{opacity: 0, duration: .25}}, {tp - 0.3:.3f});\n"
          f"    tl.fromTo('#i-tap', {{opacity: 1, scale: .4}}, {{opacity: 0, scale: 1.6, duration: .6, ease: 'power2.out', immediateRender: false}}, {tp:.3f});\n"
          f"    tl.fromTo('#i-tap', {{opacity: 1, scale: .4}}, {{opacity: 0, scale: 1.6, duration: .6, ease: 'power2.out', immediateRender: false}}, {tp + 0.7:.3f});\n"
          + swap('#i-s1', '#i-s2', T.t(28, 'berperingkat') - t0 - 0.2))
    S.append(('si', t0, t1 - t0, scene('si', css, html, js)))

    # S9 two kinds of smart ----------------------------------------------------------------------
    t0, t1 = c(29) - 0.2, c(31) - 0.15
    html = """<div id="j-deck" class="deck"><div class="tag">MEMBINA KEKAYAAN</div>
      <div id="j-1" class="col" style="left:36px"><div class="ck">&#10003;</div><div class="mid">Bijak pilih</div><div class="big">ASET</div></div>
      <div id="j-p" style="position:absolute;left:470px;top:150px;font:700 90px 'Oswald',sans-serif;color:#F2C14E">+</div>
      <div id="j-2" class="col" style="left:560px"><div class="ck">&#10003;</div><div class="mid">Bijak urus</div><div class="big au">TINGKAH LAKU</div></div></div>"""
    css = CSS + """
    .col { position: absolute; top: 84px; width: 400px; }
    .ck { width: 56px; height: 56px; border-radius: 50%; background: #2FBF71; color: #0B231C; font: 800 36px/56px 'Inter', sans-serif; text-align: center; margin-bottom: 10px; }"""
    js = (deck_in('#j-deck', 0.1) + "    tl.set(['#j-1','#j-2','#j-p'], {opacity: 0}, 0);\n"
          + blur_in('#j-1', T.t(29, 'aset') - t0 - 0.3) + pop_in('#j-p', T.cue(30) - t0) + blur_in('#j-2', T.t(30, 'tingkah') - t0 - 0.3)
          + blur_out('#j-deck', t1 - t0 - 0.3))
    S.append(('sj', t0, t1 - t0, scene('sj', css, html, js)))

    # S10 reading prices vs planning + discipline --------------------------------------------------
    t0, t1 = c(31) - 0.15, c(35) - 0.15
    html = """<div id="k-deck" class="deck"><div class="tag">AKHIRNYA</div>
      <div id="k-a" style="position:absolute;left:36px;top:90px"><div class="mid" style="color:#9fb3aa">Pandai baca pergerakan harga</div>
        <div class="big"><span class="dn">&#8800;</span> BERJAYA BINA SIMPANAN</div></div>
      <div id="k-b" style="position:absolute;left:36px;top:90px;width:910px"><div class="big"><span class="au">PERANCANGAN</span> + <span class="au">DISIPLIN</span></div>
        <div class="mid">= asas lebih kukuh untuk capai matlamat kewangan</div></div></div>"""
    js = (deck_in('#k-deck', 0.1) + blur_in('#k-a', 0.5) + f"    tl.set(['#k-a','#k-b'], {{opacity: 0}}, 0);\n"
          + swap('#k-a', '#k-b', T.t(33, 'perancangan') - t0 - 0.2) + blur_out('#k-deck', t1 - t0 - 0.3))
    S.append(('sk', t0, t1 - t0, scene('sk', CSS, html, js)))

    # S11 how to start: checklist ----------------------------------------------------------------
    t0, t1 = c(35) - 0.15, c(46) - 0.25
    html = """<div id="l-deck" class="deck"><div class="tag">BELUM MULA?</div>
      <div id="l-1" class="li" style="top:96px"><b>01</b>Mula dengan jumlah yang <span class="au">selesa</span></div>
      <div id="l-2" class="li" style="top:186px"><b>02</b>Faham <span class="au">tujuan</span> simpan emas</div>
      <div id="l-3" class="li" style="top:276px"><b>03</b>Bina <span class="au">tabiat</span> menyimpan</div></div>"""
    css = CSS + """
    .li { position: absolute; left: 36px; width: 900px; height: 76px; display: flex; align-items: center; gap: 20px;
          border-bottom: 2px solid rgba(242,193,78,.25); font: 700 44px 'Inter', sans-serif; color: #F4F1EA; }
    .li b { font: 700 30px 'IBM Plex Mono', monospace; color: #F2C14E; }"""
    js = deck_in('#l-deck', 0.1) + "    tl.set(['#l-1','#l-2','#l-3'], {opacity: 0}, 0);\n"
    for i, (cu, w) in enumerate([(35, 'selesa'), (36, 'tujuan'), (38, 'tabiat')], 1):
        js += f"    tl.fromTo('#l-{i}', {{opacity: 0, x: -50}}, {{opacity: 1, x: 0, duration: .45, ease: 'expo.out'}}, {T.t(cu, w) - t0 - 0.35:.3f});\n"
    js += blur_out('#l-deck', t1 - t0 - 0.3)
    S.append(('sl', t0, t1 - t0, scene('sl', css, html, js)))

    # S12 TAKEOVER CTA -------------------------------------------------------------------------------
    t0, t1 = c(46) - 0.25, total
    take.append((c(46) - 0.25, total + 1))
    html = """<div class="desk"></div>
      <div id="m-a" style="position:absolute;left:92px;top:260px;width:900px"><div style="font:600 30px 'IBM Plex Mono',monospace;letter-spacing:6px;color:#F2C14E">NAK MULA?</div>
        <div style="font:700 104px/1 'Oswald',sans-serif;color:#F4F1EA;text-transform:uppercase;margin-top:12px">Simpan emas<br><span style="color:#F2C14E">Public Gold</span><br>dengan betul</div></div>
      <div id="m-btn" style="position:absolute;left:92px;top:720px;width:860px;height:130px;border-radius:30px;background:#F4F1EA;box-shadow:0 20px 50px rgba(0,0,0,.4)">
        <div style="position:absolute;left:22px;top:18px;width:94px;height:94px;border-radius:50%;background:#0B231C;display:flex;align-items:center;justify-content:center"><img src="assets/logo_white.png" style="width:80px"></div>
        <div style="position:absolute;left:138px;top:38px;font:800 46px 'Inter',sans-serif;color:#0B231C">Azlan &amp; Eza</div>
        <div id="m-f" style="position:absolute;right:20px;top:20px;width:230px;height:90px;border-radius:22px;background:#E5484D;color:#fff;font:800 42px/90px 'Inter',sans-serif;text-align:center">Follow</div></div>"""
    fo = T.t(46, 'follow') - t0
    js = ("    tl.set(['#m-a','#m-btn'], {opacity: 0}, 0);\n" + blur_in('#m-a', 0.5) +
          f"    tl.fromTo('#m-btn', {{opacity: 0, y: 60}}, {{opacity: 1, y: 0, duration: .6, ease: 'expo.out'}}, {fo - 1.0:.3f});\n"
          f"    tl.to('#m-f', {{scale: .9, duration: .08}}, {fo:.3f});\n"
          f"    tl.to('#m-f', {{scale: 1, background: '#2FBF71', duration: .25, ease: 'back.out(3)'}}, {fo + 0.08:.3f});\n"
          f"    tl.set('#m-f', {{textContent: 'Following'}}, {fo + 0.1:.3f});\n")
    S.append(('sm', t0, t1 - t0, scene('sm', CSS, html, js)))
    return S, take


def caption_scene(words, total):
    groups, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        if (len(cur) >= 4 or nxt is None or nxt['cue'] != w['cue'] or w['w'][-1] in '.,?!' or nxt['os'] - w['oe'] > 0.25):
            groups.append(cur); cur = []
    html, js = [], []
    for gi, g in enumerate(groups):
        spans = ' '.join(f"<span id='cw{gi}_{k}'>{w['w']}</span>" for k, w in enumerate(g))
        html.append(f"    <div id='cg{gi}' class='cg'><div class='cin'>{spans}</div></div>")
        a = max(0.0, g[0]['os'] - 0.08)
        b = min(g[-1]['oe'] + 0.35, groups[gi + 1][0]['os'] - 0.08 if gi + 1 < len(groups) else total)
        js.append(f"    tl.set('#cg{gi}', {{opacity: 1, visibility: 'visible'}}, {a:.3f});")
        js.append(f"    tl.fromTo('#cg{gi} .cin', {{scale: .9, opacity: 0}}, {{scale: 1, opacity: 1, duration: .14, ease: 'power3.out'}}, {a:.3f});")
        for k, w in enumerate(g):
            js.append(f"    tl.set('#cw{gi}_{k}', {{color: '#0B231C', backgroundColor: '#F2C14E'}}, {w['os']:.3f});")
            if k < len(g) - 1:
                js.append(f"    tl.set('#cw{gi}_{k}', {{color: '#F4F1EA', backgroundColor: 'rgba(0,0,0,0)'}}, {g[k + 1]['os']:.3f});")
        js.append(f"    tl.set('#cg{gi}', {{opacity: 0, visibility: 'hidden'}}, {b:.3f});")
    css = """
    .cg { position: absolute; left: 40px; width: 900px; top: 1236px; text-align: center; opacity: 0; visibility: hidden; }
    .cin { display: inline-block; padding: 8px 14px; border-radius: 12px; background: rgba(9,30,23,.82);
           font: 700 46px/1.2 'Inter', sans-serif; color: #F4F1EA; }
    .cin span { padding: 0 6px; border-radius: 8px; }"""
    return scene('captions', css, '\n'.join(html), '\n'.join(js))


def outro_scene():
    css = """
    #o-bg { position: absolute; inset: 0; background: radial-gradient(80% 60% at 50% 40%, #12382c, #071a14); }
    #o-grid { position: absolute; inset: 0; opacity: .5; background-image: linear-gradient(rgba(255,255,255,.06) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,.06) 1px, transparent 1px); background-size: 60px 60px; }
    #o-logo { position: absolute; left: 330px; top: 620px; width: 420px; }
    #o-l { position: absolute; left: 140px; top: 1000px; width: 800px; height: 120px; }
    #o-t { position: absolute; left: 0; width: 1080px; top: 1150px; text-align: center; font: 600 30px 'IBM Plex Mono', monospace; letter-spacing: 8px; color: #F2C14E; }"""
    html = """<div id="o-bg"></div><div id="o-grid"></div><img id="o-logo" src="assets/logo_white.png">
    <svg id="o-l" viewBox="0 0 800 120"><polyline id="o-p" points="0,100 120,80 220,92 340,60 460,70 580,36 700,44 800,10" fill="none" stroke="#2FBF71" stroke-width="6"
      stroke-linejoin="round" pathLength="100" stroke-dasharray="100 120" stroke-dashoffset="110"/></svg>
    <div id="o-t">AZLAN &amp; EZA</div>"""
    js = ("    tl.fromTo('#o-bg', {opacity: 0}, {opacity: 1, duration: .35}, 0);\n    tl.fromTo('#o-grid', {opacity: 0}, {opacity: .5, duration: .5}, .1);\n"
          "    tl.fromTo('#o-logo', {opacity: 0, scale: .85, filter: 'blur(10px)'}, {opacity: 1, scale: 1, filter: 'blur(0px)', duration: .7, ease: 'expo.out'}, .3);\n"
          "    tl.fromTo('#o-p', {attr: {'stroke-dashoffset': 110}}, {attr: {'stroke-dashoffset': 0}, duration: 1.2, ease: 'power2.inOut'}, .6);\n"
          + blur_in('#o-t', 1.0) + f"    tl.to('#root', {{opacity: 0, duration: .45, ease: 'power2.in'}}, {OUTRO - 0.5:.2f});\n")
    return scene('outro', css, html, js)


def css_initial(src):
    """Initial hidden states as CSS (a tl.set at 0 does not show while the playhead sits on the scene's first frame)."""
    import re
    rules = []
    for m in re.finditer(r"tl\.set\((\[[^\]]*\]|'[^']*'), \{(opacity: 0)\}, 0\);", src):
        sels = [x.strip().strip("'") for x in m.group(1).strip('[]').split(',')]
        prop = 'opacity: 0'
        rules.append(f"    {', '.join(sels)} {{ {prop}; }}")
    return src.replace('  </style>', '\n'.join(rules) + '\n  </style>', 1)


def write_project(proj, words, total):
    T = Words(words)
    a = os.path.join(proj, 'assets')
    comp = os.path.join(proj, 'compositions')
    os.makedirs(comp, exist_ok=True)
    shutil.copy(os.path.join(REPO, 'work', '13', 'proj', 'assets', 'logo_white.png'), a)
    shutil.copy(os.path.join(REPO, 'work', '13', 'proj', 'assets', 'gsap.min.js'), a)
    shutil.copy(os.path.join(REPO, 'work', '15', 'gap', 'gap_app.jpg'), a)
    for f in ('whoosh', 'whoosh-short', 'whoosh-cinematic', 'pop', 'click-soft', 'click', 'sparkle', 'impact-bass-1',
              'impact-bass-2', 'riser', 'ping', 'key-press'):
        shutil.copy(os.path.join(SFX_DIR, f + '.mp3'), os.path.join(a, f'sfx-{f}.mp3'))
    dur = round(total + OUTRO, 3)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(MUSIC_SS), '-i', MUSIC_SRC, '-t', str(dur + 1),
                    '-c:a', 'aac', '-b:a', '192k', os.path.join(a, 'music-bed.m4a')], check=True)
    scenes, take = build(T, total)
    merged = []                       # back-to-back takeovers stay in the bubble
    for a0, b0 in take:
        if merged and a0 - merged[-1][1] < 1.0:
            merged[-1] = (merged[-1][0], b0)
        else:
            merged.append((a0, b0))
    take = merged
    for sid, st, du, src in scenes:
        open(os.path.join(comp, f'{sid}.html'), 'w').write(css_initial(src))
    open(os.path.join(comp, 'captions.html'), 'w').write(caption_scene(words, total))
    open(os.path.join(comp, 'outro.html'), 'w').write(outro_scene())

    # music ducking: 0.12 under speech, 0.3 in gaps, 0.45 on the outro
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
    lane = lane[:500]

    # SFX: few, exact, each with a cause on screen
    c = T.cue
    sfx = [('impact-bass-1', 0.02, .5), ('whoosh-short', T.t(2, 'turun') - 0.15, .45)]
    decks = [c(3), c(5), c(7), c(21), c(25), c(29), c(31), c(35)]
    for i, d in enumerate(decks):
        sfx.append((['whoosh-short', 'whoosh'][i % 2], d - 0.05, .35))
    for i, (a0, b0) in enumerate(take):
        sfx.append((['whoosh-cinematic', 'whoosh'][i % 2], a0 - 0.1, .5))
    sfx += [('pop', T.t(3, 'tetap'), .45), ('ping', T.t(6, 'rendah') - 0.1, .3), ('click-soft', T.t(8, 'tetapi'), .7),
            ('sparkle', T.t(8, 'konsisten') - 0.4, .35), ('impact-bass-2', T.t(9, 'Dollar') - 0.45, .4),
            ('pop', T.t(11, 'tetap') - 0.25, .35), ('pop', T.t(12, 'berkala') - 0.25, .35), ('pop', T.t(12, 'jangka') - 0.25, .35),
            ('pop', T.t(14, 'meningkat') + 0.1, .35), ('pop', T.t(17, 'menurun') + 0.1, .35),
            ('riser', T.t(20, 'kos') - 2.1, .3), ('impact-bass-1', T.t(20, 'kos') - 0.2, .45), ('sparkle', T.t(20, 'kos') + 0.5, .35),
            ('click-soft', T.t(23, 'disiplin'), .7), ('whoosh-short', T.t(26, 'emosi') + 0.1, .35),
            ('pop', T.t(27, 'RM') - 0.1, .4), ('click-soft', T.t(28, 'menambah'), .7), ('click-soft', T.t(28, 'menambah') + 0.7, .6), ('pop', T.t(29, 'aset') - 0.25, .35), ('pop', T.t(30, 'tingkah') - 0.25, .35),
            ('click-soft', T.t(35, 'selesa') - 0.3, .6), ('click-soft', T.t(36, 'tujuan') - 0.3, .6), ('click-soft', T.t(38, 'tabiat') - 0.3, .6),
            ('click', T.t(46, 'follow'), .8), ('whoosh-cinematic', total - 0.1, .45)]
    for i in range(12):
        if i % 3 == 0:
            sfx.append(('key-press', T.t(13, 'lima') + 0.15 + i * 0.16, .35))
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

    # camera: punch-ins in FULL, shrink into the bubble in TAKEOVER (captions lift with it)
    tx, ty = BUB_X - FACE_X, BUB_Y - FACE_Y
    cam = [f"    tl.set('#punch', {{scale: {s}}}, {t:.3f});" for t, s in
           [(0.0, 1.06), (c(2) - 0.03, 1.0), (c(5) - 0.03, 1.05), (c(7) - 0.03, 1.0), (c(8) - 0.03, 1.06),
            (c(9) - 0.03, 1.0), (c(21) - 0.03, 1.05), (c(22) - 0.03, 1.0), (c(25) - 0.03, 1.06), (c(27) - 0.03, 1.0),
            (c(31) - 0.03, 1.05), (c(33) - 0.03, 1.0), (c(37) - 0.03, 1.06), (c(38) - 0.03, 1.0)]]
    for a0, b0 in take:
        cam += [f"    tl.to('#cam', {{scale: {BUB_SCALE}, x: {tx}, y: {ty}, duration: .7, ease: 'power3.inOut'}}, {a0:.3f});",
                f"    tl.to('#camclip', {{'--r': '{BUB_R_SRC}px', duration: .7, ease: 'power3.inOut'}}, {a0:.3f});",
                f"    tl.to('#ring', {{opacity: 1, scale: 1, duration: .5, ease: 'back.out(1.6)'}}, {a0 + 0.45:.3f});",
                f"    tl.to('#deskbg', {{opacity: 1, duration: .5, ease: 'power2.out'}}, {a0 + 0.05:.3f});",
                f"    tl.to('#capwrap', {{y: -305, duration: .6, ease: 'power3.inOut'}}, {a0 + 0.1:.3f});"]
        if b0 < total:
            cam += [f"    tl.to('#cam', {{scale: 1, x: 0, y: 0, duration: .6, ease: 'power3.inOut'}}, {b0:.3f});",
                    f"    tl.to('#camclip', {{'--r': '1400px', duration: .6, ease: 'power3.inOut'}}, {b0:.3f});",
                    f"    tl.to('#ring', {{opacity: 0, scale: .9, duration: .25}}, {b0:.3f});",
                    f"    tl.to('#deskbg', {{opacity: 0, duration: .4}}, {b0 + 0.25:.3f});",
                    f"    tl.to('#capwrap', {{y: 0, duration: .55, ease: 'power3.inOut'}}, {b0:.3f});"]
    hosts = [f'    <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{st:.3f}" '
             f'data-duration="{du:.3f}" data-track-index="{2 + i % 2}" data-track-kind="graphics" data-width="{W}" data-height="{H}" '
             f'style="z-index: 20"></div>' for i, (sid, st, du, _) in enumerate(scenes)]
    lane_json = json.dumps({'version': 1, 'lanes': [{'target': 'volume', 'points': lane}]}).replace('"', '&quot;')
    ring = BUB_R_SRC * BUB_SCALE
    index = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="assets/gsap.min.js"></script>
  <style>
    html, body {{ margin: 0; padding: 0; background: #071a14; }}
    #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: #071a14; }}
    #deskbg {{ position: absolute; inset: 0; opacity: 0; z-index: 1;
              background: radial-gradient(90% 60% at 50% 35%, #12382c 0%, #0a251d 55%, #061710 100%); }}
    #deskbg::after {{ content: ''; position: absolute; inset: 0; opacity: .6;
              background-image: linear-gradient(rgba(255,255,255,.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.05) 1px, transparent 1px);
              background-size: 60px 60px; }}
    #cam {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; z-index: 5; transform-origin: {FACE_X}px {FACE_Y}px; }}
    #camclip {{ position: absolute; inset: 0; --r: 1400px; clip-path: circle(var(--r) at {FACE_X}px {FACE_Y}px); overflow: hidden; }}
    #punch {{ position: absolute; inset: 0; transform-origin: 540px 860px; }}
    #base {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
    #ring {{ position: absolute; left: {BUB_X - ring - 8:.0f}px; top: {BUB_Y - ring - 8:.0f}px; width: {2 * ring + 16:.0f}px; height: {2 * ring + 16:.0f}px;
            border-radius: 50%; border: 6px solid #F2C14E; box-sizing: border-box; z-index: 6; opacity: 0;
            box-shadow: 0 0 40px rgba(242,193,78,.35); }}
    #capwrap {{ position: absolute; inset: 0; z-index: 30; }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="{W}" data-height="{H}">
    <div id="deskbg"></div>
    <div id="cam"><div id="camclip"><div id="punch">
      <video id="base" class="clip" src="assets/base.mp4" data-start="0" data-duration="{total:.3f}" data-track-index="0"
             data-has-audio="true" data-volume="1" playsinline></video>
    </div></div></div>
    <div id="ring"></div>
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
