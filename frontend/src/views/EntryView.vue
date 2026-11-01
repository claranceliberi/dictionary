<template>
  <div>
    <Ribbon orientation="v" />
    <div class="wrap">
      <p v-if="loading" class="state">Gushakisha…</p>

      <article v-else-if="entry" class="entry entry-grid">
        <div class="entry-main">
          <div class="crumb-row">
            <nav class="crumb" aria-label="Aho uri">
              <router-link to="/" class="crumb-home"><Icon name="home" :size="15" />Ahabanza</router-link> ›
              <router-link :to="`/browse/${letter}`">{{ letter }}</router-link> ›
              {{ entry.term }}
            </nav>
            <a href="#" class="back" @click.prevent="$router.back()"><Icon name="arrow-left" :size="15" />Subira inyuma</a>
          </div>

          <div class="entry-top">
            <div>
              <h1>{{ entry.term }}</h1>
              <div v-if="entry.pronunciation" class="pr">({{ entry.pronunciation }})</div>
            </div>
            <img v-if="image" class="img-phone" :src="image" :alt="entry.term" />
          </div>

          <div v-if="definition" class="lead">
            <span class="lb">Inshoza</span>
            <p>{{ definition }}</p>
          </div>

          <div class="fields">
            <div v-if="synonyms.length" class="f">
              <span class="lb">Impuzanyito</span>
              <span>
                <template v-for="(s, i) in synonyms" :key="i">
                  <template v-if="i">; </template>
                  <b v-if="i === 0">{{ s.term }}</b><template v-else>{{ s.term }}</template>
                  <small v-if="s.pron"> ({{ s.pron }})</small>
                </template>
              </span>
            </div>
            <div v-if="english.main" class="f">
              <span class="lb">Icyongereza</span>
              <span><b>{{ english.main }}</b><template v-if="english.rest.length">; {{ english.rest.join('; ') }}</template></span>
            </div>
            <div v-if="french.main" class="f">
              <span class="lb">Igifaransa</span>
              <span><b>{{ french.main }}</b><template v-if="french.rest.length">; {{ french.rest.join('; ') }}</template></span>
            </div>
            <div v-if="entry.category" class="f">
              <span class="lb">Igitsibo</span>
              <span><router-link :to="categoryLink(entry.category)" class="cat">{{ entry.category }}</router-link></span>
            </div>
          </div>
        </div>

        <aside class="entry-side">
          <img v-if="image" class="img-side" :src="image" :alt="entry.term" />
          <div class="side-acts">
            <button type="button" class="act share" @click="share">
              <Icon :name="shareCopied ? 'check' : 'share'" />{{ shareCopied ? 'Yakopwe' : 'Sangiza' }}
            </button>
            <button type="button" class="act copy" @click="copyLink">
              <Icon :name="copied ? 'check' : 'link'" />{{ copied ? 'Yakopwe' : 'Kopa aderesi' }}
            </button>
            <router-link v-if="entry.category" :to="categoryLink(entry.category)" class="act primary">
              Andi magambo y'iki gitsibo<Icon name="arrow-right" />
            </router-link>
          </div>
        </aside>
      </article>

      <div v-else class="state">
        <Icon name="search-x" :size="34" class="state-icon" />
        <p class="state-title">Ijambo ntiryabonetse</p>
        <router-link to="/">← Garuka ahabanza</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import Icon from '../components/Icon.vue'
import Ribbon from '../components/Ribbon.vue'
import { splitTerms, splitSynonyms, stripMarks, categoryLink } from '../format.js'

export default {
  name: 'EntryView',
  components: { Icon, Ribbon },
  data() {
    return { entry: null, loading: false, copied: false, shareCopied: false }
  },
  computed: {
    image() { return this.entry?.images?.length ? `/images/${this.entry.images[0]}` : null },
    letter() { return (this.entry?.letter || this.entry?.term?.[0] || '').toUpperCase() },
    synonyms() { return splitSynonyms(this.entry?.synonym) },
    definition() { return stripMarks(this.entry?.definition) },
    english() { return splitTerms(this.entry?.english) },
    french() { return splitTerms(this.entry?.french) },
  },
  watch: {
    '$route.params.id'() { this.fetch() },
  },
  created() { this.fetch() },
  methods: {
    categoryLink,
    async fetch() {
      if (!this.$route.params.id) return
      this.loading = true
      try {
        this.entry = (await axios.get(`/api/entries/${this.$route.params.id}`)).data
      } catch {
        this.entry = null
      } finally {
        this.loading = false
      }
    },
    async copy(flag) {
      try {
        await navigator.clipboard.writeText(window.location.href)
        this[flag] = true
        setTimeout(() => { this[flag] = false }, 2000)
      } catch { /* clipboard blocked: leave the label unchanged */ }
    },
    copyLink() {
      return this.copy('copied')
    },
    // The phone's share sheet where there is one (most phones, Safari); else copy the link.
    async share() {
      if (navigator.share) {
        try {
          await navigator.share({ title: this.entry.term, text: this.definition, url: window.location.href })
        } catch { /* user closed the share sheet */ }
        return
      }
      return this.copy('shareCopied')
    },
  },
}
</script>
