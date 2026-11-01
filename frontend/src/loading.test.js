import { describe, it, expect, vi, afterEach } from 'vitest'
import axios from 'axios'
import { loading, trackRequests } from './loading.js'

function clientResolvingAfter(ms) {
  const client = axios.create({
    adapter: (config) => new Promise((resolve) => setTimeout(() => resolve({ data: {}, status: 200, statusText: 'OK', headers: {}, config }), ms)),
  })
  trackRequests(client)
  return client
}

describe('loading bar', () => {
  afterEach(() => vi.useRealTimers())

  it('stays hidden while a request is younger than the delay', async () => {
    vi.useFakeTimers()
    const req = clientResolvingAfter(120).get('/api/fast')
    await vi.advanceTimersByTimeAsync(100)
    expect(loading.active).toBe(1)
    expect(loading.visible).toBe(false)
    await vi.advanceTimersByTimeAsync(30)
    await req
    expect(loading.visible).toBe(false)
    expect(loading.active).toBe(0)
  })

  it('shows for slow requests and hides when they finish', async () => {
    vi.useFakeTimers()
    const req = clientResolvingAfter(1000).get('/api/slow')
    await vi.advanceTimersByTimeAsync(200)
    expect(loading.visible).toBe(true)
    await vi.advanceTimersByTimeAsync(900)
    await req
    expect(loading.visible).toBe(false)
  })
})
