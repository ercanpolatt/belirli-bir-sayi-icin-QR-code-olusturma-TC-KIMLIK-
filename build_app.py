"""
PyInstaller Otomatik Derleme ve Paketleme Scripti
Barkod & QR Kod Studio uygulamasını Python gerektirmeyen bağımsız masaüstü (.exe) haline getirir.
"""
import os
import sys
import shutil
import subprocess

def build():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    app_name = "Barkod_ve_QR_Kod_Studio"
    icon_file = os.path.join(current_dir, "app_icon.ico")
    main_file = os.path.join(current_dir, "main.py")
    db_file = os.path.join(current_dir, "workers.db")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=" + app_name,
        "--noconsole",
        "--clean",
        "--noconfirm",
    ]
    
    if os.path.exists(icon_file):
        cmd.append(f"--icon={icon_file}")
        cmd.append(f"--add-data={icon_file};.")
        
    hidden_imports = [
        "win32print",
        "win32ui",
        "win32con",
        "win32clipboard",
        "PIL",
        "PIL.Image",
        "PIL.ImageTk",
        "PIL.ImageWin",
        "PIL.ImageDraw",
        "PIL.ImageFont",
        "qrcode",
        "barcode",
        "barcode.writer",
        "openpyxl",
        "sqlite3",
    ]
    for imp in hidden_imports:
        cmd.append(f"--hidden-import={imp}")
        
    cmd.append(main_file)
    
    print("PyInstaller derleme başlatılıyor...")
    print("Komut:", " ".join(cmd))
    
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"HATA: Derleme başarısız oldu (Hata kodu: {result.returncode})")
        return False
        
    # dist klasöründeki çıktı dizinine workers.db kopyala (Mevcut kayıtlar korunsun)
    dist_dir = os.path.join(current_dir, "dist", app_name)
    if os.path.exists(dist_dir) and os.path.exists(db_file):
        target_db = os.path.join(dist_dir, "workers.db")
        if not os.path.exists(target_db):
            shutil.copy2(db_file, target_db)
            print(f"[OK] Mevcut personellerin veritabanı kopyalandı: {target_db}")
            
    print("\n" + "="*60)
    print("TEBRIKLER! Uygulama basariyla derlendi.")
    print(f"Uygulama klasoru: {dist_dir}")
    print(f"Calistirilabilir dosya: {os.path.join(dist_dir, app_name + '.exe')}")
    print("="*60)
    return True

if __name__ == "__main__":
    build()
