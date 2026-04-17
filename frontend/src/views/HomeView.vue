<template>
  <div>
    <!-- Hero -->
    <div class="text-center py-14 mb-8">
      <h2 class="font-serif text-4xl font-bold text-slate-900 mb-3">
        Inkoranyamuga y'Ikoranabuhanga
      </h2>
      <p class="text-slate-500 mb-1">
        Inteko y'Umuco — Rwanda Cultural Heritage Academy, 2026
      </p>
      <p v-if="stats.total_entries" class="text-sm text-slate-400 mb-8">
        {{ stats.total_entries.toLocaleString() }} amajambo · Ikinyarwanda · Icyongereza · Igifaransa
      </p>
      <div class="max-w-xl mx-auto">
        <SearchBar
          v-model="query"
          size="lg"
          autofocus
          @search="onSearch"
        />
      </div>
    </div>

    <!-- Letter navigation -->
    <div class="mb-8">
      <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 text-center">
        Shakisha ku inyuguti
      </p>
      <LetterNav :letters="letters" />
    </div>

    <!-- Category grid -->
    <div>
      <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4 text-center">
        Ingeri z'ikoranabuhanga
      </p>
      <div v-if="categories.length" class="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <button
          v-for="cat in categories"
          :key="cat.name"
          @click="browseCategory(cat.name)"
          class="text-left px-4 py-3 bg-white rounded-xl border border-slate-100
                 border-l-4 border-l-rw-green shadow-sm
                 hover:shadow-md hover:-translate-y-px transition-all duration-150"
        >
          <div class="text-sm font-semibold text-slate-800 leading-tight">{{ shortName(cat.name) }}</div>
          <div class="text-xs text-slate-400 mt-0.5">{{ cat.count }} amuga</div>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import SearchBar from '../components/SearchBar.vue'
import LetterNav from '../components/LetterNav.vue'

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
      if (q.trim()) {
        this.$router.push({ path: '/search', query: { q } })
      }
    },
    browseCategory(name) {
      this.$router.push({ path: '/search', query: { q: name.split(' ').pop() } })
    },
    shortName(cat) {
      const map = {
        'Ikoranabuhanga rya mudasobwa': 'Ikoranabuhanga rya mudasobwa',
        'Ikoranabuhanga rya murandasi': 'Ikoranabuhanga rya murandasi',
        'Itumanaho koranabuhanga': 'Itumanaho koranabuhanga',
        'Isakazamakuru': 'Isakazamakuru',
        'Ubwenge buhangano': 'Ubwenge buhangano (AI)',
        'Urusobe ntangamakuru': 'Urusobe ntangamakuru',
        'Ikoranabuhanga ngaragazabimenyetso': 'Ikoranabuhanga ngaragazabimenyetso',
        'Ikoranabuhanga ndangamuntu': 'Ikoranabuhanga ndangamuntu',
        "Ikoranabuhanga ry'imari": "Ikoranabuhanga ry'imari",
        'Itangazabumenyi koranabuhanga': 'Itangazabumenyi koranabuhanga',
      }
      return map[cat] || cat
    },
  },
}
</script>
