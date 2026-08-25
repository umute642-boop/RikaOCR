# Rik'a OCR Eğitim Deneyleri

Tarih: 25 Ağustos 2026

## Veri

- Rik'a eğitim kümesi: 1575 satır görüntüsü ve Osmanlıca ground-truth.
- Kraken 7.0.3
- GPU: NVIDIA GeForce RTX 4060 Laptop GPU
- Normalizasyon: NFC
- Temel yön: R
- Batch size: 4
- Ana deneylerde seed: 42

## OpenITI -> Rik'a Fine-tuning

OpenITI taban modelinden Rik'a verisine fine-tuning:

- Learning rate: 0.001
- Early stopping: min 5 epoch, lag 10
- En iyi Kraken val_accuracy: 0.1615
- En iyi aşama: stage 15

Bu deney, OpenITI/Nesih taban modelinin Rik'a alanına aktarımının sınırlı kaldığını göstermiştir.

## Rik'a Sıfırdan Eğitim

Rik'a verisiyle rastgele başlangıçtan eğitim:

- Learning rate: 0.001
- Early stopping: min 5 epoch, lag 10
- En iyi Kraken val_accuracy: 0.8347
- En iyi aşama: stage 23
- Stage 23 val_word_accuracy: yaklaşık 0.418
- Eğitim stage 33'te early stopping ile sona ermiştir.

Seçilen deneysel model:

data/kraken_models/riqa/rika_scratch_best_0.8347_seed42.safetensors

Model dosyası Git deposuna eklenmemekte, yalnızca yerel olarak saklanmaktadır.

## Öğrenme Oranı Bulgusu

0.0001 learning rate ile Rik'a fine-tuning etkisiz kalmıştır.
0.001 learning rate belirgin biçimde daha iyi öğrenme sağlamıştır.

## Bağımsız Test Verisi Kontrolü

`data/benchmark/riqa` içindeki 1575 görüntünün tamamı eğitim görüntüleriyle SHA-256 düzeyinde aynıdır:

- Eğitim görüntüsü: 1575
- Benchmark görüntüsü: 1575
- Ortak SHA-256: 1575

Ayrıca `RiqaTestset.zip` içindeki 1575 görüntünün de tamamı eğitim kümesiyle aynıdır:

- Test adayı: 1575
- Eğitim: 1575
- Ortak SHA-256: 1575

Bu nedenle bu iki kaynak bağımsız CER/WER testi olarak kullanılamaz.

## Final Eğitim Denemesi

1575 örneğin tamamını `-p 1.0` ile eğitime verme denemesi Kraken tarafından reddedilmiştir; çünkü Kraken eğitim sırasında validation verisi de beklemektedir.

Bu nedenle mevcut durumda seçilen model, gerçek train/validation ayrımıyla eğitilen `rika_scratch_best_0.8347_seed42.safetensors` modelidir.

## Akademik Değerlendirme Notu

0.8347 değeri nihai OCR başarısı değildir; Kraken iç validation metriğidir.

Nihai başarı iddiası için modelin eğitim sırasında hiç görmediği bağımsız Rik'a belgelerinde CER ve WER hesaplanacaktır.

## Belge Bazlı Nihai Değerlendirme

Belge kimlikleri kullanılarak 85 belge deterministik biçimde ayrılmıştır:

- Train: 67 belge / 1201 satır
- Validation: 9 belge / 242 satır
- Test: 9 belge / 132 satır
- Aynı belge birden fazla bölüme girmemektedir.

Belge-bazlı sıfırdan Kraken eğitiminin en iyi validation sonucu:

- En iyi stage: 58
- Kraken val_accuracy: 0.7502
- Model: rika_docsplit_best_0.7502_seed42.safetensors

Eğitimde hiç görülmeyen 9 test belgesi / 132 satır üzerinde Kraken test raporu:

- Toplam karakter: 13,714
- Karakter hatası: 3,122
- Character Accuracy: 77.23%
- CER: 22.77%
- Word Accuracy: 27.66%
- Insertions: 487
- Deletions: 1,232
- Substitutions: 1,403

Not: Nihai WER değeri ayrıca doğrudan Levenshtein tabanlı değerlendirme ile hesaplanıp doğrulanacaktır; Word Accuracy değerinden otomatik olarak WER türetilmiş kabul edilmemektedir.

### RikaOCR direct held-out evaluation
- Held-out test: 9 documents / 132 lines
- CER: 0.2276903 (22.77%)
- Character accuracy: 77.23%
- WER: 0.7247142 (72.47%)
- RikaOCR character accuracy agrees with Kraken ketos test (77.23%).
- WER was computed directly with RikaOCR aggregate_wer; it was not inferred from Kraken Word Accuracy.
