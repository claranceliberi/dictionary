import { describe, it, expect } from 'vitest'
import { mount, RouterLinkStub } from '@vue/test-utils'
import EntryCard from './EntryCard.vue'

const menu = {
  id: 1138,
  slug: '1138-meni-yo-gutangira',
  term: 'Meni yo gutangira',
  pronunciation: 'meni yô gutâangira',
  synonym: "Ingingo y'ihagurutsa (ingiingo y'ihâgurutsa)",
  english: 'Start menu',
  french: 'Menu de démarrage; menu démarrer',
  category: 'Ikoranabuhanga rya mudasobwa',
  definition: 'Igikoresho gitanga inzira igera kuri za gahunda, igenabikorwa, incapanyandiko n\'ibindi',
  images: ['img-116.jpeg'],
}

const mountCard = (entry, props = {}) =>
  mount(EntryCard, { props: { entry, ...props }, global: { stubs: { RouterLink: RouterLinkStub } } })

describe('EntryCard', () => {
  it('bolds the synonym and the main French term, leaving alternatives plain', () => {
    const w = mountCard(menu)
    const bolds = w.findAll('dd b').map((b) => b.text())
    expect(bolds).toContain("Ingingo y'ihagurutsa")
    expect(bolds).toContain('Menu de démarrage')
    expect(w.text()).toContain('; menu démarrer')
    expect(w.find('img').attributes('src')).toBe('/images/img-116.jpeg')
  })

  it('omits empty fields without leaving stray brackets', () => {
    const w = mountCard({ ...menu, synonym: '', french: '', images: [], pronunciation: '' })
    const labels = w.findAll('dt abbr').map((a) => a.text())
    expect(labels).toEqual(['Eng', 'NK'])
    expect(w.find('img').exists()).toBe(false)
    expect(w.text()).not.toContain('()')
  })

  it('drops the ** markers from the data', () => {
    const w = mountCard({ ...menu, english: '**Megabyte**' })
    expect(w.text()).toContain('Megabyte')
    expect(w.text()).not.toContain('*')
  })

  it('names each abbreviation in full for the tooltip', () => {
    const w = mountCard(menu)
    const full = Object.fromEntries(w.findAll('dt abbr').map((a) => [a.text(), a.attributes('data-full')]))
    expect(full).toEqual({
      HI: 'Impuzanyito',
      Eng: 'Icyongereza',
      Fr: 'Igifaransa',
      NK: "Igitsibo (ingeri y'ikoranabuhanga)",
    })
  })

  it('drops ** markers from the definition', () => {
    const w = mountCard({ ...menu, definition: 'Cyohereje. **Icyuma ntangafaranga** (icyuma)' })
    expect(w.find('.def').text()).toBe('Cyohereje. Icyuma ntangafaranga (icyuma)')
  })

  it('bolds only the first of several synonyms and mutes every pronunciation', () => {
    const w = mountCard({ ...menu, synonym: 'Imbikamakuru nto (imbikamakuru ntô); disike ngendanwa (disike ngeendânwa)' })
    const hi = w.findAll('dd')[0]
    expect(hi.findAll('b').map((b) => b.text())).toEqual(['Imbikamakuru nto'])
    expect(hi.findAll('.mut').map((s) => s.text())).toEqual(['(imbikamakuru ntô)', '(disike ngeendânwa)'])
    expect(hi.text()).toContain('disike ngendanwa')
  })

  it('marks the search query in the headword, definition and translations, but not the category', () => {
    const w = mountCard({ ...menu, english: 'Start menu; menu bar' }, { q: 'menu' })
    expect(w.find('.hw mark').exists()).toBe(false)
    const marked = w.findAll('mark').map((m) => m.text())
    expect(marked).toEqual(['menu', 'menu', 'Menu', 'menu'])
    expect(w.findAll('dd')[3].find('mark').exists()).toBe(false)
  })

  it('links the headword to the readable word URL', () => {
    expect(mountCard(menu).findComponent(RouterLinkStub).props('to')).toBe('/ijambo/1138-meni-yo-gutangira')
  })

  it('can hide the image for the home page example', () => {
    expect(mountCard(menu, { hideImage: true }).find('img').exists()).toBe(false)
  })
})
