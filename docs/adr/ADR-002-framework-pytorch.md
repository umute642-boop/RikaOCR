# ADR-002: Derin Öğrenme Çatısı — PyTorch + HuggingFace

- **Statü:** Kabul
- **Tarih:** 2026-06-29
- **Karar verenler:** Umut

## Bağlam
Proje başlangıçta TensorFlow ile kuruldu, ancak uzun vadeli hedef modeller
(TrOCR, Donut, ViT, Kraken, Calamari) farklı bir ekosistemde yer alıyor.

## Karar
Çatı **PyTorch + HuggingFace**'tir. TensorFlow bırakılmıştır.

## Gerekçe
Hedeflenen modellerin tamamı PyTorch ekosistemindedir. Geçiş maliyeti proje
başında minimumdur; TF'de kod biriktikten sonra geçmek ikinci bir yeniden yazım
demektir.

## Sonuçlar
- requirements'taki sürümsüz `tensorflow` kaldırılır.
- PyTorch ve HF, M5'te opsiyonel `[train]` extras olarak eklenir (erken kurulmaz).
