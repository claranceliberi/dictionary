<template>
  <div>
    <Ribbon orientation="v" />
    <div class="wrap">
      <LetterNav variant="strip" :letters="letters" :active="letter" />
      <div class="page">
        <LetterNav variant="tabs" :letters="letters" :active="letter" />
        <div class="list">
          <template v-if="isSearch">
            <h1 class="results-title">Ibisubizo bya “{{ $route.query.q }}”</h1>
          </template>
          <div v-else class="roundel">{{ letter }}</div>
          <div v-if="total !== null" class="count">{{ countLabel(total) }}</div>

          <p v-if="loading" class="state">Gushakisha…</p>
          <div v-else-if="!entries.length" class="state">
            <Icon name="search-x" :size="34" class="state-icon" />
            <p class="state-title">Nta jambo ryabonetse</p>
            <p>Gerageza ijambo rindi cyangwa inyuguti</p>
            <router-link to="/">← Garuka ahabanza</router-link>
          </div>
          <template v-else>
            <EntryCard
              v-for="(entry, i) in entries"
              :key="entry.id"
              :entry="entry"
              :q="isSearch ? $route.query.q : ''"
              class="rise"
              :style="{ '--i': Math.min(i, 10) }"
            />
            <Pager :page="page" :total-pages="totalPages" @go="goToPage" />
          </template>

          <div v-if="!isSearch" class="runhead runfoot">Inkoranyamuga y'ikoranabuhanga</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import EntryCard from '../components/EntryCard.vue'
import Icon from '../components/Icon.vue'
import { countLabel } from '../format.js'
import LetterNav from '../components/LetterNav.vue'
import Pager from '../components/Pager.vue'
import Ribbon from '../components/Ribbon.vue'

const PER_PAGE = 50

export default {
  name: 'BrowseView',
  components: { EntryCard, Icon, LetterNav, Pager, Ribbon },
  props: {
    letters: { type: Array, default: () => [] },
  },
  data() {
    return { entries: [], total: null, page: 1, loading: false }
  },
  computed: {
    isSearch() { return this.$route.path === '/search' },
    letter() { return this.isSearch ? '' : (this.$route.params.letter || '').toUpperCase() },
    totalPages() { return Math.ceil((this.total || 0) / PER_PAGE) },
  },
  watch: {
    $route() { this.page = 1; this.fetch() },
  },
  created() { this.fetch() },
  methods: {
    countLabel,
    async fetch() {
      this.loading = true
      this.total = null
      try {
        const res = this.isSearch
          ? await axios.get('/api/search', { params: { q: this.$route.query.q, page: this.page, per_page: PER_PAGE } })
          : await axios.get('/api/entries', { params: { letter: this.letter, page: this.page, per_page: PER_PAGE } })
        this.entries = this.isSearch ? res.data.results : res.data.entries
        this.total = res.data.total
      } catch {
        this.entries = []
        this.total = 0
      } finally {
        this.loading = false
      }
    },
    goToPage(p) {
      this.page = p
      this.fetch()
      window.scrollTo(0, 0)
    },
  },
}
</script>
