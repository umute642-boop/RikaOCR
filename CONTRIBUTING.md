# Katkı Rehberi

RikaOCR, Osmanlı Rik'a belgeleri için açık kaynak bir HTR/OCR platformudur.
Katkılar memnuniyetle karşılanır.

## Geliştirme ortamı

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

> Not: Sanal ortamı OneDrive/cloud ile senkronlanan bir klasörde tutmak yol
> bozulmalarına yol açabilir; mümkünse projeyi senkronsuz bir dizinde tutun.

## Çalışma akışı

- `main` daima yeşildir (CI geçer); doğrudan push yapılmaz.
- Özellik dalları: `feat/...`, `fix/...`, `docs/...`, `chore/...`.
- Commit mesajları **Conventional Commits** biçimindedir: `feat(core): ...`.
  Tipler: `feat`, `fix`, `test`, `docs`, `chore`, `refactor`, `perf`, `ci`.
- PR açmadan önce yerelde şunlar geçmelidir:

```bash
ruff check .
black --check .
mypy src
pytest
```

## "Tamamlandı" tanımı (Definition of Done)

Bir değişiklik ancak şu koşullarla bitmiş sayılır:

1. Kod + tip işaretleri (type hints) + docstring
2. Testler yeşil
3. `ruff` / `black` / `mypy` temiz
4. İlgili dokümantasyon güncel
5. PR review geçti

## Mimari

Tüm geliştirme `docs/architecture.md` (TDD v0.2) ve `docs/adr/` kararlarına bağlı
kalır. Mimari değişiklik **yalnızca yeni bir ADR ile** yapılır; mevcut bir karar
değişecekse eski ADR "Yerini aldı" olarak işaretlenir.

## Kod stili

- Python 3.11+, PEP 8, satır uzunluğu 100.
- Küçük fonksiyonlar, küçük modüller, SOLID ilkeleri.
- Her kaynak dosyada `# SPDX-License-Identifier: Apache-2.0` başlığı.

## Veri katkıları

BOA görüntü hakları netleşene kadar veri katkıları kısıtlıdır. Ayrıntı:
`LICENSE-DATA` ve `docs/adr/ADR-014-data-license.md`.

## Lisans

Kod katkıları **Apache-2.0** altında lisanslanır (bkz. `LICENSE`). Katkı
göndererek, katkınızın bu lisans altında dağıtılmasını kabul etmiş olursunuz.

## Davranış kuralları

Bu projeye katılım, `CODE_OF_CONDUCT.md` belgesindeki kurallara tabidir.
