"""
QR Kod & Barkod Üretimi ve TC Kimlik Numarası Doğrulama Modülü
Desteklenen formatlar: QR Kod, 1D Barkod (Code 128, Code 39), Kombine (QR + Barkod)
"""
import os
import re
import csv
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import qrcode
import barcode
from barcode.writer import ImageWriter


def get_system_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """
    Sistemde yüklü olan en uygun yazı tipini (Arial, Segoe UI, Calibri) döndürür.
    Bulamazsa varsayılan PIL fontunu yükler.
    """
    candidates = [
        "arialbd.ttf" if bold else "arial.ttf",
        "segoeuib.ttf" if bold else "segoeui.ttf",
        "calibrib.ttf" if bold else "calibri.ttf",
        "tahoma.ttf",
    ]
    for font_name in candidates:
        try:
            return ImageFont.truetype(font_name, size)
        except IOError:
            continue
    return ImageFont.load_default()


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
    Girilen TC Kimlik numarasını içeren yüksek çözünürlüklü QR kod görseli oluşturur.
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


def generate_barcode_image(
    tckn: str,
    barcode_type: str = "code128",
    show_text: bool = True,
    module_width: float = 0.42,
    module_height: float = 16.0,
    font_size: int = 14
) -> Image.Image:
    """
    Girilen TC Kimlik numarası için endüstri standardı 1D çizgi barkod görseli üretir.
    Optik tarayıcılar ve el terminalleri için optimize edilmiş quiet zone içerir.
    - barcode_type: "code128" (varsayılan) veya "code39"
    """
    tckn = str(tckn).strip()
    type_key = barcode_type.lower().replace("-", "").replace(" ", "")
    if "39" in type_key:
        bc_class_name = "code39"
    else:
        bc_class_name = "code128"
        
    bc_cls = barcode.get_barcode_class(bc_class_name)
    writer = ImageWriter()
    
    writer_options = {
        "module_width": module_width,
        "module_height": module_height,
        "font_size": font_size,
        "text_distance": 4.0,
        "quiet_zone": 4.0,
        "write_text": show_text
    }
    
    if bc_class_name == "code39":
        bc = bc_cls(tckn, writer=writer, add_checksum=False)
    else:
        bc = bc_cls(tckn, writer=writer)
        
    fp = BytesIO()
    bc.write(fp, options=writer_options)
    fp.seek(0)
    img = Image.open(fp).convert("RGB")
    return img


def generate_combined_code_image(
    tckn: str,
    barcode_type: str = "code128",
    show_barcode_text: bool = True
) -> Image.Image:
    """
    Hem QR Kod hem de Çizgi Barkodu tek bir görselde estetik olarak birleştirir.
    """
    tckn = str(tckn).strip()
    qr_img = generate_qr_image(tckn, box_size=8, border=2)
    bc_img = generate_barcode_image(tckn, barcode_type=barcode_type, show_text=show_barcode_text, module_width=0.38, module_height=14.0)
    
    # Boyutları belirle
    total_w = max(qr_img.width + 40, bc_img.width + 40, 600)
    total_h = qr_img.height + bc_img.height + 60
    
    combined = Image.new("RGB", (total_w, total_h), "white")
    
    qr_x = (total_w - qr_img.width) // 2
    qr_y = 20
    combined.paste(qr_img, (qr_x, qr_y))
    
    bc_x = (total_w - bc_img.width) // 2
    bc_y = qr_y + qr_img.height + 20
    combined.paste(bc_img, (bc_x, bc_y))
    
    return combined


def create_printable_badge(
    name: str,
    surname: str,
    tckn: str,
    code_mode: str = "qr",
    barcode_type: str = "code128",
    show_barcode_text: bool = True,
    company_title: str = ""
) -> Image.Image:
    """
    Yazıcı çıktısı ve yaka kartı için yüksek kaliteli, net ve estetik etiket/kart görseli oluşturur.
    - code_mode: "qr" (Yalnızca QR), "barcode" (Yalnızca Barkod), "both" (QR + Barkod)
    """
    width, height = 800, 850
    card = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(card)
    
    font_name = get_system_font(42, bold=True)
    font_tckn = get_system_font(28, bold=False)
    font_header = get_system_font(26, bold=True)
    
    full_name = f"{name.upper()} {surname.upper()}".strip()
    if not full_name:
        full_name = "-"
        
    start_y = 35
    
    # Opsiyonel Firma / Kurum Başlığı
    if company_title.strip():
        comp_text = company_title.strip().upper()
        bbox_comp = draw.textbbox((0, 0), comp_text, font=font_header)
        comp_w = bbox_comp[2] - bbox_comp[0]
        draw.text(((width - comp_w) // 2, start_y), comp_text, fill="#334155", font=font_header)
        # İnce ayraç çizgi
        draw.line([(60, start_y + 40), (width - 60, start_y + 40)], fill="#E2E8F0", width=2)
        start_y += 55

    # 1. YALNIZCA QR KOD MODU
    if code_mode == "qr":
        qr_img = generate_qr_image(tckn, box_size=15, border=2)
        qr_w, qr_h = qr_img.size
        qr_x = (width - qr_w) // 2
        qr_y = start_y + 10
        card.paste(qr_img, (qr_x, qr_y))
        
        # İsim ve TC Metni
        bbox = draw.textbbox((0, 0), full_name, font=font_name)
        text_w = bbox[2] - bbox[0]
        text_x = (width - text_w) // 2
        text_y = qr_y + qr_h + 30
        draw.text((text_x, text_y), full_name, fill="#000000", font=font_name)
        
        tc_text = f"TCKN: {tckn}"
        bbox_tc = draw.textbbox((0, 0), tc_text, font=font_tckn)
        tc_w = bbox_tc[2] - bbox_tc[0]
        draw.text(((width - tc_w) // 2, text_y + 55), tc_text, fill="#475569", font=font_tckn)

    # 2. YALNIZCA BARKOD MODU
    elif code_mode == "barcode":
        bc_img = generate_barcode_image(
            tckn,
            barcode_type=barcode_type,
            show_text=show_barcode_text,
            module_width=0.48,
            module_height=26.0,
            font_size=18
        )
        
        # Eğer barkod genişliği karttan büyükse orantılı sığdır
        if bc_img.width > (width - 60):
            ratio = (width - 60) / bc_img.width
            new_h = int(bc_img.height * ratio)
            bc_img = bc_img.resize((width - 60, new_h), Image.Resampling.LANCZOS)
            
        bc_w, bc_h = bc_img.size
        bc_x = (width - bc_w) // 2
        bc_y = start_y + 80
        card.paste(bc_img, (bc_x, bc_y))
        
        # İsim ve TC Metni
        bbox = draw.textbbox((0, 0), full_name, font=font_name)
        text_w = bbox[2] - bbox[0]
        text_x = (width - text_w) // 2
        text_y = bc_y + bc_h + 50
        draw.text((text_x, text_y), full_name, fill="#000000", font=font_name)
        
        if not show_barcode_text:
            tc_text = f"TCKN: {tckn}"
            bbox_tc = draw.textbbox((0, 0), tc_text, font=font_tckn)
            tc_w = bbox_tc[2] - bbox_tc[0]
            draw.text(((width - tc_w) // 2, text_y + 55), tc_text, fill="#475569", font=font_tckn)

    # 3. KOMBİNE MOD (QR KOD + BARKOD BİRLİKTE)
    else:
        # Üstte QR Kod
        qr_img = generate_qr_image(tckn, box_size=9, border=2)
        qr_w, qr_h = qr_img.size
        qr_x = (width - qr_w) // 2
        qr_y = start_y + 5
        card.paste(qr_img, (qr_x, qr_y))
        
        # Ortada Barkod
        bc_img = generate_barcode_image(
            tckn,
            barcode_type=barcode_type,
            show_text=show_barcode_text,
            module_width=0.40,
            module_height=14.0,
            font_size=15
        )
        if bc_img.width > (width - 80):
            ratio = (width - 80) / bc_img.width
            new_h = int(bc_img.height * ratio)
            bc_img = bc_img.resize((width - 80, new_h), Image.Resampling.LANCZOS)
            
        bc_w, bc_h = bc_img.size
        bc_x = (width - bc_w) // 2
        bc_y = qr_y + qr_h + 20
        card.paste(bc_img, (bc_x, bc_y))
        
        # Altta İsim
        bbox = draw.textbbox((0, 0), full_name, font=font_name)
        text_w = bbox[2] - bbox[0]
        text_x = (width - text_w) // 2
        text_y = bc_y + bc_h + 25
        draw.text((text_x, text_y), full_name, fill="#000000", font=font_name)

    return card


def create_grid_printable_pages(
    workers: list[tuple[str, str, str]],
    items_per_row: int = 3,
    rows_per_page: int = 4,
    code_mode: str = "qr",
    barcode_type: str = "code128",
    show_barcode_text: bool = True,
    company_title: str = ""
) -> list[Image.Image]:
    """
    Birden fazla işçi için A4 sayfasına yan yana 3'lü dizilimde kağıt tasarrufu sağlayan
    yazdırılabilir A4 sayfa görselleri oluşturur (2480 x 3508 px - 300 DPI yüksek kalite).
    QR, Barkod veya Kombine modunu destekler.
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
    
    font_name = get_system_font(34, bold=True)
    font_tc = get_system_font(24, bold=False)

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
        
        full_name = f"{name.upper()} {surname.upper()}".strip()
        if not full_name:
            full_name = "-"

        # 1. YALNIZCA QR MODU
        if code_mode == "qr":
            qr_img = generate_qr_image(tckn, box_size=12, border=2)
            qr_w, qr_h = qr_img.size
            qr_x = x + (cell_w - qr_w) // 2
            qr_y = y + 35
            current_page.paste(qr_img, (qr_x, qr_y))
            
            bbox = draw.textbbox((0, 0), full_name, font=font_name)
            text_w = bbox[2] - bbox[0]
            text_x = x + (cell_w - text_w) // 2
            text_y = qr_y + qr_h + 20
            draw.text((text_x, text_y), full_name, fill="#000000", font=font_name)
            
            tc_str = f"TC: {tckn}"
            bbox_tc = draw.textbbox((0, 0), tc_str, font=font_tc)
            tc_w = bbox_tc[2] - bbox_tc[0]
            draw.text((x + (cell_w - tc_w) // 2, text_y + 45), tc_str, fill="#64748B", font=font_tc)

        # 2. YALNIZCA BARKOD MODU
        elif code_mode == "barcode":
            bc_img = generate_barcode_image(
                tckn,
                barcode_type=barcode_type,
                show_text=show_barcode_text,
                module_width=0.44,
                module_height=24.0,
                font_size=16
            )
            if bc_img.width > (cell_w - 40):
                ratio = (cell_w - 40) / bc_img.width
                bc_img = bc_img.resize((cell_w - 40, int(bc_img.height * ratio)), Image.Resampling.LANCZOS)
                
            bc_w, bc_h = bc_img.size
            bc_x = x + (cell_w - bc_w) // 2
            bc_y = y + 160
            current_page.paste(bc_img, (bc_x, bc_y))
            
            bbox = draw.textbbox((0, 0), full_name, font=font_name)
            text_w = bbox[2] - bbox[0]
            text_x = x + (cell_w - text_w) // 2
            text_y = bc_y + bc_h + 40
            draw.text((text_x, text_y), full_name, fill="#000000", font=font_name)

        # 3. KOMBİNE MOD (QR + BARKOD)
        else:
            qr_img = generate_qr_image(tckn, box_size=8, border=2)
            qr_w, qr_h = qr_img.size
            qr_x = x + (cell_w - qr_w) // 2
            qr_y = y + 25
            current_page.paste(qr_img, (qr_x, qr_y))
            
            bc_img = generate_barcode_image(
                tckn,
                barcode_type=barcode_type,
                show_text=show_barcode_text,
                module_width=0.38,
                module_height=12.0,
                font_size=14
            )
            if bc_img.width > (cell_w - 40):
                ratio = (cell_w - 40) / bc_img.width
                bc_img = bc_img.resize((cell_w - 40, int(bc_img.height * ratio)), Image.Resampling.LANCZOS)
                
            bc_w, bc_h = bc_img.size
            bc_x = x + (cell_w - bc_w) // 2
            bc_y = qr_y + qr_h + 15
            current_page.paste(bc_img, (bc_x, bc_y))
            
            bbox = draw.textbbox((0, 0), full_name, font=font_name)
            text_w = bbox[2] - bbox[0]
            text_x = x + (cell_w - text_w) // 2
            text_y = bc_y + bc_h + 20
            draw.text((text_x, text_y), full_name, fill="#000000", font=font_name)

    return pages


def smart_extract_tckn(cell_value) -> str:
    """
    Herhangi bir hücre değerinden 11 haneli TC Kimlik / YKN numarasını yakalar.
    """
    if cell_value is None:
        return ""
        
    s = str(cell_value).strip()
    if not s:
        return ""
        
    # Bilimsel gösterim veya float temizliği (Örn: 10000000146.0 -> 10000000146)
    if isinstance(cell_value, (float, int)):
        try:
            s = f"{cell_value:.0f}"
        except Exception:
            pass
    elif s.endswith(".0"):
        s = s[:-2]
        
    # Sadece rakamları ayıkla
    clean_digits = "".join([c for c in s if c.isdigit()])
    
    # 1. Hücre direkt 11 haneli ve 0 ile başlamıyorsa (TCKN / YKN)
    if len(clean_digits) == 11 and clean_digits[0] != '0':
        return clean_digits
            
    # 2. Hücre içindeki 11 haneli dizilimleri regex ile arama
    matches = re.findall(r'\d{11}', s)
    for m in matches:
        if m[0] != '0':
            return m
            
    return ""


def smart_parse_excel_or_csv(filepath: str) -> list[dict]:
    """
    Satır, sütun veya sayfa yeri ne olursa olsun Excel / CSV dosyasındaki TÜM işçileri
    (Ad, Soyad, TC No) tam doğrulukla çıkarır.
    """
    all_sheet_rows = []
    
    # 1. Dosyadaki tüm sayfaları ve tüm hücreleri oku
    if filepath.lower().endswith(".csv"):
        sheet_rows = []
        for encoding in ["utf-8-sig", "utf-8", "cp1254", "iso-8859-9", "latin-1"]:
            try:
                with open(filepath, mode="r", encoding=encoding) as f:
                    reader = csv.reader(f)
                    for r in reader:
                        sheet_rows.append([str(cell).strip() if cell else "" for cell in r])
                break
            except Exception:
                continue
        if sheet_rows:
            all_sheet_rows.append(sheet_rows)
    else:
        import openpyxl
        try:
            wb = openpyxl.load_workbook(filepath, data_only=True)
            for sheet in wb.worksheets:
                sheet_rows = []
                for row in sheet.iter_rows(values_only=True):
                    row_cells = []
                    for cell in row:
                        if cell is not None:
                            if isinstance(cell, (float, int)):
                                if isinstance(cell, float) and cell.is_integer():
                                    row_cells.append(str(int(cell)))
                                else:
                                    row_cells.append(f"{cell:.0f}" if isinstance(cell, float) else str(cell))
                            else:
                                row_cells.append(str(cell).strip())
                        else:
                            row_cells.append("")
                    if any(row_cells):
                        sheet_rows.append(row_cells)
                if sheet_rows:
                    all_sheet_rows.append(sheet_rows)
        except Exception as e:
            print(f"Excel Okuma Hatası: {e}")

    workers = []
    seen_tcs = set()

    for raw_rows in all_sheet_rows:
        for row in raw_rows:
            if not any(row):
                continue
                
            tckn_found = ""
            tc_col_idx = -1
            
            # Satırda 11 haneli TC Kimlik / YKN ara
            for col_idx, cell_val in enumerate(row):
                cand = smart_extract_tckn(cell_val)
                if cand and cand not in seen_tcs:
                    tckn_found = cand
                    tc_col_idx = col_idx
                    break
                    
            if not tckn_found:
                continue
                
            # TC bulundu! Şimdi aynı satırdaki diğer hücrelerden Ad ve Soyad çıkar
            text_candidates = []
            for col_idx, cell_val in enumerate(row):
                if col_idx == tc_col_idx:
                    continue
                    
                val_str = str(cell_val).strip()
                if not val_str:
                    continue
                    
                clean_text = re.sub(r'^\d+[\s\.\-\)]*', '', val_str).strip()
                if not clean_text:
                    continue
                    
                if clean_text.isdigit() or clean_text.replace('.', '', 1).isdigit():
                    continue
                    
                val_upper = clean_text.upper()
                if val_upper in ["TC", "TCKN", "TC NO", "T.C.", "T.C. KİMLİK NO", "AD", "SOYAD", "AD SOYAD", "İSİM", "SOYİSİM", "SIRA NO", "NO", "SIRA", "PERSONEL", "NOT", "ACİL", "DURUM", "AÇIKLAMA", "TARİH", "KAYIT"]:
                    continue
                    
                text_candidates.append(clean_text)

            name = ""
            surname = ""
            
            multi_word_cells = [c for c in text_candidates if len(c.split()) >= 2]
            if multi_word_cells:
                target = multi_word_cells[0]
                parts = target.split()
                surname = parts[-1]
                name = " ".join(parts[:-1])
            elif len(text_candidates) >= 2:
                name = text_candidates[0]
                surname = text_candidates[1]
            elif len(text_candidates) == 1:
                name = text_candidates[0]
                surname = ""
            else:
                name = "İŞÇİ"
                surname = f"({tckn_found[-4:]})"

            workers.append({
                "name": name.strip(),
                "surname": surname.strip(),
                "tckn": tckn_found
            })
            seen_tcs.add(tckn_found)

    return workers
