import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Hl from './Hl.vue'

describe('Hl', () => {
  it('wraps matches in <mark> and escapes the text', () => {
    const w = mount(Hl, { props: { text: '<b>Mūdasobwā</b> nto', q: 'mudasobwa' } })
    expect(w.findAll('mark').map((m) => m.text())).toEqual(['Mūdasobwā'])
    expect(w.find('b').exists()).toBe(false)
    expect(w.text()).toBe('<b>Mūdasobwā</b> nto')
  })

  it('renders plain text without a query', () => {
    const w = mount(Hl, { props: { text: 'Mikoro' } })
    expect(w.find('mark').exists()).toBe(false)
    expect(w.text()).toBe('Mikoro')
  })
})
