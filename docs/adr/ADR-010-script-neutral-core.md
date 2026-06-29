# ADR-010: Yazı-Nötr Çekirdek + Script Profile

- **Statü:** Kabul
- **Tarih:** 2026-06-29
- **Karar verenler:** Umut

## Bağlam
Gelecekte Divani, Siyakat, Talik gibi yazı türleri de desteklenmek istenebilir.

## Karar
Çekirdek tek bir yazı türüne bağlı değildir. Her yazı türü bir **ScriptProfile**
(charset, normalizasyon, okuma kuralları, model referansı) olarak tanımlanır;
bu profil **kod değil, veri/yapılandırmadır**.

## Gerekçe
Yeni yazı türü = yeni profil + veri/model; çekirdek hat değişmez. Bu, ileride
çekirdeği yeniden yazmayı önler.

## Sonuçlar
- `core.script_profile` modülü + `configs/script_profiles/rika.yaml`.
- Proje adı "RikaOCR" kalır; çekirdek paketler yazı-nötr yazılır.
