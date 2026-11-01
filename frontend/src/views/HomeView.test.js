import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises, RouterLinkStub } from '@vue/test-utils'
import axios from 'axios'
import HomeView from './HomeView.vue'

vi.mock('axios')

const CATEGORIES = [
  { name: 'Ikoranabuhanga rya mudasobwa', count: 995 },
  { name: 'Ibikoresho by\'itangazamakuru', count: 1 },
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

describe('Ibitsibo table', () => {
  it('has Igitsibo and Amagambo column headers', async () => {
    const w = await mountHome()
    const headers = w.findAll('.ibitsibo [role="columnheader"]').map((h) => h.text())
    expect(headers).toEqual(['Igitsibo', 'Amagambo'])
  })

  it('has one linked row per category with its name and word count', async () => {
    const w = await mountHome()
    const rows = w.findAll('.ibitsibo .ib-row')
    expect(rows.map((r) => r.findAll('[role="cell"]').map((c) => c.text()))).toEqual([
      ['Ikoranabuhanga rya mudasobwa', '995'],
      ["Ibikoresho by'itangazamakuru", '1'],
    ])
    expect(w.findAllComponents(RouterLinkStub).map((l) => l.props('to')))
      .toContainEqual({ path: '/search', query: { q: 'mudasobwa' } })
  })
})
