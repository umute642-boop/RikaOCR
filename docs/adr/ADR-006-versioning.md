# ADR-006: Versiyonlama — Git + Hash Manifest → DVC

- **Statü:** Kabul
- **Tarih:** 2026-06-29
- **Karar verenler:** Umut

## Bağlam
Kod, veri ve model farklı yaşam döngülerine sahiptir; büyük dosyalar Git'e
konmamalıdır.

## Karar
Kod: Git + SemVer. Veri/model: önce **hash'li manifest**, gerçek veri büyüyünce
**tam DVC**. Her sonuç `(kod commit + veri sürümü + config)` üçlüsüyle
ilişkilendirilir.

## Gerekçe
Boş repoda ağır DVC kurmak "altyapı tiyatrosu"dur. Veri henüz yokken hash'li
manifest yeterlidir; DVC, gerçek veri geldiğinde (M4) karşılığını verir.

## Sonuçlar
- M0–M3: hash'li manifest. M4+: DVC.
- Yeniden üretilebilirlik üçlüsü her deneyde kaydedilir.
