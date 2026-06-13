# CMS NLP Corpus — Pointer

> **The corpus lives in its own dedicated repository.**  
> This file is a navigation pointer only.

---

## → [github.com/heso73/cms-nlp-corpus](https://github.com/heso73/cms-nlp-corpus)

The **CMS NLP Corpus** is maintained as a separate repository to allow independent versioning, citation, and academic use.

### Quick stats (v2.0 — June 2026)

| Metric | Value |
|--------|-------|
| Records | 110 |
| Languages | 10 (BCP 47) |
| Cultural markers | 27 |
| Territories | 17 |
| Domains | 14 |
| License | CC BY 4.0 |

### Direct links

| Resource | URL |
|----------|-----|
| Corpus JSONL | [data/CMS_corpus_v2_unified.jsonl](https://github.com/heso73/cms-nlp-corpus/blob/main/data/CMS_corpus_v2_unified.jsonl) |
| Schema JSON | [data/CMS_corpus_schema_v2.json](https://github.com/heso73/cms-nlp-corpus/blob/main/data/CMS_corpus_schema_v2.json) |
| Cultural markers | [docs/CULTURAL_MARKERS.md](https://github.com/heso73/cms-nlp-corpus/blob/main/docs/CULTURAL_MARKERS.md) |
| Languages | [docs/LANGUAGES.md](https://github.com/heso73/cms-nlp-corpus/blob/main/docs/LANGUAGES.md) |
| Schema docs | [docs/SCHEMA.md](https://github.com/heso73/cms-nlp-corpus/blob/main/docs/SCHEMA.md) |
| Validate script | [scripts/validate_corpus.py](https://github.com/heso73/cms-nlp-corpus/blob/main/scripts/validate_corpus.py) |
| Add record | [scripts/add_record.py](https://github.com/heso73/cms-nlp-corpus/blob/main/scripts/add_record.py) |

### Load corpus (Python)

```python
import json

with open("CMS_corpus_v2_unified.jsonl", encoding="utf-8") as f:
    records = [json.loads(line) for line in f if line.strip()]

print(f"Loaded {len(records)} records")
# Filter by territory
guadeloupe = [r for r in records if r.get("cms:territory") == "GLP"]
# Filter by language
creole = [r for r in records if r.get("inLanguage") in ("hat", "gcf", "acf")]
```

---

*Caribbean Metadata Standard · [caribbeanmetadata.org](https://caribbeanmetadata.org) · cms@caribwood.org*
