import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises, RouterLinkStub } from '@vue/test-utils'
import axios from 'axios'
import HomeView from './HomeView.vue'

vi.mock('axios')

const CATEGORIES = [
  { name: 'Ikoranabuhanga rya mudasobwa', count: 995 },
  { name: 'Ikoranabuhanga rya murandasi', count: 248 },
  { name: 'Itumanaho koranabuhanga', count: 78 },
]

async function mountHome() {
  axios.get.mockResolvedValue({ data: null })
  const w = mount(HomeView, {
    props: { categories: CATEGORIES, letters: [], stats: { total_entries: 1601 } },
    global: { stubs: { RouterLink: RouterLinkStub } },
  })
  await flushPromises()
  return w
}

describe('Ibitsibo list', () => {
  it('labels each column Igitsibo … Amagambo', async () => {
    const w = await mountHome()
    const caps = w.findAll('.col-cats .ib-cap').map((c) => c.findAll('span').map((s) => s.text()))
    expect(caps.length).toBeGreaterThan(0)
    for (const cap of caps) expect(cap).toEqual(['Igitsibo', 'Amagambo'])
  })

  it('keeps the dotted-leader rows, in order, each linking to its category', async () => {
    const w = await mountHome()
    const rows = w.findAll('.col-cats li')
    expect(rows.map((r) => [r.find('span').text(), r.find('.n').text()])).toEqual([
      ['Ikoranabuhanga rya mudasobwa', '995'],
      ['Ikoranabuhanga rya murandasi', '248'],
      ['Itumanaho koranabuhanga', '78'],
    ])
    expect(rows.every((r) => r.find('.dots').exists())).toBe(true)
    expect(rows[0].findComponent(RouterLinkStub).props('to')).toEqual({ path: '/search', query: { q: 'mudasobwa' } })
  })
})
