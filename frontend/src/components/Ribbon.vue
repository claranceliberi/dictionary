<template>
  <svg
    :class="orientation === 'v' ? 'ribbon-v' : 'ribbon-h'"
    aria-hidden="true"
    focusable="false"
  >
    <defs>
      <pattern
        v-if="orientation === 'v'"
        :id="id"
        width="34"
        height="18"
        patternUnits="userSpaceOnUse"
      >
        <polyline class="z z-blue" points="3,0 12,9 3,18" />
        <polyline class="z z-yellow" points="12,0 21,9 12,18" />
        <polyline class="z z-green" points="21,0 30,9 21,18" />
      </pattern>
      <pattern v-else :id="id" width="14" height="22" patternUnits="userSpaceOnUse">
        <polyline class="z z-blue" points="0,2 7,9 14,2" />
        <polyline class="z z-yellow" points="0,9 7,16 14,9" />
        <polyline class="z z-green" points="0,16 7,23 14,16" />
      </pattern>
    </defs>
    <rect width="100%" height="100%" :fill="`url(#${id})`" />
  </svg>
</template>

<script>
let seq = 0

// The book's flag-colour zigzag. Drawn inline (not as a CSS background) so the
// stroke colours follow the light/dark theme tokens. Each instance needs its
// own pattern id because several ribbons can be on the page at once.
export default {
  name: 'Ribbon',
  props: {
    orientation: { type: String, default: 'v', validator: (v) => v === 'v' || v === 'h' },
  },
  data() {
    return { id: `zigzag-${++seq}` }
  },
}
</script>
