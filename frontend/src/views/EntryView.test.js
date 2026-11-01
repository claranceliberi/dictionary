import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises, RouterLinkStub } from '@vue/test-utils'
import axios from 'axios'
import EntryView from './EntryView.vue'

vi.mock('axios')

async function mountEntry() {
  axios.get.mockResolvedValue({
    data: { id: 1140, term: 'Mikoro', pronunciation: 'mikoro', letter: 'M', images: [], synonym: '', english: 'Microphone', french: 'Microphone', category: "Ikoranabuhanga ry'amajwi", definition: 'Indangururamajwi' },
  })
  const w = mount(EntryView, {
    global: { stubs: { RouterLink: RouterLinkStub }, mocks: { $route: { params: { id: '1140' } }, $router: { back() {} } } },
  })
  await flushPromises()
  return w
}

describe('EntryView sharing', () => {
  it('opens the device share sheet when there is one', async () => {
    const share = vi.fn().mockResolvedValue()
    Object.defineProperty(navigator, 'share', { value: share, configurable: true })
    const w = await mountEntry()
    await w.find('button.share').trigger('click')
    expect(share).toHaveBeenCalledWith({ title: 'Mikoro', text: 'Indangururamajwi', url: window.location.href })
    delete navigator.share
  })

  it('copies the link when there is no share sheet', async () => {
    const writeText = vi.fn().mockResolvedValue()
    Object.defineProperty(navigator, 'clipboard', { value: { writeText }, configurable: true })
    const w = await mountEntry()
    await w.find('button.share').trigger('click')
    await flushPromises()
    expect(writeText).toHaveBeenCalledWith(window.location.href)
    expect(w.find('button.share').text()).toContain('Yakopwe')
  })
})

describe('EntryView', () => {
  it('shows several synonyms with only the first bold, and strips ** from the definition', async () => {
    axios.get.mockResolvedValue({
      data: {
        id: 181, term: 'Ikarita', pronunciation: '', letter: 'I', images: [],
        synonym: 'Imbikamakuru nto (imbikamakuru ntô); disike ngendanwa (disike ngeendânwa)',
        english: 'Card', french: 'Carte', category: 'Ikoranabuhanga rya mudasobwa',
        definition: 'Cyohereje. **Icyuma ntangafaranga** (icyuma)',
      },
    })
    const w = mount(EntryView, {
      global: { stubs: { RouterLink: RouterLinkStub }, mocks: { $route: { params: { id: '181' } }, $router: { back() {} } } },
    })
    await flushPromises()
    expect(w.find('.lead p').text()).toBe('Cyohereje. Icyuma ntangafaranga (icyuma)')
    const hi = w.findAll('.f')[0]
    expect(hi.findAll('b').map((b) => b.text())).toEqual(['Imbikamakuru nto'])
    expect(hi.findAll('small').map((s) => s.text())).toEqual(['(imbikamakuru ntô)', '(disike ngeendânwa)'])
  })
})
