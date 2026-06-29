# ADR-005: Etiketleme Aracı — eScriptorium

- **Statü:** Kabul
- **Tarih:** 2026-06-29
- **Karar verenler:** Umut

## Bağlam
Etiketleme için kendi aracımızı mı yazacağız, yoksa mevcut bir araç mı
kullanacağız?

## Karar
**eScriptorium** kullanılır; kendi annotation arayüzümüz yazılmaz.

## Gerekçe
eScriptorium açık kaynaktır, PAGE/ALTO destekler ve "model tahmin et → insan
düzelt" döngüsünü destekler. Kendi arayüzünü yazmak yıllarca sürecek bir dikkat
dağıtıcıdır ve projenin asıl değerini üretmez.

## Sonuçlar
- M3'te operasyonel entegrasyon; insan-döngüde geri besleme döngüsü kurulur.
- Codec, eScriptorium çıktısını (PAGE/ALTO) tüketir.
