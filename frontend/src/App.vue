<template>
  <div class="loadbar" :class="{ on: loading.visible }" role="progressbar" aria-label="Birimo gushakishwa" :aria-hidden="!loading.visible"></div>
  <Ribbon orientation="h" />

  <header>
    <div class="wrap">
      <div class="bar">
        <router-link class="mark" to="/">
          <img class="logo" src="/favicon.svg" alt="" width="34" height="34" />
          <span class="mark-text"><span>Inkoranyamuga</span><span>y'Ikoranabuhanga</span></span>
        </router-link>
        <SearchBar
          v-if="!isHome"
          ref="search"
          v-model="query"
          class="hsearch"
          @search="onSearch"
        />
        <router-link class="hlink" to="/uko-wasoma" aria-label="Uko wasoma">
          <Icon name="help" /><span class="tl">Uko wasoma</span>
        </router-link>
        <button
          class="theme"
          type="button"
          :aria-label="darkMode ? 'Koresha urumuri' : 'Koresha umwijima'"
          @click="toggleDark"
        >
          <Icon :name="darkMode ? 'sun' : 'moon'" />
          <span class="tl">{{ darkMode ? 'Urumuri' : 'Umwijima' }}</span>
        </button>
      </div>
    </div>
  </header>

  <main class="view">
    <router-view v-slot="{ Component, route }">
      <Transition name="page" mode="out-in">
        <component :is="Component" :key="route.path" :letters="letters" :stats="stats" :categories="categories" />
      </Transition>
    </router-view>
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
import Icon from './components/Icon.vue'
import Ribbon from './components/Ribbon.vue'
import { loading } from './loading.js'
import SearchBar from './components/SearchBar.vue'

const THEME_KEY = 'rw-dark-mode'

export default {
  name: 'App',
  components: { Icon, Ribbon, SearchBar },
  data() {
    return {
      query: '',
      letters: [],
      stats: { total_entries: 0 },
      categories: [],
      darkMode: false,
      loading,
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
      // Colours cross-fade only while switching, not on every page load.
      const root = document.documentElement
      root.classList.add('theming')
      setTimeout(() => root.classList.remove('theming'), 300)
      this.darkMode = !this.darkMode
      localStorage.setItem(THEME_KEY, String(this.darkMode))
      this.applyTheme()
    },
    // ⌘K / Ctrl+K anywhere, or "/" outside a text field, jumps to the header search.
    onGlobalKey(e) {
      const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(e.target?.tagName) || e.target?.isContentEditable
      const cmdK = (e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k'
      if (!cmdK && !(e.key === '/' && !typing)) return
      // On the home page the header search is hidden; use the cover search instead.
      const target = this.$refs.search ?? document.querySelector('.cover input[type="search"]')
      if (!target) return
      e.preventDefault()
      target.focus()
    },
  },
  watch: {
    $route(to) {
      this.query = to.query.q || ''
    },
  },
}
</script>
