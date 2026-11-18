"""HyperFrames project for video 16 (bonus hujung tahun, Bahasa Sarawak). Look: "Sky Glass" (new, unlike 1-15).

White/sky-blue frosted glass cards with navy ink, sky-blue accent, gold for emas; Archivo Black (kinetic), Nunito (body),
Space Mono (labels). Subtitles: white, important words in light blue (user's rule).
  * FULL     - talking head fills the frame; a glass deck sits on the wall above the head (y 175-555).
  * TAKEOVER - the frame turns into a soft sky desk, the camera becomes a white-framed portrait card bottom-left
               (face whole), the big chart takes y 185-840 and captions lift to y ~870.
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
MUSIC_SRC = os.path.join(REPO, 'work', '13', 'music', 'acoustic.m4a')   # video 4's approved "Positive Hopeful" track
MUSIC_SS = 36.0
NAVY, SKY, SKYL, GOLD, RED = '#0B2545', '#0EA5E9', '#7DD3FC', '#E9A93A', '#EF4444'
# camera card (TAKEOVER): source rect around the face -> on-screen card
FACE_X, FACE_Y, SCALE = 528, 960, 0.6
CARD = dict(x=60, y=945, w=330, h=430)
CAP_LIFT = -368

CSS = """
    .deck { position: absolute; left: 50px; top: 178px; width: 980px; height: 370px; border-radius: 36px; overflow: hidden;
            background: linear-gradient(160deg, rgba(255,255,255,.92), rgba(225,242,255,.88));
            box-shadow: 0 24px 60px rgba(11,37,69,.25), inset 0 0 0 2px rgba(255,255,255,.9); }
    .lab { position: absolute; left: 38px; top: 28px; font: 700 28px 'Space Mono', monospace; letter-spacing: 4px; color: #0EA5E9; }
    .kin { font: 400 92px/1 'Archivo Black', sans-serif; color: #0B2545; letter-spacing: -1px; }
    .bd { font: 800 46px/1.15 'Nunito', sans-serif; color: #0B2545; }
    .sky { color: #0EA5E9; } .au { color: #D99A22; } .rd { color: #EF4444; }
    .desk { position: absolute; left: 50px; top: 185px; width: 980px; height: 650px; border-radius: 40px; overflow: hidden;
            background: linear-gradient(160deg, rgba(255,255,255,.95), rgba(232,245,255,.92));
            box-shadow: 0 30px 70px rgba(11,37,69,.18), inset 0 0 0 2px #fff; }
    .side { position: absolute; left: 430px; top: 975px; width: 500px; }
    .ill { position: absolute; right: 30px; top: 26px; font: 700 28px 'Space Mono', monospace; letter-spacing: 3px; color: #7a8ba3;
           border: 2px solid #c6d3e3; padding: 2px 12px; border-radius: 10px; }
"""


def deck_in(sel, t):
    return (f"    tl.fromTo('{sel}', {{opacity: 0, y: -40, scale: .96}}, {{opacity: 1, y: 0, scale: 1, duration: .6, ease: 'expo.out'}}, {t:.3f});\n")


def swap(a, b, t):
    return blur_out(a, t - 0.22, 0.2) + blur_in(b, t, 0.4, 18) + f"    tl.set('{b}', {{opacity: 0}}, 0);\n"


def build(T, total):
    S, take = [], []
    c = T.cue

    # S0 HOOK: RM10,000 bonus drains to RM0, "Pernah jadi sik?" --------------------------------
    t0, t1 = 0.0, c(4) + 0.7
    html = """<div id="a-d" class="deck"><div class="lab">BONUS MASUK</div>
      <div id="a-n" style="position:absolute;left:36px;top:84px;font:400 150px/1 'Archivo Black',sans-serif;color:#0B2545;letter-spacing:-3px">RM<span id="a-v">10,000</span></div>
      <div id="a-bar" style="position:absolute;left:40px;top:262px;width:900px;height:40px;border-radius:20px;background:#dbeafe;overflow:hidden">
        <div id="a-fill" style="position:absolute;left:0;top:0;bottom:0;width:100%;border-radius:20px;background:linear-gradient(90deg,#0EA5E9,#7DD3FC);transform-origin:0 50%"></div></div>
      <div id="a-t" style="position:absolute;left:40px;top:312px;font:700 28px 'Space Mono',monospace;color:#EF4444;letter-spacing:3px">SIK SAMPAI SEBULAN</div>
      <div id="a-q" style="position:absolute;left:0;right:0;top:110px;text-align:center" class="kin">PERNAH JADI <span class="sky">SIK?</span></div></div>"""
    sb = T.t(2, 'sebulan') - t0
    hp = T.t(2, 'pergi') - t0
    js = ("    tl.set('#a-d', {opacity: 1}, 0);\n    tl.set(['#a-t'], {opacity: 0}, 0);\n"
          "    tl.fromTo('#a-n', {scale: 1.08, transformOrigin: '0 50%'}, {scale: 1, duration: .5, ease: 'expo.out'}, 0);\n"
          + blur_in('#a-t', sb - 0.3) +
          f"    const v = {{n: 10000}};\n"
          f"    tl.to(v, {{n: 0, duration: {hp - sb + 0.6:.2f}, ease: 'power2.in', onUpdate: () => {{ document.getElementById('a-v').textContent = Math.round(v.n).toLocaleString('en-US'); }}}}, {sb:.3f});\n"
          f"    tl.to('#a-fill', {{scaleX: 0, background: '#EF4444', duration: {hp - sb + 0.6:.2f}, ease: 'power2.in'}}, {sb:.3f});\n"
          f"    tl.to('#a-n', {{color: '#EF4444', duration: .3}}, {hp:.3f});\n"
          + swap('#a-n', '#a-q', T.cue(3) - t0) +
          f"    tl.to(['#a-bar','#a-t','#a-lab'], {{opacity: 0, duration: .2}}, {T.cue(3) - t0 - 0.2:.3f});\n"
          + blur_out('#a-d', t1 - t0 - 0.3))
    S.append(('sa', t0, t1 - t0, scene('sa', CSS, html, js)))

    # S1 spending: bonus bar shrinks per purchase, then HABIS ------------------------------------
    t0, t1 = c(4) + 0.7, c(10) - 0.15
    icon = lambda svg, lbl, i: (f"<div id='b-i{i}' style='position:absolute;left:{40 + i * 300}px;top:200px;width:280px;height:120px;border-radius:24px;"
                                f"background:#fff;box-shadow:0 10px 24px rgba(11,37,69,.12);display:flex;align-items:center;gap:14px;padding:0 20px;box-sizing:border-box'>"
                                f"{svg}<div style=\"font:800 34px/1.05 'Nunito',sans-serif;color:#0B2545\">{lbl}</div></div>")
    ph = "<svg width='54' height='70' viewBox='0 0 54 70'><rect x='4' y='2' width='46' height='66' rx='9' fill='#0B2545'/><rect x='9' y='9' width='36' height='48' rx='4' fill='#7DD3FC'/></svg>"
    bag = "<svg width='60' height='66' viewBox='0 0 60 66'><path d='M8 20 H52 L48 64 H12Z' fill='#0EA5E9'/><path d='M20 22 V14 a10 10 0 0 1 20 0 V22' fill='none' stroke='#0B2545' stroke-width='5'/></svg>"
    pl = "<svg width='66' height='66' viewBox='0 0 66 66'><path d='M30 6 L36 6 L40 28 L62 38 L62 44 L40 38 L38 54 L46 60 L46 64 L33 60 L20 64 L20 60 L28 54 L26 38 L4 44 L4 38 L26 28Z' fill='#0B2545'/></svg>"
    html = f"""<div id="b-d" class="deck"><div class="lab">BONUS</div>
      <div id="b-bar" style="position:absolute;left:40px;top:84px;width:900px;height:84px;border-radius:24px;background:#e2e8f0;overflow:hidden">
        <div id="b-fill" style="position:absolute;inset:0;border-radius:24px;background:linear-gradient(90deg,#0EA5E9,#7DD3FC);transform-origin:0 50%"></div>
        <div id="b-pct" style="position:absolute;left:28px;top:12px;font:400 54px/60px 'Archivo Black',sans-serif;color:#0B2545">RM10,000</div></div>
      {icon(ph, 'Upgrade<br>handphone', 0)}{icon(bag, 'Shopping', 1)}{icon(pl, 'Travel', 2)}
      <div id="b-h" style="position:absolute;left:0;right:0;top:196px;text-align:center"><span class="kin rd" style="font-size:120px">HABIS.</span></div></div>"""
    js = (deck_in('#b-d', 0.1) + "    tl.set(['#b-i0','#b-i1','#b-i2','#b-h'], {opacity: 0}, 0);\n")
    fill = [1.0, 0.62, 0.34, 0.12]
    for i, w in enumerate(['upgrade', 'shopping', 'travel']):
        tt = T.t(8, w) - t0
        js += (f"    tl.fromTo('#b-i{i}', {{opacity: 0, y: 40, scale: .8}}, {{opacity: 1, y: 0, scale: 1, duration: .4, ease: 'back.out(1.8)'}}, {tt - 0.1:.3f});\n"
               f"    tl.to('#b-fill', {{scaleX: {fill[i + 1]}, duration: .4, ease: 'power3.out'}}, {tt:.3f});\n")
    hb = T.t(9, 'habis') - t0
    js += (f"    tl.to('#b-fill', {{scaleX: 0, duration: .35, ease: 'power3.in'}}, {hb - 0.3:.3f});\n"
           f"    tl.to('#b-pct', {{color: '#EF4444', duration: .2}}, {hb - 0.3:.3f});\n"
           f"    tl.to(['#b-i0','#b-i1','#b-i2'], {{opacity: 0, y: 30, duration: .2, stagger: .04}}, {hb - 0.3:.3f});\n"
           f"    tl.fromTo('#b-h', {{opacity: 0, scale: 1.5}}, {{opacity: 1, scale: 1, duration: .3, ease: 'expo.out'}}, {hb:.3f});\n"
           + blur_out('#b-d', t1 - t0 - 0.3))
    S.append(('sb', t0, t1 - t0, scene('sb', CSS, html, js)))

    # S2 the advice quote ---------------------------------------------------------------------------
    t0, t1 = c(10) - 0.15, c(12) - 0.15
    html = """<div id="c-d" class="deck"><div class="lab">PESAN KAMEK</div>
      <div style="position:absolute;left:30px;top:40px;font:400 220px/1 'Archivo Black',sans-serif;color:#7DD3FC;opacity:.45">&ldquo;</div>
      <div id="c-a" style="position:absolute;left:150px;top:92px;width:800px" class="bd">Bonus tok <span class="sky">sik semestinya</span></div>
      <div id="c-b" style="position:absolute;left:150px;top:166px;width:800px" class="kin">DUIT UNTUK<br><span class="rd">DIHABISKAN</span></div></div>"""
    js = (deck_in('#c-d', 0.1) + "    tl.set(['#c-a','#c-b'], {opacity: 0}, 0);\n" + blur_in('#c-a', T.t(10, 'bonus') - t0 - 0.2)
          + blur_in('#c-b', T.t(11, 'duit') - t0 - 0.2) + blur_out('#c-d', t1 - t0 - 0.3))
    S.append(('sc', t0, t1 - t0, scene('sc', CSS, html, js)))

    # S3 TAKEOVER: bonus donut -> part of it becomes gold (aset) ----------------------------------
    t0, t1 = c(12) - 0.15, c(14) - 0.2
    take.append((c(12) - 0.15, c(15) - 0.3))
    R = 190
    circ = 2 * 3.14159 * R
    html = f"""<div class="desk"></div><div class="lab" style="left:88px;top:212px">BONUS TAHUN TOK</div>
      <svg viewBox="0 0 520 520" style="position:absolute;left:100px;top:270px;width:520px;height:520px">
        <circle cx="260" cy="260" r="{R}" fill="none" stroke="#7DD3FC" stroke-width="80"/>
        <circle id="d-g" cx="260" cy="260" r="{R}" fill="none" stroke="#E9A93A" stroke-width="80" stroke-dasharray="0 {circ:.0f}" transform="rotate(-90 260 260)"/>
        <text x="260" y="250" text-anchor="middle" font-family="Archivo Black" font-size="64" fill="#0B2545">BONUS</text>
        <text id="d-tx" x="260" y="305" text-anchor="middle" font-family="Nunito" font-weight="800" font-size="34" fill="#0EA5E9">jadi peluang</text></svg>
      <div id="d-l1" style="position:absolute;left:650px;top:330px;width:340px"><div class="bd">Peluang tambah</div><div class="kin sky">ASET</div></div>
      <div id="d-l2" style="position:absolute;left:650px;top:540px;width:340px"><div style="display:flex;align-items:center;gap:14px"><div style="width:34px;height:34px;border-radius:8px;background:#E9A93A"></div>
        <div class="bd">Sebahagian</div></div><div class="kin au" style="font-size:70px">SIMPAN EMAS</div></div>"""
    asg = T.t(13, 'asingkan') - t0
    js = ("    tl.set(['#d-l1','#d-l2'], {opacity: 0}, 0);\n" + blur_in('#d-l1', T.t(12, 'aset') - t0 - 0.4) +
          f"    tl.to('#d-g', {{attr: {{'stroke-dasharray': '{circ * 0.3:.0f} {circ:.0f}'}}, duration: 1.0, ease: 'power3.inOut'}}, {asg:.3f});\n"
          + blur_in('#d-l2', T.t(13, 'simpan') - t0 - 0.2))
    S.append(('sd', t0, t1 - t0, scene('sd', CSS, html, js)))

    # S4 TAKEOVER: two ways -- GAP account (real app, blurred) and physical gold bar -------------
    t0, t1 = c(14) - 0.2, c(15) - 0.3
    html = """<div class="desk"></div><div class="lab" style="left:88px;top:212px">CARA KUMPUL EMAS</div>
      <div id="e-p" style="position:absolute;left:96px;top:262px;width:470px;height:480px;border-radius:44px;background:#0b0b0b;box-shadow:0 30px 60px rgba(11,37,69,.3)">
        <div style="position:absolute;left:12px;top:12px;right:12px;bottom:0;border-radius:34px 34px 0 0;overflow:hidden;background:#fff6c9">
          <img src="assets/gap_app.jpg" style="position:absolute;left:0;top:30px;width:446px">
          <div style="position:absolute;left:0;top:0;width:446px;height:32px;background:#F8DD5A"></div>
          <div style="position:absolute;left:173px;top:8px;width:100px;height:22px;border-radius:12px;background:#111"></div></div>
        <div style="position:absolute;left:0;right:0;bottom:-2px;height:100px;background:linear-gradient(180deg,rgba(246,251,255,0),#f2f9ff);border-radius:0 0 44px 44px"></div></div>
      <div id="e-pl" style="position:absolute;left:96px;top:752px;width:470px;text-align:center" class="bd">Akaun <span class="sky">GAP</span></div>
      <div id="e-or" style="position:absolute;left:592px;top:470px;font:700 30px 'Space Mono',monospace;color:#7a8ba3">ATAU</div>
      <img id="e-b" src="assets/goldbar_100g.png" style="position:absolute;left:705px;top:330px;width:250px">
      <div id="e-bl" style="position:absolute;left:670px;top:752px;width:320px;text-align:center" class="bd">Gold bar <span class="au">fizikal</span></div>"""
    js = ("    tl.set(['#e-p','#e-pl','#e-or','#e-b','#e-bl'], {opacity: 0}, 0);\n"
          f"    tl.fromTo('#e-p', {{opacity: 0, y: 120, rotationX: 25, transformPerspective: 1100}}, {{opacity: 1, y: 0, rotationX: 0, duration: .8, ease: 'expo.out'}}, {T.t(14, 'akaun') - t0 - 0.3:.3f});\n"
          + blur_in('#e-pl', T.t(14, 'GAP') - t0) + blur_in('#e-or', T.t(14, 'ataupun') - t0 - 0.1) +
          f"    tl.fromTo('#e-b', {{opacity: 0, y: -160, rotation: -12}}, {{opacity: 1, y: 0, rotation: 4, duration: .7, ease: 'bounce.out'}}, {T.t(14, 'beli') - t0:.3f});\n"
          + blur_in('#e-bl', T.t(14, 'gold') - t0 + 0.1))
    S.append(('se', t0, t1 - t0, scene('se', CSS, html, js)))

    # S5 FULL: she holds the real bars -- label only ----------------------------------------------
    t0, t1 = c(15) - 0.3, c(16) - 0.2
    html = """<div id="f-d" class="deck" style="height:200px"><div class="lab">MACAM TOK</div>
      <div style="position:absolute;left:38px;top:84px;font-size:76px;white-space:nowrap" class="kin">GOLD BAR <span class="au">FIZIKAL</span></div></div>
      <div id="f-k" style="position:absolute;left:50px;top:400px;padding:14px 26px;border-radius:999px;background:#0B2545;color:#7DD3FC;font:800 38px 'Nunito',sans-serif">ikut kemampuan</div>"""
    js = (deck_in('#f-d', 0.2) + "    tl.set('#f-k', {opacity: 0}, 0);\n" + pop_in('#f-k', T.t(15, 'kemampuan') - t0 - 0.2) + blur_out('#f-d', t1 - t0 - 0.3)
          + blur_out('#f-k', t1 - t0 - 0.3))
    S.append(('sf', t0, t1 - t0, scene('sf', CSS, html, js)))

    # S6 TAKEOVER: grams stacking year after year (5 / 10 years), then price wave with long-term rise
    t0, t1 = c(16) - 0.2, c(25) - 0.2
    take.append((c(16) - 0.2, c(25) - 0.35))
    bars = ''.join(f"<div class='yb' id='g-b{i}' style='left:{120 + i * 82}px;top:{760 - (i + 1) * 46}px;height:{(i + 1) * 46}px'></div>"
                   f"<div class='yl' style='left:{120 + i * 82}px'>{i + 1}</div>" for i in range(10))
    html = f"""<div class="desk"></div><div class="lab" style="left:88px;top:212px">EMAS SETIAP TAHUN</div><div class="ill" style="left:470px;right:auto;top:205px">ILUSTRASI</div>
      <div id="g-a">{bars}
        <div id="g-m5" class="mk" style="left:{120 + 4 * 82 - 40}px;top:{760 - 5 * 46 - 80}px">5 TAHUN</div>
        <div id="g-m10" class="mk" style="left:{120 + 9 * 82 - 60}px;top:{760 - 10 * 46 - 80}px">10 TAHUN</div>
        <div style="position:absolute;left:930px;top:770px;font:700 28px 'Space Mono',monospace;color:#7a8ba3">THN</div>
        <div id="g-q" style="position:absolute;left:96px;top:290px;width:420px" class="bd">Berapa banyak <span class="au">gram</span> dah kitak boleh kumpul?</div></div>
      <div id="g-c"><svg viewBox="0 0 900 460" style="position:absolute;left:90px;top:300px;width:900px;height:460px">
          <polyline id="g-p" points="0,400 70,360 120,390 190,300 250,340 320,260 380,300 450,220 510,270 580,180 640,230 720,140 780,170 860,70"
            fill="none" stroke="#0B2545" stroke-width="8" stroke-linejoin="round" pathLength="100" stroke-dasharray="100 120" stroke-dashoffset="110"/>
          <line id="g-tr" x1="0" y1="420" x2="870" y2="60" stroke="#0EA5E9" stroke-width="7" stroke-dasharray="20 14"/>
          <polygon id="g-ah" points="870,60 830,62 852,92" fill="#0EA5E9"/></svg>
        <div id="g-nt" style="position:absolute;left:96px;top:280px" class="bd">Ada <span class="sky">naik</span>, ada <span class="rd">turun</span></div>
        <div id="g-lt" style="position:absolute;left:96px;top:280px" class="bd">Jangka masa <span class="sky">panjang</span></div></div>
      <div id="g-s1" class="side"><div class="kin" style="font-size:64px">5 atau <span class="sky">10</span> tahun</div></div>
      <div id="g-s2" class="side"><div class="bd">Simpanan untuk</div><div class="kin sky" style="font-size:70px">MASA DEPAN</div></div>"""
    css = CSS + """
    .yb { position: absolute; width: 62px; border-radius: 12px 12px 4px 4px; transform-origin: 50% 100%;
          background: linear-gradient(180deg, #F6CD6B, #D99A22); box-shadow: inset 0 2px 0 rgba(255,255,255,.6); }
    .yl { position: absolute; top: 770px; width: 62px; text-align: center; font: 700 28px 'Space Mono', monospace; color: #0B2545; }
    .mk { position: absolute; padding: 8px 16px; border-radius: 12px; background: #0B2545; color: #7DD3FC; font: 700 28px 'Space Mono', monospace; white-space: nowrap; }"""
    st = T.t(16, 'setiap') - t0
    y5 = T.t(20, 'lima') - t0
    y10 = T.t(20, 'sepuluh') - t0
    nk = T.cue(22) - t0
    lp = T.t(23, 'panjang') - t0
    md = T.t(24, 'masa') - t0
    js = ("    tl.set(['#g-m5','#g-m10','#g-q','#g-c','#g-s1','#g-s2','#g-nt','#g-lt','#g-tr','#g-ah'], {opacity: 0}, 0);\n"
          "    tl.set('.yb', {scaleY: 0}, 0);\n")
    for i in range(10):
        js += f"    tl.to('#g-b{i}', {{scaleY: 1, duration: .4, ease: 'back.out(1.5)'}}, {st + i * 0.28:.3f});\n"
    js += (pop_in('#g-m5', y5) + pop_in('#g-m10', y10) + blur_in('#g-s1', y5 - 0.2) + blur_in('#g-q', T.t(20, 'berapa') - t0 - 0.2)
           + f"    tl.to('#g-a', {{opacity: 0, y: -30, filter: 'blur(10px)', duration: .3, ease: 'power2.in'}}, {nk - 0.35:.3f});\n"
           + blur_out('#g-s1', nk - 0.35) +
           f"    tl.to('#g-c', {{opacity: 1, duration: .3}}, {nk - 0.1:.3f});\n" + blur_in('#g-nt', nk) +
           f"    tl.fromTo('#g-p', {{attr: {{'stroke-dashoffset': 110}}}}, {{attr: {{'stroke-dashoffset': 0}}, duration: 2.6, ease: 'power1.inOut'}}, {nk:.3f});\n"
           + swap('#g-nt', '#g-lt', lp - 0.4) +
           f"    tl.fromTo('#g-tr', {{opacity: 1, attr: {{x2: 0, y2: 420}}}}, {{attr: {{x2: 870, y2: 60}}, duration: 1.0, ease: 'power2.inOut'}}, {lp:.3f});\n"
           f"    tl.to('#g-ah', {{opacity: 1, duration: .2}}, {lp + 0.95:.3f});\n" + blur_in('#g-s2', md - 0.3))
    S.append(('sg', t0, t1 - t0, scene('sg', css, html, js)))

    # S7 FULL: don't wait until it's gone -----------------------------------------------------------
    t0, t1 = c(25) - 0.2, c(27) - 0.25
    html = """<div id="h-d" class="deck"><div class="lab">BONUS HUJUNG TAHUN TOK</div>
      <svg id="h-hg" viewBox="0 0 120 180" style="position:absolute;right:50px;top:90px;width:150px;height:225px">
        <path d="M10 6 H110 M10 174 H110" stroke="#0B2545" stroke-width="10" stroke-linecap="round"/>
        <path d="M20 10 C20 70 100 80 100 90 C100 100 20 110 20 170 M100 10 C100 70 20 80 20 90 C20 100 100 110 100 170" fill="none" stroke="#0B2545" stroke-width="6"/>
        <path id="h-top" d="M28 18 H92 C90 50 62 72 60 84 C58 72 30 50 28 18Z" fill="#E9A93A"/>
        <path id="h-bot" d="M30 168 H90 C88 140 64 128 60 112 C56 128 32 140 30 168Z" fill="#E9A93A"/></svg>
      <div id="h-a" style="position:absolute;left:38px;top:86px;width:760px;font-size:74px;white-space:nowrap" class="kin">JANGAN TUNGGU<br><span class="rd">DUIT YA HABIS</span></div>
      <div id="h-b" style="position:absolute;left:38px;top:262px" class="bd">baru mok fikir pasal <span class="sky">simpanan</span></div></div>"""
    js = (deck_in('#h-d', 0.1) + "    tl.set(['#h-a','#h-b'], {opacity: 0}, 0);\n"
          "    tl.fromTo('#h-top', {scaleY: 1, transformOrigin: '50% 100%'}, {scaleY: .1, duration: 5, ease: 'none'}, .3);\n"
          "    tl.fromTo('#h-bot', {scaleY: .1, transformOrigin: '50% 100%'}, {scaleY: 1, duration: 5, ease: 'none'}, .3);\n"
          + blur_in('#h-a', T.t(25, 'jangan') - t0 - 0.2) + blur_in('#h-b', T.t(26, 'fikir') - t0 - 0.3) + blur_out('#h-d', t1 - t0 - 0.3))
    S.append(('sh', t0, t1 - t0, scene('sh', CSS, html, js)))

    # S8 TAKEOVER CTA: type "BONUS" in a comment box ------------------------------------------------
    t0, t1 = c(27) - 0.25, total
    take.append((c(27) - 0.25, total + 1))
    html = """<div class="desk"></div><div class="lab" style="left:88px;top:212px">KOMEN SEKARANG</div>
      <div id="i-h" style="position:absolute;left:96px;top:270px;width:880px;font-size:66px;line-height:1.05" class="kin">KAMEK BANTU KITAK<br><span class="sky">RANCANG</span> SIMPANAN EMAS</div>
      <div id="i-box" style="position:absolute;left:96px;top:560px;width:880px;height:120px;border-radius:60px;background:#fff;box-shadow:0 14px 34px rgba(11,37,69,.15);
           display:flex;align-items:center;padding:0 34px;box-sizing:border-box;gap:18px">
        <div style="width:72px;height:72px;border-radius:50%;background:#0B2545;display:flex;align-items:center;justify-content:center"><img src="assets/logo_white.png" style="width:62px"></div>
        <div id="i-ty" style="font:900 52px 'Nunito',sans-serif;color:#0B2545;letter-spacing:2px"></div><div id="i-cr" style="width:4px;height:54px;background:#0EA5E9"></div>
        <div id="i-send" style="margin-left:auto;width:84px;height:84px;border-radius:50%;background:#0EA5E9;color:#fff;font:900 44px/84px 'Nunito',sans-serif;text-align:center">&#10148;</div></div>
      <div id="i-ok" style="position:absolute;left:96px;top:710px;padding:12px 26px;border-radius:999px;background:#0B2545;color:#7DD3FC;font:800 36px 'Nunito',sans-serif">ikut bajet kitak &#10003;</div>"""
    kb = T.t(27, 'BONUS') - t0
    js = ("    tl.set(['#i-h','#i-box','#i-ok'], {opacity: 0}, 0);\n" + blur_in('#i-h', 0.45) +
          f"    tl.fromTo('#i-box', {{opacity: 0, y: 60}}, {{opacity: 1, y: 0, duration: .5, ease: 'expo.out'}}, {kb - 0.7:.3f});\n")
    for k, ch in enumerate('BONUS'):
        js += f"    tl.set('#i-ty', {{textContent: '{'BONUS'[:k + 1]}'}}, {kb - 0.1 + k * 0.08:.3f});\n"
    js += (f"    tl.to('#i-send', {{scale: .85, duration: .08, yoyo: true, repeat: 1}}, {kb + 0.6:.3f});\n"
           f"    tl.to('#i-send', {{background: '#22C55E', duration: .2}}, {kb + 0.7:.3f});\n"
           + pop_in('#i-ok', T.t(27, 'bajet') - t0 - 0.2))
    for k in range(8):
        js += f"    tl.set('#i-cr', {{opacity: {k % 2}}}, {kb - 0.6 + k * 0.4:.3f});\n"
    S.append(('si', t0, t1 - t0, scene('si', CSS, html, js)))
    return S, take


KEYWORDS = {'bonus', 'rm10,000', 'sik', 'habis', 'aset', 'emas', 'gap', 'public', 'gold', 'bar', 'konsisten', 'gram',
            'simpanan', 'upgrade', 'handphone', 'shopping', 'travel', 'sebulan', 'fizikal', 'lima', 'sepuluh', 'naik', 'turun',
            'panjang', 'depan', 'jangan', 'komen', 'bajet', 'dihabiskan', 'peluang', 'kemampuan', 'simpan'}


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
        js.append(f"    tl.fromTo('#cg{gi} .cin', {{y: 16, opacity: 0}}, {{y: 0, opacity: 1, duration: .14, ease: 'power3.out'}}, {a:.3f});")
        for k, w in enumerate(g):
            js.append(f"    tl.fromTo('#cw{gi}_{k}', {{scale: 1.08}}, {{scale: 1, duration: .18, ease: 'power2.out', immediateRender: false}}, {w['os']:.3f});")
        js.append(f"    tl.set('#cg{gi}', {{opacity: 0, visibility: 'hidden'}}, {b:.3f});")
    css = """
    .cg { position: absolute; left: 40px; width: 900px; top: 1236px; text-align: center; opacity: 0; visibility: hidden; }
    .cin { display: inline-block; padding: 8px 20px 10px; border-radius: 18px; background: rgba(11,37,69,.80);
           font: 900 50px/1.18 'Nunito', sans-serif; color: #FFFFFF; text-shadow: 0 2px 8px rgba(0,0,0,.35); }
    .cin span { display: inline-block; margin: 0 .2em; transform-origin: 50% 70%; }
    .cin .kw { color: #7DD3FC; }"""
    return scene('captions', css, '\n'.join(html), '\n'.join(js))


def outro_scene():
    css = """
    #o-bg { position: absolute; inset: 0; background: linear-gradient(170deg, #F4FAFF 0%, #DCEFFF 60%, #BFE3FF 100%); }
    #o-c { position: absolute; left: 290px; top: 620px; width: 500px; height: 500px; border-radius: 50%; background: radial-gradient(circle, #fff 0%, rgba(255,255,255,0) 70%); }
    #o-logo { position: absolute; left: 340px; top: 660px; width: 400px; }
    #o-t { position: absolute; left: 0; width: 1080px; top: 1120px; text-align: center; font: 700 30px 'Space Mono', monospace; letter-spacing: 8px; color: #0EA5E9; }"""
    html = """<div id="o-bg"></div><div id="o-c"></div><img id="o-logo" src="assets/logo.png"><div id="o-t">AZLAN &amp; EZA</div>"""
    js = ("    tl.fromTo('#o-bg', {opacity: 0}, {opacity: 1, duration: .35}, 0);\n"
          "    tl.fromTo('#o-logo', {opacity: 0, y: 40, scale: .9}, {opacity: 1, y: 0, scale: 1, duration: .7, ease: 'expo.out'}, .25);\n"
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
                ('15', 'gap', 'gap_app.jpg'), ('13', 'gold', 'goldbar_100g.png')):
        shutil.copy(os.path.join(REPO, 'work', *src), a)
    for f in ('whoosh', 'whoosh-short', 'whoosh-cinematic', 'pop', 'click-soft', 'click', 'sparkle', 'impact-bass-1',
              'impact-bass-2', 'riser', 'ping', 'key-press', 'notification'):
        shutil.copy(os.path.join(SFX_DIR, f + '.mp3'), os.path.join(a, f'sfx-{f}.mp3'))
    dur = round(total + OUTRO, 3)
    # the acoustic track is 91.6 s: start at its strongest section and loop with a crossfade if needed
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(MUSIC_SS), '-i', MUSIC_SRC, '-i', MUSIC_SRC, '-filter_complex',
                    '[0:a][1:a]acrossfade=d=3:c1=tri:c2=tri[m]', '-map', '[m]', '-t', str(dur + 1), '-c:a', 'aac', '-b:a', '192k',
                    os.path.join(a, 'music-bed.m4a')], check=True)
    scenes, take = build(T, total)
    merged = []
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
    sfx = [('impact-bass-1', 0.02, .5), ('notification', 0.15, .35), ('whoosh-short', T.t(2, 'sebulan') - 0.1, .4),
           ('pop', c(3) - 0.02, .5)]
    for i, d in enumerate([c(4) + 0.8, c(10), c(15), c(25)]):
        sfx.append((['whoosh-short', 'whoosh'][i % 2], d - 0.05, .35))
    for i, (a0, b0) in enumerate(take):
        sfx.append((['whoosh-cinematic', 'whoosh'][i % 2], a0 - 0.1, .5))
        if b0 < total:
            sfx.append(('whoosh-short', b0 - 0.05, .35))
    sfx += [('pop', T.t(8, 'upgrade') - 0.1, .4), ('pop', T.t(8, 'shopping') - 0.1, .4), ('pop', T.t(8, 'travel') - 0.1, .4),
            ('impact-bass-2', T.t(9, 'habis') - 0.35, .45), ('click-soft', T.t(11, 'duit') - 0.2, .6),
            ('ping', T.t(12, 'aset') - 0.4, .3), ('sparkle', T.t(13, 'asingkan'), .4),
            ('pop', T.t(14, 'GAP'), .4), ('impact-bass-1', T.t(14, 'beli') + 0.25, .35), ('sparkle', T.t(15, 'fizikal'), .4),
            ('riser', T.t(20, 'lima') - 2.0, .25), ('pop', T.t(20, 'lima'), .45), ('pop', T.t(20, 'sepuluh'), .45),
            ('whoosh-short', T.t(23, 'panjang'), .35), ('sparkle', T.t(24, 'masa') - 0.2, .35),
            ('click', T.t(27, 'BONUS') + 0.6, .8), ('ping', T.t(27, 'bajet') - 0.2, .3), ('whoosh-cinematic', total - 0.1, .45)]
    for k in range(5):
        sfx.append(('key-press', T.t(27, 'BONUS') - 0.1 + k * 0.08, .3))
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

    cx, cy = CARD['x'] + CARD['w'] / 2, CARD['y'] + CARD['h'] / 2
    sw, sh = CARD['w'] / SCALE, CARD['h'] / SCALE
    ins = (FACE_Y - sh / 2, W - (FACE_X + sw / 2), H - (FACE_Y + sh / 2), FACE_X - sw / 2, 40 / SCALE)
    cam = [f"    tl.set('#punch', {{scale: {s}}}, {t:.3f});" for t, s in
           [(0.0, 1.06), (c(2) - 0.03, 1.0), (c(3) - 0.03, 1.1), (c(4) - 0.03, 1.0), (c(9) - 0.03, 1.07), (c(10) - 0.03, 1.0),
            (c(15) - 0.03, 1.08), (c(16) - 0.03, 1.0), (c(26) - 0.03, 1.06), (c(27) - 0.03, 1.0)]]
    for a0, b0 in take:
        cam += [f"    tl.to('#cam', {{scale: {SCALE}, x: {cx - FACE_X:.0f}, y: {cy - FACE_Y:.0f}, duration: .7, ease: 'power3.inOut'}}, {a0:.3f});",
                f"    tl.to('#camclip', {{'--t': '{ins[0]:.0f}px', '--r': '{ins[1]:.0f}px', '--b': '{ins[2]:.0f}px', '--l': '{ins[3]:.0f}px', '--rad': '{ins[4]:.0f}px', duration: .7, ease: 'power3.inOut'}}, {a0:.3f});",
                f"    tl.to('#frame', {{opacity: 1, scale: 1, duration: .45, ease: 'back.out(1.6)'}}, {a0 + 0.45:.3f});",
                f"    tl.to('#skybg', {{opacity: 1, duration: .5, ease: 'power2.out'}}, {a0 + 0.05:.3f});",
                f"    tl.to('#capwrap', {{y: {CAP_LIFT}, duration: .6, ease: 'power3.inOut'}}, {a0 + 0.1:.3f});"]
        if b0 < total:
            cam += [f"    tl.to('#cam', {{scale: 1, x: 0, y: 0, duration: .6, ease: 'power3.inOut'}}, {b0:.3f});",
                    f"    tl.to('#camclip', {{'--t': '0px', '--r': '0px', '--b': '0px', '--l': '0px', '--rad': '0px', duration: .6, ease: 'power3.inOut'}}, {b0:.3f});",
                    f"    tl.to('#frame', {{opacity: 0, scale: .95, duration: .25}}, {b0:.3f});",
                    f"    tl.to('#skybg', {{opacity: 0, duration: .4}}, {b0 + 0.25:.3f});",
                    f"    tl.to('#capwrap', {{y: 0, duration: .55, ease: 'power3.inOut'}}, {b0:.3f});"]
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
    html, body {{ margin: 0; padding: 0; background: #EAF5FF; }}
    #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: #EAF5FF; }}
    #skybg {{ position: absolute; inset: 0; opacity: 0; z-index: 1;
             background: radial-gradient(70% 45% at 30% 20%, #FFFFFF 0%, rgba(255,255,255,0) 70%), linear-gradient(170deg, #F4FAFF 0%, #DCEFFF 55%, #BFE3FF 100%); }}
    #skybg::after {{ content: ''; position: absolute; inset: 0; opacity: .5;
             background-image: radial-gradient(rgba(14,165,233,.18) 2px, transparent 2px); background-size: 44px 44px; }}
    #cam {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; z-index: 5; transform-origin: {FACE_X}px {FACE_Y}px; }}
    #camclip {{ position: absolute; inset: 0; --t: 0px; --r: 0px; --b: 0px; --l: 0px; --rad: 0px;
               clip-path: inset(var(--t) var(--r) var(--b) var(--l) round var(--rad)); overflow: hidden; }}
    #punch {{ position: absolute; inset: 0; transform-origin: 540px 900px; }}
    #base {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
    #frame {{ position: absolute; left: {CARD['x'] - 9}px; top: {CARD['y'] - 9}px; width: {CARD['w'] + 18}px; height: {CARD['h'] + 18}px;
             border-radius: 46px; border: 9px solid #FFFFFF; box-sizing: border-box; z-index: 6; opacity: 0;
             box-shadow: 0 24px 50px rgba(11,37,69,.28), 0 0 0 3px rgba(14,165,233,.35); }}
    #capwrap {{ position: absolute; inset: 0; z-index: 30; }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="{W}" data-height="{H}">
    <div id="skybg"></div>
    <div id="cam"><div id="camclip"><div id="punch">
      <video id="base" class="clip" src="assets/base.mp4" data-start="0" data-duration="{total:.3f}" data-track-index="0"
             data-has-audio="true" data-volume="1" playsinline></video>
    </div></div></div>
    <div id="frame"></div>
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
    tl.set('#frame', {{scale: .95}}, 0);
{chr(10).join(cam)}
    tl.set({{}}, {{}}, {dur});
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
"""
    open(os.path.join(proj, 'index.html'), 'w').write(index)
    return scenes, take
