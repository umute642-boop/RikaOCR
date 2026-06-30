# ADR-020: Düzen Analizi (Segmentation) Portu (M6)

- **Statü:** Kabul
- **Tarih:** 2026-06-30
- **Karar verenler:** Umut

## Bağlam
M5'te tanıma (recognition) yeteneği eklendi, ancak satır geometrisi yalnızca elle
hazırlanmış PAGE-XML'den geliyordu. Uçtan uca "ham görüntü → metin" akışı için
sayfadan satır/bölge geometrisini üreten bir düzen analizi katmanı gerekir.
ADR-011 dış motorların doğrudan çekirdeğe girmeyip adaptörle sarılmasını,
ADR-009 ise koordinat↔metin hizalamasının birinci sınıf bir çıktı olmasını
şart koşar. Bu ADR, segmentasyon katmanının somut tasarımını sabitler.

## Karar
1. **Segmentasyon bir porttur:** `layout.base.Segmenter` Protocol'ü
   (`segment(image) -> SegmentationResult`). Motorlar (Kraken vb.) bu portu
   uygulayan adaptörlerle sarılır; çekirdek motor ayrıntısından habersiz kalır.
2. **Çıktı ince, motor-nötr bir DTO'dur:** `SegmentationResult` yalnızca üretilen
   `Region`/`Line` geometrisini taşır; sayfa bilgisi (boyut) ve okuma sırası
   ataması `segment_document` yardımcı fonksiyonuna bırakılır. Bu, motor çıktısı →
   çekirdek model dönüşümünü tek ve açık bir noktada toplar.
3. **Segmentasyon ve tanıma ayrıştırılmıştır (decoupled):** Segmenter yalnızca
   *nerede* (geometri), recognizer yalnızca *ne* (metin) sorusunu yanıtlar.
   `segment_document` metni doldurmaz; çıktı `recognition.recognize_document`'a
   beslenir. Böylece her iki motor bağımsız olarak değiştirilebilir/test edilebilir
   (ADR-011) ve hizalama tek yönde, kayıpsız ilerler (ADR-009).
4. **Okuma sırası M6'da deterministik atanır:** `order_reading`, bölge ve
   satırları üstten-alta, sonra sağdan-sola (RTL — Rik'a) sıralar ve
   `reading_index` alanlarını yeniden yazar; geometrisi çözülemeyen öğeler sırası
   korunarak sona alınır. Motordan gelen sıra yedek/girdi kabul edilir.
5. **Motor adaptörü tembel (lazy) içe aktarılır:** `KrakenSegmenter`, `kraken.blla`
   ve model yükleme modüllerini yalnızca çağrı anında yükler; modül import'u
   `[train]` extra'sını gerektirmez. Kraken kurulu değilken örnekleme açık bir
   `RikaOCRError` ile reddedilir. Çıktı eşleme (`map_kraken_segmentation`) ise
   saf, Kraken'siz bir fonksiyondur ve mock ile test edilebilir.
6. **Kapsam yalnızca geometridir:** Tüm satırlar tek bir `RegionType.PARAGRAPH`
   bölgesine konur; bölge sınıflandırma ve eğri satır düzleştirme (dewarping)
   ertelenmiştir (bkz. ADR-009).

## Gerekçe
İnce DTO + tek dönüşüm noktası, motor çıktısının tuhaflıklarını çekirdek modelden
uzak tutar; mypy `--strict` altında dönüşümü denetlemeyi kolaylaştırır.
Segmentasyon-tanıma ayrışması, her motorun ayrı ayrı doğrulanmasını ve ileride
değiştirilmesini mümkün kılar; eşleme fonksiyonunu saf tutmak, ağır motor kurulu
olmadan bile mantığın test edilebilmesini sağlar. RTL okuma sırasını çekirdekte
deterministik üretmek, akademik tekrar-üretilebilirliği güvence altına alır.

## Sonuçlar
- `KrakenSegmenter.segment`'in Kraken'e bağlı yolu yalnızca model hazır olduğunda
  (WSL2/F1) uçtan uca doğrulanır; o ana dek `pytest.importorskip` ile korunur.
  Eşleme mantığı ise mock ile sınanır.
- Uçtan uca zincir `segment_document → recognize_document → evaluate` artık
  `Dummy*` motorlarıyla (ML'siz) bütünüyle test edilebilir.
- Bölge sınıflandırma, dewarping ve gerçek segmentasyon modeli eğitimi ileri
  milestone'lara bırakılmıştır.
