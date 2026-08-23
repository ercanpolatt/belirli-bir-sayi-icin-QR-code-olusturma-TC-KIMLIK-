"""
Windows Yazıcı Hizmeti Modülü
Sistemde tanımlı yazıcıları listeler ve seçilen yazıcıya QR kartı görselini gönderir.
"""
import os
import tempfile
from PIL import Image, ImageWin
import win32print
import win32ui
import win32con


def get_installed_printers() -> list[str]:
    """
    Sistemde yüklü olan tüm yazıcıların isimlerini döndürür.
    """
    printers = []
    try:
        # PRINTER_ENUM_LOCAL ve PRINTER_ENUM_CONNECTIONS ile tüm local ve ağ yazıcıları
        printer_info = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        for p in printer_info:
            printers.append(p[2])
    except Exception as e:
        print(f"Yazıcılar listelenirken hata: {e}")
    return printers


def get_default_printer() -> str:
    """
    Varsayılan Windows yazıcısının adını getirir.
    """
    try:
        return win32print.GetDefaultPrinter()
    except Exception:
        return ""


def print_image_to_printer(image: Image.Image, printer_name: str = None, doc_name: str = "İşçi QR/Barkod Kartı") -> tuple[bool, str]:
    """
    Verilen PIL Image görselini seçilen yazıcıya doğrudan gönderir.
    Yazıcı ismi verilmezse varsayılan yazıcıyı kullanır.
    """
    if not printer_name:
        printer_name = get_default_printer()
        
    if not printer_name:
        return False, "Sistemde kullanılabilir varsayılan bir yazıcı bulunamadı."
        
    try:
        # Printer DC (Device Context) oluşturma
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer_name)
        
        # Yazıcı çözünürlük bilgileri
        printable_width = hDC.GetDeviceCaps(win32con.HORZRES)
        printable_height = hDC.GetDeviceCaps(win32con.VERTRES)
        
        # Görsel boyutlandırma (Orantılı sığdırma)
        img_w, img_h = image.size
        aspect_ratio = img_w / img_h
        
        # Sayfaya uygun hedef boyut belirleme (Etiket veya A4 sayfasının üst kısmına uygun)
        target_w = int(printable_width * 0.8)
        target_h = int(target_w / aspect_ratio)
        
        if target_h > int(printable_height * 0.8):
            target_h = int(printable_height * 0.8)
            target_w = int(target_h * aspect_ratio)
            
        # Merkeze hizalama
        x1 = (printable_width - target_w) // 2
        y1 = (printable_height - target_h) // 2
        x2 = x1 + target_w
        y2 = y1 + target_h
        
        # Yazdırma işini başlatma
        hDC.StartDoc(doc_name)
        hDC.StartPage()
        
        # PIL Image'i Windows Dib (Device Independent Bitmap) formatına çevirme
        dib = ImageWin.Dib(image)
        dib.draw(hDC.GetHandleOutput(), (x1, y1, x2, y2))
        
        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()
        
        return True, f"Başarıyla '{printer_name}' yazıcısına gönderildi."
        
    except Exception as e:
        # Hata durumunda alternatif yöntem: Geçici dosyaya kaydedip Windows shell print çağırma
        try:
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, "temp_code_badge.png")
            image.save(temp_path)
            os.startfile(temp_path, "print")
            return True, "Yazdırma penceresi açıldı."
        except Exception as alt_err:
            return False, f"Yazdırma hatası: {str(e)} / {str(alt_err)}"


def print_images_to_printer(images: list[Image.Image], printer_name: str = None, doc_name: str = None) -> tuple[bool, str]:
    """
    Birden fazla sayfa görselini (PIL Image listesi) seçilen yazıcıya tek bir yazdırma işi olarak gönderir.
    """
    if not images:
        return False, "Yazdırılacak sayfa görseli bulunamadı."
        
    if not printer_name:
        printer_name = get_default_printer()
        
    if not printer_name:
        return False, "Sistemde kullanılabilir varsayılan bir yazıcı bulunamadı."
        
    try:
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer_name)
        
        printable_width = hDC.GetDeviceCaps(win32con.HORZRES)
        printable_height = hDC.GetDeviceCaps(win32con.VERTRES)
        
        job_title = doc_name or f"İşçi Kartları Yazdırma İşlemi ({len(images)} Sayfa)"
        hDC.StartDoc(job_title)
        
        for img in images:
            hDC.StartPage()
            
            img_w, img_h = img.size
            aspect_ratio = img_w / img_h
            
            target_w = printable_width
            target_h = int(target_w / aspect_ratio)
            
            if target_h > printable_height:
                target_h = printable_height
                target_w = int(target_h * aspect_ratio)
                
            x1 = (printable_width - target_w) // 2
            y1 = (printable_height - target_h) // 2
            x2 = x1 + target_w
            y2 = y1 + target_h
            
            dib = ImageWin.Dib(img)
            dib.draw(hDC.GetHandleOutput(), (x1, y1, x2, y2))
            
            hDC.EndPage()
            
        hDC.EndDoc()
        hDC.DeleteDC()
        
        return True, f"Toplam {len(images)} sayfa başarıyla '{printer_name}' yazıcısına gönderildi."
        
    except Exception as e:
        try:
            temp_dir = tempfile.gettempdir()
            for idx, img in enumerate(images):
                temp_path = os.path.join(temp_dir, f"temp_qr_page_{idx}.png")
                img.save(temp_path)
                os.startfile(temp_path, "print")
            return True, f"Yazdırma pencereleri açıldı ({len(images)} sayfa)."
        except Exception as alt_err:
            return False, f"Yazdırma hatası: {str(e)} / {str(alt_err)}"

