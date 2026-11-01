<template>
  <nav v-if="pages.length" class="pager" aria-label="Amapaji">
    <a v-if="page > 1" href="#" aria-label="Ipaji ibanza" @click.prevent="$emit('go', page - 1)">‹</a>
    <template v-for="(p, i) in pages" :key="`${p}-${i}`">
      <span v-if="p === '…'" class="gap" aria-hidden="true">…</span>
      <span v-else-if="p === page" class="cur" aria-current="page">{{ p }}</span>
      <a v-else href="#" @click.prevent="$emit('go', p)">{{ p }}</a>
    </template>
    <a v-if="page < totalPages" href="#" aria-label="Ipaji ikurikira" @click.prevent="$emit('go', page + 1)">›</a>
  </nav>
</template>

<script>
import { pageWindow } from '../format.js'

export default {
  name: 'Pager',
  props: {
    page: { type: Number, required: true },
    totalPages: { type: Number, required: true },
  },
  emits: ['go'],
  computed: {
    pages() {
      return pageWindow(this.page, this.totalPages)
    },
  },
}
</script>
