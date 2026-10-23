"""Small 3D toolkit for the Azlan & Eza shorts (no Blender/OpenGL needed).

- warp3d(sprite, rx, ry, rz)        : perspective-rotate any RGBA sprite (3D card flips/tilts)
- extrude_text(...)                 : 3D extruded title text with depth and a soft shadow
- render_bar / render_coin(...)     : lit, shaded 3D gold bar / coin meshes (painter's algorithm, 2x SSAA)
All angles in degrees. Camera looks down -z from z=+dist.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

GOLD_BASE = np.array([222, 172, 64], float)
GOLD_LIGHT = np.array([255, 226, 140], float)


# ---------------------------------------------------------------- math
def rot(rx, ry, rz):
    a, b, c = (math.radians(v) for v in (rx, ry, rz))
    Rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    Ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return Rx @ Ry @ Rz      # spin (y) first, then tilt (x): objects turn on a level turntable


def project(P, dist, f):
    z = dist - P[:, 2]
    return np.stack([P[:, 0] * f / z, -P[:, 1] * f / z], 1)


def _persp_coeffs(dst, src):
    """Coefficients for PIL PERSPECTIVE: maps output (dst) points to input (src) points."""
    A, Bv = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); Bv.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); Bv.append(v)
    return np.linalg.solve(np.array(A, float), np.array(Bv, float)).tolist()


# ---------------------------------------------------------------- card warp
def warp3d(sprite, rx=0.0, ry=0.0, rz=0.0, dist=2200.0, shade=True):
    """Rotate a flat RGBA sprite in 3D around its centre and project with perspective."""
    w, h = sprite.size
    if abs(rx) < 0.01 and abs(ry) < 0.01 and abs(rz) < 0.01:
        return sprite
    R = rot(rx, ry, rz)
    corners = np.array([[-w / 2, h / 2, 0], [w / 2, h / 2, 0], [w / 2, -h / 2, 0], [-w / 2, -h / 2, 0]], float) @ R.T
    if (R @ np.array([0, 0, 1.0]))[2] <= 0.02:          # seen edge-on / from behind
        return Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    pts = project(corners, dist, dist)
    mn = pts.min(0)
    pts = pts - mn
    ow, oh = int(math.ceil(pts[:, 0].max())) + 2, int(math.ceil(pts[:, 1].max())) + 2
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    out = sprite.transform((ow, oh), Image.PERSPECTIVE, _persp_coeffs(pts.tolist(), src), Image.BICUBIC)
    if shade:
        k = (R @ np.array([0, 0, 1.0]))[2]                 # darker as it turns away
        if k < 0.98:
            dark = Image.new('RGBA', out.size, (0, 0, 0, int(110 * (1 - k))))
            dark.putalpha(Image.fromarray((np.asarray(out.getchannel('A')) * (1 - k) * 0.45).astype(np.uint8)))
            out.alpha_composite(dark)
    return out


def flip_in(sprite, k, axis='y', amount=80):
    """3D flip-in: k 0->1 rotates the card from `amount` degrees to flat."""
    a = amount * (1 - k)
    return warp3d(sprite, rx=a if axis == 'x' else 0, ry=a if axis == 'y' else 0)


# ---------------------------------------------------------------- extruded text
def extrude_text(text, size, font_path, top=(255, 235, 160), bot=(232, 180, 70), side=(120, 80, 20),
                 depth=16, dx=0.55, dy=1.0, outline=(60, 40, 10)):
    f = ImageFont.truetype(font_path, size)
    bb = f.getbbox(text, stroke_width=4)
    pad = depth + 30
    tw, th = bb[2] - bb[0] + pad * 2, bb[3] - bb[1] + pad * 2
    org = (pad - bb[0], pad - bb[1])
    mask = Image.new('L', (tw, th), 0)
    ImageDraw.Draw(mask).text(org, text, font=f, fill=255, stroke_width=4, stroke_fill=255)
    out = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    # soft drop shadow
    sh = mask.filter(ImageFilter.GaussianBlur(size * 0.08)).point(lambda v: int(v * 0.55))
    shimg = Image.new('RGBA', (tw, th), (0, 0, 0, 255)); shimg.putalpha(sh)
    out.alpha_composite(shimg, (int(depth * dx) + 6, int(depth * dy) + 10))
    # extrusion: stacked layers from back to front, darker at the back
    for i in range(depth, 0, -1):
        t = i / depth
        col = tuple(int(side[c] * (1 - 0.35 * t)) for c in range(3))
        layer = Image.new('RGBA', (tw, th), col + (255,)); layer.putalpha(mask)
        out.alpha_composite(layer, (int(i * dx), int(i * dy)))
    # front face with vertical gradient + thin outline
    face_mask = Image.new('L', (tw, th), 0)
    ImageDraw.Draw(face_mask).text(org, text, font=f, fill=255)
    ol = Image.new('RGBA', (tw, th), outline + (255,)); ol.putalpha(mask)
    out.alpha_composite(ol)
    g = np.zeros((th, tw, 4), np.uint8)
    ys = np.clip((np.arange(th) - pad) / max(1, th - 2 * pad), 0, 1)[:, None]
    for c in range(3):
        g[..., c] = (top[c] * (1 - ys) + bot[c] * ys).astype(np.uint8)
    g[..., 3] = 255
    face = Image.fromarray(g); face.putalpha(face_mask)
    out.alpha_composite(face)
    return out


# ---------------------------------------------------------------- meshes
def _shade(base, n, light, view=np.array([0, 0, 1.0]), spec_pow=40, spec=0.45, amb=0.45):
    lam = max(0.0, float(n @ light))
    hv = light + view; hv /= np.linalg.norm(hv)
    s = max(0.0, float(n @ hv)) ** spec_pow
    c = base * (amb + (1 - amb) * lam) + 255 * spec * s
    return tuple(int(v) for v in np.clip(c, 0, 255))


def _render(faces, rx, ry, rz, size, scale, dist=9.0, light=(-0.35, 0.8, 0.75), textures=()):
    """faces: list of (verts Nx3, base_rgb). textures: list of (face_index, RGBA image, uv quad corner order)."""
    S = 2
    W = H = size * S
    R = rot(rx, ry, rz)
    L = np.array(light, float); L /= np.linalg.norm(L)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = scale * W * dist      # world unit -> fraction of the image width
    items = []
    for idx, (V, base) in enumerate(faces):
        P = np.asarray(V, float) @ R.T
        n = np.cross(P[1] - P[0], P[2] - P[0])
        nn = np.linalg.norm(n)
        if nn < 1e-9:
            continue
        n /= nn
        cen = P.mean(0)
        if n @ cen < 0:            # convex meshes: make every normal point outward
            n = -n
        to_cam = np.array([0, 0, dist]) - cen
        if n @ to_cam <= 0:
            continue
        items.append((cen[2], idx, P, n, base))
    items.sort(key=lambda it: it[0])
    tex = {i: (t, ) for i, t in textures}
    for _, idx, P, n, base in items:
        q = project(P, dist, f) + np.array([W / 2, H / 2])
        d.polygon([tuple(p) for p in q], fill=_shade(np.asarray(base, float), n, L) + (255,))
        if idx in tex:
            t = tex[idx][0]
            corners = q[:4]
            tw, th = t.size
            warped = t.transform((W, H), Image.PERSPECTIVE,
                                 _persp_coeffs(corners.tolist(), [(0, 0), (tw, 0), (tw, th), (0, th)]), Image.BICUBIC)
            img.alpha_composite(warped)
    return img.resize((size, size), Image.LANCZOS)


def bar_faces(w=2.0, d=1.0, h=0.55, inset=0.18):
    x, z, y = w / 2, d / 2, h / 2
    xi, zi = x - inset, z - inset * 0.8
    B = [(-x, -y, z), (x, -y, z), (x, -y, -z), (-x, -y, -z)]
    T = [(-xi, y, zi), (xi, y, zi), (xi, y, -zi), (-xi, y, -zi)]
    g = GOLD_BASE
    return [
        ([T[3], T[2], T[1], T[0]], g * 1.05),           # top (index 0) - texture goes here
        ([B[0], B[1], T[1], T[0]], g),                  # front
        ([B[1], B[2], T[2], T[1]], g * 0.95),           # right
        ([B[2], B[3], T[3], T[2]], g),                  # back
        ([B[3], B[0], T[0], T[3]], g * 0.95),           # left
        ([B[3], B[2], B[1], B[0]], g * 0.8),            # bottom
    ]


def bar_texture(label='999.9', sub='FINE GOLD', w=400, h=200, font_path=None):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([10, 10, w - 10, h - 10], 16, outline=(150, 105, 25, 200), width=5)
    if font_path:
        dr.text((w / 2, h * 0.42), label, font=ImageFont.truetype(font_path, int(h * 0.30)), fill=(140, 95, 20, 230), anchor='mm')
        dr.text((w / 2, h * 0.74), sub, font=ImageFont.truetype(font_path, int(h * 0.15)), fill=(140, 95, 20, 210), anchor='mm')
    return im


def render_bar(ry, rx=24.0, rz=0.0, size=520, scale=0.30, texture=None):
    faces = bar_faces()
    # top face corners must be listed in texture order (tl, tr, br, bl) as seen from above-front
    return _render(faces, rx, ry, rz, size, scale, textures=[(0, texture)] if texture is not None else [])


def coin_faces(r=1.0, t=0.14, n=48):
    ang = np.linspace(0, 2 * math.pi, n, endpoint=False)
    front = [(r * math.cos(a), r * math.sin(a), t / 2) for a in ang]
    back = [(r * math.cos(a), r * math.sin(a), -t / 2) for a in ang][::-1]
    faces = [(front, GOLD_BASE * 1.05), (back, GOLD_BASE * 0.95)]
    for i in range(n):
        a0, a1 = ang[i], ang[(i + 1) % n]
        faces.append(([(r * math.cos(a0), r * math.sin(a0), -t / 2), (r * math.cos(a1), r * math.sin(a1), -t / 2),
                       (r * math.cos(a1), r * math.sin(a1), t / 2), (r * math.cos(a0), r * math.sin(a0), t / 2)],
                      GOLD_BASE * 0.85))
    # inner raised ring on the front face (gives the coin a minted look)
    ri = r * 0.82
    faces.append(([(ri * math.cos(a), ri * math.sin(a), t / 2 + 0.01) for a in ang], GOLD_LIGHT * 0.92))
    return faces


def render_coin(ry, rx=0.0, rz=0.0, size=360, scale=0.32, label=None, font_path=None):
    img = _render(coin_faces(), rx, ry, rz, size, scale)
    if label and font_path:
        # stamp the label onto the coin face with the same rotation
        lab = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
        ImageDraw.Draw(lab).text((200, 200), label, font=ImageFont.truetype(font_path, 120), fill=(140, 95, 20, 235), anchor='mm')
        R = rot(rx, ry, rz)
        if (R @ np.array([0, 0, 1.0]))[2] > 0.15:
            lab = lab.resize((int(size * 0.62), int(size * 0.62)), Image.LANCZOS)
            w = warp3d(lab, rx, ry, rz, dist=size * 4.2, shade=False)
            img.alpha_composite(w, (int(size / 2 - w.width / 2), int(size / 2 - w.height / 2)))
    return img
