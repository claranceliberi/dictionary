#!/usr/bin/env python3
"""
Parser for Inkoranyamuga y'Ikoranabuhanga markdown.
Extracts dictionary entries and seeds SQLite database.
"""

import re
import os
import json
import glob
import sqlite3
import shutil
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / "content" / "Inkoranyamuga Ikoranabuhanga.pdf"
MARKDOWN_FILE = CONTENT_DIR / "markdown.md"
PAGES_DIR = CONTENT_DIR / "pages"
IMAGES_DIR = BASE_DIR / "images"
DB_PATH = Path(__file__).parent / "dictionary.db"

# Front/back matter image filenames to skip
SKIP_IMAGES = {"img-0.jpeg", "img-1.jpeg", "img-2.jpeg", "img-147.jpeg", "img-148.jpeg", "img-149.jpeg"}

# Noise line patterns — match both Y'IKORANABUHANGA and YIKORANABUHANGA
RE_PAGE_HEADER = re.compile(r"^INKORANYAMUGA\s+Y'?IKORANABUHANGA\s*$")
RE_PAGE_NUMBER = re.compile(r"^\d{1,3}\s*$")
RE_IMAGE = re.compile(r"!\[([^\]]+)\]\(([^)]+)\)")

# Entry boundary detection
# Matches both: **Term** (pronunciation). AND **Term (pronunciation).**
RE_ENTRY_BOLD = re.compile(
    r"^\*\*(.+?)\*\*\*?\s*\((.+?)\)\."
    r"|"
    r"^\*\*(.+?)\s*\((.+?)\)\.\*\*"
)
# Heading entries MUST have (pronunciation) to qualify as entries
RE_ENTRY_HEADING = re.compile(r"^##\s+(.+?)\s*\(([^)]+)\)")
RE_ENTRY_PLAIN = re.compile(
    r"^([A-ZÀÂÉÈÊËÎÏÔÛÙÜÇK][^\n(]{1,80}?)\s*\(([^)]{2,80})\)\."
)

# Field markers — lines starting with these are continuations, not new entries
RE_FIELD_START = re.compile(r"^(HI|Eng|EnIg|Engl|Fr|Fra|NK|SH|ENG)\s*:")

# Field splitter — also handle lowercase variants like "fr:"
RE_FIELDS = re.compile(
    r"\b(HI|Eng|EnIg|Engl|ENG|Fr|fra|Fra|fr|NK|Nk|SH)\s*:?\s*(?=\s)"
    r"|\b(HI|Eng|EnIg|Engl|ENG|Fr|fra|Fra|fr|NK|Nk|SH)\s*:\s*"
)
# Simpler: split on known field markers with colon
RE_FIELDS = re.compile(
    r"\b(HI|Eng|EnIg|Engl|ENG|Fr|Fra|fra|fr|NK|Nk|SH)\s*:\s*"
)

# Known NK categories for fuzzy matching when prefix is missing
KNOWN_CATEGORIES = [
    "Ikoranabuhanga rya mudasobwa",
    "Ikoranabuhanga rya murandasi",
    "Itumanaho koranabuhanga",
    "Isakazamakuru",
    "Ubwenge buhangano",
    "Urusobe ntangamakuru",
    "Ikoranabuhanga ngaragazabimenyetso",
    "Ikoranabuhanga ndangamuntu",
    "Ikoranabuhanga ry'imari",
    "Itangazabumenyi koranabuhanga",
    "Ikorabuhanga rya mudasobwa",   # OCR variant
    "Ibikoresho by'itangazamakuru",
    "Ikoranabuhanga ry'imiraba",
    "Ikoranabuhanga ry'amashusho",
    "Isakazabumenyi koranabuhanga",
    "Ikoranabuhanga ry'amajwi",
    "Ikoranabuhanga ry'itumanaho",
    "Ibikoresho bya mudasobwa",
]

FIELD_ALIASES = {
    "EnIg": "Eng",
    "Engl": "Eng",
    "ENG": "Eng",
    "Fra": "Fr",
    "fra": "Fr",
    "fr": "Fr",
    "Nk": "NK",
}

# OCR typo → canonical category mapping
CATEGORY_TYPO_MAP = {
    "Ikorabuhanga rya mudasobwa": "Ikoranabuhanga rya mudasobwa",
    "Inkoranabuhanga rya mudasobwa": "Ikoranabuhanga rya mudasobwa",
    "Ikorananabuhanga rya mudasobwa": "Ikoranabuhanga rya mudasobwa",
    "Ikoranabuhaga rya mudasobwa": "Ikoranabuhanga rya mudasobwa",
    "Ikoranabuhanaga rya mudasobwa": "Ikoranabuhanga rya mudasobwa",
    "Ikoranabuhanga rya mudasi": "Ikoranabuhanga rya mudasobwa",
    "Ikoranabuhanga wa mudasobwa": "Ikoranabuhanga rya mudasobwa",
    "Ikoranabuhanga koranabuhanga": "Ikoranabuhanga rya mudasobwa",
    "Ikoranabuhanga rya Murandasi": "Ikoranabuhanga rya murandasi",
    "koranabuhanga rya murandasi": "Ikoranabuhanga rya murandasi",
    "Urusobe ntangazamakuru": "Urusobe ntangamakuru",
    "Urusobe Ntangazamakuru": "Urusobe ntangamakuru",
    "Urusobe nsakazamakuru": "Urusobe ntangamakuru",
    "Urusobe ntagamakuru": "Urusobe ntangamakuru",
    "Ikoranabuhanga rya ngaragazabimenyetso": "Ikoranabuhanga ngaragazabimenyetso",
    "Ikoranabuhanga y'imari": "Ikoranabuhanga ry'imari",
    "Imbonezanzira koranabuhanga": "Ikoranabuhanga rya mudasobwa",
    "Ubwenge bukorano": "Ubwenge buhangano",
    "Ibikoresho bya mudasobwa": "Ikoranabuhanga rya mudasobwa",
    "Itangazabumenyi koranabuhanga": "Isakazamakuru",
    "Isakazabumenyi koranabuhanga": "Isakazamakuru",
}


def normalize_field_key(key: str) -> str:
    return FIELD_ALIASES.get(key, key)


def normalize_category(raw_cat: str) -> str:
    """Clean and normalize a category value."""
    if not raw_cat:
        return ""

    cat = raw_cat

    # Strip markdown bold/italic markers
    cat = re.sub(r"\*+", "", cat).strip()

    # Normalize smart quotes to straight quotes
    cat = cat.replace("\u2019", "'").replace("\u2018", "'")

    # Truncate at leaked definition content
    # e.g. "Ikoranabuhanga rya mudasobwa. SH ..." or ". Inshoza..."
    for marker in [". SH ", ". SH:", ". Inshoza", ". (", ". Ihuriza"]:
        idx = cat.find(marker)
        if idx > 0:
            cat = cat[:idx].strip()

    cat = cat.rstrip(".")

    # Strip parenthetical notes at the end (e.g. "(Biotechnology, imaging ...)")
    cat = re.sub(r"\s*\([^)]*\)\s*$", "", cat).strip()

    # Handle semicolons: split, deduplicate, take first meaningful one
    if ";" in cat:
        parts = [p.strip() for p in cat.split(";") if p.strip()]
        # Deduplicate
        seen = []
        for p in parts:
            normalized_p = normalize_category(p)
            if normalized_p and normalized_p not in seen:
                seen.append(normalized_p)
        cat = seen[0] if seen else ""

    # Apply typo corrections
    if cat in CATEGORY_TYPO_MAP:
        cat = CATEGORY_TYPO_MAP[cat]

    return cat.strip()


def setup_images():
    """Symlink all img-*.jpeg from pages dirs to flat images/ dir."""
    IMAGES_DIR.mkdir(exist_ok=True)
    count = 0
    for img_path in PAGES_DIR.glob("**/img-*.jpeg"):
        dest = IMAGES_DIR / img_path.name
        if not dest.exists():
            shutil.copy2(img_path, dest)
            count += 1
    print(f"  Copied {count} images to {IMAGES_DIR}")


def extract_nk_from_field(value: str) -> tuple[str, str]:
    """Extract leaked NK category from a field value.

    Handles patterns like:
    - "Zettaoctet. NK Ikoranabuhanga rya mudasobwa"
    - "Fond d'écran. Nk: Ikoranabuhanga rya mudasobwa"
    - "Pictogramme; idéogramme. NK Ikoranabuhanga rya mudasobwa"

    Returns (cleaned_value, extracted_category).
    """
    # Pattern: ". NK " or ". Nk:" followed by category text
    m = re.search(r"\.\s*(?:NK|Nk)\s*:?\s*(.+)$", value)
    if m:
        cleaned = value[:m.start()].strip().rstrip(".")
        extracted_cat = m.group(1).strip().rstrip(".")
        return cleaned, extracted_cat
    return value, ""


def parse_entry_text(raw: str, images: list[str]) -> dict | None:
    """Parse a single reassembled entry string into a dict."""
    raw = raw.strip()
    if not raw:
        return None

    # Strip markdown bold/heading markers from start
    term = ""
    pronunciation = ""
    remainder = raw

    # Pattern B1: **Term** (pronunciation).
    m = re.match(r"^\*\*(.+?)\*\*\*?\s*\(([^)]+)\)\.\s*", raw)
    if m:
        term = m.group(1).strip("* ").strip()
        pronunciation = m.group(2).strip()
        remainder = raw[m.end():]
    # Pattern B2: **Term (pronunciation).** — bold wraps entire thing
    elif re.match(r"^\*\*(.+?)\s*\((.+?)\)\.\*\*", raw):
        m = re.match(r"^\*\*(.+?)\s*\((.+?)\)\.\*\*\s*", raw)
        term = m.group(1).strip("* ").strip()
        pronunciation = m.group(2).strip()
        remainder = raw[m.end():]
    else:
        # Pattern C: ## Term (pronunciation). OR ## Term (pronunciation) Eng:...
        m = re.match(r"^##\s+(.+?)\s*\(([^)]+)\)\.?\s*", raw)
        if m:
            term = m.group(1).strip()
            pronunciation = m.group(2).strip()
            remainder = raw[m.end():]
        else:
            # Pattern A: Term (pronunciation). or Term (pronunciation) Eng:
            m = re.match(r"^(.+?)\s*\(([^)]+)\)\.?\s*", raw)
            if m:
                term = m.group(1).strip("# *").strip()
                pronunciation = m.group(2).strip()
                remainder = raw[m.end():]
            else:
                # Can't parse term/pronunciation — skip
                return None

    # Clean up term
    term = re.sub(r"^\*+|\*+$", "", term).strip()
    if not term:
        return None

    # Split remainder by field markers
    parts = RE_FIELDS.split(remainder)
    # parts = [pre_text, key1, val1, key2, val2, ...]
    fields: dict[str, str] = {}
    i = 1
    while i < len(parts) - 1:
        key = normalize_field_key(parts[i].strip())
        val = parts[i + 1].strip().rstrip(".")
        if key in fields:
            fields[key] += "; " + val
        else:
            fields[key] = val
        i += 2

    # Extract synonym (HI field)
    synonym = fields.get("HI", "").strip()

    # Clean english/french
    english = fields.get("Eng", "").strip()
    french = fields.get("Fr", "").strip()
    category = fields.get("NK", "").strip().rstrip(".")
    definition = fields.get("SH", "").strip()

    # Fix: extract NK leaked into french field (e.g. "Zettaoctet. NK Ikoranabuhanga...")
    if french:
        french, leaked_cat = extract_nk_from_field(french)
        if leaked_cat and not category:
            category = leaked_cat

    # Fix: extract lowercase fr: leaked into english field (e.g. "Transport layer. fr: Couche...")
    if english and ". fr:" in english.lower():
        idx = english.lower().find(". fr:")
        leaked_fr = english[idx + 5:].strip()
        english = english[:idx].strip()
        if leaked_fr and not french:
            french = leaked_fr

    # Normalize category
    category = normalize_category(category)

    # Skip entries where all content fields are empty (stub entries from page breaks)
    if not synonym and not english and not french and not category and not definition:
        return None

    # Determine first letter
    first_letter = term[0].upper() if term else "?"

    return {
        "term": term,
        "pronunciation": pronunciation,
        "synonym": synonym,
        "english": english,
        "french": french,
        "category": category,
        "definition": definition,
        "images": json.dumps([img for img in images if img not in SKIP_IMAGES]),
        "letter": first_letter,
    }


def is_entry_start(line: str) -> bool:
    """Return True if this line looks like the beginning of a new dictionary entry."""
    stripped = line.strip()
    if not stripped:
        return False
    # Lines starting with field markers are continuations, not new entries
    if RE_FIELD_START.match(stripped):
        return False
    # Noise lines are never entry starts (e.g. "## © 2026 Inteko y'Umuco (RCHA)")
    if is_noise(stripped):
        return False
    # Bold entry: **Term** (pronunciation). or **Term (pronunciation).**
    if RE_ENTRY_BOLD.match(stripped):
        return True
    # Heading entry: ## Term (pronunciation) — must have pronunciation
    if RE_ENTRY_HEADING.match(stripped):
        return True
    # Plain entry: Capitalized word(s) (pronunciation).
    if RE_ENTRY_PLAIN.match(stripped):
        return True
    return False


def is_noise(line: str) -> bool:
    stripped = line.strip()
    if RE_PAGE_HEADER.match(stripped):
        return True
    if RE_PAGE_NUMBER.match(stripped):
        return True
    # Letter section dividers (single letter on a line)
    if re.match(r"^[A-Z]\s*$", stripped):
        return True
    # Copyright / publisher lines (not dictionary entries)
    if re.match(r"^(©|##\s*©|ISBN)", stripped):
        return True
    return False


def extract_images(line: str) -> list[str]:
    return [m.group(2) for m in RE_IMAGE.finditer(line)]


def load_and_reassemble(md_path: Path) -> list[tuple[str, list[str]]]:
    """
    Pass 1: Read markdown, reassemble entry texts.
    Returns list of (entry_raw_text, [image_filenames]).
    """
    with open(md_path, encoding="utf-8") as f:
        lines = f.readlines()

    # Skip front matter — find first real entry
    start_idx = 0
    for i, line in enumerate(lines):
        if is_entry_start(line.strip()):
            start_idx = i
            break

    # Find last real entry (end of dictionary, skip back matter)
    # Back matter starts after "Z" section entries
    end_idx = len(lines)
    for i in range(len(lines) - 1, start_idx, -1):
        if is_entry_start(lines[i].strip()):
            # Find the end of this last entry
            end_idx = i + 50  # Include some lines after
            break

    entries: list[tuple[str, list[str]]] = []
    current_lines: list[str] = []
    current_images: list[str] = []

    def flush():
        if current_lines:
            text = " ".join(l.strip() for l in current_lines if l.strip())
            entries.append((text, list(current_images)))

    for line in lines[start_idx:end_idx]:
        # Collect images before noise check (images carry data)
        imgs = extract_images(line)

        if is_noise(line.strip()):
            continue

        if imgs:
            # Associate images with current entry
            current_images.extend(imgs)
            # Don't add the image line itself as text
            continue

        stripped = line.strip()
        if not stripped:
            continue

        if is_entry_start(stripped):
            flush()
            current_lines = [stripped]
            current_images = []
        else:
            current_lines.append(stripped)

    flush()
    return entries


def merge_english_continuations(entries: list[dict]) -> list[dict]:
    """Post-processing: merge entries whose term is an English phrase
    (continuation from page break) into the previous entry.

    Example: "Graphics Array" (VGA) should merge into previous "Indebero" entry.
    """
    if not entries:
        return entries

    result = [entries[0]]
    for entry in entries[1:]:
        term = entry["term"]
        # Heuristic: if term is all ASCII (English/technical) and has no english
        # field but has french, it's likely a continuation from a page break
        is_english_term = all(
            c.isascii() or c in "''- " for c in term
        ) and term[0].isupper()
        has_no_english = not entry["english"]
        has_french = bool(entry["french"])

        if is_english_term and has_no_english and has_french and result:
            prev = result[-1]
            # Merge: append this entry's english term to prev's english
            if prev["english"] and not prev["english"].rstrip().endswith(term.split()[0]):
                prev["english"] = prev["english"].rstrip("; ").rstrip(",") + " " + term
            # Merge french
            if entry["french"] and not prev["french"]:
                prev["french"] = entry["french"]
            elif entry["french"]:
                prev["french"] = prev["french"].rstrip("; ") + "; " + entry["french"]
            # Take category/definition from continuation if prev is missing them
            if entry["category"] and not prev["category"]:
                prev["category"] = entry["category"]
            if entry["definition"] and not prev["definition"]:
                prev["definition"] = entry["definition"]
            # Merge images
            prev_imgs = json.loads(prev["images"])
            new_imgs = json.loads(entry["images"])
            prev["images"] = json.dumps(prev_imgs + new_imgs)
        else:
            result.append(entry)

    return result


def init_db(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS entries (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            term          TEXT NOT NULL,
            pronunciation TEXT,
            synonym       TEXT,
            english       TEXT,
            french        TEXT,
            category      TEXT,
            definition    TEXT,
            images        TEXT DEFAULT '[]',
            letter        CHAR(1) NOT NULL
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts USING fts5(
            term, english, french, definition, synonym,
            content='entries', content_rowid='id',
            tokenize='unicode61 remove_diacritics 2'
        );

        CREATE INDEX IF NOT EXISTS idx_entries_letter ON entries(letter, term COLLATE NOCASE);
    """)
    conn.commit()


def seed_db(conn: sqlite3.Connection, entries: list[dict]):
    conn.execute("DELETE FROM entries")
    conn.execute("DELETE FROM entries_fts")
    conn.commit()

    rows = []
    for e in entries:
        rows.append((
            e["term"], e["pronunciation"], e["synonym"],
            e["english"], e["french"], e["category"],
            e["definition"], e["images"], e["letter"],
        ))

    conn.executemany("""
        INSERT INTO entries (term, pronunciation, synonym, english, french, category, definition, images, letter)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()

    # Populate FTS
    conn.execute("""
        INSERT INTO entries_fts(rowid, term, english, french, definition, synonym)
        SELECT id, term, english, french, definition, synonym FROM entries
    """)
    conn.commit()
    print(f"  Inserted {len(rows)} entries into database")


def main():
    print("=== Inkoranyamuga y'Ikoranabuhanga Parser ===\n")

    # Step 1: Set up images
    print("1. Copying images...")
    setup_images()

    # Step 2: Parse markdown
    print("\n2. Parsing markdown...")
    raw_entries = load_and_reassemble(MARKDOWN_FILE)
    print(f"  Found {len(raw_entries)} raw entry blocks")

    # Step 3: Parse fields
    print("\n3. Extracting fields...")
    parsed = []
    skipped = 0
    for raw_text, images in raw_entries:
        entry = parse_entry_text(raw_text, images)
        if entry:
            parsed.append(entry)
        else:
            skipped += 1
            if skipped <= 5:
                print(f"  [SKIP] {raw_text[:80]}")

    print(f"  Parsed: {len(parsed)}, Skipped: {skipped}")

    # Step 3b: Post-processing merges
    print("\n3b. Merging page-break continuations...")
    before = len(parsed)
    parsed = merge_english_continuations(parsed)
    merged = before - len(parsed)
    if merged:
        print(f"  Merged {merged} continuation entries")

    # Step 4: Seed database
    print("\n4. Seeding database...")
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    seed_db(conn, parsed)

    # Step 5: Stats
    print("\n5. Stats:")
    letters = conn.execute(
        "SELECT letter, COUNT(*) FROM entries GROUP BY letter ORDER BY letter"
    ).fetchall()
    for letter, count in letters:
        print(f"  {letter}: {count}")

    total = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    print(f"\n  Total entries: {total}")

    # Category stats
    print("\n  Categories:")
    cats = conn.execute(
        "SELECT category, COUNT(*) as cnt FROM entries WHERE category != '' GROUP BY category ORDER BY cnt DESC"
    ).fetchall()
    for cat, cnt in cats:
        print(f"    [{cnt:4d}] {cat}")
    print(f"  Total distinct categories: {len(cats)}")

    # Sample verification
    print("\n6. Sample entries:")
    samples = conn.execute(
        "SELECT term, english, category FROM entries ORDER BY RANDOM() LIMIT 5"
    ).fetchall()
    for term, eng, cat in samples:
        print(f"  [{cat}] {term} -> {eng}")

    conn.close()
    print("\n Done!")


if __name__ == "__main__":
    main()
