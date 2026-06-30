# ADR-019: Tanıma Motoru Olarak Kraken ve WSL2 Eğitim Ortamı (M5)

- **Statü:** Kabul
- **Tarih:** 2026-06-30
- **Karar verenler:** Umut

## Bağlam
M5'te ilk gerçek HTR tanıma yeteneğini ekliyoruz. ADR-015, F1 tabanında sıfırdan
model yazmak yerine olgun bir motorla başlamayı; ADR-011, dış motorların doğrudan
çekirdeğe girmek yerine bir port/adaptör arkasında sarılmasını kararlaştırmıştı.
Bu ADR, somut motor seçimini, eğitim ortamını ve veri alışveriş biçimini sabitler.

## Karar
1. **F1 tanıma motoru Kraken'dir** (`kraken>=5`). Satır düzeyi HTR'ye, Arap
   harfli/RTL yazıya ve `ketos` ile eğitime doğrudan uygundur.
2. **Motor adaptör arkasında izole edilir:** `recognition.kraken_adapter.
   KrakenRecognizer`, çekirdek `Recognizer` Protocol'ünü uygular. Kraken **tembel
   (lazy) içe aktarılır** — modül import'u veya test paketi Kraken gerektirmez.
3. **Eğitim ortamı WSL2 (Ubuntu) + CUDA'dır.** Kraken Windows'ta resmî olarak
   desteklenmediğinden eğitim Linux tarafında yapılır; RikaOCR yalnızca veri
   hazırlar ve modeli sarar. Akış `docs/kraken-training.md`'de belgelenir.
4. **Veri alışverişi `.gt.txt` sidecar formatıdır:** `training.kraken_export`,
   satır görüntüsünün yanına aynı adlı `.gt.txt` dosyası yazar (UTF-8, sondaki
   newline yok). Eğitim **elle `ketos`** ile yürütülür; RikaOCR `ketos`'u
   sarmalamaz.
5. **Bağımlılıklar tek opsiyonel `[train]` grubunda toplanır:** `kraken>=5` ve
   `mlflow>=2`. Çekirdek ve `[data]` katmanı bundan etkilenmez. mypy `--strict`
   korunur; `kraken.*` ve `mlflow.*` için dar `ignore_missing_imports`
   override'ları eklenmiştir (her ikisi de tembel içe aktarıldığından CI'da
   kurulu olmaları gerekmez).
6. **Bağımsız değerlendirme:** Kraken kendi CER'ini raporlasa da, resmî metrik
   RikaOCR'ın motordan bağımsız `evaluation` modülüdür (CER/WER, ADR'siz saf
   stdlib). Deney takibi MLflow ile yapılır (ADR-016).

## Gerekçe
Kraken, baseline tabanlı satır HTR'sinde olgun ve RTL/Arap yazıya yatkındır;
sıfırdan CRNN yazma maliyetini F1'de üstlenmek gereksiz risktir (ADR-015). Tembel
içe aktarma + opsiyonel `[train]` grubu, ağır ve platforma duyarlı bu motoru
çekirdeğin hafifliğini ve test edilebilirliğini bozmadan tutar. Eğitimi WSL2'ye
taşımak, Windows'taki Kraken desteği boşluğunu pratik biçimde çözer. Sidecar +
elle `ketos`, ilk turda araç sarmalamanın kırılganlığından kaçınır.

## Sonuçlar
- `recognition.kraken_adapter`'ın Kraken'e bağlı davranışı yalnızca model
  hazır olduğunda (WSL2'de) uçtan uca doğrulanır; o ana dek `pytest.importorskip`
  ile korunur. Tembel-import garantisi ise koşulsuz test edilir.
- Eğitim, geliştirme makinesinin Windows tarafında değil WSL2'de yürür; çıktı
  `.mlmodel` dosyası `KrakenRecognizer` ile yüklenir.
- İleride farklı bir motor (Calamari, kendi CRNN'imiz) gerekrse yeni bir adaptör
  ve ADR ile eklenir; çekirdek değişmez.
