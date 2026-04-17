<template>
  <div>
    <!-- ── Mobile letter strip ──────────────────────── -->
    <div class="md:hidden mb-4 -mx-4 px-4 overflow-x-auto">
      <div class="flex gap-1.5 pb-1 min-w-max">
        <router-link
          v-for="item in letters"
          :key="item.letter"
          :to="`/browse/${item.letter}`"
          class="w-9 h-9 flex-shrink-0 flex items-center justify-center rounded-lg text-sm font-semibold
                 border transition-colors duration-100"
          :class="$route.params.letter === item.letter
            ? 'bg-rw-green text-white border-rw-green'
            : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'"
        >
          {{ item.letter }}
        </router-link>
      </div>
    </div>

    <!-- ── Three-pane layout ────────────────────────── -->
    <div class="flex gap-4">

      <!-- Pane 1: Letter rail (desktop) -->
      <aside class="w-36 flex-shrink-0 hidden md:block">
        <div class="sticky top-20 card-bordered shadow-sm p-3">
          <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-2 text-center">
            Inyuguti
          </p>
          <LetterNav :letters="letters" :active="$route.params.letter" vertical />
        </div>
      </aside>

      <!-- Pane 2: Entry list -->
      <div class="flex-1 min-w-0">
        <!-- Header row -->
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 v-if="isSearch" class="font-serif text-xl font-bold text-slate-900 dark:text-white">
              Ibisubizo bya "{{ $route.query.q }}"
            </h2>
            <h2 v-else class="font-serif text-xl font-bold text-slate-900 dark:text-white">
              Inyuguti "{{ $route.params.letter }}"
            </h2>
            <p v-if="total !== null" class="text-sm text-slate-400 dark:text-slate-500 mt-0.5">
              {{ total.toLocaleString() }} {{ total === 1 ? 'ijambo' : 'amajambo' }}
            </p>
          </div>
          <!-- View toggle -->
          <div class="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
            <button
              v-for="v in ['list', 'compact']"
              :key="v"
              @click="viewMode = v"
              class="px-3 py-1.5 rounded-md text-xs font-semibold transition-all duration-150"
              :class="viewMode === v
                ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'"
            >
              {{ v === 'list' ? '≡ Urutonde' : '⊟ Ngufi' }}
            </button>
          </div>
        </div>

        <!-- Skeleton loading -->
        <div v-if="loading" class="space-y-px">
          <div
            v-for="i in 6"
            :key="i"
            class="card-bordered p-5 animate-slideUp"
            :style="`animation-delay: ${i * 40}ms`"
          >
            <div class="flex items-center gap-3 mb-2">
              <div class="skeleton h-5 w-32 rounded"></div>
              <div class="skeleton h-4 w-20 rounded"></div>
              <div class="skeleton h-4 w-16 rounded-full"></div>
            </div>
            <div class="skeleton h-3.5 w-48 rounded mb-1.5"></div>
            <div class="skeleton h-3.5 w-64 rounded"></div>
          </div>
        </div>

        <!-- No results -->
        <div v-else-if="entries.length === 0" class="card-bordered px-8 py-16 text-center">
          <div class="text-4xl mb-4">🔍</div>
          <p class="font-serif text-lg text-slate-600 dark:text-slate-300 mb-1">Nta jambo ryabonetse</p>
          <p class="text-sm text-slate-400 dark:text-slate-500 mb-5">Gerageza ijambo rindi cyangwa inyuguti</p>
          <router-link to="/" class="text-rw-green hover:text-rw-green-dark text-sm font-medium">
            ← Garuka ahabanza
          </router-link>
        </div>

        <!-- Entry list -->
        <div v-else class="card-bordered divide-y divide-slate-100 dark:divide-slate-800 overflow-hidden">
          <EntryCard
            v-for="entry in entries"
            :key="entry.id"
            :entry="entry"
            :compact="viewMode === 'compact'"
            :selected="selectedId === entry.id"
            @select="selectEntry(entry)"
          />
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 mt-6">
          <button
            v-if="page > 1"
            @click="goToPage(page - 1)"
            class="px-4 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200
                   dark:border-slate-700 text-sm text-slate-700 dark:text-slate-300
                   hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
          >
            ← Iya mbere
          </button>
          <div class="flex items-center gap-1">
            <span class="px-3 py-2 text-sm text-slate-500 dark:text-slate-400">
              {{ page }} / {{ totalPages }}
            </span>
          </div>
          <button
            v-if="page < totalPages"
            @click="goToPage(page + 1)"
            class="px-4 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200
                   dark:border-slate-700 text-sm text-slate-700 dark:text-slate-300
                   hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
          >
            Iya nyuma →
          </button>
        </div>
      </div>

      <!-- Pane 3: Entry preview (desktop, when selected) -->
      <aside
        v-if="selectedEntry"
        class="w-80 flex-shrink-0 hidden lg:block animate-slideInRight"
      >
        <div class="sticky top-20 card-bordered overflow-hidden">
          <!-- Close -->
          <div class="flex items-center justify-between px-5 pt-4 pb-0">
            <span class="text-xs text-slate-400 dark:text-slate-500 font-semibold uppercase tracking-wider">
              Ibisobanuro
            </span>
            <button
              @click="selectedEntry = null; selectedId = null"
              class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 text-lg leading-none w-7 h-7 flex items-center justify-center rounded"
            >×</button>
          </div>

          <div class="px-5 py-4">
            <!-- Term -->
            <div class="mb-4 pb-4 border-b border-slate-100 dark:border-slate-800">
              <dfn class="font-serif text-2xl font-bold text-slate-900 dark:text-white not-italic block">
                {{ selectedEntry.term }}
              </dfn>
              <span v-if="selectedEntry.pronunciation"
                class="font-serif italic text-slate-400 dark:text-slate-500 text-sm">
                ({{ selectedEntry.pronunciation }})
              </span>
              <span v-if="selectedEntry.category"
                :class="catClass(selectedEntry.category)"
                class="cat-badge mt-1 block w-fit">
                {{ shortCat(selectedEntry.category) }}
              </span>
            </div>

            <!-- Translations -->
            <div class="space-y-2 text-sm mb-4">
              <div v-if="selectedEntry.synonym" class="flex gap-2">
                <span class="text-slate-400 dark:text-slate-500 flex-shrink-0 w-5 text-center">≈</span>
                <span class="italic text-slate-600 dark:text-slate-400">{{ selectedEntry.synonym }}</span>
              </div>
              <div v-if="selectedEntry.english" class="flex gap-2">
                <span class="flex-shrink-0 text-sm" title="Icyongereza">🇬🇧</span>
                <span class="italic text-slate-700 dark:text-slate-300">{{ selectedEntry.english }}</span>
              </div>
              <div v-if="selectedEntry.french" class="flex gap-2">
                <span class="flex-shrink-0 text-sm" title="Igifaransa">🇫🇷</span>
                <span class="italic text-slate-600 dark:text-slate-400">{{ selectedEntry.french }}</span>
              </div>
            </div>

            <!-- Definition -->
            <p v-if="selectedEntry.definition"
              class="text-sm text-slate-700 dark:text-slate-300 leading-relaxed border-t border-slate-100 dark:border-slate-800 pt-3">
              {{ selectedEntry.definition }}
            </p>

            <!-- Image -->
            <div v-if="selectedEntry.images && selectedEntry.images.length" class="mt-4">
              <img
                :src="`/images/${selectedEntry.images[0]}`"
                :alt="selectedEntry.term"
                class="w-full rounded-xl object-contain max-h-40 bg-slate-50 dark:bg-slate-800"
                loading="lazy"
              />
            </div>

            <!-- Full entry link -->
            <router-link
              :to="`/entry/${selectedEntry.id}`"
              class="mt-4 flex items-center justify-center gap-2 w-full py-2.5 rounded-xl
                     bg-rw-green text-white text-sm font-semibold hover:bg-rw-green-dark
                     transition-colors duration-150"
            >
              Reba byuzuye →
            </router-link>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import EntryCard from '../components/EntryCard.vue'
import LetterNav from '../components/LetterNav.vue'

const CATEGORY_COLORS = {
  'mudasobwa': 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  'murandasi': 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
  'itumanaho': 'bg-violet-50 text-violet-700 dark:bg-violet-900/30 dark:text-violet-400',
  'isakazamakuru': 'bg-orange-50 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
  'ubwenge': 'bg-pink-50 text-pink-700 dark:bg-pink-900/30 dark:text-pink-400',
  'urusobe': 'bg-teal-50 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400',
  'forensics': 'bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  'ndangamuntu': 'bg-indigo-50 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400',
  'imari': 'bg-yellow-50 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
  'itangazabumenyi': 'bg-cyan-50 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400',
}

const SHORT_CAT = {
  'Ikoranabuhanga rya mudasobwa': 'Mudasobwa',
  'Ikoranabuhanga rya murandasi': 'Murandasi',
  'Itumanaho koranabuhanga': 'Itumanaho',
  'Isakazamakuru': 'Isakazamakuru',
  'Ubwenge buhangano': 'AI',
  'Urusobe ntangamakuru': 'Multimedia',
  'Ikoranabuhanga ngaragazabimenyetso': 'Forensics',
  'Ikoranabuhanga ndangamuntu': 'Ndangamuntu',
  "Ikoranabuhanga ry'imari": 'Imari',
  'Itangazabumenyi koranabuhanga': 'ICT',
}

export default {
  name: 'BrowseView',
  components: { EntryCard, LetterNav },
  props: {
    letters: { type: Array, default: () => [] },
  },
  data() {
    return {
      entries: [],
      total: null,
      page: 1,
      perPage: 50,
      loading: false,
      viewMode: 'list',
      selectedId: null,
      selectedEntry: null,
    }
  },
  computed: {
    isSearch() { return this.$route.path === '/search' },
    totalPages() { return Math.ceil((this.total || 0) / this.perPage) },
  },
  watch: {
    $route() { this.page = 1; this.selectedEntry = null; this.selectedId = null; this.fetch() },
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
    goToPage(p) { this.page = p; this.selectedEntry = null; this.selectedId = null; this.fetch(); window.scrollTo(0, 0) },
    selectEntry(entry) {
      if (this.selectedId === entry.id) {
        this.selectedId = null
        this.selectedEntry = null
      } else {
        this.selectedId = entry.id
        this.selectedEntry = entry
      }
    },
    catClass(cat) {
      const lower = (cat || '').toLowerCase()
      for (const [key, cls] of Object.entries(CATEGORY_COLORS)) {
        if (lower.includes(key)) return cls
      }
      return 'bg-slate-100 text-slate-600'
    },
    shortCat(cat) {
      return SHORT_CAT[cat] || cat.split(' ').slice(-1)[0]
    },
  },
}
</script>
