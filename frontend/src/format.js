// Text helpers for entry fields. The source data keeps the PDF's `**bold**`
// markers on some terms; the book prints the first translation bold and the
// alternatives plain, so we derive that from position instead of the markers.

export function stripMarks(s) {
  return (s ?? '').replace(/\*\*/g, '').trim()
}

export function splitTerms(s) {
  const parts = stripMarks(s).split(';').map((p) => p.trim()).filter(Boolean)
  return { main: parts[0] ?? '', rest: parts.slice(1) }
}

// "Indangururamajwi (indâangururamâjwi)" → { term, pron }
export function splitSynonym(s) {
  const clean = stripMarks(s)
  const i = clean.indexOf(' (')
  if (i === -1) return { term: clean, pron: '' }
  return { term: clean.slice(0, i).trim(), pron: clean.slice(i + 2).replace(/\)\s*$/, '').trim() }
}

// Page numbers to show; '…' marks a skipped range. Empty when there is one page.
export function pageWindow(current, total) {
  if (total <= 1) return []
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
  const pages = new Set([1, total])
  for (let p = current - 1; p <= current + 1; p++) {
    if (p >= 1 && p <= total) pages.add(p)
  }
  const sorted = [...pages].sort((a, b) => a - b)
  const out = []
  sorted.forEach((p, i) => {
    if (i > 0 && p - sorted[i - 1] > 1) out.push('…')
    out.push(p)
  })
  return out
}

// Category links search for the category's last word. That is how the app has
// always done it; a real category filter needs an API change.
export function categoryLink(name) {
  return { path: '/search', query: { q: (name ?? '').trim().split(' ').pop() } }
}
