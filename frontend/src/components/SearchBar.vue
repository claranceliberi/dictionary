<template>
  <div class="search-box">
    <form class="search" role="search" @submit.prevent="onEnter">
      <input
        ref="inputEl"
        v-model="localQuery"
        type="search"
        :placeholder="placeholder"
        aria-label="Shakisha ijambo"
        autocomplete="off"
        @keydown.down.prevent="moveDropdown(1)"
        @keydown.up.prevent="moveDropdown(-1)"
        @keydown.esc="closeDropdown"
        @focus="onFocus"
        @blur="onBlur"
      />
      <button type="submit">Shakisha</button>
    </form>

    <div
      v-if="showDropdown && (localQuery.trim() || recentSearches.length)"
      class="sdrop"
    >
      <template v-if="!localQuery.trim()">
        <div class="sdrop-head">
          <span>Byasakazwe vuba</span>
          <button type="button" @mousedown.prevent="clearRecent">Siba</button>
        </div>
        <button
          v-for="(r, i) in recentSearches"
          :key="r"
          type="button"
          class="sdrop-row"
          :class="{ on: dropdownIdx === i }"
          @mousedown.prevent="pickRecent(r)"
        >{{ r }}</button>
      </template>

      <template v-else>
        <div v-if="loadingAuto" class="sdrop-note">Gushakisha…</div>
        <template v-else-if="dropdownItems.length">
          <router-link
            v-for="(item, i) in dropdownItems"
            :key="item.id"
            :to="`/entry/${item.id}`"
            class="sdrop-row"
            :class="{ on: dropdownIdx === i }"
            @mousedown.prevent
            @click="onAutocompleteClick(item)"
          >
            <span class="hw">{{ item.term }}</span>
            <span v-if="item.pronunciation" class="pr">({{ item.pronunciation }})</span>
            <span v-if="item.english" class="en">{{ splitTerms(item.english).main }}</span>
          </router-link>
          <button type="button" class="sdrop-all" @mousedown.prevent="submit">
            Reba ibisubizo byose kuri “{{ localQuery }}” →
          </button>
        </template>
        <div v-else class="sdrop-note">Nta jambo ryabonetse</div>
      </template>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { splitTerms } from '../format.js'

const RECENT_KEY = 'rw-recent-searches'
const MAX_RECENT = 6

export default {
  name: 'SearchBar',
  props: {
    modelValue: { type: String, default: '' },
    placeholder: { type: String, default: 'Shakisha ijambo…' },
    autofocus: { type: Boolean, default: false },
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
      autoController: null,
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
      this.autoController?.abort()
      if (!v.trim()) {
        this.dropdownItems = []
        this.loadingAuto = false
        return
      }
      this.loadingAuto = true
      this.autoTimer = setTimeout(async () => {
        this.autoController = new AbortController()
        try {
          const res = await axios.get('/api/search', {
            params: { q: v, per_page: 6 },
            signal: this.autoController.signal,
          })
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
    focus() {
      this.$refs.inputEl?.focus()
    },
    onEnter() {
      if (this.dropdownIdx >= 0) {
        const list = this.localQuery.trim() ? this.dropdownItems : this.recentSearches
        const item = list[this.dropdownIdx]
        if (item) {
          if (typeof item === 'string') { this.pickRecent(item); return }
          this.onAutocompleteClick(item)
          this.$router.push(`/entry/${item.id}`)
          return
        }
      }
      this.submit()
    },
    submit() {
      const q = this.localQuery.trim()
      if (!q) return
      this.saveRecent(q)
      this.closeDropdown()
      clearTimeout(this.autoTimer)
      this.loadingAuto = false
      this.$emit('search', q)
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
    splitTerms,
  },
}
</script>
