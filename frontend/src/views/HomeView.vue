<template>
  <div>
    <!-- ── Cultural hero ──────────────────────────────── -->
    <div class="imigongo-hero rounded-3xl overflow-hidden mb-6 -mx-4 px-8 py-14 text-white text-center relative">
      <!-- Subtle inner vignette -->
      <div class="absolute inset-0 bg-gradient-to-b from-black/10 via-transparent to-black/20 pointer-events-none"></div>
      <div class="relative">
        <p class="text-xs font-semibold uppercase tracking-widest text-white/60 mb-3">
          Inteko y'Umuco · Rwanda Cultural Heritage Academy
        </p>
        <h2 class="font-serif text-4xl md:text-5xl font-bold text-white mb-2 leading-tight">
          Inkoranyamuga y'Ikoranabuhanga
        </h2>
        <div v-if="stats.total_entries" class="flex items-center justify-center gap-3 mb-8 text-white/70 text-sm">
          <span>{{ stats.total_entries.toLocaleString() }} amajambo</span>
          <span class="w-1 h-1 rounded-full bg-white/40"></span>
          <span>Ikinyarwanda</span>
          <span class="w-1 h-1 rounded-full bg-white/40"></span>
          <span>Icyongereza</span>
          <span class="w-1 h-1 rounded-full bg-white/40"></span>
          <span>Igifaransa</span>
        </div>
        <div class="max-w-xl mx-auto">
          <SearchBar v-model="query" size="lg" @search="onSearch" />
        </div>
        <p class="mt-3 text-xs text-white/40">
          Kanda <kbd class="font-mono border border-white/20 rounded px-1 py-0.5">⌘K</kbd> kugirango ukoreshe palette
        </p>
      </div>
    </div>

    <!-- ── Bento grid ─────────────────────────────────── -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">

      <!-- Tile 1: Letter navigation (1 col) -->
      <div class="card-bordered p-5 dark:border-slate-800">
        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-4">
          Shakisha ku inyuguti
        </p>
        <LetterNav :letters="letters" compact />
      </div>

      <!-- Tile 2: Categories (2 cols) -->
      <div class="md:col-span-2 card-bordered p-5 dark:border-slate-800">
        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-4">
          Ingeri z'ikoranabuhanga
        </p>
        <div v-if="categories.length" class="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
          <button
            v-for="cat in categories"
            :key="cat.name"
            @click="browseCategory(cat.name)"
            class="group text-left px-4 py-3 rounded-xl border transition-all duration-200
                   hover:shadow-md hover:-translate-y-0.5
                   bg-white dark:bg-slate-800/60
                   border-slate-100 dark:border-slate-700/60
                   hover:border-rw-green/40 dark:hover:border-rw-green/40"
          >
            <span class="text-xl mb-1 block">{{ categoryIcon(cat.name) }}</span>
            <div class="text-sm font-semibold text-slate-800 dark:text-slate-200 leading-tight">
              {{ shortName(cat.name) }}
            </div>
            <div class="text-xs text-slate-400 dark:text-slate-500 mt-0.5 font-mono">
              {{ cat.count }}
            </div>
          </button>
        </div>
        <!-- Skeleton while loading -->
        <div v-else class="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
          <div v-for="i in 9" :key="i" class="skeleton h-16 rounded-xl"></div>
        </div>
      </div>

      <!-- Tile 3: Stats / About (full width on mobile, 3 cols on lg) -->
      <div class="md:col-span-3 card-bordered px-6 py-4 flex flex-wrap items-center gap-6 dark:border-slate-800">
        <div class="text-center px-4 border-r border-slate-100 dark:border-slate-800 last:border-0">
          <div class="font-serif text-2xl font-bold text-rw-green dark:text-rw-green-muted">
            {{ stats.total_entries ? stats.total_entries.toLocaleString() : '—' }}
          </div>
          <div class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">Amajambo</div>
        </div>
        <div class="text-center px-4 border-r border-slate-100 dark:border-slate-800 last:border-0">
          <div class="font-serif text-2xl font-bold text-rw-green dark:text-rw-green-muted">
            {{ categories.length || '—' }}
          </div>
          <div class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">Ingeri</div>
        </div>
        <div class="text-center px-4 border-r border-slate-100 dark:border-slate-800 last:border-0">
          <div class="font-serif text-2xl font-bold text-rw-green dark:text-rw-green-muted">3</div>
          <div class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">Indimi</div>
        </div>
        <div class="flex-1 text-right hidden sm:block">
          <p class="text-xs text-slate-400 dark:text-slate-500 leading-relaxed max-w-xs ml-auto">
            Inkoranyamuga y'ikoranabuhanga yateguwe na Inteko y'Umuco — Rwanda Cultural Heritage Academy, 2026.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import SearchBar from '../components/SearchBar.vue'
import LetterNav from '../components/LetterNav.vue'

const CAT_ICONS = {
  mudasobwa: '💻',
  murandasi: '🌐',
  itumanaho: '📡',
  isakazamakuru: '📰',
  ubwenge: '🤖',
  urusobe: '🎬',
  forensics: '🔍',
  ndangamuntu: '👤',
  imari: '💳',
  itangazabumenyi: '📊',
  imiraba: '📶',
  ibikoresho: '🛠️',
}

const CAT_SHORT = {
  'Ikoranabuhanga rya mudasobwa': 'Mudasobwa',
  'Ikoranabuhanga rya murandasi': 'Murandasi',
  'Itumanaho koranabuhanga': 'Itumanaho',
  'Isakazamakuru': 'Isakazamakuru',
  'Ubwenge buhangano': 'Ubwenge buhangano (AI)',
  'Urusobe ntangamakuru': 'Urusobe ntangamakuru',
  'Ikoranabuhanga ngaragazabimenyetso': 'Forensics',
  'Ikoranabuhanga ndangamuntu': 'Ndangamuntu',
  "Ikoranabuhanga ry'imari": "Ry'imari",
  "Ikoranabuhanga ry'amashusho": "Ry'amashusho",
  "Ikoranabuhanga ry'amajwi": "Ry'amajwi",
  "Ikoranabuhanga ry'itumanaho": "Ry'itumanaho",
  "Ikoranabuhanga ry'imiraba": "Ry'imiraba",
  'Ibikoresho by\'itangazamakuru': 'Itangazamakuru',
}

export default {
  name: 'HomeView',
  components: { SearchBar, LetterNav },
  props: {
    letters: { type: Array, default: () => [] },
    stats: { type: Object, default: () => ({}) },
  },
  data() {
    return { categories: [], query: '' }
  },
  async created() {
    const res = await axios.get('/api/categories')
    this.categories = res.data
  },
  methods: {
    onSearch(q) {
      if (q.trim()) this.$router.push({ path: '/search', query: { q } })
    },
    browseCategory(name) {
      this.$router.push({ path: '/search', query: { q: name.split(' ').pop() } })
    },
    shortName(cat) {
      return CAT_SHORT[cat] || cat
    },
    categoryIcon(cat) {
      const lower = cat.toLowerCase()
      for (const [key, icon] of Object.entries(CAT_ICONS)) {
        if (lower.includes(key)) return icon
      }
      return '📖'
    },
  },
}
</script>
