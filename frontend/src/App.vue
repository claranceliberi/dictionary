<template>
  <div :class="['min-h-screen flex flex-col', darkMode ? 'dark' : '']">

    <!-- ── Sticky header ─────────────────────────────── -->
    <header class="bg-rw-green text-white sticky top-0 z-40 shadow-lg">
      <div class="max-w-7xl mx-auto px-4 py-3 flex items-center gap-3">

        <!-- Logo -->
        <router-link to="/" class="flex-shrink-0 group mr-1">
          <h1 class="font-serif text-base font-bold leading-tight">
            Inkoranyamuga
            <span class="text-white/60 text-xs font-normal block">y'Ikoranabuhanga</span>
          </h1>
        </router-link>

        <!-- Search — always visible -->
        <div class="flex-1 max-w-xl">
          <SearchBar v-model="query" @search="onSearch" />
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-1.5 flex-shrink-0">
          <!-- Cmd palette hint (desktop) -->
          <button
            @click="showPalette = true"
            class="hidden md:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg
                   bg-white/10 hover:bg-white/20 text-xs text-white/70
                   transition-colors duration-150"
            title="Ctrl+K"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"/>
            </svg>
            <kbd class="font-mono">⌘K</kbd>
          </button>

          <!-- Dark mode toggle -->
          <button
            @click="toggleDark"
            class="w-9 h-9 rounded-lg bg-white/10 hover:bg-white/20
                   flex items-center justify-center transition-colors duration-150"
            :aria-label="darkMode ? 'Light mode' : 'Dark mode'"
          >
            <svg v-if="darkMode" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0z"/>
            </svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
          </button>

          <!-- Mobile menu -->
          <button
            @click="drawerOpen = true"
            class="md:hidden w-9 h-9 rounded-lg bg-white/10 hover:bg-white/20
                   flex items-center justify-center transition-colors duration-150"
            aria-label="Menu"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 6h16M4 12h16M4 18h7"/>
            </svg>
          </button>
        </div>
      </div>
    </header>

    <!-- Imigongo strip -->
    <div class="imigongo-strip w-full"></div>

    <!-- ── Mobile drawer ────────────────────────────── -->
    <!-- Backdrop -->
    <div
      class="fixed inset-0 bg-black/50 z-50 md:hidden transition-opacity duration-200"
      :class="drawerOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'"
      @click="drawerOpen = false"
    ></div>
    <!-- Panel -->
    <div
      class="fixed left-0 top-0 bottom-0 w-72 z-50 md:hidden
             bg-white dark:bg-slate-900 shadow-2xl flex flex-col
             transition-transform duration-250 ease-out"
      :class="drawerOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="bg-rw-green text-white px-5 py-4 flex items-center justify-between flex-shrink-0">
        <span class="font-serif font-bold">Inkoranyamuga</span>
        <button @click="drawerOpen = false" class="text-white/70 hover:text-white text-2xl leading-none w-8 h-8 flex items-center justify-center">
          ×
        </button>
      </div>
      <div class="imigongo-strip flex-shrink-0"></div>
      <div class="p-4 flex-1 overflow-y-auto">
        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-3">
          Inyuguti
        </p>
        <LetterNav
          :letters="letters"
          vertical
          :active="$route.params.letter"
          @navigate="drawerOpen = false"
        />
      </div>
    </div>

    <!-- ── Command palette ──────────────────────────── -->
    <CommandPalette
      v-if="showPalette"
      :letters="letters"
      @close="showPalette = false"
      @navigate="showPalette = false"
    />

    <!-- ── Main content ─────────────────────────────── -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
      <router-view :letters="letters" :stats="stats" :dark-mode="darkMode" />
    </main>

    <!-- ── Footer ───────────────────────────────────── -->
    <footer class="bg-imigongo-dark dark:bg-black text-imigongo-cream py-8 mt-4">
      <div class="max-w-7xl mx-auto px-4 text-center">
        <div class="imigongo-strip w-32 mx-auto mb-5 rounded-full overflow-hidden"></div>
        <p class="font-serif text-sm mb-1">Inkoranyamuga y'Ikoranabuhanga</p>
        <p class="text-xs text-imigongo-cream/50">
          © 2026 Inteko y'Umuco — Rwanda Cultural Heritage Academy
        </p>
      </div>
    </footer>
  </div>
</template>

<script>
import axios from 'axios'
import SearchBar from './components/SearchBar.vue'
import LetterNav from './components/LetterNav.vue'
import CommandPalette from './components/CommandPalette.vue'

export default {
  name: 'App',
  components: { SearchBar, LetterNav, CommandPalette },
  data() {
    return {
      query: '',
      letters: [],
      stats: { total_entries: 0 },
      darkMode: false,
      drawerOpen: false,
      showPalette: false,
    }
  },
  async created() {
    // Restore dark mode preference
    const saved = localStorage.getItem('rw-dark-mode')
    this.darkMode = saved !== null
      ? saved === 'true'
      : window.matchMedia('(prefers-color-scheme: dark)').matches
    document.documentElement.classList.toggle('dark', this.darkMode)

    const [lettersRes, statsRes] = await Promise.all([
      axios.get('/api/letters'),
      axios.get('/api/stats'),
    ])
    this.letters = lettersRes.data
    this.stats = statsRes.data
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
    toggleDark() {
      this.darkMode = !this.darkMode
      localStorage.setItem('rw-dark-mode', this.darkMode)
      document.documentElement.classList.toggle('dark', this.darkMode)
    },
    onGlobalKey(e) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        this.showPalette = !this.showPalette
      }
      if (e.key === 'Escape') {
        this.drawerOpen = false
        this.showPalette = false
      }
    },
  },
  watch: {
    $route(to) {
      this.query = to.query.q || ''
      this.drawerOpen = false
    },
  },
}
</script>
