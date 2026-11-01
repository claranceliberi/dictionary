<template>
  <nav :class="variant === 'band' ? 'lband' : variant" aria-label="Inyuguti">
    <router-link
      v-for="l in letters"
      :key="l.letter"
      :to="`/browse/${l.letter}`"
      :class="{ on: l.letter === active }"
      :aria-current="l.letter === active ? 'true' : undefined"
      :title="`${l.letter} — ${countLabel(l.count)}`"
    >{{ l.letter }}</router-link>
  </nav>
</template>

<script>
import { countLabel } from '../format.js'

// "band" is the home page's row of letters; "tabs" is the desktop rail on
// letter pages and "strip" its phone equivalent (CSS shows one or the other).
export default {
  name: 'LetterNav',
  methods: { countLabel },
  props: {
    letters: { type: Array, default: () => [] },
    active: { type: String, default: '' },
    variant: { type: String, default: 'tabs', validator: (v) => ['band', 'tabs', 'strip'].includes(v) },
  },
}
</script>
