import { describe, it, expect } from 'vitest'
import { stripMarks, splitTerms, splitSynonym, pageWindow, categoryLink, splitSynonyms, countLabel, highlight } from './format.js'

describe('countLabel', () => {
  it('uses the singular for exactly one word', () => {
    expect(countLabel(1)).toBe('Ijambo 1')
  })
  it('uses the plural otherwise', () => {
    expect(countLabel(0)).toBe('Amagambo 0')
    expect(countLabel(55)).toBe('Amagambo 55')
  })
})

describe('highlight', () => {
  const hits = (parts) => parts.filter((p) => p.hit).map((p) => p.text)

  it('marks every case-insensitive match and keeps the rest of the text intact', () => {
    const parts = highlight('Mudasobwa ya mudasobwa', 'mudasobwa')
    expect(hits(parts)).toEqual(['Mudasobwa', 'mudasobwa'])
    expect(parts.map((p) => p.text).join('')).toBe('Mudasobwa ya mudasobwa')
  })
  it('ignores tone marks, so a plain query matches the pronunciation', () => {
    expect(hits(highlight('(mūdasobwā ngeendânwa)', 'mudasobwa'))).toEqual(['mūdasobwā'])
  })
  it('matches inside longer words', () => {
    expect(hits(highlight('Umujyo nyatsamudasobwa', 'mudasobwa'))).toEqual(['mudasobwa'])
  })
  it('returns the text unmarked when there is no query or no match', () => {
    expect(highlight('Mikoro', '')).toEqual([{ text: 'Mikoro', hit: false }])
    expect(highlight('Mikoro', 'imeri')).toEqual([{ text: 'Mikoro', hit: false }])
    expect(highlight('', 'x')).toEqual([])
  })
})
import { readFileSync } from 'node:fs'

describe('dark theme fills', () => {
  it('uses dark text on the current page number', () => {
    const css = readFileSync('src/style.css', 'utf8')
    expect(css).toMatch(/\[data-theme="dark"\] \.pager \.cur[^{]*\{[^}]*color: #0E1B2B/)
  })
})

describe('stripMarks', () => {
  it('removes the ** bold markers left over from the PDF', () => {
    expect(stripMarks('**Megabyte**')).toBe('Megabyte')
  })
  it('returns an empty string for missing values', () => {
    expect(stripMarks(undefined)).toBe('')
    expect(stripMarks(null)).toBe('')
  })
})

describe('splitTerms', () => {
  it('separates the main term from the alternatives', () => {
    expect(splitTerms('**Macintoch**; Mac')).toEqual({ main: 'Macintoch', rest: ['Mac'] })
    expect(splitTerms('Menu de démarrage; menu démarrer')).toEqual({ main: 'Menu de démarrage', rest: ['menu démarrer'] })
  })
  it('handles a single term', () => {
    expect(splitTerms('Microphone')).toEqual({ main: 'Microphone', rest: [] })
  })
  it('handles empty input and stray separators', () => {
    expect(splitTerms('')).toEqual({ main: '', rest: [] })
    expect(splitTerms('a;; b; ')).toEqual({ main: 'a', rest: ['b'] })
  })
})

describe('splitSynonym', () => {
  it('splits the synonym from its pronunciation', () => {
    expect(splitSynonym('Indangururamajwi (indâangururamâjwi)')).toEqual({ term: 'Indangururamajwi', pron: 'indâangururamâjwi' })
    expect(splitSynonym('**Mudasobwa ya Mac** (Mudâsobwâ ya maâki)')).toEqual({ term: 'Mudasobwa ya Mac', pron: 'Mudâsobwâ ya maâki' })
  })
  it('handles a synonym without pronunciation, and empty input', () => {
    expect(splitSynonym('Indanga')).toEqual({ term: 'Indanga', pron: '' })
    expect(splitSynonym('')).toEqual({ term: '', pron: '' })
  })
})

describe('pageWindow', () => {
  it('hides the pager for a single page', () => {
    expect(pageWindow(1, 1)).toEqual([])
  })
  it('lists every page up to seven', () => {
    expect(pageWindow(1, 2)).toEqual([1, 2])
    expect(pageWindow(4, 7)).toEqual([1, 2, 3, 4, 5, 6, 7])
  })
  it('windows long ranges around the current page', () => {
    expect(pageWindow(1, 20)).toEqual([1, 2, '…', 20])
    expect(pageWindow(10, 20)).toEqual([1, '…', 9, 10, 11, '…', 20])
    expect(pageWindow(20, 20)).toEqual([1, '…', 19, 20])
  })
})

describe('splitSynonyms', () => {
  it('splits a ;-separated list of synonyms, each with its pronunciation', () => {
    expect(splitSynonyms('Imbikamakuru nto (imbikamakuru ntô); disike ngendanwa (disike ngeendânwa)')).toEqual([
      { term: 'Imbikamakuru nto', pron: 'imbikamakuru ntô' },
      { term: 'disike ngendanwa', pron: 'disike ngeendânwa' },
    ])
    expect(splitSynonyms('')).toEqual([])
  })
})

describe('categoryLink', () => {
  it('keeps the existing behaviour: search for the last word of the category', () => {
    expect(categoryLink('Ikoranabuhanga rya mudasobwa')).toEqual({ path: '/search', query: { q: 'mudasobwa' } })
    expect(categoryLink('Isakazamakuru')).toEqual({ path: '/search', query: { q: 'Isakazamakuru' } })
  })
})
