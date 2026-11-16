#!/usr/bin/env python3
"""Cut the Public Gold 100 g bar out of the user's photo (work/13/gold/src.png) -> goldbar_100g.png (RGBA).
GrabCut seeded with the bar's four corners; the left edge touches a satin cloth, so pixels beyond the bar's
left edge line are cleared to keep that edge straight."""
import sys
import cv2
import numpy as np
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
im = cv2.imread(src)
H, W = im.shape[:2]
poly = np.array([(170, 960), (790, 820), (1050, 1774), (410, 1920)], float)   # TL, TR, BR, BL in the photo


def grow(p, d):
    c = p.mean(0)
    return np.array([v + (v - c) / np.linalg.norm(v - c) * d for v in p], np.int32)


mask = np.full((H, W), cv2.GC_BGD, np.uint8)
cv2.fillPoly(mask, [grow(poly, 60)], cv2.GC_PR_BGD)
cv2.fillPoly(mask, [grow(poly, 0)], cv2.GC_PR_FGD)
cv2.fillPoly(mask, [grow(poly, -45)], cv2.GC_FGD)
cv2.grabCut(im, mask, None, np.zeros((1, 65)), np.zeros((1, 65)), 6, cv2.GC_INIT_WITH_MASK)
a = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)

p0, p1 = poly[0], poly[3]
u = (p1 - p0) / np.linalg.norm(p1 - p0)
nrm = np.array([u[1], -u[0]])
yy, xx = np.mgrid[0:H, 0:W]
a[((xx - p0[0]) * nrm[0] + (yy - p0[1]) * nrm[1]) < -3] = 0

n, lab, st, _ = cv2.connectedComponentsWithStats(a)
a = np.where(lab == 1 + np.argmax(st[1:, 4]), 255, 0).astype(np.uint8)
cnts, _ = cv2.findContours(a, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
a = np.zeros_like(a)
cv2.drawContours(a, cnts, -1, 255, -1)
a = cv2.morphologyEx(a, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
a = cv2.GaussianBlur(a, (5, 5), 0)
x, y, w, h = cv2.boundingRect((a > 8).astype(np.uint8))
rgba = cv2.cvtColor(im, cv2.COLOR_BGR2BGRA)
rgba[..., 3] = a
cv2.imwrite(dst, rgba[y:y + h, x:x + w])
p = Image.open(dst)
b = Image.new('RGB', (p.width + 40, p.height + 40), (245, 239, 227))
b.paste(p, (20, 20), p)
b.thumbnail((500, 700))
b.save(dst.replace('.png', '_check.jpg'))
print(w, h)
