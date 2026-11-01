<template>
  <div>
    <Ribbon orientation="v" />
    <div class="wrap">
      <p v-if="loading" class="state">Gushakisha…</p>

      <article v-else-if="entry" class="entry">
        <nav class="crumb" aria-label="Aho uri">
          <router-link to="/">Ahabanza</router-link> ›
          <router-link :to="`/browse/${letter}`">{{ letter }}</router-link> ›
          {{ entry.term }}
        </nav>

        <div class="entry-top">
          <div>
            <h1>{{ entry.term }}</h1>
            <div v-if="entry.pronunciation" class="pr">({{ entry.pronunciation }})</div>
          </div>
          <img v-if="entry.images?.length" :src="`/images/${entry.images[0]}`" :alt="entry.term" />
        </div>

        <div v-if="entry.definition" class="lead">
          <span class="lb">Inshoza</span>
          <p>{{ entry.definition }}</p>
        </div>

        <div class="fields">
          <div v-if="synonym.term" class="f">
            <span class="lb">Impuzanyito</span>
            <span><b>{{ synonym.term }}</b> <small v-if="synonym.pron">({{ synonym.pron }})</small></span>
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

        <div class="acts">
          <a href="#" @click.prevent="$router.back()">← Subira inyuma</a>
          <button type="button" @click="copyLink">{{ copied ? 'Yakopwe' : 'Kopa aderesi' }}</button>
          <router-link v-if="entry.category" :to="categoryLink(entry.category)" class="primary">
            Andi magambo y'iki gitsibo →
          </router-link>
        </div>
      </article>

      <div v-else class="state">
        <p class="state-title">Ijambo ntiryabonetse</p>
        <router-link to="/">← Garuka ahabanza</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import Ribbon from '../components/Ribbon.vue'
import { splitTerms, splitSynonym, categoryLink } from '../format.js'

export default {
  name: 'EntryView',
  components: { Ribbon },
  data() {
    return { entry: null, loading: false, copied: false }
  },
  computed: {
    letter() { return (this.entry?.letter || this.entry?.term?.[0] || '').toUpperCase() },
    synonym() { return splitSynonym(this.entry?.synonym) },
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
    async copyLink() {
      try {
        await navigator.clipboard.writeText(window.location.href)
        this.copied = true
        setTimeout(() => { this.copied = false }, 2000)
      } catch { /* clipboard blocked: leave the label unchanged */ }
    },
  },
}
</script>
