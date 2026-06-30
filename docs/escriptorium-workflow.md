# RikaOCR - eScriptorium Etiketleme ve Ingest Akışı

Bu doküman, ham arşiv görüntülerinin (özellikle BOA evraklarının) RikaOCR sistemine nasıl dahil edileceğini ve eScriptorium kullanılarak nasıl etiketleneceğini tanımlar.

## 1. İlk Ingest (Sisteme Kayıt)

Ham görüntüler (JPG/PNG vb.) doğrudan sisteme işlenmez, opak dosyalar olarak ele alınır.

* Ham dosyalar yerel `data/raw/` dizinine konur (Git tarafından izlenmez).
* `ingest_source()` fonksiyonu çağrılarak içerik hash'i (SHA-256) ve bayt boyutu hesaplanır.
* İşlem sırasında haklar kapısı (Rights Gate) zorunludur. `RightsStatus.CLEARED` olmayan hiçbir belge dağıtım hattına giremez.
* İşlem sonucu `SourceRecord` oluşturulur ve JSONL manifestosuna eklenir.

## 2. eScriptorium Etiketleme

* Kaydı oluşturulan ham görüntüler eScriptorium platformuna yüklenir.
* Kullanıcı (insan) tarafından satır bölme (segmentation) ve transkripsiyon (GT) işlemleri yapılır.
* Transkripsiyon kuralları **ADR-003 (GT Kodlama Politikası)** standartlarına tabidir.
* Etiketlenen veriler eScriptorium'dan PAGE-XML formatında dışa aktarılır.

## 3. RikaOCR'ye Entegrasyon ve Metadata Bağlama

* Dışa aktarılan PAGE-XML dosyası `from_page_xml()` (M2 Codec) ile kayıpsız bir şekilde `Document` nesnesine dönüştürülür.
* Arşiv bilgileri (Fon, Dosya, Gömlek, Tarih) `DocumentMetadata` nesnesine doldurulur.
* `attach()` fonksiyonu ile bu yapısal metadata, `Document` nesnesine bağlanır.

## 4. Dışa Aktarım (Export)

* `to_json()` kullanılarak `Document` nesnesi, metadata ile birlikte türetilmiş JSON formatına çevrilir.
* Bu JSON dosyaları (eğitim verisi), hakları temizlenmişse repoda veya model eğitim hattında (`M4`) kullanılır.

## İlgili Kararlar (ADR)

* **ADR-003** — GT kodlama politikası (Arap harfli Unicode; harekeler hariç).
* **ADR-004** — PAGE-XML kaynak biçimi.
* **ADR-005** — Etiketleme aracı olarak eScriptorium.
* **ADR-014** — Veri lisansı (KARAR BEKLİYOR); haklar kapısının dayanağı.
* **ADR-017** — PAGE-XML round-trip garantisi.
