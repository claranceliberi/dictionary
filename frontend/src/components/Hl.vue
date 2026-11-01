<template>
  <span class="hl"><template v-for="(p, i) in parts" :key="i"><mark v-if="p.hit">{{ p.text }}</mark><template v-else>{{ p.text }}</template></template></span>
</template>

<script>
import { highlight } from '../format.js'

// Text with every match of the search query marked.
export default {
  name: 'Hl',
  props: {
    text: { type: String, default: '' },
    q: { type: String, default: '' },
  },
  computed: {
    parts() {
      return highlight(this.text, this.q)
    },
  },
}
</script>
