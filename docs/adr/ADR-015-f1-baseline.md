# ADR-015: F1 Tabanı — Önce Kraken/Calamari

- **Statü:** Kabul
- **Tarih:** 2026-06-29
- **Karar verenler:** Umut

## Bağlam
İlk çalışan HTR modeli (F1) için kendi CRNN'imizi mi yazalım, yoksa hazır bir
tabanı mı ince ayarlayalım?

## Karar
İlk aşamada **Kraken/Calamari hazır tabanı** Rik'a'ya ince ayarlanır. Kendi
CRNN+CTC modelimiz sonradan bir alternatif olarak değerlendirilir.

## Gerekçe
Hazır taban çok daha hızlı sonuç verir, transfer öğrenmeyle (ADR-007) uyumludur
ve ilk CER/WER ölçümünü erkene çeker. Kendi modelimiz ancak gerekçe doğunca
yazılır.

## Sonuçlar
- M5'te `kraken_adapter.py` öncelikli; `crnn.py` alternatif olarak ertelenir.
- `Recognizer` arayüzü her iki gerçeklemeyi de destekler.
