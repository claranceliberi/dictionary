<template>
  <article class="e">
    <figure v-if="image">
      <img :src="`/images/${image}`" :alt="entry.term" loading="lazy" />
    </figure>
    <div>
      <router-link :to="`/entry/${entry.id}`" class="hw">{{ entry.term }}</router-link>
      <span v-if="entry.pronunciation" class="pr">({{ entry.pronunciation }})</span>
    </div>
    <p v-if="definition" class="def">{{ definition }}</p>
    <dl class="meta">
      <template v-for="row in rows" :key="row.key">
        <dt><abbr tabindex="0" :data-full="FULL[row.key]" :aria-label="FULL[row.key]">{{ row.key }}</abbr></dt>
        <dd>
          <template v-if="row.key === 'HI'">
            <template v-for="(s, i) in synonyms" :key="i">
              <template v-if="i">; </template>
              <b v-if="i === 0">{{ s.term }}</b><template v-else>{{ s.term }}</template>
              <span v-if="s.pron" class="mut"> ({{ s.pron }})</span>
            </template>
          </template>
          <template v-else-if="row.key === 'NK'">{{ entry.category }}</template>
          <template v-else>
            <b>{{ row.terms.main }}</b><template v-if="row.terms.rest.length">; {{ row.terms.rest.join('; ') }}</template>
          </template>
        </dd>
      </template>
    </dl>
  </article>
</template>

<script>
import { splitTerms, splitSynonyms, stripMarks } from '../format.js'

const FULL = {
  HI: 'Impuzanyito',
  Eng: 'Icyongereza',
  Fr: 'Igifaransa',
  NK: "Igitsibo (ingeri y'ikoranabuhanga)",
}

export default {
  name: 'EntryCard',
  props: {
    entry: { type: Object, required: true },
    hideImage: { type: Boolean, default: false },
  },
  data() {
    return { FULL }
  },
  computed: {
    image() {
      return this.hideImage ? null : this.entry.images?.[0] ?? null
    },
    synonyms() {
      return splitSynonyms(this.entry.synonym)
    },
    definition() {
      return stripMarks(this.entry.definition)
    },
    rows() {
      const en = splitTerms(this.entry.english)
      const fr = splitTerms(this.entry.french)
      return [
        this.synonyms.length && { key: 'HI' },
        en.main && { key: 'Eng', terms: en },
        fr.main && { key: 'Fr', terms: fr },
        this.entry.category && { key: 'NK' },
      ].filter(Boolean)
    },
  },
}
</script>
