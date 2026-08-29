# RikaOCR

[![CI](https://github.com/umute642-boop/RikaOCR/actions/workflows/ci.yml/badge.svg)](https://github.com/umute642-boop/RikaOCR/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](pyproject.toml)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.22151212-blue.svg)](https://doi.org/10.5281/zenodo.22151212)

**RikaOCR** is an open-source research prototype for the recognition of Ottoman **Rik'a** handwritten historical documents and for the subsequent **transliteration of recognized Ottoman Arabic-script text into Latin letters**.

The project is designed as a reproducible digital-history / historical-document research workflow rather than as a single black-box model.

> **Important:** the transliteration stage is **not semantic translation into modern Turkish**.

## Recommended archival release

- **Release:** `v0.10.3`
- **Zenodo DOI:** [`10.5281/zenodo.22151212`](https://doi.org/10.5281/zenodo.22151212)
- **License:** Apache-2.0 for RikaOCR source code
- **Status:** working research prototype; not a production-grade universal Rik'a OCR system

---

## Türkçe kısa özet

RikaOCR, Osmanlı Rik'a yazılı tarihî belgeleri için geliştirilen açık kaynaklı bir araştırma prototipidir.

Temel işlem zinciri:

**Rik'a belge görüntüsü → Kraken HTR/OCR → Osmanlıca Arap harfli metin → ByT5 transliterasyon → Latin harflerine aktarım**

ByT5 aşaması **modern Türkçeye anlamsal çeviri yapmaz**. Amaç, OCR tarafından üretilen Osmanlıca Arap harfli metni Latin harflerine aktarmaktır.

Kontrollü belge-ayrımlı testlerde model anlamlı sonuçlar vermiş olsa da, iki haricî Rik'a belgesinde yapılan ek deneyler mevcut OCR modelinin farklı el yazılarına güvenilir biçimde genellenemediğini göstermiştir. Bu nedenle proje bir **çalışan araştırma prototipi** olarak sunulmaktadır.

---

## 1. Research goals

RikaOCR was developed around four research goals:

1. build a reproducible software infrastructure for Ottoman historical-document research;
2. train and evaluate a Rik'a-specific handwriting-recognition model using document-separated evaluation;
3. model Ottoman Arabic-script → Latin-letter transliteration separately from OCR;
4. preserve models, splits, logs, experiments, code, provenance, and limitations in a citable public archive.

The separation between OCR and transliteration is methodological:

```text
Rik'a document image
        ↓
Kraken segmentation / HTR
        ↓
Ottoman Arabic-script text
        ↓
ByT5 transliteration
        ↓
Latin-letter transfer
```

A successful transliteration inference does not imply that the historical document was read correctly if the OCR input is wrong.

---

## 2. Project trajectory

RikaOCR evolved through several research stages.

### 2.1 Research software infrastructure

The first phase focused on building a stable historical-document software foundation, including:

- document- and line-level data models;
- image loading and preprocessing;
- annotation handling;
- PAGE XML support;
- region and line geometry;
- dataset construction;
- deterministic splitting;
- evaluation utilities;
- Kraken integration;
- transliteration interfaces;
- command-line workflows;
- output serialization;
- experiment tracking;
- automated testing;
- continuous integration.

This made later model experiments traceable to explicit data splits, model paths, evaluation procedures, and versioned source code.

### 2.2 Ottoman-script recognition initialization

A selected OpenITI / MAKHZAN subset was used to establish an Ottoman-script Kraken base model before Rik'a-specific training.

### 2.3 Rik'a-specific HTR

Rik'a-specific Kraken models were trained and compared, including scratch and fine-tuning experiments. The principal reported model uses a deterministic document-level split.

### 2.4 Transliteration

Two approaches were evaluated for Ottoman Arabic-script → Latin-letter transliteration:

- character-level Transformer baseline;
- ByT5-small fine-tuning.

### 2.5 End-to-end integration and external testing

The OCR and transliteration stages were technically integrated. Two additional external Rik'a documents were then tested to examine generalization beyond the controlled benchmark distribution.

---

## 3. Data used in the research

### 3.1 OpenITI / MAKHZAN selection

A selected subset of:

- **3,512 lines**

was prepared for the initial Ottoman-script Kraken stage.

Principal base model:

```text
data/kraken_models/openiti/openiti_best_0.2866.safetensors
```

### 3.2 Rik'a benchmark

The Rik'a benchmark used in the experiments contains:

- **85 pages**
- **1,575 annotated lines**

The principal deterministic document-level split is:

| Split | Documents | Lines |
|---|---:|---:|
| Training | 67 | 1,201 |
| Validation | — | 242 |
| Held-out test | 9 | 132 |

Leakage checks for the reported held-out test:

- train/validation ↔ test document overlap: **0**
- train/validation ↔ test line overlap: **0**

### 3.3 Transliteration data

The Ottoman Place Names Gazetteer material contained approximately:

- **44,838 raw pairs**

After filtering and preparation:

- **14,131 safe pairs**

were retained for the controlled transliteration experiments.

> Third-party data are not automatically treated as unrestricted RikaOCR-owned data. Provenance and redistribution notes are documented in [`DATA_LICENSES.md`](DATA_LICENSES.md).

---

## 4. Principal models

| Component | Role | Principal artifact |
|---|---|---|
| OpenITI Kraken model | Ottoman-script initialization | `data/kraken_models/openiti/openiti_best_0.2866.safetensors` |
| Rik'a Kraken model | Principal document-split HTR model | `data/kraken_models/riqa/rika_docsplit_best_0.7502_seed42.safetensors` |
| Character Transformer | Transliteration baseline | `data/transliteration/models/char_transformer_seed42/best_model.pt` |
| ByT5-small | Principal transliteration model | `data/transliteration/models/byt5_small_seed42_bf16/best_model` |

Additional experimental Kraken models are retained in:

```text
data/kraken_models/riqa/
```

Preserved Rik'a model artifacts include:

```text
rika_best_0.1615_seed42_lr001.safetensors
rika_docsplit_best_0.7502_seed42.safetensors
rika_scratch_best_0.8347_seed42.safetensors
```

The principal reported held-out model is `rika_docsplit_best_0.7502_seed42.safetensors`; the other files are retained as experimental artifacts rather than being substituted for the reported model.

and additional transliteration checkpoints are retained under:

```text
data/transliteration/models/
```

Large model artifacts are managed with **Git LFS**.

---

## 5. Experiment A — Held-out Rik'a document HTR

### Evaluation design

The principal Kraken Rik'a model was evaluated on:

- **9 unseen documents**
- **132 lines**

These documents were excluded from the corresponding training split.

### Results

| Metric | Result |
|---|---:|
| Character Accuracy | **77.23%** |
| CER | **22.77%** |
| WER | **72.47%** |

### Interpretation

These are valid metrics for the documented held-out split.

They do **not** establish that the model achieves the same performance on arbitrary Rik'a documents from different:

- archives;
- scribes;
- periods;
- scanning conditions;
- page layouts;
- handwriting styles.

The gap between character-level and word-level performance is especially important: useful character recognition does not automatically imply reliable word transcription.

---

## 6. Experiment B — Frozen 500-word OCR diagnostic subset

A frozen subset of **500 unique words** was used for a more diagnostic OCR analysis.

| Diagnostic measure | Result |
|---|---:|
| Exact | **23.20%** |
| Exact + near-reading | **47.80%** |
| Unaligned/deleted | **6.20%** |
| Micro CER | **34.23%** |

This analysis complements the document-level CER/WER by exposing:

- exact recognition;
- near readings;
- deletions;
- alignment failures;
- character-level error behavior.

---

## 7. Experiment C — Character-level Transformer baseline

A character-level Transformer was trained as the initial transliteration baseline.

Principal model:

```text
data/transliteration/models/char_transformer_seed42/best_model.pt
```

Held-out results:

| Metric | Result |
|---|---:|
| CER | **33.71%** |
| Exact Match | **24.56%** |

This baseline was used to assess whether ByT5 provided a meaningful improvement.

---

## 8. Experiment D — ByT5 held-out transliteration evaluation

A ByT5-small model was fine-tuned for Ottoman Arabic-script → Latin-letter transliteration.

Principal model:

```text
data/transliteration/models/byt5_small_seed42_bf16/best_model
```

Held-out evaluation:

- **1,409 examples**

| Metric | Result |
|---|---:|
| CER | **17.05%** |
| Exact Match | **39.96%** |

### Important metric note

`CER = 17.05%` must **not** be restated as “82.95% translation accuracy”.

CER and Exact Match measure different aspects of sequence prediction, and the task is transliteration rather than semantic translation.

---

## 9. Experiment E — Frozen 500-word ByT5 diagnostic subset

A frozen **500 unique single-word** subset was evaluated separately.

| Metric | Result |
|---|---:|
| CER | **14.65%** |
| Exact Match | **44.40%** |
| Exact predictions | **222 / 500** |

This provides a controlled view of single-word transliteration performance.

---

## 10. Transliteration model comparison

| Model | CER | Exact Match |
|---|---:|---:|
| Character-level Transformer | **33.71%** | **24.56%** |
| ByT5-small | **17.05%** | **39.96%** |

Under the documented experimental setup, ByT5 substantially outperformed the character-level baseline.

This does **not** mean that ByT5 can repair arbitrary OCR corruption. If the recognition stage produces the wrong Ottoman-script sequence, the transliteration stage is operating on the wrong source text.

---

## 11. Experiment F — End-to-end integration smoke test

The complete technical chain was connected successfully:

```text
image
  ↓
Kraken HTR/OCR
  ↓
Ottoman Arabic-script OCR output
  ↓
ByT5
  ↓
Latin-letter output
```

This demonstrates software integration, not end-to-end palaeographic accuracy.

The OCR stage remains the critical bottleneck when the target handwriting differs from the controlled training distribution.

---

## 12. Experiment G — External Rik'a document test 01

A Rik'a document outside the principal benchmark material was tested qualitatively.

### Full-page result

Full-page segmentation produced many unreliable text units and the OCR output was largely unusable.

### Full-page segmentation

The full-page Kraken run produced **49 segmentation units**, substantially more than the useful visual line structure.

### Segmentation-free line tests

To determine whether the problem was caused only by segmentation, manually selected line crops were tested with segmentation disabled.

Crop 1:

```text
coordinates: (300, 210, 823, 270)
size: 523 × 60
OCR: نرا ه رر الردارهت
```

Crop 2:

```text
coordinates: (250, 232, 823, 275)
size: 573 × 43
OCR: ندالا هیری رم شاراوا هداعك هدر
```

### Interpretation

Recognition remained unreliable even on manually selected single-line crops.

Therefore the failure cannot be attributed only to full-page segmentation.

The experiment indicates weak generalization of the current Rik'a model to this external handwriting/domain.

---

## 13. Experiment H — External Rik'a document test 02

A second external Rik'a document was tested.

### Full-page segmentation

The full-page Kraken run produced **35 segmentation units** for a document whose visual structure contained only a small number of main handwritten lines, indicating substantial over-segmentation.

### Deskewed single-line test

The page was rotated by approximately **4°**, then a line was cropped at:

```text
coordinates: (10, 74, 600, 108)
size: 590 × 34
```

The crop was passed directly to Kraken with segmentation disabled.

Raw OCR:

```text
ما وعلعس یرددل م ایعا یلا عام تادض انماطرایلعم هم اعان دضوا
```

The OCR string was then passed to the separate ByT5 environment as a technical pipeline test.

Recorded experimental environment:

```text
Transformers: 4.57.1
PyTorch: 2.10.0+cu128
```

ByT5 output:

```text
Ma ve Alas Yerddel merkez
```

### Interpretation

This is **not** considered a successful reading or successful document transliteration.

The source OCR was already unreliable. The ByT5 output only demonstrates that the second stage technically accepted the OCR string and generated a Latin-letter sequence.

---

## 14. What the external tests change about the project claim

The controlled held-out benchmark and the external tests answer different questions.

The held-out benchmark shows that the model learned useful recognition behavior within the documented benchmark distribution.

The external tests show that the current model does **not yet generalize reliably to arbitrary external Rik'a handwriting**.

Accordingly, RikaOCR should be described as:

> **a working research prototype**

and not as:

> **a production-grade universal Ottoman Rik'a OCR system**

The external failures are preserved because they are part of the research result, not something to hide.

---

## 15. Current validated results at a glance

### Rik'a HTR

| Evaluation | Metric | Result |
|---|---|---:|
| 9 unseen documents / 132 lines | Character Accuracy | **77.23%** |
| 9 unseen documents / 132 lines | CER | **22.77%** |
| 9 unseen documents / 132 lines | WER | **72.47%** |

### OCR diagnostic subset

| Evaluation | Metric | Result |
|---|---|---:|
| Frozen 500 unique words | Exact | **23.20%** |
| Frozen 500 unique words | Exact + near-reading | **47.80%** |
| Frozen 500 unique words | Unaligned/deleted | **6.20%** |
| Frozen 500 unique words | Micro CER | **34.23%** |

### Transliteration

| Model / evaluation | CER | Exact Match |
|---|---:|---:|
| Character Transformer baseline | **33.71%** | **24.56%** |
| ByT5 — 1,409 held-out examples | **17.05%** | **39.96%** |
| ByT5 — frozen 500-word subset | **14.65%** | **44.40%** |

### Software validation

- **203 tests passed**
- **4 tests skipped**
- Ruff: passed
- Black: passed
- Mypy: passed
- GitHub Actions CI: passing

---

## 16. Known limitations

Current limitations include:

- weak generalization to some external Rik'a handwriting;
- sensitivity to page layout and segmentation;
- relatively high WER despite better character-level performance;
- propagation of OCR errors into transliteration;
- limited writer-independent external validation;
- transliteration experiments being more controlled than unrestricted long-document processing;
- possible ByT5 repetition on long OCR sequences;
- word-by-word ByT5 mode reducing some repetition in testing but not constituting a validated general sentence-level solution;
- domain dependence on the handwriting and historical material represented in training data.

These limitations define the next research questions.

---

## 17. Reproducibility

Detailed reproduction instructions are available in:

[`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md)

The repository records:

- deterministic data splits;
- a detailed Rik'a experiment journal (`docs/riqa-training-experiments.md`);
- model paths;
- experiment outputs;
- research logs;
- software tests;
- Git LFS configuration;
- eScriptorium version;
- GPU Docker configuration;
- optimizer reconstruction hashes;
- data provenance and licensing notes.

---

## 18. Clone the complete repository

RikaOCR uses both **Git LFS** and a **Git submodule**.

```bash
git lfs install
git clone --recurse-submodules https://github.com/umute642-boop/RikaOCR.git
cd RikaOCR
git lfs pull
```

If the repository was cloned without submodules:

```bash
git submodule update --init --recursive
```

---

## 19. Python environment

The main package targets **Python 3.11**.

Create an environment:

```bash
python -m venv rikaenv
```

Then install the project:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev,data]"
```

Run the validated software checks:

```bash
python -m ruff check .
python -m black --check .
python -m mypy src
python -m pytest
```

### ByT5 environment

The ByT5 experiments used a separate Transformers/PyTorch environment because the OCR and transliteration software stacks had dependency constraints during experimentation.

The separation is intentional and is described in the reproducibility documentation.

---

## 20. eScriptorium integration

eScriptorium is included as a Git submodule.

Pinned commit:

```text
b28fba8df35d3d7dea44427be8429996145f67b8
```

NVIDIA GPU Docker override:

```text
configs/escriptorium/docker-compose.override.yml
```

To use the preserved GPU override:

### PowerShell

```powershell
Copy-Item configs/escriptorium/docker-compose.override.yml escriptorium/docker-compose.override.yml
```

### Linux/macOS

```bash
cp configs/escriptorium/docker-compose.override.yml escriptorium/docker-compose.override.yml
```

Local `.env` files are intentionally not tracked.

---

## 21. Large ByT5 optimizer reconstruction

Two optimizer states were too large for convenient single-file hosting and were therefore split losslessly into Git LFS parts.

### checkpoint-9926

Expected SHA-256:

```text
1d772973765dddfc488ab466ed2a8352ec19499c0e03578f48fafda7127a2316
```

Reconstruct:

```bash
python scripts/reconstruct_byt5_optimizer.py data/transliteration/models/byt5_small_seed42_bf16/checkpoints/checkpoint-9926
```

### checkpoint-10635

Expected SHA-256:

```text
9a6f7bdbafd68b82a596cab5b5fb0a59de2263db83edc39e2401d2a59d374db3
```

Reconstruct:

```bash
python scripts/reconstruct_byt5_optimizer.py data/transliteration/models/byt5_small_seed42_bf16/checkpoints/checkpoint-10635
```

The helper verifies the reconstructed SHA-256 digest.

---

## 22. Repository structure

A simplified overview:

```text
RikaOCR/
├── src/rikaocr/                         # active Python package
├── tests/                               # automated tests
├── scripts/                             # experiment / utility scripts
├── docs/                                # reproducibility and research documentation
├── data/
│   ├── kraken_models/                   # Kraken model artifacts
│   ├── kraken_work/                     # selected reproducibility artifacts
│   └── transliteration/
│       ├── models/                      # ByT5 and baseline models
│       ├── splits/                      # transliteration splits
│       └── integration/                 # integration artifacts
├── configs/escriptorium/                # reproducible GPU override
├── archive/source_backups/              # preserved historical source backups
├── escriptorium/                        # Git submodule
├── CITATION.cff
├── DATA_LICENSES.md
├── LICENSE
├── README.md
└── pyproject.toml
```

Some raw third-party datasets are intentionally excluded from the public repository when redistribution rights are unclear.

---

## 23. Data provenance and licensing

RikaOCR source code is licensed under the **Apache License 2.0**.

Historical source datasets may have different rights and redistribution conditions.

See:

[`DATA_LICENSES.md`](DATA_LICENSES.md)

The repository intentionally distinguishes between:

1. RikaOCR source code;
2. trained models and RikaOCR-generated artifacts;
3. third-party source datasets;
4. derived research metadata.

Open reproducibility does not mean claiming unrestricted ownership of third-party historical collections.

---

## 24. Research integrity and evaluation policy

The project follows several evaluation principles:

- held-out documents should remain isolated from training;
- external qualitative samples should not be added to training before evaluation;
- OCR and transliteration metrics should be reported separately;
- failed external tests should be preserved and discussed;
- CER should not be converted into an invented “accuracy” percentage;
- technical pipeline execution should not be confused with successful historical reading;
- model limitations should be part of the published research record.

---

## 25. Release history

### v0.10.1

Earlier project state before final archival/reproducibility preparation.

### v0.10.2

Archival research preparation including:

- citation metadata;
- reproducibility documentation;
- CI fixes;
- model preservation;
- eScriptorium GPU configuration;
- Git LFS archival work.

### v0.10.3 — recommended archival release

Prepared after the GitHub–Zenodo archival connection was active.

No new model training was performed merely to create this release.

The purpose of `v0.10.3` is to provide a stable citable research snapshot with synchronized:

- source version;
- citation metadata;
- research documentation;
- CI status;
- model archive;
- data-rights documentation;
- Zenodo DOI registration.

**DOI:** [`10.5281/zenodo.22151212`](https://doi.org/10.5281/zenodo.22151212)

---

## 26. Future work

Priority directions include:

- expanding Rik'a Ground Truth;
- increasing writer diversity;
- increasing archive and document-type diversity;
- larger external test sets;
- writer-independent evaluation;
- improved page and line segmentation;
- handwriting-specific augmentation;
- confidence-aware recognition;
- systematic palaeographic error analysis;
- comparison with additional HTR architectures;
- improved recognition of rare Ottoman character sequences;
- error-aware OCR/transliteration coupling;
- sentence-level transliteration evaluation;
- document-level transliteration evaluation.

The most important experimental rule remains:

> external test material should stay isolated from training until evaluation is complete.

---

## 27. Citation

Machine-readable citation metadata is provided in:

[`CITATION.cff`](CITATION.cff)

Recommended archival record:

**RikaOCR v0.10.3**
**DOI:** [`10.5281/zenodo.22151212`](https://doi.org/10.5281/zenodo.22151212)

When citing the software, prefer the metadata provided by `CITATION.cff` or the Zenodo record.

---

## 28. Author

**Umut Çetinbaş**
History MA Student
ORCID: [`0009-0006-6769-0052`](https://orcid.org/0009-0006-6769-0052)
Mail: Umute642@gmail.com
---

## 29. License

RikaOCR source code is distributed under the **Apache License 2.0**.

See [`LICENSE`](LICENSE).

Third-party data licensing and redistribution notes are documented separately in [`DATA_LICENSES.md`](DATA_LICENSES.md).

---

## 30. Project status

RikaOCR currently demonstrates that:

1. a Rik'a-specific Kraken recognizer can be trained and evaluated with a document-separated benchmark;
2. controlled Ottoman Arabic-script → Latin-letter transliteration can be modeled effectively with ByT5;
3. the OCR and transliteration stages can be integrated technically;
4. same-distribution held-out performance can differ substantially from external-document behavior;
5. reproducible software infrastructure is necessary to document those distinctions correctly.

The project is therefore best understood as a **reproducible digital-history research prototype and experimental baseline** for future Ottoman Rik'a HTR work.
