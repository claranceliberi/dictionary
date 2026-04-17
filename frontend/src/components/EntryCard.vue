<template>
  <article class="py-4 last:border-0 hover:bg-slate-50 transition-colors duration-100 -mx-6 px-6">
    <!-- Headword line -->
    <div class="mb-1">
      <dfn class="entry-term not-italic">{{ entry.term }}</dfn>
      <span v-if="entry.pronunciation" class="entry-pron">({{ entry.pronunciation }})</span>
      <span v-if="entry.category" :class="categoryClass(entry.category)" class="cat-badge ml-2">
        {{ shortCategory(entry.category) }}
      </span>
    </div>

    <!-- Synonym (HI) -->
    <div v-if="entry.synonym" class="text-sm mb-1">
      <span class="entry-label">HI</span>
      <span class="entry-synonym">{{ entry.synonym }}</span>
    </div>

    <!-- English -->
    <div v-if="entry.english" class="text-sm mb-1">
      <span class="entry-label">Eng</span>
      <span class="entry-eng">{{ entry.english }}</span>
    </div>

    <!-- French -->
    <div v-if="entry.french" class="text-sm mb-1">
      <span class="entry-label">Fr</span>
      <span class="entry-fr">{{ entry.french }}</span>
    </div>

    <!-- Definition -->
    <div v-if="entry.definition" class="text-sm mt-2 entry-def">
      <span class="entry-label">SH</span>{{ entry.definition }}
    </div>

    <!-- Images -->
    <div v-if="entry.images && entry.images.length" class="mt-3 flex flex-wrap gap-3">
      <img
        v-for="img in entry.images"
        :key="img"
        :src="`/images/${img}`"
        :alt="`${entry.term} illustration`"
        class="max-h-28 max-w-[180px] rounded border border-slate-100 object-contain bg-white"
        loading="lazy"
      />
    </div>

    <!-- Detail link -->
    <div class="mt-2">
      <router-link
        :to="`/entry/${entry.id}`"
        class="text-xs text-rw-green hover:text-rw-green-dark hover:underline"
      >
        Reba byuzuye →
      </router-link>
    </div>
  </article>
</template>

<script>
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
  name: 'EntryCard',
  props: {
    entry: { type: Object, required: true },
  },
  methods: {
    categoryClass(cat) {
      const lower = (cat || '').toLowerCase()
      for (const [key, cls] of Object.entries(CATEGORY_COLORS)) {
        if (lower.includes(key)) return cls
      }
      return 'bg-slate-100 text-slate-600'
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
  },
}
</script>
