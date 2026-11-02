import cv2, numpy as np, sys
from PIL import Image

def finish(img_full, m_small, out):
    h, w = img_full.shape[:2]
    m = cv2.resize(m_small, (w, h), interpolation=cv2.INTER_LINEAR)
    m = np.where(m > 127, 255, 0).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    k = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    m = np.where(lab == k, 255, 0).astype(np.uint8)
    ff = m.copy(); mm = np.zeros((h + 2, w + 2), np.uint8); cv2.floodFill(ff, mm, (0, 0), 255); m = m | cv2.bitwise_not(ff)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    m = cv2.GaussianBlur(m, (7, 7), 0)
    rgb = cv2.cvtColor(img_full, cv2.COLOR_BGR2RGB)
    im = Image.fromarray(np.dstack([rgb, m]))
    im = im.crop(im.getbbox()); im.save(out)
    bg = Image.new('RGBA', im.size, (240, 240, 244, 255)); bg.alpha_composite(im)
    bg.convert('RGB').resize((im.width // 2, im.height // 2)).save(out.replace('_cut.png', '_chk.jpg'))
    print(out, im.size)

def grab(img_full, rect, scale, prior=None):
    small = cv2.resize(img_full, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    r = tuple(int(v * scale) for v in rect)
    mask = np.zeros(small.shape[:2], np.uint8)
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    if prior is None:
        cv2.grabCut(small, mask, r, bgd, fgd, 5, cv2.GC_INIT_WITH_RECT)
    else:
        mask[:] = cv2.GC_PR_BGD
        x, y, w, h = r
        mask[y:y + h, x:x + w] = cv2.GC_PR_FGD
        p = cv2.resize(prior, (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
        mask[p == 1] = cv2.GC_FGD
        mask[p == 0] = cv2.GC_BGD
        cv2.grabCut(small, mask, None, bgd, fgd, 5, cv2.GC_INIT_WITH_MASK)
    return np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)

which = sys.argv[1]
if which == 'gold':
    img = cv2.imread('img/goldbar.jpg')
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gold = ((hsv[..., 0] >= 12) & (hsv[..., 0] <= 32) & (hsv[..., 1] > 110) & (hsv[..., 2] > 90)).astype(np.uint8)
    prior = np.full(gold.shape, 2, np.uint8)
    prior[:, :380] = 0; prior[:, 1060:] = 0; prior[:420] = 0; prior[1650:] = 0
    prior[cv2.erode(gold, np.ones((31, 31), np.uint8)) == 1] = 1
    finish(img, grab(img, (430, 470, 590, 1140), 0.4, prior), 'img/goldbar_cut.png')
else:
    img = cv2.imread('img/money.png')
    finish(img, grab(img, (95, 560, 900, 890), 0.5), 'img/money_cut.png')
