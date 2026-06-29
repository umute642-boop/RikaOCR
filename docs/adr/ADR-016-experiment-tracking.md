# ADR-016: Deney Takibi — F1'de MLflow

- **Statü:** Kabul
- **Tarih:** 2026-06-29
- **Karar verenler:** Umut

## Bağlam
Deney takibi gerekli ama boş repoda/erken fazda kurmak gereksiz yüktür.

## Karar
Deney takibi **MLflow** (yerel, açık kaynak) ile yapılır ve **F1'de (M5)**
devreye alınır; daha önce kurulmaz.

## Gerekçe
M0–M4'te eğitilecek model yoktur; MLflow'u erken kurmak "altyapı tiyatrosu"dur.
MLflow yereldir, açık kaynaktır ve dış servis bağımlılığı getirmez.

## Sonuçlar
- M5'te metrik/parametre/artefakt takibi MLflow'a yazılır.
- Uygulama logging'i ve config'ten ayrı tutulur.
