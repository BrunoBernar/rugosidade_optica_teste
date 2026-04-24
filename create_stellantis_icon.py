"""
Gera icone estilo app matematico: fundo verde degradê, simbolo integral
branco cursivo (∫x), bordas arredondadas.
Execute: python create_stellantis_icon.py
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT  = "stellantis.ico"
SIZES   = [(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)]

# Verde degradê (canto sup-esq claro → inf-dir escuro)
GREEN_TL = (72,  200, 120)
GREEN_BR = (30,  140,  70)
WHITE    = (255, 255, 255)


def gradient_bg(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size))
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * size)
            r = int(GREEN_TL[0] * (1-t) + GREEN_BR[0] * t)
            g = int(GREEN_TL[1] * (1-t) + GREEN_BR[1] * t)
            b = int(GREEN_TL[2] * (1-t) + GREEN_BR[2] * t)
            img.putpixel((x, y), (r, g, b, 255))
    return img


def rounded_mask(size: int, radius: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, size-1, size-1], radius=radius, fill=255
    )
    return mask


def best_font(size: int, italic: bool = False):
    candidates = [
        "C:/Windows/Fonts/cambriai.ttf",   # Cambria Italic — ótimo para ∫
        "C:/Windows/Fonts/cambria.ttc",
        "C:/Windows/Fonts/timesi.ttf",
        "C:/Windows/Fonts/times.ttf",
        "C:/Windows/Fonts/georgiab.ttf",
        "C:/Windows/Fonts/georgia.ttf",
    ]
    if not italic:
        candidates = candidates[1:] + candidates[:1]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def draw_frame(size: int) -> Image.Image:
    radius = int(size * 0.22)

    img  = gradient_bg(size)
    img.putalpha(rounded_mask(size, radius))

    draw = ImageDraw.Draw(img)

    # ── Símbolo ∫x centrado ────────────────────────────────────────
    # ∫ em fonte maior italica, x menor ao lado
    integral_h = int(size * 0.68)
    x_h        = int(size * 0.36)

    f_int = best_font(integral_h, italic=True)
    f_x   = best_font(x_h,        italic=True)

    sym_int = "\u222B"   # ∫
    sym_x   = "x"

    # Medir cada parte
    bi = draw.textbbox((0, 0), sym_int, font=f_int)
    bx = draw.textbbox((0, 0), sym_x,  font=f_x)

    wi = bi[2] - bi[0]
    wx = bx[2] - bx[0]
    gap = int(size * 0.01)
    total_w = wi + gap + wx

    # Centro do canvas
    cx = size // 2
    cy = size // 2

    # Posição baseline: ∫ centrado verticalmente, x alinhado ao centro do ∫
    ix = cx - total_w // 2 - bi[0]
    iy = cy - (bi[3] - bi[1]) // 2 - bi[1] - int(size * 0.03)

    xx = ix + bi[0] + wi + gap - bx[0]
    xy = iy + bi[1] + (bi[3]-bi[1])//2 - (bx[3]-bx[1])//2 - bx[1]

    # Sombra suave
    shadow = Image.new("RGBA", (size, size), (0,0,0,0))
    sd = ImageDraw.Draw(shadow)
    sd.text((ix+size//40, iy+size//40), sym_int, fill=(0,0,0,80), font=f_int)
    sd.text((xx+size//40, xy+size//40), sym_x,   fill=(0,0,0,80), font=f_x)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=max(1, size//40)))
    img = Image.alpha_composite(img, shadow)

    # Texto branco
    draw = ImageDraw.Draw(img)
    draw.text((ix, iy), sym_int, fill=WHITE, font=f_int)
    draw.text((xx, xy), sym_x,   fill=WHITE, font=f_x)

    return img


def make_ico(path: str):
    frames = [draw_frame(w) for w, h in SIZES]
    frames[0].save(path, format="ICO", sizes=SIZES, append_images=frames[1:])
    print(f"[OK] Icone salvo em: {path}")


if __name__ == "__main__":
    make_ico(OUTPUT)
    preview = draw_frame(256)
    preview.save("stellantis_preview.png")
    print("[OK] Preview salvo em: stellantis_preview.png")
