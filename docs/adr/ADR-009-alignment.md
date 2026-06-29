# ADR-009: Koordinat↔Metin Hizalaması Birinci Sınıf Çıktıdır

- **Statü:** Kabul
- **Tarih:** 2026-06-29
- **Karar verenler:** Umut

## Bağlam
Projenin amiral özelliği (belgede kelimeyi bulup işaretleme) metnin görüntüdeki
konumuyla bağlı olmasını gerektirir. Düz metin temsili bu hizayı kaybeder.

## Karar
Tanınan/etiketli metin daima geometriyle ilişkilidir (satır zorunlu, kelime
hedef, token opsiyonel). Hiza birinci sınıf çıktıdır; JSONL tek/kanonik temsil
olamaz.

## Gerekçe
Hiza kaybedilirse arama+işaretleme özelliği çöker ve büyük bir yeniden yazım
gerekir.

## Sonuçlar
- Document modeli her düğümde geometri taşır.
- Veri-sözleşmesi testleri hiza bütünlüğünü doğrular.
- Arama indeksi sonuçları koordinata geri bağlar.
