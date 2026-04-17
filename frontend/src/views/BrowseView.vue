<template>
  <div class="flex gap-6">
    <!-- Sidebar: letter index -->
    <aside class="w-36 flex-shrink-0 hidden md:block">
      <div class="sticky top-6 bg-white rounded-xl border border-slate-100 shadow-sm p-3">
        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 text-center">
          Inyuguti
        </p>
        <LetterNav :letters="letters" :active="$route.params.letter" vertical />
      </div>
    </aside>

    <!-- Main content -->
    <div class="flex-1 min-w-0">
      <!-- Header -->
      <div class="mb-4">
        <h2 v-if="isSearch" class="font-serif text-xl font-bold text-slate-900">
          Ibisubizo bya "{{ $route.query.q }}"
        </h2>
        <h2 v-else class="font-serif text-xl font-bold text-slate-900">
          Iynguti "{{ $route.params.letter }}"
        </h2>
        <p v-if="total !== null" class="text-sm text-slate-400">
          {{ total.toLocaleString() }} {{ total === 1 ? 'ijambo' : 'amajambo' }}
        </p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12 text-slate-400">
        Gushakisha...
      </div>

      <!-- No results -->
      <div v-else-if="entries.length === 0" class="text-center py-12">
        <p class="text-slate-500 mb-2">Nta jambo ryabonetse.</p>
        <router-link to="/" class="text-rw-green hover:underline text-sm">← Garuka imbere</router-link>
      </div>

      <!-- Entry list -->
      <div v-else class="bg-white rounded-2xl shadow-sm border border-slate-100 px-6 divide-y divide-slate-100">
        <EntryCard v-for="entry in entries" :key="entry.id" :entry="entry" />
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-6">
        <button
          v-if="page > 1"
          @click="goToPage(page - 1)"
          class="px-4 py-2 rounded-lg bg-white border border-slate-200 text-sm text-slate-700 hover:bg-slate-50"
        >← Iya mbere</button>
        <span class="px-4 py-2 text-sm text-slate-500">
          {{ page }} / {{ totalPages }}
        </span>
        <button
          v-if="page < totalPages"
          @click="goToPage(page + 1)"
          class="px-4 py-2 rounded-lg bg-white border border-slate-200 text-sm text-slate-700 hover:bg-slate-50"
        >Iya nyuma →</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import EntryCard from '../components/EntryCard.vue'
import LetterNav from '../components/LetterNav.vue'

export default {
  name: 'BrowseView',
  components: { EntryCard, LetterNav },
  props: {
    letters: { type: Array, default: () => [] },
  },
  data() {
    return { entries: [], total: null, page: 1, perPage: 50, loading: false }
  },
  computed: {
    isSearch() { return this.$route.path === '/search' },
    totalPages() { return Math.ceil((this.total || 0) / this.perPage) },
  },
  watch: {
    $route() { this.page = 1; this.fetch() },
  },
  created() { this.fetch() },
  methods: {
    async fetch() {
      this.loading = true
      try {
        if (this.isSearch) {
          const q = this.$route.query.q
          const res = await axios.get('/api/search', {
            params: { q, page: this.page, per_page: this.perPage },
          })
          this.entries = res.data.results
          this.total = res.data.total
        } else {
          const letter = this.$route.params.letter
          const res = await axios.get('/api/entries', {
            params: { letter, page: this.page, per_page: this.perPage },
          })
          this.entries = res.data.entries
          this.total = res.data.total
        }
      } finally {
        this.loading = false
      }
    },
    goToPage(p) { this.page = p; this.fetch(); window.scrollTo(0, 0) },
  },
}
</script>
