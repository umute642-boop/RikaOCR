> **Repo notu:** Bu dosya, RikaOCR Teknik Tasarım Dokümanı v0.2nin depo içindeki dondurulmuş kopyasıdır. Mimari yalnızca yeni bir ADR ile değişir (bkz. `docs/adr/`).

# RikaOCR — Teknik Tasarım Dokümanı (TDD)

**Sürüm:** 0.2 (taslak) · **Tarih:** 2026-06-29 · **Statü:** Mimari inceleme sonrası güncellendi; dondurmaya aday
**Önceki sürüm:** v0.1 (2026-06-29) · **Bu sürümdeki değişiklikler:** bkz. Bölüm 21 (Değişiklik Günlüğü)
**Kapsam:** Rik'a hattıyla yazılmış Osmanlı arşiv (BOA) belgeleri için uzun vadeli, açık kaynaklı bir HTR (Handwritten Text Recognition) / belge anlama platformunun mimari tasarımı. Mimari, çok-yazılı (Rik'a, Divani, Siyakat, Talik) bir geleceği destekleyecek biçimde yazı-nötr çekirdek üzerine kurulmuştur.

> Bu doküman, kod yazımından önce hazırlanan bağlayıcı mimari referanstır. Tüm geliştirme bu belgeye atıfla yürütülecek; mimari değişiklikler ADR (Architecture Decision Record) olarak kayıt altına alınacaktır.

---

## 0. Bu dokümanı nasıl okumalı

Belge üç katmanda ilerler: (1) **temel ilkeler ve kritik kararlar** (ADR'ler), (2) **alan modeli, sistem ve modül mimarisi**, (3) **veri, model, test ve operasyon stratejileri**. v0.2'de eklenen yeni kavramsal omurga **Document alan modeli** (Bölüm 3) ve **koordinat↔metin hizalaması** (Bölüm 6.1) bölümleridir; mimarinin geri kalanı bu ikisine asılır. Sonda (Bölüm 20) senin vermen gereken açık kararlar listelenmiştir.

Belgedeki kesin olmayan/literatüre dayalı iddialar "öneri" veya "değerlendirme" olarak işaretlenmiştir; bunlar tartışmaya açıktır.

---

## 1. Yönetici özeti ve temel tasarım ilkeleri

RikaOCR'ı 6 aylık bir OCR denemesi değil, **5+ yıllık veri-merkezli bir araştırma altyapısı** olarak tasarlıyoruz. Bu ölçekte başarıyı belirleyen şey model mimarisi değil, **verinin kalitesi, etiketleme disiplini, belgenin doğru modellenmesi ve sistemin yeniden üretilebilirliğidir.**

Altı temel ilke:

1. **Veri-merkezlilik (data-centric).** Model kodu değiştirilebilir; etiketli veri projenin asıl sermayesidir. Veri birinci sınıf vatandaştır (ayrı versiyonlama, ayrı dokümantasyon, ayrı kalite kapıları).
2. **Belge-merkezlilik (document-centric).** Sistemin merkezinde geçici bir "metin dizisi" değil, kalıcı bir **Document alan nesnesi** (`Document → Page → Region → Line → Word → Token`) vardır. Metadata, dilbilim, arama ve transliterasyon hep bu nesneye asılır.
3. **Koordinat↔metin ayrılmazlığı.** Tanınan metin her zaman görüntüdeki konumuyla bağlı kalır. "Belgede kelimeyi bul ve işaretle" hedefi ancak bu hizalama mimarinin temeli olursa mümkündür.
4. **Katmanlı ayrışma (ports & adapters / hexagonal).** Tanıma çekirdeği; dosya biçimleri, GUI, web servisi, arama motoru gibi dış dünyadan bağımsızdır.
5. **Yapılandırma ile sürülen, yeniden üretilebilir deneyler.** Her sonuç, `(kod commit + veri sürümü + config)` üçlüsüyle birebir tekrar edilebilir olmalıdır.
6. **Yazı-nötr çekirdek + script profile.** Çekirdek tek bir yazı türüne bağlı değildir; Rik'a, Divani, Siyakat, Talik birer "script profile" (veri/yapılandırma) olarak eklenir.

Ayrıca akademik izlenebilirlik (datasheet, model card, ADR) ve açık kaynak yönetişimi (lisans, katkı süreci) tasarımın ayrılmaz parçalarıdır.

---

## 2. Kritik mimari kararlar (ADR özetleri)

| ADR | Karar | Gerekçe (özet) | Statü |
|-----|-------|----------------|-------|
| 001 | **Ana eksen: satır düzeyi HTR** (segmentasyonsuz). İzole harf yalnızca yardımcı veri. | Rik'a kürsivdir; güvenilir harf segmentasyonu çözülmemiş problemdir. SOTA satır düzeyinde çalışır. | Kabul |
| 002 | **Çatı: PyTorch + HuggingFace.** | Hedef modellerin tamamı (TrOCR, Donut, ViT, Kraken, Calamari) bu ekosistemde. | Kabul |
| 003 | **Ground-truth kodlaması: Arap harfli Unicode (birincil).** Latin transliterasyon ayrı modüldür. | Modelin öğreneceği şey yazının kendisidir; transliterasyon ayrı bir dönüşümdür. | Karar bekliyor → Bölüm 20 |
| 004 | **Annotation biçimi: PAGE-XML (kaynak/source of truth), ALTO (dışa aktarım), JSONL (yalnızca türetilmiş eğitim temsili).** | PAGE-XML koordinat+metin hiyerarşisini taşır; JSONL ondan üretilir, elle düzenlenmez. | Kabul |
| 005 | **Etiketleme aracı: eScriptorium** (kendi aracımızı yazmayız). | Açık kaynak, PAGE/ALTO destekli, insan-döngüde düzeltmeyi destekler. | Kabul |
| 006 | **Versiyonlama: Git (kod) + hash'li manifest → ileride DVC (veri/model).** | Boş repoda ağır DVC kurulmaz; gerçek veri gelince (v0.2 veri fazı) tam DVC'ye geçilir. | Kabul |
| 007 | **Sıfırdan eğitim yerine transfer öğrenme** (Arapça/Farsça HTR'den). | Az Rik'a verisiyle çok daha verimli. | Kabul |
| 008 | **(YENİ) Belge-merkezli mimari: Document alan modeli çekirdektir.** | Tüm modüller ortak, kalıcı bir belge temsili üzerinden konuşur; ad-hoc temsiller yasak. | Kabul |
| 009 | **(YENİ) Koordinat↔metin hizalaması birinci sınıf çıktıdır.** | Arama+işaretleme hedefi ancak hizalama korunursa mümkündür; düz metin tek temsil olamaz. | Kabul |
| 010 | **(YENİ) Yazı-nötr çekirdek + script profile soyutlaması.** | Divani/Siyakat/Talik çekirdeği yeniden yazmadan eklenebilsin. | Kabul |
| 011 | **(YENİ) Arama bir port'tur; motor yazılmaz, adaptörle sarılır** (SQLite FTS5 / Tantivy / OpenSearch). | Bulanık/öbek araması çözülmüş bir iştir; yeniden icat edilmez. | Kabul |
| 012 | **(YENİ) Açık kaynak yönetişimi tasarımın parçasıdır** (kod ve veri için ayrı lisans, katkı süreci, donmuş benchmark, reprodüksiyon sabitleme). | OSS'in 5 yıllık ömrünü bu belirler. | Kabul |

> **Eleştirel not:** ADR-003 (kodlama politikası) hâlâ en kritik açık karardır; etiketleme başlamadan kilitlenmelidir (Bölüm 20).

---

## 3. Document alan modeli (çekirdek)

Sistemin merkezinde, tüm modüllerin paylaştığı kalıcı bir **alan nesnesi (domain aggregate)** vardır. Bu, geçici bir pipeline durumu değil; PAGE-XML kaynağından üretilen, belleğe ve diske serileştirilebilen birinci sınıf bir temsildir.

Hiyerarşi:

```
Document
 ├── (metadata: provenance, catalog, archive, document_info)
 └── Page[]
      ├── (image_ref, boyut, çözünürlük)
      └── Region[]            # bölge (metin bloğu, derkenar, mühür vb.)
           └── Line[]          # satır + baseline + poligon
                ├── text       # tanınan/etiketli metin (Arap harfli Unicode)
                ├── alignment   # metin ↔ koordinat hizası (aşağıda)
                └── Word[]      # kelime + kutu (varsa)
                     └── Token[] # alt-kelime/karakter düzeyi birim (opsiyonel)
```

Tasarım kuralları:

- **Her düğüm geometriye sahiptir:** Region poligonu, Line baseline+poligonu, Word/Token kutusu. Metin daima bir geometriyle ilişkilidir.
- **Document, kaynak (PAGE-XML) ile birebir eşlenebilir** ve ona geri yazılabilir (round-trip). Bilgi kaybı olmamalıdır.
- **Modüller bu nesneyi tüketir/zenginleştirir:** layout `Region/Line` üretir, recognition `Line.text` doldurur, linguistics `Token`/normalize/etiket ekler, metadata belge başlığına yazar, search bu nesneden indeks üretir.
- **Sürümlenebilir:** Document temsilinin şema sürümü (`schema_version`) tutulur; gelecekte alan eklemek geriye dönük göçü (migration) mümkün kılar.

> Bu nesne, v0.1'de eksik olan merkezi soyutlamadır. Metadata, arama, NLP ve transliterasyonun tümü artık ortak bir dile (Document) konuşur.

---

## 4. Genel sistem mimarisi

Üç halkalı (hexagonal) yapı; merkezde Document alan modeli:

```
                ┌────────────────────────────────────────────────┐
                │              UYGULAMA KATMANI (apps)             │
                │   CLI · (ertelendi) FastAPI · (ertelendi) GUI    │
                └───────────────▲────────────────────────────────┘
                                │ (yalnızca arayüzler üzerinden)
                ┌───────────────┴────────────────────────────────┐
                │                ÇEKİRDEK (core)                   │
                │  Document alan modeli  +                         │
                │  Preprocessor · LayoutAnalyzer · Recognizer ·    │
                │  Linguistics(NLP) · Search(port) · Evaluator     │
                └───────────────▲────────────────────────────────┘
                                │
                ┌───────────────┴────────────────────────────────┐
                │              ADAPTÖRLER (adapters/io)            │
                │  PAGE/ALTO codec · görüntü I/O · dataset yük. ·  │
                │  metadata kaynakları · arama motoru adaptörleri  │
                └──────────────────────────────────────────────────┘
```

İşlem hattı (inference yönü) — artık Document'i zenginleştirir:

```
Belge görüntüsü + arşiv metadata'sı
   → Önişleme (deskew, normalize)
   → Layout (Region/Line/baseline) ............ Document doldurulur
   → Satır görüntüleri çıkarımı
   → Tanıma (satır → Arap-harfli metin) ........ Line.text + hizalama
   → Okuma sırası / bidi çözümü ................ mantıksal metin akışı
   → Linguistics (normalizasyon, ↦ token, ner...) Document zenginleşir
   → (opsiyonel) Transliterasyon (Arap → Latin)
   → Dışa aktarım: PAGE/ALTO (kaynak) · JSONL (eğitim) · arama indeksi
```

---

## 5. Modül yapısı ve sorumlulukları

| Modül (paket) | Sorumluluk | Arayüz / Durum |
|---------------|-----------|-----------------|
| `core.document` | **(YENİ)** Document alan modeli, serileştirme, şema sürümü | Çekirdek tip |
| `core.preprocessing` | Deskew, gürültü azaltma, normalizasyon | `Preprocessor` |
| `core.layout` | Bölge/satır/baseline tespiti, satır çıkarımı | `LayoutAnalyzer` |
| `core.reading_order` | **(YENİ)** Okuma sırası ve RTL/bidi çözümü | `ReadingOrderResolver` |
| `core.recognition` | Satır görüntüsü → metin (HTR) | `Recognizer` |
| `core.linguistics` | **(YENİ — Ottoman NLP katmanı)** alt modüller aşağıda | bkz. Bölüm 5.1 |
| `core.search` | **(YENİ)** Arama portu (yalnızca arayüz; motor adaptörle) | `SearchIndex`, `SearchQuery` |
| `core.evaluation` | CER/WER + hata analizi | `Evaluator` |
| `core.script_profile` | **(YENİ)** Yazı türü profili (charset, normalizasyon, okuma kuralları, model referansı) | `ScriptProfile` (veri/yapılandırma) |
| `data.ingest` | Ham belge alımı, doğrulama, tekilleştirme | — |
| `data.annotation` | PAGE/ALTO ↔ Document codec, GT doğrulama | `AnnotationCodec` |
| `data.metadata` | **(YENİ — BOA metadata katmanı)** alt modüller aşağıda | bkz. Bölüm 5.2 |
| `data.dataset` | Eğitim/doğrulama/test kümeleri, bölme, JSONL manifest | `DatasetBuilder` |
| `data.synthesis` | Sentetik satır üretimi (izole harf + Osmanlıca metin) | `SynthGenerator` |
| `data.augmentation` | Görüntü artırma (blur, noise, perspective, ink/paper) | `Augmenter` |
| `training` | Eğitim döngüleri, config çözümleme, checkpoint | — |
| `common` | Logging, config, tipler, hata sınıfları, yardımcılar | — |
| `apps.cli` | Komut satırı arayüzü (`rikaocr train/predict/...`) | — |

**Ertelenen modüller (arayüz veya kavram düzeyinde tanımlı, gerçekleme sonraya):** `serving` (FastAPI), `apps.gui/web`, gelişmiş `linguistics` alt modülleri (morphology/NER/lexicon gerçeklemeleri), dış eklenti keşfi (plugin entry-points), Donut tabanlı belge anlama.

### 5.1. `core.linguistics` — Ottoman NLP katmanı (YENİ)

Tanıma sonrası tüm dilsel işleme tek çatı altında toplanır (v0.1'deki dağınık `language_model` + `transliteration` buraya katlanmıştır):

| Alt modül | Sorumluluk | Faz |
|-----------|-----------|-----|
| `normalization` | **Dilbilimsel** normalizasyon (imla varyantları, birleşik/ayrık biçimler). *Kodlama (Unicode/NFC) normalizasyonundan ayrıdır; o veri hattındadır.* | Erken |
| `transliteration` | Arap harfli metin → Latin (kural + model) | Orta |
| `language_model` | Tanıma çıktısının dilsel düzeltmesi (n-gram → nöral) | Orta |
| `lexicon` | Osmanlıca sözlük/kök listesi; tanıma ve düzeltmeye destek | Ertelenmiş (arayüz şimdi) |
| `morphology` | Biçimbirim analizi | Ertelenmiş (arayüz şimdi) |
| `abbreviations` | Arşiv kısaltmalarının açılımı | Ertelenmiş (arayüz şimdi) |
| `named_entities` | Kişi/yer/kurum adı tanıma (ör. "Laçin", "Dersim") | Ertelenmiş (arayüz şimdi) |

> İlke: morphology, NER, lexicon başlı başına araştırma projeleridir. **Arayüzleri (Protocol) bugün tanımlanır; gerçeklemeleri v1.0 sonrasına bırakılır.** Bu, Siyakat gibi ağır kısaltmalı yazılara geçişte katmanın hazır olmasını sağlar.

### 5.2. `data.metadata` — BOA metadata katmanı (YENİ)

Arşiv gerçekliğini Document modeline bağlayan köprü:

| Alt modül | Sorumluluk |
|-----------|-----------|
| `provenance` | Kaynak, erişim tarihi, haklar durumu, türetme zinciri |
| `catalog` | BOA katalog hiyerarşisi (fon / dosya / gömlek vb.) ile eşleme |
| `archive` | Arşiv-düzeyi bilgi (koleksiyon, tasnif, dönem) |
| `document_info` | Belge-düzeyi alanlar (tür, tarih, dil, kâtip eli — extensible) |

> Uyarı: Gerçek BOA metadata'sını görmeden tam katalog şemasını aşırı tasarlama. **Minimal `provenance` + genişletilebilir `document_info` ile başla;** tam katalog entegrasyonunu gerçek veri gelince yap.

### 5.3. `core.script_profile` — Yazı-nötr çekirdek (YENİ)

Çekirdek tek bir yazı türüne bağlı değildir. Her yazı türü bir **profil** olarak tanımlanır ve bu profil **kod değil, veri/yapılandırmadır**:

```
ScriptProfile:
  name: "rika" | "divani" | "siyakat" | "talik"
  charset: <izinli karakter envanteri>
  normalization_rules: <Unicode + dilbilimsel>
  reading_rules: <RTL, satır/bölge sıralaması özellikleri>
  models: <layout + recognition model referansları>
  guidelines_ref: <annotation kılavuzu>
```

Yeni yazı türü eklemek = yeni bir `ScriptProfile` + ilgili veri/model. Çekirdek hat değişmez. Proje adı şimdilik "RikaOCR" kalır; ancak çekirdek paketler bilinçli olarak yazı-nötr yazılır (ileride "OttomanHTR" çekirdeği + Rik'a ilk profil).

---

## 6. Veri temsili ve hizalama

### 6.1. Koordinat↔metin hizalaması (YENİ, çekirdek ilke — ADR-009)

Tanınan/etiketli metin daima görüntü konumuyla bağlıdır. Hizalama Document modelinde şu düzeylerde tutulur:

- **Satır düzeyi (zorunlu):** her `Line.text` bir baseline/poligon ile ilişkilidir.
- **Kelime düzeyi (hedef):** `Word` kutuları — "belgede kelimeyi işaretle" özelliğinin temeli.
- **Token/karakter düzeyi (opsiyonel):** CTC/attention hizasından türetilebilen ince hiza; mümkün olduğunda saklanır.

Kaynak hiyerarşi: **PAGE-XML = source of truth.** JSONL eğitim manifesti bu kaynaktan **türetilir** ve yalnızca eğitim için kullanılır; elle düzenlenmez. Arama indeksi de Document'ten üretilir, böylece her arama sonucu bir koordinata geri bağlanabilir.

### 6.2. Dosya biçimleri

| Katman | Biçim | Ne için | Notlar |
|--------|-------|---------|--------|
| Görüntü | TIFF/PNG (kayıpsız) | Ham + satır kırpımları | GT için JPEG'den kaçın |
| Layout + GT (**kaynak**) | **PAGE-XML** | Bölge/satır/baseline/metin + koordinat | Source of truth |
| Birlikte çalışabilirlik | ALTO-XML | Kütüphane/METS dünyasına dışa aktarım | İkincil |
| Eğitim (**türetilmiş**) | JSONL | Satır→metin eşlemesi, split, gt_version | PAGE'den üretilir, elle düzenlenmez |
| Konfigürasyon | YAML (Hydra) | Deney/model/veri/script profile | İnsan-okur |
| Model meta | Model Card + JSON | Eğitim koşulları, metrik, sınırlar | İzlenebilirlik |
| Veri meta | Datasheet (MD) | Küme tanımı, yanlılık, haklar | Her sürümde |

---

## 7. Önerilen repo / klasör yapısı

```text
RikaOCR/
├── docs/
│   ├── architecture.md             # bu doküman
│   ├── adr/                         # ADR-001..012 ve sonrası
│   ├── annotation-guidelines.md     # GT kodlama politikası (kilitlenecek)
│   ├── benchmark.md                 # (YENİ) donmuş kamu benchmark tanımı
│   └── datasheets/                  # her veri kümesi için datasheet
├── configs/                         # Hydra/OmegaConf
│   ├── data/  model/  train/  experiment/
│   └── script_profiles/             # (YENİ) rika.yaml, divani.yaml, ...
├── src/
│   └── rikaocr/                     # tek, kurulabilir paket
│       ├── common/                  # config, logging, types, exceptions
│       ├── core/
│       │   ├── interfaces.py        # Protocol/ABC sözleşmeleri
│       │   ├── document/            # (YENİ) Document alan modeli
│       │   ├── preprocessing/
│       │   ├── layout/
│       │   ├── reading_order/       # (YENİ)
│       │   ├── recognition/
│       │   ├── linguistics/         # (YENİ) normalization, transliteration,
│       │   │                        #        language_model, lexicon,
│       │   │                        #        morphology, abbreviations, ner
│       │   ├── search/              # (YENİ) port + sorgu modeli (motor YOK)
│       │   ├── script_profile/      # (YENİ)
│       │   └── evaluation/
│       ├── data/
│       │   ├── ingest/  annotation/  metadata/  dataset/
│       │   ├── synthesis/  augmentation/
│       ├── training/
│       └── apps/
│           └── cli/                 # train/predict ileride buraya taşınır (bkz. not)
├── tests/
│   ├── unit/  integration/  data_contracts/  regression/  fixtures/
├── scripts/
├── notebooks/                       # yalnızca keşif
├── data/                            # hash'li manifest → ileride DVC
│   ├── raw/  interim/  processed/  external/
├── models/                          # ileride DVC + model cards
├── pyproject.toml
├── requirements.lock / poetry.lock  # (YENİ) sürüm kilidi
├── Dockerfile                       # (YENİ) reprodüksiyon ortamı
├── .pre-commit-config.yaml          # black, ruff, mypy, isort
├── .github/workflows/               # CI: lint + test
├── LICENSE                          # (YENİ) kod lisansı
├── LICENSE-DATA                     # (YENİ) veri lisansı (ayrı)
├── CONTRIBUTING.md                  # (YENİ)
├── CODE_OF_CONDUCT.md               # (YENİ)
└── README.md
```

> **Not (train.py / predict.py):** Mevcut repoda kök dizinde duran `train.py` ve `predict.py` **geçicidir**. Uzun vadede bunlar `src/rikaocr/apps/cli/` altındaki CLI komutlarına (`rikaocr train ...`, `rikaocr predict ...`) taşınacaktır. Yeni mantık kök dizinde script olarak yazılmaz; paket içine girer.

---

## 8. Veri hattı (Data Pipeline)

Yeniden çalıştırılabilir aşamalar (önce hash'li manifest, gerçek veri büyüyünce DVC):

```
raw/ (ham belge + arşiv metadata + provenans)
  → 01_ingest      : doğrulama, tekilleştirme, provenans + metadata kaydı
  → 02_layout      : bölge/satır/baseline (otomatik + insan düzeltmesi) → Document
  → 03_lines       : PAGE baseline'larına göre satır kırpımı (hiza korunur)
  → 04_normalize   : GT metnin Unicode normalizasyonu (kodlama politikası)
  → 05_dataset     : belgeye göre train/val/test bölmesi + JSONL manifest
  → 06_synth/aug   : sentetik + artırma (yalnızca eğitim bölmesine)
processed/ (eğitime hazır manifest + satır görüntüleri; PAGE kaynak korunur)
```

Kurallar: **bölme belgeye göre** (satır sızıntısı yasak); **artırma/sentetik yalnızca eğitime**; her aşama **deterministik** (sabit seed); kaynak temsil **PAGE-XML**, JSONL türetilmiş.

---

## 9. Veri etiketleme stratejisi ve annotation süreci

**Araç:** eScriptorium (ADR-005). **Biçim:** PAGE-XML kaynak (ADR-004). **Kural:** etiketlemeden önce kilitlenen kodlama kılavuzu (`docs/annotation-guidelines.md`).

Kodlama kılavuzunda karara bağlanacaklar (ADR-003): Arap harfli Unicode birincil mi; Unicode normalizasyon biçimi (NFC); elif/hemze/ligatür kodlaması; harekelerin dahil olup olmayacağı; izinli karakter envanteri; okunamayan bölge işaretlemesi.

**Kalite:** alt kümenin çift etiketlenmesi + **etiketçiler arası uyum (CER cinsinden)** ölçümü → veri kalitesi ve model üst sınırı (ceiling) belirlenir.

**Geri besleme döngüsü (flywheel):** model belirsiz satırları işaretler → eScriptorium'da insan düzeltir → veri kümesine geri akar. Bu, bir "eğitim hilesi" değil, **mimari bir bileşendir.**

---

## 10. BOA veri toplama yaklaşımı

> **Önce hukuk/etik.** BOA görüntülerinin kullanım/çoğaltma/yayım koşulları kuruma ve belgeye göre değişir. **Öneri:** ham görüntüleri repoda dağıtma; yalnızca türetilmiş veriyi (manifest, koordinat, transkripsiyon) ve provenans/atıf bilgisini tut. Koşullar netleşmeden büyük toplama başlatma. (Bu hukuki görüş değildir; kurum koşulları teyit edilmelidir.)

**Örnekleme eksenleri:** dönem, kâtip eli, belge türü, mürekkep/kâğıt durumu, tarama kalitesi. **Datasheet zorunlu.** **Provenans zorunlu** (kaynak, fon/dosya no, erişim tarihi, haklar).

Soğuk başlangıç: (1) transfer öğrenme, (2) izole harften sentetik satır üretimi, (3) aktif öğrenme.

---

## 11. Versiyonlama stratejisi

Üç şey ayrı versiyonlanır:

- **Kod:** Git + SemVer (`v0.1` … `v1.0`); `main`/`dev`/özellik dalları, PR + review.
- **Veri:** Önce **hash'li manifest** (boş repoda DVC kurmuyoruz), gerçek veri gelince **tam DVC**. Deney, hangi veri sürümüyle eğitildiğini kaydeder.
- **Model:** Model registry mantığı; her ağırlık bir model card + `(kod commit, veri sürümü, config)` üçlüsüyle ilişkilenir.

Altın kural: bir sonuç **(kod + veri + config)** üçlüsüyle birebir tekrarlanabilmeli.

---

## 12. Model stratejisi ve yol haritası

İzole harf CNN'i **ana tanıma yolunda değildir** (yalnızca sentetik üretim + ön-eğitim).

| Faz | Model | Görev | Neden bu fazda | Veri |
|-----|-------|-------|----------------|------|
| F1 | **CRNN + CTC** | Satır → metin (temel HTR) | Düşük veriyle çalışır, yorumlanabilir, sağlam taban | Orta (+sentetik) |
| F1' | İzole harf CNN | *Yardımcı:* sentetik satır + ön-eğitim | Eldeki harf verisinin asıl değeri | Eldeki harf seti |
| F2 | Layout/baseline modeli | Sayfa → bölge/satır/baseline | Tanıma iyileşince darboğaz layout'a kayar | Sayfa annotation |
| F3 | Transformer encoder + CTC / seq2seq | Daha güçlü tanıma | Veri büyüdükçe CRNN'i geçer | Yüksek |
| F4 | **TrOCR** (ince ayar) | SOTA satır tanıma | Yeterli veri + transfer | Yüksek (transferle azalır) |
| F5 | **Donut** (ertelenmiş) | Tam sayfa/yapısal belge anlama | Satır tanıma olgunlaşınca | Çok yüksek |
| F6+ | Dil modeli (n-gram → nöral) | Çıktı düzeltme | Her fazın üstüne | Osmanlıca korpus |

İlke: her fazda **çalışan uçtan uca sistem.** F1 mütevazı ama gerçek; sonraki fazlar onu değiştirir, sıfırdan başlamaz. **F1'de kendi CRNN'imizi yazmadan önce Kraken/Calamari hazır tabanını ince ayarlamak** değerlendirilecek (bkz. Bölüm 20).

PyTorch/HF: çatı baştan PyTorch; HF `transformers` asıl F3–F5'te kritik.

---

## 13. Eğitim stratejisi

Müfredatlı öğrenme (sentetik→gerçek, kolay→zor); transfer öğrenme (Arapça/Farsça HTR'den); insan-döngüde aktif öğrenme; birincil metrikler **CER/WER** + hata türü analizi; her run `(config + veri sürümü + seed)` ile kaydedilir.

---

## 14. Test mimarisi

1. **Birim:** saf fonksiyonlar (normalizasyon, codec, koordinat dönüşümü).
2. **Veri sözleşmesi (data contracts):** manifest şeması, charset uyumu, **split sızıntısı**, **PAGE↔JSONL↔Document tutarlılığı**, **hizalama bütünlüğü**. *Veri-merkezli projede en değerli katman.*
3. **Entegrasyon:** küçük örnekte uçtan uca hat.
4. **Regresyon/eval:** sabit **golden set** üzerinde CER eşik altına düşmemeli (deterministik tohum).

Araçlar: `pytest` + fixtures; CI'da lint + birim + veri-sözleşmesi her PR'da; pahalı eval nightly/etiketli.

---

## 15. Logging, konfigürasyon ve deney takibi

- **Uygulama logging'i:** yapılandırılmış log (`logging`/`loguru`), seviyeler config'ten.
- **Konfigürasyon:** Hydra + OmegaConf; hiçbir hiperparametre koda gömülmez; script profile de config'tir.
- **Deney takibi:** **MLflow ertelenmiştir** → ilk eğitime (F1/v0.4) kadar kurulmaz. O zamana dek metrikler basit yapılandırılmış kayıtlarla tutulur.

Hata yönetimi: alana özgü istisna hiyerarşisi (`RikaOCRError → DataError, ModelError, ConfigError, AlignmentError`). Sessiz `except: pass` yasak.

---

## 16. Arama mimarisi (port — YENİ, ADR-011)

Arama bir **port**tur; kendi motorumuzu yazmayız.

- `core.search` yalnızca **arayüzü** tanımlar: `SearchIndex` (Document'ten indeks kurar) ve `SearchQuery` (kelime/öbek/bulanık/varlık sorgusu).
- Gerçekleme bir **adaptör**dür ve mevcut bir motoru sarar: gömülü için **SQLite FTS5** veya **Tantivy**, ölçek için **OpenSearch**.
- Her arama sonucu Document hizalaması sayesinde bir **koordinata geri bağlanır** (kelimeyi sayfada işaretleme).
- **Gerçekleme ertelenmiştir;** v0.2'de yalnızca port ve veri modeli tasarlanır. Bulanık/öbek araması Arap-harfli + OCR-hatalı metinde zordur; hazır motorların dil/normalizasyon yetenekleri kullanılacaktır.

---

## 17. Açık kaynak yönetişimi (YENİ, ADR-012)

5 yıllık OSS ömrü için tasarımın parçası:

- **Lisans (kod ≠ veri):** koda izin verici lisans (ör. Apache-2.0 veya MIT — Bölüm 20'de karar), veriye ayrı lisans (ör. CC-BY veya kullanım-kısıtlı) `LICENSE` ve `LICENSE-DATA` olarak ayrılır.
- **Katkı süreci:** `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, issue/PR şablonları, kamuya açık roadmap.
- **Donmuş benchmark:** sürümlü, kamuya açık, donmuş test kümesi (`docs/benchmark.md`) — başkalarının kıyaslayabileceği bilimsel omurga; bir araştırma çıktısı olarak yayımlanır. (İç regresyon golden set'inden ayrıdır.)
- **Veri lisansı/etik kaydı:** datasheet + haklar register'ı; provenans zorunlu.
- **Reprodüksiyon sabitleme:** **sürüm kilidi (lockfile)** + **Docker** + determinizm. Mevcut `requirements.txt` içindeki sürümsüz `tensorflow` reprodüksiyon deliğidir; kilitlenecektir.

---

## 18. Gelecek: GUI, web ve platformlaşma (ertelenmiş)

Bugün yazılmaz; mimari sonradan eklenebilecek şekilde kurulur:

```
Çekirdek kütüphane (rikaocr)        ← kararlı, UI'den habersiz
        ▲ temiz Python API
   (ertelendi) FastAPI servis katmanı
        ▲ REST/WS
   İstemciler: CLI · (ertelendi) Web · (ertelendi) Masaüstü GUI
```

Kural: **UI çekirdeğe değil, API'ye konuşur.** "BOA AI platformu" (arama, indeksleme, sınıflandırma) bu servis katmanının üzerine ayrı uygulamalar olarak eklenir.

---

## 19. Riskler ve eleştirel notlar

| Risk | Etki | Azaltma |
|------|------|---------|
| **Veri darboğazı** (asıl risk) | Proje durur | Bütçeyi veriye/etiketlemeye; sentetik + transfer + aktif öğrenme |
| Hizalamayı kaybetme | Arama/işaretleme özelliği çöker | ADR-009: hiza birinci sınıf çıktı; data-contract testleri |
| Kürsiv segmentasyon yanılgısına dönüş | Yıllar kaybı | ADR-001; izole harf yalnızca yardımcı |
| Kodlama politikasının geç belirlenmesi | Tüm GT yeniden işlenir | Etiketlemeden ÖNCE kilitle (Bölüm 20) |
| BOA görüntü hakları | Yayım/dağıtım engeli | Ham görüntü dağıtma; provenans + türetilmiş veri |
| **Kapsam genişlemesi (scope creep)** | Hiçbir şey bitmez | Tek dikey dilim: Rik'a satır tanıma, uçtan uca; gerisi ertelenmiş |
| Altyapı tiyatrosu (boş repoda ağır kurulum) | Yavaşlama | MLflow/DVC/plugin/FastAPI ertelendi |
| Yeniden üretilemeyen deneyler | Bilimsel değer kaybı | (kod+veri+config) üçlüsü + lockfile/Docker |

> **Sürdürülen uyarı:** En büyük tehlike teknik değil, kapsam genişlemesidir. Mimari çok-yazılı ve platform geleceğini *destekler*, ama **yürütme tek bir dikey dilimde** (Rik'a satır tanıma, uçtan uca, küçük ama gerçek) yoğunlaşmalıdır.

---

## 20. Senin vermen gereken açık kararlar

v0.2 ile birçok yapı netleşti; geriye şu kararlar kaldı (veri fazından önce):

1. **GT kodlama politikası (ADR-003):** Arap harfli Unicode birincil + transliterasyon ayrı + harekeler hariç (önerim). Onaylıyor musun?
2. **F1 stratejisi:** Kendi CRNN'imiz mi, yoksa **Kraken/Calamari hazır tabanını ince ayar mı** (önerim: önce hazır taban)?
3. **Kod lisansı:** Apache-2.0 (patent koruması; önerim) mi, MIT (en sade) mi?
4. **Veri lisansı:** CC-BY mı, kullanım-kısıtlı mı (BOA haklarına göre)?
5. **Deney takibi (ertelendiğinde):** F1'de MLflow (yerel, açık kaynak — önerim) mi, W&B mi?

---

## 21. Değişiklik günlüğü (v0.1 → v0.2)

| # | Değişiklik | Bölüm |
|---|-----------|-------|
| 1 | **Document alan modeli** eklendi (`Document→Page→Region→Line→Word→Token`) | 3, 5 (`core.document`) |
| 2 | **Koordinat↔metin hizalaması** çekirdek ilke yapıldı; PAGE kaynak, JSONL türetilmiş | 1, 6.1, ADR-009 |
| 3 | **`core.linguistics` (Ottoman NLP)** katmanı eklendi (normalization, transliteration, language_model, lexicon, morphology, abbreviations, ner) | 5.1 |
| 4 | **`data.metadata`** katmanı eklendi (provenance, catalog, archive, document_info) | 5.2 |
| 5 | **`core.search` portu** eklendi (yalnızca arayüz; motor adaptörle, gerçekleme ertelendi) | 16, ADR-011 |
| 6 | **`core.script_profile`** (yazı-nötr çekirdek) eklendi (Rik'a/Divani/Siyakat/Talik) | 5.3, ADR-010 |
| 7 | **Erteleme** kararı: plugin keşfi, MLflow, FastAPI, GUI, Donut, tam DVC, gelişmiş NLP gerçeklemeleri | 5, 11, 15, 18 |
| 8 | **Açık kaynak yönetişimi** eklendi (LICENSE/LICENSE-DATA, CONTRIBUTING, benchmark, lockfile/Docker) | 17, ADR-012 |
| 9 | **train.py / predict.py** için CLI'ya taşıma notu düşüldü | 7 |
| + | `core.reading_order` (RTL/bidi) modülü eklendi (hizalama ve okuma akışı için) | 5 |

---

*Bu belge yaşayan bir dokümandır. Onaylanan kararlar ADR olarak sabitlenecek, değişiklikler sürüm notlarıyla işlenecektir. v0.2, dondurma (freeze) için adaydır; Bölüm 20'deki kararlar netleşince v1.0-mimari olarak dondurulabilir.*
