# RikaOCR 

> **Osmanlı Arşiv Belgeleri (BOA) İçin Bağımsız, Deterministik ve Bilimsel HTR Araştırma Altyapısı**

![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)
![Tests](https://img.shields.io/badge/tests-194%20passed-brightgreen.svg)
![Architecture](https://img.shields.io/badge/architecture-engine--agnostic-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Durum:** v0.9 — M8 (Veri Hazırlığı ve Ground Truth Aşaması). Çekirdek mimari, otomatik testler ve PAGE-XML köprüleri tamamlandı.

RikaOCR, yalnızca "Osmanlıca okuyan sıradan bir yapay zeka modeli" değildir. Literatürdeki veri sızıntısı (data leakage), tek modele bağımlılık ve bilimsel ispat eksikliği gibi kronik sorunları çözmek amacıyla sıfırdan inşa edilmiş **matematiksel olarak kanıtlanabilir bir Tarihi Metin Tanıma (HTR) altyapısıdır.**

---

##  Geliştirme Motivasyonu: Neden Rik'a ve Neden Yeni Bir Altyapı?

Standart OCR (Optik Karakter Tanıma) sistemleri, Latin alfabesiyle yazılmış düz matbu metinler için tasarlanmıştır. Ancak Başbakanlık Osmanlı Arşivi'ndeki (BOA) el yazması Rik'a belgeleri, standart yapay zeka mimarilerini çökerten şu kronik zorluklara sahiptir:

1. **Karmaşık Belge Geometrisi:** Düz satırlar yoktur. Derkenarlar (kenar notları), çapraz yazılar, mühürler, iç içe geçmiş nizamlar ve kavisli (eğimli) satırlar (baseline) standart "dikdörtgen kutu" (bounding box) mantığını işlevsiz kılar.
2. **Ligatürler ve Bitişiklik:** Rik'a hattında harfler sadece yan yana gelmez, dikeyde de istiflenir ve karmaşık ligatürler oluşturur.
3. **Harekesizlik ve Bağlam:** Arap alfabesi tabanlı Osmanlıca, ünlü harflerin eksikliği nedeniyle yoğun bağlamsal analiz gerektirir.

RikaOCR, yapay zekayı bu kaotik yapıya uydurmak için **"Geometri-Farkındalıklı" (Geometry-Aware)** bir veri hazırlama ve eğitim köprüsü olarak doğmuştur.

---

##  Çekirdek Mühendislik Farkları ve Vizyon

Piyasadaki kapalı kutu (black-box) çeviri araçlarının aksine RikaOCR, %100 şeffaf, kanıtlanabilir ve metodolojik olarak kusursuz bir mimari sunar:

###  1. Motor Bağımsızlık (Engine-Agnostic / Adapter Pattern)
Sistem herhangi bir yapay zeka motoruna (Kraken, Calamari, TrOCR, Tesseract vb.) göbekten bağlı değildir. Yazılım dünyasındaki *Dependency Inversion* (Bağımlılığı Tersine Çevirme) prensibi kullanılarak, motorlar sisteme sadece birer "Adaptör" olarak takılır. 
* **Avantajı:** Yarın daha üstün bir yapay zeka teknolojisi çıksa bile RikaOCR altyapısı çöpe gitmez; sadece yeni bir adaptör yazılır ve sistem çalışmaya devam eder.

###  2. Sıfır Veri Sızıntısı ve Deterministik Bölme (Zero Data Leakage)
Literatürdeki birçok HTR projesinin en büyük hatası, eğitim ve test verilerini "satır bazında" rastgele bölmektir. Bu, yapay zekanın "kopya çekmesine" (overfitting) yol açar.
* RikaOCR, belgeleri bölmek için **SHA-256 kriptografik şifreleme** algoritmasını kullanır.
* Bölme işlemi katı bir şekilde **"Belge Bazında"** yapılır. Eğitim setindeki bir sayfanın kağıt dokusunu, mürekkebini veya kâtibinin el yazısını, yapay zeka test setinde asla göremez. Sonuçlar %100 dürüsttür.

###  3. Poligonal Maskeleme ve Yön-Farkındalığı
Standart (x, y, w, h) formatındaki dikdörtgen kutular yerine, sistem her bir kelime ve satır için çok noktalı poligonlar (polygon masks) ve okuma yönü (Right-to-Left) hizalamaları kullanır.

###  4. Standart Kütüphanelerle PAGE-XML Entegrasyonu (ADR-017)
eScriptorium, Transkribus ve benzeri uluslararası etiketleme platformlarının ürettiği PAGE-XML formatı ile kusursuz konuşur. Herhangi bir dış bağımlılığa (lxml vb.) ihtiyaç duymadan, sistem `Document → PAGE-XML → Document` döngüsünde sıfır veri kaybı garantisi verir.

---

##  Kanıtlanabilirlik Laboratuvarı: 194 Otomatik Test

RikaOCR, "çalıştığını varsaydığımız" scriptlerden oluşmaz. Sistem her çalıştığında veya kod güncellendiğinde, tüm altyapı matematiksel testlerden geçirilir. **194 adet otomatik Pytest** şunları doğrular:

* **Çekirdek (Core):** Belge alan modelinin (Document Hierarchy) bütünlüğü.
* **Geometri (Geometry):** Koordinatların eksi (-) değer almadığı ve çokgenlerin matematiksel geçerliliği.
* **Bölme (Splitting):** SHA-256 algoritmasının hiçbir koşulda veri sızdırmadığı.
* **Uyarlanabilirlik (Dummy Engine):** Kraken gibi motorlar sistemde kurulu olmasa bile boru hattının (pipeline) çökmediği ve zarifçe atlandığı (Lazy Loading).

```bash
# Tüm test laboratuvarını milisaniyeler içinde çalıştırmak için:
pytest
