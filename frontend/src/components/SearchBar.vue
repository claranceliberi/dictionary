<template>
  <div class="relative w-full">
    <input
      ref="inputEl"
      v-model="localQuery"
      type="search"
      :placeholder="placeholder"
      :class="[
        'w-full px-4 pr-12 rounded-xl border-2 bg-white',
        'text-slate-900 font-sans shadow-sm',
        'focus:outline-none focus:border-rw-green focus:ring-2 focus:ring-rw-green/10',
        'placeholder-slate-400 border-slate-200',
        size === 'lg' ? 'py-4 text-lg rounded-2xl' : 'py-3 text-base',
      ]"
      @keydown.enter="submit"
    />
    <button
      v-if="localQuery"
      @click="clear"
      class="absolute right-10 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-lg"
      aria-label="Siba"
    >×</button>
    <button
      @click="submit"
      class="absolute right-3 top-1/2 -translate-y-1/2 text-rw-green hover:text-rw-green-dark"
      aria-label="Shakisha"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"/>
      </svg>
    </button>
  </div>
</template>

<script>
export default {
  name: 'SearchBar',
  props: {
    modelValue: { type: String, default: '' },
    placeholder: { type: String, default: 'Shakisha ijambo... Search... Rechercher...' },
    autofocus: { type: Boolean, default: false },
    size: { type: String, default: 'md' },
  },
  emits: ['update:modelValue', 'search'],
  data() {
    return { localQuery: this.modelValue, timer: null }
  },
  watch: {
    modelValue(v) { this.localQuery = v },
    localQuery(v) {
      this.$emit('update:modelValue', v)
      clearTimeout(this.timer)
      this.timer = setTimeout(() => this.$emit('search', v), 350)
    },
  },
  mounted() {
    if (this.autofocus) this.$refs.inputEl?.focus()
  },
  methods: {
    submit() {
      clearTimeout(this.timer)
      this.$emit('search', this.localQuery)
    },
    clear() {
      this.localQuery = ''
      this.$refs.inputEl?.focus()
    },
  },
}
</script>
