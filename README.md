# İşçi TC Kimlik QR Kod ve Barkod Oluşturma & Yazdırma Programı

Bu profesyonel masaüstü uygulaması, işçilerinizin TC Kimlik Numaralarına göre doğrulanmış **2D QR Kodlar (Karekod)** ve endüstri standardında **1D Çizgi Barkodlar (Code 128 & Code 39)** üretmesini; cep telefonu, el terminali veya lazer barkod okuyucu ile taratıldığında doğrudan TC Kimlik Numarasının çıkmasını ve Windows yazıcı seçimi ile kart/etiket şeklinde çıktı alınmasını sağlar.

---

## 🚀 Özellikler

- **Çoklu Kod Standardı (QR & Barkod):**
  - 📱 **QR Kod (Karekod - 2D):** Akıllı telefon kameraları ve 2D okuyucular için.
  - 📊 **Çizgi Barkod (Code 128 & Code 39 - 1D):** Lazer barkod tabancaları, el terminalleri ve POS sistemleri için yüksek yoğunluklu barkod.
  - 🔄 **Kombine Kart (QR + Barkod):** Hem QR kodun hem de barkodun tek bir yaka kartında yer aldığı çift okuma uyumlu kart modu.
- **Canlı Kod Önizleme ve Format Geçişi:** Kod tipi veya işçi bilgisi değiştirildiği anda yüksek çözünürlüklü önizleme.
- **Çoklu Seçim ve Kağıt Tasarruflu Yazdırma (A4 3'lü Izgara):** Tablodan `Ctrl` veya `Shift` tuşlarıyla dilediğiniz kadar işçiyi seçebilir, kartları tek bir A4 sayfasına **yan yana 3 tane** gelecek şekilde (3x4 = sayfada 12 kart) kesim çizgileriyle yazdırabilirsiniz.
- **Esnek Excel / CSV İçe Aktarma:** Excel dosyanızdaki sütun düzeni fark etmeksizin 11 haneli TC Kimlik numaralarını ve Ad-Soyad verilerini otomatik tespit edip aktarır.
- **11 Haneli TC Kimlik Algoritma Doğrulaması:** Girilen TC Kimlik numarasının biçimini ve matematiksel doğrulama algoritmasını canlı denetler.
- **Yazıcı Seçimi ve Doğrudan Çıktı:** Bilgisayarınıza bağlı olan tüm yerel ve ağ yazıcılarını listeleyip seçilen yazıcıdan yüksek kaliteli çıktı alır.
- **Gelişmiş Toplu Dışa Aktarma:** Sistemdeki tüm işçilerin görsellerini tek seferde `.png` formatında klasöre aktarabilirsiniz:
  - *Hazır Baskı Kartları / Etiketleri*
  - *Yalnızca QR Kodlar*
  - *Yalnızca Çizgi Barkodlar*
- **Arama, Filtreleme ve Panoya Kopyalama:** İsim, soyisim veya TC No ile anlık arama ve tek tuşla TC Kimlik kopyalama.

---

## 🛠️ Kurulum ve Çalıştırma

### 1. Gereksinimlerin Yüklenmesi
Sistemde Python 3.10+ kurulu olmalıdır. Gerekli kütüphaneleri yüklemek için terminal veya komut satırında şu komutu çalıştırın:

```bash
pip install -r requirements.txt
```

### 2. Uygulamanın Çalıştırılması
Uygulama arayüzünü başlatmak için:

```bash
python main.py
```

---

## 📁 Proje Yapısı

```text
├── main.py            # Ana masaüstü grafik arayüzü (GUI), kod kontrolleri ve tablo yönetimi
├── qr_generator.py    # TC doğrulama, QR kod & Barkod üretimi ve kart tasarımı
├── printer_service.py # Windows yazıcı seçimi ve doğrudan çıktı alma servisi
├── requirements.txt   # Gerekli Python kütüphaneleri (qrcode, python-barcode, pillow, pywin32, openpyxl)
└── README.md          # Proje açıklama ve kullanım rehberi
```

---

## 📖 Kullanım Adımları

1. **İşçi Bilgilerini Girin:** Sol paneldeki `İşçi Adı`, `İşçi Soyadı` ve `TC Kimlik No` alanlarını doldurun. (İsteğe bağlı firma başlığı eklenebilir).
2. **Kod Türünü Seçin:** `QR Kod (2D)`, `Çizgi Barkod (1D)` veya `QR + Barkod (Kombine)` seçeneklerinden birini belirleyin.
3. **Kart Önizlemesini İnceleyin:** Kartınız anında yüksek çözünürlükte sağ taraftaki önizleme alanında oluşturulur.
4. **Listeye Kaydedin:** **"➕ Listeye Kaydet"** butonuna basarak işçiyi tabloya ekleyin.
5. **Yazdırın:**
   - **Tek Kart:** **"🖨️ Yazıcı Seç ve Yazdır"** butonuna tıklayarak doğrudan yazıcıya gönderin.
   - **Toplu Seçim:** Tablodan birden fazla işçi seçip **"🖨️ Seçilenleri Yazdır (A4 3'lü)"** butonuna basın.
6. **Excel'den Aktarma:** **"📂 Excel/CSV'den Aktar"** butonu ile yüzlerce personeli tek tıkla sisteme aktarın.
