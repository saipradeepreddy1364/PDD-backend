import re
import csv
import os

# ============================================================
# This script reads your AFPAM extracted text files and
# pulls real procedure steps to add to dental_steps.csv
# ============================================================

AFPAM_FILES = {
    "vol1": "extracted_texts/afpam_vol1_cleaned.txt",
    "vol2": "extracted_texts/afpam_vol2_cleaned.txt"
}

OUTPUT_CSV = "dental_steps.csv"

# Dental procedure sections to look for in AFPAM
SECTION_KEYWORDS = {
    "Complete Denture": [
        "complete denture", "special tray", "occlusal rim", "record base",
        "teeth setting", "denture processing", "denture base", "articulation",
        "relining", "rebasing", "impression tray"
    ],
    "Cast Partial Denture": [
        "removable partial denture", "cast partial", "rpd framework",
        "block out", "duplication", "spruing", "investing", "casting",
        "finishing and polishing", "partial denture base"
    ],
    "Fixed Partial Denture": [
        "fixed partial denture", "metal ceramic", "porcelain fused",
        "wax pattern", "investing", "casting", "metal coping",
        "bisque bake", "crown fabrication", "pontic"
    ],
    "Crown": [
        "crown preparation", "full cast crown", "metal crown",
        "all ceramic", "zirconia crown", "temporary crown",
        "cementation", "crown and bridge"
    ],
    "Implant": [
        "implant abutment", "implant crown", "screw retained",
        "custom abutment", "implant prosthesis", "osseointegration"
    ]
}

# Step indicator patterns in AFPAM text
STEP_PATTERNS = [
    r'(?:step\s+\d+|procedure\s+\d+)[:\.\-\s]+([A-Za-z][^\n\.]{10,80})',
    r'^\s*\d+\.\s+([A-Z][a-zA-Z\s\-]{10,70})\.',
    r'(?:first|second|third|fourth|fifth|next|then|finally)[,\s]+([a-zA-Z][^\n\.]{10,70})\.',
    r'(?:the\s+)?(?:technician|laboratory)\s+(?:should|must|will)\s+([^\n\.]{10,70})\.',
    r'(?:construct|fabricate|prepare|pour|block|invest|cast|finish|polish|process)\s+(?:the\s+)?([^\n\.]{10,60})\.'
]

def load_text(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return ""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def find_section(text, keywords, window=2000):
    """Find text sections containing procedure keywords"""
    sections = []
    text_lower = text.lower()
    for kw in keywords:
        idx = 0
        while True:
            idx = text_lower.find(kw.lower(), idx)
            if idx == -1:
                break
            start = max(0, idx - 200)
            end = min(len(text), idx + window)
            sections.append(text[start:end])
            idx += len(kw)
    return sections

def extract_steps_from_section(section):
    """Extract sequential steps from a text section"""
    steps = []
    for pattern in STEP_PATTERNS:
        matches = re.findall(pattern, section, re.IGNORECASE | re.MULTILINE)
        for m in matches:
            clean = m.strip().strip('.,;').title()
            if len(clean) > 8 and clean not in steps:
                steps.append(clean)
    return steps

def build_rows_from_steps(procedure, subtype, steps, source):
    """Convert a list of steps into current_step → next_step rows"""
    rows = []
    for i in range(len(steps) - 1):
        rows.append({
            "procedure": procedure,
            "subtype": subtype,
            "current_step": steps[i],
            "next_step": steps[i + 1],
            "component": "Refer AFPAM",
            "brand": "Generic",
            "cost": 0,
            "source": source
        })
    return rows

def main():
    all_rows = []
    total_sections = 0

    for vol_name, filepath in AFPAM_FILES.items():
        print(f"\nProcessing {vol_name}: {filepath}")
        text = load_text(filepath)
        if not text:
            continue

        for procedure, keywords in SECTION_KEYWORDS.items():
            sections = find_section(text, keywords)
            print(f"  {procedure}: found {len(sections)} relevant sections")
            total_sections += len(sections)

            for i, section in enumerate(sections[:10]):  # max 10 sections per procedure
                steps = extract_steps_from_section(section)
                if len(steps) >= 2:
                    subtype = f"{procedure} - AFPAM Ref {i+1}"
                    rows = build_rows_from_steps(procedure, subtype, steps, f"AFPAM_{vol_name}")
                    all_rows.extend(rows)

    print(f"\nTotal sections processed: {total_sections}")
    print(f"Total new rows extracted: {len(all_rows)}")

    if not all_rows:
        print("No rows extracted from AFPAM — using DIAS data only.")
        return

    # Append to existing CSV
    file_exists = os.path.exists(OUTPUT_CSV)
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "procedure", "subtype", "current_step",
            "next_step", "component", "brand", "cost", "source"
        ])
        if not file_exists:
            writer.writeheader()
        writer.writerows(all_rows)

    print(f"Appended {len(all_rows)} AFPAM rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
