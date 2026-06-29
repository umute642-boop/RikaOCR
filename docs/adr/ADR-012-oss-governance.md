# ADR-012: Açık Kaynak Yönetişimi Tasarımın Parçasıdır

- **Statü:** Kabul
- **Tarih:** 2026-06-29
- **Karar verenler:** Umut

## Bağlam
5 yıllık bir açık kaynak projenin ömrünü, kod kadar yönetişim de belirler.

## Karar
Yönetişim tasarımın parçasıdır: kod ve veri için **ayrı lisans**, katkı süreci
(CONTRIBUTING, CODE_OF_CONDUCT), donmuş kamu benchmark'ı, ve reprodüksiyon
sabitleme (lockfile + Docker).

## Gerekçe
Bunlar olmadan proje sürdürülebilir ve atıf alabilir bir açık kaynak çalışma
olamaz.

## Sonuçlar
- `LICENSE`, `LICENSE-DATA`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` (M0).
- `docs/benchmark.md` (v1.0) ve lockfile/Docker (ilerleyen fazlar).
