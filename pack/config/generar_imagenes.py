#!/usr/bin/env python3
"""
Genera las imagenes del preset de carga de Alkima (fondo, logo y texto "CARGANDO").
Requiere:  pip install pillow
Edita las constantes de abajo y ejecuta:  python generar_imagenes.py
(las imagenes se guardan en config/simple-custom-early-loading/)
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ----------------------------------------------------------------- personaliza aqui
TITULO = "ALKIMA"
SUBTITULO = "HARDCOREV3"          # "" para quitarlo
TEXTO_CARGA = "CARGANDO"
FONDO = "fondo_original.png"      # imagen de fondo (se oscurece sola). Si no existe, usa un degradado
ROJO = (213, 6, 30)
GLOW = (255, 40, 62)
BLANCO = (240, 240, 242)
SALIDA = Path(__file__).resolve().parent / "config" / "simple-custom-early-loading"
W, H = 1920, 1080
# ------------------------------------------------------------------------------------

FUENTES_BOLD = ["ariblk.ttf", "seguibl.ttf", "segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"]


def fuente(size):
    for n in FUENTES_BOLD:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            pass
    return ImageFont.load_default(size)


def cover(img, w, h):
    s = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def mascara_radial(w, h, inner, blur):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).ellipse((w * inner, -h * 0.1, w * (1 - inner), h * 1.1), fill=255)
    return m.filter(ImageFilter.GaussianBlur(min(w, h) * blur))


def texto_espaciado(d, cx, y, texto, f, fill, sp):
    ws = [d.textlength(c, font=f) for c in texto]
    total = sum(ws) + sp * (len(texto) - 1)
    x = cx - total / 2
    for c, w in zip(texto, ws):
        d.text((x, y), c, font=f, fill=fill, anchor="la")
        x += w + sp


def fondo():
    p = Path(__file__).resolve().parent / FONDO
    negro = Image.new("RGB", (W, H), (0, 0, 0))
    if p.exists():
        bg = cover(Image.open(p).convert("RGB"), W, H).filter(ImageFilter.GaussianBlur(2.4))
        bg = Image.blend(bg, negro, 0.62)
        bg = Image.composite(bg, negro, mascara_radial(W, H, 0.05, 0.22))
    else:
        bg = Image.composite(Image.new("RGB", (W, H), (36, 33, 38)), Image.new("RGB", (W, H), (5, 5, 6)),
                             mascara_radial(W, H, 0.2, 0.2))
    d = ImageDraw.Draw(bg)  # bordes rojos inclinados, igual que el launcher
    k = H / 640
    d.polygon([(W - 7 * k, 0), (W, 0), (W, H), (W - 15 * k, H)], fill=ROJO)
    d.polygon([(0, H - 3 * k), (W, H - 12 * k), (W, H), (0, H)], fill=ROJO)
    return bg


def logo():
    cw, ch = 1500, 460
    f = fuente(300)
    tmp = ImageDraw.Draw(Image.new("L", (4, 4)))
    while tmp.textlength(TITULO, font=f) > cw - 120 and f.size > 60:
        f = fuente(f.size - 6)
    cy = 200
    mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask).text((cw // 2, cy), TITULO, font=f, fill=255, anchor="mm")
    from PIL import ImageChops
    cerca = mask.filter(ImageFilter.GaussianBlur(f.size * 0.06)).point(lambda v: int(v * 0.95))
    lejos = mask.filter(ImageFilter.GaussianBlur(f.size * 0.16)).point(lambda v: int(v * 0.75))
    glow = ImageChops.add(cerca, lejos)  # resplandor rojo en dos capas (cerca y lejos)
    out = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    out.paste(Image.new("RGBA", (cw, ch), GLOW + (255,)), (0, 0), glow)
    d = ImageDraw.Draw(out)
    d.text((cw // 2, cy), TITULO, font=f, fill=BLANCO + (255,), anchor="mm")
    if SUBTITULO:
        texto_espaciado(d, cw // 2, cy + int(f.size * 0.62) + 14, SUBTITULO, fuente(44), (205, 205, 212, 255), 14)
    return out


def carga():
    cw, ch = 900, 120
    out = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    texto_espaciado(d, cw // 2, 34, TEXTO_CARGA, fuente(56), (205, 205, 212, 255), 22)
    return out


if __name__ == "__main__":
    SALIDA.mkdir(parents=True, exist_ok=True)
    fondo().save(SALIDA / "background.png")
    logo().save(SALIDA / "logo.png")
    carga().save(SALIDA / "cargando.png")
    print("Imagenes creadas en", SALIDA)
