# Book-style Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle the Vue frontend to match the printed *Inkoranyamuga y'Ikoranabuhanga*. The interface is all Kinyarwanda, definitions come first, and there is a new `/uko-wasoma` guide page.

**Architecture:**
- Replace Tailwind with plain CSS: theme tokens on `:root`/`[data-theme="dark"]` in `src/style.css`, and per-component `<style scoped>`.
- All entry text formatting goes through one pure module, `src/format.js`, which is unit-tested with Vitest.
- The backend, API and routes are unchanged, apart from the added `/uko-wasoma` route.

**Tech Stack:** Vue 3 (Options API, as in the existing code), vue-router 4, axios, Vite 5, Vitest + @vue/test-utils + jsdom (dev only).

**Spec:** `docs/superpowers/specs/2026-11-01-book-style-redesign-design.md`. The visual reference is `docs/superpowers/specs/2026-11-01-book-style-redesign-mockup.html`. Its CSS and markup are the source to port; open it and copy its values rather than re-deriving them.

## Global Constraints

- All UI strings are Kinyarwanda, copied verbatim from the spec or mockup. English and French appear only as entry data.
- Use "amagambo", never "amajambo".
- Fonts:
  - Montserrat 500/600/700/800 and Bodoni Moda 900 from Google Fonts, with `display=swap`;
  - reading text uses `"Palatino Linotype", "Book Antiqua", Palatino, "Noto Serif", Georgia, serif`.
- Colour tokens are exactly the spec's table (light and dark). On blue or green fills in dark mode, text is `#0E1B2B`.
- The theme is stored in localStorage key `rw-dark-mode` (`'true'`/`'false'`) and applied as `document.documentElement.dataset.theme = 'dark'|'light'`.
- No emoji, no shimmer skeletons, no category colour pills, no internal `#id` shown.
- No new runtime dependencies. Dev dependencies: `vitest`, `@vue/test-utils`, `jsdom` only.
- Backend files are untouched. `pytest backend/test_parser.py` must stay green (122 tests).
- Commits are small. The PR is squash-merged, and only after the user's OK.

## Review Focus

1. **Entries with empty fields** (no synonym, French, image or pronunciation): no empty rows, no stray `()` or `;`. This is pinned in Task 1 (format) and Task 5 (EntryCard).
2. **Letters with one page** (C, D, H, R and Y have one entry): no pager is rendered. **Letters with 20 pages** (I): windowed numbers. Pinned in Task 1 (`pageWindow`).
3. **Long translation lists** (entry 1143 *Mikoro yambarwa*) wrap cleanly at 375px. This is a manual check in Task 8.
4. **A saved `rw-dark-mode='true'` from the old app** still loads dark. Pinned in Task 3.
5. **Deep links** (`/uko-wasoma`, `/entry/1140`, `/browse/U`) load directly from the backend's SPA fallback. This is a manual check in Task 8, against `uvicorn`.

---

### Task 1: `format.js` + Vitest + CI

**Files:**
- Create: `frontend/src/format.js`, `frontend/src/format.test.js`
- Modify: `frontend/package.json` (add `"test": "vitest run"`, devDeps `vitest`, `@vue/test-utils`, `jsdom`), `frontend/vite.config.js` (`test: { environment: 'jsdom' }`), `.github/workflows/ci.yml` (in `build-frontend`, add a step `npm test` before Build)

**Interfaces — Produces:**
- `stripMarks(s?: string): string`: removes `**` and trims; `undefined`/`null` gives `''`.
- `splitTerms(s?: string): { main: string, rest: string[] }`: strips marks, splits on `;`, trims, and drops empty pieces.
- `splitSynonym(s?: string): { term: string, pron: string }`: splits on the first ` (` and drops the closing `)`.
- `pageWindow(current: number, total: number): (number|'…')[]`

- [ ] **Step 1: Write failing tests in `format.test.js`**

```js
expect(stripMarks('**Megabyte**')).toBe('Megabyte')
expect(stripMarks(undefined)).toBe('')
expect(splitTerms('**Macintoch**; Mac')).toEqual({ main: 'Macintoch', rest: ['Mac'] })
expect(splitTerms('Menu de démarrage; menu démarrer')).toEqual({ main: 'Menu de démarrage', rest: ['menu démarrer'] })
expect(splitTerms('Microphone')).toEqual({ main: 'Microphone', rest: [] })
expect(splitTerms('')).toEqual({ main: '', rest: [] })
expect(splitTerms('a;; b; ')).toEqual({ main: 'a', rest: ['b'] })
expect(splitSynonym('Indangururamajwi (indâangururamâjwi)')).toEqual({ term: 'Indangururamajwi', pron: 'indâangururamâjwi' })
expect(splitSynonym('**Mudasobwa ya Mac** (Mudâsobwâ ya maâki)')).toEqual({ term: 'Mudasobwa ya Mac', pron: 'Mudâsobwâ ya maâki' })
expect(splitSynonym('Indanga')).toEqual({ term: 'Indanga', pron: '' })
expect(splitSynonym('')).toEqual({ term: '', pron: '' })
expect(pageWindow(1, 1)).toEqual([])
expect(pageWindow(1, 2)).toEqual([1, 2])
expect(pageWindow(4, 7)).toEqual([1, 2, 3, 4, 5, 6, 7])
expect(pageWindow(1, 20)).toEqual([1, 2, '…', 20])
expect(pageWindow(10, 20)).toEqual([1, '…', 9, 10, 11, '…', 20])
expect(pageWindow(20, 20)).toEqual([1, '…', 19, 20])
```

- [ ] **Step 2:** Run `npm --prefix frontend test`. Expected: FAIL (module missing).
- [ ] **Step 3: Implement the four functions.** For `pageWindow`:
  - with `total <= 1`, return `[]`;
  - with `total <= 7`, return every page;
  - otherwise return `1`, `current-1..current+1` clamped to `[1,total]`, and `total`, with `'…'` wherever pages are skipped.
- [ ] **Step 4:** Run `npm --prefix frontend test`. Expected: all pass.
- [ ] **Step 5:** Commit: `feat(frontend): format helpers with tests`.

### Task 2: Style foundation (Tailwind out, tokens and fonts in)

**Files:**
- Delete: `frontend/tailwind.config.js`, `frontend/postcss.config.js`
- Modify:
  - `frontend/package.json`: remove `tailwindcss`, `postcss`, `autoprefixer`.
  - `frontend/index.html`: swap the Noto link for Montserrat and Bodoni Moda; keep `lang="rw"` and the title.
  - `frontend/src/style.css`: rewrite with the tokens, base `body` (`--bg`, `--ink`, reading font), a `:focus-visible` outline in `--blue`, and the shared classes `.wrap`, `.ttl`, `.runhead`, `.lb`, `.e` (list entry), `.meta`, `abbr` tooltip, ported from the mockup.
- Create: `frontend/src/components/Ribbon.vue`. Prop `orientation: 'v'|'h'`. It renders the mockup's `#zv`/`#zh` SVG patterns, with a unique pattern id per instance.

**Interfaces — Produces:**
- CSS classes `.wrap`, `.ttl`, `.runhead`, `.lb`, `.e`, `.meta`, and the CSS variables from the spec.
- `<Ribbon orientation="v|h" />`

- [ ] **Step 1:** Make the changes. The app will look unstyled where Tailwind classes remain; Tasks 3–7 replace them.
- [ ] **Step 2:** `npm --prefix frontend ci && npm --prefix frontend run build` succeeds, and `npm --prefix frontend test` still passes.
- [ ] **Step 3:** Commit: `refactor(frontend): replace Tailwind with theme tokens`.

### Task 3: App shell (header, footer, theme, shortcuts, routes)

**Files:**
- Modify: `frontend/src/App.vue`, `frontend/src/main.js` (add `{ path: '/uko-wasoma', component: GuideView }`; create a stub `GuideView.vue` that Task 7 fills in)
- Delete: `frontend/src/components/CommandPalette.vue`
- Test: `frontend/src/App.test.js`

**Interfaces — Consumes:** `Ribbon`, tokens. **Produces:**
- `App` passes `letters`, `stats` and `categories` to `<router-view>`. Categories now load once in App, not in HomeView.
- Header:
  - the wordmark;
  - `<SearchBar>`, hidden when `$route.path === '/'`;
  - an "Uko wasoma" link, desktop only;
  - a theme button labelled "Umwijima"/"Urumuri".
- The phone search row sits under the header.
- Footer: the spec's exact one-line text, with Clarance linking to `https://clarance.me` (`rel="author"`).
- `⌘K`/`Ctrl+K` and `/` (when not typing in an input) focus the header search input. They do nothing on `/`, where the home search is autofocused.
- The mobile drawer is gone.

- [ ] **Step 1: Write a failing test.** Mount `App` with a router and mocked axios, with `localStorage['rw-dark-mode'] = 'true'` set beforehand. Then:
  - assert `document.documentElement.dataset.theme === 'dark'`;
  - click the theme button and assert `localStorage['rw-dark-mode'] === 'false'` and `dataset.theme === 'light'`;
  - assert the footer link has `href === 'https://clarance.me'`.
- [ ] **Step 2:** Run `npm --prefix frontend test`. Expected: FAIL.
- [ ] **Step 3:** Implement the shell per the spec's Header and Footer sections and the mockup's `header` and `footer` CSS. With no saved value, the default comes from `prefers-color-scheme`, as today.
- [ ] **Step 4:** Tests pass and the build passes.
- [ ] **Step 5:** Commit: `feat(frontend): book-style header, footer and theme`.

### Task 4: SearchBar restyle

**Files:** Modify `frontend/src/components/SearchBar.vue`.

**Interfaces — Produces:**
- Props: `modelValue`, `size: 'md'|'lg'` (default `'md'`), `autofocus: boolean`.
- Exposes `focus()`, used by App's shortcuts.
- Emits `update:modelValue` and `search`.

- [ ] **Step 1:** Restyle to the mockup's `.search` (input plus a joined "Shakisha" button; `lg` uses the cover variant with a yellow button).
  - Keep the existing autocomplete, recent searches, keyboard navigation and `RECENT_KEY` behaviour.
  - Remove the custom × clear button and keep the native one, so the field no longer shows two.
  - Dropdown rows: Bodoni headword, muted pronunciation, and the English main term via `splitTerms`.
  - The recent-searches label stays "Byasakazwe vuba" and the clear action stays "Siba".
- [ ] **Step 2:** Build passes. In `npm --prefix frontend run dev` (with the backend running, or a proxy to `https://dict.clarance.me`), typing "mikoro" shows the dropdown, and Enter goes to `/search?q=mikoro`.
- [ ] **Step 3:** Commit: `feat(frontend): restyle search`.

### Task 5: List entry, pager, letter navigation, BrowseView

**Files:**
- Modify: `frontend/src/components/EntryCard.vue`, `frontend/src/components/LetterNav.vue`, `frontend/src/views/BrowseView.vue`
- Create: `frontend/src/components/Pager.vue`, `frontend/src/components/EntryCard.test.js`

**Interfaces — Consumes:** `splitTerms`, `splitSynonym`, `stripMarks`, `pageWindow`. **Produces:**
- `<EntryCard :entry :hide-image="false" />`: the mockup's `.e` markup. The headword links to `/entry/:id`. The `abbr` full names are HI → Impuzanyito, Eng → Icyongereza, Fr → Igifaransa, NK → "Igitsibo (ingeri y'ikoranabuhanga)".
- `<Pager :page :total-pages @go="(p:number)=>…" />`: renders nothing when `pageWindow` returns `[]`. The current page has `aria-current="page"`. Arrow labels are "Ipaji ibanza" and "Ipaji ikurikira".
- `<LetterNav :letters :active variant="tabs|strip|table" />`:
  - `tabs` is the desktop rail;
  - `strip` is the phone strip;
  - `table` is the home Ishakiro, with counts, hover arrow and caption-free markup.
  - The active letter has `aria-current="true"`.

- [ ] **Step 1: Write failing EntryCard tests.**
  - Entry 1138 data (synonym, two French terms, image) renders "Ingingo y'ihagurutsa" in `<b>`, "Menu de démarrage" in `<b>` followed by "; menu démarrer", and an `img` with `src="/images/img-116.jpeg"`.
  - An entry with `synonym: ''`, `french: ''`, `images: []` and `pronunciation: ''` renders no HI or Fr rows, no `img`, and no `()`.
  - `english: '**Megabyte**'` renders the text "Megabyte" without `*`.
- [ ] **Step 2:** Run them. Expected: FAIL.
- [ ] **Step 3:** Implement EntryCard, Pager and LetterNav, then rebuild BrowseView:
  - Remove the preview pane, the view toggle and the colour maps.
  - Heading: roundel + "Amagambo N" for letters, or "Ibisubizo bya “q”" + "Amagambo N" for search. The running head goes **below the Pager**, at the foot of the list, on letter pages only.
  - Loading shows "Gushakisha…".
  - Empty shows "Nta jambo ryabonetse", "Gerageza ijambo rindi cyangwa inyuguti" and a link home.
  - The page is 50 per page; `go` sets the page, refetches and scrolls to the top.
- [ ] **Step 4:** Tests and build pass.
- [ ] **Step 5:** Commit: `feat(frontend): book-style letter and search pages`.

### Task 6: Home and entry pages

**Files:** Modify `frontend/src/views/HomeView.vue` and `frontend/src/views/EntryView.vue`.

**Interfaces — Consumes:** `SearchBar size="lg" autofocus`, `LetterNav variant="table"`, `EntryCard hide-image`, `Ribbon`, `splitTerms`, `splitSynonym`, and the `categories`/`stats` props from App.

- [ ] **Step 1: Home** per the spec's Home section and the mockup:
  - the cover with "Gerageza" links to `/search?q=mudasobwa|imeri|murandasi|mikoro`;
  - the Ishakiro column with the caption "Inyuguti n'umubare w'amagambo";
  - the guide legend and "Soma ibisobanuro byose →" linking to `/uko-wasoma`;
  - the miniature page, which fetches `/api/entries/1140` and renders it via `EntryCard hide-image`, with an "M" marker;
  - Ibitsibo with dotted leaders. Clicking a category keeps today's behaviour: `/search?q=<last word of the category>`.
- [ ] **Step 2: Entry page** per the spec's Entry section:
  - breadcrumb, headword, pronunciation and image;
  - the "Inshoza" lead;
  - the field table, omitting empty rows;
  - actions "← Subira inyuma", "Kopa aderesi"/"Yakopwe" (2s) and "Andi magambo y'iki gitsibo →" (same category search as above);
  - not-found shows "Ijambo ntiryabonetse" plus a link home.
- [ ] **Step 3:** Build passes. In dev, `/` and `/entry/1140` match the mockup at 1280px and 375px in both themes.
- [ ] **Step 4:** Commit: `feat(frontend): book-style home and entry pages`.

### Task 7: Guide page `/uko-wasoma`

**Files:** Fill in `frontend/src/views/GuideView.vue`.

- [ ] **Step 1:** Port the mockup's `#s-guide` markup and its `.guide`, `.anno`, `.pin`, `.parts` and `.abbr-table` CSS verbatim, with all text exactly as in the mockup. The annotated example is static.
- [ ] **Step 2:** Build passes. `/uko-wasoma` matches the mockup at both widths and in both themes, and the header and footer "Uko wasoma" links reach it.
- [ ] **Step 3:** Commit: `feat(frontend): guide page`.

### Task 8: Verification, screenshots, PR

- [ ] **Step 1:** Run `npm --prefix frontend test` and `npm --prefix frontend run build`. Then run `python backend/parser.py && python -m pytest backend/test_parser.py -q`, using a venv with `backend/requirements.txt` and pytest. Expected: all green (122 backend tests).
- [ ] **Step 2:** Serve the built app through the backend (`uvicorn backend.main:app`, with `frontend/dist` where the Dockerfile puts it; read `backend/Dockerfile` for the path) and run these manual checks:
  - deep links `/uko-wasoma`, `/entry/1140` and `/browse/U` load directly;
  - `/browse/I` pages through all 20 pages with the windowed pager;
  - `/browse/C` shows no pager;
  - entry 1143 wraps cleanly at 375px;
  - theme persists after reload;
  - "Kopa aderesi" copies the URL.
- [ ] **Step 3: Screenshots.** Take before shots (dict.clarance.me) and after shots (local) of home, `/browse/M`, `/search?q=mikoro`, `/entry/1140` and `/uko-wasoma` (after only), at 1280px and 375px, light and dark. Save them to the shared notes folder, not the repo, and attach them to the PR.
- [ ] **Step 4:** Push `ui/book-redesign` and open one PR against `main`.
  - The body includes: the spec link, a summary, the removed features, the Kinyarwanda strings needing a native check, and the follow-ups (search ranking, category filter).
  - It ends with the attribution line.
  - Do not merge.
