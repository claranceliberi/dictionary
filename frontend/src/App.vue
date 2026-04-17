<template>
  <div class="min-h-screen flex flex-col">
    <!-- Header -->
    <header class="bg-rw-green text-white shadow-md">
      <div class="max-w-6xl mx-auto px-4 py-3 flex items-center gap-4">
        <router-link to="/" class="flex-shrink-0">
          <h1 class="font-serif text-lg font-bold leading-tight">
            Inkoranyamuga<br>
            <span class="text-white/70 text-sm font-normal">y'Ikoranabuhanga</span>
          </h1>
        </router-link>
        <div v-if="$route.path !== '/'" class="flex-1 max-w-xl">
          <SearchBar v-model="query" @search="onSearch" />
        </div>
      </div>
    </header>

    <!-- Imigongo decorative strip -->
    <div class="imigongo-strip w-full flex-shrink-0"></div>

    <!-- Main -->
    <main class="flex-1 max-w-6xl w-full mx-auto px-4 py-6">
      <router-view :letters="letters" :stats="stats" />
    </main>

    <!-- Footer -->
    <footer class="bg-imigongo-dark text-imigongo-cream mt-8 py-5 text-center text-xs">
      © 2026 Inteko y'Umuco — Rwanda Cultural Heritage Academy
    </footer>
  </div>
</template>

<script>
import axios from 'axios'
import SearchBar from './components/SearchBar.vue'

export default {
  name: 'App',
  components: { SearchBar },
  data() {
    return {
      query: '',
      letters: [],
      stats: { total_entries: 0, entries_with_images: 0 },
    }
  },
  async created() {
    const [lettersRes, statsRes] = await Promise.all([
      axios.get('/api/letters'),
      axios.get('/api/stats'),
    ])
    this.letters = lettersRes.data
    this.stats = statsRes.data
  },
  methods: {
    onSearch(q) {
      if (q.trim()) {
        this.$router.push({ path: '/search', query: { q } })
      }
    },
  },
  watch: {
    $route(to) {
      this.query = to.query.q || ''
    },
  },
}
</script>
