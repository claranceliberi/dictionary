import json
import os
import re
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from database import get_db
from pages import entry_path, render_entry_page, sitemap_xml

# The interactive API docs load swagger-ui/redoc from a CDN by floating tag, so
# they are off unless ENABLE_API_DOCS=1 (for local development only).
API_DOCS = os.environ.get("ENABLE_API_DOCS") == "1"
app = FastAPI(
    title="Inkoranyamuga y'Ikoranabuhanga",
    docs_url="/docs" if API_DOCS else None,
    redoc_url="/redoc" if API_DOCS else None,
    openapi_url="/openapi.json" if API_DOCS else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)
# The JS bundle and search results compress to about a third of their size.
app.add_middleware(GZipMiddleware, minimum_size=1024)

# API data and images only change when a new image is built and deployed, so
# browsers may reuse them for an hour (and serve a stale copy for a day while
# they refetch) instead of waiting a round trip on every page load.
DATA_CACHE = "public, max-age=3600, stale-while-revalidate=86400"


@app.middleware("http")
async def cache_data_responses(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if (
        request.method in ("GET", "HEAD")
        and response.status_code == 200
        and (path.startswith("/api/") or path.startswith("/images/"))
        and "cache-control" not in response.headers
    ):
        response.headers["Cache-Control"] = DATA_CACHE
    return response

BASE_DIR   = Path(__file__).parent.parent
IMAGES_DIR = BASE_DIR / "images"
DIST_DIR   = Path(os.environ.get("DIST_DIR", BASE_DIR / "dist"))
# Absolute site address for canonical links, link previews and the sitemap.
PUBLIC_URL = os.environ.get("PUBLIC_URL", "https://dict.clarance.me").rstrip("/")

app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")


# Largest id SQLite can store (signed 64-bit). Anything bigger, or anything that
# isn't plain ASCII digits ("²", "１２"), is simply not a word: 404, not a 500.
MAX_ID = 2**63 - 1
RE_ID = re.compile(r"[0-9]{1,19}")
# Pages beyond this are always empty; the cap keeps OFFSET inside int64.
MAX_PAGE = 100_000


def parse_entry_id(text: str) -> int | None:
    if not RE_ID.fullmatch(text):
        return None
    entry_id = int(text)
    return entry_id if 1 <= entry_id <= MAX_ID else None


def row_to_dict(row) -> dict:
    d = dict(row)
    if d.get("images"):
        try:
            d["images"] = json.loads(d["images"])
        except Exception:
            d["images"] = []
    else:
        d["images"] = []
    d["slug"] = entry_path(d)
    return d


@app.get("/api/letters")
def get_letters():
    """Return letters with entry counts."""
    conn = get_db()
    rows = conn.execute(
        "SELECT letter, COUNT(*) as count FROM entries GROUP BY letter ORDER BY letter"
    ).fetchall()
    conn.close()
    return [{"letter": r["letter"], "count": r["count"]} for r in rows]


@app.get("/api/categories")
def get_categories():
    """Return categories with entry counts."""
    conn = get_db()
    rows = conn.execute(
        """SELECT category, COUNT(*) as count FROM entries
           WHERE category != '' GROUP BY category ORDER BY count DESC"""
    ).fetchall()
    conn.close()
    return [{"name": r["category"], "count": r["count"]} for r in rows]


@app.get("/api/search")
def search_entries(
    # The longest real value is 227 characters (a French gloss), so 256 lets any
    # pasted term through while capping the cost of the FTS phrase query.
    q: str = Query(..., min_length=1, max_length=256),
    page: int = Query(1, ge=1, le=MAX_PAGE),
    per_page: int = Query(30, ge=1, le=100),
):
    """FTS5 trilingual search."""
    conn = get_db()
    offset = (page - 1) * per_page

    # Escape FTS5 special characters
    safe_q = q.replace('"', '""')
    fts_query = f'"{safe_q}"*'

    try:
        rows = conn.execute(
            """SELECT e.*, bm25(entries_fts, 10.0, 5.0, 5.0, 1.0, 3.0) as rank
               FROM entries_fts
               JOIN entries e ON entries_fts.rowid = e.id
               WHERE entries_fts MATCH ?
               ORDER BY rank
               LIMIT ? OFFSET ?""",
            (fts_query, per_page, offset),
        ).fetchall()
        total = conn.execute(
            "SELECT COUNT(*) FROM entries_fts WHERE entries_fts MATCH ?",
            (fts_query,),
        ).fetchone()[0]
    except Exception:
        # Fallback to LIKE search if FTS fails (e.g. empty/invalid query)
        like = f"%{q}%"
        rows = conn.execute(
            """SELECT * FROM entries
               WHERE term LIKE ? OR english LIKE ? OR french LIKE ? OR definition LIKE ?
               LIMIT ? OFFSET ?""",
            (like, like, like, like, per_page, offset),
        ).fetchall()
        total = conn.execute(
            """SELECT COUNT(*) FROM entries
               WHERE term LIKE ? OR english LIKE ? OR french LIKE ? OR definition LIKE ?""",
            (like, like, like, like),
        ).fetchone()[0]

    conn.close()
    return {
        "results": [row_to_dict(r) for r in rows],
        "total": total,
        "page": page,
        "per_page": per_page,
        "q": q,
    }


@app.get("/api/entries")
def list_entries(
    letter: str = Query(None, min_length=1, max_length=1),
    page: int = Query(1, ge=1, le=MAX_PAGE),
    per_page: int = Query(50, ge=1, le=200),
):
    """Browse entries by letter."""
    conn = get_db()
    offset = (page - 1) * per_page

    if letter:
        rows = conn.execute(
            """SELECT * FROM entries WHERE letter = ?
               ORDER BY term COLLATE NOCASE LIMIT ? OFFSET ?""",
            (letter.upper(), per_page, offset),
        ).fetchall()
        total = conn.execute(
            "SELECT COUNT(*) FROM entries WHERE letter = ?",
            (letter.upper(),),
        ).fetchone()[0]
    else:
        rows = conn.execute(
            "SELECT * FROM entries ORDER BY letter, term COLLATE NOCASE LIMIT ? OFFSET ?",
            (per_page, offset),
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]

    conn.close()
    return {
        "entries": [row_to_dict(r) for r in rows],
        "total": total,
        "page": page,
        "per_page": per_page,
        "letter": letter,
    }


@app.get("/api/entries/{entry_id}")
def get_entry(entry_id: str):
    """Get a single entry by ID."""
    entry = find_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@app.get("/api/stats")
def get_stats():
    """Overall dictionary stats."""
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    with_images = conn.execute(
        "SELECT COUNT(*) FROM entries WHERE images != '[]'"
    ).fetchone()[0]
    conn.close()
    return {"total_entries": total, "entries_with_images": with_images}


# ── Vue SPA fallback ──────────────────────────────────────────────────────────
# Must be defined AFTER all API routes so it only catches unmatched paths.
# Serves static assets directly; everything else gets index.html for Vue Router.
#
# Caching: Vite puts a content hash in every /assets/* filename, so those can be
# cached for a year. index.html and the unhashed files next to it (favicons)
# keep the same URL across deploys, so browsers must revalidate them each time
# (a cheap 304 when nothing changed); otherwise they show the old UI after a deploy.
NO_CACHE  = {"Cache-Control": "no-cache"}
IMMUTABLE = "public, max-age=31536000, immutable"


class HashedAssets(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 200:
            response.headers["Cache-Control"] = IMMUTABLE
        return response


def find_entry(text: str):
    """The entry whose id is spelled `text`, or None for unknown or invalid ids."""
    entry_id = parse_entry_id(text)
    if entry_id is None:
        return None
    conn = get_db()
    row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    conn.close()
    return row_to_dict(row) if row else None


@app.get("/sitemap.xml", include_in_schema=False)
def sitemap():
    conn = get_db()
    rows = conn.execute("SELECT id, term FROM entries ORDER BY id").fetchall()
    conn.close()
    return Response(sitemap_xml([dict(r) for r in rows], PUBLIC_URL), media_type="application/xml")


@app.get("/robots.txt", include_in_schema=False)
def robots():
    return PlainTextResponse(f"User-agent: *\nAllow: /\nSitemap: {PUBLIC_URL}/sitemap.xml\n")


if DIST_DIR.exists():
    app.mount("/assets", HashedAssets(directory=str(DIST_DIR / "assets")), name="assets")

    DIST_ROOT = DIST_DIR.resolve()

    def app_shell(status_code: int = 200) -> HTMLResponse:
        return HTMLResponse((DIST_ROOT / "index.html").read_text(), status_code=status_code, headers=NO_CACHE)

    # Word pages: /ijambo/<id>-<slug>. Any other spelling of the address, and the
    # old /entry/<id> links, redirect permanently to the readable one.
    @app.get("/ijambo/{word}", include_in_schema=False)
    def word_page(word: str):
        match = re.match(r"([0-9]+)(?:-|$)", word)
        entry = find_entry(match.group(1)) if match else None
        if not entry:
            return app_shell(404)
        if word != entry["slug"]:
            return RedirectResponse(f"/ijambo/{entry['slug']}", status_code=301)
        index_html = (DIST_ROOT / "index.html").read_text()
        return HTMLResponse(render_entry_page(index_html, entry, PUBLIC_URL), headers=NO_CACHE)

    @app.get("/entry/{entry_id}", include_in_schema=False)
    def old_entry_link(entry_id: str):
        entry = find_entry(entry_id)
        if not entry:
            return app_shell(404)
        return RedirectResponse(f"/ijambo/{entry['slug']}", status_code=301)

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str):
        # full_path arrives URL-decoded, so "..%2F" becomes "../": resolve it and
        # only serve files that are really inside the build.
        candidate = (DIST_ROOT / full_path).resolve()
        if candidate.is_relative_to(DIST_ROOT) and candidate.is_file():
            return FileResponse(candidate, headers=NO_CACHE)
        return FileResponse(DIST_ROOT / "index.html", headers=NO_CACHE)
