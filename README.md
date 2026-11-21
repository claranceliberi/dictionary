# dictionary

Inkoranyamuga y'Ikoranabuhanga, the Kinyarwanda ICT dictionary, served at
https://dict.clarance.me. A FastAPI backend serves a JSON API, the word
pages and a Vue single-page app from one container.

## How content reaches the site

1. **Source text.** `content/Inkoranyamuga Ikoranabuhanga.pdf/pages/page-N/markdown.md`
   holds the OCR'd text of book page N, next to that page's images
   (`img-*.jpeg`). These per-page files are the only text source. To fix a
   typo, edit the page it is on.
2. **Parse.** `backend/parser.py` reads the pages in order, splits them into
   entries, copies the images to `images/` and writes `backend/dictionary.db`
   (SQLite with an FTS5 index).
3. **Build.** `backend/Dockerfile` runs the parser in stage 2 and bakes the
   database, the images and the built frontend into the image. The build
   fails if the entry count leaves the expected range (1550-1650) or if
   `test_parser.py` fails, including the id check below.
4. **Run.** The app opens `dictionary.db` read-only (`mode=ro&immutable=1`).
   Nothing writes to it at runtime. New content means a new image.

Deploys are driven from the k8s-homelab repo (`scripts/apps.tsv` pins the
commit that gets built).

## Word ids

Word URLs look like `/ijambo/1158-mubitsi`. The number comes from
`content/ids.tsv`, which maps every word ever published to its id. The key
is the slug of the term, with `~2`, `~3` and so on for repeated headwords.
Ids no longer depend on parse order, so adding, merging or removing an entry
does not renumber the others.

- New words get the next unused id. Run `python backend/parser.py --update-ids`
  and commit `content/ids.tsv`. CI and the image build fail until you do.
- When you correct a term's spelling, its key changes. To keep its URL,
  change the key on its line in `ids.tsv` to the new slug before running
  the parser. Otherwise it gets a new id and the old URL returns 404.
- Never reuse or renumber an id. Ids of removed words stay in the file so
  they are never handed out again.

## Development

```sh
# backend (Python 3.12)
pip install -r backend/requirements.txt -r backend/requirements-dev.txt
python backend/parser.py
python -m pytest backend/test_parser.py backend/test_main.py backend/test_pages.py
cd backend && ENABLE_API_DOCS=1 uvicorn main:app --reload   # /docs only with ENABLE_API_DOCS=1

# frontend (Node 22)
cd frontend && npm ci && npm test && npm run build
```

Python dependencies are locked with hashes. Edit `backend/requirements.in`
(or `requirements-dev.in`) and regenerate with the command in the lock
file's header. Renovate (`renovate.json`) proposes updates once a release
is 14 days old.
