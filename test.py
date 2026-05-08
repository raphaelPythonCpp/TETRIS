from PIL import Image

for nom in ["grille_I", "grille_T", "grille_X"]:
    image = Image.open(f"MENUS\\IMAGES_BASE\\IMAGES\\{nom}.png").convert("RGBA")
    pixels = image.load()
    w, h = image.size
    for y in range(h):
        for x in range(w):
            r,g,b,a = pixels[x, y]
            if max(r,g,b) < 100:
                pixels[x, y] = (255-r,255-g,255-b,a)
    image.save(f"MENUS\\IMAGES_BASE\\IMAGES\\{nom}_blanc.png")