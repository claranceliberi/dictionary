import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises, RouterLinkStub } from '@vue/test-utils'
import axios from 'axios'
import EntryView from './EntryView.vue'

vi.mock('axios')

const MIKORO = {
  id: 1140, slug: '1140-mikoro', term: 'Mikoro', pronunciation: 'mikoro', letter: 'M', images: [], synonym: '',
  english: 'Microphone', french: 'Microphone', category: "Ikoranabuhanga ry'amajwi", definition: 'Indangururamajwi',
}

async function mountEntry(data = MIKORO, slug = data.slug) {
  axios.get.mockResolvedValue({ data })
  const router = { back: vi.fn(), replace: vi.fn() }
  const w = mount(EntryView, {
    global: { stubs: { RouterLink: RouterLinkStub }, mocks: { $route: { params: { slug } }, $router: router } },
  })
  await flushPromises()
  return { w, router }
}

describe('EntryView address', () => {
  beforeEach(() => axios.get.mockReset())

  it('loads the entry by the number at the start of the address', async () => {
    await mountEntry()
    expect(axios.get).toHaveBeenCalledWith('/api/entries/1140')
  })

  it('names the browser tab after the word', async () => {
    await mountEntry()
    expect(document.title).toBe("Mikoro — Microphone | Inkoranyamuga y'Ikoranabuhanga")
  })

  it('swaps a short or outdated address for the readable one', async () => {
    const { router } = await mountEntry(MIKORO, '1140')
    expect(router.replace).toHaveBeenCalledWith('/ijambo/1140-mikoro')
  })

  it('leaves the readable address alone', async () => {
    const { router } = await mountEntry()
    expect(router.replace).not.toHaveBeenCalled()
  })
})

describe('EntryView sharing', () => {
  it('opens the device share sheet when there is one', async () => {
    const share = vi.fn().mockResolvedValue()
    Object.defineProperty(navigator, 'share', { value: share, configurable: true })
    const { w } = await mountEntry()
    await w.find('button.share').trigger('click')
    expect(share).toHaveBeenCalledWith({ title: 'Mikoro', text: 'Indangururamajwi', url: window.location.href })
    delete navigator.share
  })

  it('copies the link when there is no share sheet', async () => {
    const writeText = vi.fn().mockResolvedValue()
    Object.defineProperty(navigator, 'clipboard', { value: { writeText }, configurable: true })
    const { w } = await mountEntry()
    await w.find('button.share').trigger('click')
    await flushPromises()
    expect(writeText).toHaveBeenCalledWith(window.location.href)
    expect(w.find('button.share').text()).toContain('Yakopwe')
  })
})

describe('EntryView', () => {
  it('shows several synonyms with only the first bold, and strips ** from the definition', async () => {
    const { w } = await mountEntry({
      ...MIKORO, id: 181, slug: '181-ikarita', term: 'Ikarita',
      synonym: 'Imbikamakuru nto (imbikamakuru ntô); disike ngendanwa (disike ngeendânwa)',
      definition: 'Cyohereje. **Icyuma ntangafaranga** (icyuma)',
    })
    expect(w.find('.lead p').text()).toBe('Cyohereje. Icyuma ntangafaranga (icyuma)')
    const hi = w.findAll('.f')[0]
    expect(hi.findAll('b').map((b) => b.text())).toEqual(['Imbikamakuru nto'])
    expect(hi.findAll('small').map((s) => s.text())).toEqual(['(imbikamakuru ntô)', '(disike ngeendânwa)'])
  })
})
