<template>
  <nav :class="vertical ? 'grid grid-cols-4 gap-1' : 'flex flex-wrap gap-1 justify-center'"
       aria-label="Shakisha inyuguti">
    <router-link
      v-for="item in letters"
      :key="item.letter"
      :to="`/browse/${item.letter}`"
      class="w-9 h-9 flex items-center justify-center rounded-lg text-sm font-semibold
             border transition-colors duration-100"
      :class="active === item.letter
        ? 'bg-rw-green text-white border-rw-green'
        : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50 hover:border-slate-300'"
      :title="`${item.letter} (${item.count})`"
    >
      {{ item.letter }}
    </router-link>
  </nav>
</template>

<script>
export default {
  name: 'LetterNav',
  props: {
    letters: { type: Array, default: () => [] },
    active: { type: String, default: null },
    vertical: { type: Boolean, default: false },
  },
}
</script>
