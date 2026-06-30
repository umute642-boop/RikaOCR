# ADR-018: Veri Seti Yapısı ve Görüntü Bağımlılıkları (M4)

- **Statü:** Kabul
- **Tarih:** 2026-06-30
- **Karar verenler:** Umut

## Bağlam
M4'te ilk kez piksele dokunduk: etiketli `Document` nesnelerini satır görüntüsü +
metin çiftlerine çevirip eğitime hazır bir veri seti ürettik. Bu, M0–M3 boyunca
sürdürülen "sıfır runtime bağımlılığı" (stdlib-only) ilkesinin bilinçli olarak
gevşetilmesini gerektirdi.

## Karar
1. **Görüntü bağımlılıkları opsiyonel `[data]` extras'tır:** Pillow + NumPy.
   OpenCV ertelenmiştir ve gerektiğinde ayrı `[cv]` extra olarak gelir. Çekirdek
   (`core`, `data.ingest`, `data.metadata`) **stdlib-only kalır**; yalnızca
   `data.dataset / augmentation / synthesis` bu extras'ı ister.
2. **Görüntü kütüphanesi tek modülde izole edilir** (`data.dataset.image_io`).
   mypy `--strict` korunur; PIL için dar bir `ignore_missing_imports` override'ı
   eklenmiştir (NumPy tipli olduğundan override gerekmez).
3. **Split belge düzeyinde ve deterministiktir:** `doc_id`'nin SHA-256 hash'i
   `[0,1)` kesrine eşlenir; varsayılan oran 80/10/10. Aynı belgenin tüm satırları
   aynı split'e düşer (sızıntı yok).
4. **Klasör yapısı:** `<output>/<version>/{train,val,test}/lines/` + per-split
   JSONL manifest (`manifests/`) + `datasheet.md`. `data/processed/` Git'e girmez.
5. **Satır kırpımı v1:** bbox kırpımı (+ opsiyonel poligon→beyaz maske). Eğri
   satırı düzleştirme (dewarping) **ertelenmiştir** (bkz. ADR-009).
6. **Augmentation yalnızca train'e** uygulanır; seedlenebilir ve deterministiktir
   (sabit seed → bayt-aynı çıktı). Val/test gerçek veridir.
7. **Sentetik üretim kaba v1'dir** (`GlyphConcatSynth` — glyph birleştirme);
   kürsiv bağlanmayı modellemez, yalnızca hattı test etmek için yardımcıdır.
   Gerçekçi sentez ileride ayrı bir ADR ile ele alınır.

## Gerekçe
Pillow + NumPy, satır kırpma ve temel augmentation'ın neredeyse tamamını hafif
bir ayak iziyle karşılar; OpenCV'nin ağırlığı bu aşamada gereksizdir. Bağımlılığı
opsiyonel tutmak ve tek modülde izole etmek, çekirdeğin hafifliğini ve katı tip
güvenliğini korur. Belge düzeyi deterministik split, akademik çalışmalarda veri
sızıntısını (modelin kendini kandırması) önler.

## Sonuçlar
- Geliştirme/CI kurulumu artık `pip install -e ".[dev,data]"` kullanır.
- M5 (ilk HTR modeli) doğrudan bu veri setini ve manifestleri tüketir.
- Dewarping, gerçekçi sentez ve OpenCV gerektiren işlemler ileri milestone'lara
  bırakılmıştır.
