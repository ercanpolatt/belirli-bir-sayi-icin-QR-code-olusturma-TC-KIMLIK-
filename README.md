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

## 📸 Ekran Görüntüleri ve Kullanım

> **Not:** Lütfen uygulamanın ekran görüntülerini ve örnek çıktılarını proje klasöründeki `assets` veya `images` klasörüne ekleyip aşağıdaki bağlantıları güncelleyiniz.

<div align="center">
  <img src="https://via.placeholder.com/800x450.png?text=Ana+Arayuz+Ekrani" alt="Ana Arayüz" width="800"/>
  <p><i>Uygulama Ana Arayüzü ve Canlı Önizleme Paneli</i></p>
</div>

<br/>

### 1. Barkod ve QR Oluşturma
Sadece kodu (veya TC Kimlik no) girin. İsteğe bağlı olarak İsim, Soyisim ve Kurum Başlığı ekleyebilirsiniz. Sistem, geçersiz TC numaralarında sizi uyarır.

<div align="center">
  <img src="https://via.placeholder.com/400x300.png?text=Barkod+Olusturma" alt="Kayıt" width="400"/>
  <img src="https://via.placeholder.com/400x300.png?text=QR+ve+Kombine+Mod" alt="Modlar" width="400"/>
</div>

### 2. Excel'e Görselli Aktarım
Tablodaki seçili kayıtları veya tümünü, barkod görselleri hücrelere yerleştirilmiş biçimde Excel (.xlsx) olarak dışa aktarabilirsiniz.

### 3. A4 Toplu Baskı
Oluşturduğunuz kodları A4 kağıdına uygun grid sisteminde dizer. İster doğrudan yazdırın, ister Word'e yapıştırın.

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
