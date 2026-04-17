<template>
  <div class="fixed inset-0 z-[100] flex items-start justify-center pt-[12vh] px-4">
    <!-- Backdrop -->
    <div
      class="absolute inset-0 bg-black/60 backdrop-blur-sm animate-fadeIn"
      @click="$emit('close')"
    ></div>

    <!-- Panel -->
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Shakisha"
      class="relative w-full max-w-lg bg-white dark:bg-slate-900 rounded-2xl shadow-2xl
             overflow-hidden animate-scaleIn"
    >
      <!-- Input row -->
      <div class="flex items-center px-4 py-3.5 border-b border-slate-100 dark:border-slate-800">
        <svg class="w-5 h-5 text-slate-400 flex-shrink-0 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"/>
        </svg>
        <input
          ref="input"
          v-model="query"
          class="flex-1 text-base bg-transparent outline-none text-slate-900 dark:text-white
                 placeholder-slate-400 dark:placeholder-slate-500"
          placeholder="Shakisha ijambo, inyuguti..."
          autocomplete="off"
          @keydown.down.prevent="move(1)"
          @keydown.up.prevent="move(-1)"
          @keydown.enter.prevent="select"
          @keydown.esc="$emit('close')"
        />
        <kbd class="text-xs text-slate-400 border border-slate-200 dark:border-slate-700
                    dark:text-slate-500 rounded px-1.5 py-0.5 font-mono">
          Esc
        </kbd>
      </div>

      <!-- Results area -->
      <div class="max-h-[22rem] overflow-y-auto">

        <!-- No query: show letter quick-jump -->
        <div v-if="!query" class="p-4">
          <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-3 px-1">
            Inyuguti
          </p>
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="item in letters"
              :key="item.letter"
              @click="goLetter(item.letter)"
              class="w-9 h-9 rounded-lg text-sm font-semibold border transition-colors duration-100
                     bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-300
                     border-slate-200 dark:border-slate-700
                     hover:bg-rw-green hover:text-white hover:border-rw-green"
            >
              {{ item.letter }}
            </button>
          </div>
          <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 mt-4 mb-2 px-1">
            Ibikorwa
          </p>
          <button
            @click="$router.push('/'); $emit('close')"
            class="w-full text-left px-3 py-2 rounded-lg text-sm text-slate-700 dark:text-slate-300
                   hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center gap-2"
          >
            <span class="text-base">🏠</span> Ahabanza
          </button>
        </div>

        <!-- Loading -->
        <div v-else-if="loading" class="px-4 py-8 text-center text-sm text-slate-400">
          <div class="inline-block w-4 h-4 border-2 border-rw-green/30 border-t-rw-green rounded-full animate-spin mr-2"></div>
          Gushakisha...
        </div>

        <!-- Results -->
        <div v-else-if="results.length">
          <button
            v-for="(r, i) in results"
            :key="r.id"
            @click="goEntry(r)"
            class="w-full text-left px-4 py-3 flex items-center gap-3 transition-colors duration-100"
            :class="i === activeIdx
              ? 'bg-rw-green/8 dark:bg-rw-green/15'
              : 'hover:bg-slate-50 dark:hover:bg-slate-800'"
          >
            <div class="flex-1 min-w-0">
              <span class="font-serif font-semibold text-slate-900 dark:text-white">{{ r.term }}</span>
              <span v-if="r.pronunciation" class="font-serif italic text-slate-400 text-sm ml-1.5">
                ({{ r.pronunciation }})
              </span>
              <p v-if="r.english" class="text-xs text-slate-500 dark:text-slate-400 truncate mt-0.5">
                🇬🇧 {{ r.english }}
              </p>
            </div>
            <span
              v-if="r.category"
              class="text-xs px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700
                     text-slate-500 dark:text-slate-400 flex-shrink-0"
            >
              {{ shortCat(r.category) }}
            </span>
          </button>
        </div>

        <!-- Empty -->
        <div v-else class="px-4 py-10 text-center">
          <p class="text-slate-400 text-sm">Nta jambo ryabonetse kuri "<strong class="text-slate-600 dark:text-slate-300">{{ query }}</strong>"</p>
          <p class="text-xs text-slate-400 mt-1">Gerageza ijambo rindi</p>
        </div>
      </div>

      <!-- Footer hint -->
      <div class="px-4 py-2.5 border-t border-slate-100 dark:border-slate-800 flex items-center gap-3 text-xs text-slate-400">
        <span><kbd class="font-mono border border-slate-200 dark:border-slate-700 rounded px-1">↑↓</kbd> kugenda</span>
        <span><kbd class="font-mono border border-slate-200 dark:border-slate-700 rounded px-1">↵</kbd> gufungura</span>
        <span><kbd class="font-mono border border-slate-200 dark:border-slate-700 rounded px-1">Esc</kbd> guhunga</span>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

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
  name: 'CommandPalette',
  emits: ['close', 'navigate'],
  props: {
    letters: { type: Array, default: () => [] },
  },
  data() {
    return { query: '', results: [], loading: false, activeIdx: -1, timer: null }
  },
  mounted() {
    this._trigger = document.activeElement
    document.body.style.overflow = 'hidden'
    this.$nextTick(() => this.$refs.input?.focus())
  },
  beforeUnmount() {
    document.body.style.overflow = ''
    this._trigger?.focus()
  },
  watch: {
    query(v) {
      this.activeIdx = -1
      clearTimeout(this.timer)
      if (!v.trim()) { this.results = []; this.loading = false; return }
      this.loading = true
      this.timer = setTimeout(async () => {
        try {
          const res = await axios.get('/api/search', { params: { q: v, per_page: 8 } })
          this.results = res.data.results || []
        } catch {
          this.results = []
        } finally {
          this.loading = false
        }
      }, 200)
    },
  },
  methods: {
    move(dir) {
      const max = this.results.length - 1
      if (max < 0) return
      this.activeIdx = Math.max(-1, Math.min(max, this.activeIdx + dir))
    },
    select() {
      if (this.activeIdx >= 0 && this.results[this.activeIdx]) {
        this.goEntry(this.results[this.activeIdx])
      } else if (this.query.trim()) {
        this.$router.push({ path: '/search', query: { q: this.query } })
        this.$emit('close')
      }
    },
    goEntry(r) {
      this.$router.push(`/entry/${r.id}`)
      this.$emit('close')
    },
    goLetter(l) {
      this.$router.push(`/browse/${l}`)
      this.$emit('close')
    },
    shortCat(cat) {
      return SHORT_CAT[cat] || cat.split(' ').slice(-1)[0]
    },
  },
}
</script>
