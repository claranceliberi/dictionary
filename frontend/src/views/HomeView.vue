<template>
  <div>
    <section class="cover">
      <Ribbon orientation="v" />
      <div class="wrap">
        <h1>Inkoranyamuga<br />y'Ikoranabuhanga</h1>
        <p>
          <template v-if="stats.total_entries">Amagambo <b>{{ stats.total_entries }}</b> &nbsp;·&nbsp; </template>Ikinyarwanda, Icyongereza n'Igifaransa
        </p>
        <SearchBar v-model="query" @search="onSearch" />
        <p class="try">
          Gerageza:
          <template v-for="(w, i) in TRY" :key="w">
            <router-link :to="{ path: '/search', query: { q: w } }">{{ w }}</router-link><template v-if="i < TRY.length - 1"> · </template>
          </template>
        </p>
      </div>
    </section>

    <div class="wrap home-body">
      <section class="col-ish">
        <h2 class="ttl">Ishakiro</h2>
        <p class="cap">Inyuguti n'umubare w'amagambo</p>
        <LetterNav variant="table" :letters="letters" />
      </section>

      <div class="col-main">
        <section class="howto">
          <h2 class="ttl">Urutonde rw'ibimenyetso mpine</h2>
          <div class="howto-grid">
            <div>
              <p class="intro">
                Buri jambo rikurikirwa n'imisomere yaryo mu dukubo, hanyuma inshoza yaryo. Munsi yayo haza
                ibindi biriranga, buri kimwe kibanzirizwa n'impine yacyo:
              </p>
              <dl class="legend">
                <dt>HI</dt><dd><b>Impuzanyito</b> — iryuga rivuga kimwe n'ijambo ry'indatwa.</dd>
                <dt>Eng</dt><dd><b>Icyongereza</b> — iyo amagambo ari menshi, iry'indatwa ryandikwa mu nyuguti zitsindagiye, ayandi akarikurikira.</dd>
                <dt>Fr</dt><dd><b>Igifaransa</b> — byandikwa kimwe n'Icyongereza.</dd>
                <dt>NK</dt><dd><b>Igitsibo</b> — ingeri y'ikoranabuhanga ijambo ribarizwamo.</dd>
              </dl>
              <router-link class="more" to="/uko-wasoma">Soma ibisobanuro byose <span aria-hidden="true">→</span></router-link>
            </div>
            <figure class="minipage" aria-label="Urugero">
              <div class="runhead">Inkoranyamuga y'ikoranabuhanga</div>
              <div class="mp-lb">Urugero</div>
              <EntryCard v-if="example" :entry="example" hide-image />
              <div class="mp-foot"><span>M</span></div>
            </figure>
          </div>
        </section>

        <section class="col-cats">
          <h2 class="ttl">Ibitsibo</h2>
          <ul class="ibitsibo">
            <li v-for="cat in categories" :key="cat.name">
              <router-link :to="categoryLink(cat.name)">
                <span>{{ cat.name }}</span><span class="dots"></span><span class="n">{{ cat.count }}</span>
              </router-link>
            </li>
          </ul>
        </section>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import EntryCard from '../components/EntryCard.vue'
import LetterNav from '../components/LetterNav.vue'
import Ribbon from '../components/Ribbon.vue'
import SearchBar from '../components/SearchBar.vue'
import { categoryLink } from '../format.js'

const TRY = ['mudasobwa', 'imeri', 'murandasi', 'mikoro']
// Mikoro: a short entry that has every field except a second translation.
const EXAMPLE_ID = 1140

export default {
  name: 'HomeView',
  components: { EntryCard, LetterNav, Ribbon, SearchBar },
  props: {
    letters: { type: Array, default: () => [] },
    stats: { type: Object, default: () => ({}) },
    categories: { type: Array, default: () => [] },
  },
  data() {
    return { query: '', example: null, TRY }
  },
  async created() {
    try {
      this.example = (await axios.get(`/api/entries/${EXAMPLE_ID}`)).data
    } catch {
      this.example = null
    }
  },
  methods: {
    categoryLink,
    onSearch(q) {
      if (q.trim()) this.$router.push({ path: '/search', query: { q } })
    },
  },
}
</script>
