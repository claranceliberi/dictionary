import json
import re

from pages import entry_path, render_entry_page, sitemap_xml, slugify

INDEX = """<!DOCTYPE html>
<html lang="rw">
<head>
  <meta charset="UTF-8" />
  <title>Inkoranyamuga y'Ikoranabuhanga</title>
</head>
<body>
  <div id="app"></div>
</body>
</html>"""

# entry 1158 as stored, with a ** marker added to check it is stripped
MUBITSI = {
    "id": 1158, "term": "Mubitsi", "pronunciation": "mubīitsi", "synonym": "",
    "english": "**C drive**; Filing Cabinet", "french": "Disque C; armoire de classement",
    "category": "Ikoranabuhanga rya mudasobwa",
    "definition": "Ahantu nyamukuru ho kubika amakuru muri mudasobwa", "images": [], "letter": "M",
}
BASE = "https://dict.clarance.me"


def test_slugify_makes_lowercase_ascii_words_joined_by_hyphens():
    assert slugify("Mubitsi") == "mubitsi"
    assert slugify("Abagarutse kuri murandasi") == "abagarutse-kuri-murandasi"


def test_slugify_drops_tone_marks_and_apostrophes():
    assert slugify("Mudâsobwâ ya Mac") == "mudasobwa-ya-mac"
    assert slugify("Umutekano w'amakuru") == "umutekano-wamakuru"
    assert slugify("Umutekano w’amakuru") == "umutekano-wamakuru"


def test_slugify_collapses_punctuation():
    assert slugify("  Wi-Fi (Ihuzanzira)  ") == "wi-fi-ihuzanzira"


def test_entry_path_puts_the_id_first():
    assert entry_path(MUBITSI) == "1158-mubitsi"


def page():
    return render_entry_page(INDEX, MUBITSI, BASE)


def test_page_title_names_the_word_and_its_english():
    assert re.search(r"<title>Mubitsi — C drive \| Inkoranyamuga y'Ikoranabuhanga</title>", page())


def test_page_has_description_canonical_and_open_graph():
    html = page()
    assert '<meta name="description" content="Ahantu nyamukuru ho kubika amakuru muri mudasobwa"' in html
    assert '<link rel="canonical" href="https://dict.clarance.me/ijambo/1158-mubitsi"' in html
    assert '<meta property="og:title" content="Mubitsi — C drive"' in html
    assert '<meta property="og:url" content="https://dict.clarance.me/ijambo/1158-mubitsi"' in html


def test_page_has_defined_term_structured_data():
    data = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', page(), re.S).group(1))
    assert data["@type"] == "DefinedTerm"
    assert data["name"] == "Mubitsi"
    assert data["inLanguage"] == "rw"
    assert data["url"] == "https://dict.clarance.me/ijambo/1158-mubitsi"
    assert "C drive" in data["alternateName"]


def test_page_puts_the_entry_text_inside_the_app_root_for_readers_without_js():
    app = re.search(r'<div id="app">(.*?)</div>\s*</body>', page(), re.S).group(1)
    assert "<h1>Mubitsi</h1>" in app
    assert "Ahantu nyamukuru" in app
    assert "C drive; Filing Cabinet" in app
    assert "*" not in app


def test_page_escapes_entry_text():
    evil = dict(MUBITSI, term='<script>alert(1)</script>', definition='"></meta><script>x</script>')
    html = render_entry_page(INDEX, evil, BASE)
    assert "<script>alert(1)</script>" not in html
    assert "<script>x</script>" not in html


def test_sitemap_lists_every_word_page():
    xml = sitemap_xml([MUBITSI, dict(MUBITSI, id=1140, term="Mikoro")], BASE)
    assert xml.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert "<loc>https://dict.clarance.me/ijambo/1158-mubitsi</loc>" in xml
    assert "<loc>https://dict.clarance.me/ijambo/1140-mikoro</loc>" in xml
    assert "<loc>https://dict.clarance.me/</loc>" in xml
