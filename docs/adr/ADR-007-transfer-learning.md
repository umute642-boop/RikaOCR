# ADR-007: Soğuk Başlangıç — Transfer Öğrenme

- **Statü:** Kabul
- **Tarih:** 2026-06-29
- **Karar verenler:** Umut

## Bağlam
Etiketli Rik'a verisi başlangıçta azdır; sıfırdan eğitim çok veri ister.

## Karar
Sıfırdan eğitim yerine **transfer öğrenme** (Arapça/Farsça HTR modellerinden
ince ayar) önceliklidir; sentetik veri ve aktif öğrenme ile desteklenir.

## Gerekçe
Mevcut Arap-harfli HTR ağırlıklarından başlamak, az veriyle çok daha verimlidir.

## Sonuçlar
- F1 stratejisi (ADR-015) hazır taban ince ayarıyla uyumludur.
- Sentetik üretim (izole harf) ve aktif öğrenme döngüsü tamamlayıcıdır.
