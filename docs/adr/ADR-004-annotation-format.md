# ADR-004: Annotation Biçimleri — PAGE-XML Kaynak

- **Statü:** Kabul
- **Tarih:** 2026-06-29
- **Karar verenler:** Umut

## Bağlam
Layout + metin etiketlerinin hangi biçimde tutulacağı, koordinat↔metin
hizalamasının korunması açısından kritiktir.

## Karar
**PAGE-XML** kaynak (source of truth); **ALTO-XML** dışa aktarım; **JSONL**
yalnızca türetilmiş eğitim temsilidir ve elle düzenlenmez.

## Gerekçe
PAGE-XML, HTR dünyasının (eScriptorium, Transkribus, OCR-D) fiili standardıdır
ve bölge/satır/baseline/metin hiyerarşisini taşır. JSONL yalın ve hızlıdır ama
koordinat taşımaz; bu yüzden kaynak değil türev olmalıdır.

## Sonuçlar
- Düzenlemeler PAGE üzerinde yapılır; JSONL yeniden üretilir.
- Codec (M2) PAGE↔Document round-trip'i kayıpsız sağlamalıdır.
