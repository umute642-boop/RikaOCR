# ADR-021: Pipeline Sınırları, Çıktı Formatları ve CLI (M7)

- **Statü:** Kabul
- **Tarih:** 2026-06-30
- **Karar verenler:** Umut

## Bağlam
M7'de parçalar (veri → segmentasyon → tanıma → değerlendirme) tek bir akışta
birleştirildi. Bu ADR; orkestrasyon (`Pipeline`), sonuçların diske yazımı
(çıktı katmanı) ve komut satırı arayüzü (CLI) arasındaki sorumluluk sınırlarını
ve çıktı format konvansiyonlarını sabitler.

## Karar
1. **`Pipeline` yalnızca orkestrasyondur:** enjekte edilen `Segmenter` +
   `Recognizer`'ı birleştirir (`run(image) -> Document`); G/Ç yapmaz, motor
   oluşturmaz, değerlendirme yapmaz. Motorlar dışarıdan verilir (test/araştırma
   için takılıp çıkarılabilir).
2. **Çıktı yazımı ayrı bir katmandır** (`rikaocr.output`): `Document`'ı diske
   yazar. PAGE-XML serileştirmesi mevcut `PageXmlCodec`'e delege edilir (mantık
   çoğaltılmaz); düz metin `document_to_text` ile okuma sırasında üretilir.
   Yeni formatlar (ALTO, hOCR, JSONL) yalnızca bu katmana eklenir.
3. **Birincil çıktı PAGE-XML'dir** (varsayılan); düz metin ikincil/insan-okur
   formattır. PAGE-XML, M2 round-trip garantisini (ADR-017) taşıdığı için
   yeniden işlenebilir kanonik formattır.
4. **Değerlendirme çıktıdan ayrıdır** (ADR-020 ilkesi): `Pipeline` `Document`
   üretir; onu ground-truth'a karşı puanlamak `evaluation` katmanının işidir
   (`evaluate_document`).
5. **CLI ayrı bir modüldür** (`rikaocr.cli`) ve legacy kök `predict.py`'ye
   **dokunmaz** (regresyon riskini önlemek için). Komut:
   `python -m rikaocr.cli <image> -o <out> [--format page|text]
   [--engine dummy|kraken] [--seg-model ...] [--rec-model ...]`.
6. **CLI test edilebilir ve hafiftir:** mantık `build_pipeline()` ve
   `main(argv)` olarak ayrılır; varsayılan `dummy` motoruyla ML çalıştırmadan
   uçtan uca test edilir. Kraken motorları yalnızca seçildiğinde **tembel**
   içe aktarılır; `import rikaocr.cli` ve `--help` ağır bağımlılık çekmez.
7. **Konsol giriş noktası:** `rikaocr = "rikaocr.cli:main"` (`[project.scripts]`).
8. **Satır sonu normalizasyonu:** depo köküne `.gitattributes`
   (`* text=auto eol=lf`) eklenir; Windows/WSL2/CI arası tutarlılık ve gürültüsüz
   diff için. İkili varlıklar `binary` olarak işaretlenir.

## Gerekçe
Orkestrasyon, G/Ç ve CLI'yi ayırmak her katmanı bağımsız test edilebilir ve
değiştirilebilir kılar (ADR-011 ruhuyla uyumlu). Çıktı yazımını tek katmanda
toplamak, ileride format eklemeyi pipeline'a dokunmadan mümkün kılar. CLI'yi
`dummy` varsayılanı + tembel Kraken ile kurmak, CI'da ML olmadan tam kapsam
sağlar. Legacy `predict.py`'ye dokunmamak, mevcut davranışın regresyonunu önler.

## Sonuçlar
- `python -m rikaocr.cli` ve `rikaocr` komutu `dummy` motoruyla hemen çalışır;
  `--engine kraken` yalnızca WSL2/F1 ortamında (model hazır olduğunda) anlamlıdır.
- Kraken motorlu uçtan uca CLI doğrulaması F1'e bırakılmıştır; CLI plumbing'i
  `dummy` ile tam test edilir.
- Yeni çıktı formatları ve gelişmiş CLI seçenekleri (toplu işleme, dizin girişi)
  ileride bu sınırlar korunarak eklenir.
