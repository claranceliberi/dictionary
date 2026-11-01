<template>
  <div>
    <section class="cover">
      <Ribbon orientation="v" :class="{ 'draw-in': drawRibbon }" />
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

    <div class="wrap home-c">
      <section class="home-sect">
        <h2 class="ttl">Inyuguti</h2>
        <p class="cap">Kanda ku nyuguti ubone amagambo yose atangirira kuri yo.</p>
        <LetterNav variant="band" :letters="letters" />
      </section>

      <div class="home-pair">
        <section class="home-sect col-cats">
          <h2 class="ttl">Ibitsibo</h2>
          <p class="cap">Ingeri z'ikoranabuhanga n'umubare w'amagambo muri buri imwe.</p>
          <div class="ib-cap"><span>Igitsibo</span><span>Amagambo</span></div>
          <ul class="ibitsibo">
            <li v-for="cat in categories" :key="cat.name">
              <router-link :to="categoryLink(cat.name)">
                <span>{{ cat.name }}</span><span class="dots"></span><span class="n">{{ cat.count }}</span>
              </router-link>
            </li>
          </ul>
        </section>

        <section class="home-sect">
          <h2 class="ttl">Uko wasoma</h2>
          <p class="cap">Uko ijambo ryanditse: imisomere, inshoza n'ibindi biriranga.</p>
          <figure class="minipage" aria-label="Urugero">
            <div class="mp-lb">Urugero</div>
            <EntryCard v-if="example" :entry="example" hide-image />
          </figure>
          <router-link class="more" to="/uko-wasoma">Soma ibisobanuro byose <span aria-hidden="true">→</span></router-link>
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
// The cover ribbon draws itself in on the first visit only, not on every return home.
let ribbonDrawn = false

export default {
  name: 'HomeView',
  components: { EntryCard, LetterNav, Ribbon, SearchBar },
  props: {
    letters: { type: Array, default: () => [] },
    stats: { type: Object, default: () => ({}) },
    categories: { type: Array, default: () => [] },
  },
  data() {
    const drawRibbon = !ribbonDrawn
    ribbonDrawn = true
    return { query: '', example: null, TRY, drawRibbon }
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
