<template>
  <div>
    <!-- ── Breadcrumb ────────────────────────────────── -->
    <nav class="flex items-center gap-1.5 text-sm text-slate-400 dark:text-slate-500 mb-5">
      <router-link to="/" class="hover:text-rw-green transition-colors">Ahabanza</router-link>
      <span>›</span>
      <router-link
        v-if="entry && entry.term"
        :to="`/browse/${entry.term[0].toUpperCase()}`"
        class="hover:text-rw-green transition-colors"
      >
        {{ entry.term[0].toUpperCase() }}
      </router-link>
      <span v-if="entry && entry.term">›</span>
      <span v-if="entry" class="text-slate-600 dark:text-slate-300 font-medium truncate max-w-[200px]">
        {{ entry.term }}
      </span>
    </nav>

    <!-- Loading skeletons -->
    <div v-if="loading" class="card-bordered p-8">
      <div class="flex items-start gap-6">
        <div class="flex-1">
          <div class="skeleton h-8 w-48 rounded mb-3"></div>
          <div class="skeleton h-4 w-32 rounded mb-6"></div>
          <div class="skeleton h-3.5 w-full rounded mb-2"></div>
          <div class="skeleton h-3.5 w-3/4 rounded mb-2"></div>
          <div class="skeleton h-3.5 w-5/6 rounded"></div>
        </div>
      </div>
    </div>

    <!-- Entry detail -->
    <div v-else-if="entry" class="card-bordered overflow-hidden">

      <!-- Hero band -->
      <div class="imigongo-hero px-8 py-8 relative">
        <div class="absolute inset-0 bg-gradient-to-b from-black/5 to-black/30 pointer-events-none"></div>
        <div class="relative flex items-start justify-between gap-4">
          <div>
            <dfn class="font-serif text-4xl font-bold text-white not-italic block leading-tight mb-1">
              {{ entry.term }}
            </dfn>
            <span v-if="entry.pronunciation" class="font-serif italic text-white/70 text-lg">
              ({{ entry.pronunciation }})
            </span>
            <div class="mt-3">
              <span
                v-if="entry.category"
                :class="categoryClass"
                class="cat-badge text-sm"
              >
                {{ entry.category }}
              </span>
            </div>
          </div>
          <!-- Actions -->
          <div class="flex items-center gap-2 flex-shrink-0">
            <button
              @click="copyLink"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/15 hover:bg-white/25
                     text-white text-xs font-medium transition-colors duration-150"
            >
              {{ copied ? '✓ Yakopwe' : '⎘ Kopa URL' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Two-column body -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-0 divide-y md:divide-y-0 md:divide-x divide-slate-100 dark:divide-slate-800">

        <!-- Left: translations -->
        <div class="px-8 py-6 space-y-4">
          <h3 class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-4">
            Ubusobanuro
          </h3>

          <div v-if="entry.synonym" class="flex gap-3">
            <span class="w-6 flex-shrink-0 text-center text-slate-300 dark:text-slate-600 font-serif text-lg">≈</span>
            <div>
              <p class="text-xs text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-0.5">Impuzanyito</p>
              <p class="italic text-slate-700 dark:text-slate-300">{{ entry.synonym }}</p>
            </div>
          </div>

          <div v-if="entry.english" class="flex gap-3">
            <span class="w-6 flex-shrink-0 text-sm mt-0.5" title="Icyongereza">🇬🇧</span>
            <div>
              <p class="text-xs text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-0.5">English</p>
              <p class="italic text-slate-700 dark:text-slate-300">{{ entry.english }}</p>
            </div>
          </div>

          <div v-if="entry.french" class="flex gap-3">
            <span class="w-6 flex-shrink-0 text-sm mt-0.5" title="Igifaransa">🇫🇷</span>
            <div>
              <p class="text-xs text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-0.5">Français</p>
              <p class="italic text-slate-600 dark:text-slate-400">{{ entry.french }}</p>
            </div>
          </div>
        </div>

        <!-- Right: definition + images -->
        <div class="px-8 py-6">
          <h3 class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-4">
            Inshoza
          </h3>
          <p v-if="entry.definition"
             class="text-slate-700 dark:text-slate-300 leading-relaxed text-base">
            {{ entry.definition }}
          </p>
          <p v-else class="text-slate-400 dark:text-slate-500 text-sm italic">
            Nta nshoza ihari.
          </p>

          <!-- Images -->
          <div v-if="entry.images && entry.images.length" class="mt-6 flex flex-wrap gap-4">
            <figure v-for="img in entry.images" :key="img">
              <img
                :src="`/images/${img}`"
                :alt="`${entry.term} ishusho`"
                class="max-h-44 max-w-[240px] rounded-xl border border-slate-100 dark:border-slate-700
                       object-contain bg-slate-50 dark:bg-slate-800 p-2"
                loading="lazy"
              />
              <figcaption class="text-xs text-slate-400 dark:text-slate-500 mt-1.5 text-center">
                {{ entry.term }}
              </figcaption>
            </figure>
          </div>
        </div>
      </div>

      <!-- Footer meta -->
      <div class="px-8 py-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30
                  flex items-center justify-between text-xs text-slate-400 dark:text-slate-500">
        <span>#{{ entry.id }} · Inkoranyamuga y'Ikoranabuhanga</span>
        <div class="flex items-center gap-3">
          <button @click="$router.back()" class="hover:text-rw-green transition-colors">
            ← Subira inyuma
          </button>
          <router-link
            v-if="entry.category"
            :to="`/search?q=${encodeURIComponent(entry.category.split(' ').pop())}`"
            class="hover:text-rw-green transition-colors"
          >
            Ijambo risa →
          </router-link>
        </div>
      </div>
    </div>

    <!-- Not found -->
    <div v-else class="card-bordered px-8 py-16 text-center">
      <div class="text-4xl mb-4">📭</div>
      <p class="font-serif text-lg text-slate-600 dark:text-slate-300 mb-1">Ijambo ntiryabonetse</p>
      <router-link to="/" class="text-rw-green hover:text-rw-green-dark text-sm font-medium">
        ← Garuka ahabanza
      </router-link>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const CATEGORY_COLORS = {
  'mudasobwa': 'bg-blue-100/70 text-blue-800',
  'murandasi': 'bg-emerald-100/70 text-emerald-800',
  'itumanaho': 'bg-violet-100/70 text-violet-800',
  'isakazamakuru': 'bg-orange-100/70 text-orange-800',
  'ubwenge': 'bg-pink-100/70 text-pink-800',
  'urusobe': 'bg-teal-100/70 text-teal-800',
  'forensics': 'bg-red-100/70 text-red-800',
  'ndangamuntu': 'bg-indigo-100/70 text-indigo-800',
  'imari': 'bg-yellow-100/70 text-yellow-800',
  'itangazabumenyi': 'bg-cyan-100/70 text-cyan-800',
}

export default {
  name: 'EntryView',
  data() {
    return { entry: null, loading: false, copied: false }
  },
  computed: {
    categoryClass() {
      const cat = (this.entry?.category || '').toLowerCase()
      for (const [key, cls] of Object.entries(CATEGORY_COLORS)) {
        if (cat.includes(key)) return cls
      }
      return 'bg-white/20 text-white'
    },
  },
  created() { this.fetch() },
  watch: {
    '$route.params.id'() { this.fetch() },
  },
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
    async copyLink() {
      await navigator.clipboard.writeText(window.location.href).catch(() => {})
      this.copied = true
      setTimeout(() => { this.copied = false }, 2000)
    },
  },
}
</script>
