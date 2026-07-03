# RikaOCR

RikaOCR, **Rik'a hattıyla yazılmış Osmanlı arşiv (BOA) belgeleri** için
geliştirilen açık kaynaklı bir **HTR (Handwritten Text Recognition)** / belge
anlama platformudur. Mimari, ileride Divani, Siyakat ve Talik gibi diğer Osmanlı
yazı türlerini de destekleyecek biçimde **yazı-nötr** kurulmuştur.
(rikaenv) PS C:\Users\umut1\OneDrive\Desktop\RikaOCR> git add README.md
(rikaenv) PS C:\Users\umut1\OneDrive\Desktop\RikaOCR> git commit -m "docs: update README with v0.9 architecture and M8 instructions"
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
(rikaenv) PS C:\Users\umut1\OneDrive\Desktop\RikaOCR> git push
Everything up-to-date
(rikaenv) PS C:\Users\umut1\OneDrive\Desktop\RikaOCR> 
> **Durum:** v0.1 — M0 (iskelet & yönetişim). Mimari donduruldu (TDD v0.2).
> Henüz tanıma yeteneği yoktur; altyapı kurulmaktadır.

## Vizyon

Nihai hedef yalnızca OCR değil; satır tanıma, sayfa analizi, Osmanlıca dil
işleme, Latin harflerine transliterasyon ve BOA belgelerinde **kelime arama +
belge üzerinde işaretleme**dir. Sistemin merkezinde, koordinat↔metin
hizalamasını koruyan bir **belge alan modeli** (`Document → Page → Region →
Line → Word → Token`) bulunur.

RikaOCR şu aşamada Rik'a hattına odaklanır. Ancak mimari bilinçli olarak
yazı-nötr tasarlanmıştır ve ileriki sürümlerde Divânî, Ta'lik, Siyâkat ve
Osmanlı matbu metinlerini de destekleyecek biçimde kurulmuştur.

## Mimari

Tasarımın tamamı [`docs/architecture.md`](docs/architecture.md) (TDD v0.2)
belgesindedir. Bağlayıcı kararlar [`docs/adr/`](docs/adr/) altında kayıtlıdır.
Temel ilkeler:

- Satır düzeyi HTR (segmentasyonsuz) — izole harf yalnızca yardımcı veri
- PyTorch + HuggingFace
- Belge-merkezli alan modeli + koordinat↔metin hizalaması
- PAGE-XML kaynak, JSONL türetilmiş eğitim temsili
- Yazı-nötr çekirdek + script profile (Rik'a / Divani / Siyakat / Talik)
- Veri-merkezlilik ve yeniden üretilebilirlik

## Kurulum (geliştirici)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
pytest
```

> M0 aşamasında ağır bağımlılık (PyTorch/TensorFlow/OpenCV) yoktur; yalnızca
> geliştirme araçları kurulur. PyTorch, ileride (M5) opsiyonel `[train]` extras
> olarak eklenecektir.

## Yol haritası

```
M0 (iskelet) → M1 (Document modeli) → M2 (PAGE codec) → M3 (ingest+metadata) →
M4 (dataset) → M5 (ilk HTR modeli) → M6 (uçtan uca) → M7 (NLP+arama) → v1.0
```

## Proje yapısı

```text
RikaOCR/
├── docs/              # architecture.md (TDD v0.2), adr/, datasheets/
├── src/rikaocr/       # kurulabilir Python paketi
├── tests/             # pytest test paketi
├── dataset/ models/ notebooks/
├── pyproject.toml     # paket + araç yapılandırması
├── LICENSE            # Apache-2.0 (kod)
└── LICENSE-DATA       # veri lisansı (karar bekliyor)
```

## Lisans

- **Kod:** Apache-2.0 — bkz. [`LICENSE`](LICENSE)
- **Veri:** karar bekliyor / kısıtlı — bkz. [`LICENSE-DATA`](LICENSE-DATA)

## Katkı

Katkı süreci için bkz. [`CONTRIBUTING.md`](CONTRIBUTING.md). Bu proje bir
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) ile yönetilir.
