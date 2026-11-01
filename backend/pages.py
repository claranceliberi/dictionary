"""Readable word URLs and server-rendered word pages.

A word lives at /ijambo/<id>-<slug>, e.g. /ijambo/1158-mubitsi. The id makes
it unique (14 headwords repeat with different meanings); the slug makes it
readable. The page sent for that URL carries the entry as plain HTML, meta
tags and schema.org data, so link previews, search engines and AI tools that
don't run JavaScript still see the word and its meaning.
"""
import html
import json
import re
import unicodedata

SITE_NAME = "Inkoranyamuga y'Ikoranabuhanga"


def slugify(text: str) -> str:
    folded = unicodedata.normalize("NFD", text or "")
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch)).lower()
    folded = folded.replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", "-", folded).strip("-")


def entry_path(entry: dict) -> str:
    return f"{entry['id']}-{slugify(entry['term'])}"


def _clean(text: str) -> str:
    return (text or "").replace("**", "").strip()


def _main_term(text: str) -> str:
    return _clean(text).split(";")[0].strip()


def render_entry_page(index_html: str, entry: dict, base_url: str) -> str:
    """index.html with the entry's title, meta tags, structured data and text filled in."""
    e = html.escape  # attribute values
    t = lambda s: html.escape(s, quote=False)  # text content
    url = f"{base_url}/ijambo/{entry_path(entry)}"
    term = _clean(entry["term"])
    english = _main_term(entry.get("english"))
    definition = _clean(entry.get("definition"))
    heading = f"{term} — {english}" if english else term
    image = f"{base_url}/images/{entry['images'][0]}" if entry.get("images") else f"{base_url}/apple-touch-icon.png"

    data = {
        "@context": "https://schema.org",
        "@type": "DefinedTerm",
        "name": term,
        "description": definition,
        "inLanguage": "rw",
        "url": url,
        "alternateName": [t for t in (english, _main_term(entry.get("french"))) if t],
        "inDefinedTermSet": {"@type": "DefinedTermSet", "name": SITE_NAME, "url": base_url + "/"},
    }
    # "</" inside JSON would close the script tag early
    ld_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

    head = "\n".join([
        f'  <meta name="description" content="{e(definition[:200])}" />',
        f'  <link rel="canonical" href="{e(url)}" />',
        f'  <meta property="og:type" content="article" />',
        f'  <meta property="og:site_name" content="{e(SITE_NAME)}" />',
        f'  <meta property="og:title" content="{e(heading)}" />',
        f'  <meta property="og:description" content="{e(definition[:200])}" />',
        f'  <meta property="og:url" content="{e(url)}" />',
        f'  <meta property="og:image" content="{e(image)}" />',
        '  <meta name="twitter:card" content="summary" />',
        f'  <script type="application/ld+json">{ld_json}</script>',
    ])

    rows = [
        ("Impuzanyito", _clean(entry.get("synonym"))),
        ("Icyongereza", _clean(entry.get("english"))),
        ("Igifaransa", _clean(entry.get("french"))),
        ("Igitsibo", _clean(entry.get("category"))),
    ]
    fields = "".join(f"<dt>{t(k)}</dt><dd>{t(v)}</dd>" for k, v in rows if v)
    pron = f"<p>({t(_clean(entry.get('pronunciation')))})</p>" if entry.get("pronunciation") else ""
    body = (
        f'<article class="prerender"><h1>{t(term)}</h1>{pron}'
        f"<p>{t(definition)}</p><dl>{fields}</dl></article>"
    )

    page = re.sub(r"<title>.*?</title>", lambda _: f"<title>{t(heading)} | {t(SITE_NAME)}</title>", index_html, count=1, flags=re.S)
    page = page.replace("</head>", head + "\n</head>", 1)
    return page.replace('<div id="app"></div>', f'<div id="app">{body}</div>', 1)


def sitemap_xml(entries: list, base_url: str) -> str:
    urls = [f"{base_url}/", f"{base_url}/uko-wasoma"]
    urls += [f"{base_url}/ijambo/{entry_path(x)}" for x in entries]
    items = "".join(f"<url><loc>{html.escape(u)}</loc></url>" for u in urls)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{items}</urlset>'
    )
