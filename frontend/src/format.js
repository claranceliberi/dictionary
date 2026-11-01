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

// Some entries list several synonyms separated by ";", each with its own pronunciation.
export function splitSynonyms(s) {
  return stripMarks(s).split(';').map((p) => splitSynonym(p)).filter((p) => p.term || p.pron)
}

export const SITE_TITLE = "Inkoranyamuga y'Ikoranabuhanga"

// Matches the <title> the server sends for /ijambo/ pages.
export function entryTitle(entry) {
  const english = splitTerms(entry.english).main
  return `${stripMarks(entry.term)}${english ? ` — ${english}` : ''} | ${SITE_TITLE}`
}

export function countLabel(n) {
  return n === 1 ? 'Ijambo 1' : `Amagambo ${n}`
}

const fold = (s) => s.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase()

// Splits text into [{ text, hit }] around every match of q, ignoring case and
// tone marks (so "mudasobwa" also marks "mūdasobwā"). Rendered as <mark> by the
// caller, which keeps the text escaped.
export function highlight(text, q) {
  const src = text ?? ''
  if (!src) return []
  const needle = fold((q ?? '').trim())
  if (!needle) return [{ text: src, hit: false }]

  // folded string plus, for each folded char, the index of its source char
  let folded = ''
  const at = []
  for (let i = 0; i < src.length; i++) {
    const f = fold(src[i])
    folded += f
    for (let k = 0; k < f.length; k++) at.push(i)
  }

  const parts = []
  let last = 0
  let from = 0
  let hitAt
  while ((hitAt = folded.indexOf(needle, from)) !== -1) {
    const start = at[hitAt]
    const end = at[hitAt + needle.length - 1] + 1
    if (start > last) parts.push({ text: src.slice(last, start), hit: false })
    parts.push({ text: src.slice(start, end), hit: true })
    last = end
    from = hitAt + needle.length
  }
  if (last < src.length) parts.push({ text: src.slice(last), hit: false })
  return parts
}

// Category links search for the category's last word. That is how the app has
// always done it; a real category filter needs an API change.
export function categoryLink(name) {
  return { path: '/search', query: { q: (name ?? '').trim().split(' ').pop() } }
}
