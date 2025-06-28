import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from math import sin, cos, pi

# === CHOIX DE LA VERSION ===
def ask_p_value():
    while True:
        try:
            p = int(input("Choisissez la version de Dobble (p = 2, 3, 5 ou 7) : "))
            if p in [2, 3, 5, 7]:
                return p
            else:
                print("Veuillez entrer 2, 3, 5 ou 7.")
        except ValueError:
            print("Entrée invalide.")

# === CHARGER LES IMAGES D'UN DOSSIER ===
def load_images_from_folder(folder_path, expected_count, symbol_size):
    all_files = sorted(os.listdir(folder_path))
    image_paths = [os.path.join(folder_path, f) for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if len(image_paths) < expected_count:
        raise ValueError(f"❌ Seulement {len(image_paths)} images trouvées, mais {expected_count} nécessaires.")

    return [
        Image.open(path).convert("RGBA").resize((symbol_size, symbol_size))
        for path in image_paths[:expected_count]
    ]

# === GÉNÉRATION MATHÉMATIQUE DES CARTES DOBBLE ===
def generate_dobble_cards(p):
    cards = []

    for a in range(p):
        for b in range(p):
            card = [0]
            for i in range(1, p + 1):
                value = (i * a + b) % p
                card.append(i * p + value + 1)
            cards.append(card)

    for j in range(p + 1):
        card = [j + 1]
        for k in range(p):
            card.append((p + 1) + p * k + j)
        cards.append(card)

    return cards

# === CRÉER DES IMAGES DE CARTES ===
def create_card(symbol_indices, symbols, output_path, card_size=500, symbol_size=100):
    card = Image.new("RGBA", (card_size, card_size), (255, 255, 255, 255))
    center = card_size // 2
    radius = card_size // 2 - symbol_size

    for i, index in enumerate(symbol_indices):
        angle = 2 * pi * i / len(symbol_indices)
        x = int(center + radius * cos(angle) - symbol_size // 2)
        y = int(center + radius * sin(angle) - symbol_size // 2)
        card.paste(symbols[index - 1], (x, y), symbols[index - 1])

    card.save(output_path)

# === GÉNÉRER LE PDF 6 CARTES PAR PAGE AVEC LIGNES DE DÉCOUPE ===
def generate_pdf_six_cards_per_page(image_paths, output_pdf, card_size=250):
    c = canvas.Canvas(output_pdf, pagesize=A4)
    page_width, page_height = A4

    cols = 2
    rows = 3
    margin = 20  # marge autour des cartes en points
    h_spacing = (page_width - 2 * margin - cols * card_size) / (cols - 1)
    v_spacing = (page_height - 2 * margin - rows * card_size) / (rows - 1)

    def draw_cut_lines():
        # Lignes verticales
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(0.5)
        c.setDash(3, 3)  # ligne pointillée
        for col in range(1, cols):
            x = margin + col * (card_size + h_spacing) - h_spacing / 2
            c.line(x, margin, x, page_height - margin)
        # Lignes horizontales
        for row in range(1, rows):
            y = page_height - margin - row * (card_size + v_spacing) + v_spacing / 2
            c.line(margin, y, page_width - margin, y)
        c.setDash()  # reset dash

    for i, img_path in enumerate(image_paths):
        col = i % cols
        row = (i // cols) % rows

        x = margin + col * (card_size + h_spacing)
        y = page_height - margin - (row + 1) * card_size - row * v_spacing

        c.drawImage(img_path, x, y, width=card_size, height=card_size)

        # Si dernière carte sur la page ou fin des images, tracer lignes et nouvelle page
        if (i + 1) % (cols * rows) == 0:
            draw_cut_lines()
            c.showPage()

    # Tracer lignes de découpe pour la dernière page (si incomplète)
    draw_cut_lines()
    c.save()

# === MAIN ===
def main():
    print("🎴 Générateur de Dobble personnalisé")
    p = ask_p_value()
    n_symbols = p**2 + p + 1
    symbols_per_card = p + 1
    n_cards = n_symbols

    print(f"\n➡️  p = {p} → {n_symbols} symboles, {symbols_per_card} symboles/carte, {n_cards} cartes.")

    # Demande du dossier contenant les images
    while True:
        folder = input(f"\n📁 Entrez le chemin du dossier contenant AU MOINS {n_symbols} images : ").strip('"')
        if os.path.isdir(folder):
            try:
                SYMBOL_SIZE = 100
                symbols = load_images_from_folder(folder, n_symbols, SYMBOL_SIZE)
                break
            except ValueError as e:
                print(e)
        else:
            print("❌ Dossier introuvable.")

    # Génération des cartes mathématiques
    symbol_indices_cards = generate_dobble_cards(p)

    # Génération des images
    output_folder = f"dobble_p{p}_cards"
    os.makedirs(output_folder, exist_ok=True)
    card_image_paths = []

    for i, symbol_indices in enumerate(symbol_indices_cards):
        path = os.path.join(output_folder, f"card_{i+1}.png")
        create_card(symbol_indices, symbols, path)
        card_image_paths.append(path)

    # Génération du PDF avec 6 cartes par page
    pdf_filename = f"dobble_p{p}_6cards_per_page.pdf"
    generate_pdf_six_cards_per_page(card_image_paths, pdf_filename)

    print(f"\n✅ PDF généré : {pdf_filename}")
    print(f"🖼️  Images des cartes enregistrées dans : {output_folder}")

if __name__ == "__main__":
    main()
