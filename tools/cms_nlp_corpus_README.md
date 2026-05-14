# CMS NLP Corpus
### First structured Caribbean cultural corpus — open source

[![License](https://img.shields.io/badge/license-CC%20BY%204.0-C9843A)](https://creativecommons.org/licenses/by/4.0/)
[![Standard](https://img.shields.io/badge/standard-CMS%20v2.0-0B4F6C)](https://caribbeanmetadata.org)
[![Status](https://img.shields.io/badge/status-active-3FB950)](https://github.com/heso73/cms-nlp-corpus)

---

The **CMS NLP Corpus** is the first structured dataset of Caribbean cultural content, annotated according to the [Caribbean Metadata Standard (CMS) v2.0](https://caribbeanmetadata.org). It is designed for natural language processing research, cultural heritage classification, and AI model training on Caribbean linguistic and cultural data.

→ **CMS Standard:** [caribbeanmetadata.org](https://caribbeanmetadata.org)  
→ **CMS Repository:** [github.com/heso73/cms](https://github.com/heso73/cms)  
→ **Contact:** cms@caribwood.org

---

## What is this corpus?

This corpus provides structured, CMS-annotated records covering Caribbean audiovisual and cultural content across 8 languages and 15+ cultural markers. Each record is annotated with the six CMS metadata families:

| Family | Fields |
|---|---|
| **Linguistic** | Language (BCP 47 + ISO 639-3), code-switching |
| **Cultural** | Cultural markers (Carnival, Vodou, Gwoka, Konpa…) |
| **Narrative** | Genre (Documentary, Magical realism, Social drama…) |
| **Rhythmic** | Dialogue tempo |
| **Geographic** | Territory, environment |
| **Socio-historical** | Postcolonial markers, memory, migration |

---

## Repository Structure

```
cms-nlp-corpus/
├── data/
│   ├── CMS_corpus_schema_v1       ← JSON schema for corpus records
│   └── CMS_corpus_v1_unified.jsonl ← Unified corpus (JSONL format)
├── docs/
│   └── SCHEMA                     ← Schema documentation
├── scripts/
│   ├── add_record                 ← Script to add new corpus entries
│   └── validate_corpus            ← Script to validate records against CMS schema
├── CITATION.cff                   ← Citation metadata (academic use)
├── LICENSE                        ← CC BY 4.0
└── README.md                      ← This file
```

---

## Corpus Statistics (v1.0)

| Metric | Value |
|---|---|
| Records | 15 |
| Languages covered | 8 |
| Cultural markers | 15+ |
| Schema fields | 14 |
| Format | JSONL |
| License | CC BY 4.0 |

**Languages:** Haitian Creole (hat) · Guadeloupe Creole (gcf) · Martinique Creole (acf) · Jamaican Patois (jam) · Papiamento (pap) · French (fra) · Spanish (spa) · English (eng)

**Cultural markers include:** gwo ka · bèlè · konpa · zouk · calypso · reggae · tumba · carnival · vodou · diaspora identity · oral tradition

---

## Data Format

Each record in `CMS_corpus_v1_unified.jsonl` follows the CMS JSON-LD schema:

```json
{
  "@context": {
    "@vocab": "https://schema.org/",
    "cms": "https://caribbeanmetadata.org/ns/"
  },
  "@type": "CreativeWork",
  "name": "Content title",
  "inLanguage": "ht",
  "cms:territory": "Haiti",
  "cms:linguistic_marker": "Haitian Creole",
  "cms:cultural_markers": ["Vodou", "Family memory"],
  "cms:narrative_genre": "Documentary",
  "cms:rhythmic_tempo": "slow contemplative island",
  "cms:sociohistorical_markers": ["Postcolonial identity"],
  "cms:standard_version": "CMS-2.0"
}
```

Full schema reference: [docs/SCHEMA](docs/SCHEMA) · [CMS Metadata Bible](https://caribbeanmetadata.org)

---

## Usage

### Load the corpus (Python)

```python
import json

with open('data/CMS_corpus_v1_unified.jsonl', encoding='utf-8') as f:
    records = [json.loads(line) for line in f if line.strip()]

print(f"Loaded {len(records)} records")

# Filter by territory
haiti = [r for r in records if r.get('cms:territory') == 'Haiti']

# Filter by language
creole = [r for r in records if r.get('inLanguage') in ('ht', 'gcf', 'acf')]
```

### Add a new record

```bash
python scripts/add_record
```

### Validate the corpus

```bash
python scripts/validate_corpus
```

---

## Citation

If you use this corpus in your research, please cite it using the metadata in [CITATION.cff](CITATION.cff):

```bibtex
@dataset{caribwood_cms_nlp_corpus_2026,
  author    = {Caribwood Language Lab},
  title     = {CMS NLP Corpus — First structured Caribbean cultural corpus},
  year      = {2026},
  publisher = {GitHub},
  url       = {https://github.com/heso73/cms-nlp-corpus},
  license   = {CC BY 4.0},
  note      = {Annotated according to Caribbean Metadata Standard (CMS) v2.0}
}
```

---

## Contributing

Contributions are welcome — new records, additional languages, corrections, or tooling improvements.

1. Fork the repository
2. Add your record(s) following the CMS schema
3. Run `python scripts/validate_corpus` to verify
4. Open a Pull Request with a brief description

For significant additions (new territories, new cultural markers), please open an Issue first.

For questions about the CMS schema itself, see the [CMS repository](https://github.com/heso73/cms) and its [Metadata Bible](https://caribbeanmetadata.org).

---

## License

**CC BY 4.0** — Caribwood Language Lab, 2026  
Free to use, adapt, and redistribute with attribution.  
→ [creativecommons.org/licenses/by/4.0](https://creativecommons.org/licenses/by/4.0/)

---

*Caribwood Language Lab · caribbeanmetadata.org · cms@caribwood.org*
