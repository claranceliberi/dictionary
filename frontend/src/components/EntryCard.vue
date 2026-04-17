<template>
  <!-- Image-first variant when entry has images -->
  <article
    v-if="entry.images && entry.images.length && !compact"
    class="group py-4 px-6 -mx-0 transition-colors duration-150 cursor-pointer"
    :class="selected
      ? 'bg-rw-green/5 dark:bg-rw-green/10'
      : 'hover:bg-slate-50 dark:hover:bg-slate-800/50'"
    @click="$emit('select', entry)"
  >
    <div class="flex gap-4">
      <!-- Thumbnail -->
      <div class="flex-shrink-0">
        <img
          :src="`/images/${entry.images[0]}`"
          :alt="entry.term"
          class="w-20 h-16 object-contain rounded-xl border border-slate-100 dark:border-slate-700
                 bg-slate-50 dark:bg-slate-800"
          loading="lazy"
        />
      </div>
      <!-- Content -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center flex-wrap gap-1.5 mb-1">
          <dfn class="entry-term not-italic">{{ entry.term }}</dfn>
          <span v-if="entry.pronunciation" class="entry-pron">({{ entry.pronunciation }})</span>
          <span v-if="entry.category" :class="categoryClass(entry.category)" class="cat-badge">
            {{ shortCategory(entry.category) }}
          </span>
        </div>
        <div class="flex flex-wrap gap-x-4 gap-y-0.5 text-sm mb-1">
          <span v-if="entry.english" class="text-slate-600 dark:text-slate-400 italic">
            🇬🇧 {{ entry.english }}
          </span>
          <span v-if="entry.french" class="text-slate-500 dark:text-slate-500 italic">
            🇫🇷 {{ entry.french }}
          </span>
        </div>
        <p v-if="entry.definition" class="text-xs text-slate-500 dark:text-slate-400 leading-relaxed line-clamp-2">
          {{ entry.definition }}
        </p>
      </div>
    </div>
    <!-- Hover-reveal actions -->
    <div class="mt-2 flex items-center gap-3 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
      <router-link
        :to="`/entry/${entry.id}`"
        class="text-xs text-rw-green hover:text-rw-green-dark font-medium"
        @click.stop
      >
        Reba byuzuye →
      </router-link>
      <button
        @click.stop="copyLink"
        class="text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
        :title="copied ? 'Yakopwe!' : 'Kopa url'"
      >
        {{ copied ? '✓ Yakopwe' : '⎘ Kopa' }}
      </button>
    </div>
  </article>

  <!-- Standard / compact variant -->
  <article
    v-else
    class="group transition-colors duration-150 cursor-pointer"
    :class="[
      compact ? 'py-2.5 px-6' : 'py-4 px-6',
      selected
        ? 'bg-rw-green/5 dark:bg-rw-green/10'
        : 'hover:bg-slate-50 dark:hover:bg-slate-800/50',
    ]"
    @click="$emit('select', entry)"
  >
    <!-- Headword line -->
    <div class="flex items-center flex-wrap gap-1.5 mb-1">
      <dfn class="entry-term not-italic" :class="compact ? 'text-base' : ''">{{ entry.term }}</dfn>
      <span v-if="entry.pronunciation" class="entry-pron">({{ entry.pronunciation }})</span>
      <span v-if="entry.category" :class="categoryClass(entry.category)" class="cat-badge">
        {{ shortCategory(entry.category) }}
      </span>
    </div>

    <!-- Translations row -->
    <div v-if="!compact" class="flex flex-wrap gap-x-5 gap-y-0.5 text-sm mb-1">
      <span v-if="entry.synonym" class="text-slate-500 dark:text-slate-400 italic">
        ≈ {{ entry.synonym }}
      </span>
      <span v-if="entry.english" class="text-slate-600 dark:text-slate-400 italic">
        🇬🇧 {{ entry.english }}
      </span>
      <span v-if="entry.french" class="text-slate-500 dark:text-slate-500 italic">
        🇫🇷 {{ entry.french }}
      </span>
    </div>

    <!-- Compact: just EN translation inline -->
    <div v-if="compact && entry.english" class="text-xs text-slate-500 dark:text-slate-400 italic">
      🇬🇧 {{ entry.english }}
    </div>

    <!-- Definition (non-compact) -->
    <p v-if="entry.definition && !compact"
       class="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mt-1.5 line-clamp-2">
      {{ entry.definition }}
    </p>

    <!-- Hover-reveal actions -->
    <div
      v-if="!compact"
      class="mt-1.5 flex items-center gap-3 opacity-0 group-hover:opacity-100 transition-opacity duration-150"
    >
      <router-link
        :to="`/entry/${entry.id}`"
        class="text-xs text-rw-green hover:text-rw-green-dark font-medium"
        @click.stop
      >
        Reba byuzuye →
      </router-link>
      <button
        @click.stop="copyLink"
        class="text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
        :title="copied ? 'Yakopwe!' : 'Kopa url'"
      >
        {{ copied ? '✓ Yakopwe' : '⎘ Kopa' }}
      </button>
    </div>
  </article>
</template>

<script>
const CATEGORY_COLORS = {
  'mudasobwa': 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  'murandasi': 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
  'itumanaho': 'bg-violet-50 text-violet-700 dark:bg-violet-900/30 dark:text-violet-400',
  'isakazamakuru': 'bg-orange-50 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
  'ubwenge': 'bg-pink-50 text-pink-700 dark:bg-pink-900/30 dark:text-pink-400',
  'urusobe': 'bg-teal-50 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400',
  'forensics': 'bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  'ndangamuntu': 'bg-indigo-50 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400',
  'imari': 'bg-yellow-50 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
  'itangazabumenyi': 'bg-cyan-50 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400',
}

export default {
  name: 'EntryCard',
  emits: ['select'],
  props: {
    entry: { type: Object, required: true },
    compact: { type: Boolean, default: false },
    selected: { type: Boolean, default: false },
  },
  data() {
    return { copied: false }
  },
  methods: {
    categoryClass(cat) {
      const lower = (cat || '').toLowerCase()
      for (const [key, cls] of Object.entries(CATEGORY_COLORS)) {
        if (lower.includes(key)) return cls
      }
      return 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400'
    },
    shortCategory(cat) {
      const map = {
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
      return map[cat] || cat.split(' ').slice(-1)[0]
    },
    async copyLink() {
      const url = `${window.location.origin}/entry/${this.entry.id}`
      try {
        await navigator.clipboard?.writeText(url)
        this.copied = true
        setTimeout(() => { this.copied = false }, 2000)
      } catch { /* silent */ }
    },
  },
}
</script>
