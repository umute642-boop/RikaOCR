# ADR-003: Ground-Truth Kodlama Politikası

- **Statü:** Kabul
- **Tarih:** 2026-06-29
- **Karar verenler:** Umut

## Bağlam
Etiketçilerin gireceği ve modelin öğreneceği "doğru metin"in nasıl kodlanacağı,
etiketlemeden önce kilitlenmesi gereken en kritik karardır. Yanlış başlanırsa
tüm etiketli veri yeniden işlenir.

## Karar
1. Ground-truth **Arap harfli Unicode** olarak girilir (birincil temsil).
2. Latin **transliterasyon ayrı bir modüldür** (`core.linguistics.transliteration`);
   tanımanın çıktısı değildir.
3. **Harekeler şimdilik dahil edilmez.**
4. Unicode normalizasyon biçimi NFC; izinli karakter envanteri annotation
   kılavuzunda sabitlenir.

## Gerekçe
Modelin öğrenmesi gereken şey yazının kendisidir; transliterasyon dil/kural
bağımlı bir dönüşümdür ve tanımayla karıştırılırsa hem veri hem model kirlenir.
Arşiv Rik'a metinleri genelde harekesizdir; harekesiz başlamak sınıf uzayını ve
etiketleme yükünü küçük tutar.

## Sonuçlar
- `docs/annotation-guidelines.md` bu politikaya göre yazılır.
- Codec (M2) ve dataset normalizasyonu (M4) bu kurala bağlıdır.
- Harekeli metin gelecekte istenirse ayrı GT katmanı + yeni ADR gerektirir.
