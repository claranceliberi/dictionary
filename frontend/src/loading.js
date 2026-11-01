import { reactive } from 'vue'
import axios from 'axios'

// Counts in-flight API requests so the app can show a thin progress bar.
// The bar only appears when a request takes longer than DELAY, so fast
// responses don't flash it.
export const loading = reactive({ active: 0, visible: false })

const DELAY = 150
let timer = null

function update() {
  clearTimeout(timer)
  if (loading.active > 0) {
    if (!loading.visible) timer = setTimeout(() => { loading.visible = loading.active > 0 }, DELAY)
  } else {
    loading.visible = false
  }
}

export function trackRequests(client = axios) {
  client.interceptors.request.use((config) => { loading.active++; update(); return config })
  const done = () => { loading.active = Math.max(0, loading.active - 1); update() }
  client.interceptors.response.use(
    (res) => { done(); return res },
    (err) => { done(); return Promise.reject(err) },
  )
}
