# İşçi TC Kimlik QR Kod Oluşturma ve Yazdırma Programı

Bu masaüstü uygulaması, işçilerinizin TC Kimlik Numaralarına göre doğrulanmış QR kodlar üretmesini, cep telefonu veya barkod okuyucu ile taratıldığında doğrudan TC Kimlik Numarasının çıkmasını ve Windows yazıcı seçimi ile kart/etiket şeklinde çıktı alınmasını sağlar.

---

## 🚀 Özellikler

- **Çoklu Seçim ve Kağıt Tasarruflu Yazdırma (3'lü Izgara):** Tablodan `Ctrl` veya `Shift` tuşlarıyla dilediğiniz kadar işçiyi seçebilir, QR kodları tek bir A4 sayfasına **yan yana 3 tane** gelecek şekilde (3x4 = sayfada 12 kart) yazdırarak kağıt tasarrufu sağlayabilirsiniz.
- **Esnek Excel / CSV İçe Aktarma:** Excel dosyanızdaki `İsim`, `Ad`, `Soyad`, `Soyisim`, `TC`, `TCKN` kolonlarını otomatik tanıyıp listeye aktarır.
- **11 Haneli TC Kimlik Doğrulaması:** Girilen TC Kimlik numarasının uzunluğunu ve matematiksel algoritma kuralını canlı kontrol eder.
- **Doğrudan TC Çıktılı QR Kod:** QR kod taratıldığında ekranda doğrudan işçinin 11 haneli TC Kimlik Numarası görünür.
- **Yazıcı Seçimi ve Çıktı Alma:** Bilgisayarınıza bağlı olan tüm yazıcıları listeleyip seçilen yazıcıdan yüksek kaliteli çıktı alır.
- **Toplu Görsel Dışa Aktarma:** Tüm kayıtlı işçilerin QR kod kartlarını seçilen bir klasöre `.png` formatında kaydeder.
- **Arama ve Filtreleme:** Kayıtlı işçiler arasında isim, soyisim veya TC Kimlik No ile anlık arama yapabilir.

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
├── main.py            # Ana masaüstü grafik arayüzü (GUI) ve tablo yönetimi
├── qr_generator.py    # TC doğrulama, QR kod üretimi ve kart tasarımı
├── printer_service.py # Windows yazıcı seçimi ve doğrudan çıktı alma servisi
├── requirements.txt   # Gerekli Python kütüphaneleri
└── README.md          # Proje açıklama ve kullanım rehberi
```

---

## 📖 Kullanım Adımları

1. **İşçi Ekleme:** Sol paneldeki `İşçi Adı`, `İşçi Soyadı` ve `TC Kimlik No` alanlarını doldurun.
2. **QR Kod Oluşturma:** **"QR Kod Oluştur"** butonuna basarak kart önizlemesini inceleyin.
3. **Listeye Kaydet:** İsterseniz **"Listeye Kaydet"** butonuna basarak işçiyi sağ taraftaki tabloya ekleyin.
4. **Yazıcı Çıktısı Alma:** **"🖨️ Yazıcı Seç ve Yazdır"** butonuna basın, açılan pencereden çıktı almak istediğiniz yazıcıyı seçerek **"Yazdır"**a tıklayın.
5. **Excel'den Aktarma:** Sağ alt kısımdaki **"📂 Excel/CSV'den Aktar"** butonunu kullanarak toplu işçi ekleyebilirsiniz.
