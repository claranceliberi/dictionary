# Book-style redesign of the dictionary frontend

Date: 2026-11-01
Branch: `ui/book-redesign`
Visual reference: [`2026-11-01-book-style-redesign-mockup.html`](2026-11-01-book-style-redesign-mockup.html) (open in a browser; the bar at the top switches screen, theme and width).

## Goal

Replace the current generic look (green hero, bento cards, emoji icons, rainbow category pills) with a design that Rwandan readers recognise. It is modelled on the printed *Inkoranyamuga y'Ikoranabuhanga* (2026), which is where the 1,601 terms come from.

Success means:
- the UI reads like the book;
- every interface string is in Kinyarwanda;
- an entry's definition is the first thing a reader sees;
- the site works as well on a phone as on a desktop.

## Decided with the user

- Book-like reading style, not the editor style of the notes app.
- Green is not required. Use the book's palette: flag-colour zigzag (sky blue, yellow, green), cover blue, and the green field labels.
- Interface text is Kinyarwanda only. English and French appear only as the dictionary's own translations.
- A visible note that this is a personal project, not affiliated with or endorsed by Inteko y'Umuco or any government body. It credits Clarance and links to https://clarance.me.
- In the list, every field is on its own line, and the definition is larger than the metadata.
- Hovering (or focusing) HI / Eng / Fr / NK shows the full Kinyarwanda name.
- Ishakiro (the letter index) is a single column like the book's contents page. Its hover state must be obvious.
- The home page explains the abbreviations next to a real example entry, without a callout box, and links to a full guide page.
- The page-number arches from the book were tried and **rejected**. Pagination stays as plain round numbers.
- The footer is one small grey line that does not compete for attention.

## Assumptions to confirm in review

- **Removed features:** the ⌘K command palette, the preview side pane on letter pages, the list/compact toggle, and the mobile menu drawer. The user did not answer this question; each is redundant in the new layout. ⌘K and `/` will focus the header search instead, so a keyboard shortcut still exists.
- **Category links:** "Ibitsibo" links and "Andi magambo y'iki gitsibo" keep today's behaviour, which searches for the category's last word. See the follow-ups.
- **Tailwind:** it is replaced by plain CSS with custom properties (see Implementation).

## Out of scope

- Backend, API, parser and data are unchanged. This includes search ranking (see follow-ups).
- Routes keep their paths. One route is added: `/uko-wasoma`.
- No new runtime dependencies.

## Visual system

### Colour tokens (CSS custom properties on `:root`, overridden under `[data-theme="dark"]`)

| Token | Light | Dark | Use |
|---|---|---|---|
| `--blue` | `#1D6CB5` | `#4FA3E3` | cover, tabs, links, buttons |
| `--blue-ink` | `#155A99` | `#7FBDEB` | hover text |
| `--sky` | `#18A0DB` | `#4CBDEB` | section titles, zigzag |
| `--green` | `#2F9A46` | `#5BC274` | field labels (HI, Eng…), running head |
| `--yellow` | `#F5D000` | `#F5D000` | zigzag, primary search button, active letter |
| `--bg` | `#FFFFFF` | `#0E1B2B` | page |
| `--row` | `#EEF6FC` | `#13263B` | alternate rows, running-head wash |
| `--line` | `#CFE1F1` | `#22405F` | rules |
| `--ink` / `--ink-2` / `--muted` | `#1B1B1B` / `#4B4F55` / `#6E747C` | `#E9EEF4` / `#C3CCD6` / `#8C99A8` | text |
| `--cover` | `#1D6CB5` | `#12385E` | home cover band |
| `--hover` | `#FFF3B0` | `#3A3618` | Ishakiro row hover |
| `--img-bg` | `#FFFFFF` | `#F4F7FA` | behind entry images (they have white backgrounds) |

On blue or green fills in dark mode, the text colour is `#0E1B2B`, not white.

### Type

- **UI and titles:** Montserrat 500/600/700/800 (Google Fonts). Titles are uppercase, as on the book's cover.
- **Headwords:** Bodoni Moda 900 (Google Fonts), standing in for the book's Bodoni MT Black.
- **Reading text** (definitions, translations): `"Palatino Linotype", "Book Antiqua", Palatino, "Noto Serif", Georgia, serif`. This matches the book's Book Antiqua with no download; Android falls back to Noto Serif.
- **Sizes:** headword 23px in lists and 52px on the entry page (36px on phone). Definition 19px in lists (17.5px on phone) and 23px on the entry page. Metadata 15.5px. Footer 11.5px.

### Motifs

- **Zigzag ribbon:** three parallel zigzags (sky, yellow, green), drawn as an inline SVG `<pattern>` so the colours follow the theme tokens. On desktop it runs vertically down the left margin, 34px wide, as on every page of the book. On phone it runs horizontally across the top, 22px tall.
- **Running head:** "INKORANYAMUGA Y'IKORANABUHANGA" in italic green small caps on a faint gradient wash, as at the top of each page of the book. It appears on letter pages and the example "page".
- **Letter roundel:** a blue circle with the letter in Bodoni, as in the book.

## Pages and components

### Header (all pages)
- **Wordmark:** "INKORANYAMUGA / Y'IKORANABUHANGA" in two lines, Montserrat 800, blue. It links to `/`.
- **Search:** an input joined to a blue "Shakisha" button. It keeps the existing autocomplete and the recent-searches dropdown, restyled. The search is hidden on `/`, which has its own search.
- **Links:** "Uko wasoma" goes to `/uko-wasoma`. It is shown on desktop only; on phone the footer carries it.
- **Theme toggle:** labelled "Umwijima" or "Urumuri". On phone only the icon shows.
- **Phone layout:** the search moves to a full-width row under the wordmark.

### Home `/`
1. **Cover band** (`--cover`) with the vertical zigzag. It contains:
   - the title in two lines;
   - "Amagambo **1601** · Ikinyarwanda, Icyongereza n'Igifaransa", with the count from `/api/stats`;
   - the large search with a yellow "Shakisha" button;
   - "Gerageza: mudasobwa · imeri · murandasi · mikoro", which links to `/search?q=…`. All four return results today.
2. **Body grid on desktop:** a 240px column plus the rest.
   - **Ishakiro**, with the caption "Inyuguti n'umubare w'amagambo". It is a single-column table: a blue letter cell plus a count cell, with alternating `--row` fill. On hover or focus, the letter cell turns yellow, the row turns `--hover`, the count goes bold and an arrow appears.
   - **Main column:**
     - "Urutonde rw'ibimenyetso mpine": an intro paragraph and a legend list (HI, Eng, Fr, NK), with a link "Soma ibisobanuro byose →" to `/uko-wasoma`. Next to it sits a **miniature book page** with the running head, an "Urugero" label, entry 1140 *Mikoro* rendered exactly like a list entry with its image hidden, and a round "M" marker at the foot.
     - "Ibitsibo": the categories as a two-column contents list with dotted leaders and counts.
3. **Phone layout:** one column in this order: cover, Ishakiro, Ibitsibo, guide plus example.

### Letter page `/browse/:letter` and search `/search?q=`
- **Desktop:** a sticky vertical blue letter-tab column on the left; the active letter is yellow. **Phone:** a horizontally scrolling blue letter strip instead.
- **Heading:**
  - letter pages: the running head, the letter roundel and "Amagambo N";
  - search results: "Ibisubizo bya “q”" and "Amagambo N" instead of the roundel.
- **Each entry, max 720px wide:**
  1. headword (Bodoni) linking to the entry page, with the pronunciation in parentheses (muted);
  2. the definition;
  3. a metadata grid: HI (synonym in bold with its pronunciation), Eng, Fr, NK. Each label is a focusable `<abbr>` with a tooltip giving the full name. Rows with no data are not rendered.
  - An image, if present, floats right at 96px (72px on phone).
- **Pagination:** 50 per page, as today.
  - Round number buttons; the current page is filled with a blue-to-green gradient; there are ‹ › arrows.
  - With more than 7 pages, show `1 … p-1 p p+1 … last`. The letter I has 960 entries, which is 20 pages.
- **No results:** "Nta jambo ryabonetse" plus "Gerageza ijambo rindi cyangwa inyuguti" and a link home. No emoji.
- **Loading:** the text "Gushakisha…" in muted grey. No shimmer skeletons.

### Entry page `/entry/:id`
- Breadcrumb: Ahabanza › letter › term.
- Headword (52px Bodoni) and pronunciation, with the image at the top right (200px, or 88px on phone).
- **Inshoza** (green label) and the definition at 23px, directly under the headword.
- A field table under a 3px blue rule:
  - Impuzanyito (synonym plus pronunciation);
  - Icyongereza;
  - Igifaransa;
  - Igitsibo, a link that keeps today's behaviour.
- Actions:
  - "← Subira inyuma";
  - "Kopa aderesi", which shows "Yakopwe" for 2s after copying;
  - "Andi magambo y'iki gitsibo →" as the primary button.
- No internal `#id` shown.
- Not found: "Ijambo ntiryabonetse" plus a link home.

### Guide `/uko-wasoma` (new, static)
- **Title:** "UKO WASOMA INKORANYAMUGA", followed by a lede.
- **Annotated example:** entry 1138 *Meni yo gutangira* (it has a synonym, two French terms, tone marks and an image), with yellow numbered pins 1–7 on its parts.
- **Numbered sections 1–7,** each with an explanation and a real "Urugero" from the data:
  1. Ijambo ry'indatwa
  2. Imisomere
  3. Inshoza (SH)
  4. Impuzanyito (HI)
  5. Icyongereza (Eng) n'Igifaransa (Fr)
  6. Igitsibo (NK)
  7. Ishusho
- **Abbreviation table** in the book's style (HI, Eng, Fr, NK, SH).
- **Source line:** "Ibisobanuro birambuye biri mu gitabo … (2026), ipaji vi–vii."
- **Copyright:** the text is written for the site, not copied from the book (see Risks). The example entries are static in the component, matching the mockup.

### Footer (all pages)
- One line of 11.5px muted Montserrat above a 1px `--line` rule:
  > Umushinga bwite wakozwe na [Clarance](https://clarance.me), ntaho uhuriye n'Inteko y'Umuco cyangwa urundi rwego rwa Leta. · Amagambo yakuwe mu gitabo *Inkoranyamuga y'Ikoranabuhanga* (2026). · [Uko wasoma](/uko-wasoma)
- Links stay muted and turn blue on hover.

## Data display rules

- **Translations (`english`, `french`):** strip `**` markers. Split on `;`, then render the first term bold and the rest plain, separated by "; ". This follows the book's rule on page vi: the main term is printed bold and the alternatives follow it in plain type.
- **Synonym (`synonym`):** the data looks like `Indangururamajwi (indâangururamâjwi)`. Render the part before " (" in bold and the parenthesised pronunciation muted. Also strip `**`.
- **Pronunciation:** shown in parentheses, as in the book.
- **Category short names and emoji maps** (`CAT_ICONS`, `CAT_SHORT`, `CATEGORY_COLORS`): delete them. Categories always show their full name.
- **The word for words:** use "amagambo", not "amajambo". The book uses *amagambo*.

These rules live in one module, `src/format.js`, so that list, entry, home example and guide all render the same way.

## Implementation

- **Styling:** replace Tailwind with plain CSS.
  - The mockup's CSS ports almost one-to-one, and the token table above becomes `:root` and `[data-theme="dark"]` blocks in `src/style.css`. Component CSS goes in each component's `<style scoped>`.
  - Remove `tailwindcss`, `postcss`, `autoprefixer`, `tailwind.config.js` and `postcss.config.js`.
  - Dark mode moves from the `.dark` class to `html[data-theme]`. It keeps the localStorage key `rw-dark-mode` so saved preferences survive.
  - Alternative: keep Tailwind and map the tokens into its theme. That means more churn for no visual gain, so it is not recommended.
- **`index.html`:** keep `lang="rw"`. Load Montserrat and Bodoni Moda (with `display=swap`) instead of Noto.
- **Files:**
  - Rewrite `App.vue`, `HomeView.vue`, `BrowseView.vue`, `EntryView.vue`, `EntryCard.vue`, `LetterNav.vue` and `SearchBar.vue`.
  - Add `GuideView.vue`, `src/format.js`, `src/components/Ribbon.vue` (the zigzag SVG) and `src/components/Pager.vue`.
  - Delete `CommandPalette.vue`.
  - Add the `/uko-wasoma` route in `main.js`.
- **Accessibility:**
  - visible focus styles on links and buttons;
  - `<abbr>` labels have `tabindex="0"` and an accessible name;
  - the current page in pagination has `aria-current="page"`;
  - the active letter has `aria-current="true"`;
  - touch targets are at least 34px tall on phone.

## Testing

- **Add Vitest** as a dev dependency with an `npm test` script. Unit-test `src/format.js`:
  - `**` stripping;
  - bold first term with the rest plain, for single and multiple terms;
  - splitting a synonym from its pronunciation;
  - empty and missing fields;
  - the page-number windowing for 1, 2, 7 and 20 pages.
- **Add a `npm test` step** to the frontend CI job, before the build.
- **Backend tests** (`pytest`) must still pass unchanged.
- **Before and after screenshots** go in the PR: home, letter M, search "mikoro", entry 1140, and the guide, at 1280px and 375px, light and dark.
- **Manual checks:**
  - search with autocomplete;
  - recent searches;
  - pagination on I (20 pages);
  - copy link;
  - theme persists after reload;
  - deep links load: `/entry/1140`, `/browse/U`, `/uko-wasoma`.

## Risks

- **Copyright:** the book's page ii reserves all rights and forbids reproduction without Inteko y'Umuco's written permission. The site already publishes the full term list, which this redesign does not change. The guide page avoids copying the book's text.
- **Kinyarwanda copy:** the following strings were written for this redesign and need a native check before merge:
  - the intro paragraph;
  - "Inyuguti n'umubare w'amagambo";
  - "Gerageza";
  - "Soma ibisobanuro byose";
  - "Kopa aderesi";
  - "Andi magambo y'iki gitsibo";
  - the footer;
  - every sentence on `/uko-wasoma`.

## Follow-ups (separate work)

- **Search ranking:** an exact headword match should rank first. Today "mikoro" lists *Mikoro* 6th, under "Isoko rya Mikorosofuti". This is a backend change.
- **Category filter:** the category links search for the category's last word. "Ikoranabuhanga rya mudasobwa" lists 995 terms, but its link returns 484 search hits for "mudasobwa". A `category` filter on `/api/entries` would fix this.

## Delivery

- One branch, `ui/book-redesign`, and one PR, squash-merged only after the user's OK.
- After merge: deploy through the deploy-notes session by pinning the new commit in `k8s-homelab/scripts/apps.tsv`.
