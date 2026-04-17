<template>
  <div>
    <div class="mb-4">
      <button @click="$router.back()" class="text-sm text-rw-green hover:underline">
        ← Subira inyuma
      </button>
    </div>

    <div v-if="loading" class="text-center py-12 text-slate-400">Gutunganya...</div>

    <div v-else-if="entry" class="bg-white rounded-2xl shadow-sm border border-slate-100 p-8">
      <!-- Headword -->
      <div class="mb-5 pb-5 border-b border-slate-100 border-l-4 border-l-rw-green pl-4">
        <dfn class="font-serif text-3xl font-bold text-slate-900 not-italic block">
          {{ entry.term }}
        </dfn>
        <span v-if="entry.pronunciation" class="font-serif italic text-slate-400 text-lg">
          ({{ entry.pronunciation }})
        </span>
        <span v-if="entry.category" :class="categoryClass" class="cat-badge ml-3 text-sm">
          {{ entry.category }}
        </span>
      </div>

      <!-- Synonym -->
      <div v-if="entry.synonym" class="mb-3">
        <span class="entry-label">Impuzanyito (HI)</span>
        <span class="entry-synonym text-base">{{ entry.synonym }}</span>
      </div>

      <!-- English -->
      <div v-if="entry.english" class="mb-3">
        <span class="entry-label">Icyongereza (Eng)</span>
        <span class="entry-eng text-base">{{ entry.english }}</span>
      </div>

      <!-- French -->
      <div v-if="entry.french" class="mb-3">
        <span class="entry-label">Igifaransa (Fr)</span>
        <span class="entry-fr text-base">{{ entry.french }}</span>
      </div>

      <!-- Definition -->
      <div v-if="entry.definition" class="mt-5">
        <span class="entry-label block mb-1">Inshoza (SH)</span>
        <p class="entry-def text-base leading-relaxed">{{ entry.definition }}</p>
      </div>

      <!-- Images -->
      <div v-if="entry.images && entry.images.length" class="mt-6 flex flex-wrap gap-4">
        <figure v-for="img in entry.images" :key="img" class="text-center">
          <img
            :src="`/images/${img}`"
            :alt="`${entry.term} ishusho`"
            class="max-h-48 max-w-xs rounded-lg border border-slate-100 object-contain bg-slate-50 p-2"
          />
          <figcaption class="text-xs text-slate-400 mt-1">{{ entry.term }}</figcaption>
        </figure>
      </div>

      <!-- Entry ID -->
      <div class="mt-8 pt-4 border-t border-slate-100 text-xs text-slate-400">
        #{{ entry.id }} · Inkoranyamuga y'Ikoranabuhanga © 2026 Inteko y'Umuco
      </div>
    </div>

    <div v-else class="text-center py-12">
      <p class="text-slate-500">Ijambo ntiryabonetse.</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const CATEGORY_COLORS = {
  'mudasobwa': 'bg-blue-50 text-blue-700',
  'murandasi': 'bg-emerald-50 text-emerald-700',
  'itumanaho': 'bg-violet-50 text-violet-700',
  'isakazamakuru': 'bg-orange-50 text-orange-700',
  'ubwenge': 'bg-pink-50 text-pink-700',
  'urusobe': 'bg-teal-50 text-teal-700',
  'forensics': 'bg-red-50 text-red-700',
  'ndangamuntu': 'bg-indigo-50 text-indigo-700',
  'imari': 'bg-yellow-50 text-yellow-700',
  'itangazabumenyi': 'bg-cyan-50 text-cyan-700',
}

export default {
  name: 'EntryView',
  data() {
    return { entry: null, loading: false }
  },
  computed: {
    categoryClass() {
      const cat = (this.entry?.category || '').toLowerCase()
      for (const [key, cls] of Object.entries(CATEGORY_COLORS)) {
        if (cat.includes(key)) return cls
      }
      return 'bg-slate-100 text-slate-600'
    },
  },
  created() { this.fetch() },
  methods: {
    async fetch() {
      this.loading = true
      try {
        const res = await axios.get(`/api/entries/${this.$route.params.id}`)
        this.entry = res.data
      } catch {
        this.entry = null
      } finally {
        this.loading = false
      }
    },
  },
}
</script>
