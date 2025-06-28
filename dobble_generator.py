import os
import random
from math import ceil, sqrt, pi, cos, sin
from PIL import Image, ImageDraw
from itertools import cycle

CARD_SIZE = 500
MARGIN = 5

# === Fonctions Dobble ===
def generate_dobble_cards(p):
    n = p**2 + p + 1
    cards = []
    # première série
    for i in range(p + 1):
        cards.append([1] + [i*p + j + 2 for j in range(p)])
    # séries suivantes
    for a in range(1, p + 1):
        for b in range(1, p + 1):
            card = [a+1]
            for k in range(1, p + 1):
                sym = (p+1) + p*(k-1) + ((a-1)*(k-1)+(b-1)) % p
                card.append(sym+1)
            cards.append(card)
    return cards

# === Génération des zones via grille ===
def generate_grid_zones(n, card_size, coverage_ratio=0.8, margin=MARGIN):
    """
    Renvoie exactement n zones (dicts) non chevauchantes dans une grille,
    couvrant approx coverage_ratio * surface.
    Chaque zone a champs x,y,size,rotation,bbox.
    """
    # surface totale / zone
    total_area = card_size * card_size
    zone_area = total_area * coverage_ratio / n
    base_size = int(sqrt(zone_area))

    # on autorise variation ±10%
    min_size = int(base_size * 0.9)
    max_size = int(base_size * 1.1)

    # grille minimale
    side = 1
    while side * side < n:
        side += 1

    cell_w = card_size // side
    cell_h = card_size // side

    # on prend exactement n positions
    positions = [(col*cell_w, row*cell_h, cell_w, cell_h)
                 for row in range(side) for col in range(side)]
    random.shuffle(positions)

    zones = []
    for i in range(n):
        x0, y0, w, h = positions[i]
        # taille zonale
        size = random.randint(min_size, max_size)
        # clip pour pas dépasser la case en tenant compte de la marge
        size = min(size, w - 2*margin, h - 2*margin)
        # position aléatoire dans la case
        x = x0 + random.randint(margin, w - size - margin)
        y = y0 + random.randint(margin, h - size - margin)
        rot = random.uniform(0, 360)
        bbox = (x - margin, y - margin, x + size + margin, y + size + margin)
        zones.append({
            "x": x, "y": y,
            "size": size,
            "rotation": rot,
            "bbox": bbox
        })
    return zones

def generate_layouts(p, card_size):
    # crée p layouts (listes de zones) cycliques
    return [generate_grid_zones(p+1, card_size) for _ in range(p)]

def save_layout_debug_image(layout, path, card_size=CARD_SIZE, margin=MARGIN):
    img = Image.new("RGBA", (card_size, card_size), (255,255,255,255))
    draw = ImageDraw.Draw(img)
    for i, z in enumerate(layout):
        # zone avec marge (noir)
        draw.rectangle(z['bbox'], outline="black", width=2)
        # zone réelle (rouge)
        draw.rectangle([z['x'], z['y'], z['x']+z['size'], z['y']+z['size']],
                       outline="red", width=2)
        # centre + flèche rotation
        cx, cy = z['x']+z['size']//2, z['y']+z['size']//2
        r = z['size']//2
        ang = z['rotation']*pi/180
        xe, ye = int(cx + r*cos(ang)), int(cy + r*sin(ang))
        draw.line((cx, cy, xe, ye), fill="blue", width=2)
        draw.text((cx-5, cy-5), str(i+1), fill="black")
    img.save(path)

# === Création d’une carte ===
def create_card(symbol_indices, symbols, output_path, layout):
    card = Image.new("RGBA", (CARD_SIZE, CARD_SIZE), (255,255,255,255))
    order = symbol_indices[:]
    random.shuffle(order)
    for idx, zone in zip(order, layout):
        sym = symbols[idx-1].resize((zone['size'], zone['size']), Image.BICUBIC)
        rot = sym.rotate(zone['rotation'], expand=False)
        card.paste(rot, (zone['x'], zone['y']), rot)
    card.save(output_path)
    return card

# === Génération du PDF ===
def create_pdf(cards, output_path):
    from PIL import ImageDraw
    dpi = 300
    w_pt, h_pt = int(210/25.4*dpi), int(297/25.4*dpi)
    per_row, per_col = 2, 3
    margin_x = (w_pt - per_row*CARD_SIZE)//(per_row+1)
    margin_y = (h_pt - per_col*CARD_SIZE)//(per_col+1)

    pages = []
    for i in range(0, len(cards), per_row*per_col):
        pg = Image.new("RGB", (w_pt, h_pt), "white")
        d = ImageDraw.Draw(pg)
        slice = cards[i:i+per_row*per_col]
        for j, c in enumerate(slice):
            row, col = divmod(j, per_row)
            x = margin_x + col*(CARD_SIZE+margin_x)
            y = margin_y + row*(CARD_SIZE+margin_y)
            pg.paste(c.convert("RGB"), (x,y))
        # lignes de découpe
        for c in range(1, per_row):
            x = margin_x*c + CARD_SIZE*(c)
            d.line([(x,0),(x,h_pt)], fill="black", width=2)
        for r in range(1, per_col):
            y = margin_y*r + CARD_SIZE*(r)
            d.line([(0,y),(w_pt,y)], fill="black", width=2)
        pages.append(pg)

    pages[0].save(output_path, save_all=True, append_images=pages[1:])
    print(f"✅ PDF généré : {output_path}")

# === Script principal ===
def main():
    print("🎴 Générateur de Dobble personnalisé")
    # choix de p
    symbols_per_card = int(input("Choisissez la version de Dobble (le nombre de symboles par cartes (3, 4, 6 ou 8) : "))
    if symbols_per_card not in [3, 4, 6, 8]:
        print("Veuillez entrer (3, 4, 6 ou 8).")
    p = symbols_per_card - 1;
    n_symbols = p**2 + p + 1
    print(f"\n➡️ {n_symbols} symboles, {symbols_per_card} symboles/carte, {n_symbols} cartes.")

    # Demande du dossier contenant les images
    folder = input(f"\n📁 Entrez le chemin du dossier contenant AU MOINS {n_symbols} images : ").strip('"')
    imgs = [os.path.join(folder,f) for f in os.listdir(folder)
    if f.lower().endswith(('png','jpg','jpeg'))]
    if len(imgs)<n_symbols:
        print(f"⛔ Il faut {n_symbols} images, trouvé {len(imgs)}.") 
        return

    imgs = imgs[:n_symbols]
    symbols = [Image.open(f).convert("RGBA") for f in imgs]

    cards_idx = generate_dobble_cards(p)
    layouts = generate_layouts(p, CARD_SIZE)

    out = "output"
    os.makedirs(out, exist_ok=True)

    # debug layouts
    for i, l in enumerate(layouts,1):
        save_layout_debug_image(l, os.path.join(out,f"layout_debug_{i}.png"))

    # créer cartes
    cards = []
    for i, ci in enumerate(cards_idx,1):
        lay = layouts[(i-1)%p]
        path = os.path.join(out, f"card_{i}.png")
        card = create_card(ci, symbols, path, lay)
        cards.append(card)

    # PDF
    pdf_path = os.path.join(out,"dobble_custom.pdf")
    create_pdf(cards, pdf_path)

if __name__=="__main__":
    main()
