# Caribbean Metadata Standard (CMS)
### Reclaiming Digital Visibility for Caribbean Creative Industries

[![Version](https://img.shields.io/badge/version-2.0-0B4F6C)](https://caribbeanmetadata.org)
[![License](https://img.shields.io/badge/license-CC%20BY%204.0-C9843A)](https://creativecommons.org/licenses/by/4.0/)
[![Status](https://img.shields.io/badge/status-active-3FB950)](https://caribbeanmetadata.org)

---

The **Caribbean Metadata Standard (CMS)** is the first open framework designed to classify, describe, and index Caribbean audiovisual content — aligning with global digital platforms while preserving cultural authenticity.

It does not replace existing standards. It extends them: adding a Caribbean semantic layer to **Dublin Core**, **schema.org**, and **EBUCore**.

→ **White Paper v2.0:** [caribbeanmetadata.org](https://caribbeanmetadata.org)  
→ **Live Tagger:** [caribbeanmetadata.org/#tagger](https://caribbeanmetadata.org/#tagger)  
→ **Contact:** cms@caribwood.org

---

## The Problem

Caribbean creators face three systemic barriers:

- **Misclassification** — Platforms lack categories for Caribbean genres, dialects, and cultural nuances
- **Algorithmic Blindness** — Recommendation engines cannot promote what they cannot interpret
- **Cultural Dilution** — Without proper metadata, Caribbean identity is flattened into generic categories

## The Solution — Six Metadata Families

| Family | CMS Fields | Example Tags |
|---|---|---|
| **Linguistic** | `cms:linguistic_marker`, `cms:code_switching` | Haitian Creole, FR/Kreyol |
| **Cultural** | `cms:cultural_markers[]` | Carnival, Vodou, Diaspora identity |
| **Narrative** | `cms:narrative_genre` | Magical realism, Social drama |
| **Rhythmic** | `cms:rhythmic_tempo` | Syncopated, Island tempo |
| **Geographic** | `cms:territory`, `cms:environment` | Haiti, Guadeloupe, Coastal |
| **Socio-historical** | `cms:sociohistorical_markers[]` | Postcolonial identity, Creolization |

---

## Quick Start

### Minimum valid CMS document

```json
{
  "@context": {
    "@vocab": "https://schema.org/",
    "cms": "https://caribbeanmetadata.org/ns/"
  },
  "@type": "CreativeWork",
  "name": "Your content title",
  "inLanguage": "ht",
  "cms:territory": "Haiti",
  "cms:standard_version": "CMS-2.0"
}
```

### Full example

```json
{
  "@context": {
    "@vocab": "https://schema.org/",
    "cms": "https://caribbeanmetadata.org/ns/"
  },
  "@type": "Movie",
  "name": "Anba Dlo",
  "description": "A documentary on Vodou spirituality in rural Haiti.",
  "creator": { "@type": "Person", "name": "Claudine Moreau" },
  "datePublished": "2024-06-01",
  "inLanguage": "ht",
  "keywords": ["haiti", "documentary", "vodou"],
  "cms:territory": "Haiti",
  "cms:environment": "Rural",
  "cms:linguistic_marker": "Haitian Creole",
  "cms:narrative_genre": "Documentary",
  "cms:cultural_markers": ["Vodou", "Afro-Caribbean spirituality"],
  "cms:rhythmic_tempo": "slow contemplative island",
  "cms:sociohistorical_markers": ["Postcolonial identity", "Memory of slavery"],
  "cms:certification": "Gold",
  "cms:standard_version": "CMS-2.0"
}
```

→ **Use the interactive Tagger** to generate your JSON-LD without writing code: [caribbeanmetadata.org/#tagger](https://caribbeanmetadata.org/#tagger)

---

## Integration Levels

| Level | Description | Effort |
|---|---|---|
| **Level 1 — Basic** | Accept CMS tags as keywords in existing fields (`dc:subject`) | Hours |
| **Level 2 — Structured** | Map CMS families to dedicated fields or `schema:additionalProperty` | Days |
| **Level 3 — Native** | Fully integrate all six families as first-class metadata fields | Weeks |

---

## Repository Structure

```
cms/
├── README.md                        # This file
├── LICENSE                          # CC BY 4.0
│
├── spec/
│   └── CMS_WhitePaper_v2.0.md       # Full standard specification (Markdown)
│
├── templates/
│   └── cms_template.json            # Annotated JSON-LD template for creators
│
├── tools/
│   ├── cms_to_dublin_core.py        # CMS → Dublin Core XML/CSV converter
│   └── cms_to_ebucore.py            # CMS → EBUCore 1.6 XML converter
│
├── examples/
│   ├── example_movie.json           # Movie (Haiti, Documentary)
│   ├── example_music.json           # Music recording (Guadeloupe, Konpa)
│   └── example_podcast.json         # Podcast (Jamaica, Diaspora)
│
└── docs/
    └── developer_guide.html         # Full technical reference for developers
```

---

## Tools

### CMS → Dublin Core
```bash
python tools/cms_to_dublin_core.py your_content.json
python tools/cms_to_dublin_core.py your_content.json --format both
python tools/cms_to_dublin_core.py your_content.json --validate-only
```

### CMS → EBUCore
```bash
python tools/cms_to_ebucore.py your_content.json
python tools/cms_to_ebucore.py your_content.json --validate-only
```

Both scripts require **Python 3.10+** and no external dependencies.

---

## Governance

The CMS is designed as a **regional common good**, not a private asset.

| Body | Role |
|---|---|
| **Technical Committee** | Validates new tags, corrections, minor versions. 5–9 experts, 2-year mandates. |
| **General Assembly** | Approves major versions. All adopting institutions, one vote each. |
| **Secretariat** | Operations, website, GitHub, certifications. |

**Transfer clause:** Once 5 independent Caribbean institutions officially adopt the CMS, governance transfers entirely from Caribwood Language Lab to the independent Technical Committee.

→ Current adopter count: **0 / 5** — [express interest](mailto:cms@caribwood.org?subject=CMS%20Co-adoption%20Interest)

---

## Contributing

The CMS governance is open. Any Caribbean institution can:

- **Propose new tags** — open an Issue using the `tag-proposal` template
- **Report errors** — open an Issue using the `correction` template  
- **Join the Technical Committee** — contact cms@caribwood.org

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full evolution process.

---

## Roadmap

| Phase | Timeline | Key Deliverable |
|---|---|---|
| Phase 1 — Foundation | Months 0–3 | CMS v1.0 + Metadata Bible |
| Phase 2 — Adoption | Months 3–9 | Pilot platforms + Certification badges |
| Phase 3 — Scaling | Months 9–18 | AI-assisted tagging (experimental) + CMS v2.0 public |

---

## License

**CC BY 4.0** — Caribbean Metadata Standard © 2026 Caribwood Language Lab  
You are free to use, adapt, and redistribute with attribution.  
→ [creativecommons.org/licenses/by/4.0](https://creativecommons.org/licenses/by/4.0/)

---

*Caribwood Language Lab — Metadata & Cultural Innovation Hub*  
*caribbeanmetadata.org · cms@caribwood.org*
