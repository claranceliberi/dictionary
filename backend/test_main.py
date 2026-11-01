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
    (dist / "index.html").write_text("<!doctype html><title>t</title>")
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


def test_api_responses_are_left_alone(client):
    r = client.get("/api/stats")
    assert r.status_code == 200
    assert "cache-control" not in r.headers
