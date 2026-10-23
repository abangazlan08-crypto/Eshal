from PIL import Image, ImageDraw, ImageFont
S = 4  # supersample
W, H = 130*S, 205*S
GREY = (74, 74, 74, 255)
ROSE = (196, 112, 122, 255)
img = Image.new("RGBA", (W, H), (255, 255, 255, 0))
d = ImageDraw.Draw(img)
bw = 2*S
d.rectangle([bw//2, bw//2, W-1-bw//2, H-1-bw//2], outline=ROSE, width=bw)

def glyph(ch, font, box):
    f = ImageFont.truetype(font, 600)
    l, t, r, b = f.getbbox(ch)
    g = Image.new("L", (r-l, b-t), 0)
    ImageDraw.Draw(g).text((-l, -t), ch, font=f, fill=255)
    x0, y0, x1, y1 = box
    g = g.resize((x1-x0, y1-y0), Image.LANCZOS)
    img.paste(Image.new("RGBA", g.size, GREY), (x0, y0), g)

INTER = "/usr/share/fonts/opentype/inter/"
glyph("B", INTER+"Inter-Light.otf", (12*S, 34*S, 74*S, 172*S))   # large B
glyph("B", INTER+"Inter-Light.otf",   (86*S, 52*S, 112*S, 92*S))   # small B
d.rectangle([86*S, 103*S, 112*S, 103*S + int(1.6*S)], fill=GREY)   # divider
glyph("S", INTER+"Inter-Light.otf",   (86*S, 114*S, 112*S, 154*S)) # small S

out = img.resize((W//S*4, H//S*4), Image.LANCZOS)  # keep 4x for print sharpness
bg = Image.new("RGB", out.size, "white"); bg.paste(out, mask=out.split()[3])
bg.save("bbs_logo.png", dpi=(600, 600))
