<template>
  <div class="relative w-full" ref="root">
    <input
      ref="inputEl"
      v-model="localQuery"
      type="search"
      :placeholder="placeholder"
      :class="[
        'w-full px-4 pr-20 bg-white dark:bg-slate-800 rounded-xl border-2',
        'text-slate-900 dark:text-white font-sans',
        'focus:outline-none focus:border-rw-green focus:ring-2 focus:ring-rw-green/10',
        'placeholder-slate-400 dark:placeholder-slate-500',
        'border-slate-200 dark:border-slate-700',
        'transition-colors duration-150',
        size === 'lg' ? 'py-4 text-lg rounded-2xl' : 'py-2.5 text-sm',
      ]"
      autocomplete="off"
      @keydown.enter="submit"
      @keydown.down.prevent="moveDropdown(1)"
      @keydown.up.prevent="moveDropdown(-1)"
      @keydown.esc="closeDropdown"
      @focus="onFocus"
      @blur="onBlur"
    />

    <!-- Clear button -->
    <button
      v-if="localQuery"
      @click="clear"
      class="absolute right-10 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600
             dark:hover:text-slate-300 text-lg w-6 h-6 flex items-center justify-center"
      aria-label="Siba"
      tabindex="-1"
    >×</button>

    <!-- Search icon -->
    <button
      @click="submit"
      class="absolute right-3 top-1/2 -translate-y-1/2 text-rw-green hover:text-rw-green-dark
             transition-colors duration-150"
      aria-label="Shakisha"
      tabindex="-1"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"/>
      </svg>
    </button>

    <!-- Dropdown: autocomplete + recent searches -->
    <div
      v-if="showDropdown && (dropdownItems.length > 0 || recentSearches.length > 0)"
      class="absolute top-full left-0 right-0 mt-1.5 bg-white dark:bg-slate-900 rounded-xl
             border border-slate-100 dark:border-slate-800 shadow-xl z-50 overflow-hidden
             animate-slideUp"
    >
      <!-- Recent searches (when no query) -->
      <template v-if="!localQuery.trim() && recentSearches.length">
        <div class="px-3 pt-2.5 pb-1 flex items-center justify-between">
          <span class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
            Byasakazwe vuba
          </span>
          <button
            @click="clearRecent"
            class="text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
          >Siba</button>
        </div>
        <div>
          <button
            v-for="(r, i) in recentSearches"
            :key="r"
            @mousedown.prevent="pickRecent(r)"
            class="w-full text-left px-4 py-2.5 text-sm flex items-center gap-2.5 transition-colors duration-100"
            :class="dropdownIdx === i
              ? 'bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white'
              : 'text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800'"
          >
            <svg class="w-3.5 h-3.5 text-slate-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"/>
            </svg>
            {{ r }}
          </button>
        </div>
      </template>

      <!-- Autocomplete results -->
      <template v-else-if="localQuery.trim()">
        <div v-if="loadingAuto" class="px-4 py-3 text-sm text-slate-400 dark:text-slate-500">
          Gushakisha...
        </div>
        <div v-else-if="dropdownItems.length">
          <router-link
            v-for="(item, i) in dropdownItems"
            :key="item.id"
            :to="`/entry/${item.id}`"
            @click="onAutocompleteClick(item)"
            @mousedown.prevent
            class="flex items-center gap-3 px-4 py-2.5 transition-colors duration-100"
            :class="dropdownIdx === i
              ? 'bg-slate-50 dark:bg-slate-800'
              : 'hover:bg-slate-50 dark:hover:bg-slate-800'"
          >
            <div class="flex-1 min-w-0">
              <span class="font-serif font-semibold text-slate-900 dark:text-white text-sm">{{ item.term }}</span>
              <span v-if="item.pronunciation" class="font-serif italic text-slate-400 text-xs ml-1">
                ({{ item.pronunciation }})
              </span>
              <p v-if="item.english" class="text-xs text-slate-500 dark:text-slate-400 truncate italic mt-0.5">
                🇬🇧 {{ item.english }}
              </p>
            </div>
            <span
              v-if="item.category"
              class="text-xs px-1.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700
                     text-slate-500 dark:text-slate-400 flex-shrink-0"
            >
              {{ shortCat(item.category) }}
            </span>
          </router-link>

          <!-- Search all results -->
          <div class="border-t border-slate-100 dark:border-slate-800">
            <button
              @mousedown.prevent="submit"
              class="w-full text-left px-4 py-2.5 text-xs text-rw-green hover:bg-slate-50
                     dark:hover:bg-slate-800 font-medium transition-colors duration-100"
            >
              Reba ibisubizo byose kuri "{{ localQuery }}" →
            </button>
          </div>
        </div>
        <div v-else class="px-4 py-3 text-sm text-slate-400 dark:text-slate-500">
          Nta jambo ryabonetse
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const RECENT_KEY = 'rw-recent-searches'
const MAX_RECENT = 6

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
  name: 'SearchBar',
  props: {
    modelValue: { type: String, default: '' },
    placeholder: { type: String, default: 'Shakisha ijambo... Search... Rechercher...' },
    autofocus: { type: Boolean, default: false },
    size: { type: String, default: 'md' },
  },
  emits: ['update:modelValue', 'search'],
  data() {
    return {
      localQuery: this.modelValue,
      dropdownItems: [],
      dropdownIdx: -1,
      showDropdown: false,
      loadingAuto: false,
      recentSearches: [],
      timer: null,
      autoTimer: null,
    }
  },
  mounted() {
    if (this.autofocus) this.$refs.inputEl?.focus()
    this.recentSearches = this.loadRecent()
  },
  watch: {
    modelValue(v) { this.localQuery = v },
    localQuery(v) {
      this.$emit('update:modelValue', v)
      this.dropdownIdx = -1
      clearTimeout(this.autoTimer)
      if (!v.trim()) {
        this.dropdownItems = []
        this.loadingAuto = false
        return
      }
      this.loadingAuto = true
      this.autoTimer = setTimeout(async () => {
        try {
          const res = await axios.get('/api/search', { params: { q: v, per_page: 6 } })
          this.dropdownItems = res.data.results || []
        } catch {
          this.dropdownItems = []
        } finally {
          this.loadingAuto = false
        }
      }, 200)
    },
  },
  methods: {
    submit() {
      const q = this.localQuery.trim()
      if (!q) return
      this.saveRecent(q)
      this.closeDropdown()
      clearTimeout(this.timer)
      this.$emit('search', this.localQuery)
    },
    clear() {
      this.localQuery = ''
      this.dropdownItems = []
      this.$refs.inputEl?.focus()
    },
    onFocus() {
      this.showDropdown = true
    },
    onBlur() {
      setTimeout(() => { this.showDropdown = false }, 150)
    },
    closeDropdown() {
      this.showDropdown = false
      this.dropdownIdx = -1
    },
    moveDropdown(dir) {
      const list = this.localQuery.trim() ? this.dropdownItems : this.recentSearches
      const max = list.length - 1
      if (max < 0) return
      this.dropdownIdx = Math.max(-1, Math.min(max, this.dropdownIdx + dir))
    },
    pickRecent(q) {
      this.localQuery = q
      this.$nextTick(() => this.submit())
    },
    onAutocompleteClick(item) {
      this.saveRecent(item.term)
      this.closeDropdown()
    },
    loadRecent() {
      try { return JSON.parse(localStorage.getItem(RECENT_KEY) || '[]') } catch { return [] }
    },
    saveRecent(q) {
      const list = [q, ...this.recentSearches.filter(r => r !== q)].slice(0, MAX_RECENT)
      this.recentSearches = list
      localStorage.setItem(RECENT_KEY, JSON.stringify(list))
    },
    clearRecent() {
      this.recentSearches = []
      localStorage.removeItem(RECENT_KEY)
    },
    shortCat(cat) {
      return SHORT_CAT[cat] || cat.split(' ').slice(-1)[0]
    },
  },
}
</script>
