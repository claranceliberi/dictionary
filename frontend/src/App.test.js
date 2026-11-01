import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import axios from 'axios'
import App from './App.vue'

vi.mock('axios')

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div class="cover"><input type="search" /></div>' } },
      { path: '/uko-wasoma', component: { template: '<div />' } },
    ],
  })
}

async function mountApp() {
  axios.get.mockResolvedValue({ data: [] })
  const router = makeRouter()
  router.push('/')
  await router.isReady()
  const wrapper = mount(App, { global: { plugins: [router] }, attachTo: document.body })
  await flushPromises()
  return wrapper
}

describe('App shell', () => {
  beforeEach(() => {
    localStorage.clear()
    delete document.documentElement.dataset.theme
    window.matchMedia = vi.fn().mockReturnValue({ matches: false })
  })

  it('keeps a dark theme saved by the previous version of the app', async () => {
    localStorage.setItem('rw-dark-mode', 'true')
    await mountApp()
    expect(document.documentElement.dataset.theme).toBe('dark')
  })

  it('toggles the theme and saves it under the same key', async () => {
    localStorage.setItem('rw-dark-mode', 'true')
    const wrapper = await mountApp()
    await wrapper.find('button.theme').trigger('click')
    expect(localStorage.getItem('rw-dark-mode')).toBe('false')
    expect(document.documentElement.dataset.theme).toBe('light')
    wrapper.unmount()
  })

  it('focuses the home search on ⌘K when the header search is hidden', async () => {
    const wrapper = await mountApp()
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', metaKey: true }))
    expect(document.activeElement).toBe(document.querySelector('.cover input[type="search"]'))
    wrapper.unmount()
  })

  it('gives pages other than a word the site name as their tab title', async () => {
    document.title = 'Mikoro — Microphone | old'
    const wrapper = await mountApp()
    expect(document.title).toBe("Inkoranyamuga y'Ikoranabuhanga")
    wrapper.unmount()
  })

  it('credits Clarance in the footer with a link to clarance.me', async () => {
    const wrapper = await mountApp()
    const link = wrapper.find('footer a[rel="author"]')
    expect(link.text()).toBe('Clarance')
    expect(link.attributes('href')).toBe('https://clarance.me')
    wrapper.unmount()
  })
})
