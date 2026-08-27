# RikaOCR 

> **Osmanlı Arşiv Belgeleri (BOA) İçin Bağımsız, Deterministik ve Motor-Nötr HTR Araştırma Altyapısı**

![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)
![Tests](https://img.shields.io/badge/tests-203%20passed%20%7C%204%20skipped-brightgreen.svg)
![Architecture](https://img.shields.io/badge/architecture-engine--agnostic-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Mevcut Durum:** Çekirdek mimari, PAGE-XML desteği, belge-bazlı deterministik veri bölme, Kraken tabanlı Rik’a OCR ve ByT5 transliterasyon entegrasyonu tamamlanmıştır. Son test durumu: **203 passed, 4 skipped**.

RikaOCR, kapalı kutu (black-box) olarak çalışan ticari OCR araçlarına veya spesifik bir yapay zeka modeline bağımlı sistemlere karşı geliştirilmiş, **tamamen bağımsız ve şahsi bir açık kaynak araştırma inisiyatifidir.** Literatürdeki "veri sızıntısı" (data leakage), "tek modele bağımlılık" ve "karmaşık Osmanlı geometrisi" problemlerini kökünden çözmek için katı yazılım mühendisliği prensipleriyle (TDD, Dependency Inversion) inşa edilmiştir.

Bu depo, sadece bir kod yığını değil; tüm bu altyapı geliştirme sürecinin, mimari kararların ve 203 adet geçen doğrulama testinin detaylıca raporlandığı **58 sayfalık akademik bir makale taslağının (Q1 seviyesi hedefli) yaşayan, çalışan ve ispatlanmış halidir.**

---

##  Geliştirme Motivasyonu: Neden "Sıradan" Bir OCR İşe Yaramaz?

Tesseract veya standart PyTorch/HuggingFace HTR modelleri, Latin alfabesiyle ve düz satırlarla yazılmış modern matbu metinler için tasarlanmıştır. Ancak Başbakanlık Osmanlı Arşivi'ndeki (BOA) karmaşık Rik'a belgeleri bu sistemleri şu sebeplerle çökertir:

1. **Topolojik Kaos (Derkenarlar ve Kavisler):** Osmanlı evrakında okuma sırası yukarıdan aşağıya standart bir akış izlemez. Çapraz yazılan derkenarlar, mühürler etrafında dolanan metinler ve kavisli (eğimli) satırlar (baseline) standart "dikdörtgen kutu (x, y, w, h)" mantığını işlevsiz kılar.
2. **Dikey Ligatürler ve İstifleme:** Rik'a hattında kelimeler sadece yatay eksende birleşmez. Harfler dikeyde birbirinin üzerine biner (istif).
3. **Bağlam Zorunluluğu:** Ünlü harflerin (harekelerin) olmaması, sistemi sadece karakter tanımaya (OCR) değil, dilsel bir tahmin yürütmeye (HTR + NLP) zorlar.

RikaOCR, yapay zekayı bu kaotik belge yapısına uydurmak için **Geometri-Farkındalıklı (Geometry-Aware)** devasa bir köprü işlevi görür.

---

##  Çekirdek Mühendislik Kararları ve Mimari (ADR)

### 1. Motor Bağımsızlığı ve Adaptör Deseni (Engine-Agnosticism)
RikaOCR çekirdeği **hiçbir** yapay zeka motoruna bağımlı değildir. Kraken, Calamari, TrOCR veya Tesseract; bu sistemlerin hepsi RikaOCR için sadece birer "Adaptör"dür (Dependency Inversion / Port-Adapter Pattern). 
* **Pratik Sonuç:** Kraken projesi yarın güncellenmeyi bıraksa veya tamamen çökse bile, RikaOCR altyapısı bir satır bile hasar almaz. Yeni bir model için sadece `Segmenter` ve `Recognizer` arayüzlerine yeni bir sınıf yazılması yeterlidir.

###  2. SHA-256 ile Deterministik Bölme (Zero Data Leakage)
HTR literatüründeki en büyük metodolojik hata, eğitim (train) ve test verilerinin satır bazında rastgele bölünmesidir. Bu durum "Veri Sızıntısına" yol açar; yapay zeka, eğitimde gördüğü bir belgenin kağıt dokusunu, gürültüsünü veya kâtibinin el yazısını test setinde de görür ve yüksek başarı göstererek bizi kandırır.
* **Çözümümüz:** RikaOCR, belgelerin kimliğini (ID) **SHA-256** ile şifreler ve veri setini katı bir şekilde **"Belge Bazında"** (Document-Level) böler. Eğitimdeki bir görselin tek bir pikseli bile test setine sızamaz (`test_splitting.py` ile matematiksel olarak ispatlanmıştır).

###  3. Poligonal Geometri ve Yönlendirme (RTL)
Sistemdeki `Region`, `Line` ve `Word` sınıflarının her biri kendi poligonal maskelerini (Polygon) barındırır. Okuma sırası algoritmaları Arap/Osmanlı alfabesinin doğasına uygun olarak Sağdan-Sola (RTL) ve çokgen tabanlı çalışacak şekilde özelleştirilmiştir.

###  4. PAGE-XML "Round-Trip" Garantisi (ADR-017)
Uluslararası platformlarla (eScriptorium, Transkribus) iletişim kuran `PageXmlCodec` modülü, kayıpsız bir gidiş-dönüş garantisi sunar. Sisteme giren bir belge, PAGE-XML'e dönüştürülüp tekrar projeye alındığında; okuma sırasından poligon noktalarına kadar hiçbir veri bozulmaz.
---

##  Kilometre Taşları ve Geliştirme Günlükleri (M1 - M8)

RikaOCR, rastgele yazılmış scriptlerin bir araya gelmesiyle değil, katı bir Milestones (M) planlaması ve Test-Güdümlü Geliştirme (TDD) metodolojisiyle adım adım inşa edilmiştir. Her bir aşama, 58 sayfalık akademik makale taslağında teorik olarak ispatlanmış ve kod düzeyinde doğrulanmıştır.

###  M1: Belge Alan Modelinin (Domain Model) İnşası
Sistemin veriyi hafızada nasıl tutacağını belirleyen temel ontoloji oluşturuldu. Osmanlı arşiv belgelerinin hiyerarşik yapısını temsil eden nesne yönelimli model sıfırdan yazıldı.
* **Hiyerarşik Yapı:** `Document` ➔ `Page` ➔ `Region` ➔ `Line` ➔ `Word` ➔ `Token` zinciri kuruldu.
* **Doğrulama:** Satırların üst bölgelere, kelimelerin satırlara olan geometrik bağımlılıkları `test_alignment.py` altındaki testlerle koruma altına alındı. Bir satırın, ait olduğu sayfa sınırlarının dışına çıkması yazılımsal olarak engellendi.

###  M2: PAGE-XML Codec Modülü (`PageXmlCodec`)
Uluslararası standart etiketleme formatı olan PAGE-XML verilerini okuma ve yazma yeteneği projeye kazandırıldı.
* **Mühendislik Kararı:** Dış kütüphanelerin (lxml vb.) getireceği bağımlılık ve versiyon karmaşasını önlemek adına, Python'un yerleşik standart kütüphaneleriyle sıfırdan bir XML parser/encoder yazıldı (ADR-017).
* **Kayıpsız Gidiş-Dönüş (Canonical Round-Trip):** Bir belgenin RikaOCR modelinden PAGE-XML'e dönüştürülüp, ardından tekrar RikaOCR modeline geri yüklenmesi durumunda koordinatların, okuma sırasının ve metinlerin tek bir bit bile kayba uğramadığı matematiksel olarak ispatlandı (`test_page_xml.py`).

###  M3: Veri Girişi ve Üstveri (Ingest & Metadata) Yönetimi
Arşivden gelen ham görüntülerin ve bunlara ait meta verilerin (kâtip bilgisi, fon kodu, belge tarihi vb.) sisteme güvenli bir şekilde alınması sağlandı. Veri manipülasyonunu engellemek amacıyla tüm girdiler izole bir dosya sistemine bağlandı.

###  M4: Dataset Modülü ve Deterministik Bölme (SHA-256)
Yapay zekanın eğitim sürecindeki en büyük bilimsel açmaz olan "veri sızıntısı" (data leakage) problemi bu aşamada çözüldü.
* **Algoritma:** Her belge içeriği ve görseli, **SHA-256** algoritmasıyla benzersiz bir karma (hash) değerine dönüştürüldü.
* **Katı Bölme Politikası:** Veri kümesi %80 Eğitim, %10 Doğrulama (Validation) ve %10 Test olarak ayrılırken, satır bazlı değil tamamen **Belge Bazlı** bölme yapıldı. Yapay zekanın test setinde karşılaşacağı bir kâtibin el yazısını veya sayfa gürültüsünü eğitim setinde görerek "kopya çekmesi" imkansız hale getirildi (`test_splitting.py`).

###  M5: Model ve Motor Bağımsızlığı (Abstraction Layer)
Yapay zeka motorlarının (Kraken vb.) projeye göbekten bağlanmasını önlemek amacıyla soyutlama katmanları (Protocols) yazıldı.
* **Tasarım Kalıbı (Design Pattern):** *Adapter Pattern* kullanılarak `Recognizer` ve `Segmenter` sınıfları protokollere bağlandı.
* **Tembel Yükleme (Lazy Loading):** PyTorch veya Kraken gibi devasa kütüphanelerin, projenin çekirdek modülleri çalışırken RAM'i şişirmemesi sağlandı. Bu kütüphaneler sadece yapay zeka tahmini (inference) istendiği milisaniyede hafızaya çağrılır (`test_kraken_adapter.py`).

###  M6: Uçtan Uca (End-to-End) Boru Hattı ve CLI Entegrasyonu
Yazılan tüm bağımsız modüller (Ingest, Codec, Dataset, Abstraction) merkezi bir boru hattında (`pipeline.py`) birleştirildi ve kullanıcı dostu bir Komut Satırı Arayüzü (CLI) geliştirildi.

###  M7: Değerlendirme Motoru (Evaluation Engine)
Eğitilen modellerin başarısını ölçmek için endüstri standardı olan CER (Karakter Hata Oranı) ve WER (Kelime Hata Oranı) hesaplama algoritmaları entegre edildi.
* **Algoritmik Detay:** Karakter karşılaştırmaları için *Levenshtein Distance* (Düzenleme Mesafesi) algoritması Osmanlıca/Arap alfabesinin doğasına uygun olarak Sağdan-Sola (RTL) okuma sırasını gözetecek şekilde optimize edildi.

###  M8: Veri Hazırlığı ve Yerel eScriptorium Laboratuvarı (Aktif Aşama)
Yazılım altyapısının doğrulanmasının ardından, yapay zekaya Rik'a hattını öğreteceğimiz "Öğretmenlik" safhasına geçildi.
* **Laboratuvar Kurulumu:** Windows ortamında WSL2 (Linux için Windows Alt Sistemi) ve Docker konteyner mimarisi kullanılarak yerel bir **eScriptorium** sunucusu ayağa kaldırıldı.
* **Veri Köprüleri:** eScriptorium'dan çıkacak verileri anında işlemek üzere `prepare_boa.py` ve `export_gt.py` scriptleri tamamlandı. Şu an aktif olarak pilot belgelerin tam manuel segmentasyonu ve transkripsiyonu (Ground Truth üretimi) bu laboratuvar üzerinden yürütülmektedir.

---

##  Doğrulama Laboratuvarı: 194 Onaylanmış Matematiksel İspat

RikaOCR, "çalıştığı iddia edilen" değil, **"çalıştığı 194 testle matematiksel olarak ispatlanmış"** bir altyapıdır. Geliştirilen test süiti (`pytest`), her kod satırını ve geometrik hesabı anlık olarak denetler:

* **Geometri Doğrulamaları (`geometry`):** Poligon noktalarının eksi değer alamayacağını, çizgilerin çakışma matrislerini ve alan hesaplamalarını doğrular.
* **Güvenlik ve Dayanıklılık:** Bozuk, eksik veya manipüle edilmiş PAGE-XML dosyaları sisteme yüklendiğinde, altyapının çökmeden bu dosyaları zarifçe reddettiğini (`validation`) kanıtlar.
* **Donanım Bağımsızlığı:** Bilgisayarda GPU veya ağır yapay zeka kütüphaneleri kurulu olmasa bile, 194 testin 190'ı standart Python kütüphaneleriyle milisaniyeler içinde çalışır; yapay zeka motoruna bağlı kalan 4 test ise sistem tarafından çökme yaşanmadan güvenle atlanır (Skipped).
---

##  Kurulum Mimarisi: Modüler Katmanlar

RikaOCR, gereksiz kaynak tüketimini ve versiyon çakışmalarını önlemek amacıyla "Katmanlı Kurulum" (Layered Installation) mimarisine sahiptir. Sistemin hangi özelliğine ihtiyaç duyuluyorsa, sadece o katmanın bağımlılıkları yüklenir:

**1. Çekirdek Kurulum (Hafif İşlemler Katmanı)**
Yalnızca belge hiyerarşisi, PAGE-XML dönüştürme, dizin yönetimi ve 194 testin çalıştırılması içindir. Ağır kütüphaneler içermez, sıradan bir işlemcide (CPU) saniyeler içinde kurulur.
```bash
pip install -e .

## Doğrulanmış Deney Sonuçları

### Rik'a OCR — Kraken

Nihai OCR modeli, deterministik belge-bazlı bölme ile eğitim sırasında hiç görülmeyen 9 belge / 132 satırlık held-out test kümesinde değerlendirilmiştir.

- Character Accuracy: **77.23%**
- CER: **22.77%**
- WER: **72.47%**
- Model: `data/kraken_models/riqa/rika_docsplit_best_0.7502_seed42.safetensors`

Bu sonuçlar satır tanıma performansını ölçer. Özellikle WER değerinin yüksek olması, sistemin henüz kusursuz belge transkripsiyonu sağlamadığını gösterir.

### Osmanlıca → Latin Harfli Transliterasyon — ByT5

ByT5 transliterasyon modeli, sabit ve bağımsız held-out yer-adı test kümesinde değerlendirilmiştir.

- CER: **17.05%**
- Exact Match: **39.96%**
- Model: `data/transliteration/models/byt5_small_seed42_bf16/best_model`

Bu deney bir **yer-adı gazetteer'i** üzerinde yapılmıştır. Sonuçlar genel Osmanlı Türkçesi cümle transliterasyonu veya modern Türkçeye çeviri başarısı olarak yorumlanmamalıdır.

### Uçtan Uca Mimari

RikaOCR işlem hattında katmanlar ayrı tutulur:

`Rik'a görüntüsü → Kraken OCR → Osmanlıca Arap harfli metin → ByT5 transliterasyon → Latin harfli çıktı`

Ham OCR metni değiştirilmez; transliterasyon ayrı bir çıktı katmanı olarak saklanır. `--line-image` seçeneği, önceden satır olarak kırpılmış görüntülerde sayfa segmentasyonunu atlayarak doğrudan tanıma yapılmasını sağlar.



## CLI Kullanımı

Önceden satır olarak kırpılmış bir Rik'a görüntüsünü Kraken ile okuyup sonucu ByT5 ile Latin harflerine aktarmak için:

```bash
python -m rikaocr.cli INPUT.png \
  -o ocr.txt \
  --format text \
  --engine kraken \
  --line-image \
  --rec-model PATH/TO/rika_docsplit_best_0.7502_seed42.safetensors \
  --transliterate \
  --translit-engine byt5 \
  --translit-model PATH/TO/byt5_small_seed42_bf16/best_model \
  --translit-output transliteration.json \
  --translit-format json \
  --translit-mode word
```

`--line-image`, görüntünün zaten tek satır olduğunu belirtir ve sayfa segmentasyonunu atlar.

`--translit-mode whole`, kontrollü ByT5 yer-adı deneyinde kullanılan tam-sekans çıkarım davranışını korur. `--translit-mode word` ise daha uzun OCR satırlarında tekrarlayan üretimi azaltmak için sunulan operasyonel bir seçenektir; genel Osmanlıca cümle transliterasyonu için doğrulanmış bir doğruluk iddiası taşımaz.
