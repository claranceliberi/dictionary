<template>
  <Ribbon orientation="h" />

  <header>
    <div class="wrap">
      <div class="bar">
        <router-link class="mark" to="/">
          <span>Inkoranyamuga</span><span>y'Ikoranabuhanga</span>
        </router-link>
        <SearchBar
          v-if="!isHome"
          ref="search"
          v-model="query"
          class="hsearch"
          @search="onSearch"
        />
        <router-link class="hlink" to="/uko-wasoma">Uko wasoma</router-link>
        <button
          class="theme"
          type="button"
          :aria-label="darkMode ? 'Koresha urumuri' : 'Koresha umwijima'"
          @click="toggleDark"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
          </svg>
          <span class="tl">{{ darkMode ? 'Urumuri' : 'Umwijima' }}</span>
        </button>
      </div>
    </div>
  </header>

  <main class="view">
    <router-view :letters="letters" :stats="stats" :categories="categories" />
  </main>

  <footer>
    <div class="wrap">
      <p>
        Umushinga bwite wakozwe na <a href="https://clarance.me" rel="author">Clarance</a>,
        ntaho uhuriye n'Inteko y'Umuco cyangwa urundi rwego rwa Leta.<span class="sep">·</span>Amagambo
        yakuwe mu gitabo <i>Inkoranyamuga y'Ikoranabuhanga</i> (2026).<span class="sep">·</span><router-link to="/uko-wasoma">Uko wasoma</router-link>
      </p>
    </div>
  </footer>
</template>

<script>
import axios from 'axios'
import Ribbon from './components/Ribbon.vue'
import SearchBar from './components/SearchBar.vue'

const THEME_KEY = 'rw-dark-mode'

export default {
  name: 'App',
  components: { Ribbon, SearchBar },
  data() {
    return {
      query: '',
      letters: [],
      stats: { total_entries: 0 },
      categories: [],
      darkMode: false,
    }
  },
  computed: {
    isHome() { return this.$route.path === '/' },
  },
  async created() {
    const saved = localStorage.getItem(THEME_KEY)
    this.darkMode = saved !== null
      ? saved === 'true'
      : window.matchMedia('(prefers-color-scheme: dark)').matches
    this.applyTheme()

    try {
      const [letters, stats, categories] = await Promise.all([
        axios.get('/api/letters'),
        axios.get('/api/stats'),
        axios.get('/api/categories'),
      ])
      this.letters = letters.data
      this.stats = stats.data
      this.categories = categories.data
    } catch (err) {
      console.error('Failed to load app data:', err)
    }
  },
  mounted() {
    window.addEventListener('keydown', this.onGlobalKey)
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.onGlobalKey)
  },
  methods: {
    onSearch(q) {
      if (q.trim()) this.$router.push({ path: '/search', query: { q } })
    },
    applyTheme() {
      document.documentElement.dataset.theme = this.darkMode ? 'dark' : 'light'
    },
    toggleDark() {
      this.darkMode = !this.darkMode
      localStorage.setItem(THEME_KEY, String(this.darkMode))
      this.applyTheme()
    },
    // ⌘K / Ctrl+K anywhere, or "/" outside a text field, jumps to the header search.
    onGlobalKey(e) {
      const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(e.target?.tagName) || e.target?.isContentEditable
      const cmdK = (e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k'
      if (!cmdK && !(e.key === '/' && !typing)) return
      if (!this.$refs.search) return
      e.preventDefault()
      this.$refs.search.focus()
    },
  },
  watch: {
    $route(to) {
      this.query = to.query.q || ''
    },
  },
}
</script>
