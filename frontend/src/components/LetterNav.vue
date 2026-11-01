<template>
  <nav v-if="variant === 'table'" class="ishakiro" aria-label="Ishakiro">
    <router-link v-for="l in letters" :key="l.letter" :to="`/browse/${l.letter}`">
      <b>{{ l.letter }}</b><span>{{ l.count }}</span>
    </router-link>
  </nav>
  <nav v-else :class="variant === 'tabs' ? 'tabs' : 'strip'" aria-label="Inyuguti">
    <router-link
      v-for="l in letters"
      :key="l.letter"
      :to="`/browse/${l.letter}`"
      :class="{ on: l.letter === active }"
      :aria-current="l.letter === active ? 'true' : undefined"
      :title="`${l.letter} — amagambo ${l.count}`"
    >{{ l.letter }}</router-link>
  </nav>
</template>

<script>
// "table" is the home page's Ishakiro; "tabs" is the desktop rail on letter
// pages and "strip" its phone equivalent (CSS shows one or the other).
export default {
  name: 'LetterNav',
  props: {
    letters: { type: Array, default: () => [] },
    active: { type: String, default: '' },
    variant: { type: String, default: 'tabs', validator: (v) => ['table', 'tabs', 'strip'].includes(v) },
  },
}
</script>
