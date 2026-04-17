"""
Test suite for Inkoranyamuga y'Ikoranabuhanga dictionary parser.

Run: cd /app/dictionary/backend && python -m pytest test_parser.py -v

Functions under test (all from parser.py):
  - normalize_field_key(key: str) -> str
  - normalize_category(raw_cat: str) -> str
  - extract_nk_from_field(value: str) -> tuple[str, str]
  - parse_entry_text(raw: str, images: list[str]) -> dict | None
  - is_entry_start(line: str) -> bool
  - is_noise(line: str) -> bool
  - extract_images(line: str) -> list[str]
  - load_and_reassemble(md_path: Path) -> list[tuple[str, list[str]]]
  - merge_english_continuations(entries: list[dict]) -> list[dict]
  - init_db(conn) + seed_db(conn, entries)
"""

import pytest
import json
import sqlite3
import tempfile
from pathlib import Path

from parser import (
    normalize_field_key,
    normalize_category,
    extract_nk_from_field,
    parse_entry_text,
    is_entry_start,
    is_noise,
    extract_images,
    load_and_reassemble,
    merge_english_continuations,
    init_db,
    seed_db,
    CATEGORY_TYPO_MAP,
    FIELD_ALIASES,
)


# ============================================================================
# normalize_field_key
# ============================================================================

class TestNormalizeFieldKey:
    """Tests for normalize_field_key(key) -> str"""

    def test_standard_keys_unchanged(self):
        """Standard keys (HI, Eng, Fr, NK, SH) should pass through unchanged."""
        for key in ["HI", "Eng", "Fr", "NK", "SH"]:
            assert normalize_field_key(key) == key

    def test_enig_alias(self):
        """'EnIg' should normalize to 'Eng'."""
        assert normalize_field_key("EnIg") == "Eng"

    def test_engl_alias(self):
        """'Engl' should normalize to 'Eng'."""
        assert normalize_field_key("Engl") == "Eng"

    def test_eng_uppercase_alias(self):
        """'ENG' should normalize to 'Eng'."""
        assert normalize_field_key("ENG") == "Eng"

    def test_fra_alias(self):
        """'Fra' should normalize to 'Fr'."""
        assert normalize_field_key("Fra") == "Fr"

    def test_fra_lowercase_alias(self):
        """'fra' should normalize to 'Fr'."""
        assert normalize_field_key("fra") == "Fr"

    def test_fr_lowercase_alias(self):
        """'fr' should normalize to 'Fr'."""
        assert normalize_field_key("fr") == "Fr"

    def test_nk_lowercase_alias(self):
        """'Nk' should normalize to 'NK'."""
        assert normalize_field_key("Nk") == "NK"

    def test_unknown_key_passthrough(self):
        """Unknown keys should be returned as-is."""
        assert normalize_field_key("XYZ") == "XYZ"


# ============================================================================
# normalize_category
# ============================================================================

class TestNormalizeCategory:
    """Tests for normalize_category(raw_cat) -> str"""

    def test_empty_string(self):
        """Empty string should return empty string."""
        assert normalize_category("") == ""

    def test_none_like_empty(self):
        """Falsy input should return empty string."""
        assert normalize_category("") == ""

    def test_clean_category_unchanged(self):
        """A clean canonical category should pass through unchanged."""
        assert normalize_category("Ikoranabuhanga rya mudasobwa") == "Ikoranabuhanga rya mudasobwa"

    def test_strip_bold_markdown(self):
        """'**Ikoranabuhanga rya mudasobwa**' should strip to clean form."""
        assert normalize_category("**Ikoranabuhanga rya mudasobwa**") == "Ikoranabuhanga rya mudasobwa"

    def test_strip_italic_markdown(self):
        """'*Ikoranabuhanga rya mudasobwa*' should strip to clean form."""
        assert normalize_category("*Ikoranabuhanga rya mudasobwa*") == "Ikoranabuhanga rya mudasobwa"

    def test_strip_partial_markdown(self):
        """'*Ikoranabuhanga rya* mudasobwa' should strip asterisks."""
        assert normalize_category("*Ikoranabuhanga rya* mudasobwa") == "Ikoranabuhanga rya mudasobwa"

    def test_smart_quote_normalization(self):
        """Smart quote \u2019 should be replaced with straight quote '."""
        assert normalize_category("Ikoranabuhanga ry\u2019imari") == "Ikoranabuhanga ry'imari"

    def test_truncate_leaked_sh_definition(self):
        """Category with '. SH ...' leaked definition should be truncated."""
        raw = "Ikoranabuhanga rya mudasobwa. SH Umwanya werekana ahantu"
        assert normalize_category(raw) == "Ikoranabuhanga rya mudasobwa"

    def test_truncate_leaked_inshoza(self):
        """Category with '. Inshoza...' leaked should be truncated."""
        raw = "Ikoranabuhanga rya mudasobwa. Inshoza: Igisobanuro kigufi"
        assert normalize_category(raw) == "Ikoranabuhanga rya mudasobwa"

    def test_truncate_leaked_parenthetical(self):
        """Category with '. (' leaked content should be truncated."""
        raw = "Ikoranabuhanga rya mudasobwa. (Biotechnology, imaging ikoreshwa kwa mugaganga)"
        assert normalize_category(raw) == "Ikoranabuhanga rya mudasobwa"

    def test_strip_trailing_parenthetical(self):
        """Category ending with (extra note) should strip it."""
        raw = "Ikoranabuhanga rya mudasobwa (Biotechnology, imaging ikoreshwa kwa mugaganga)"
        assert normalize_category(raw) == "Ikoranabuhanga rya mudasobwa"

    def test_trailing_dot_stripped(self):
        """Trailing dots should be stripped."""
        assert normalize_category("Ikoranabuhanga rya mudasobwa.") == "Ikoranabuhanga rya mudasobwa"

    def test_deduplicate_semicolons_same(self):
        """'A; A' should deduplicate to 'A'."""
        raw = "Ikoranabuhanga rya mudasobwa; Ikoranabuhanga rya mudasobwa"
        assert normalize_category(raw) == "Ikoranabuhanga rya mudasobwa"

    def test_deduplicate_semicolons_triple(self):
        """'A; A; A' should deduplicate to 'A'."""
        raw = "Ikoranabuhanga rya mudasobwa; Ikoranabuhanga rya mudasobwa; Ikoranabuhanga rya mudasobwa"
        assert normalize_category(raw) == "Ikoranabuhanga rya mudasobwa"

    def test_semicolons_different_takes_first(self):
        """'A; B' with different categories should take the first."""
        raw = "Ikoranabuhanga rya mudasobwa; Ikoranabuhanga ry'amajwi"
        assert normalize_category(raw) == "Ikoranabuhanga rya mudasobwa"

    def test_typo_ikorabuhanga(self):
        """OCR typo 'Ikorabuhanga rya mudasobwa' should correct to canonical."""
        assert normalize_category("Ikorabuhanga rya mudasobwa") == "Ikoranabuhanga rya mudasobwa"

    def test_typo_inkoranabuhanga(self):
        """OCR typo 'Inkoranabuhanga' should correct to canonical."""
        assert normalize_category("Inkoranabuhanga rya mudasobwa") == "Ikoranabuhanga rya mudasobwa"

    def test_typo_ikorananabuhanga(self):
        """OCR typo 'Ikorananabuhanga' should correct to canonical."""
        assert normalize_category("Ikorananabuhanga rya mudasobwa") == "Ikoranabuhanga rya mudasobwa"

    def test_typo_ikoranabuhaga(self):
        """OCR typo 'Ikoranabuhaga' (missing n) should correct to canonical."""
        assert normalize_category("Ikoranabuhaga rya mudasobwa") == "Ikoranabuhanga rya mudasobwa"

    def test_typo_mudasi_truncated(self):
        """OCR typo 'mudasi' (truncated) should correct to 'mudasobwa'."""
        assert normalize_category("Ikoranabuhanga rya mudasi") == "Ikoranabuhanga rya mudasobwa"

    def test_typo_murandasi_capitalized(self):
        """'Ikoranabuhanga rya Murandasi' (capital M) should normalize."""
        assert normalize_category("Ikoranabuhanga rya Murandasi") == "Ikoranabuhanga rya murandasi"

    def test_typo_lowercase_koranabuhanga(self):
        """'koranabuhanga rya murandasi' (missing I) should correct."""
        assert normalize_category("koranabuhanga rya murandasi") == "Ikoranabuhanga rya murandasi"

    def test_typo_urusobe_variants(self):
        """Various 'Urusobe' typos should all normalize to 'Urusobe ntangamakuru'."""
        for typo in ["Urusobe ntangazamakuru", "Urusobe Ntangazamakuru", "Urusobe nsakazamakuru", "Urusobe ntagamakuru"]:
            assert normalize_category(typo) == "Urusobe ntangamakuru", f"Failed for: {typo}"

    def test_typo_ubwenge_bukorano(self):
        """'Ubwenge bukorano' should correct to 'Ubwenge buhangano'."""
        assert normalize_category("Ubwenge bukorano") == "Ubwenge buhangano"

    def test_all_typo_map_entries(self):
        """Every key in CATEGORY_TYPO_MAP should normalize to its value."""
        for typo, canonical in CATEGORY_TYPO_MAP.items():
            assert normalize_category(typo) == canonical, f"Failed for typo: {typo}"

    def test_bold_plus_typo_combined(self):
        """'**Ikorabuhanga rya mudasobwa**' should strip markdown AND fix typo."""
        assert normalize_category("**Ikorabuhanga rya mudasobwa**") == "Ikoranabuhanga rya mudasobwa"

    def test_semicolons_with_markdown(self):
        """Semicolons where parts have markdown should clean both."""
        raw = "**Ikoranabuhanga rya mudasobwa**; **Ikoranabuhanga rya mudasobwa**"
        assert normalize_category(raw) == "Ikoranabuhanga rya mudasobwa"


# ============================================================================
# extract_nk_from_field
# ============================================================================

class TestExtractNkFromField:
    """Tests for extract_nk_from_field(value) -> (cleaned, category)"""

    def test_no_nk_leak(self):
        """Field without NK leak should return unchanged value and empty string."""
        val = "Zettaoctet"
        cleaned, cat = extract_nk_from_field(val)
        assert cleaned == "Zettaoctet"
        assert cat == ""

    def test_nk_without_colon(self):
        """'Zettaoctet. NK Ikoranabuhanga rya mudasobwa' should split correctly."""
        val = "Zettaoctet. NK Ikoranabuhanga rya mudasobwa"
        cleaned, cat = extract_nk_from_field(val)
        assert cleaned == "Zettaoctet"
        assert cat == "Ikoranabuhanga rya mudasobwa"

    def test_nk_with_colon(self):
        """'Fond d'ecran. Nk: Ikoranabuhanga rya mudasobwa' should split correctly."""
        val = "Fond d'ecran. Nk: Ikoranabuhanga rya mudasobwa"
        cleaned, cat = extract_nk_from_field(val)
        assert cleaned == "Fond d'ecran"
        assert cat == "Ikoranabuhanga rya mudasobwa"

    def test_nk_after_semicolons(self):
        """NK leak after semicolons in french should still be extracted."""
        val = "Pictogramme; ideogramme. NK Ikoranabuhanga rya mudasobwa"
        cleaned, cat = extract_nk_from_field(val)
        assert cleaned == "Pictogramme; ideogramme"
        assert cat == "Ikoranabuhanga rya mudasobwa"

    def test_nk_strips_trailing_dot(self):
        """Extracted category should have trailing dot stripped."""
        val = "Zettaoctet. NK Ikoranabuhanga rya mudasobwa."
        cleaned, cat = extract_nk_from_field(val)
        assert cat == "Ikoranabuhanga rya mudasobwa"


# ============================================================================
# is_noise
# ============================================================================

class TestIsNoise:
    """Tests for is_noise(line) -> bool"""

    def test_page_header_with_apostrophe(self):
        """'INKORANYAMUGA Y'IKORANABUHANGA' should be noise."""
        assert is_noise("INKORANYAMUGA Y'IKORANABUHANGA") is True

    def test_page_header_without_apostrophe(self):
        """'INKORANYAMUGA YIKORANABUHANGA' should also be noise."""
        assert is_noise("INKORANYAMUGA YIKORANABUHANGA") is True

    def test_page_number(self):
        """A standalone number like '251' should be noise."""
        assert is_noise("251") is True

    def test_three_digit_number(self):
        """'99' should be noise (page number)."""
        assert is_noise("99") is True

    def test_four_digit_not_noise(self):
        """'1234' (4+ digits) should NOT be noise."""
        assert is_noise("1234") is False

    def test_letter_divider(self):
        """A single letter 'A' on a line should be noise (section divider)."""
        assert is_noise("A") is True

    def test_copyright_line(self):
        """Lines starting with copyright should be noise."""
        assert is_noise("© 2026 Inteko y'Umuco") is True

    def test_heading_copyright(self):
        """'## © 2026 Inteko y'Umuco (RCHA)' should be noise."""
        assert is_noise("## © 2026 Inteko y'Umuco (RCHA)") is True

    def test_isbn_line(self):
        """'ISBN: 978-99977-0-699-7' should be noise."""
        assert is_noise("ISBN: 978-99977-0-699-7") is True

    def test_normal_entry_not_noise(self):
        """A regular entry line should NOT be noise."""
        assert is_noise("Aderesi (aderesi). Eng: Address.") is False

    def test_empty_string_not_noise(self):
        """Empty string should not be noise (it's nothing)."""
        assert is_noise("") is False


# ============================================================================
# is_entry_start
# ============================================================================

class TestIsEntryStart:
    """Tests for is_entry_start(line) -> bool"""

    def test_bold_standard(self):
        """'**Term** (pronunciation).' should be an entry start."""
        assert is_entry_start("**Aderesi** (aderesi). Eng: Address.") is True

    def test_bold_wrapped(self):
        """'**Term (pronunciation).**' (bold wraps whole thing) should be an entry start."""
        assert is_entry_start("**Virusi (viruusi).** Eng: Computer virus.") is True

    def test_heading_with_pronunciation(self):
        """'## Term (pronunciation)' should be an entry start."""
        assert is_entry_start("## Imbonezangiro (imbonezangiro)") is True

    def test_heading_without_pronunciation(self):
        """'## Umwanditsi:' (no pronunciation) should NOT be an entry start."""
        assert is_entry_start("## Umwanditsi:") is False

    def test_heading_section_only(self):
        """'## Ijambo ry'ibanze' (no pronunciation parens) should NOT be an entry start."""
        assert is_entry_start("## Ijambo ry'ibanze") is False

    def test_plain_entry(self):
        """'CapitalizedTerm (pronunciation).' should be an entry start."""
        assert is_entry_start("Aderesi (aderesi). Eng: Address.") is True

    def test_field_marker_eng(self):
        """'Eng: File Transfer Protocol' should NOT be an entry start (field continuation)."""
        assert is_entry_start("Eng: File Transfer Protocol (FTP).") is False

    def test_field_marker_hi(self):
        """'HI: Arugoritime (arugoriitime).' should NOT be an entry start."""
        assert is_entry_start("HI: Arugoritime (arugoriitime).") is False

    def test_field_marker_fr(self):
        """'Fr: Protocole HTTP.' should NOT be an entry start."""
        assert is_entry_start("Fr: Protocole HTTP.") is False

    def test_field_marker_nk(self):
        """'NK: Ikoranabuhanga rya mudasobwa.' should NOT be an entry start."""
        assert is_entry_start("NK: Ikoranabuhanga rya mudasobwa.") is False

    def test_field_marker_sh(self):
        """'SH: Some definition text.' should NOT be an entry start."""
        assert is_entry_start("SH: Some definition text.") is False

    def test_copyright_heading_not_entry(self):
        """'## © 2026 Inteko y'Umuco (RCHA)' should NOT be an entry (noise takes priority)."""
        assert is_entry_start("## © 2026 Inteko y'Umuco (RCHA)") is False

    def test_page_header_not_entry(self):
        """Page header should NOT be an entry start."""
        assert is_entry_start("INKORANYAMUGA YIKORANABUHANGA") is False

    def test_empty_string(self):
        """Empty string should not be an entry start."""
        assert is_entry_start("") is False

    def test_continuation_lowercase(self):
        """Lowercase continuation text should NOT be an entry start."""
        assert is_entry_start("mu isura imwe ntangamakuru byereka abarebyi") is False


# ============================================================================
# extract_images
# ============================================================================

class TestExtractImages:
    """Tests for extract_images(line) -> list[str]"""

    def test_single_image(self):
        """Should extract a single image filename."""
        line = "![img-70.jpeg](img-70.jpeg)"
        assert extract_images(line) == ["img-70.jpeg"]

    def test_no_images(self):
        """Line without images should return empty list."""
        assert extract_images("Aderesi (aderesi). Eng: Address.") == []

    def test_multiple_images(self):
        """Should extract multiple image filenames from one line."""
        line = "![img-1.jpeg](img-1.jpeg) text ![img-2.jpeg](img-2.jpeg)"
        assert extract_images(line) == ["img-1.jpeg", "img-2.jpeg"]


# ============================================================================
# parse_entry_text
# ============================================================================

class TestParseEntryText:
    """Tests for parse_entry_text(raw, images) -> dict | None"""

    def test_standard_bold_entry(self):
        """Standard **Term** (pron). Eng: ... Fr: ... NK: ... SH: ... should parse all fields."""
        raw = "**Aderesi** (aderesi). Eng: Address. Fr: Adresse. NK: Ikoranabuhanga rya mudasobwa. SH: Ibiranga ahantu"
        result = parse_entry_text(raw, [])
        assert result is not None
        assert result["term"] == "Aderesi"
        assert result["pronunciation"] == "aderesi"
        assert result["english"] == "Address"
        assert result["french"] == "Adresse"
        assert result["category"] == "Ikoranabuhanga rya mudasobwa"
        assert result["definition"] == "Ibiranga ahantu"
        assert result["letter"] == "A"

    def test_bold_wrapped_entry(self):
        """**Term (pron).** format should parse correctly."""
        raw = "**Virusi (viruusi).** Eng: Computer virus. Fr: Virus informatique. NK: Ikoranabuhanga rya mudasobwa. SH: Inkoranabuhanga ngome"
        result = parse_entry_text(raw, [])
        assert result is not None
        assert result["term"] == "Virusi"
        assert result["pronunciation"] == "viruusi"
        assert result["english"] == "Computer virus"

    def test_heading_entry(self):
        """## Term (pronunciation) followed by fields should parse correctly."""
        raw = "## Imbonezangiro (imbonezangiro) HI: Arugoritime (arugoriitime). Eng: Algorithm. Fr: Algorithmme. NK: Ikoranabuhanga rya mudasobwa. SH: Igice kimwe"
        result = parse_entry_text(raw, [])
        assert result is not None
        assert result["term"] == "Imbonezangiro"
        assert result["pronunciation"] == "imbonezangiro"
        assert result["synonym"] == "Arugoritime (arugoriitime)"
        assert result["english"] == "Algorithm"

    def test_plain_entry(self):
        """Plain Term (pronunciation). format should parse."""
        raw = "Aderesi (aderesi). Eng: Address. Fr: Adresse. NK: Ikoranabuhanga rya mudasobwa. SH: Ibiranga"
        result = parse_entry_text(raw, [])
        assert result is not None
        assert result["term"] == "Aderesi"

    def test_field_aliases_enig(self):
        """EnIg: should be treated as Eng:."""
        raw = "**Term** (pron). EnIg: Something. NK: Ikoranabuhanga rya mudasobwa. SH: Def"
        result = parse_entry_text(raw, [])
        assert result is not None
        assert result["english"] == "Something"

    def test_multiple_eng_fields_concatenated(self):
        """Multiple Eng: fields should be joined with '; '."""
        raw = "**Term** (pron). Eng: First. Eng: Second. NK: Ikoranabuhanga rya mudasobwa. SH: Def"
        result = parse_entry_text(raw, [])
        assert result is not None
        assert "First" in result["english"]
        assert "Second" in result["english"]

    def test_empty_raw_returns_none(self):
        """Empty raw string should return None."""
        assert parse_entry_text("", []) is None

    def test_unparseable_returns_none(self):
        """Text with no term/pronunciation pattern should return None."""
        assert parse_entry_text("just some random text", []) is None

    def test_all_fields_empty_returns_none(self):
        """Entry with only term+pronunciation but no content should return None (stub)."""
        raw = "**Term** (pron). Eng:"
        result = parse_entry_text(raw, [])
        # If Eng: has nothing after it, all fields are empty -> None
        assert result is None

    def test_french_nk_leak_extracted(self):
        """French value containing '. NK ...' should have NK extracted to category."""
        raw = "Zetabayiti (zetabayiti). Eng: Zettabyte. Fr: Zettaoctet. NK Ikoranabuhanga rya mudasobwa. SH: Definition"
        result = parse_entry_text(raw, [])
        assert result is not None
        assert "NK" not in (result["french"] or "")
        assert result["category"] == "Ikoranabuhanga rya mudasobwa"

    def test_english_fr_leak_extracted(self):
        """English value containing '. fr: ...' should split french out."""
        raw = "Icyiciro ntwaramakuru (icyiiciro). Eng: Transport layer. fr: Couche de transport. NK: Itumanaho koranabuhanga. SH: Def"
        result = parse_entry_text(raw, [])
        assert result is not None
        assert "fr:" not in (result["english"] or "").lower()
        assert result["english"] == "Transport layer"
        assert "Couche de transport" in (result["french"] or "")

    def test_category_normalization_applied(self):
        """Category should be normalized (typo correction, markdown stripping)."""
        raw = "**Term** (pron). Eng: Test. NK: **Ikorabuhanga rya mudasobwa**. SH: Def"
        result = parse_entry_text(raw, [])
        assert result is not None
        assert result["category"] == "Ikoranabuhanga rya mudasobwa"

    def test_images_skip_front_matter(self):
        """Front/back matter images (img-0, img-1, img-2, img-147-149) should be filtered out."""
        raw = "**Term** (pron). Eng: Test. NK: Ikoranabuhanga rya mudasobwa. SH: Def"
        result = parse_entry_text(raw, ["img-0.jpeg", "img-50.jpeg", "img-147.jpeg"])
        assert result is not None
        images = json.loads(result["images"])
        assert images == ["img-50.jpeg"]

    def test_letter_from_first_char(self):
        """Letter should be the uppercase first character of the term."""
        raw = "**Aderesi** (aderesi). Eng: Address. NK: Ikoranabuhanga rya mudasobwa. SH: Def"
        result = parse_entry_text(raw, [])
        assert result["letter"] == "A"


# ============================================================================
# load_and_reassemble
# ============================================================================

class TestLoadAndReassemble:
    """Tests for load_and_reassemble(md_path) -> list[tuple[str, list[str]]]"""

    def _write_md(self, tmp_path: Path, content: str) -> Path:
        md = tmp_path / "test.md"
        md.write_text(content, encoding="utf-8")
        return md

    def test_single_entry(self, tmp_path):
        """A single entry should produce one raw block."""
        md = self._write_md(tmp_path, "Aderesi (aderesi). Eng: Address. NK: Ikoranabuhanga rya mudasobwa. SH: Def\n")
        entries = load_and_reassemble(md)
        assert len(entries) == 1
        assert "Aderesi" in entries[0][0]

    def test_two_entries(self, tmp_path):
        """Two entries should produce two raw blocks."""
        content = (
            "Aderesi (aderesi). Eng: Address. NK: Ikoranabuhanga rya mudasobwa. SH: Def\n"
            "\n"
            "Bayiti (bayiti). Eng: Byte. NK: Ikoranabuhanga rya mudasobwa. SH: Def\n"
        )
        md = self._write_md(tmp_path, content)
        entries = load_and_reassemble(md)
        assert len(entries) == 2

    def test_multiline_entry_reassembled(self, tmp_path):
        """Entry spanning multiple lines should be reassembled into one block."""
        content = (
            "## Imbonezangiro (imbonezangiro)\n"
            "\n"
            "HI: Arugoritime. Eng: Algorithm. NK: Ikoranabuhanga rya mudasobwa. SH: Def\n"
        )
        md = self._write_md(tmp_path, content)
        entries = load_and_reassemble(md)
        assert len(entries) == 1
        assert "Imbonezangiro" in entries[0][0]
        assert "Algorithm" in entries[0][0]

    def test_noise_lines_filtered(self, tmp_path):
        """Page headers, numbers, and letter dividers should be filtered out."""
        content = (
            "Aderesi (aderesi). Eng: Address. NK: Ikoranabuhanga rya mudasobwa. SH: Def\n"
            "\n"
            "INKORANYAMUGA YIKORANABUHANGA\n"
            "\n"
            "99\n"
            "\n"
            "Bayiti (bayiti). Eng: Byte. NK: Ikoranabuhanga rya mudasobwa. SH: Def\n"
        )
        md = self._write_md(tmp_path, content)
        entries = load_and_reassemble(md)
        assert len(entries) == 2
        # Noise should not appear in reassembled text
        for text, _ in entries:
            assert "INKORANYAMUGA" not in text
            assert text.strip() != "99"

    def test_images_associated_with_entry(self, tmp_path):
        """Images should be associated with the current entry."""
        content = (
            "Aderesi (aderesi). Eng: Address. NK: Ikoranabuhanga rya mudasobwa. SH: Def\n"
            "\n"
            "![img-50.jpeg](img-50.jpeg)\n"
            "\n"
            "Bayiti (bayiti). Eng: Byte. NK: Ikoranabuhanga rya mudasobwa. SH: Def\n"
        )
        md = self._write_md(tmp_path, content)
        entries = load_and_reassemble(md)
        assert len(entries) == 2
        assert entries[0][1] == ["img-50.jpeg"]  # image on first entry
        assert entries[1][1] == []  # no image on second

    def test_field_marker_line_not_split(self, tmp_path):
        """A line starting with 'Eng:' should NOT be treated as a new entry."""
        content = (
            "## Imbonezanzira nyoherezamafishyye (imbonezanzira nyoherezamafishyye)\n"
            "\n"
            "Eng: File Transfer Protocol (FTP). Fr: Protocole. NK: Ikoranabuhanga rya murandasi. SH: Def\n"
        )
        md = self._write_md(tmp_path, content)
        entries = load_and_reassemble(md)
        assert len(entries) == 1
        assert "File Transfer Protocol" in entries[0][0]

    def test_front_matter_skipped(self, tmp_path):
        """Lines before the first real entry should be skipped."""
        content = (
            "# INTEKO Y'UMUCO\n"
            "RWANDA CULTURAL HERITAGE ACADEMY\n"
            "## Umwanditsi:\n"
            "Some front matter text\n"
            "\n"
            "Aderesi (aderesi). Eng: Address. NK: Ikoranabuhanga rya mudasobwa. SH: Def\n"
        )
        md = self._write_md(tmp_path, content)
        entries = load_and_reassemble(md)
        assert len(entries) == 1
        assert "Aderesi" in entries[0][0]
        assert "Umwanditsi" not in entries[0][0]


# ============================================================================
# merge_english_continuations
# ============================================================================

class TestMergeEnglishContinuations:
    """Tests for merge_english_continuations(entries) -> list[dict]"""

    def _make_entry(self, term, english="", french="", category="", definition="", images="[]"):
        return {
            "term": term,
            "pronunciation": "pron",
            "synonym": "",
            "english": english,
            "french": french,
            "category": category,
            "definition": definition,
            "images": images,
            "letter": term[0].upper(),
        }

    def test_no_merge_normal_entries(self):
        """Two normal Kinyarwanda entries should not merge."""
        entries = [
            self._make_entry("Aderesi", english="Address", category="Cat"),
            self._make_entry("Bayiti", english="Byte", category="Cat"),
        ]
        result = merge_english_continuations(entries)
        assert len(result) == 2

    def test_merge_english_continuation(self):
        """An English-only term with no english field but french should merge into previous."""
        entries = [
            self._make_entry("Indebero", english="Computer Screen; Video", category=""),
            self._make_entry("Graphics Array", english="", french="Ecran; moniteur", category="Ikoranabuhanga rya mudasobwa", definition="Igice kirambuye"),
        ]
        result = merge_english_continuations(entries)
        assert len(result) == 1
        assert "Graphics Array" in result[0]["english"]
        assert result[0]["french"] == "Ecran; moniteur"
        assert result[0]["category"] == "Ikoranabuhanga rya mudasobwa"
        assert result[0]["definition"] == "Igice kirambuye"

    def test_no_merge_if_has_english(self):
        """English-looking term WITH english field should NOT merge (it's a real entry)."""
        entries = [
            self._make_entry("Aderesi", english="Address"),
            self._make_entry("Bluetooth", english="Bluetooth", french="Bluetooth"),
        ]
        result = merge_english_continuations(entries)
        assert len(result) == 2

    def test_no_merge_if_no_french(self):
        """English-looking term with no french should NOT merge (insufficient signal)."""
        entries = [
            self._make_entry("Aderesi", english="Address"),
            self._make_entry("Graphics Array", english="", french=""),
        ]
        result = merge_english_continuations(entries)
        assert len(result) == 2

    def test_empty_list(self):
        """Empty list should return empty list."""
        assert merge_english_continuations([]) == []

    def test_single_entry(self):
        """Single entry should return as-is."""
        entries = [self._make_entry("Aderesi", english="Address")]
        result = merge_english_continuations(entries)
        assert len(result) == 1


# ============================================================================
# Database: init_db + seed_db
# ============================================================================

class TestDatabase:
    """Tests for init_db and seed_db."""

    def test_init_creates_tables(self):
        """init_db should create entries table, entries_fts, and index."""
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        # Check entries table exists
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_names = [t[0] for t in tables]
        assert "entries" in table_names
        assert "entries_fts" in table_names
        conn.close()

    def test_seed_inserts_entries(self):
        """seed_db should insert entries and populate FTS."""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        init_db(conn)
        entries = [{
            "term": "Aderesi",
            "pronunciation": "aderesi",
            "synonym": "",
            "english": "Address",
            "french": "Adresse",
            "category": "Ikoranabuhanga rya mudasobwa",
            "definition": "Def text",
            "images": "[]",
            "letter": "A",
        }]
        seed_db(conn, entries)
        count = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        assert count == 1
        # Check FTS
        fts_count = conn.execute("SELECT COUNT(*) FROM entries_fts").fetchone()[0]
        assert fts_count == 1
        conn.close()

    def test_seed_replaces_existing(self):
        """Running seed_db twice should replace, not duplicate."""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        init_db(conn)
        entries = [{
            "term": "Test", "pronunciation": "t", "synonym": "",
            "english": "T", "french": "T", "category": "C",
            "definition": "D", "images": "[]", "letter": "T",
        }]
        seed_db(conn, entries)
        seed_db(conn, entries)
        count = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        assert count == 1
        conn.close()


# ============================================================================
# Integration: full pipeline on real data
# ============================================================================

class TestIntegrationRealData:
    """Integration tests that run against the actual dictionary.db after parsing.

    These tests verify the parser produced correct results on the real source data.
    They read from /app/dictionary/backend/dictionary.db which must exist.
    """

    @pytest.fixture(autouse=True)
    def setup_db(self):
        db_path = Path(__file__).parent / "dictionary.db"
        if not db_path.exists():
            pytest.skip("dictionary.db not found — run parser.py first")
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        yield
        self.conn.close()

    def test_total_entries_in_range(self):
        """Should have ~1600 entries (between 1550 and 1650)."""
        total = self.conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        assert 1550 <= total <= 1650

    def test_no_front_matter_entry(self):
        """No entry should contain 'Umwanditsi: ###' or 'Uburenganzira bwose' in term."""
        rows = self.conn.execute(
            "SELECT id, term FROM entries WHERE term LIKE '%Umwanditsi: ###%' OR term LIKE '%Uburenganzira bwose%'"
        ).fetchall()
        assert len(rows) == 0, f"Front matter leak: {[dict(r) for r in rows]}"

    def test_first_entry_is_real(self):
        """Entry ID 1 should be a real dictionary entry (e.g. starts with A)."""
        row = self.conn.execute("SELECT term FROM entries WHERE id = 1").fetchone()
        assert row is not None
        assert row["term"][0].isalpha()
        assert len(row["term"]) < 100  # not a huge paragraph

    def test_no_eng_colon_terms(self):
        """No entry should have a term starting with 'Eng:'."""
        rows = self.conn.execute("SELECT id, term FROM entries WHERE term LIKE 'Eng:%'").fetchall()
        assert len(rows) == 0, f"Found Eng: terms: {[dict(r) for r in rows]}"

    def test_no_entries_all_empty(self):
        """No entry should have ALL of english, french, and definition empty."""
        rows = self.conn.execute("""
            SELECT id, term FROM entries
            WHERE (english IS NULL OR english = '')
            AND (french IS NULL OR french = '')
            AND (definition IS NULL OR definition = '')
        """).fetchall()
        assert len(rows) == 0, f"Empty entries: {[dict(r) for r in rows]}"

    def test_categories_count_under_20(self):
        """Should have fewer than 20 distinct categories (was 61 before fix)."""
        count = self.conn.execute(
            "SELECT COUNT(DISTINCT category) FROM entries WHERE category != ''"
        ).fetchone()[0]
        assert count <= 20, f"Too many categories: {count}"

    def test_no_markdown_in_categories(self):
        """No category should contain markdown asterisks."""
        rows = self.conn.execute(
            "SELECT DISTINCT category FROM entries WHERE category LIKE '%*%'"
        ).fetchall()
        assert len(rows) == 0, f"Markdown in categories: {[r['category'] for r in rows]}"

    def test_no_smart_quotes_in_categories(self):
        """No category should contain smart quotes (U+2018/U+2019)."""
        rows = self.conn.execute(
            "SELECT DISTINCT category FROM entries WHERE category LIKE '%\u2019%' OR category LIKE '%\u2018%'"
        ).fetchall()
        assert len(rows) == 0, f"Smart quotes in categories: {[r['category'] for r in rows]}"

    def test_no_semicolon_duplicated_categories(self):
        """No category should contain semicolons (deduplicated or multi-cat handled)."""
        rows = self.conn.execute(
            "SELECT DISTINCT category FROM entries WHERE category LIKE '%;%'"
        ).fetchall()
        assert len(rows) == 0, f"Semicolons in categories: {[r['category'] for r in rows]}"

    def test_no_leaked_definitions_in_categories(self):
        """No category should contain '. SH' or '. Inshoza' (leaked definitions)."""
        rows = self.conn.execute(
            "SELECT DISTINCT category FROM entries WHERE category LIKE '%. SH%' OR category LIKE '%. Inshoza%'"
        ).fetchall()
        assert len(rows) == 0, f"Leaked definitions in categories: {[r['category'] for r in rows]}"

    def test_videwo_entry_clean(self):
        """Videwo should have english='Video' (not virus data merged in)."""
        row = self.conn.execute("SELECT english FROM entries WHERE term = 'Videwo'").fetchone()
        assert row is not None
        assert row["english"] == "Video"

    def test_virusi_entries_separate(self):
        """There should be at least 10 separate Virusi entries."""
        count = self.conn.execute("SELECT COUNT(*) FROM entries WHERE term LIKE 'Virusi%'").fetchone()[0]
        assert count >= 10, f"Only {count} Virusi entries — some may still be merged"

    def test_virusi_base_entry_exists(self):
        """'Virusi' (the base entry) should exist with english='Computer virus'."""
        row = self.conn.execute("SELECT english FROM entries WHERE term = 'Virusi'").fetchone()
        assert row is not None
        assert "Computer virus" in row["english"]

    def test_imbonezangiro_has_content(self):
        """Imbonezangiro should have english='Algorithm' (was empty before fix)."""
        row = self.conn.execute("SELECT english FROM entries WHERE term = 'Imbonezangiro'").fetchone()
        assert row is not None
        assert "Algorithm" in row["english"]

    def test_imbonezamirimo_ya_mudasobwa_has_content(self):
        """Imbonezamirimo ya mudasobwa should have english='Computer system'."""
        row = self.conn.execute(
            "SELECT english FROM entries WHERE term = 'Imbonezamirimo ya mudasobwa'"
        ).fetchone()
        assert row is not None
        assert "Computer system" in row["english"]

    def test_zetabayiti_has_category(self):
        """Zetabayiti should have a category (was empty before fix due to NK leak)."""
        row = self.conn.execute("SELECT category FROM entries WHERE term = 'Zetabayiti'").fetchone()
        assert row is not None
        assert row["category"] != ""

    def test_no_nk_leak_in_french(self):
        """No entry should have '. NK' in its french field."""
        rows = self.conn.execute(
            "SELECT id, term, french FROM entries WHERE french LIKE '%. NK%'"
        ).fetchall()
        assert len(rows) == 0, f"NK leak in french: {[(r['id'], r['term']) for r in rows]}"

    def test_no_fr_leak_in_english(self):
        """No entry should have '. fr:' (lowercase) in its english field."""
        rows = self.conn.execute(
            "SELECT id, term, english FROM entries WHERE english LIKE '%. fr:%'"
        ).fetchall()
        assert len(rows) == 0, f"fr: leak in english: {[(r['id'], r['term']) for r in rows]}"

    def test_all_images_valid_json(self):
        """Every entry's images field should be valid JSON array."""
        rows = self.conn.execute("SELECT id, term, images FROM entries").fetchall()
        for r in rows:
            try:
                parsed = json.loads(r["images"])
                assert isinstance(parsed, list), f"ID {r['id']}: images is not a list"
            except json.JSONDecodeError:
                pytest.fail(f"ID {r['id']} ({r['term']}): invalid JSON in images: {r['images'][:50]}")

    def test_all_entries_have_letter(self):
        """Every entry should have a single uppercase letter."""
        rows = self.conn.execute("SELECT id, term, letter FROM entries WHERE length(letter) != 1").fetchall()
        assert len(rows) == 0

    def test_letter_matches_term(self):
        """Every entry's letter should match the first character of its term (uppercase)."""
        rows = self.conn.execute(
            "SELECT id, term, letter FROM entries WHERE UPPER(SUBSTR(term, 1, 1)) != letter"
        ).fetchall()
        assert len(rows) == 0, f"Letter mismatch: {[(r['id'], r['term'], r['letter']) for r in rows[:5]]}"

    def test_fts_populated(self):
        """FTS index should have the same number of rows as entries."""
        entry_count = self.conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        fts_count = self.conn.execute("SELECT COUNT(*) FROM entries_fts").fetchone()[0]
        assert fts_count == entry_count
