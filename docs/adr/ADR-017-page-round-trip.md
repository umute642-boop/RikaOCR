# ADR-017: PAGE-XML Round-Trip Garantisi

- **Statü:** Kabul
- **Tarih:** 2026-06-30
- **Karar verenler:** Umut

## Bağlam
M2'de PAGE-XML codec'i (`from_page_xml` / `to_page_xml`) eklendi. PAGE poligonları
kelime/glif düzeyinde tam ayrıntı taşırken, Document modeli (M1 kararı, ADR-009)
Word/Token için `BBox` tutar. Bu nedenle iki yönlü round-trip'in garantisi açıkça
tanımlanmalıdır.

## Karar
1. **`Document → PAGE → Document` kayıpsızdır** — ancak belge, reader ve layout'un
   ürettiği **kanonik biçimde** olduğunda: tek sayfa; `page_id == image_ref`;
   `reading_index` değerleri okuma sırasında bitişik (0..n-1); boş `metadata`;
   ve kelimelerde alt-token (glif) ayrışması yok.
2. **`PAGE → Document → PAGE`** yönünde kelime/glif poligonları **bbox'a sadeleşir**
   (dikdörtgen). Bu bilinçli bir sadeleştirmedir.
3. Kimlikler: `doc_id`, PcGts `@pcGtsId` ile saklanır; `page_id` `imageFilename`'den
   türetilir (sayfanın kimliği görüntüsüdür).
4. Token/glif eşlemesi bu aşamada **uygulanmaz** (ertelenmiştir); tokenlar PAGE'e
   yazılmaz.

## Gerekçe
Word/Token'ı M1'de basit tutmak için `BBox` ile modelledik. Kelime poligonunu tam
korumak Word'e `Polygon` eklemeyi gerektirirdi. Kanonik-biçim round-trip'i, gerçek
eScriptorium/Kraken verisi için yeterli ve test edilebilir bir sözleşmedir.

## Sonuçlar
- Round-trip sınırı `test_page_xml_writer.py` içinde açıkça test edilir
  (kelime poligonu→bbox; token persist edilmez).
- İleride gerçek kelime poligonu veya glif/token gerekirse, modele `Polygon`/glif
  eklenmesi ayrı bir ADR ile yapılır ve bu ADR güncellenir/yerini alır.
