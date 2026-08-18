"""
QR Kod Üretimi ve TC Kimlik Numarası Doğrulama Modülü
"""
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os


def validate_tckn(tckn: str) -> tuple[bool, str]:
    """
    TC Kimlik Numarasının geçerliliğini kontrol eder.
    - 11 haneli olmalıdır.
    - Sadece rakamlardan oluşmalıdır.
    - 0 ile başlayamaz.
    - Matematiksel doğrulama algoritmasına uymalıdır.
    """
    if not tckn:
        return False, "TC Kimlik numarası boş olamaz."
    
    tckn = str(tckn).strip()
    
    if len(tckn) != 11:
        return False, "TC Kimlik numarası tam 11 haneli olmalıdır."
    
    if not tckn.isdigit():
        return False, "TC Kimlik numarası sadece rakamlardan oluşmalıdır."
    
    if tckn[0] == '0':
        return False, "TC Kimlik numarası 0 ile başlayamaz."
    
    digits = [int(d) for d in tckn]
    
    # 10. basamak kontrolü
    odd_sum = sum(digits[0:9:2])   # 1, 3, 5, 7, 9. haneler
    even_sum = sum(digits[1:8:2])  # 2, 4, 6, 8. haneler
    digit10 = ((odd_sum * 7) - even_sum) % 10
    
    if digits[9] != digit10:
        return False, "Geçersiz TC Kimlik Numarası (Algoritma doğrulaması başarısız)."
    
    # 11. basamak kontrolü
    digit11 = sum(digits[:10]) % 10
    if digits[10] != digit11:
        return False, "Geçersiz TC Kimlik Numarası (Toplam kontrolü başarısız)."
    
    return True, "TC Kimlik numarası geçerli."


def generate_qr_image(tckn: str, box_size: int = 10, border: int = 2) -> Image.Image:
    """
    Girilen TC Kimlik numarasını içeren QR kod görseli oluşturur.
    Taratıldığında tam olarak TC Kimlik Numarası çıkar.
    """
    tckn = str(tckn).strip()
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(tckn)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    return img.convert("RGB")


def create_printable_badge(name: str, surname: str, tckn: str) -> Image.Image:
    """
    Yazıcı çıktısı için SADECE büyük bir QR kod ve altında İşçinin Adı-Soyadını içeren
    sade ve yüksek kaliteli etiket/kart görseli oluşturur (800x850 px).
    """
    width, height = 800, 850
    card = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(card)
    
    # 1. Büyük QR Kod Üretimi (box_size=15 ile geniş QR kod)
    qr_img = generate_qr_image(tckn, box_size=15, border=2)
    qr_w, qr_h = qr_img.size
    
    # QR Kodu yatayda merkeze yerleştirme
    qr_x = (width - qr_w) // 2
    qr_y = 40
    card.paste(qr_img, (qr_x, qr_y))
    
    # 2. Ad Soyad Metni
    full_name = f"{name.upper()} {surname.upper()}".strip()
    if not full_name:
        full_name = "-"
        
    try:
        font_name = ImageFont.truetype("arialbd.ttf", 46)
    except IOError:
        try:
            font_name = ImageFont.truetype("arial.ttf", 46)
        except IOError:
            font_name = ImageFont.load_default()
            
    # Ad Soyad metnini ortalama
    bbox = draw.textbbox((0, 0), full_name, font=font_name)
    text_w = bbox[2] - bbox[0]
    text_x = (width - text_w) // 2
    text_y = qr_y + qr_h + 30
    
    draw.text((text_x, text_y), full_name, fill="#000000", font=font_name)
    
    return card


def create_grid_printable_pages(workers: list[tuple[str, str, str]], items_per_row: int = 3, rows_per_page: int = 4) -> list[Image.Image]:
    """
    Birden fazla işçi için A4 sayfasına yan yana 3'lü dizilimde kağıt tasarrufu sağlayan
    yazdırılabilir A4 sayfa görselleri oluşturur (2480 x 3508 px - 300 DPI).
    """
    if not workers:
        return []
        
    page_width, page_height = 2480, 3508
    margin_x = 115
    margin_y = 100
    gap_x = 30
    gap_y = 40
    
    cell_w = 740
    cell_h = 770
    
    capacity_per_page = items_per_row * rows_per_page
    pages = []
    
    try:
        font_name = ImageFont.truetype("arialbd.ttf", 36)
    except IOError:
        try:
            font_name = ImageFont.truetype("arial.ttf", 36)
        except IOError:
            font_name = ImageFont.load_default()

    current_page = None
    draw = None
    
    for idx, (name, surname, tckn) in enumerate(workers):
        pos_in_page = idx % capacity_per_page
        
        # Yeni sayfa başlatma
        if pos_in_page == 0:
            current_page = Image.new("RGB", (page_width, page_height), "white")
            draw = ImageDraw.Draw(current_page)
            pages.append(current_page)
            
        row = pos_in_page // items_per_row
        col = pos_in_page % items_per_row
        
        x = margin_x + col * (cell_w + gap_x)
        y = margin_y + row * (cell_h + gap_y)
        
        # Kesim çizgisi (Hafif gri kesikli dış çerçeve)
        draw.rectangle([(x, y), (x + cell_w, y + cell_h)], outline="#CBD5E1", width=2)
        
        # QR Kod üretme
        qr_img = generate_qr_image(tckn, box_size=12, border=2)
        qr_w, qr_h = qr_img.size
        
        qr_x = x + (cell_w - qr_w) // 2
        qr_y = y + 30
        current_page.paste(qr_img, (qr_x, qr_y))
        
        # Ad Soyad Metni
        full_name = f"{name.upper()} {surname.upper()}".strip()
        if not full_name:
            full_name = "-"
            
        bbox = draw.textbbox((0, 0), full_name, font=font_name)
        text_w = bbox[2] - bbox[0]
        text_x = x + (cell_w - text_w) // 2
        text_y = qr_y + qr_h + 25
        
        draw.text((text_x, text_y), full_name, fill="#000000", font=font_name)

    return pages


