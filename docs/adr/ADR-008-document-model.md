# ADR-008: Belge-Merkezli Mimari — Document Alan Modeli

- **Statü:** Kabul
- **Tarih:** 2026-06-29
- **Karar verenler:** Umut

## Bağlam
v0.1'de sistemin merkezinde kalıcı bir belge temsili yoktu; modüller ad-hoc
temsillerle konuşma riski taşıyordu.

## Karar
Çekirdeğe `Document → Page → Region → Line → Word → Token` **alan modeli**
(aggregate) yerleştirilir. Tüm modüller bu nesne üzerinden konuşur.

## Gerekçe
Metadata, dilbilim, arama ve transliterasyonun ortak bir dile ihtiyacı vardır.
Merkezi nesne olmadan entegrasyon borcu birikir.

## Sonuçlar
- `core.document` modülü çekirdek tiptir (M1).
- PAGE-XML ile kayıpsız round-trip; `schema_version` ile sürümlenir.
