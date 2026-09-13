# Barkod & QR Kod Studio | Excel & Baskı Entegrasyonu

Bu masaüstü uygulaması; **belirlediğiniz herhangi bir sayı, harf, seri numarası, ürün kodu veya TC Kimlik Numarası** ile endüstri standardında **1D Çizgi Barkodlar (Code 128, Code 39, EAN-13, EAN-8, UPC-A)** ve **2D QR Kodlar (Karekod)** üretmenizi, doğrudan Windows panosuna kopyalayarak **Excel'e `Ctrl+V` ile resim olarak yapıştırmanızı**, Excel tabloları ile çift yönlü senkronizasyon yapmanızı ve Windows yazıcınızdan tekli veya A4 sayfasında 3'lü dizilimle (300 DPI) çıktı almanızı sağlar.

---

## 🚀 Öne Çıkan Özellikler

### 📊 1. Gelişmiş Excel & Pano Entegrasyonu
- **🖼️ Barkod Görsellerini Excel Hücrelerine Gömerek Aktarma:** Tablodaki kayıtları Excel'e aktarırken her satırın yanındaki sütuna gerçek barkod/QR kod görselini otomatik gömer.
- **🖼️ Barkod Görselini Panoya Kopyalama (`Ctrl+Shift+C`):** Oluşturulan barkodu dosyaya kaydetmeye gerek kalmadan panoya kopyalar. Excel'e geçip herhangi bir hücreye **`Ctrl+V`** yaptığınızda **barkod görseli doğrudan Excel'e yapışır!**
- **📋 Tabloyu Excel Formatında Kopyalama (`Ctrl+C`):** Tablodan seçtiğiniz satırları `Ctrl+C` ile kopyalayıp Excel'e yapıştırdığınızda veriler ayrı ayrı sütunlara otomatik yerleşir.
- **📥 Excel Panosundan Hızlı Aktarım (`Ctrl+V`):** Excel'de kopyaladığınız satırları dosya açma zahmetine girmeden **"📋 Excel Panosundan Aktar"** butonu veya `Ctrl+V` ile anında sisteme ekler.
- **📊 Doğrudan `.xlsx` Excel Çıktısı Alma:** Tablodaki tüm verileri profesyonel ve renkli biçimlendirilmiş bir Excel tablosu olarak kaydeder.

### ⚡ 2. Seri Kod & Barkod Üretici
- **🔢 Sıralı / Seri Kod Üretimi:** Belirlediğiniz başlangıç numarası, adet, ön ek (örn: `URUN-`) ve basamak sayısına göre saniyeler içinde binlerce sıralı barkod üretip listeye ekler.

### 🖨️ 3. Profesyonel Yazdırma & Tasarruflu A4 Şablonu
- **A4 3'lü Izgara Baskı (300 DPI):** Seçilen kayıtları A4 sayfasına yan yana 3'lü dizilimle (sayfada 12 kart) kesim çizgileriyle yazdırır.
- **Yazıcı Seçimi:** Sistemdeki tüm yerel ve ağ yazıcılarını listeleyip istenilen yazıcıya doğrudan gönderir.

### 📱 4. Kod Standartları & Esneklik
- **Çoklu Barkod Formatları:** Code 128 (Evrensel), Code 39 (Alfanümerik), EAN-13 (Perakende), EAN-8 ve UPC-A standartları.
- **QR Kod & Kombine Kart (QR + Barkod):** Çift okuyucu destekli yaka kartı ve etiket tasarımı.
- **Dinamik Önizleme & High-DPI:** Yüksek çözünürlüklü ekranlarda net tipografi ve pencere boyutuna göre orantılı canlı önizleme.
- **Sütun Sıralama (A-Z / Z-A):** Tablo sütun başlıklarına tıklayarak ID, İsim, Soyisim, Kod ve Tarihe göre artan/azalan anlık sıralama.
- **İsteğe Bağlı Sıkı TC Kimlik Kontrolü:** 11 haneli matematiksel TC algoritma doğrulamasını tek tıkla açıp kapatabilme.

---

## ⌨️ Klavye Kısayolları

| Kısayol | İşlev |
|---|---|
| **Ctrl + C** | Tablodaki seçili satırları Excel formatında panoya kopyalar |
| **Ctrl + Shift + C** | Aktif barkod görselini panoya kopyalar (Excel'e `Ctrl+V` ile resim yapıştırılır) |
| **Ctrl + V** | Excel'den kopyalanan satırları doğrudan programa yapıştırıp kaydeder |
| **Ctrl + A** | Tablodaki tüm kayıtları seçer |
| **Ctrl + P** | Seçilen kayıtları yazıcıya gönderir |
| **Delete** | Seçilen kayıtları tablodan siler |

---

## 🛠️ Kurulum ve Çalıştırma

```bash
pip install -r requirements.txt
python main.py
```
