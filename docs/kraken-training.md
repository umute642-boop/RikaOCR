# Kraken ile Rik'a Modeli Eğitimi (WSL2 + CUDA)

Bu belge, RikaOCR'ın F1 tabanı için Kraken motoruyla satır düzeyi bir HTR
modelinin elle nasıl eğitileceğini açıklar (bkz. ADR-015, ADR-019). Eğitim
geliştirme makinesinin Windows tarafında değil, **WSL2 (Ubuntu) + CUDA**
ortamında yapılır; RikaOCR paketi yalnızca veriyi Kraken'in beklediği biçime
hazırlar ve ortaya çıkan modeli `KrakenRecognizer` ile sarar.

## 1. Sorumluluk sınırı

| Aşama | Araç | Nerede |
|-------|------|--------|
| Veri seti üretimi, satır kırpma, manifest | RikaOCR (`[data]`) | Windows/Linux |
| `.gt.txt` sidecar export | RikaOCR `training.kraken_export` | Windows/Linux |
| Model eğitimi (`ketos train`) | Kraken (`[train]`) | **WSL2 + CUDA** |
| Çıkarım (model sarmalama) | RikaOCR `KrakenRecognizer` | Linux/WSL2 |

RikaOCR çekirdeği ve testleri Kraken'e bağımlı değildir; Kraken yalnızca
`recognition.kraken_adapter` içinde **tembel (lazy)** içe aktarılır.

## 2. WSL2 + CUDA ortamı

```bash
# Windows PowerShell (yönetici): WSL2 + Ubuntu
wsl --install -d Ubuntu
# NVIDIA sürücüsü Windows tarafında kurulu olmalı; WSL2 CUDA'yı otomatik görür.

# Ubuntu (WSL2) içinde:
python3 -m venv ~/kraken-env
source ~/kraken-env/bin/activate
pip install "kraken>=5"
nvidia-smi           # GPU görünüyor mu?
ketos --version
```

> Not: Kraken yalnızca Linux'ta resmî olarak desteklenir. Windows'ta doğrudan
> kurmak yerine WSL2 kullanın.

## 3. Eğitim verisini hazırlama (RikaOCR tarafı)

Satır görüntüleri ve manifest M4'te üretilir. Kraken için her satır
görüntüsünün yanına aynı adlı bir `.gt.txt` dosyası gerekir:

```python
from rikaocr.data.dataset.sample import read_line_manifest
from rikaocr.data.dataset.splitting import Split
from rikaocr.training.kraken_export import export_gt_sidecars

samples = read_line_manifest("data/processed/lines.jsonl")
export_gt_sidecars(samples, "data/processed", split=Split.TRAIN)
export_gt_sidecars(samples, "data/processed", split=Split.VAL)
```

Sonuç:

```
data/processed/train/lines/rika_0007.png
data/processed/train/lines/rika_0007.gt.txt   # "بسم الله ..."
```

Metin kodlaması ADR-003'e uyar: Arap harfli Unicode, harekeler hariç.

## 4. Model eğitimi (`ketos train`)

```bash
# Eğitim ve doğrulama satırlarını ayrı listelerle veriyoruz.
ketos train \
  -o models/rika_f1 \
  --device cuda:0 \
  --augment \
  -f path \
  data/processed/train/lines/*.png

# Çıktı: models/rika_f1_best.mlmodel
```

Değerlendirme (Kraken kendi CER'ini raporlar; RikaOCR'ın `evaluation` modülü
bağımsız bir CER/WER ölçümü sağlar):

```bash
ketos test -m models/rika_f1_best.mlmodel data/processed/val/lines/*.png
```

## 5. Modeli RikaOCR ile kullanma

```python
from PIL import Image
from rikaocr.recognition.kraken_adapter import KrakenRecognizer

recognizer = KrakenRecognizer(model_path="models/rika_f1_best.mlmodel")
result = recognizer.recognize(Image.open("line.png"))
print(result.text, result.confidence)
```

Belge düzeyinde tanıma için `recognition.base.recognize_document`, bağımsız
CER/WER ölçümü için `evaluation.evaluate.evaluate` kullanılır.

## 6. Yeniden üretilebilirlik

Eğitim komutu, kullanılan veri sürümü (hash manifest, ADR-006) ve model çıktısı
MLflow ile kaydedilir (ADR-016). Eğitim ortamı (Kraken sürümü, CUDA, GPU) bu
belgeyle birlikte raporlanır.
