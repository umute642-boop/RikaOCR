# Architecture Decision Records (ADR)

Bu dizin, RikaOCR'ın bağlayıcı mimari kararlarını içerir. Mimari yalnızca yeni
bir ADR ile değişir; mevcut bir karar değiştirilecekse eski ADR "Yerini aldı
(ADR-YYY)" olarak işaretlenir ve yeni bir ADR yazılır.

Biçim: her ADR `_template.md` yapısını izler (Bağlam, Karar, Gerekçe, Sonuçlar).
Kaynak gerekçeler için bkz. `../architecture.md` (TDD v0.2).

| ADR | Karar | Statü |
|-----|-------|-------|
| [001](ADR-001-line-level-htr.md) | Ana eksen: satır düzeyi HTR | Kabul |
| [002](ADR-002-framework-pytorch.md) | Çatı: PyTorch + HuggingFace | Kabul |
| [003](ADR-003-gt-encoding.md) | GT kodlama: Arap harfli Unicode; translit ayrı; harekeler hariç | Kabul |
| [004](ADR-004-annotation-format.md) | Annotation: PAGE-XML kaynak, ALTO export, JSONL türetilmiş | Kabul |
| [005](ADR-005-annotation-tool.md) | Etiketleme aracı: eScriptorium | Kabul |
| [006](ADR-006-versioning.md) | Versiyonlama: Git + hash manifest → DVC | Kabul |
| [007](ADR-007-transfer-learning.md) | Sıfırdan eğitim yerine transfer öğrenme | Kabul |
| [008](ADR-008-document-model.md) | Belge-merkezli mimari: Document alan modeli | Kabul |
| [009](ADR-009-alignment.md) | Koordinat↔metin hizalaması birinci sınıf çıktı | Kabul |
| [010](ADR-010-script-neutral-core.md) | Yazı-nötr çekirdek + script profile | Kabul |
| [011](ADR-011-search-port.md) | Arama bir port; motor yazılmaz, adaptörle sarılır | Kabul |
| [012](ADR-012-oss-governance.md) | Açık kaynak yönetişimi tasarımın parçası | Kabul |
| [013](ADR-013-code-license.md) | Kod lisansı: Apache-2.0 | Kabul |
| [014](ADR-014-data-license.md) | Veri lisansı | KARAR BEKLİYOR |
| [015](ADR-015-f1-baseline.md) | F1 tabanı: önce Kraken/Calamari, kendi CRNN sonra | Kabul |
| [016](ADR-016-experiment-tracking.md) | Deney takibi: F1'de MLflow | Kabul |
| [017](ADR-017-page-round-trip.md) | PAGE-XML round-trip garantisi (Document→PAGE→Document kayıpsız) | Kabul |
| [018](ADR-018-dataset-and-image-deps.md) | Veri seti yapısı + görüntü bağımlılıkları (Pillow/NumPy `[data]`, OpenCV ertelenmiş) | Kabul |
