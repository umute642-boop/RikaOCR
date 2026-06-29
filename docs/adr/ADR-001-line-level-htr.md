# ADR-001: Ana Tanıma Ekseni — Satır Düzeyi HTR

- **Statü:** Kabul
- **Tarih:** 2026-06-29
- **Karar verenler:** Umut

## Bağlam
Rik'a bitişik (kürsiv) bir yazıdır; harf biçimi konuma göre (baş/orta/son/münferit)
değişir ve harfler birbirine bağlanır. Tanıma yaklaşımı, izole harf sınıflandırma
ile satır düzeyi dizi tanıma arasında seçilmelidir.

## Karar
Ana tanıma ekseni **satır düzeyi HTR**'dir (segmentasyonsuz; CTC/seq2seq). İzole
harf yalnızca yardımcı veri (sentetik üretim + ön-eğitim) olarak kullanılır.

## Gerekçe
Bitişik yazıda güvenilir harf segmentasyonu çözülmemiş bir problemdir. Modern
SOTA (Kraken, Calamari, TrOCR) satır düzeyinde çalışır; harf hizalaması model
içinde örtük öğrenilir. İzole harf yolu kırılgan ve ölçeklenemez.

## Sonuçlar
- Tüm veri hattı satır görüntüsü + transkripsiyon çiftleri üzerine kurulur.
- İzole harf seti çöpe atılmaz; sentetik satır üretiminde değerlendirilir.
- Model yol haritası (F1: CRNN+CTC) bu karara dayanır.
