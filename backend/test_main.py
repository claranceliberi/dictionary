import sys

import pytest
from fastapi.testclient import TestClient

NO_CACHE = "no-cache"
IMMUTABLE = "public, max-age=31536000, immutable"


@pytest.fixture
def client(tmp_path, monkeypatch):
    """The app serving a small fake frontend build from a temporary dist/."""
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text(
        "<!doctype html><html><head><title>t</title></head><body><div id=\"app\"></div></body></html>"
    )
    (dist / "assets" / "index-abc123.js").write_text("console.log(1)")
    (dist / "favicon.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>")
    (tmp_path / "secret.txt").write_text("SECRET-OUTSIDE-DIST")
    monkeypatch.setenv("DIST_DIR", str(dist))
    sys.modules.pop("main", None)  # DIST_DIR is read at import time
    import main
    return TestClient(main.app)


@pytest.mark.parametrize("path", ["/", "/browse/M", "/entry/1140", "/uko-wasoma"])
def test_html_pages_are_revalidated_on_every_visit(client, path):
    r = client.get(path)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    assert r.headers["cache-control"] == NO_CACHE


def test_hashed_assets_are_cached_for_a_year(client):
    r = client.get("/assets/index-abc123.js")
    assert r.status_code == 200
    assert r.headers["cache-control"] == IMMUTABLE


def test_unhashed_public_files_are_revalidated(client):
    r = client.get("/favicon.svg")
    assert r.status_code == 200
    assert r.headers["cache-control"] == NO_CACHE


@pytest.mark.parametrize("path", ["/..%2Fsecret.txt", "/%2E%2E/secret.txt", "/..%2F..%2Fetc%2Fpasswd", "/%2E%2E%2Fsecret.txt"])
def test_files_outside_the_build_are_never_served(client, path):
    r = client.get(path)
    assert "SECRET-OUTSIDE-DIST" not in r.text
    assert "root:" not in r.text
    # anything that isn't a real file in dist/ falls back to the app shell
    assert r.headers["content-type"].startswith("text/html")


def test_entries_carry_their_readable_path(client):
    assert client.get("/api/entries/1158").json()["slug"] == "1158-mubitsi"
    assert all("slug" in e for e in client.get("/api/entries", params={"letter": "M"}).json()["entries"])


def test_word_page_is_served_with_the_entry_filled_in(client):
    r = client.get("/ijambo/1158-mubitsi")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    assert r.headers["cache-control"] == NO_CACHE
    assert "<h1>Mubitsi</h1>" in r.text
    assert 'rel="canonical" href="https://dict.clarance.me/ijambo/1158-mubitsi"' in r.text


@pytest.mark.parametrize("path", ["/ijambo/1158", "/ijambo/1158-wrong-name", "/entry/1158"])
def test_other_addresses_for_a_word_redirect_to_its_readable_url(client, path):
    r = client.get(path, follow_redirects=False)
    assert r.status_code == 301
    assert r.headers["location"] == "/ijambo/1158-mubitsi"


@pytest.mark.parametrize("path", ["/ijambo/999999-nta", "/ijambo/mubitsi", "/entry/999999"])
def test_unknown_words_get_the_app_shell_with_404(client, path):
    r = client.get(path, follow_redirects=False)
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("text/html")


def test_sitemap_lists_all_words(client):
    r = client.get("/sitemap.xml")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/xml")
    assert r.text.count("/ijambo/") == client.get("/api/stats").json()["total_entries"]


def test_robots_points_to_the_sitemap(client):
    r = client.get("/robots.txt")
    assert "Sitemap: https://dict.clarance.me/sitemap.xml" in r.text


def test_api_responses_are_left_alone(client):
    r = client.get("/api/stats")
    assert r.status_code == 200
    assert "cache-control" not in r.headers


def test_search_accepts_the_longest_real_value(client):
    import database
    conn = database.get_db()
    longest = conn.execute(
        "SELECT MAX(MAX(LENGTH(term)), MAX(LENGTH(english)), MAX(LENGTH(french))) FROM entries"
    ).fetchone()[0]
    conn.close()
    assert longest <= 256
    assert client.get("/api/search", params={"q": "a" * 256}).status_code == 200


def test_search_rejects_oversized_queries(client):
    r = client.get("/api/search", params={"q": "ijambo " * 1000})
    assert r.status_code == 422


BAD_IDS = ["99999999999999999999", str(2**63), "0", "²", "١٢", "１２", "-1", "1e3"]


@pytest.mark.parametrize("entry_id", BAD_IDS)
def test_invalid_or_oversized_ids_are_not_found(client, entry_id):
    assert client.get(f"/api/entries/{entry_id}").status_code == 404
    assert client.get(f"/entry/{entry_id}", follow_redirects=False).status_code == 404
    assert client.get(f"/ijambo/{entry_id}", follow_redirects=False).status_code == 404
    assert client.get(f"/ijambo/{entry_id}-nta", follow_redirects=False).status_code == 404


def test_largest_int64_id_is_a_plain_404(client):
    assert client.get(f"/api/entries/{2**63 - 1}").status_code == 404


@pytest.mark.parametrize("path", ["/api/entries", "/api/search?q=a"])
def test_huge_page_numbers_are_rejected(client, path):
    sep = "&" if "?" in path else "?"
    assert client.get(f"{path}{sep}page=99999999999999999999").status_code == 422


@pytest.mark.parametrize("path", ["/docs", "/redoc", "/openapi.json"])
def test_api_docs_are_off_by_default(client, path):
    r = client.get(path)
    assert "swagger-ui" not in r.text and "redoc" not in r.text
    assert not r.headers["content-type"].startswith("application/json")


def test_api_docs_can_be_turned_on_for_development(tmp_path, monkeypatch):
    monkeypatch.setenv("ENABLE_API_DOCS", "1")
    monkeypatch.setenv("DIST_DIR", str(tmp_path / "no-dist"))
    sys.modules.pop("main", None)
    import main
    c = TestClient(main.app)
    assert c.get("/openapi.json").status_code == 200
    assert c.get("/docs").status_code == 200
