import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises, RouterLinkStub } from '@vue/test-utils'
import axios from 'axios'
import HomeView from './HomeView.vue'

vi.mock('axios')

const LETTERS = [{ letter: 'A', count: 76 }, { letter: 'B', count: 11 }, { letter: 'C', count: 1 }]
const CATEGORIES = [
  { name: 'Ikoranabuhanga rya mudasobwa', count: 995 },
  { name: 'Itumanaho koranabuhanga', count: 78 },
]
const MIKORO = {
  id: 1140, slug: '1140-mikoro', term: 'Mikoro', pronunciation: 'mikoro', synonym: '', images: [],
  english: 'Microphone', french: 'Microphone', category: "Ikoranabuhanga ry'amajwi", definition: 'Indangururamajwi',
}

async function mountHome() {
  axios.get.mockResolvedValue({ data: MIKORO })
  const w = mount(HomeView, {
    props: { categories: CATEGORIES, letters: LETTERS, stats: { total_entries: 1601 } },
    global: { stubs: { RouterLink: RouterLinkStub } },
  })
  await flushPromises()
  return w
}

describe('home page sections', () => {
  it('gives every section a title with a short description under it', async () => {
    const w = await mountHome()
    const sections = w.findAll('.home-sect').map((s) => [s.find('h2').text(), s.find('.cap').text()])
    expect(sections.map(([title]) => title)).toEqual(['Inyuguti', 'Ibitsibo', 'Uko wasoma'])
    for (const [, cap] of sections) expect(cap.length).toBeGreaterThan(10)
  })

  it('shows the letters as one band, each linking to its letter page', async () => {
    const w = await mountHome()
    const links = w.findAll('.lband a')
    expect(links.map((a) => a.text())).toEqual(['A', 'B', 'C'])
    expect(w.findAll('.lband a').length).toBe(3)
    const to = w.findAllComponents(RouterLinkStub).map((l) => l.props('to'))
    expect(to).toContain('/browse/A')
  })

  it('lists the categories under an Igitsibo … Amagambo header', async () => {
    const w = await mountHome()
    expect(w.find('.ib-cap').findAll('span').map((s) => s.text())).toEqual(['Igitsibo', 'Amagambo'])
    const rows = w.findAll('.ibitsibo li')
    expect(rows.map((r) => [r.find('span').text(), r.find('.n').text()])).toEqual([
      ['Ikoranabuhanga rya mudasobwa', '995'],
      ['Itumanaho koranabuhanga', '78'],
    ])
  })

  it('shows one example entry with a link to the full guide', async () => {
    const w = await mountHome()
    expect(w.find('.minipage .hw').text()).toBe('Mikoro')
    expect(w.findAllComponents(RouterLinkStub).map((l) => l.props('to'))).toContain('/uko-wasoma')
  })

  it('no longer repeats the abbreviation guide or the letter table', async () => {
    const w = await mountHome()
    expect(w.find('.legend').exists()).toBe(false)
    expect(w.find('.ishakiro').exists()).toBe(false)
  })
})
