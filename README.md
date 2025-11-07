# CRM Analytics – FLO RFM Segmentasyonu & CLTV Prediction

Bu proje, FLO müşteri verisi üzerinde hem **RFM Segmentasyonu** hem de **CLTV Prediction** çalışmalarını içeren bir CRM analitiği uygulamasıdır.

---

## 📌 Proje Amaçları

### ✔️ RFM Segmentasyonu  (`src/refm_segmentation.py`)
- Müşterilerin **Recency – Frequency – Monetary** değerlerini hesaplar.
- Regex tabanlı segmentasyon ile müşterileri gruplara ayırır:
  `champions`, `loyal_customers`, `cant_loose`, `about_to_sleep`, `at_Risk`, vb.
- İş senaryolarına göre hedef müşteri listelerini CSV olarak üretir:

| İş Senaryosu | Açıklama | Çıktı |
|--------------|----------|--------|
| Görev 5-a | Yeni kadın ayakkabı markası → kadın kategorisinde alışveriş yapan champions & loyal müşteriler | `loyal_champ_woman_customers.csv` |
| Görev 5-b | Erkek / Çocuk ürünlerinde indirim → uzun süredir alışveriş yapmayan sadık müşteriler | `discount_male_kids.csv` |

---

### ✔️ CLTV Prediction  (`src/cltv_prediction.py`)
- BG-NBD ve Gamma–Gamma modelleri ile **6 aylık CLTV tahmini** yapar.
- Müşterileri CLTV değerine göre segmentlere ayırır.
- Sonuçları CSV olarak kaydeder:

| Çıktı | Amaç |
|-------|------|
| `cltv_output_6m.csv` | Tahmini 6 aylık müşteri yaşam boyu değeri |

---

## 📂 Proje Yapısı

crm-analitics/

├─ Datasets/

│ 

└─ flo_data_20k.csv

├─ src/

│ 

├─ refm_segmentation.py

│ 

└─ cltv_prediction.py

├─ requirements.txt

├─ loyal_champ_woman_customers.csv # RFM çıktısı (Görev 5-a)

├─ discount_male_kids.csv # RFM çıktısı (Görev 5-b)

└─ cltv_output_6m.csv # CLTV çıktısı


> **⚠️ Veri seti repoya dahil edilmez.**  
> `.gitignore` ile `Datasets/` klasörü gizlenmiştir.

---

## 🚀 Kurulum

1. Sanal ortam oluştur:

python -m venv .venv
Ortamı aktif et:

Windows

.venv\Scripts\activate

Mac / Linux

source .venv/bin/activate

Gereksinimleri yükle:

pip install -r requirements.txt

▶️ Çalıştırma

RFM Segmentasyonu:

python src/refm_segmentation.py
#Çıktılar proje kökünde oluşur:

loyal_champ_woman_customers.csv

discount_male_kids.csv

CLTV Prediction

python src/cltv_prediction.py

Çıktı:
    cltv_output_6m.csv

🛡️ Veri Gizliliği
Bu proje gerçek veri içerdiğinden:

Veri seti repo dışında tutulur.


📎 Kullanılan Teknolojiler
Python

Pandas

Lifetimes (BG-NBD & Gamma-Gamma)

Regex tabanlı RFM segmentasyonu

✨ Özellikler
Modüler fonksiyon yapısı (her görev fonksiyonlaştırıldı)

Plug & Play kullanım — veri setini koy, script’i çalıştır, çıktı hazır

Çıktılar otomatik CSV olarak kaydedilir


💬 İletişim

Proje sahibi: Dilek Miraç Çolak

LinkedIn: www.linkedin.com/in/dilek-mirac-colak