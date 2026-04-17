import json
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from database import get_db

app = FastAPI(title="Inkoranyamuga y'Ikoranabuhanga")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

BASE_DIR   = Path(__file__).parent.parent
IMAGES_DIR = BASE_DIR / "images"
DIST_DIR   = BASE_DIR / "dist"

app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")


def row_to_dict(row) -> dict:
    d = dict(row)
    if d.get("images"):
        try:
            d["images"] = json.loads(d["images"])
        except Exception:
            d["images"] = []
    else:
        d["images"] = []
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
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
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
    page: int = Query(1, ge=1),
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
def get_entry(entry_id: int):
    """Get a single entry by ID."""
    conn = get_db()
    row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Entry not found")
    return row_to_dict(row)


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
if DIST_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(DIST_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str):
        candidate = DIST_DIR / full_path
        if candidate.exists() and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(DIST_DIR / "index.html")
