# Créé par raphael.garivier, le 23/04/2026 en Python 3.7
from PIL import Image

dossier1 = "EXPOSE"
dossier2 = "EXPOSE2"
lNoms = ["image_1"]

for nom in lNoms:
    image = Image.open(f"{dossier1}\\{nom}.png").convert("RGBA")
    pixels = image.load()
    w, h = image.size
    for y in range(h):
        for x in range(w):
            r,g,b,a = pixels[x,y]
            if min(r,g,b) > 200 and a > 240:
                pixels[x,y] = (0,0,0,0)
            elif max(r,g,b) < 120 and a > 140:
                pixels[x,y] = (255,255,255,255)
    image.save(f"{dossier2}\\{nom}_2.png")

