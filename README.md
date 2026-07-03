# RikaOCR 📜🤖

> **Osmanlı Arşiv Belgeleri (BOA) İçin Bağımsız, Deterministik ve Bilimsel HTR Araştırma Altyapısı**

![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)
![Tests](https://img.shields.io/badge/tests-194%20passed-brightgreen.svg)
![Architecture](https://img.shields.io/badge/architecture-engine--agnostic-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Durum:** v0.9 — M8 (Veri Hazırlığı ve Ground Truth Aşaması). Mimari, testler ve köprüler (PAGE-XML) tamamlandı.

RikaOCR, yalnızca "Osmanlıca okuyan bir yapay zeka modeli" değildir. Bilecik Şeyh Edebali Üniversitesi Tarih Bölümü yüksek lisans tez projesi kapsamında, literatürdeki veri sızıntısı (data leakage), tek modele bağımlılık ve bilimsel ispat eksikliği gibi kronik sorunları çözmek amacıyla sıfırdan inşa edilmiş **matematiksel olarak kanıtlanabilir bir Tarihi Metin Tanıma (HTR) altyapısıdır.**

---

## 🌟 Projenin Vizyonu ve Temel Farkları

Piyasadaki kapalı kutu (black-box) çeviri araçlarının aksine RikaOCR, %100 şeffaf ve metodolojik olarak kusursuz bir mimari sunar:

* 🔌 **Motor Bağımsızlık (Engine-Agnostic):** Sistem herhangi bir yapay zeka motoruna (Kraken, Calamari, TrOCR vb.) göbekten bağlı değildir. Motorlar sisteme "Adaptör" mantığıyla (Dependency Inversion) takılır. Yarın daha iyi bir teknoloji çıkarsa, çekirdek kod değişmeden sisteme entegre edilebilir.
* 🛡️ **Sıfır Veri Sızıntısı (Deterministik Bölme):** RikaOCR, yapay zekanın kopya çekmesini engellemek için satır bazlı rastgele bölme yapmaz. SHA-256 kriptografik şifrelemesi kullanarak verileri "Belge Bazında" böler. Yapay zeka, testte göreceği sayfanın mürekkebini eğitimde asla göremez.
* 📐 **Karmaşık Osmanlı Geometrisi:** Matbu eserlerin basit dikdörtgen kutuları yerine; Başbakanlık Osmanlı Arşivi (BOA) belgelerindeki derkenarlar, mühürler, kavisli Rik'a satırları ve iç içe geçen nizamlar için **poligonal maskeler (çokgenler) ve alt çizgiler (baseline)** kullanır.
* 🔄 **Kusursuz Dışa Aktarım (PAGE-XML):** eScriptorium ve Transkribus gibi uluslararası platformlarla kayıpsız iletişim kuran `PageXmlCodec` altyapısına sahiptir.

---

## 🧪 Kanıtlanabilirlik (194 Otomatik Test)

Bu proje "çalıştığı varsayılan" kodlarla değil, ispatlanmış matematiksel testlerle çalışır. 

Çekirdek altyapı, PAGE-XML okuyucusu, veri sızıntısı kontrolleri ve geometri hesaplamaları, her kod değişikliğinde mili-saniyeler içinde koşan tam **194 adet otomatik test (Pytest)** ile güvence altına alınmıştır. Ağır yapay zeka kütüphaneleri "tembel yükleme" (lazy loading) ile sadece ihtiyaç anında çağrılır, böylece sistem CPU üzerinde hafifçe çalışabilir.

---

## 🛠️ Kurulum ve Kullanım

Sistem, profesyonel Python paketleme standartlarına uygun olarak modüler tasarlanmıştır.

**1. Çekirdek Kurulum (Veri hazırlığı ve testler için - GPU gerektirmez)**
```bash
pip install -e .
