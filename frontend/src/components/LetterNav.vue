<template>
  <!-- Vertical grid (sidebar) -->
  <nav
    v-if="vertical"
    class="grid grid-cols-4 gap-1"
    aria-label="Shakisha inyuguti"
  >
    <router-link
      v-for="item in letters"
      :key="item.letter"
      :to="`/browse/${item.letter}`"
      class="w-full aspect-square flex items-center justify-center rounded-lg text-sm font-semibold
             border transition-colors duration-100"
      :class="active === item.letter
        ? 'bg-rw-green text-white border-rw-green'
        : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300
           border-slate-200 dark:border-slate-700
           hover:bg-slate-50 dark:hover:bg-slate-700 hover:border-slate-300'"
      :title="`${item.letter} (${item.count})`"
      @click="$emit('navigate', item.letter)"
    >
      {{ item.letter }}
    </router-link>
  </nav>

  <!-- Compact horizontal (home bento) -->
  <nav
    v-else-if="compact"
    class="flex flex-wrap gap-1.5"
    aria-label="Shakisha inyuguti"
  >
    <router-link
      v-for="item in letters"
      :key="item.letter"
      :to="`/browse/${item.letter}`"
      class="w-9 h-9 flex items-center justify-center rounded-lg text-sm font-semibold
             border transition-all duration-150 hover:-translate-y-px"
      :class="active === item.letter
        ? 'bg-rw-green text-white border-rw-green shadow-sm'
        : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300
           border-slate-200 dark:border-slate-700
           hover:bg-slate-50 dark:hover:bg-slate-700 hover:border-rw-green/40 hover:shadow-sm'"
      :title="`${item.letter} — ${item.count} amajambo`"
    >
      {{ item.letter }}
    </router-link>
  </nav>

  <!-- Default horizontal flex (home original) -->
  <nav
    v-else
    class="flex flex-wrap gap-1 justify-center"
    aria-label="Shakisha inyuguti"
  >
    <router-link
      v-for="item in letters"
      :key="item.letter"
      :to="`/browse/${item.letter}`"
      class="w-9 h-9 flex items-center justify-center rounded-lg text-sm font-semibold
             border transition-colors duration-100"
      :class="active === item.letter
        ? 'bg-rw-green text-white border-rw-green'
        : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300
           border-slate-200 dark:border-slate-700
           hover:bg-slate-50 dark:hover:bg-slate-700 hover:border-slate-300'"
      :title="`${item.letter} (${item.count})`"
    >
      {{ item.letter }}
    </router-link>
  </nav>
</template>

<script>
export default {
  name: 'LetterNav',
  emits: ['navigate'],
  props: {
    letters: { type: Array, default: () => [] },
    active: { type: String, default: null },
    vertical: { type: Boolean, default: false },
    compact: { type: Boolean, default: false },
  },
}
</script>
