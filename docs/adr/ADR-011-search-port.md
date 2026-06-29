# ADR-011: Arama Bir Port'tur; Motor Yazılmaz

- **Statü:** Kabul
- **Tarih:** 2026-06-29
- **Karar verenler:** Umut

## Bağlam
Araştırmacı için belge içi kelime/öbek/bulanık arama gerekir; ama kendi arama
motorunu yazmak çözülmüş bir işi yeniden icat etmektir.

## Karar
`core.search` yalnızca **arayüzü** (port) tanımlar; gerçekleme bir mevcut motoru
saran adaptördür (SQLite FTS5 / Tantivy / OpenSearch). Gerçekleme ertelenmiştir.

## Gerekçe
Arap-harfli + OCR-hatalı metinde bulanık/öbek araması zordur; hazır motorların
dil/normalizasyon yetenekleri kullanılır.

## Sonuçlar
- v0.2'de yalnızca port + sorgu modeli; gerçekleme M7.
- Her sonuç Document hizası sayesinde koordinata bağlanır.
