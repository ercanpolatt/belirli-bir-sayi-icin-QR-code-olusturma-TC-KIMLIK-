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
    Yazıcı çıktısı için işçinin QR kodu, Adı-Soyadı ve TC Kimlik Numarasını içeren
    yüksek kaliteli bir etiket/kart görseli oluşturur (900x600 px).
    """
    width, height = 900, 600
    card = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(card)
    
    # Kenarlık çizimi
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline="#2B3A4A", width=4)
    draw.rectangle([(25, 25), (width - 25, height - 25)], outline="#3B82F6", width=2)
    
    # Başlık Alanı
    draw.rectangle([(25, 25), (width - 25, 110)], fill="#1E293B")
    
    # Font seçimi (Sistem fontu yüklenemezsa varsayılan font)
    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_label = ImageFont.truetype("arial.ttf", 26)
        font_bold = ImageFont.truetype("arialbd.ttf", 34)
        font_tc = ImageFont.truetype("arialbd.ttf", 32)
    except IOError:
        font_title = font_label = font_bold = font_tc = ImageFont.load_default()
    
    # Başlık Metni
    header_text = "İŞÇİ KİMLİK & QR KOD KARTI"
    bbox = draw.textbbox((0, 0), header_text, font=font_title)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) / 2, 45), header_text, fill="white", font=font_title)
    
    # QR Kod Oluşturma ve Yerleştirme
    qr_img = generate_qr_image(tckn, box_size=11, border=2)
    qr_w, qr_h = qr_img.size
    card.paste(qr_img, (50, 160))
    
    # İşçi Bilgileri Alanı
    x_offset = 50 + qr_w + 50
    y_start = 180
    
    full_name = f"{name.upper()} {surname.upper()}".strip()
    
    draw.text((x_offset, y_start), "AD SOYAD:", fill="#64748B", font=font_label)
    draw.text((x_offset, y_start + 35), full_name if full_name else "-", fill="#0F172A", font=font_bold)
    
    draw.text((x_offset, y_start + 120), "TC KİMLİK NO:", fill="#64748B", font=font_label)
    draw.text((x_offset, y_start + 155), tckn, fill="#1D4ED8", font=font_tc)
    
    # Alt Bilgi / Doğrulama Notu
    footer_text = "Bu QR Kod taranarak TC Kimlik Numarası doğrulanabilir."
    bbox_f = draw.textbbox((0, 0), footer_text, font=font_label)
    text_w_f = bbox_f[2] - bbox_f[0]
    draw.text(((width - text_w_f) / 2, height - 60), footer_text, fill="#475569", font=font_label)
    
    return card
