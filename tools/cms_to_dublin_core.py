#!/usr/bin/env python3
"""
CMS → Dublin Core Converter
Caribbean Metadata Standard v2.0
Caribwood Language Lab — https://caribbeanmetadata.org
License: CC BY 4.0

Usage:
    python cms_to_dublin_core.py input.json
    python cms_to_dublin_core.py input.json --format xml
    python cms_to_dublin_core.py input.json --format csv
    python cms_to_dublin_core.py input.json --format both
    python cms_to_dublin_core.py input.json --validate-only

Outputs:
    <input_name>_dublin_core.xml   (default or --format xml/both)
    <input_name>_dublin_core.csv   (--format csv/both)

Mapping reference:
    CMS field                  → Dublin Core field
    ─────────────────────────────────────────────
    name                       → dc:title
    description                → dc:description
    creator.name               → dc:creator
    datePublished              → dc:date
    inLanguage                 → dc:language
    keywords[]                 → dc:subject (one per keyword)
    cms:territory              → dc:coverage (spatial)
    cms:environment            → dc:coverage (spatial, qualifier)
    cms:narrative_genre        → dc:type
    cms:cultural_markers[]     → dc:subject (one per marker)
    cms:sociohistorical_markers[] → dc:subject (one per marker)
    cms:certification          → dc:relation (CMS certification level)
    cms:standard_version       → dc:source
    url                        → dc:identifier
    @type                      → dc:format (content type)
"""

import json
import csv
import sys
import argparse
import re
from pathlib import Path
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


# ─── MAPPING TABLE ──────────────────────────────────────────────────────────

CMS_TO_DC = {
    "name":                        "dc:title",
    "description":                 "dc:description",
    "datePublished":               "dc:date",
    "inLanguage":                  "dc:language",
    "url":                         "dc:identifier",
    "@type":                       "dc:format",
}

# Dublin Core namespaces
DC_NS  = "http://purl.org/dc/elements/1.1/"
CMS_NS = "https://caribbeanmetadata.org/ns/"

# BCP 47 → human-readable language names
LANG_LABELS = {
    "ht":         "Haitian Creole",
    "gcf":        "Guadeloupe Creole",
    "mart1259":   "Martinique Creole",
    "jam":        "Jamaican Patois",
    "fr":         "French",
    "en":         "English",
    "es":         "Spanish",
    "nl":         "Dutch / Papiamento",
}


# ─── VALIDATION ─────────────────────────────────────────────────────────────

def validate_cms(data: dict) -> list[str]:
    """
    Validate a CMS JSON-LD document.
    Returns a list of warning strings (empty = valid).
    """
    warnings = []

    # Required fields
    for field in ["@context", "@type", "name"]:
        if field not in data:
            warnings.append(f"MISSING required field: {field}")

    # @context must declare cms namespace
    ctx = data.get("@context", {})
    if isinstance(ctx, dict):
        if ctx.get("cms") != CMS_NS:
            warnings.append(
                f"@context.cms should be '{CMS_NS}' "
                f"(found: {ctx.get('cms', 'MISSING')})"
            )
        if "@vocab" not in ctx:
            warnings.append("@context missing @vocab — schema.org properties will not resolve")
    elif isinstance(ctx, str):
        warnings.append(
            "@context is a plain string — CMS namespace not declared. "
            "Use object form: {'@vocab': 'https://schema.org/', 'cms': '...'}"
        )

    # inLanguage must be BCP 47 (rough check: 2–3 chars or subtag)
    lang = data.get("inLanguage", "")
    if lang and not re.match(r'^[a-zA-Z]{2,8}(-[a-zA-Z0-9]{1,8})*$', lang):
        warnings.append(
            f"inLanguage '{lang}' may not be valid BCP 47. "
            "Expected: ht, gcf, jam, fr, en…"
        )

    # cms:standard_version
    if data.get("cms:standard_version") != "CMS-2.0":
        warnings.append(
            f"cms:standard_version should be 'CMS-2.0' "
            f"(found: {data.get('cms:standard_version', 'MISSING')})"
        )

    # cms:certification value
    cert = data.get("cms:certification")
    if cert and cert not in ("Bronze", "Silver", "Gold", "Platinum"):
        warnings.append(
            f"cms:certification '{cert}' is not a valid level. "
            "Expected: Bronze, Silver, Gold, Platinum"
        )

    return warnings


# ─── EXTRACTION ─────────────────────────────────────────────────────────────

def extract_dc_fields(data: dict) -> list[tuple[str, str]]:
    """
    Extract Dublin Core field-value pairs from a CMS JSON-LD document.
    Returns a list of (dc_field, value) tuples — multiple entries per field allowed.
    """
    fields = []

    # dc:title
    if name := data.get("name"):
        fields.append(("dc:title", name))

    # dc:description
    if desc := data.get("description"):
        fields.append(("dc:description", desc))

    # dc:creator — handles Person or Organization
    creator = data.get("creator", {})
    if isinstance(creator, dict):
        if cname := creator.get("name"):
            ctype = creator.get("@type", "Person")
            fields.append(("dc:creator", f"{cname} [{ctype}]"))
    elif isinstance(creator, str):
        fields.append(("dc:creator", creator))

    # dc:date
    if date := data.get("datePublished"):
        fields.append(("dc:date", date))

    # dc:language — BCP 47 + human label
    if lang := data.get("inLanguage"):
        label = LANG_LABELS.get(lang, "")
        fields.append(("dc:language", f"{lang}" + (f" ({label})" if label else "")))

    # dc:identifier
    if url := data.get("url"):
        fields.append(("dc:identifier", url))

    # dc:format — content type from @type
    if ctype := data.get("@type"):
        fields.append(("dc:format", f"schema:{ctype}"))

    # dc:subject — from keywords[]
    for kw in (data.get("keywords") or []):
        fields.append(("dc:subject", str(kw)))

    # dc:subject — from cms:cultural_markers[]
    for marker in (data.get("cms:cultural_markers") or []):
        fields.append(("dc:subject", f"CMS:cultural:{marker}"))

    # dc:subject — from cms:sociohistorical_markers[]
    for marker in (data.get("cms:sociohistorical_markers") or []):
        fields.append(("dc:subject", f"CMS:sociohistorical:{marker}"))

    # dc:subject — from cms:narrative_genre
    if genre := data.get("cms:narrative_genre"):
        fields.append(("dc:subject", f"CMS:genre:{genre}"))

    # dc:coverage — spatial: territory + environment
    territory = data.get("cms:territory") or (
        data.get("contentLocation", {}).get("name") if isinstance(data.get("contentLocation"), dict) else None
    )
    if territory:
        env = data.get("cms:environment", "")
        spatial = territory + (f" ({env})" if env else "")
        fields.append(("dc:coverage", f"spatial:{spatial}"))

    # dc:coverage — temporal: sociohistorical context (first marker as proxy)
    socio = data.get("cms:sociohistorical_markers") or []
    if socio:
        fields.append(("dc:coverage", f"temporal:{socio[0]}"))

    # dc:type — narrative genre
    if genre := data.get("cms:narrative_genre"):
        fields.append(("dc:type", genre))

    # dc:relation — CMS certification
    cert = data.get("cms:certification")
    cert_date = data.get("cms:certification_date", "")
    if cert:
        val = f"CMS-Certification:{cert}"
        if cert_date:
            val += f" ({cert_date})"
        fields.append(("dc:relation", val))

    # dc:source — CMS standard version
    if version := data.get("cms:standard_version"):
        fields.append(("dc:source", f"Caribbean Metadata Standard {version} — {CMS_NS}"))

    # dc:rights — default open license
    fields.append(("dc:rights", "CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/"))

    return fields


# ─── XML OUTPUT ─────────────────────────────────────────────────────────────

def to_xml(fields: list[tuple[str, str]], source_file: str) -> str:
    root = Element("oai_dc:dc", attrib={
        "xmlns:oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/",
        "xmlns:dc":     DC_NS,
        "xmlns:xsi":    "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation": (
            "http://www.openarchives.org/OAI/2.0/oai_dc/ "
            "http://www.openarchives.org/OAI/2.0/oai_dc.xsd"
        ),
    })

    # Conversion metadata
    meta = SubElement(root, "dc:description")
    meta.text = (
        f"Converted from CMS JSON-LD by cms_to_dublin_core.py — "
        f"{datetime.now().strftime('%Y-%m-%d')} — "
        f"source: {source_file}"
    )

    for field, value in fields:
        el = SubElement(root, field)
        el.text = value

    raw = tostring(root, encoding="unicode")
    return minidom.parseString(raw).toprettyxml(indent="  ")


# ─── CSV OUTPUT ─────────────────────────────────────────────────────────────

def to_csv(fields: list[tuple[str, str]], output_path: Path) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["dc_field", "value", "cms_source"])
        for field, value in fields:
            # Annotate origin
            if "CMS:" in value or "CMS-" in value or "Caribbean Metadata" in value:
                source = "CMS extension"
            elif field in ("dc:title", "dc:creator", "dc:date", "dc:language", "dc:format"):
                source = "schema.org core"
            else:
                source = "mapped"
            writer.writerow([field, value, source])


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Convert a CMS JSON-LD file to Dublin Core (XML and/or CSV).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("input", help="Path to CMS JSON-LD file (.json)")
    parser.add_argument(
        "--format", choices=["xml", "csv", "both"], default="xml",
        help="Output format (default: xml)"
    )
    parser.add_argument(
        "--validate-only", action="store_true",
        help="Only validate — do not produce output files"
    )
    parser.add_argument(
        "--output-dir", default=None,
        help="Directory for output files (default: same as input)"
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

    # Remove _cms_template annotation keys before processing
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

    # Extract Dublin Core fields
    fields = extract_dc_fields(data)

    # Determine output directory
    out_dir = Path(args.output_dir) if args.output_dir else input_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = input_path.stem

    # XML output
    if args.format in ("xml", "both"):
        xml_path = out_dir / f"{stem}_dublin_core.xml"
        xml_str = to_xml(fields, input_path.name)
        xml_path.write_text(xml_str, encoding="utf-8")
        print(f"✓  XML  → {xml_path}")

    # CSV output
    if args.format in ("csv", "both"):
        csv_path = out_dir / f"{stem}_dublin_core.csv"
        to_csv(fields, csv_path)
        print(f"✓  CSV  → {csv_path}")

    # Summary
    print(f"\n   {len(fields)} Dublin Core fields extracted")
    dc_counts = {}
    for field, _ in fields:
        dc_counts[field] = dc_counts.get(field, 0) + 1
    for field, count in sorted(dc_counts.items()):
        print(f"   {field:<20} × {count}")
    print()


if __name__ == "__main__":
    main()
