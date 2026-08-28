# RikaOCR Reproducibility Guide

## Scope

RikaOCR is a research prototype for Ottoman Rik'a historical documents.

The pipeline is intentionally separated into two stages:

1. Rik'a document image -> Kraken HTR/OCR -> Ottoman Arabic-script text
2. Ottoman Arabic-script text -> ByT5 transliteration -> Latin-letter transfer

The second stage is transliteration, not semantic translation into modern Turkish.

## Clone the repository

RikaOCR uses both Git submodules and Git LFS.

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

## Python environment

The main package targets Python 3.11.

```bash
python -m venv rikaenv
python -m pip install --upgrade pip
pip install -e ".[dev,data]"
```

The ByT5 experiments used a separate Transformers/PyTorch environment because the OCR and transliteration stacks were isolated during experimentation.

## Continuous integration

The repository CI checks Ruff, Black, Mypy, and Pytest.

Validated source snapshot:

- 203 tests passed
- 4 tests skipped

## eScriptorium

eScriptorium is included as a Git submodule pinned to:

```text
b28fba8df35d3d7dea44427be8429996145f67b8
```

The NVIDIA GPU Docker override is stored at:

```text
configs/escriptorium/docker-compose.override.yml
```

Copy it into the eScriptorium checkout when required.

PowerShell:

```powershell
Copy-Item configs/escriptorium/docker-compose.override.yml escriptorium/docker-compose.override.yml
```

Linux/macOS:

```bash
cp configs/escriptorium/docker-compose.override.yml escriptorium/docker-compose.override.yml
```

Local `.env` files are intentionally excluded from version control.

## Principal model artifacts

OpenITI initialization model:

```text
data/kraken_models/openiti/openiti_best_0.2866.safetensors
```

Primary held-out-document Rik'a model:

```text
data/kraken_models/riqa/rika_docsplit_best_0.7502_seed42.safetensors
```

Character-level Transformer baseline:

```text
data/transliteration/models/char_transformer_seed42/best_model.pt
```

ByT5 model:

```text
data/transliteration/models/byt5_small_seed42_bf16/best_model
```

Large binary artifacts are managed with Git LFS.

## Deterministic Rik'a document split

- Training: 67 documents / 1,201 lines
- Validation: 242 lines
- Held-out test: 9 unseen documents / 132 lines
- Train/validation to test document and line overlap: 0

## Validated research results

### Rik'a HTR held-out document test

- Character Accuracy: 77.23%
- CER: 22.77%
- WER: 72.47%

### Diagnostic OCR subset

Frozen 500 unique-word subset:

- Exact: 23.20%
- Exact + near-reading: 47.80%
- Unaligned/deleted: 6.20%
- Micro CER: 34.23%

### ByT5 transliteration

Held-out place-name test set, 1,409 examples:

- CER: 17.05%
- Exact Match: 39.96%

Frozen 500 unique single-word subset:

- CER: 14.65%
- Exact Match: 44.40% (222/500)

### Character-level Transformer baseline

- CER: 33.71%
- Exact Match: 24.56%

## Generalization limitation

The held-out benchmark results above are valid for the documented experimental split.

Two additional external Rik'a document tests were performed. The complete image-to-OCR-to-transliteration pipeline executed technically, but Kraken recognition on both external handwriting samples was unreliable, including on manually cropped single lines.

RikaOCR should therefore be described as a working research prototype, not as a production-grade recognizer that generalizes reliably to arbitrary Rik'a handwriting.

## ByT5 optimizer reconstruction

Two optimizer files were split losslessly into two Git LFS parts each.

Checkpoint 9926:

```bash
python scripts/reconstruct_byt5_optimizer.py data/transliteration/models/byt5_small_seed42_bf16/checkpoints/checkpoint-9926
```

Expected SHA-256:

```text
1d772973765dddfc488ab466ed2a8352ec19499c0e03578f48fafda7127a2316
```

Checkpoint 10635:

```bash
python scripts/reconstruct_byt5_optimizer.py data/transliteration/models/byt5_small_seed42_bf16/checkpoints/checkpoint-10635
```

Expected SHA-256:

```text
9a6f7bdbafd68b82a596cab5b5fb0a59de2263db83edc39e2401d2a59d374db3
```

The helper script verifies the reconstructed file against the expected digest.

## Data and licensing

RikaOCR source code is licensed under Apache-2.0. Third-party datasets and derived research material can have separate redistribution conditions. See `DATA_LICENSES.md`.

Raw material with unclear redistribution rights is intentionally not republished as unrestricted data.

## Citation

Machine-readable citation metadata is provided in `CITATION.cff`. A DOI can be added after an archival release is deposited in a DOI-granting repository such as Zenodo.
