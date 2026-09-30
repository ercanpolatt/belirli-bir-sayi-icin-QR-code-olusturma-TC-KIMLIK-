<div align="center">

# 🏷️ Barkod & QR Kod Studio
**Excel ve Baskı Entegrasyonlu Profesyonel Barkod Yönetim Sistemi**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)]()

Barkod & QR Kod Studio, özellikle TC Kimlik numaraları, personel kodları, ürün seri numaraları ve özel metinler için gelişmiş **1D Barkod** ve **2D QR Kod** üretimi sağlayan profesyonel bir masaüstü uygulamasıdır. Gelişmiş Excel entegrasyonu, toplu üretim özellikleri ve A4 baskı yetenekleriyle iş süreçlerinizi hızlandırır.

</div>

---

## ✨ Öne Çıkan Özellikler

🚀 **Gelişmiş Kod Üretimi**
* **Çoklu Format Desteği:** QR Kod (2D) ve 1D Barkodlar (Code 128, Code 39, EAN-13, EAN-8, UPC-A).
* **Kombine Kartlar:** Tek bir kart üzerinde hem QR kod hem de Barkod barındırabilme.
* **Akıllı Doğrulama:** 11 Haneli TC Kimlik numaraları için matematiksel algoritma kontrolü (İsteğe bağlı sıkı denetim).

📊 **Excel ve Pano Entegrasyonu**
* **Görselli Dışa Aktarım:** Oluşturulan barkodları hücre içine gömülü resimler olarak Excel'e aktarma.
* **Hızlı İçe Aktarım:** Excel, CSV dosyalarından veya doğrudan panodan (Ctrl+C / Ctrl+V) akıllı veri çekimi.

🖨️ **Profesyonel Baskı ve Çıktı**
* **A4 Grid Baskı:** Toplu kayıtları otomatik olarak A4 sayfalarına 3'lü sütunlar halinde (grid) dizme ve Word/Excel'e yapıştırılacak formata getirme.
* **Canlı Önizleme:** Arayüz üzerinden anlık görsel önizleme.
* **Panoya Kopyalama:** Tek bir barkodu veya A4 sayfalarını doğrudan Windows panosuna kopyalayarak başka programlara resim olarak yapıştırabilme.

🔢 **Seri Üretim**
* **Toplu Sıralı Kod:** Belirli bir ön ek, başlangıç numarası ve basamak sayısıyla tek tıkla yüzlerce sıralı barkod üretimi (Örn: URUN-0001, URUN-0002).

---

## 📸 Ekran Görüntüleri ve Özellikler

Uygulamanın modern ve kullanımı kolay arayüzü sayesinde işlemlerinizi saniyeler içinde tamamlayabilirsiniz. İster tekli ister toplu olsun, barkod ve QR kod üretim süreci tamamen hız ve görsellik üzerine tasarlanmıştır.

<div align="center">
  <img src="photos/uygulama%20arayuzu.png" alt="Ana Arayüz" width="800"/>
  <p><i>Geniş, Detaylı ve Kullanıcı Dostu Uygulama Arayüzü</i></p>
</div>

<br/>

### 1. Toplu A4 Formatında Çıktı ve Baskı
Oluşturduğunuz tüm kodları otomatik hesaplayarak A4 boyutlarına uygun, şık bir grid (ızgara) sisteminde dizer. Bu sayede seçtiğiniz onlarca personelin veya ürünün kodlarını tek bir hamleyle A4 kağıdına yazdırabilir, Word veya Excel dosyalarına kalitesi bozulmadan kopyalayabilirsiniz.

<div align="center">
  <img src="photos/toplu%20a4%20formati.png" alt="A4 Baskı Modu" width="700"/>
  <p><i>A4 Sayfa Grid Dizilimi ve Profesyonel Baskı Çıktısı</i></p>
</div>

### 2. Yüksek Kaliteli PNG Çıktısı ve Tekli Kayıt
Her bir barkod veya QR kod, standartlara uygun ve yüksek kalitede üretilir. Kodu anında PNG olarak kaydedebilir veya "Görseli Kopyala" diyerek doğrudan başka bir uygulamaya (Photoshop, Illustrator, Excel vb.) yapıştırabilirsiniz.

<div align="center">
  <img src="photos/png%20formati%20.png" alt="PNG Formatında Çıktı" width="650"/>
  <p><i>Detaylı, Okunabilir ve Temiz PNG Kod Formatı</i></p>
</div>

---

## 🛠️ Kurulum ve Çalıştırma

### Gereksinimler
Uygulamanın çalışması için sisteminizde **Python 3.8 veya üzeri** yüklü olmalıdır.

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/kullaniciadi/proje-adi.git
cd proje-adi
```

### 2. Gerekli Kütüphaneleri Yükleyin
Tüm bağımlılıklar `requirements.txt` dosyasında listelenmiştir. Yüklemek için:
```bash
pip install -r requirements.txt
```

**Temel Bağımlılıklar:**
* `Pillow` (Görsel işleme)
* `qrcode` (QR kod üretimi)
* `python-barcode` (1D Barkod üretimi)
* `openpyxl` (Excel işlemleri)
* `pywin32` (Windows pano etkileşimleri ve yazdırma)

### 3. Uygulamayı Başlatın
```bash
python main.py
```

---

## 📋 Kullanım İpuçları ve Kısayollar

| Kısayol | İşlem |
| :--- | :--- |
| `Ctrl + C` | Tabloda seçili satırları Excel uyumlu formatta metin olarak kopyalar. |
| `Ctrl + Shift + C` | Önizlemedeki mevcut barkod **görselini** kopyalar (Word/Excel'e resim olarak yapıştırmak için). |
| `Ctrl + V` | Excel'den kopyaladığınız satırları tabloya aktarır. |
| `Ctrl + A` | Tablodaki tüm kayıtları seçer. |
| `Ctrl + P` | Seçili kayıtları doğrudan varsayılan yazıcıya gönderir. |
| `Delete` | Tablodaki seçili kayıtları siler. |

---

## 📂 Proje Yapısı

```text
📦 Proje Klasörü
 ┣ 📜 main.py              # Ana GUI uygulamasının başlatıldığı dosya (Tkinter)
 ┣ 📜 qr_generator.py      # QR, Barkod üretimi ve görsel işleme (Pillow) motoru
 ┣ 📜 printer_service.py   # Windows yazdırma (win32print) işlemleri
 ┣ 📜 requirements.txt     # Python kütüphane bağımlılıkları
 ┗ 📜 workers.db           # (Otomatik oluşturulur) Kayıtların tutulduğu SQLite veritabanı
```

---

## 🤝 Katkıda Bulunma

1. Bu depoyu forklayın.
2. Yeni bir özellik dalı oluşturun (`git checkout -b ozellik/YeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Dalınızı push edin (`git push origin ozellik/YeniOzellik`)
5. Bir Pull Request oluşturun.

## 📄 Lisans
Bu proje MIT Lisansı ile lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına bakabilirsiniz.
