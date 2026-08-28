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

## Controlled OpenITI → Rik'a transfer experiment (document-level split)

Same deterministic document-level split and training settings as the final scratch experiment were used:
- Train: 67 documents / 1201 lines
- Validation: 9 documents / 242 lines
- Test: 9 documents / 132 lines
- Seed: 42
- Learning rate: 0.001
- Batch size: 4
- Base direction: R
- Unicode normalization: NFC
- Early stopping: lag 10

### Scratch baseline
Model: `rika_docsplit_best_0.7502_seed42.safetensors`
- Best validation character accuracy: 75.02%
- Held-out document-level test character accuracy: 77.23%
- CER: 22.77%
- RikaOCR aggregate WER: 72.47%

### Transfer learning: OpenITI base + `--resize union`
OpenITI base model: `openiti_best_0.2866.safetensors`
- Best validation character accuracy: 1.08%
- Kraken held-out test character accuracy: 1.06%
- RikaOCR CER: 98.94%
- RikaOCR character accuracy: 1.06%
- RikaOCR WER: 100%

This configuration clearly underperformed the scratch baseline.

### Transfer learning: OpenITI base + `--resize new`
- Best validation character accuracy: 16.83%
- Kraken `ketos test` character accuracy: 3.57%
- Kraken word accuracy: 0%
- RikaOCR/manual inference character accuracy: 15.48%
- RikaOCR/manual CER: 84.52%
- RikaOCR/manual WER: 100%

A discrepancy remains between Kraken `ketos test` (3.57%) and direct model/RikaOCR inference (15.48%) for this weak transfer model. Checks performed so far ruled out:
- image mode conversion (`L`)
- crop/extract_polygons differences
- CPU vs CUDA inference
- train/eval mode
- ground-truth normalization as a meaningful source of the discrepancy
- decoder identity / basic forward path differences

Therefore the `--resize new` held-out test accuracy should not yet be treated as a definitive paper metric. Both evaluation paths nevertheless show that transfer learning from the current OpenITI Naskh model performs far below the Rik'a scratch model.

### Current methodological conclusion
Under the controlled document-level protocol used here, training the Rik'a OCR model from scratch is substantially more successful than initializing from the available OpenITI-MAKHZAN Naskh model. The transfer-learning result is retained as a negative experimental finding rather than selected as the final OCR model.


## Controlled OpenITI → Rik'a transfer experiment

The same deterministic document-level split was used for the scratch and transfer-learning experiments:
- Train: 67 documents / 1201 lines
- Validation: 9 documents / 242 lines
- Test: 9 documents / 132 lines
- Seed: 42
- Learning rate: 0.001
- Batch size: 4
- Base direction: R
- Unicode normalization: NFC

### Scratch baseline
- Best validation character accuracy: 75.02%
- Held-out document-level test character accuracy: 77.23%
- CER: 22.77%
- RikaOCR aggregate WER: 72.47%

### OpenITI transfer — resize union
- Best validation character accuracy: 1.08%
- Held-out test character accuracy: 1.06%
- RikaOCR CER: 98.94%
- RikaOCR WER: 100%

### OpenITI transfer — resize new
- Best validation character accuracy: 16.83%
- Kraken ketos test character accuracy: 3.57%
- Direct RikaOCR/manual inference character accuracy: 15.48%
- Direct CER: 84.52%
- WER: 100%

A discrepancy remains between Kraken ketos test (3.57%) and direct inference (15.48%) for the resize-new transfer model. Image mode, crop/extract_polygons behavior, CPU/CUDA execution, train/eval mode, ground-truth normalization, and the basic forward/decoder path were checked and did not explain the discrepancy.

Therefore the resize-new test accuracy is not yet treated as a definitive paper metric. Both evaluation paths nevertheless show that the OpenITI-MAKHZAN Naskh transfer model performs substantially below the Rik'a scratch model.

### Methodological conclusion
Under the controlled document-level protocol, training the Rik'a OCR model from scratch substantially outperformed initialization from the available OpenITI-MAKHZAN Naskh model. Transfer learning is retained as a negative experimental result rather than selected as the final OCR model.


## External Rik'a document sanity check

- External document: 0.jpg
- This document was not part of the 1575-line Rik'a dataset.
- Full-page OCR produced poor recognition.
- Cropped-region OCR also remained poor.
- A manually cropped single line was tested with segmentation disabled.
- Recognition still did not match the manuscript line reliably.
- Conclusion: the current model performs substantially worse on this out-of-domain archival Rik'a document.
- This external document will NOT be added to the training set and is retained as an independent qualitative generalization example.


## Transliteration baseline

- Dataset source: Ottoman place-name gazetteer
- Raw records: 44,838
- Clean unambiguous Ottoman -> Latin pairs: 14,131
- Split strategy: grouped by Latin target name to prevent spelling variants of the same place name from crossing splits
- Seed: 42
- Train: 11,330 pairs
- Validation: 1,392 pairs
- Test: 1,409 pairs
- Target-group overlap between train/validation/test: 0
- Model: character-level Transformer
- PyTorch: 2.10.0+cu128
- GPU: NVIDIA GeForce RTX 4060 Laptop GPU
- Best validation CER: 34.82%
- Best validation exact match: 22.70%
- Final held-out test CER: 33.71%
- Final held-out test exact match: 24.56%
- Model: data/transliteration/models/char_transformer_seed42/best_model.pt
- Final test results: data/transliteration/models/char_transformer_seed42/test_results.json
- Inference script: scripts/transliteration/infer_char_transformer.py
- Example sanity check: آب كارون -> Abkran
- Interpretation: the transliteration component is a functional baseline, but accuracy remains limited. The training resource is a place-name gazetteer rather than a general Ottoman Turkish sentence-level transliteration corpus, so the model should not be presented as a gene@'

## Transliteration baseline

- Dataset source: Ottoman place-name gazetteer
- Raw records: 44,838
- Clean unambiguous Ottoman -> Latin pairs: 14,131
- Split strategy: grouped by Latin target name to prevent spelling variants of the same place name from crossing splits
- Seed: 42
- Train: 11,330 pairs
- Validation: 1,392 pairs
- Test: 1,409 pairs
- Target-group overlap between train/validation/test: 0
- Model: character-level Transformer
- PyTorch: 2.10.0+cu128
- GPU: NVIDIA GeForce RTX 4060 Laptop GPU
- Best validation CER: 34.82%
- Best validation exact match: 22.70%
- Final held-out test CER: 33.71%
- Final held-out test exact match: 24.56%
- Model: data/transliteration/models/char_transformer_seed42/best_model.pt
- Final test results: data/transliteration/models/char_transformer_seed42/test_results.json
- Inference script: scripts/transliteration/infer_char_transformer.py
- Example sanity check: آب كارون -> Abkran
- Interpretation: the transliteration component is a functional baseline, but accuracy remains limited. The training resource is a place-name gazetteer rather than a general Ottoman Turkish sentence-level transliteration corpus, so the model should not be presented as a general-purpose Ottoman transliterator.


## Transliteration baseline

- Dataset source: Ottoman place-name gazetteer
- Raw records: 44,838
- Clean unambiguous Ottoman -> Latin pairs: 14,131
- Split strategy: grouped by Latin target name to prevent spelling variants of the same place name from crossing splits
- Seed: 42
- Train: 11,330 pairs
- Validation: 1,392 pairs
- Test: 1,409 pairs
- Target-group overlap between train/validation/test: 0
- Model: character-level Transformer
- PyTorch: 2.10.0+cu128
- GPU: NVIDIA GeForce RTX 4060 Laptop GPU
- Best validation CER: 34.82%
- Best validation exact match: 22.70%
- Final held-out test CER: 33.71%
- Final held-out test exact match: 24.56%
- Model: data/transliteration/models/char_transformer_seed42/best_model.pt
- Final test results: data/transliteration/models/char_transformer_seed42/test_results.json
- Inference script: scripts/transliteration/infer_char_transformer.py
- Example sanity check: آب كارون -> Abkran
- Interpretation: the transliteration component is a functional baseline, but accuracy remains limited. The training resource is a place-name gazetteer rather than a general Ottoman Turkish sentence-level transliteration corpus, so the model should not be presented as a general-purpose Ottoman transliterator.


## ByT5 improvement checkpoint - 27 Aug 2026

- Existing transliteration baseline completed.
- Held-out test CER: 33.71%
- Held-out test exact match: 24.56%.
- Stronger ByT5 experiment started but training has NOT started yet.
- Isolated environment created inside container: /tmp/byt5env
- Transformers: 4.57.1
- PyTorch: 2.10.0+cu128
- GPU: NVIDIA GeForce RTX 4060 Laptop GPU
- GPU VRAM: 8188 MiB (~8 GB)
- google/byt5-small successfully downloaded and loaded.
- ByT5-small parameters: 299,637,760
- Tokenizer size: 384
- Kraken environment verified before shutdown:
  Kraken 7.0.3
  safetensors 0.7.0
- Docker Desktop later returned a 500 Internal Server Error and the Docker Engine was shut down.
- Next session:
  1. Start Docker Desktop.
  2. Verify escriptorium-celery-main-1 is available.
  3. Check whether /tmp/byt5env and cached google/byt5-small remain.
  4. Recreate them only if necessary.
  5. Prepare 8-GB-VRAM-safe ByT5 fine-tuning with FP16, gradient checkpointing and gradient accumulation.
  6. Tune only on validation; do not use the held-out test set for model selection.
  7. Compare ByT5 against the character-Transformer baseline.
  8. OpenAI/ChatGPT integration will be considered only after ByT5 evaluation.


## ByT5 transliteration final experiment - 28 Aug 2026

- Base model: google/byt5-small
- Parameters: 299,637,760
- Seed: 42
- Dataset: same controlled Ottoman place-name split used for the character-Transformer baseline
- Train: 11,330 pairs
- Validation: 1,392 pairs
- Held-out test: 1,409 pairs
- Target-group overlap between train/validation/test: 0
- Input/output normalization: NFC
- Maximum source length: 192 ByT5 tokens
- Maximum target length: 160 ByT5 tokens
- Training precision: BF16
- FP16 was tested initially but manually stopped because of numerical instability (extreme loss values and NaN gradient norms); FP16 results were not used.
- Gradient checkpointing: enabled
- Train batch size: 1
- Evaluation batch size: 2
- Gradient accumulation steps: 16
- Learning rate: 5e-5
- Maximum epochs: 15
- Early-stopping patience: 3
- Model-selection metric: validation CER
- Held-out test set was not used for model selection or tuning.
- Best checkpoint: checkpoint-10635 (epoch 15)
- Best validation CER: 17.07%
- Validation exact match: 39.22%
- Final held-out test CER: 17.05%
- Final held-out test exact match: 39.96%
- Character-Transformer baseline held-out CER: 33.71%
- Character-Transformer baseline held-out exact match: 24.56%
- ByT5 substantially outperformed the character-Transformer baseline on the unchanged held-out test split.
- Model: data/transliteration/models/byt5_small_seed42_bf16/best_model
- Results: data/transliteration/models/byt5_small_seed42_bf16/results.json
- Training log: data/transliteration/models/byt5_small_seed42_bf16/training.log
- Inference script: scripts/transliteration/infer_byt5.py
- Inference sanity check: آباران -> Abaran
- Interpretation: this experiment evaluates Ottoman Arabic-script to Latin-script transliteration of place names. It must not be interpreted as sentence-level Ottoman Turkish translation performance or as end-to-end Rik'a document accuracy.

