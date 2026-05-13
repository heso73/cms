#!/usr/bin/env python3
"""
CMS → EBUCore Converter
Caribbean Metadata Standard v2.0
Caribwood Language Lab — https://caribbeanmetadata.org
License: CC BY 4.0

Target audience:
    Broadcasters, audiovisual archives, and media institutions using EBUCore 1.6
    (INA, Canal+ Overseas, RFO/Outre-mer 1ère, CAPTV, BBC Caribbean, ARTE, etc.)

Usage:
    python cms_to_ebucore.py input.json
    python cms_to_ebucore.py input.json --output-dir ./output
    python cms_to_ebucore.py input.json --validate-only
    python cms_to_ebucore.py input.json --pretty

Output:
    <input_name>_ebucore.xml

Mapping reference:
    CMS / schema.org field             → EBUCore element
    ──────────────────────────────────────────────────────
    name                               → ebucore:title [@titleType="main"]
    description                        → ebucore:description
    creator.name                       → ebucore:contributor [@jobFunction="director/creator"]
    datePublished                      → ebucore:date [@dateType="published"]
    inLanguage (BCP 47)                → ebucore:language [@typeLabel="original"]
    @type                              → ebucore:type
    keywords[]                         → ebucore:keyword (one per keyword)
    contentLocation.addressCountry     → ebucore:coverage [@coverageType="spatial"]
    cms:territory                      → ebucore:coverage [@coverageType="spatial"]
    cms:environment                    → ebucore:coverage [@coverageType="spatial", qualifier]
    cms:narrative_genre                → ebucore:genre
    cms:cultural_markers[]             → ebucore:subject [@subjectDefinitionSource="CMS:cultural"]
    cms:sociohistorical_markers[]      → ebucore:subject [@subjectDefinitionSource="CMS:sociohistorical"]
    cms:linguistic_marker              → ebucore:language [@typeLabel="dialect"]
    cms:code_switching                 → ebucore:language [@typeLabel="code-switching"]
    cms:rhythmic_tempo                 → ebucore:description [@descriptionType="CMS:rhythmic"]
    cms:certification                  → ebucore:relation [@typeLabel="CMS-certification"]
    cms:standard_version               → ebucore:identifier [@typeLabel="cms-standard-version"]
    url                                → ebucore:locator
"""

import json
import sys
import argparse
import re
from pathlib import Path
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


# ─── CONSTANTS ───────────────────────────────────────────────────────────────

EBUCORE_NS  = "urn:ebu:metadata-schema:ebuCore_2014"
XSI_NS      = "http://www.w3.org/2001/XMLSchema-instance"
XSI_SCHEMA  = "urn:ebu:metadata-schema:ebuCore_2014 https://www.ebu.ch/metadata/schemas/EBUCore/ebucore.xsd"
CMS_NS      = "https://caribbeanmetadata.org/ns/"
CMS_VERSION = "CMS-2.0"

SCHEMA_TYPE_TO_EBUCORE = {
    "Movie":           "AV:film",
    "TVSeries":        "AV:tv-series",
    "MusicRecording":  "AV:music",
    "Podcast":         "AV:podcast",
    "VideoObject":     "AV:video",
    "CreativeWork":    "AV:creative-work",
    "Book":            "text:book",
    "ShortStory":      "text:short-story",
}

LANG_LABELS = {
    "ht":        "Haitian Creole",
    "gcf":       "Guadeloupe Creole",
    "mart1259":  "Martinique Creole",
    "jam":       "Jamaican Patois",
    "fr":        "French",
    "en":        "English",
    "es":        "Spanish",
    "nl":        "Dutch",
    "pap":       "Papiamento",
}


# ─── VALIDATION ──────────────────────────────────────────────────────────────

def validate_cms(data: dict) -> list[str]:
    warnings = []

    for field in ["@context", "@type", "name"]:
        if field not in data:
            warnings.append(f"MISSING required field: {field}")

    ctx = data.get("@context", {})
    if isinstance(ctx, dict):
        if ctx.get("cms") != CMS_NS:
            warnings.append(
                f"@context.cms should be '{CMS_NS}' "
                f"(found: {ctx.get('cms', 'MISSING')})"
            )
    elif isinstance(ctx, str):
        warnings.append(
            "@context is a plain string — CMS namespace not declared. "
            "Use: {\"@vocab\": \"https://schema.org/\", \"cms\": \"https://caribbeanmetadata.org/ns/\"}"
        )

    lang = data.get("inLanguage", "")
    if lang and not re.match(r'^[a-zA-Z]{2,8}(-[a-zA-Z0-9]{1,8})*$', lang):
        warnings.append(
            f"inLanguage '{lang}' may not be valid BCP 47. "
            "Expected: ht, gcf, jam, fr, en…"
        )

    cert = data.get("cms:certification")
    if cert and cert not in ("Bronze", "Silver", "Gold", "Platinum"):
        warnings.append(
            f"cms:certification '{cert}' invalid. "
            "Expected: Bronze, Silver, Gold, Platinum"
        )

    if data.get("cms:standard_version") not in (CMS_VERSION, None, ""):
        warnings.append(
            f"cms:standard_version should be '{CMS_VERSION}' "
            f"(found: {data.get('cms:standard_version')})"
        )

    return warnings


# ─── XML HELPERS ─────────────────────────────────────────────────────────────

def sub(parent: Element, tag: str, text: str = None, **attribs) -> Element:
    """Create a sub-element with optional text and attributes."""
    el = SubElement(parent, tag, attrib={k: v for k, v in attribs.items() if v})
    if text:
        el.text = text
    return el


def prettify(element: Element) -> str:
    raw = tostring(element, encoding="unicode")
    return minidom.parseString(raw).toprettyxml(indent="  ")


def compact(element: Element) -> str:
    return tostring(element, encoding="unicode", xml_declaration=False)


# ─── CORE CONVERSION ─────────────────────────────────────────────────────────

def cms_to_ebucore(data: dict, source_file: str) -> Element:
    """
    Convert a CMS JSON-LD dict to an EBUCore XML element tree.
    Returns the root ebucore:ebuCoreMain Element.
    """

    root = Element("ebucore:ebuCoreMain", attrib={
        "xmlns:ebucore":    EBUCORE_NS,
        "xmlns:dc":         "http://purl.org/dc/elements/1.1/",
        "xmlns:xsi":        XSI_NS,
        "xsi:schemaLocation": XSI_SCHEMA,
        "dateLastModified": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "version":          "1.6",
    })

    # Provenance comment (as processing instruction alternative)
    doc_note = sub(root, "ebucore:description",
        f"Converted from CMS JSON-LD ({CMS_VERSION}) by cms_to_ebucore.py — "
        f"{datetime.now().strftime('%Y-%m-%d')} — source: {source_file}",
        descriptionType="provenance"
    )

    # ── CORE OBJECT ──────────────────────────────────────────────────────────
    core = sub(root, "ebucore:coreMetadata")

    # Title
    name = data.get("name")
    if name:
        title_el = sub(core, "ebucore:title", titleType="main")
        sub(title_el, "dc:title", name)

    # Description
    desc = data.get("description")
    if desc:
        sub(core, "ebucore:description", desc, descriptionType="summary")

    # Type — from @type
    schema_type = data.get("@type", "CreativeWork")
    ebu_type = SCHEMA_TYPE_TO_EBUCORE.get(schema_type, f"AV:{schema_type.lower()}")
    type_el = sub(core, "ebucore:type")
    sub(type_el, "ebucore:objectType", ebu_type, typeLabel=schema_type)

    # ── GENRE ─────────────────────────────────────────────────────────────────
    genre = data.get("cms:narrative_genre")
    if genre:
        sub(core, "ebucore:genre", genre,
            typeLabel="CMS:narrative_genre",
            definitionURI=f"{CMS_NS}narrative_genre/{genre.lower().replace(' ', '_')}")

    # ── LANGUAGE ──────────────────────────────────────────────────────────────
    # Primary language (BCP 47)
    lang = data.get("inLanguage")
    if lang:
        lang_el = sub(core, "ebucore:language", typeLabel="original")
        label = LANG_LABELS.get(lang, "")
        sub(lang_el, "dc:language", lang + (f" ({label})" if label else ""))

    # CMS linguistic marker (human-readable dialect label)
    ling = data.get("cms:linguistic_marker")
    if ling and ling != LANG_LABELS.get(lang, ""):
        lang_el2 = sub(core, "ebucore:language", typeLabel="dialect")
        sub(lang_el2, "dc:language", ling)

    # Code-switching
    codesw = data.get("cms:code_switching")
    if codesw and codesw.lower() not in ("none", ""):
        lang_el3 = sub(core, "ebucore:language", typeLabel="code-switching")
        sub(lang_el3, "dc:language", codesw)

    # ── SUBJECT (cultural markers) ────────────────────────────────────────────
    for marker in (data.get("cms:cultural_markers") or []):
        sub(core, "ebucore:subject", marker,
            subjectDefinitionSource="CMS:cultural",
            subjectDefinitionURI=f"{CMS_NS}cultural/{marker.lower().replace(' ', '_')}")

    # Subject from keywords
    for kw in (data.get("keywords") or []):
        sub(core, "ebucore:keyword", str(kw))

    # ── COVERAGE ──────────────────────────────────────────────────────────────
    territory = data.get("cms:territory") or (
        data.get("contentLocation", {}).get("name")
        if isinstance(data.get("contentLocation"), dict) else None
    )
    environment = data.get("cms:environment", "")

    if territory:
        coverage = territory + (f" — {environment}" if environment else "")
        sub(core, "ebucore:coverage", coverage, coverageType="spatial",
            typeLabel="CMS:territory")

    # Country code from contentLocation
    country = None
    if isinstance(data.get("contentLocation"), dict):
        country = data["contentLocation"].get("addressCountry")
    if country:
        sub(core, "ebucore:coverage", country, coverageType="spatial",
            typeLabel="ISO 3166-1 alpha-2")

    # ── SOCIO-HISTORICAL ──────────────────────────────────────────────────────
    for marker in (data.get("cms:sociohistorical_markers") or []):
        sub(core, "ebucore:subject", marker,
            subjectDefinitionSource="CMS:sociohistorical",
            subjectDefinitionURI=f"{CMS_NS}sociohistorical/{marker.lower().replace(' ', '_')}")

    # ── RHYTHMIC (as description) ──────────────────────────────────────────────
    tempo = data.get("cms:rhythmic_tempo")
    if tempo:
        sub(core, "ebucore:description", tempo,
            descriptionType="CMS:rhythmic_tempo")

    # ── CONTRIBUTOR / CREATOR ────────────────────────────────────────────────
    creator = data.get("creator", {})
    if isinstance(creator, dict) and creator.get("name"):
        contrib_el = sub(core, "ebucore:contributor")
        entity_el  = sub(contrib_el, "ebucore:entity")
        sub(entity_el, "ebucore:name", creator["name"])
        role_el = sub(contrib_el, "ebucore:role")
        sub(role_el, "ebucore:typeLabel", "creator")
        if creator.get("sameAs"):
            sub(entity_el, "ebucore:identifier", creator["sameAs"],
                typeLabel="URI")
    elif isinstance(creator, str):
        contrib_el = sub(core, "ebucore:contributor")
        entity_el  = sub(contrib_el, "ebucore:entity")
        sub(entity_el, "ebucore:name", creator)

    # ── DATE ──────────────────────────────────────────────────────────────────
    date_pub = data.get("datePublished")
    if date_pub:
        date_el = sub(core, "ebucore:date", dateType="published")
        sub(date_el, "ebucore:created", date_pub)

    # ── IDENTIFIER / LOCATOR ──────────────────────────────────────────────────
    url = data.get("url")
    if url:
        sub(core, "ebucore:locator", url, typeLabel="canonical-url")

    # ── CMS CERTIFICATION ────────────────────────────────────────────────────
    cert      = data.get("cms:certification")
    cert_date = data.get("cms:certification_date", "")
    if cert:
        cert_value = f"CMS-{cert}" + (f" ({cert_date})" if cert_date else "")
        sub(core, "ebucore:relation", cert_value,
            typeLabel="CMS-certification",
            runningOrderNumber="1")

    # ── CMS STANDARD VERSION ─────────────────────────────────────────────────
    version = data.get("cms:standard_version", CMS_VERSION)
    sub(core, "ebucore:identifier",
        f"{CMS_NS} — {version}",
        typeLabel="cms-standard-version",
        formatLabel="URI")

    return root


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Convert a CMS JSON-LD file to EBUCore 1.6 XML.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("input", help="Path to CMS JSON-LD file (.json)")
    parser.add_argument(
        "--output-dir", default=None,
        help="Output directory (default: same as input)"
    )
    parser.add_argument(
        "--validate-only", action="store_true",
        help="Only validate — do not produce output files"
    )
    parser.add_argument(
        "--pretty", action="store_true", default=True,
        help="Pretty-print XML output (default: true)"
    )
    parser.add_argument(
        "--compact", action="store_true",
        help="Compact XML — overrides --pretty"
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: File not found — {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON — {e}", file=sys.stderr)
        sys.exit(1)

    # Strip template annotation keys
    data = {k: v for k, v in data.items() if not k.startswith("_")}

    # Validate
    warnings = validate_cms(data)
    if warnings:
        print(f"\n⚠  CMS Validation warnings for: {input_path.name}")
        for w in warnings:
            print(f"   • {w}")
        print()
    else:
        print(f"\n✓  CMS validation passed — {input_path.name}")

    if args.validate_only:
        print("   --validate-only: no output files produced.\n")
        sys.exit(0 if not warnings else 1)

    # Convert
    root = cms_to_ebucore(data, input_path.name)

    # Serialize
    out_dir = Path(args.output_dir) if args.output_dir else input_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{input_path.stem}_ebucore.xml"

    if args.compact:
        xml_str = compact(root)
    else:
        xml_str = prettify(root)

    out_path.write_text(xml_str, encoding="utf-8")

    print(f"✓  EBUCore XML → {out_path}")

    # Summary
    core = root.find("ebucore:coreMetadata")
    if core is not None:
        elements = list(core)
        tags = {}
        for el in elements:
            tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
            tags[tag] = tags.get(tag, 0) + 1
        print(f"\n   {len(elements)} EBUCore elements generated")
        for tag, count in sorted(tags.items()):
            print(f"   ebucore:{tag:<28} × {count}")
    print()


if __name__ == "__main__":
    main()
